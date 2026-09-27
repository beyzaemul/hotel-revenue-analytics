-- 1. Operasyonel Katman: Tüm rezervasyon kayıtlarının tutulacağı ana tablo
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id SERIAL PRIMARY KEY,
    hotel_type VARCHAR(50),
    is_canceled INT,
    lead_time INT,
    check_in_date DATE,
    check_out_date DATE,
    stays_duration INT,
    adults INT,
    children INT,
    babies INT,
    country VARCHAR(10),
    market_segment VARCHAR(50),
    distribution_channel VARCHAR(50),
    is_repeated_guest INT,
    reserved_room_type VARCHAR(10),
    assigned_room_type VARCHAR(10),
    deposit_type VARCHAR(50),
    customer_type VARCHAR(50),
    adr NUMERIC(10, 2), -- Günlük oda fiyatı (Küsüratlı olabileceği için NUMERIC)
    required_car_parking_spaces INT,
    total_of_special_requests INT
);

-- 2. Yönetimsel Katman: Günlük özetleri hazır hesaplanmış şekilde sunan VIEW
CREATE OR REPLACE VIEW view_daily_hotel_stats AS
SELECT 
    check_in_date AS stat_date,
    hotel_type,
    COUNT(reservation_id) AS total_bookings,
    SUM(CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END) AS active_bookings,
    SUM(CASE WHEN is_canceled = 1 THEN 1 ELSE 0 END) AS canceled_bookings,
    ROUND(AVG(CASE WHEN is_canceled = 0 THEN adr ELSE NULL END), 2) AS avg_daily_rate,
    ROUND(SUM(CASE WHEN is_canceled = 0 THEN adr * stays_duration ELSE 0 END), 2) AS total_revenue
FROM reservations
GROUP BY check_in_date, hotel_type;