from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from app.database import get_connection
from jose import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import base64
import hmac
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)
    organization_name: str = Field(min_length=2, max_length=150)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600000
    )

    return (
        "pbkdf2_sha256$600000$"
        + base64.b64encode(salt).decode()
        + "$"
        + base64.b64encode(hashed).decode()
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            base64.b64decode(salt),
            int(iterations)
        )

        return hmac.compare_digest(
            actual_hash,
            base64.b64decode(expected_hash)
        )
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, organization_id: int):
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not configured")

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "organization_id": organization_id,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
def register_user(data: RegisterRequest):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT user_id FROM Users WHERE email = ?",
            (data.email,)
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

        cursor.execute(
            """
            INSERT INTO Organizations (organization_name)
            OUTPUT INSERTED.organization_id
            VALUES (?)
            """,
            (data.organization_name,)
        )

        organization_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO Settings
            (organization_id, default_low_stock_threshold)
            VALUES (?, 5)
            """,
            (organization_id,)
        )

        password_hash = hash_password(data.password)

        cursor.execute(
            """
            INSERT INTO Users
            (organization_id, full_name, email, password_hash)
            OUTPUT INSERTED.user_id
            VALUES (?, ?, ?, ?)
            """,
            (
                organization_id,
                data.full_name,
                data.email,
                password_hash
            )
        )

        user_id = cursor.fetchone()[0]
        connection.commit()

        return {
            "message": "Registration successful",
            "user_id": user_id,
            "organization_id": organization_id,
            "email": data.email
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

    finally:
        cursor.close()
        connection.close()


@router.post("/login")
def login_user(data: LoginRequest):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT user_id, organization_id, full_name,
                   email, password_hash
            FROM Users
            WHERE email = ?
            """,
            (data.email,)
        )

        user = cursor.fetchone()

        if not user or not verify_password(
            data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = create_access_token(
            user.user_id,
            user.organization_id
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user.user_id,
                "organization_id": user.organization_id,
                "full_name": user.full_name,
                "email": user.email
            }
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )

    finally:
        cursor.close()
        connection.close()