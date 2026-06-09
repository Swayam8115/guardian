from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from database.db import SessionLocal
from database.models import UserModel
from datetime import datetime, timezone

router = APIRouter()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Shared helper ─────────────────────────────────────────────────────────────
def _user_response(user: UserModel) -> dict:
    return {"name": user.name, "email": user.email, "picture": user.picture or ""}


# ── Google OAuth ──────────────────────────────────────────────────────────────
class GoogleCredential(BaseModel):
    credential: str
    client_id: str


@router.post("/auth/google")
def google_auth(body: GoogleCredential):
    try:
        info = id_token.verify_oauth2_token(
            body.credential,
            google_requests.Request(),
            body.client_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.email == info["email"]).first()
        if not user:
            user = UserModel(
                name=info.get("name", ""),
                email=info["email"],
                picture=info.get("picture", ""),
                provider="google",
                created_at=datetime.now(timezone.utc),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return _user_response(user)
    finally:
        db.close()


# ── Manual register ───────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


@router.post("/auth/register")
def register(body: RegisterRequest):
    db = SessionLocal()
    try:
        if db.query(UserModel).filter(UserModel.email == body.email).first():
            raise HTTPException(status_code=409, detail="Email already registered.")
        user = UserModel(
            name=body.name,
            email=body.email,
            password_hash=pwd_ctx.hash(body.password),
            provider="manual",
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return _user_response(user)
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered.")
    finally:
        db.close()


# ── Manual login ──────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/auth/login")
def login(body: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.email == body.email).first()
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        if not pwd_ctx.verify(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return _user_response(user)
    finally:
        db.close()
