# ⚽ KICKDIARY 26 - Athletic Career OS
> **Platform Web Berbasis Kecerdasan Buatan (AI) untuk Mengubah Rekam Jejak Sepakbola Menjadi Narasi Perjalanan Karir**

Proyek Tugas Besar Mata Kuliah **Implementasi dan Pengujian Perangkat Lunak (IPPL B)**  
Disusun oleh: **Nabil Arif Ikhwanul Hakim** (NIM: **11241066**)  
Program Studi: **Informatika**

---

## 📌 1. Ringkasan Eksekutif & Milestone Capaian UTS

Berdasarkan ketentuan Ujian Tengah Semester (UTS), prototype dituntut untuk menyelesaikan **minimal 30% dari total fitur esensial**. 

Dokumen *Software Requirements Specification* (SRS) mendefinisikan total **27 Use Case (UC-001 s.d. UC-027)**. Pada milestone ini, KICKDIARY telah menyelesaikan **12 Use Case Inti (44,4% Capaian Progres)** yang menghubungkan seluruh siklus fungsional dari hulu ke hilir (*End-to-End Vertical Slice*):

| Modul Sistem | ID Use Case | Nama Fitur Fungsional | Status Implementasi | Status Uji (Pytest) |
| :--- | :--- | :--- | :---: | :---: |
| **Modul 1.0: Autentikasi & Akun** | `UC-001` | Mendaftarkan Akun Baru | ✅ Selesai | `TC 001`, `TC 002` (PASSED) |
| | `UC-002` | Login & Sesi Token JWT | ✅ Selesai | `TC 003`, `TC 004` (PASSED) |
| | `UC-003` | Logout Pengguna | ✅ Selesai | `TC 005` (PASSED) |
| | `UC-005` | Melihat Data Profil | ✅ Selesai | `TC 007` (PASSED) |
| | `UC-006` | Mengubah Data Profil | ✅ Selesai | `TC 008` (PASSED) |
| **Modul 4.0: Mode 2 Custom Player** | `UC-014` | Menambahkan Data Pertandingan | ✅ Selesai | `TC 017` (PASSED) |
| | `UC-015` | Melihat Daftar Pertandingan | ✅ Selesai | `TC 018` (PASSED) |
| | `UC-018` | Menambahkan Metrik Kustom | ✅ Selesai | `TC 021` (PASSED) |
| | `UC-019` | Menghapus Metrik Kustom | ✅ Selesai | `TC 022` (PASSED) |
| **Modul 5.0: Story Vault & AI Engine** | `UC-020` | Generate Match Story (AI Engine) | ✅ Selesai | `TC 023` (PASSED) |
| | `UC-022` | Melihat Histori Story (Story Vault) | ✅ Selesai | `TC 025` (PASSED) |
| | `UC-023` | Menghapus Story dari Histori | ✅ Selesai | `TC 026` (PASSED) |

---

## 🏗️ 2. Arsitektur & Teknologi (Tech Stack)

Sistem dirancang mengacu pada spesifikasi **Software Design Document (SDD) Bab III & IV**:

