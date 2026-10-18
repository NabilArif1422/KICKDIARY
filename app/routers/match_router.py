from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, CustomMetric, Match, MatchMetricValue, ActivityLog
from app.schemas import (
    CustomMetricCreate, CustomMetricResponse,
    MatchCreate, MatchResponse, MetricValueResponse
)
from app.security import get_current_user

router = APIRouter(prefix="/api", tags=["Mode 2 Custom Player (UC-014, UC-015, UC-018, UC-019)"])

# ============================================================================
# METRIK KUSTOM (UC-018, UC-019)
# ============================================================================

@router.get("/metrics", response_model=List[CustomMetricResponse])
def get_user_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan seluruh daftar metrik kustom milik pengguna aktif."""
    return db.query(CustomMetric).filter(CustomMetric.user_id == current_user.id).all()


@router.post("/metrics", response_model=CustomMetricResponse, status_code=status.HTTP_201_CREATED)
def add_custom_metric(
    metric_in: CustomMetricCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-018 Menambahkan Metrik Kustom.
    Memeriksa duplikasi nama metrik dan menyimpan ke database (NFR-005).
    """
    existing = db.query(CustomMetric).filter(
        CustomMetric.user_id == current_user.id,
        CustomMetric.name.ilike(metric_in.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama metrik sudah digunakan."
        )

    new_metric = CustomMetric(
        user_id=current_user.id,
        name=metric_in.name.strip(),
        unit=metric_in.unit.strip() or "kali"
    )
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric


@router.delete("/metrics/{metric_id}")
def delete_custom_metric(
    metric_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-019 Menghapus Metrik Kustom.
    Menghapus definisi metrik tanpa merusak histori data pertandingan lama (FR-021).
    """
    metric = db.query(CustomMetric).filter(
        CustomMetric.id == metric_id,
        CustomMetric.user_id == current_user.id
    ).first()
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metrik kustom tidak ditemukan."
        )

    db.delete(metric)
    db.commit()
    return {"message": "Metrik kustom berhasil dihapus."}


# ============================================================================
# DATA PERTANDINGAN (UC-014, UC-015)
# ============================================================================

@router.post("/matches", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def add_match(
    match_in: MatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-014 Menambahkan Data Pertandingan.
    Menyimpan field default pertandingan beserta nilai metrik kustom dinamis (FR-013, FR-014).
    """
    new_match = Match(
        user_id=current_user.id,
        match_date=match_in.match_date,
        team_name=match_in.team_name or "Tim Anda",
        opponent=match_in.opponent,
        score_home=match_in.score_home,
        score_away=match_in.score_away,

        position=match_in.position,
        minutes_played=match_in.minutes_played,
        goals=match_in.goals,
        assists=match_in.assists,
        yellow_cards=match_in.yellow_cards,
        red_cards=match_in.red_cards,
        memorable_moment=match_in.memorable_moment
    )
    db.add(new_match)
    db.flush()  # Dapatkan new_match.id

    # Simpan nilai metrik kustom jika ada
    custom_metrics_res = []
    if match_in.custom_metrics:
        for mv in match_in.custom_metrics:
            metric_def = db.query(CustomMetric).filter(
                CustomMetric.id == mv.metric_id,
                CustomMetric.user_id == current_user.id
            ).first()
            if metric_def:
                val_record = MatchMetricValue(
                    match_id=new_match.id,
                    metric_id=mv.metric_id,
                    value=mv.value
                )
                db.add(val_record)
                custom_metrics_res.append(
                    MetricValueResponse(
                        metric_id=metric_def.id,
                        metric_name=metric_def.name,
                        unit=metric_def.unit,
                        value=mv.value
                    )
                )

    db.commit()
    db.refresh(new_match)

    res = MatchResponse.model_validate(new_match)
    res.custom_metrics = custom_metrics_res
    return res


@router.get("/matches", response_model=List[MatchResponse])
def get_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-015 Melihat Daftar Data Pertandingan.
    Mengambil seluruh pertandingan milik pengguna secara kronologis terbaru (FR-013).
    """
    matches = db.query(Match).filter(
        Match.user_id == current_user.id
    ).order_by(Match.created_at.desc()).all()

    result = []
    for m in matches:
        metrics_list = []
        for mv in m.metric_values:
            if mv.metric:
                metrics_list.append(
                    MetricValueResponse(
                        metric_id=mv.metric.id,
                        metric_name=mv.metric.name,
                        unit=mv.metric.unit,
                        value=mv.value
                    )
                )
        res = MatchResponse.model_validate(m)
        res.custom_metrics = metrics_list
        result.append(res)

    return result
