from flask import Flask, render_template, request, redirect, url_for,session,jsonify
import MySQLdb
import pandas as pd
from datetime import datetime,timedelta
from datetime import date
import datetime
import time
from dotenv import load_dotenv
import os

load_dotenv()

def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(25) PRIMARY KEY,
        fname VARCHAR(25) NOT NULL,
        mname VARCHAR(25),
        lname VARCHAR(25),
        email VARCHAR(25) NOT NULL UNIQUE,
        password VARCHAR(25) NOT NULL,
        street VARCHAR(25),
        city VARCHAR(25),
        postal_code CHAR(6),
        id_type VARCHAR(15),
        id_number VARCHAR(25)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicle_types (
        type_id VARCHAR(10) PRIMARY KEY,
        class_type VARCHAR(15),
        class VARCHAR(25),
        icon VARCHAR(50),
        features VARCHAR(200),
        price DOUBLE
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        transaction_id VARCHAR(25) PRIMARY KEY,
        amount DOUBLE NOT NULL,
        payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        payment_mode VARCHAR(25),
        refund BOOLEAN DEFAULT 0
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        reg_no VARCHAR(15) PRIMARY KEY,
        type_id VARCHAR(25),
        status VARCHAR(10),
        location VARCHAR(6),
        next_maintenance_date DATE,
        FOREIGN KEY (type_id) REFERENCES vehicle_types(type_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id VARCHAR(25) PRIMARY KEY,
        pickup_date DATE,
        pickup_time TIME,
        return_date DATE,
        return_time TIME,
        transaction_id VARCHAR(25),
        user_id VARCHAR(25),
        vehicle_id VARCHAR(25),
        FOREIGN KEY (transaction_id) REFERENCES payments(transaction_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (vehicle_id) REFERENCES vehicle_types(type_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        booking_id VARCHAR(25),
        rating INT NOT NULL,
        comments VARCHAR(500),
        feedback_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS report (
        report_id VARCHAR(25) PRIMARY KEY,
        report_type VARCHAR(25),
        user_id VARCHAR(25),
        report_text VARCHAR(100),
        report_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance (
        maintenance_id VARCHAR(25) PRIMARY KEY,
        description VARCHAR(500),
        cost DOUBLE,
        vehicle_reg VARCHAR(25),
        maintenance_date DATE,
        FOREIGN KEY (vehicle_reg) REFERENCES vehicles(reg_no)
    );
    """)

def insert_safe(cursor, table, columns, values, key_column, key_value):
    # This function inserts a row only if the key_value does not exist in key_column
    placeholders = ', '.join(['%s'] * len(values))
    columns_str = ', '.join(columns)
    query = f"""
    INSERT INTO {table} ({columns_str})
    SELECT {placeholders} FROM DUAL
    WHERE NOT EXISTS (
        SELECT 1 FROM {table} WHERE {key_column} = %s
    )
    """
    cursor.execute(query, values + (key_value,))

def insert_initial_data(cursor):
    # Insert users safely
    insert_safe(cursor, 'users',
                ['user_id', 'fname', 'mname', 'lname', 'email', 'password', 'street', 'city', 'postal_code', 'id_type', 'id_number'],
                ('S01', 'Siddeswar', None, 'Nimmala', 'S01@gmail.com', 'Siddhu@123', None, None, None, None, None),
                'user_id', 'S01')

    insert_safe(cursor, 'users',
                ['user_id', 'fname', 'mname', 'lname', 'email', 'password', 'street', 'city', 'postal_code', 'id_type', 'id_number'],
                ('Admin01', 'Admin', None, 'User', 'siddeswar@gmail.com', 'Admin Password', None, None, None, None, None),
                'user_id', 'Admin01')

    # Insert vehicle types safely (you can add all the rows similarly)
    vehicle_types = [
        ('car01', 'car', 'Sedan', 'fas fa-car-side', '4-5 seats, Spacious trunk, Excellent fuel economy, Comfortable ride', 1800),
        ('car02', 'car', 'SUV', 'fas fa-suv', '5-7 seats, All-wheel drive, High ground clearance, Spacious interior', 2500),
        # add all your other vehicle types here...
    ]
    for vt in vehicle_types:
        insert_safe(cursor, 'vehicle_types',
                    ['type_id', 'class_type', 'class', 'icon', 'features', 'price'],
                    vt, 'type_id', vt[0])


def setup_database():
    conn = MySQLdb.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT')),
        user=os.getenv('MYSQL_USER'),
        passwd=os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DB')
    )
    cursor = conn.cursor()

    print("Creating tables...")
    create_tables(cursor)
    conn.commit()

    print("Inserting initial data...")
    insert_initial_data(cursor)
    conn.commit()

    cursor.close()
    conn.close()
    print("Database setup complete!")
    
setup_database()

db = MySQLdb.connect(
    host=os.getenv('MYSQL_HOST'),
    port=int(os.getenv('MYSQL_PORT')),
    user=os.getenv('MYSQL_USER'),
    passwd=os.getenv('MYSQL_PASSWORD'),
    db=os.getenv('MYSQL_DB')
)
cursor = db.cursor()

app = Flask(__name__)
app.secret_key = "secret_key"



@app.route('/admin/add-vehicle',methods=['GET', 'POST'])
def add_vehicle():
    try:
        if request.method == 'POST':
            reg_no = request.form['reg_no']
            type_id = request.form['type_id']
            location = request.form['location']
            if request.form['status']:
                status = 'active'
            else:
                status = 'inactive'
            cursor = db.cursor()
            cursor.execute("SELECT * FROM vehicles WHERE reg_no = %s", (reg_no,))
            result = cursor.fetchone()
            if result:
                return render_template('add-vehicle.html', error_message="Vehicle already exists")
            try:
                cursor.execute("INSERT INTO vehicles(reg_no, type_id, location, status) VALUES (%s, %s, %s, %s)", (reg_no, type_id, location, status))
                db.commit()
                return redirect(url_for('add_vehicle'))
            except Exception as e:
                return render_template('error.html',error_message=e)
    except Exception as e:
        return render_template('error.html',error_message=e)
    return render_template('add-vehicle.html')

@app.route('/admin/manage-vehicles')
def manage_vehicles():
    try:
        cursor = db.cursor()
        cursor.execute(f"""select v.reg_no,v.location,v.status,vt.class_type,vt.class
                            from vehicles v
                            join vehicle_types vt on v.type_id = vt.type_id;""")
        result = cursor.fetchall()
        vehicles = []
        for data in result:
            vehicles.append(
                {
               'reg_no': data[0],
                'location': data[1],
               'status': data[2],
                'class_type': data[3],
                'class': data[4]
                }
            )
        return render_template('manage-vehicles.html', vehicles=vehicles)
    except Exception as e:
        return render_template('error.html',error_message=e)
            
@app.route('/admin/delete-vehicle',methods=['GET', 'POST'])
def delete_vehicle():
    if True:
        reg_no = request.args.get('reg_no')
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM vehicles WHERE reg_no = %s", (reg_no,))
            db.commit()
            return redirect(url_for('manage_vehicles'))
        except Exception as e:
            return render_template('error.html',error_message=e)
        
@app.route('/admin/maintenance',methods=['GET', 'POST'])
def maintenance():
    try:
        cursor = db.cursor()
        cursor.execute(f"""select m.maintenance_id,m.vehicle_reg,m.description,m.cost,m.maintenance_date
                            from maintenance m;""")
        result = cursor.fetchall()
        records = []
        for data in result:
            records.append(
                {
               'id': data[0],
               'vehicle_reg_no' : data[1],
               'description' : data[2],
               'cost' : data[3],
               'date' : data[4].strftime('%Y-%m-%d')  # format date to string
                }
            )
        cursor.execute(f"""select v.reg_no,vt.class,v.location,m.maintenance_date,v.next_maintenance_date
                            from vehicles v
                            join vehicle_types vt on v.type_id = vt.type_id
                            left join maintenance m on v.reg_no = m.vehicle_reg
                            where v.next_maintenance_date < curdate()""")
        result = cursor.fetchall()
        due_records = []
        for data in result:
            due_records.append(
                {
                    'vehicle_reg_no' : data[0],
                     'class' : data[1],
                     'location' : data[2],
                    'last_maintenance' : data[3].strftime('%Y-%m-%d') if data[3] else 'N/A',
                    'next_maintenance' : data[4].strftime('%Y-%m-%d') if data[4] else 'N/A'
                }
            )
    except Exception as e:
        return render_template('error.html',error_message=e)
    if request.method == 'POST':
        if request.form['action'] == 'Edit_Record':
            maintenance_id = request.form['id']
            vehicle_reg_no = request.form['reg_no']
            description = request.form['description']
            cost = request.form['cost']
            date = request.form['date']
            next_date = request.form['next_date']
            cursor = db.cursor()
            try:
                cursor.execute("UPDATE maintenance SET vehicle_reg = %s, description = %s, cost = %s, maintenance_date = %s WHERE maintenance_id = %s", (vehicle_reg_no, description, cost, date, maintenance_id))
                cursor.execute("UPDATE vehicles SET next_maintenance_date = %s WHERE reg_no = %s", (next_date, vehicle_reg_no))
                db.commit()
                return redirect(url_for('maintenance'))
            except Exception as e:
                db.rollback()
                return render_template('error.html',error_message=e)
        else:
            vehicle_reg_no = request.form['reg_no']
            description = request.form['description']
            cost = request.form['cost']
            date = request.form['date']
            next_date = request.form['next_date']
            cursor = db.cursor()
            maintenance_id = 'MT'+str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[2:])
            try:
                cursor.execute("INSERT INTO maintenance(maintenance_id, vehicle_reg, description, cost, maintenance_date) VALUES (%s, %s,%s,%s,%s)", (maintenance_id, vehicle_reg_no, description, cost, date))
                cursor.execute("UPDATE vehicles SET next_maintenance_date = %s WHERE reg_no = %s", (next_date, vehicle_reg_no))
                db.commit()
                return redirect(url_for('maintenance'))
            except Exception as e:
                db.rollback()
                return render_template('error.html',error_message=e)
    return render_template('maintenance.html', records=records, due_records=due_records)

   
@app.route('/admin/delete-maintenance',methods=['GET', 'POST'])
def delete_maintenance():
    if True:
        maintenance_id = request.args.get('maintenance_id')
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM maintenance WHERE maintenance_id = %s", (maintenance_id,))
            db.commit()
            return redirect(url_for('maintenance'))
        except Exception as e:
            db.rollback()
            return render_template('error.html',error_message=e)
        
        
def format_timedelta_to_time(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@app.route('/admin/all-bookings',methods=['GET', 'POST'])
def all_bookings():
    try:
        cursor = db.cursor()
        cursor.execute(f""" select b.booking_id,b.pickup_date,b.pickup_time,b.return_date,b.return_time,b.transaction_id,b.user_id,v.class_type,v.class,v.icon,v.features,t.amount,t.payment_date as 'booking date',t.payment_mode
                            from bookings b
                            join vehicle_types v on b.vehicle_id = v.type_id
                            join payments t on b.transaction_id = t.transaction_id;""")
        result = cursor.fetchall()
        bookings = []
        for data in result:
            bookings.append(
                {   
                'booking_id': data[0],
                'pickup_date': data[1].strftime('%Y-%m-%d'),  # format date to string
                'pickup_time': format_timedelta_to_time(data[2]),
               'return_date': data[3].strftime('%Y-%m-%d'),
               'return_time': format_timedelta_to_time(data[4]),
                'transaction_id': data[5],
                'user_id': data[6],
                'class_type': data[7],
                'class': data[8],
                'icon': data[9],
                'features': data[10].split(','),
                'amount_paid': data[11],
                'payment_date': data[12].strftime('%Y-%m-%d'),  # format date to string
                'payment_method': data[13]
                }
            )
        return render_template('all_booking_details.html', bookings=bookings)
    except Exception as e:
        return render_template('error.html',error_message=e)

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('login'))
    
@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':        
        email = request.form['email']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        result = cursor.fetchone()
        if result:
            session['user_id'] = result[0]
            if email == 'siddeswar@gmail.com':
                return redirect(url_for('add_vehicle'))
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error_message="Invalid email or password")
    return render_template('login.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        mname = request.form['mname']
        lname = request.form['lname']
        user_id = request.form['user_id']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('register.html', error_message="Passwords do not match")
        else:
            cursor = db.cursor()
            try:
                cursor.execute("Insert into users (fname, mname, lname, user_id, email, password) values (%s, %s, %s, %s, %s, %s)", (fname, mname, lname, user_id, email, password))
                db.commit()
                return redirect(url_for('login'))
            except Exception as e:
                db.rollback()
                return render_template('error.html',error_message=e)
    return render_template('register.html')

@app.route('/forgot-password',methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        newPassword = request.form['newPassword']
        confirmPassword = request.form['confirmPassword']
        if newPassword != confirmPassword:
            return render_template('forgot-password.html', error_message="Passwords do not match")
        else:
            try:
                cursor = db.cursor()
                cursor.execute("UPDATE users SET password = %s WHERE email = %s", (newPassword, email))
                db.commit()
                render_template('forgot-password.html', error_message="Password reset successfully")
                time.sleep(2)
                return redirect(url_for('login'))
            except Exception as e:
                db.rollback()
                return render_template('error.html',error_message=e)
    return render_template('forgot-password.html')

@app.route('/home/dashboard')
def home():
    try:
        cursor = db.cursor()
        cursor.execute(f"""SELECT concat(v.class_type, ' (', v.class, ')') AS vehicle_class,b.pickup_date,b.return_date
                            FROM bookings b
                            JOIN vehicle_types v ON b.vehicle_id = v.type_id
                            WHERE user_id = '{session['user_id']}' LIMIT 3;""")
        result = cursor.fetchall()
        recent_bookings = []
        today = date.today()
        for data in result:
            recent_bookings.append(
                {
                'class_type': data[0],
                'pickup_date': data[1].strftime('%Y-%m %d'),  # format date to string
                'return_date' : data[2].strftime('%Y-%m %d'),
                'status' : 'Completed' if data[2] < today else 'Ongoing' if data[1] < today and data[2] > today else 'Upcoming'
                }
            )
        return render_template('home.html',recent_bookings=recent_bookings)
    except Exception as e:
        return render_template('error.html',error_message=e)


@app.route('/get-vehicles')
def get_vehicles():
    location = request.args.get('location')
    type_id = request.args.get('type_id')

    if not location or not type_id:
        return jsonify([])
    cursor = db.cursor()
    cursor.execute(f"""SELECT v.reg_no,vt.class_type,vt.class,vt.status
                   from vehicles v
                   join vehicle_types vt on v.type_id = vt.type_id
                   where v.location = '{location}' and v.type_id = {type_id}""")
    result = cursor.fetchall()
    vehicles = []
    for data in result:
        vehicles.append(
            {
           'reg_no': data[0],
            'class_type': str(data[1]) + str(data[2]),
           'status': data[3]
            }
        )
    return jsonify(vehicles)

@app.route('/home/book-vehicle',methods=['GET', 'POST'])
def book_vehicle():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM vehicle_types")
        types = cursor.fetchall()
        vehicleClasses = {}
        for i in types:
            if i[1] not in vehicleClasses:
                    vehicleClasses[i[1]] = []
            vehicleClasses[i[1]].append(
                    {
                        'id' : i[0],
                        'name' : i[2],
                        'icon' : i[3],
                        'price' : str(i[5])+'0/day',
                        'features' : [feature.strip() for feature in i[4].split(',')]
                    }
                )
    except Exception as e:
        return render_template('error.html',error_message=e)
    if request.method == 'POST':   
        try: 
            pickup_date = request.form['pickup-date']
            pickup_time = request.form['pickup-time']
            return_date = request.form['return-date']
            return_time = request.form['return-time']
            id = request.form['vehicle-class-id']
            amount = request.form['amount']
            mode = request.form['payment-mode']
            result = True
            transaction_id = ""
            while result:
                now = datetime.now()
                formatted_time = now.strftime("%Y%m%d%H%M%S%f")[:]
                transaction_id = "TR"+formatted_time
                cursor = db.cursor()
                cursor.execute("select transaction_id from payments where transaction_id = %s",(transaction_id,))
                result = cursor.fetchone()
            try:
                cursor = db.cursor()
                cursor.execute("INSERT INTO payments(transaction_id,amount,payment_mode) VALUES (%s, %s,%s)", (transaction_id,amount,mode ))
                db.commit()
            except Exception as e:
                db.rollback()
                return render_template('error.html',error_message=e)
            result = True
            booking_id = ""
            while result:
                now = datetime.now()
                formatted_time = now.strftime("%Y%m%d%H%M%S%f")[:]
                booking_id = "BK"+formatted_time
                cursor = db.cursor()
                cursor.execute("select booking_id from bookings where booking_id = %s",(booking_id,))
                result = cursor.fetchone()
            try:
                cursor = db.cursor()
                cursor.execute("INSERT INTO bookings(transaction_id, pickup_date, pickup_time, return_date, return_time, user_id,booking_id,vehicle_id) VALUES (%s, %s,%s, %s,%s, %s,%s,%s)", (transaction_id, pickup_date, pickup_time, return_date, return_time,session['user_id'],booking_id,id))
                db.commit()
            except Exception as e:
                db.rollback()
                return render_template('error.html',error_message=e)
            return render_template('book-vehicle.html',vehicleClasses=vehicleClasses,booking_id = booking_id, transaction_id = transaction_id)
        except Exception as e:
            return render_template('error.html',error_message=e)
    return render_template('book-vehicle.html',vehicleClasses=vehicleClasses)

@app.route('/home/booking-history')
def booking_history():
    try:
        cursor = db.cursor()
        cursor.execute(f"""select b.booking_id,b.pickup_date,b.return_date,b.pickup_time,b.return_time,b.transaction_id,p.amount,p.payment_date,v.class_type,v.class,v.icon,v.features
                        from bookings b
                        join payments p on b.transaction_id = p.transaction_id
                        join vehicle_types v on b.vehicle_id = v.type_id
                        where user_id='{session['user_id']}'""")
        result = cursor.fetchall()
        booking_history = []
        for data in result:
            booking_history.append(
                {
                'booking_id': data[0],
                'pickup_date': data[1].strftime('%Y-%m-%d'),  # format date to string
                'return_date': data[2].strftime('%Y-%m-%d'),  # format date to string
                'pickup_time': str(data[3]),  # Convert timedelta to string
                'return_time': str(data[4]),  # Convert timedelta to string
                'transaction_id': data[5],
                'amount': str(data[6]),  # Convert float to string
                'payment_date': data[7].strftime('%Y-%m-%d %H:%M:%S'),  # format datetime to string
                'class_type': data[8],
                'class': data[9],
                'icon': data[10],
                'features': data[11]
                }
            )
        return render_template('booking_history.html',booking_history=booking_history)
    except Exception as e:
        return render_template('error.html',error_message=e)


@app.route('/home/feedback',methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        cursor = db.cursor()
        try:
            booking_id = request.form['booking_id']
            rating = request.form['rating']
            comments = request.form['comment']
            cursor.execute("INSERT INTO feedback(booking_id,rating,comments) VALUES (%s, %s,%s)", (booking_id,rating,comments))
            db.commit()
            return redirect(url_for('feedback'))
        except Exception as e:
            db.rollback()
            return render_template('error.html',error_message=e)
    try:
        cursor = db.cursor()
        cursor.execute(f"""select b.booking_id,v.class_type,v.class
                       from bookings b
                       join vehicle_types v on b.vehicle_id = v.type_id
                       where user_id='{session['user_id']}' 
                            and b.booking_id not in (select booking_id from feedback)
                            and b.return_date < CURDATE()
                       order by b.return_date desc""")
        result = cursor.fetchall()
        bookings = []
        for data in result:
            bookings.append(
                {
                'booking_id': data[0],
                'class_type': data[1],
                'class': data[2]
                }
            )
        cursor.execute(f"""select f.booking_id, f.rating,f.comments,f.feedback_date,v.class_type,v.class
                            from feedback f
                            join bookings b on f.booking_id = b.booking_id
                            join vehicle_types v on b.vehicle_id = v.type_id
                            where b.user_id='{ session['user_id']}'
                            order by f.feedback_date desc""")
        result = cursor.fetchall()
        feedback = []
        for data in result:
            feedback.append(
                {
                'booking_id': data[0],
                'rating': data[1],
                'comments': data[2],
                'feedback_date': data[3].strftime('%d-%m-%Y %H:%M'),  # format datetime to string
                'class_type': data[4],
                'class': data[5]
                }
            )
        return render_template('feedback.html',booking_ids=bookings,feedbacks=feedback)
    except Exception as e:
        return render_template('error.html',error_message=e)
    
@app.route('/home/report',methods=['GET', 'POST'])
def report():
    try: 
        cursor = db.cursor()
        cursor.execute(f"""select r.report_id,r.report_type,r.report_date,r.report_text
                        from report r
                        where user_id='{session['user_id']}'""")
        result = cursor.fetchall()
        reports = []
        for data in result:
            reports.append(
                {
                'report_id': data[0],
                'report_type': data[1],
                'report_date': data[2].strftime('%d-%m-%Y %H:%M'),  # format datetime to string
                'report_text': data[3]
                }
            )
    except Exception as e:
        return render_template('error.html',error_message=e)

    if request.method == 'POST':
        now = datetime.now()
        report_id = "RP"+str(now.strftime("%Y%m%d%H%M%S%f")[:])
        report_type = request.form['report_type']
        report_text = request.form['report_text']
        try:
            cursor = db.cursor()
            cursor.execute("INSERT INTO report(report_id,report_type,report_text,user_id) VALUES (%s, %s,%s,%s)", (report_id,report_type,report_text,session['user_id']))
            db.commit()
            return redirect(url_for('report'))
        except Exception as e:
            db.rollback()
            return render_template('error.html',error_message=e)
    return render_template('report.html',reports=reports)
    

@app.route('/home/profile',methods=['GET', 'POST'])
def profile():
    try:
        cursor = db.cursor()
        cursor.execute(f"""select * from users where user_id='{session['user_id']}'""")
        result = cursor.fetchone()
        user = {
            'user_id': result[0],
            'fname': result[1],
            'mname': result[2],
            'lname': result[3],
            'email': result[4],
            'password': result[5],
            'street': result[6],
            'city': result[7],
            'postal_code': result[8],
            'id_type': result[9],
            'id_number': result[10]
        }
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'update':    
                fname = request.form['fname']
                mname = request.form['mname']
                lname = request.form['lname']
                email = request.form['email']
                street = request.form['street']
                city = request.form['city']
                postal_code = request.form['postal_code']
                id_type = request.form['id_type']
                id_number = request.form['id_number']
                try:
                    cursor = db.cursor()
                    cursor.execute("UPDATE users SET fname = %s, mname = %s, lname = %s, email = %s, street = %s, city = %s, postal_code = %s, id_type = %s, id_number = %s WHERE user_id = %s", (fname, mname, lname, email, street, city, postal_code, id_type, id_number, session['user_id']))
                    db.commit()
                    return redirect(url_for('profile'))
                except Exception as e:
                    db.rollback()
                    return render_template('error.html',error_message=e)
            elif action == 'update_password':
                old_password = request.form['old_password']
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']

                if new_password != confirm_password:
                    return render_template('profile.html',result=user, error_message="Passwords do not match")
                else:
                    try:
                        cursor = db.cursor()
                        cursor.execute("SELECT password FROM users WHERE user_id = %s", (session['user_id'],))
                        result = cursor.fetchone()
                        if result[0] == old_password:
                            cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password, session['user_id']))
                            db.commit()
                            return redirect(url_for('profile'))
                        else:
                            return render_template('profile.html',result=user, error_message="Incorrect Password")
                    except Exception as e:
                        db.rollback()
                        return render_template('error.html',error_message=e)
    except Exception as e:
        return render_template('error.html',error_message=e)
    return render_template('profile.html',result=user)


if __name__=="__main__":
     app.run(host="0.0.0.0",port=5000,debug=True)
    
