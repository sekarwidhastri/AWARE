import os
import pandas as pd
import numpy as np

def generate_synthetic_data():
    """
    Menghasilkan data historis karyawan sintetis berkualitas tinggi untuk simulasi
    dan analisis EDA/Scoring pada dashboard AWARE.
    """
    np.random.seed(42)
    n_records = 500

    # Data Karyawan
    departments = ['Produksi (Manufaktur)', 'Logistik & Transportasi', 'Pertambangan & Lapangan', 'Administrasi & IT']
    shifts = ['Pagi (06:00 - 14:00)', 'Siang (14:00 - 22:00)', 'Malam (22:00 - 06:00)']
    
    # Generate list
    employee_ids = [f'EMP-{np.random.randint(1000, 9999)}' for _ in range(50)] # 50 karyawan unik
    emp_pool = []
    
    for emp_id in employee_ids:
        dept = np.random.choice(departments, p=[0.4, 0.3, 0.2, 0.1])
        emp_pool.append({
            'employee_id': emp_id,
            'department': dept
        })
        
    emp_df = pd.DataFrame(emp_pool)

    # Buat records harian selama beberapa hari
    records = []
    for _ in range(n_records):
        emp = emp_df.sample(n=1).iloc[0]
        shift = np.random.choice(shifts, p=[0.4, 0.35, 0.25])
        
        # Korelasi logis durasi tidur dengan shift
        if shift == 'Malam (22:00 - 06:00)':
            sleep_duration = np.random.normal(loc=5.5, scale=1.2) # Tidur lebih sedikit
            overtime_hours = np.random.choice([0, 1, 2, 3], p=[0.5, 0.2, 0.2, 0.1])
        else:
            sleep_duration = np.random.normal(loc=6.8, scale=1.0)
            overtime_hours = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
            
        sleep_duration = max(3.0, min(10.0, sleep_duration)) # Bounded
        
        # Denyut Nadi (bpm) - fatigue biasanya denyut nadi lebih rendah / tidak teratur
        heart_rate = np.random.normal(loc=72, scale=8)
        if sleep_duration < 5.0:
            heart_rate += np.random.uniform(-5, 5) # Fluktuasi
            
        # Skor kelelahan visual (EAR, Yawn) disimulasikan
        # EAR normal sekitar 0.3, kantuk < 0.25
        if sleep_duration < 5.0:
            ear_score = np.random.uniform(0.18, 0.26)
            yawn_count = np.random.choice([0, 1, 2, 3], p=[0.2, 0.3, 0.3, 0.2])
        else:
            ear_score = np.random.uniform(0.25, 0.32)
            yawn_count = np.random.choice([0, 1], p=[0.9, 0.1])
            
        records.append({
            'employee_id': emp['employee_id'],
            'department': emp['department'],
            'shift': shift,
            'sleep_duration': round(sleep_duration, 1),
            'overtime_hours': overtime_hours,
            'heart_rate': int(heart_rate),
            'ear_score': round(ear_score, 3),
            'yawn_count': yawn_count
        })
        
    df = pd.DataFrame(records)
    
    # Save directory
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/employee_historical_logs.csv', index=False)
    print("SUCCESS: Berhasil membuat dataset historis karyawan: data/processed/employee_historical_logs.csv")

def generate_ab_testing_data():
    """
    Menghasilkan data simulasi A/B testing selama 30 hari.
    Grup A: Metode Kontrol (Manual Screening)
    Grup B: Metode Eksperimen (AWARE Screening)
    """
    np.random.seed(101)
    
    # Uji 30 hari di 2 pabrik/divisi serupa
    days = list(range(1, 31))
    
    group_a_records = []
    group_b_records = []
    
    for day in days:
        # Grup A (Manual): Near-misses rata-rata lebih tinggi, screening lebih lambat
        near_misses_a = np.random.poisson(lam=1.8)
        screening_time_a = np.random.normal(loc=120, scale=15) # 2 menit per karyawan
        
        # Grup B (AWARE): Near-misses berkurang signifikan, screening 30 detik
        near_misses_b = np.random.poisson(lam=0.6) # Penurunan signifikan!
        screening_time_b = np.random.normal(loc=25, scale=4)  # ~25 detik!
        
        group_a_records.append({
            'day': day,
            'group': 'A (Manual Control)',
            'near_misses': near_misses_a,
            'avg_screening_time_sec': round(screening_time_a, 1)
        })
        
        group_b_records.append({
            'day': day,
            'group': 'B (AWARE Treatment)',
            'near_misses': near_misses_b,
            'avg_screening_time_sec': round(screening_time_b, 1)
        })
        
    df_ab = pd.concat([pd.DataFrame(group_a_records), pd.DataFrame(group_b_records)])
    df_ab.to_csv('data/processed/ab_testing_results.csv', index=False)
    print("SUCCESS: Berhasil membuat dataset A/B Testing: data/processed/ab_testing_results.csv")

if __name__ == '__main__':
    generate_synthetic_data()
    generate_ab_testing_data()
