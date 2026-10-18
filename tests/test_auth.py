import pytest
from app.models import User
from app.security import verify_password

def test_tc_001_register_happy_path(client):
    """TC 001: Mendaftarkan Akun (UC 001) - Happy Path."""
    payload = {
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "rahasia123",
        "position": "Striker",
        "country": "Indonesia"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "raka@test.com"
    assert data["full_name"] == "Raka Pratama"
    assert data["tier"] == "Free"
    assert data["role"] == "User"

def test_tc_002_register_duplicate_email(client):
    """TC 002: Registrasi dengan Email Duplikat (UC 001) - Validasi Keunikan."""
    payload = {
        "full_name": "Raka",
        "email": "raka@test.com",
        "password": "rahasia123"
    }
    # Registrasi pertama
    client.post("/api/auth/register", json=payload)
    
    # Registrasi kedua dengan email yang sama
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "Email sudah digunakan" in response.json()["detail"]

def test_tc_003_login_happy_path(client):
    """TC 003: Login Berhasil (UC 002) - Happy Path & JWT Generation."""
    # Setup akun
    client.post("/api/auth/register", json={
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "rahasia123"
    })

    # Eksekusi login
    login_payload = {
        "email": "raka@test.com",
        "password": "rahasia123"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "User"

def test_tc_004_login_wrong_password(client):
    """TC 004: Login Password Salah (UC 002) - Penolakan Kredensial."""
    client.post("/api/auth/register", json={
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "rahasia123"
    })

    response = client.post("/api/auth/login", json={
        "email": "raka@test.com",
        "password": "wrongpassword123"
    })
    assert response.status_code == 401
    assert "Email atau password salah" in response.json()["detail"]

def test_tc_005_logout(client):
    """TC 005: Logout (UC 003) - Mengakhiri Sesi Aktif."""
    client.post("/api/auth/register", json={
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "rahasia123"
    })
    login_res = client.post("/api/auth/login", json={"email": "raka@test.com", "password": "rahasia123"})
    token = login_res.json()["access_token"]

    response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Sesi berhasil diakhiri" in response.json()["message"]

def test_tc_007_view_profile(client):
    """TC 007: Lihat Data Profil (UC 005) - Pengambilan Data Profil Aktif."""
    client.post("/api/auth/register", json={
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "rahasia123",
        "position": "Midfielder"
    })
    login_res = client.post("/api/auth/login", json={"email": "raka@test.com", "password": "rahasia123"})
    token = login_res.json()["access_token"]

    response = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Raka Pratama"
    assert data["position"] == "Midfielder"

def test_tc_008_update_profile(client):
    """TC 008: Ubah Data Profil (UC 006) - Pembaruan Profil Persisten."""
    client.post("/api/auth/register", json={
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "rahasia123"
    })
    login_res = client.post("/api/auth/login", json={"email": "raka@test.com", "password": "rahasia123"})
    token = login_res.json()["access_token"]

    update_payload = {
        "full_name": "Raka Pratama Jaya",
        "position": "Winger",
        "bio": "Menyerang dari sisi sayap cepat."
    }
    response = client.put("/api/auth/profile", json=update_payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Raka Pratama Jaya"
    assert data["position"] == "Winger"

def test_tc_nfr_003_bcrypt_encryption(db_session, client):
    """TC NFR 003: Security Enkripsi Bcrypt 12 Rounds & Keamanan Password."""
    client.post("/api/auth/register", json={
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "rahasia123"
    })
    user = db_session.query(User).filter(User.email == "raka@test.com").first()
    assert user is not None
    # Password di database tidak boleh plaintext
    assert user.password_hash != "rahasia123"
    # Harus diawali header bcrypt standard ($2b$)
    assert user.password_hash.startswith("$2b$")
    # Verifikasi bcrypt berhasil mencocokkan password
    assert verify_password("rahasia123", user.password_hash) is True

def test_tc_nfr_005_input_validation(client):
    """TC NFR 005: Security Validasi Input - Penolakan Password Pendek."""
    # Password kurang dari 8 karakter harus ditolak
    payload = {
        "full_name": "Raka Pratama",
        "email": "raka@test.com",
        "password": "short"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422  # Pydantic validation error
