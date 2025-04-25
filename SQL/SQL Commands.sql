-- Database selection
USE vehirental;

-- Users table
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

-- Vehicle types table
CREATE TABLE IF NOT EXISTS vehicle_types (
    type_id VARCHAR(10) PRIMARY KEY,
    class_type VARCHAR(15),
    class VARCHAR(25),
    icon VARCHAR(50),
    features VARCHAR(200),
    price DOUBLE
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    transaction_id VARCHAR(25) PRIMARY KEY,
    amount DOUBLE NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_mode VARCHAR(25),
    refund BOOLEAN DEFAULT 0
);

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    reg_no VARCHAR(15) PRIMARY KEY,
    type_id VARCHAR(25),
    status VARCHAR(10),
    location VARCHAR(6),
    next_maintenance_date DATE,
    FOREIGN KEY (type_id) REFERENCES vehicle_types(type_id)
);

-- Bookings table
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

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    booking_id VARCHAR(25),
    rating INT NOT NULL,
    comments VARCHAR(500),
    feedback_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- Report table
CREATE TABLE IF NOT EXISTS report (
    report_id VARCHAR(25) PRIMARY KEY,
    report_type VARCHAR(25),
    user_id VARCHAR(25),
    report_text VARCHAR(100),
    report_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Maintenance table
CREATE TABLE IF NOT EXISTS maintenance (
    maintenance_id VARCHAR(25) PRIMARY KEY,
    description VARCHAR(500),
    cost DOUBLE,
    vehicle_reg VARCHAR(25),
    maintenance_date DATE,
    FOREIGN KEY (vehicle_reg) REFERENCES vehicles(reg_no)
);

-- Triggers

-- Trigger for setting next maintenance date when inserting vehicles
DELIMITER //
CREATE TRIGGER IF NOT EXISTS set_next_maintenance_date
BEFORE INSERT ON vehicles
FOR EACH ROW
BEGIN
    IF NEW.next_maintenance_date IS NULL THEN
        SET NEW.next_maintenance_date = CURDATE() + INTERVAL 3 MONTH;
    END IF;
END//
DELIMITER ;

-- Trigger for setting maintenance date when inserting maintenance records
DELIMITER //
CREATE TRIGGER IF NOT EXISTS set_maintenance_date
BEFORE INSERT ON maintenance
FOR EACH ROW
BEGIN
    IF NEW.maintenance_date IS NULL THEN
        SET NEW.maintenance_date = CURDATE();
    END IF;
END//
DELIMITER ;

-- Insert initial data

-- Insert sample user
INSERT INTO users (user_id, fname, mname, lname, email, password, street, city, postal_code, id_type, id_number)
VALUES 
('S01', 'Siddeswar', NULL, 'Nimmala', 'S01@gmail.com', 'Siddhu@123', NULL, NULL, NULL, NULL, NULL),
('Admin01', 'Admin', NULL, 'User', 'siddeswar@gmail.com', 'Admin Password', NULL, NULL, NULL, NULL, NULL);

-- Insert vehicle types
INSERT INTO vehicle_types (type_id, class_type, class, icon, features, price) VALUES
('car01', 'car', 'Sedan', 'fas fa-car-side', '4-5 seats, Spacious trunk, Excellent fuel economy, Comfortable ride', 1800),
('car02', 'car', 'SUV', 'fas fa-suv', '5-7 seats, All-wheel drive, High ground clearance, Spacious interior', 2500),
('car03', 'car', 'Mini Car', 'fas fa-car', 'Compact size, 4 seats, Great for city driving, Excellent mileage', 1200),
('car04', 'car', 'Luxury', 'fas fa-gem', 'Premium brands, Leather seats, Advanced features, VIP service', 4500),
('bus01', 'bus', 'Mini Bus', 'fas fa-bus', '12-15 seats, AC available, Comfortable seating, Ideal for small groups', 3500),
('bus02', 'bus', 'Coach', 'fas fa-bus-alt', '30-50 seats, Luxury coach, Onboard toilet, Entertainment system', 6000),
('bus03', 'bus', 'School Bus', 'fas fa-bus-school', 'Safety features, 30-40 seats, Child-friendly, Reliable service', 4000),
('van01', 'van', 'Passenger Van', 'fas fa-shuttle-van', '8-12 seats, Spacious interior, Sliding doors, Family friendly', 2800),
('van02', 'van', 'Cargo Van', 'fas fa-truck-moving', 'Large cargo space, 2-3 seats, Diesel option, Loading ramp available', 2500),
('tempo01', 'tempo', 'Small Tempo', 'fas fa-truck-pickup', '1.5 ton capacity, Diesel engine, Easy maneuverability, Local transport', 2000),
('tempo02', 'tempo', 'Large Tempo', 'fas fa-truck', '3 ton capacity, Heavy duty, Long distance, Reliable service', 3500),
('bike01', 'bike', 'Royal Enfield', 'fas fa-motorcycle', '350-500cc, Classic style, Comfortable ride, Great for highways', 800),
('bike02', 'bike', 'Sports Bike', 'fas fa-motorcycle', 'High performance, 200-300cc, Great acceleration, Sporty look', 1200),
('bike03', 'bike', 'Scooter', 'fas fa-scooter', '80-125cc, Great mileage, Easy to ride, Perfect for city', 500),
('bike04', 'bike', 'Adventure Bike', 'fas fa-motorcycle', 'Off-road capable, Long travel suspension, Comfortable for long rides, 500cc+ engines', 1500);