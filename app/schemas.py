from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ============================================================================
# SKEMA PENGGUNA & AUTENTIKASI (UC-001, UC-002, UC-005, UC-006)
# ============================================================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password minimal 8 karakter (sesuai UC-004/NFR-005)")
    full_name: str = Field(..., min_length=2, max_length=100)
    position: Optional[str] = "Striker"
    country: Optional[str] = "Indonesia"
    bio: Optional[str] = "Pemain sepakbola amatir bersemangat tinggi."

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str
    role: str
    tier: str

class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str
    profile_picture: Optional[str]
    position: Optional[str]
    country: Optional[str]
    bio: Optional[str]
    tier: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

# ============================================================================
# SKEMA METRIK KUSTOM (UC-018, UC-019)
# ============================================================================

class CustomMetricCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nama metrik, misal: Sprint Cepat")
    unit: str = Field(default="kali", max_length=30, description="Satuan metrik, misal: kali, %, meter")

class CustomMetricResponse(BaseModel):
    id: int
    name: str
    unit: str
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# SKEMA DATA PERTANDINGAN (UC-014, UC-015, UC-016, UC-017)
# ============================================================================

class MetricValueInput(BaseModel):
    metric_id: int
    value: float

class MetricValueResponse(BaseModel):
    metric_id: int
    metric_name: str
    unit: str
    value: float

class MatchCreate(BaseModel):
    match_date: str = Field(..., description="Format YYYY-MM-DD")
    team_name: Optional[str] = Field(default="Tim Anda", description="Nama tim/klub Anda")
    opponent: str = Field(..., min_length=2, max_length=100)
    score_home: int = Field(default=0, ge=0)
    score_away: int = Field(default=0, ge=0)
    position: str = Field(..., min_length=2, max_length=50)
    minutes_played: int = Field(default=90, ge=1, le=120)
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    yellow_cards: int = Field(default=0, ge=0, le=2)
    red_cards: int = Field(default=0, ge=0, le=1)
    memorable_moment: Optional[str] = ""
    custom_metrics: Optional[List[MetricValueInput]] = []

class MatchResponse(BaseModel):
    id: int
    match_date: str
    team_name: Optional[str]
    opponent: str
    score_home: int
    score_away: int

    position: str
    minutes_played: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    memorable_moment: Optional[str]
    created_at: datetime
    custom_metrics: List[MetricValueResponse] = []

    class Config:
        from_attributes = True

# ============================================================================
# SKEMA STORY GENERATION & HISTORI (UC-020, UC-022)
# ============================================================================

class StoryGenerateRequest(BaseModel):
    match_id: int
    narrative_style: str = Field(default="Dramatis", description="Dramatis / Formal / Santai")
    language: str = Field(default="Indonesia", description="Indonesia / English")

class StoryResponse(BaseModel):
    id: int
    story_type: str
    title: str
    content: str
    narrative_style: str
    language: str
    match_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
