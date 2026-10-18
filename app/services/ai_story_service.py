import os
from typing import Dict, Any, List
from app.config import settings

def _generate_fallback_narrative(
    player_name: str,
    match_data: Dict[str, Any],
    custom_metrics_data: List[Dict[str, Any]],
    style: str,
    language: str
) -> Dict[str, str]:
    """
    Mesin Narasi Sintesis Cerdas (Fallback Engine)
    Menghasilkan cerita sepakbola berstandar jurnalisme olahraga jika Gemini API
    sedang offline atau belum memiliki API Key. Menjamin demo presentasi 100% mulus.
    """
    team_name = match_data.get("team_name", "Tim Anda")
    opponent = match_data.get("opponent", "Lawan")
    score_home = match_data.get("score_home", 0)
    score_away = match_data.get("score_away", 0)

    position = match_data.get("position", "Pemain")
    goals = match_data.get("goals", 0)
    assists = match_data.get("assists", 0)
    yellow_cards = match_data.get("yellow_cards", 0)
    red_cards = match_data.get("red_cards", 0)
    minutes = match_data.get("minutes_played", 90)
    moment = match_data.get("memorable_moment") or "Pertandingan yang memeras seluruh keringat dan determinasi di lapangan hijau."
    
    # Menentukan hasil pertandingan
    if score_home > score_away:
        result_id = f"Kemenangan gemilang {score_home}-{score_away}"
        result_en = f"A glorious {score_home}-{score_away} victory"
    elif score_home < score_away:
        result_id = f"Pertarungan sengit yang berakhir {score_home}-{score_away}"
        result_en = f"A hard-fought {score_home}-{score_away} clash"
    else:
        result_id = f"Hasil imbang penuh tensi {score_home}-{score_away}"
        result_en = f"A tense {score_home}-{score_away} deadlock"

    # Format metrik kustom
    metrics_str_id = ""
    metrics_str_en = ""
    if custom_metrics_data:
        items_id = [f"{m['name']}: {m['value']} {m.get('unit', '')}" for m in custom_metrics_data]
        items_en = [f"{m['name']}: {m['value']} {m.get('unit', '')}" for m in custom_metrics_data]
        metrics_str_id = f" Dalam catatan statistik khusus, sang pemain mencatatkan " + ", ".join(items_id) + "."
        metrics_str_en = f" In the specialized tracking metrics, the player registered " + ", ".join(items_en) + "."

    if language.lower() == "english":
        if style.lower() == "dramatis":
            title = f"The Battle of Will: {player_name} vs {opponent}"
            content = (
                f"Under the blinding stadium lights, {player_name} stepped onto the pitch as a {position}, "
                f"carrying the entire team's dreams. The showdown against {opponent} was not just another match; "
                f"it was a war of endurance and character. {result_en}.\n\n"
                f"Across {minutes} grueling minutes, {player_name} fought for every loose ball, recording {goals} goal(s) "
                f"and {assists} decisive assist(s). Disciplinary records logged {yellow_cards} yellow and {red_cards} red card(s).{metrics_str_en}\n\n"
                f"The climax came during that unforgettable instant: \"{moment}\". When the final whistle blew, "
                f"it wasn't just numbers on a scoreboard—it was a chronicle of grit etched into football folklore."
            )
        elif style.lower() == "santai":
            title = f"Matchday Diary: Taking On {opponent}"
            content = (
                f"What a game day! {player_name} lined up as {position} against {opponent}, and right from the kickoff, "
                f"the banter and energy were unreal. The scoreboard sealed {result_en}.\n\n"
                f"Cruising through {minutes} minutes on the turf, {player_name} put on a show with {goals} goal(s) "
                f"and {assists} assist(s). Aside from {yellow_cards} yellow card(s), the highlight of the day was definitely: "
                f"\"{moment}\".{metrics_str_en}\n\n"
                f"Days like this remind us why we love weekend football. On to the next match!"
            )
        else: # Formal
            title = f"Post-Match Tactical Report: {player_name} vs {opponent}"
            content = (
                f"This report outlines the competitive fixture featuring {player_name} deployed as {position} "
                f"against {opponent}. The official match outcome concluded with {result_en}.\n\n"
                f"During the {minutes}-minute appearance, tactical metrics indicate significant involvement with {goals} goal(s) "
                f"and {assists} assist(s) contributed to the squad's offensive output. Disciplinary review indicates {yellow_cards} yellow and {red_cards} red card(s).{metrics_str_en}\n\n"
                f"Critical event documentation highlights: \"{moment}\". The aggregate performance demonstrates consistent strategic adherence."
            )
    else: # Bahasa Indonesia (Default)
        if style.lower() == "santai":
            title = f"Catatan Lapangan: Seru-seruan Lawan {opponent}"
            content = (
                f"Pertandingan kali ini beneran seru dan penuh tensi! Turun sebagai {position}, {player_name} langsung tancap gas "
                f"menghadapi {opponent}. Pertandingan akhirnya ditutup dengan {result_id}.\n\n"
                f"Main penuh determinasi selama {minutes} menit, {player_name} berhasil ngasih kontribusi nyata lewat {goals} gol "
                f"dan {assists} assist ciamik. Walaupun sempat kena {yellow_cards} kartu kuning, momen paling pecah di lapangan tetap saat: "
                f"\"{moment}\".{metrics_str_id}\n\n"
                f"Sepakbola emang soal keringat bareng kawan dan cerita yang nggak bakal lupa. Sampai jumpa di laga berikutnya!"
            )
        elif style.lower() == "formal":
            title = f"Laporan Taktikal Pertandingan: {player_name} Menghadapi {opponent}"
            content = (
                f"Dokumentasi resmi laga antara tim yang diperkuat oleh {player_name} (posisi: {position}) "
                f"menghadapi {opponent}. Pertandingan berakhir dengan {result_id}.\n\n"
                f"Berdasarkan analisis statistik performa selama {minutes} menit pertandingan, pemain mencatatkan kontribusi {goals} gol "
                f"dan {assists} assist. Aspek kedisiplinan mencatat {yellow_cards} kartu kuning dan {red_cards} kartu merah.{metrics_str_id}\n\n"
                f"Peristiwa penting yang terekam dalam pertandingan ini meliputi: \"{moment}\". Data ini tersimpan resmi dalam histori evaluasi berkala."
            )
        else: # Dramatis (Default UC-020)
            title = f"Gema Lapangan Hijau: Perjuangan {player_name} Bersama {team_name} Melawan {opponent}"
            content = (
                f"Di bawah gemuruh atmosfer lapangan dan sorotan lampu stadion, {player_name} melangkah tegap mengemban peran sebagai {position} "
                f"bersama skuad {team_name}. Pertarungan menghadapi {opponent} bukan sekadar laga 90 menit biasa, melainkan panggung pembuktian harga diri. "
                f"{result_id}.\n\n"
                f"Sepanjang {minutes} menit berpeluh keringat dan beradu fisik di setiap jengkal rumput, {player_name} mengukir sumbangsih {goals} gol "
                f"serta {assists} umpan matang penentu. Catatan tensi laga menorehkan {yellow_cards} kartu kuning.{metrics_str_id}\n\n"
                f"Detik paling menggetarkan jiwa meledak pada momen krusial: \"{moment}\". Peluit panjang wasit boleh saja menyudahi pertandingan, "
                f"namun semangat juang membela {team_name} ini akan abadi dalam catatan sejarah KickDiary."
            )


    return {"title": title, "content": content}


