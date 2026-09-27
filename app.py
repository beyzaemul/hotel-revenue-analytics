import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os

from src.database import get_db_engine
from src.excel_exporter import export_management_report

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Otel Gelir Yönetimi ve Fiyatlandırma Portalı",
    page_icon="🏨",
    layout="wide"
)

st.title("🏨 Otel Gelir Yönetimi ve Dinamik Fiyatlandırma Portalı")
st.caption("Tahmin modelleri ve otomatik raporlama paneli.")
st.markdown("---")

# Veritabanı Bağlantısı
engine = get_db_engine()

# Metin Dönüştürme Sözlükleri (Grafik ve Filtre İsimlerini Türkçeleştirme)
HOTEL_MAPPING = {
    "Resort Hotel": "Tatil Köyü (Resort)",
    "City Hotel": "Şehir Oteli"
}
REVERSE_HOTEL_MAPPING = {v: k for k, v in HOTEL_MAPPING.items()}

# --- VERİ YÜKLEME ---
@st.cache_data(ttl=600)
def load_data():
    query = "SELECT * FROM view_daily_hotel_stats ORDER BY stat_date DESC;"
    df = pd.read_sql(query, engine)
    df['stat_date'] = pd.to_datetime(df['stat_date'])
    # Görselleştirme için otel isimlerini Türkçeleştirme
    df['otel_tipi_tr'] = df['hotel_type'].map(HOTEL_MAPPING).fillna(df['hotel_type'])
    return df

df_stats = load_data()

# --- SEKMELER (TABS) ---
tab1, tab2, tab3 = st.tabs(["📊 Genel Bakış ve Performans", "🤖 Dinamik Fiyat & İptal Riski Tahmini", "📄 Yönetim Raporlama"])

# ==========================================
# SEME 1: DASHBOARD VE GRAFİKLER
# ==========================================
with tab1:
    st.subheader("📌 Performans ve Gelir Analizi")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        secilen_oteller = st.multiselect(
            "Otel Tipi Seçin:", 
            options=list(HOTEL_MAPPING.values()), 
            default=list(HOTEL_MAPPING.values())
        )
    with col_f2:
        min_date = df_stats['stat_date'].min().date()
        max_date = df_stats['stat_date'].max().date()
        date_range = st.date_input("Tarih Aralığı Seçin:", [min_date, max_date], min_value=min_date, max_value=max_date, format="DD/MM/YYYY")

    # Filtreleme İşlemi
    if len(date_range) == 2:
        start_d, end_d = date_range
        filtered_df = df_stats[
            (df_stats['otel_tipi_tr'].isin(secilen_oteller)) &
            (df_stats['stat_date'].dt.date >= start_d) &
            (df_stats['stat_date'].dt.date <= end_d)
        ]
    else:
        filtered_df = df_stats

    # KPI Metrik Kartları
    tot_revenue = filtered_df['total_revenue'].sum()
    avg_adr = filtered_df['avg_daily_rate'].mean()
    tot_bookings = filtered_df['total_bookings'].sum()
    tot_canceled = filtered_df['canceled_bookings'].sum()
    cancel_rate = (tot_canceled / tot_bookings * 100) if tot_bookings > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Gelir", f"€{tot_revenue:,.2f}")
    m2.metric("Ortalama Günlük Oda Fiyatı", f"€{avg_adr:.2f}")
    m3.metric("Toplam Rezervasyon", f"{tot_bookings:,}")
    m4.metric("İptal Oranı", f"%{cancel_rate:.1f}")

    st.markdown("---")

    # Grafikler (Eksenler ve Başlıklar Tamamen Türkçe)
    c1, c2 = st.columns(2)
    with c1:
        fig_revenue = px.line(
            filtered_df, x='stat_date', y='total_revenue', color='otel_tipi_tr',
            title="Günlük Toplam Gelir Trendi (€)",
            labels={
                'stat_date': 'Tarih', 
                'total_revenue': 'Toplam Gelir (€)', 
                'otel_tipi_tr': 'Otel Tipi'
            }
        )
        st.plotly_chart(fig_revenue, use_container_width=True)

    with c2:
        fig_adr = px.box(
            filtered_df, x='otel_tipi_tr', y='avg_daily_rate', color='otel_tipi_tr',
            title="Otel Tiplerine Göre Günlük Oda Fiyatı Dağılımı (€)",
            labels={
                'otel_tipi_tr': 'Otel Tipi', 
                'avg_daily_rate': 'Ortalama Günlük Oda Fiyatı (€)'
            }
        )
        st.plotly_chart(fig_adr, use_container_width=True)

