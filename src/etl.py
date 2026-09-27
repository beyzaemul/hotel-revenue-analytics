import pandas as pd
from sqlalchemy import create_engine
import os
from src.database import get_db_engine

def run_etl():
    csv_path = "data/hotel_bookings.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Hata: {csv_path} bulunamadı!")
        return

    print("🔄 ETL Süreci Başlatılıyor...")
    
    # 1. CSV Okuma
    df = pd.read_csv(csv_path)
    print(f"📊 Okunan Ham Satır Sayısı: {len(df)}")

    # 2. Veri Temizleme ve Dönüştürme (Data Cleaning)
    
    # A. Eksik Değer Doldurma
    df['children'] = df['children'].fillna(0)
    df['country'] = df['country'].fillna('Unknown')

    # B. Ay isimlerini sayıya çevirme (July -> 7)
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['arrival_date_month_num'] = df['arrival_date_month'].map(month_map)

    # C. Giriş Tarihi (check_in_date) Oluşturma
    df['check_in_date'] = pd.to_datetime(
        df['arrival_date_year'].astype(str) + '-' + 
        df['arrival_date_month_num'].astype(str) + '-' + 
        df['arrival_date_day_of_month'].astype(str)
    )

    # D. Toplam Kalış Süresi ve Çıkış Tarihi (check_out_date)
    df['stays_duration'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    # En az 1 gece kalınmalı
    df['stays_duration'] = df['stays_duration'].replace(0, 1) 
    df['check_out_date'] = df['check_in_date'] + pd.to_timedelta(df['stays_duration'], unit='D')

    # E. Aykırı ve Hatalı Fiyat Filtreleme (0 ile 1000 EUR arası geçerli fiyatlar)
    df = df[(df['adr'] > 0) & (df['adr'] < 1000)]

    # 3. PostgreSQL Tablosuna Uygun Sütunları Seçme
    clean_df = pd.DataFrame({
        'hotel_type': df['hotel'],
        'is_canceled': df['is_canceled'],
        'lead_time': df['lead_time'],
        'check_in_date': df['check_in_date'],
        'check_out_date': df['check_out_date'],
        'stays_duration': df['stays_duration'],
        'adults': df['adults'],
        'children': df['children'].astype(int),
        'babies': df['babies'],
        'country': df['country'],
        'market_segment': df['market_segment'],
        'distribution_channel': df['distribution_channel'],
        'is_repeated_guest': df['is_repeated_guest'],
        'reserved_room_type': df['reserved_room_type'],
        'assigned_room_type': df['assigned_room_type'],
        'deposit_type': df['deposit_type'],
        'customer_type': df['customer_type'],
        'adr': df['adr'],
        'required_car_parking_spaces': df['required_car_parking_spaces'],
        'total_of_special_requests': df['total_of_special_requests']
    })

    print(f"✅ Temizlenmiş ve Aktarıma Hazır Satır Sayısı: {len(clean_df)}")

    # 4. PostgreSQL'e Verileri Basma
    engine = get_db_engine()
    clean_df.to_sql('reservations', engine, if_exists='append', index=False)
    
    print("🚀 Veriler PostgreSQL veritabanına başarıyla aktarıldı!")

if __name__ == "__main__":
    run_etl()