def generate_match_story_narrative(
    player_name: str,
    match_data: Dict[str, Any],
    custom_metrics_data: List[Dict[str, Any]],
    narrative_style: str = "Dramatis",
    language: str = "Indonesia"
) -> Dict[str, str]:
    """
    Eksekutor AI Narasi (Gemini API dengan fallback cerdas).
    Sesuai FR-015, UC-020, NFR-002 (waktu < 60 detik), NFR-014 (akurasi gaya narasi & bahasa).
    """
    # Coba hubungkan ke Gemini API jika GEMINI_API_KEY tersedia
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            Anda adalah penulis kisah sepakbola profesional untuk aplikasi KICKDIARY.
            Buatlah cerita narasi yang mendalam dan memukau tentang pertandingan berikut:
            
            Nama Pemain: {player_name}
            Posisi Bermain: {match_data.get('position')}
            Lawan: {match_data.get('opponent')}
            Skor Akhir: {match_data.get('score_home')} - {match_data.get('score_away')}
            Menit Bermain: {match_data.get('minutes_played')}
            Gol: {match_data.get('goals')}, Assist: {match_data.get('assists')}
            Kartu Kuning: {match_data.get('yellow_cards')}, Kartu Merah: {match_data.get('red_cards')}
            Momen Berkesan: {match_data.get('memorable_moment')}
            Metrik Kustom: {custom_metrics_data}
            
            ATURAN:
            1. Gaya Narasi: {narrative_style} (Dramatis/Formal/Santai)
            2. Bahasa: {language} (Indonesia/English)
            3. Berikan judul yang menarik di baris pertama diawali kata "JUDUL: " lalu narasinya.
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            lines = text.split("\n", 1)
            title = lines[0].replace("JUDUL:", "").replace("**", "").strip() if len(lines) > 0 else f"Match Story: vs {match_data.get('opponent')}"
            content = lines[1].strip() if len(lines) > 1 else text
            
            return {"title": title, "content": content}
        except Exception as e:
            # Jika Gemini API error/rate limit (NFR-006 fallback), gunakan fallback synthesis engine
            print(f"[AI Fallback Triggered] Gemini API error: {e}")
            return _generate_fallback_narrative(player_name, match_data, custom_metrics_data, narrative_style, language)

    # Jika belum ada API key, gunakan langsung narrative fallback engine
    return _generate_fallback_narrative(player_name, match_data, custom_metrics_data, narrative_style, language)
