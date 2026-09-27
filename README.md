# 🏨 Otel Gelir Yönetimi ve Dinamik Fiyatlandırma Portalı

Bu proje, otel işletmeleri için geliştirilmiş **veri analitiği, makine öğrenmesi tabanlı fiyatlandırma/iptal riski tahmini** ve **yönetim raporlama** sunan Streamlit web portalıdır.


## 📌 Özellikler

* **📊 Genel Bakış:** Günlük gelir, ortalama oda fiyatı (ADR), rezervasyon ve iptal oranlarını gösteren KPI kartları ve interaktif grafikler.
* **🤖 Yapay Zeka Tahmini:** Oda fiyatı (€) ve iptal olasılığını (%) tahmin eden Random Forest modelleri.
* **📄 Yönetim Raporlama:** Veritabanındaki güncel verileri biçimlendirilmiş Excel (`.xlsx`) raporu olarak indirme imkanı.
* **📈 Excel Dashboard:** Veri özetleri ve dinamik filtreler içeren Excel paneli.


## 🛠️ Teknolojiler

* **Arayüz:** Streamlit, Plotly
* **Veri & ML:** Pandas, Scikit-Learn, Joblib
* **Veritabanı:** PostgreSQL, SQLAlchemy
* **Raporlama:** OpenPyXL


## 📁 Proje Mimarisi

```text
hotel-revenue-analytics/
├── app.py                  # Streamlit Web Arayüzü
├── requirements.txt        # Paket Bağımlılıkları
├── .gitignore              # Gizlenecek Dosyalar
├── src/                    # Veritabanı, ML ve Raporlama Kodları
├── models/                 # Eğitilmiş ML Modelleri (.pkl)
├── sql/                    # SQL Dosyaları
├── data/                   # Ham Veri Seti
└── reports/                # Excel Raporları ve Görseller