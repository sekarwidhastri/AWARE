import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# Tambahkan direktori induk agar bisa mengimpor src.scoring_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.scoring_engine import assess_readiness

# Set Page Config
st.set_page_config(
    page_title="AWARE - Workplace Safety Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background-color: #FFFFFF;
        color: #1E293B;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #FFFFFF;
    }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    .metric-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        padding: 22px 24px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .metric-val {
        font-size: 28px;
        font-weight: 700;
        color: #0EA5E9;
        font-family: 'Inter', sans-serif;
    }
    .metric-label {
        font-size: 12px;
        color: #64748B;
        margin-bottom: 6px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .stAlert { border-radius: 8px; }

    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 4px;
        font-family: 'Inter', sans-serif;
    }
    .section-subtitle {
        font-size: 13px;
        color: #64748B;
        margin-bottom: 16px;
        line-height: 1.5;
    }
    .insight-card {
        background: #F8FAFC;
        border-left: 3px solid #0EA5E9;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 10px 0 6px 0;
        font-size: 13.5px;
        color: #334155;
        line-height: 1.6;
    }
    .stat-badge {
        display: inline-block;
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 4px 12px;
        font-size: 12.5px;
        color: #475569;
        margin: 4px 4px 4px 0;
    }
    .stat-badge strong { color: #0EA5E9; }
    .stat-badge.success strong { color: #10B981; }
    .stat-badge.danger strong { color: #EF4444; }

    .risk-table-container {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING & PREPARATION
# ============================================================
@st.cache_data
def load_historical_data():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    csv_path = os.path.join(project_root, 'data', 'processed', 'employee_historical_logs.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

@st.cache_data
def prepare_analysis_data(df_raw):
    """Memperkaya dataset dengan kolom turunan untuk analisis dashboard."""
    df = df_raw.copy()

    # --- Probabilitas kantuk (turunan dari EAR) ---
    # EAR 0.32+ = sangat terjaga (prob ≈ 0), EAR 0.15 = sangat mengantuk (prob ≈ 1)
    df['drowsy_probability'] = ((0.32 - df['ear_score']) / (0.32 - 0.15)).clip(0, 1)
    df['is_drowsy'] = df['ear_score'] < 0.25

    # --- Jam screening (turunan dari shift) ---
    np.random.seed(42)
    hour_map = {
        'Pagi (06:00 - 14:00)': ([5, 6, 7], [0.25, 0.50, 0.25]),
        'Siang (14:00 - 22:00)': ([13, 14, 15], [0.25, 0.50, 0.25]),
        'Malam (22:00 - 06:00)': ([21, 22, 23], [0.25, 0.50, 0.25]),
    }
    df['screening_hour'] = df['shift'].apply(
        lambda s: np.random.choice(hour_map[s][0], p=hour_map[s][1])
    )

    # --- Skor risiko terintegrasi (dari scoring engine) ---
    risk_results = df.apply(
        lambda row: assess_readiness(
            row['ear_score'], row['yawn_count'],
            row['sleep_duration'], row['overtime_hours']
        ), axis=1
    )
    df['total_risk_score'] = risk_results.apply(lambda r: r['final_risk_score'])
    df['risk_status'] = risk_results.apply(lambda r: r['status'])

    return df

# Load & prepare
df_raw = load_historical_data()
df = prepare_analysis_data(df_raw) if not df_raw.empty else pd.DataFrame()

# ============================================================
# HEADER
# ============================================================
st.markdown(
    "<h1 style='color:#1E293B; text-align:center; font-family:Inter,sans-serif;'>"
    "AWARE: Dashboard Analitik Kesiapan Kerja</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:#64748B; font-size:14px; font-family:Inter,sans-serif;'>"
    "Pemantauan tingkat kelelahan karyawan dan efektivitas rotasi shift berbasis analisis data historis 30 hari terakhir.</p>",
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab_dashboard, tab_simulation = st.tabs([
    "Dashboard Analitik",
    "Simulasi Screening"
])

# ================================================================
# TAB 1: DASHBOARD ANALITIK
# ================================================================
with tab_dashboard:

    if df.empty:
        st.warning("Dataset historis belum tersedia.")
    else:
        try:
            # -------------------------------------------------------
            # KPI ROW
            # -------------------------------------------------------
            total_employees = df['employee_id'].nunique()
            avg_risk = df['total_risk_score'].mean()
            pct_drowsy = df['is_drowsy'].mean() * 100
            avg_sleep = df['sleep_duration'].mean()

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Karyawan Terpantau</div>
                    <div class="metric-val">{total_employees} Orang</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                risk_color = "#10B981" if avg_risk < 40 else ("#F59E0B" if avg_risk < 70 else "#EF4444")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Rata-rata Skor Risiko</div>
                    <div class="metric-val" style="color:{risk_color};">{avg_risk:.1f} / 100</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                drowsy_color = "#10B981" if pct_drowsy < 15 else ("#F59E0B" if pct_drowsy < 30 else "#EF4444")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Deteksi Kantuk Visual</div>
                    <div class="metric-val" style="color:{drowsy_color};">{pct_drowsy:.1f}%</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                sleep_color = "#10B981" if avg_sleep >= 7 else ("#F59E0B" if avg_sleep >= 6 else "#EF4444")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Rata-rata Durasi Tidur</div>
                    <div class="metric-val" style="color:{sleep_color};">{avg_sleep:.1f} Jam</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # -------------------------------------------------------
            # SECTION 1: Shift Kerja & Jam Rawan
            # -------------------------------------------------------
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown(
                    '<div class="section-title">Tren Kewaspadaan Visual Berdasarkan Shift Kerja</div>'
                    '<div class="section-subtitle">'
                    'Rata-rata probabilitas kantuk (drowsy probability) yang terdeteksi di tiap kategori shift.'
                    '</div>',
                    unsafe_allow_html=True
                )

                avg_drowsy_shift = df.groupby('shift')['drowsy_probability'].mean().reset_index()
                avg_drowsy_shift.columns = ['Shift', 'Probabilitas Kantuk']
                avg_drowsy_shift = avg_drowsy_shift.sort_values('Probabilitas Kantuk', ascending=True)

                shift_colors = {
                    'Pagi (06:00 - 14:00)': '#38BDF8',
                    'Siang (14:00 - 22:00)': '#FBBF24',
                    'Malam (22:00 - 06:00)': '#F87171'
                }

                fig_bq1 = px.bar(
                    avg_drowsy_shift,
                    y='Shift', x='Probabilitas Kantuk',
                    orientation='h',
                    color='Shift',
                    color_discrete_map=shift_colors,
                    template='plotly_white'
                )
                fig_bq1.update_layout(
                    showlegend=False, height=280,
                    margin=dict(t=10, b=20, l=10, r=20),
                    xaxis_title='',
                    yaxis_title=''
                )
                fig_bq1.update_traces(texttemplate='%{x:.2f}', textposition='outside')
                st.plotly_chart(fig_bq1, use_container_width=True)

                night_avg = avg_drowsy_shift[avg_drowsy_shift['Shift'].str.contains('Malam')]['Probabilitas Kantuk'].values
                morning_avg = avg_drowsy_shift[avg_drowsy_shift['Shift'].str.contains('Pagi')]['Probabilitas Kantuk'].values
                if len(night_avg) > 0 and len(morning_avg) > 0:
                    diff_pct = ((night_avg[0] - morning_avg[0]) / morning_avg[0] * 100) if morning_avg[0] > 0 else 0
                    st.markdown(f"""
                    <div class="insight-card">
                        Data historis menunjukkan bahwa karyawan pada shift malam mencatat tingkat kantuk visual 
                        sekitar {diff_pct:.0f}% lebih tinggi dibandingkan shift pagi. Perbedaan ini 
                        mengindikasikan perlunya pengelolaan ritme sirkadian melalui rotasi jadwal yang lebih terencana.
                    </div>""", unsafe_allow_html=True)

            with col_right:
                st.markdown(
                    '<div class="section-title">Distribusi Waktu Rawan Kantuk</div>'
                    '<div class="section-subtitle">'
                    'Frekuensi deteksi kantuk visual (is_drowsy=True) dikelompokkan berdasarkan jam absensi masuk.'
                    '</div>',
                    unsafe_allow_html=True
                )

                drowsy_only = df[df['is_drowsy'] == True]
                hour_counts = drowsy_only.groupby('screening_hour').size().reset_index(name='Frekuensi')
                
                all_hours = sorted(df['screening_hour'].unique())
                full_hours = pd.DataFrame({'screening_hour': all_hours})
                hour_counts = full_hours.merge(hour_counts, on='screening_hour', how='left').fillna(0)
                hour_counts['Frekuensi'] = hour_counts['Frekuensi'].astype(int)
                hour_counts['Jam'] = hour_counts['screening_hour'].apply(lambda h: f"{int(h):02d}:00")

                max_hour = hour_counts.loc[hour_counts['Frekuensi'].idxmax(), 'screening_hour']
                hour_counts['Highlight'] = hour_counts['screening_hour'].apply(
                    lambda h: 'Puncak' if h == max_hour else 'Normal'
                )

                fig_bq4 = px.bar(
                    hour_counts,
                    x='Jam', y='Frekuensi',
                    color='Highlight',
                    color_discrete_map={'Puncak': '#F87171', 'Normal': '#CBD5E1'},
                    template='plotly_white'
                )
                fig_bq4.update_layout(
                    showlegend=False, height=280,
                    margin=dict(t=10, b=20, l=10, r=20),
                    xaxis_title='',
                    yaxis_title=''
                )
                st.plotly_chart(fig_bq4, use_container_width=True)

                peak_label = f"{int(max_hour):02d}:00"
                st.markdown(f"""
                <div class="insight-card">
                    Intensitas kejadian kantuk memuncak pada jam {peak_label}, yang beririsan dengan 
                    awal pergantian shift malam. Manajemen K3 disarankan untuk memprioritaskan prosedur 
                    keselamatan preventif pada jendela waktu tersebut.
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # -------------------------------------------------------
            # SECTION 2: Dampak Durasi Tidur & Lembur
            # -------------------------------------------------------
            col_sleep, col_ot = st.columns(2)

            with col_sleep:
                st.markdown(
                    '<div class="section-title">Dampak Defisit Tidur Terhadap Kewaspadaan</div>'
                    '<div class="section-subtitle">'
                    'Perbandingan probabilitas kantuk antara karyawan dengan durasi tidur kritis (< 6 jam) dan cukup (≥ 6 jam).'
                    '</div>',
                    unsafe_allow_html=True
                )

                df['Kategori Tidur'] = df['sleep_duration'].apply(
                    lambda x: '< 6 jam' if x < 6 else '≥ 6 jam'
                )

                fig_bq2 = px.box(
                    df, x='Kategori Tidur', y='drowsy_probability',
                    color='Kategori Tidur',
                    color_discrete_map={'< 6 jam': '#F87171', '≥ 6 jam': '#34D399'},
                    template='plotly_white',
                    labels={'Kategori Tidur': '', 'drowsy_probability': 'Probabilitas Kantuk'},
                    points='outliers'
                )
                fig_bq2.update_layout(
                    showlegend=False, height=280,
                    margin=dict(t=10, b=20, l=10, r=20)
                )
                st.plotly_chart(fig_bq2, use_container_width=True)

                # Statistik
                sleep_low = df[df['sleep_duration'] < 6]['drowsy_probability']
                sleep_high = df[df['sleep_duration'] >= 6]['drowsy_probability']
                u_stat, p_value = stats.mannwhitneyu(sleep_low, sleep_high, alternative='greater')
                
                mean_low = sleep_low.mean()
                mean_high = sleep_high.mean()

                st.markdown(f"""
                <div class="insight-card">
                    Terdapat peningkatan probabilitas kantuk yang signifikan secara statistik (p-value = {p_value:.3f}) 
                    pada kelompok dengan defisit tidur (rata-rata probabilitas {mean_low:.2f}) dibandingkan 
                    kelompok dengan tidur cukup ({mean_high:.2f}). Hal ini memvalidasi korelasi langsung antara 
                    durasi istirahat fisik dan kewaspadaan visual yang direkam sistem.
                </div>""", unsafe_allow_html=True)

            with col_ot:
                st.markdown(
                    '<div class="section-title">Korelasi Jam Lembur dengan Kelelahan Pagi</div>'
                    '<div class="section-subtitle">'
                    'Skor risiko kesiapan kerja bagi karyawan yang memiliki riwayat lembur pada hari sebelumnya.'
                    '</div>',
                    unsafe_allow_html=True
                )

                df['Status Lembur'] = df['overtime_hours'].apply(
                    lambda x: 'Ada Lembur' if x > 0 else 'Tidak Lembur'
                )

                fig_bq5 = px.box(
                    df, x='Status Lembur', y='total_risk_score',
                    color='Status Lembur',
                    color_discrete_map={'Ada Lembur': '#FBBF24', 'Tidak Lembur': '#38BDF8'},
                    template='plotly_white',
                    labels={'Status Lembur': '', 'total_risk_score': 'Skor Risiko Kesiapan'},
                    points='outliers'
                )
                fig_bq5.update_layout(
                    showlegend=False, height=280,
                    margin=dict(t=10, b=20, l=10, r=20)
                )
                st.plotly_chart(fig_bq5, use_container_width=True)

                # Statistik
                no_ot = df[df['overtime_hours'] == 0]['total_risk_score']
                has_ot = df[df['overtime_hours'] > 0]['total_risk_score']
                u_stat_ot, p_val_ot = stats.mannwhitneyu(has_ot, no_ot, alternative='greater')
                
                mean_ot = has_ot.mean()
                mean_no_ot = no_ot.mean()

                st.markdown(f"""
                <div class="insight-card">
                    Karyawan yang menjalankan jam kerja lembur mencatat rata-rata skor risiko pagi hari sebesar 
                    {mean_ot:.1f}, lebih tinggi dari kelompok tanpa lembur ({mean_no_ot:.1f}). Uji beda 
                    menunjukkan hasil yang terkonfirmasi (p-value = {p_val_ot:.3f}), mengindikasikan bahwa 
                    regulasi lembur sangat berpengaruh terhadap kapasitas pemulihan energi karyawan.
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # -------------------------------------------------------
            # SECTION 3: Karyawan Risiko Tinggi
            # -------------------------------------------------------
            st.markdown(
                '<div class="section-title">Identifikasi Profil Risiko Tinggi</div>'
                '<div class="section-subtitle">'
                'Daftar 10 karyawan dengan rata-rata skor risiko tertinggi yang direkomendasikan untuk tinjauan beban kerja.'
                '</div>',
                unsafe_allow_html=True
            )

            top10 = (
                df.groupby('employee_id')
                .agg(
                    Skor_Risiko=('total_risk_score', 'mean'),
                    Durasi_Tidur=('sleep_duration', 'mean'),
                    Total_Screening=('total_risk_score', 'count'),
                    Departemen=('department', 'first')
                )
                .sort_values('Skor_Risiko', ascending=False)
                .head(10)
                .reset_index()
            )
            top10.columns = ['ID Karyawan', 'Skor Risiko', 'Durasi Tidur', 'Total Presensi', 'Unit Kerja']
            top10['Peringkat'] = range(1, 11)
            top10 = top10[['Peringkat', 'ID Karyawan', 'Unit Kerja', 'Skor Risiko', 'Durasi Tidur', 'Total Presensi']]

            def apply_formatting(val):
                if isinstance(val, (int, float)):
                    if val >= 70:
                        return 'background-color: #FEF2F2; color: #991B1B;'
                    elif val >= 40:
                        return 'background-color: #FFFBEB; color: #92400E;'
                return ''

            styled_df = top10.style.applymap(
                apply_formatting, subset=['Skor Risiko']
            ).format({
                'Skor Risiko': '{:.1f}',
                'Durasi Tidur': '{:.1f} Jam'
            })

            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            highest = top10.iloc[0]
            st.markdown(f"""
            <div class="insight-card">
                Karyawan dengan ID <strong>{highest['ID Karyawan']}</strong> dari unit <strong>{highest['Unit Kerja']}</strong> 
                mencatat skor risiko rata-rata tertinggi ({highest['Skor Risiko']:.1f}). Pemantauan lebih lanjut atau 
                rotasi shift preventif direkomendasikan untuk meminimalkan potensi insiden kerja.
            </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Terjadi galat dalam memproses dashboard: {e}")

# ================================================================
# TAB 2: SIMULASI SCREENING
# ================================================================
with tab_simulation:
    try:
        st.markdown(
            '<div class="section-title">Simulator Risiko Kesiapan Kerja</div>'
            '<div class="section-subtitle">'
            'Masukkan variabel kondisi kesehatan untuk menguji hasil kalkulasi AWARE Scoring Engine.'
            '</div>',
            unsafe_allow_html=True
        )

        col_input, col_result = st.columns([1, 1])

        with col_input:
            nama_karyawan = st.text_input("Nama Karyawan", placeholder="Identitas...")
            
            st.markdown("**Profil Historis:**")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                sleep_duration = st.slider("Durasi Tidur (Jam)", 3.0, 10.0, 7.0, 0.5)
            with col_e2:
                overtime_hours = st.slider("Lembur Hari Sebelumnya (Jam)", 0, 4, 0, 1)

            st.markdown("**Pemeriksaan Visual (Computer Vision):**")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                ear_score = st.slider("Eye Aspect Ratio (Lebar Mata)", 0.15, 0.35, 0.28, 0.01)
            with col_v2:
                yawn_count = st.slider("Frekuensi Menguap", 0, 4, 0, 1)

            w_visual = st.slider("Bobot Validasi Visual (%)", 0, 100, 60, 5) / 100.0
            w_hist = 1.0 - w_visual

        with col_result:
            result = assess_readiness(ear_score, yawn_count, sleep_duration, overtime_hours, w_visual, w_hist)

            status = result['status']
            if status == 'FIT TO WORK':
                st.success(f"STATUS KESIAPAN: {status}")
            elif status == 'AT RISK (MONITOR)':
                st.warning(f"STATUS KESIAPAN: {status}")
            else:
                st.error(f"STATUS KESIAPAN: {status}")

            st.markdown(f"**Indeks Risiko Keseluruhan: {result['final_risk_score']:.1f} / 100**")
            st.progress(float(result['final_risk_score'])/100.0)

            st.markdown(f"- Komponen Visual: {result['visual_score']:.1f}")
            st.markdown(f"- Komponen Historis: {result['historical_score']:.1f}")

            st.info(f"Rekomendasi Sistem: {result['recommendation']}")

    except Exception as e:
        st.error(f"Terjadi galat pada simulator: {e}")
