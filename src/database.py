import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hotel_analytics")

# Merkezi Veritabanı URL'si
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_db_engine():
    """Tüm modüller için ortak SQLAlchemy Engine dönderir."""
    return create_engine(DATABASE_URL)
