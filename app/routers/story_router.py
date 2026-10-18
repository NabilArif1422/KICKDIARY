from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Match, Story, ActivityLog
from app.schemas import StoryGenerateRequest, StoryResponse
from app.security import get_current_user
from app.services.ai_story_service import generate_match_story_narrative

router = APIRouter(prefix="/api/stories", tags=["Stories"])

@router.post("/generate", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)

def generate_match_story(
    req: StoryGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-020 Generate Match Story.
    Memproses narasi personal menggunakan AI berdasarkan data pertandingan yang dipilih.
    Mematuhi NFR-007: Hasil generate HARUS disimpan ke database sebelum ditampilkan ke user.
    Mematuhi NFR-014: Pilihan gaya narasi (Dramatis/Formal/Santai) dan bahasa (Indonesia/English).
    """
    # Verifikasi data pertandingan
    match = db.query(Match).filter(
        Match.id == req.match_id,
        Match.user_id == current_user.id
    ).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data pertandingan tidak ditemukan."
        )

    # Susun payload data pertandingan
    match_data = {
        "team_name": getattr(match, "team_name", "Tim Anda") or "Tim Anda",
        "opponent": match.opponent,
        "score_home": match.score_home,
        "score_away": match.score_away,

        "position": match.position,
        "minutes_played": match.minutes_played,
        "goals": match.goals,
        "assists": match.assists,
        "yellow_cards": match.yellow_cards,
        "red_cards": match.red_cards,
        "memorable_moment": match.memorable_moment
    }

    # Susun data metrik kustom
    custom_metrics_data = []
    for mv in match.metric_values:
        if mv.metric:
            custom_metrics_data.append({
                "name": mv.metric.name,
                "value": mv.value,
                "unit": mv.metric.unit
            })

    # Panggil generator AI (Gemini / Smart Fallback Engine)
    ai_result = generate_match_story_narrative(
        player_name=current_user.full_name,
        match_data=match_data,
        custom_metrics_data=custom_metrics_data,
        narrative_style=req.narrative_style,
        language=req.language
    )

    # Simpan ke database sebelum dikembalikan ke user (NFR-007)
    story = Story(
        user_id=current_user.id,
        match_id=match.id,
        story_type="Match Story",
        title=ai_result["title"],
        content=ai_result["content"],
        narrative_style=req.narrative_style,
        language=req.language
    )
    db.add(story)

    # Catat ke log aktivitas (NFR-013)
    log = ActivityLog(
        user_id=current_user.id,
        activity_type="GENERATE_STORY",
        description=f"Generate Match Story #{match.id} (Gaya: {req.narrative_style}, Bahasa: {req.language})."
    )
    db.add(log)

    db.commit()
    db.refresh(story)

    return story


@router.get("", response_model=List[StoryResponse])
def get_user_stories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-022 Melihat Histori Story.
    Mengambil seluruh narasi cerita milik pengguna dalam urutan kronologis terbaru (FR-017).
    """
    return db.query(Story).filter(
        Story.user_id == current_user.id
    ).order_by(Story.created_at.desc()).all()


@router.get("/{story_id}", response_model=StoryResponse)
def get_single_story(
    story_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Membaca detail lengkap narasi story tertentu."""
    story = db.query(Story).filter(
        Story.id == story_id,
        Story.user_id == current_user.id
    ).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story tidak ditemukan."
        )
    return story


@router.delete("/{story_id}")
def delete_story(
    story_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-023 Menghapus Story.
    Menghapus narasi yang tidak diinginkan dari histori story (FR-018).
    """
    story = db.query(Story).filter(
        Story.id == story_id,
        Story.user_id == current_user.id
    ).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story tidak ditemukan."
        )

    db.delete(story)
    db.commit()
    return {"message": "Story berhasil dihapus dari histori."}
