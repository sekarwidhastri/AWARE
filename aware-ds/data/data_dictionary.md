# Kamus Data (Data Dictionary) - Proyek AWARE

Dokumen ini menjelaskan struktur data, tipe variabel, dan deskripsi untuk setiap berkas dataset yang digunakan dalam modul Data Science dan Dashboard AWARE.

---

## 1. Dataset Historis Karyawan (`employee_historical_logs.csv`)

Berkas ini menyimpan log data screening kesiapan kerja harian karyawan, menggabungkan profil kerja harian, variabel kesehatan minor, dan hasil ekstraksi landmark wajah.

| Nama Kolom | Tipe Data | Deskripsi | Rentang Nilai / Kategori |
| :--- | :--- | :--- | :--- |
| `employee_id` | String | ID Unik Karyawan. | `EMP-[1000-9999]` |
| `department` | Kategori | Departemen tempat karyawan bekerja. | `Produksi (Manufaktur)`, `Logistik & Transportasi`, `Pertambangan & Lapangan`, `Administrasi & IT` |
| `shift` | Kategori | Shift kerja karyawan pada hari screening. | `Pagi (06:00 - 14:00)`, `Siang (14:00 - 22:00)`, `Malam (22:00 - 06:00)` |
| `sleep_duration` | Float | Durasi tidur mandiri karyawan pada malam sebelum shift (dalam satuan jam). | `3.0` s.d `10.0` jam |
| `overtime_hours` | Integer | Jumlah jam kerja lembur pada hari/shift sebelumnya. | `0` s.d `3` jam |
| `heart_rate` | Integer | Denyut jantung rata-rata karyawan saat screening (bpm). | `50` s.d `100` bpm |
| `ear_score` | Float | *Eye Aspect Ratio* rata-rata yang dideteksi oleh Computer Vision dalam 30 detik pertama. | `0.15` s.d `0.35` |
| `yawn_count` | Integer | Jumlah frekuensi menguap karyawan yang terdeteksi selama 30 detik screening. | `0` s.d `4` kali |

---

## 2. Dataset Hasil Eksperimen A/B Testing (`ab_testing_results.csv`)

Berkas ini digunakan untuk membandingkan performa keselamatan kerja sebelum dan sesudah penerapan sistem digital AWARE.

| Nama Kolom | Tipe Data | Deskripsi | Rentang Nilai / Kategori |
| :--- | :--- | :--- | :--- |
| `day` | Integer | Hari pengamatan uji coba A/B testing. | `1` s.d `30` |
| `group` | Kategori | Kelompok pengamatan. | `A (Manual Control)`: screening konvensional<br>`B (AWARE Treatment)`: screening digital AWARE |
| `near_misses` | Integer | Jumlah insiden keselamatan kerja minor atau hampir celaka (*near-miss*) yang dilaporkan pada divisi terkait dalam 1 hari. | `0` s.d `5` insiden |
| `avg_screening_time_sec` | Float | Waktu rata-rata yang dibutuhkan untuk menyelesaikan screening per karyawan (dalam satuan detik). | `15.0` s.d `150.0` detik |
