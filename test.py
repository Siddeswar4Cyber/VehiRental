'''t=(('car01', 'car', 'Sedan', 'fas fa-car-side', '4-5 seats, Spacious trunk, Excellent fuel economy, Comfortable ride', 1800.0), ('car02', 'car', 'SUV', 'fas fa-suv', '5-7 seats, All-wheel drive, High ground clearance, Spacious interior', 2500.0), ('car03', 'car', 'Mini Car', 'fas fa-car', 'Compact size, 4 seats, Great for city driving, Excellent mileage', 1200.0), ('car04', 'car', 'Luxury', 'fas fa-gem', 'Premium brands, Leather seats, Advanced features, VIP service', 4500.0), ('bus01', 'bus', 'Mini Bus', 'fas fa-bus', '12-15 seats, AC available, Comfortable seating, Ideal for small groups', 3500.0), ('bus02', 'bus', 'Coach', 'fas fa-bus-alt', '30-50 seats, Luxury coach, Onboard toilet, Entertainment system', 6000.0), ('bus03', 'bus', 'School Bus', 'fas fa-bus-school', 'Safety features, 30-40 seats, Child-friendly, Reliable service', 4000.0), ('van01', 'van', 'Passenger Van', 'fas fa-shuttle-van', '8-12 seats, Spacious interior, Sliding doors, Family friendly', 2800.0), ('van02', 'van', 'Cargo Van', 'fas fa-truck-moving', 'Large cargo space, 2-3 seats, Diesel option, Loading ramp available', 2500.0), ('tempo01', 'tempo', 'Small Tempo', 'fas fa-truck-pickup', '1.5 ton capacity, Diesel engine, Easy maneuverability, Local transport', 2000.0), ('tempo02', 'tempo', 'Large Tempo', 'fas fa-truck', '3 ton capacity, Heavy duty, Long distance, Reliable service', 3500.0), ('bike01', 'bike', 'Royal Enfield', 'fas fa-motorcycle', '350-500cc, Classic style, Comfortable ride, Great for highways', 800.0), ('bike02', 'bike', 'Sports Bike', 'fas fa-motorcycle', 'High performance, 200-300cc, Great acceleration, Sporty look', 1200.0), ('bike03', 'bike', 'Scooter', 'fas fa-scooter', '80-125cc, Great mileage, Easy to ride, Perfect for city', 500.0), ('bike04', 'bike', 'Adventure Bike', 'fas fa-motorcycle', 'Off-road capable, Long travel suspension, Comfortable for long rides, 500cc+ engines', 1500.0))
vehicleClasses = {}
for i in t:
    if i[1] not in vehicleClasses:
            vehicleClasses[i[1]] = []
    vehicleClasses[i[1]].append(
            {
                'id' : i[0],
                'name' : i[2],
                'icon' : i[3],
                'price' : i[5],
                'features' : [feature.strip() for feature in i[4].split(',')]
            }
        )
    
print(vehicleClasses)



from datetime import datetime

# Current date and time with microseconds
now = datetime.now()
print(now)
# Format with milliseconds
formatted_time = now.strftime("%Y%m%d%H%M%S%f")[:]

print(len("TR"+str(formatted_time)))''''''
import MySQLdb
db = MySQLdb.connect(
    host="localhost",   # Change to your MySQL host
    user="root",       # Change to your MySQL username
    passwd="Mysqlroot@123", # Change to your MySQL password
    db="vehirental"       # Change to your MySQL Database Name
)

if True:
    if True:
        cursor = db.cursor()
        cursor.execute(f"""select r.report_id,r.report_type,r.report_date,r.report_text
                        from report r
                        where user_id='Siddeswar@123'""")
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
        print('Reports')
        print(reports)''''''cursor = db.cursor()
        cursor.execute(f"""select b.booking_id,v.class_type,v.class
                       from bookings b
                       join vehicle_types v on b.vehicle_id = v.type_id
                       where user_id='Siddeswar@123'""")
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
        print('Bookings')
        print(bookings)
        cursor.execute(f"""select f.booking_id, f.rating,f.comments,f.feedback_date,v.class_type,v.class
                            from feedback f
                            join bookings b on f.booking_id = b.booking_id
                            join vehicle_types v on b.vehicle_id = v.type_id
                            where b.user_id='Siddeswar@123'""")
        result = cursor.fetchall()
        feedback = []
        print('Feedback')
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
        print(feedback)
        
cursor = db.cursor()
cursor.execute(f"""select b.booking_id,b.pickup_date,b.return_date,b.pickup_time,b.return_time,b.transaction_id,p.amount,p.payment_date,v.class_type,v.class,v.icon,v.features
                        from bookings b
                        join payments p on b.transaction_id = p.transaction_id
                        join vehicle_types v on b.vehicle_id = v.type_id
                        where user_id='Siddeswar@123'""")
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
for booking in booking_history:
    print(booking)'''
    
import datetime

maintenance_id = 'MT'+str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[2:])
print(maintenance_id)   