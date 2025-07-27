import os
import MySQLdb

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

def main():
    # Connect to DB with env vars
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

if __name__ == '__main__':
    main()