# ==========================================
# SEKME 2: ML DİNAMİK FİYAT & İPTAL TAHMİNİ
# ==========================================
with tab2:
    st.subheader("💡 Yapay Zeka Tabanlı Oda Fiyatı ve İptal Riski Öneri Motoru")
    st.caption("Müşteri ve rezervasyon detaylarını girerek önerilen ideal oda fiyatını ve iptal olasılığını anlık olarak hesaplayın.")

    if not os.path.exists('models/price_model.pkl') or not os.path.exists('models/cancel_model.pkl'):
        st.warning("⚠️ Model dosyaları bulunamadı! Lütfen önce `python src/pricing_model.py` komutunu çalıştırarak modelleri eğitin.")
    else:
        price_model = joblib.load('models/price_model.pkl')
        cancel_model = joblib.load('models/cancel_model.pkl')

        # Türkçe SEÇENEKLER SÖZLÜĞÜ (Kullanıcı Türkçe görür, Model Arka Planda Orijinal İngilizce Veriyi Alır)
        CUSTOMER_TYPES = {
            "Bireysel Müşteri": "Transient",
            "Grup Konaklaması": "Group",
            "Sözleşmeli / Kurumsal Konaklama": "Contract",
            "Etkinlik / Kafile Grubu": "Transient-Party"
        }

        MARKET_SEGMENTS = {
            "Online Seyahat Acentesi (Booking/Expedia vb.)": "Online TA",
            "Çevrimdışı Acente / Tur Operatörü": "Offline TA/TO",
            "Doğrudan Başvuru (Otel Web Sitesi/Resepsiyon)": "Direct",
            "Kurumsal Anlaşma": "Corporate",
            "Promosyon / Ücretsiz": "Complementary"
        }

        DEPOSIT_TYPES = {
            "Depozitosuz": "No Deposit",
            "İadesiz Depozito (Ön Ödemeli)": "Non Refund",
            "İade Edilebilir Depozito": "Refundable"
        }

        with st.form("prediction_form"):
            col_in1, col_in2, col_in3 = st.columns(3)
            
            with col_in1:
                hotel_type_tr = st.selectbox("Otel Tipi", list(HOTEL_MAPPING.values()))
                lead_time = st.number_input("Erken Rezervasyon Süresi (Kaç Gün Önce?)", min_value=0, max_value=700, value=30)
                stays_duration = st.number_input("Toplam Konaklama Gecesi", min_value=1, max_value=30, value=3)

            with col_in2:
                adults = st.number_input("Yetişkin Sayısı", min_value=1, max_value=10, value=2)
                children = st.number_input("Çocuk Sayısı", min_value=0, max_value=10, value=0)
                customer_type_tr = st.selectbox("Müşteri Segmet / Tipi", list(CUSTOMER_TYPES.keys()))

            with col_in3:
                market_segment_tr = st.selectbox("Satış / Rezervasyon Kanalı", list(MARKET_SEGMENTS.keys()))
                deposit_type_tr = st.selectbox("Depozito ve Ödeme Koşulu", list(DEPOSIT_TYPES.keys()))

            submit_btn = st.form_submit_button("🚀 Tahmin Et ve Fiyat Öner")

        if submit_btn:
            # Kullanıcının seçtiği Türkçe değerleri, ML Modelinin beklediği orijinal değerlere çeviriyoruz
            input_data = pd.DataFrame([{
                'hotel_type': REVERSE_HOTEL_MAPPING[hotel_type_tr],
                'lead_time': lead_time,
                'stays_duration': stays_duration,
                'adults': adults,
                'children': children,
                'market_segment': MARKET_SEGMENTS[market_segment_tr],
                'deposit_type': DEPOSIT_TYPES[deposit_type_tr],
                'customer_type': CUSTOMER_TYPES[customer_type_tr]
            }])

            # Tahminler
            pred_price = price_model.predict(input_data)[0]
            pred_cancel_prob = cancel_model.predict_proba(input_data)[0][1] * 100

            st.markdown("---")
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.success(f"### 🎯 Önerilen İdeal Oda Fiyatı: **€{pred_price:.2f}**")
            
            with res_col2:
                if pred_cancel_prob > 50:
                    st.error(f"### ⚠️ Tahmini İptal Riski: **%{pred_cancel_prob:.1f}** (Yüksek Risk)")
                else:
                    st.info(f"### ✅ Tahmini İptal Riski: **%{pred_cancel_prob:.1f}** (Düşük Risk)")

# ==========================================
# SEKME 3: YÖNETİM RAPORLAMA
# ==========================================
with tab3:
    st.subheader("📑 Yönetim İçin Otomatik Excel Raporlayıcı")
    st.write("Veritabanındaki en güncel özet verileri biçimlendirilmiş kurumsal Excel dosyası olarak oluşturun ve indirin.")

    if st.button("📊 Güncel Excel Raporunu Üret"):
        with st.spinner("Rapor oluşturuluyor, lütfen bekleyin..."):
            export_management_report()
            report_path = "reports/Hotel_Revenue_Management_Report.xlsx"
            
            if os.path.exists(report_path):
                with open(report_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Excel Raporunu İndir (.xlsx)",
                        data=file,
                        file_name="Otel_Gelir_Yonetimi_Raporu.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                st.success("Rapor başarıyla üretildi!")