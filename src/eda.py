import pandas as pd
import os

CSV_PATH = "data/hotel_bookings.csv"

def inspect_raw_data():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Dosya bulunamadı: {CSV_PATH}")
        return

    print("📊 Ham Veri Yükleniyor...\n")
    df = pd.read_csv(CSV_PATH)

    print(f"🔹 Toplam Satır Sayısı: {df.shape[0]}")
    print(f"🔹 Toplam Sütun Sayısı: {df.shape[1]}")
    
    print("\n--- İLK 5 SATIR ---")
    print(df[['hotel', 'is_canceled', 'lead_time', 'arrival_date_year', 'arrival_date_month', 'adr', 'market_segment']].head())

    print("\n--- EKSİK (NULL) DEĞER İÇEREN SÜTUNLAR ---")
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0]
    if not missing_data.empty:
        print(missing_data)
    else:
        print("Eksik veri bulunamadı.")

    print("\n--- FİYAT (ADR) VE İPTAL İSTATİSTİKLERİ ---")
    print(df[['adr', 'lead_time', 'is_canceled']].describe())

if __name__ == "__main__":
    inspect_raw_data()
