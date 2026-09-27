import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

from src.database import get_db_engine

def train_and_save_models():
    print("📥 Veritabanından Model Verisi Çekiliyor...")
    engine = get_db_engine()
    
    query = """
    SELECT 
        hotel_type,
        lead_time,
        stays_duration,
        adults,
        children,
        market_segment,
        deposit_type,
        customer_type,
        is_canceled,
        adr
    FROM reservations;
    """
    
    df = pd.read_sql(query, engine)
    
    if df.empty:
        print("❌ Hata: Veri çekilemedi!")
        return

    print(f"📊 {len(df)} Satır Veri İle Model Eğitimi Başlıyor...")

    # Özellikler (Features) ve Hedefler (Targets)
    X = df[['hotel_type', 'lead_time', 'stays_duration', 'adults', 'children', 'market_segment', 'deposit_type', 'customer_type']]
    y_price = df['adr']          # Fiyat tahmini hedefi
    y_cancel = df['is_canceled'] # İptal riski hedefi

    # Kategorik Değişkenler İçin Dönüştürücü (OneHotEncoder)
    categorical_features = ['hotel_type', 'market_segment', 'deposit_type', 'customer_type']
    numeric_features = ['lead_time', 'stays_duration', 'adults', 'children']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )

    # 1. Dinamik Fiyat Tahmin Modeli Pipeline
    price_model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1))
    ])

    # 2. İptal Riski Tahmin Modeli Pipeline
    cancel_model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1))
    ])

    # Eğitim ve Test Parçalaması
    X_train, X_test, y_price_train, y_price_test, y_cancel_train, y_cancel_test = train_test_split(
    X, y_price, y_cancel, test_size=0.2, random_state=42
)

    print("🤖 1. Fiyat Tahmin Modeli Eğitiliyor (Random Forest Regressor)...")
    price_model.fit(X_train, y_price_train)

    print("🤖 2. İptal Riski Modeli Eğitiliyor (Random Forest Classifier)...")
    cancel_model.fit(X_train, y_cancel_train)

    # Modelleri 'models/' Klasörüne Kaydetme
    os.makedirs('models', exist_ok=True)
    joblib.dump(price_model, 'models/price_model.pkl')
    joblib.dump(cancel_model, 'models/cancel_model.pkl')

    print("🚀 Modeller Başarıyla Eğitildi ve 'models/' Klasörüne Kaydedildi!")

if __name__ == "__main__":
    train_and_save_models()