* **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) — Arsitektur RESTful API asinkron berperforma tinggi.
* **Database & ORM**: PostgreSQL-Ready via [SQLAlchemy 2.0 ORM](https://www.sqlalchemy.org/) (memisahkan logika SQL mentah dan mencegah SQL Injection).
* **Keamanan & Kriptografi**:
  * Enkripsi password menggunakan **Bcrypt minimal 12 rounds** (mematuhi **NFR-003**).
  * Manajemen sesi berbasis **JSON Web Token (JWT)** dengan kedaluwarsa otomatis 60 menit (mematuhi **NFR-003**).
  * Validasi input ketat di seluruh pintu masuk API menggunakan **Pydantic Schemas** (mematuhi **NFR-005**).
* **AI Storytelling Engine**:
  * Integrasi resmi [Google Gemini API](https://ai.google.dev/) (`gemini-1.5-flash`).
  * Dilengkapi **Smart Narrative Synthesis Engine (Fallback)** sehingga sistem tetap 100% menghasilkan narasi sepakbola berkualitas jika API Key offline (mematuhi **NFR-006 & NFR-014**).
* **Frontend Web**:
  * Single Page Application (SPA) responsif yang dilayani langsung oleh FastAPI.
  * Desain terinspirasi dari estetika **FIFA 17 Frostbite UI**: Bento Grid modular, tipografi atletik *Bebas Neue*, kartu FUT emas, dan kaca transparan (*Frosted Glassmorphism*) dengan latar belakang stadion malam megah.
* **DevOps & Kontainer**:
  * Dilengkapi **`Dockerfile`** dan **`docker-compose.yml`** (Docker-Ready).

---

## 📂 3. Struktur Direktori Proyek

```text
KICKDIARY IPPL/
├── app/
│   ├── routers/
│   │   ├── auth_router.py       # Endpoint Registrasi, Login, Profil (UC-001 s.d. UC-006)
│   │   ├── match_router.py      # Endpoint Pertandingan & Metrik Kustom (UC-014, UC-015, UC-018)
│   │   └── story_router.py      # Endpoint AI Match Story & Vault (UC-020, UC-022, UC-023)
│   ├── services/
│   │   └── ai_story_service.py  # Engine AI Gemini & Smart Narrative Fallback
│   ├── static/
│   │   └── index.html           # Frontend Antarmuka FIFA 17 UI Theme
│   ├── config.py                # Konfigurasi terpusat (Pydantic Settings)
│   ├── database.py              # Engine koneksi database & session generator
│   ├── init_db.py               # Skrip inisialisasi tabel otomatis
│   ├── models.py                # Definisi Model ORM (User, Match, Story, Metric, Log)
│   ├── schemas.py               # Skema Validasi Input/Output Pydantic
│   └── security.py              # Enkripsi Bcrypt 12 rounds & JWT token handler
├── tests/
│   ├── conftest.py              # In-memory test database fixture (SQLite :memory:)
│   ├── test_auth.py             # Unit & Integration test modul autentikasi
│   └── test_matches_story.py    # Unit & Integration test modul pertandingan & AI story
├── .env                         # Konfigurasi environment variables
├── .gitignore                   # Menyaring cache, database, dan credential
├── Dockerfile                   # Cetak biru kontainer backend
├── docker-compose.yml           # Orkestrasi multi-kontainer (FastAPI + PostgreSQL 15)
├── pytest.ini                   # Konfigurasi eksekusi pengujian otomatis
├── requirements.txt             # Daftar dependensi pustaka Python
└── README.md                    # Dokumentasi resmi proyek
```

---

## 🚀 4. Panduan Menjalankan Aplikasi

### Opsi A: Menjalankan Secara Lokal (Python)

1. **Buka terminal dan aktifkan virtual environment**:
   ```powershell
   # Jika belum ada virtual environment:
   python -m venv .venv

   # Aktifkan virtual environment di Windows:
   .\.venv\Scripts\activate
   ```

2. **Pasang seluruh dependensi**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Inisialisasi database**:
   ```powershell
   python -m app.init_db
   ```

4. **Jalankan server aplikasi**:
   ```powershell
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

5. Buka browser dan akses antarmuka web di:  
   👉 **`http://localhost:8000`**  
   *(Dokumentasi interaktif Swagger API dapat diakses di: `http://localhost:8000/docs`)*

---

### Opsi B: Menjalankan Menggunakan Docker (Docker-Ready)

Bagi penguji yang memiliki Docker di sistem operasi mereka:
```bash
docker compose up --build
```
Aplikasi backend FastAPI dan basis data PostgreSQL 15 akan terorkestrasi secara otomatis pada port `8000`.

---

## 🧪 5. Laporan Pengujian Otomatis (IPPL Automated Testing)

Pengujian perangkat lunak dilakukan secara bertahap (*Unit & Integration Testing*) menggunakan **`pytest`** dengan basis data memori mandiri (*in-memory*) agar tidak merusak data operasional.

### Perintah Eksekusi Pengujian:
```powershell
pytest -v
```

### Hasil Eksekusi Uji (17/17 PASSED - 100% Kelulusan):
```text
============================= test session starts =============================
platform win32 -- Python 3.14.8, pytest-9.1.1
rootdir: D:\KICKDIARY IPPL
configfile: pytest.ini
testpaths: tests
collected 17 items

tests/test_auth.py::test_tc_001_register_happy_path PASSED               [  5%]
tests/test_auth.py::test_tc_002_register_duplicate_email PASSED          [ 11%]
tests/test_auth.py::test_tc_003_login_happy_path PASSED                  [ 17%]
tests/test_auth.py::test_tc_004_login_wrong_password PASSED              [ 23%]
tests/test_auth.py::test_tc_005_logout PASSED                            [ 29%]
tests/test_auth.py::test_tc_007_view_profile PASSED                      [ 35%]
tests/test_auth.py::test_tc_008_update_profile PASSED                    [ 41%]
tests/test_auth.py::test_tc_nfr_003_bcrypt_encryption PASSED             [ 47%]
tests/test_auth.py::test_tc_nfr_005_input_validation PASSED              [ 52%]
tests/test_matches_story.py::test_tc_021_add_custom_metric PASSED        [ 58%]
tests/test_matches_story.py::test_tc_022_delete_custom_metric PASSED     [ 64%]
tests/test_matches_story.py::test_tc_017_add_match PASSED                [ 70%]
tests/test_matches_story.py::test_tc_018_get_matches PASSED              [ 76%]
tests/test_matches_story.py::test_tc_023_generate_match_story PASSED     [ 82%]
tests/test_matches_story.py::test_tc_025_view_story_vault PASSED         [ 88%]
tests/test_matches_story.py::test_tc_026_delete_story PASSED             [ 94%]
tests/test_matches_story.py::test_tc_nfr_007_story_persisted_before_display PASSED [100%]

============================= 17 passed in 9.07s ==============================
```

---

## 🗺️ 6. Rencana Pengembangan Pasca-UTS (Roadmap Sprint 5–7)

Sisa Use Case (~55%) dijadwalkan pada siklus sprint berikutnya sesuai dokumen perencanaan Agile Scrum:
* **Sprint 5**: Integrasi Webhook Payment Gateway Midtrans (`UC-007`, `UC-008`), Ekspor Narasi ke PDF (`UC-024`), dan Salin Link Publik (`UC-025`).
* **Sprint 6**: Integrasi Scraping Data Pemain Profesional FBRef & Transfermarkt untuk Mode 1 Real Player (`UC-009` s.d. `UC-013`).
* **Sprint 7**: Dashboard Monitoring Admin & Audit Log Aktivitas (`UC-026`, `UC-027`).
