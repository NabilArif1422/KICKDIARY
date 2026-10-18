from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    """
    Data Pengguna (D1) - Sesuai SDD Bab III Poin 3.3 & SRS FR-001 s.d. FR-005.
    Menyimpan profil pengguna, kredensial terenkripsi bcrypt, tier langganan, dan RBAC role.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    profile_picture = Column(String(500), nullable=True)
    position = Column(String(50), nullable=True, default="Striker")
    country = Column(String(50), nullable=True, default="Indonesia")
    bio = Column(Text, nullable=True, default="Pemain sepakbola amatir bersemangat tinggi.")
    tier = Column(String(20), default="Free", nullable=False)  # Free, Premium, Tim
    role = Column(String(20), default="User", nullable=False)  # User, Admin (NFR-004 RBAC)
    status = Column(String(20), default="Active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    matches = relationship("Match", back_populates="user", cascade="all, delete-orphan")
    custom_metrics = relationship("CustomMetric", back_populates="user", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user")


class CustomMetric(Base):
    """
    Data Metrik Kustom (D4) - Sesuai SDD Bab III & SRS FR-014, FR-021.
    Menyimpan metrik buatan user (misal: Pelanggaran, Sprint, Akurasi Umpan).
    """
    __tablename__ = "custom_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    unit = Column(String(30), nullable=True, default="kali")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="custom_metrics")
    metric_values = relationship("MatchMetricValue", back_populates="metric", cascade="all, delete-orphan")


class Match(Base):
    """
    Data Pertandingan (D3) - Sesuai SDD Bab III & SRS FR-013, FR-014.
    Menyimpan data pertandingan Mode 2 Custom Player.
    """
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_date = Column(String(20), nullable=False)  # format: YYYY-MM-DD
    team_name = Column(String(100), default="Tim Anda", nullable=True)
    opponent = Column(String(100), nullable=False)
    score_home = Column(Integer, default=0, nullable=False)

    score_away = Column(Integer, default=0, nullable=False)
    position = Column(String(50), nullable=False)
    minutes_played = Column(Integer, default=90, nullable=False)
    goals = Column(Integer, default=0, nullable=False)
    assists = Column(Integer, default=0, nullable=False)
    yellow_cards = Column(Integer, default=0, nullable=False)
    red_cards = Column(Integer, default=0, nullable=False)
    memorable_moment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="matches")
    metric_values = relationship("MatchMetricValue", back_populates="match", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="match")


class MatchMetricValue(Base):
    """
    Data Nilai Metrik Pertandingan (D5) - Sesuai SDD Bab III Poin 3.3.
    Relasi many-to-many nilai metrik kustom per pertandingan.
    """
    __tablename__ = "match_metric_values"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    metric_id = Column(Integer, ForeignKey("custom_metrics.id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False, default=0.0)

    # Relationships
    match = relationship("Match", back_populates="metric_values")
    metric = relationship("CustomMetric", back_populates="metric_values")


class Story(Base):
    """
    Data Story (D2) - Sesuai SDD Bab III & SRS FR-017, FR-020, NFR-007.
    Menyimpan hasil generate AI yang bersifat final.
    """
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    story_type = Column(String(50), default="Match Story", nullable=False)  # Match Story, Football Diary, dll.
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    narrative_style = Column(String(30), default="Dramatis", nullable=False)  # Dramatis, Formal, Santai
    language = Column(String(20), default="Indonesia", nullable=False)  # Indonesia, English
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="stories")
    match = relationship("Match", back_populates="stories")


class ActivityLog(Base):
    """
    Data Log Aktivitas (D10) - Sesuai SDD Bab III Poin 3.3 & SRS FR-022, NFR-013.
    Mencatat histori aktivitas sistem untuk audit dan monitoring Admin.
    """
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    activity_type = Column(String(50), nullable=False)  # REGISTER, LOGIN, LOGOUT, GENERATE_STORY, dll.
    description = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
