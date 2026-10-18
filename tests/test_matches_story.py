import pytest
from app.models import Story

@pytest.fixture
def auth_header(client):
    """Helper fixture untuk mendaftarkan akun dan mendapatkan token otentikasi."""
    client.post("/api/auth/register", json={
        "full_name": "Dimas Raharjo",
        "email": "dimas@test.com",
        "password": "password123",
        "position": "Striker"
    })
    login_res = client.post("/api/auth/login", json={
        "email": "dimas@test.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_tc_021_add_custom_metric(client, auth_header):
    """TC 021: Tambah Metrik Kustom (UC 018) - Menambahkan Metrik Statistik Baru."""
    payload = {
        "name": "Duel Udara Menang",
        "unit": "kali"
    }
    response = client.post("/api/metrics", json=payload, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Duel Udara Menang"
    assert data["unit"] == "kali"

def test_tc_022_delete_custom_metric(client, auth_header):
    """TC 022: Hapus Metrik Kustom (UC 019) - Menghapus Definisi Metrik."""
    # Buat metrik dulu
    create_res = client.post("/api/metrics", json={"name": "Sprint", "unit": "km/h"}, headers=auth_header)
    metric_id = create_res.json()["id"]

    # Hapus metrik
    del_res = client.delete(f"/api/metrics/{metric_id}", headers=auth_header)
    assert del_res.status_code == 200
    assert "berhasil dihapus" in del_res.json()["message"]

def test_tc_017_add_match(client, auth_header):
    """TC 017: Tambah Data Pertandingan (UC 014) - Pencatatan Pertandingan Lengkap."""
    # Buat metrik kustom dulu
    metric_res = client.post("/api/metrics", json={"name": "Akurasi Passing", "unit": "%"}, headers=auth_header)
    metric_id = metric_res.json()["id"]

    match_payload = {
        "match_date": "2026-10-20",
        "team_name": "Garuda FC",
        "opponent": "Tim Karet FC",
        "score_home": 3,
        "score_away": 2,
        "position": "Gelandang",
        "minutes_played": 90,
        "goals": 1,
        "assists": 2,
        "yellow_cards": 1,
        "red_cards": 0,
        "memorable_moment": "Gol salto menit ke-88 membalikkan kedudukan.",
        "custom_metrics": [
            {"metric_id": metric_id, "value": 87.5}
        ]
    }
    response = client.post("/api/matches", json=match_payload, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    assert data["opponent"] == "Tim Karet FC"
    assert data["team_name"] == "Garuda FC"
    assert data["score_home"] == 3
    assert len(data["custom_metrics"]) == 1
    assert data["custom_metrics"][0]["value"] == 87.5

def test_tc_018_get_matches(client, auth_header):
    """TC 018: Lihat Daftar Pertandingan (UC 015) - Pengambilan Riwayat Laga."""
    # Catat 1 pertandingan
    client.post("/api/matches", json={
        "match_date": "2026-10-20",
        "opponent": "Elang FC",
        "score_home": 2,
        "score_away": 1,
        "position": "Striker"
    }, headers=auth_header)

    response = client.get("/api/matches", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["opponent"] == "Elang FC"

def test_tc_023_generate_match_story(client, auth_header):
    """TC 023: Generate Match Story (UC 020) - Menghasilkan Narasi AI."""
    # Buat data pertandingan
    match_res = client.post("/api/matches", json={
        "match_date": "2026-10-20",
        "team_name": "Garuda Muda",
        "opponent": "Singa FC",
        "score_home": 4,
        "score_away": 2,
        "position": "Striker",
        "goals": 2,
        "assists": 1,
        "memorable_moment": "Hat-trick hampir tercipta lewat tendangan bebas."
    }, headers=auth_header)
    match_id = match_res.json()["id"]

    # Generate Story
    story_payload = {
        "match_id": match_id,
        "narrative_style": "Dramatis",
        "language": "Indonesia"
    }
    response = client.post("/api/stories/generate", json=story_payload, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    assert "title" in data
    assert "content" in data
    assert data["narrative_style"] == "Dramatis"
    assert len(data["content"]) > 100

def test_tc_025_view_story_vault(client, auth_header):
    """TC 025: Lihat Histori Story (UC 022) - Mengambil Arsip Cerita."""
    # Generate story
    match_res = client.post("/api/matches", json={
        "match_date": "2026-10-20",
        "opponent": "Harimau FC",
        "position": "Striker"
    }, headers=auth_header)
    client.post("/api/stories/generate", json={
        "match_id": match_res.json()["id"],
        "narrative_style": "Santai"
    }, headers=auth_header)

    response = client.get("/api/stories", headers=auth_header)
    assert response.status_code == 200
    stories = response.json()
    assert len(stories) >= 1
    assert stories[0]["narrative_style"] == "Santai"

def test_tc_026_delete_story(client, auth_header):
    """TC 026: Hapus Story (UC 023) - Menghapus Cerita dari Histori."""
    match_res = client.post("/api/matches", json={
        "match_date": "2026-10-20",
        "opponent": "Banteng FC",
        "position": "Striker"
    }, headers=auth_header)
    story_res = client.post("/api/stories/generate", json={
        "match_id": match_res.json()["id"]
    }, headers=auth_header)
    story_id = story_res.json()["id"]

    response = client.delete(f"/api/stories/{story_id}", headers=auth_header)
    assert response.status_code == 200
    assert "berhasil dihapus" in response.json()["message"]

def test_tc_nfr_007_story_persisted_before_display(db_session, client, auth_header):
    """TC NFR 007: Story Tersimpan di Database Sebelum Ditampilkan ke Pengguna."""
    match_res = client.post("/api/matches", json={
        "match_date": "2026-10-20",
        "opponent": "Persik FC",
        "position": "Striker"
    }, headers=auth_header)
    story_res = client.post("/api/stories/generate", json={
        "match_id": match_res.json()["id"]
    }, headers=auth_header)
    story_id = story_res.json()["id"]

    # Verifikasi langsung ke database SQL bahwa data sudah permanen tersimpan
    story_in_db = db_session.query(Story).filter(Story.id == story_id).first()
    assert story_in_db is not None
    assert story_in_db.title == story_res.json()["title"]
