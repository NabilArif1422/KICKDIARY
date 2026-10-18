from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import User, ActivityLog
from app.schemas import UserRegister, UserLogin, Token, UserProfileResponse, UserProfileUpdate
from app.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth & Profile"])

@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)

def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """
    UC-001 Mendaftarkan Akun.
    Validasi format data, keunikan email, dan enkripsi bcrypt minimal 12 rounds (NFR-003, NFR-005).
    """
    # Cek keunikan email
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah digunakan, silakan login."
        )

    # Enkripsi password dengan bcrypt (12 rounds)
    hashed_pwd = hash_password(user_in.password)

    new_user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        full_name=user_in.full_name,
        position=user_in.position or "Striker",
        country=user_in.country or "Indonesia",
        bio=user_in.bio or "Pemain sepakbola amatir bersemangat tinggi.",
        tier="Free",
        role="User"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Catat log aktivitas (NFR-013)
    log = ActivityLog(
        user_id=new_user.id,
        activity_type="REGISTER",
        description=f"User {new_user.email} berhasil mendaftar akun baru."
    )
    db.add(log)
    db.commit()

    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    UC-002 Login.
    Validasi kredensial, identifikasi peran (User/Admin), buat sesi aktif JWT (NFR-003).
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email tidak ditemukan."
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah."
        )

    # Terbitkan token JWT
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    # Catat log aktivitas
    log = ActivityLog(
        user_id=user.id,
        activity_type="LOGIN",
        description=f"User {user.email} berhasil login ke dalam sistem."
    )
    db.add(log)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "role": user.role,
        "tier": user.tier
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    UC-003 Logout.
    Menghapus sesi login pengguna dan mencatat log (NFR-003).
    """
    log = ActivityLog(
        user_id=current_user.id,
        activity_type="LOGOUT",
        description=f"User {current_user.email} telah mengakhiri sesi login."
    )
    db.add(log)
    db.commit()
    return {"message": "Sesi berhasil diakhiri. Silakan login kembali."}


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    UC-005 Melihat Data Profil.
    Menampilkan informasi profil akun pengguna aktif.
    """
    return current_user


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UC-006 Mengubah Data Profil.
    Memperbarui informasi profil akun (nama, posisi, negara, bio, foto).
    """
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.position is not None:
        current_user.position = profile_data.position
    if profile_data.country is not None:
        current_user.country = profile_data.country
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.profile_picture is not None:
        current_user.profile_picture = profile_data.profile_picture

    db.commit()
    db.refresh(current_user)
    return current_user
