"""
PROJECT JAMES - JWT 인증 모듈 (Phase 4)

Phase 4 변경:
  [P4-AUTH-1] USER_DB → SQLite 영구화
              서버 재시작 후 계정 유지
              DB 파일: james_users.db (BASE_DIR 기준)

  [P4-AUTH-2] X-Role 개발용 헤더 → 운영 모드에서 비활성화 설정 추가

JWT_SECRET는 Phase 3.5에서 이미 환경변수화 완료 (os.environ.get)
"""

import os
import sqlite3
import hashlib
import hmac
import json
import time
import base64
from typing import Optional, Dict
from pathlib import Path

# ─── 설정 ────────────────────────────────────────────────────

JWT_SECRET = os.environ.get(
    "JAMES_JWT_SECRET",
    "james_dev_secret_change_in_prod_2026"   # 환경변수 없으면 경고
)
JWT_ALGO   = "HS256"
JWT_EXPIRE = 3600 * 8   # 8시간 (개발/운영 모두 적합)

if JWT_SECRET == "james_dev_secret_change_in_prod_2026":
    print("[AUTH] ⚠️  JAMES_JWT_SECRET 환경변수 미설정 — 개발 시크릿 사용 중 (운영 금지)")

# 운영 모드 플래그 (환경변수로 제어)
# JAMES_DEV_MODE=0 이면 X-Role 헤더 비활성화
DEV_MODE = os.environ.get("JAMES_DEV_MODE", "1") == "1"

ALLOWED_ROLES = {"admin", "manager", "employee", "external"}

# ─── [P4-AUTH-1] SQLite USER DB ──────────────────────────────

try:
    from config import BASE_DIR
    _DB_PATH = os.path.join(BASE_DIR, "james_users.db")
except ImportError:
    _DB_PATH = "james_users.db"

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db():
    """DB 초기화 + 기본 계정 생성 (없을 때만)"""
    conn = _get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username      TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL,
                active        INTEGER NOT NULL DEFAULT 1,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()

        # 기본 계정 삽입 (이미 존재하면 무시)
        defaults = [
            ("admin",     _hash_password("admin_pw_change_me"), "admin"),
            ("manager1",  _hash_password("manager_pw"),         "manager"),
            ("employee1", _hash_password("employee_pw"),         "employee"),
            ("guest",     _hash_password("guest_pw"),            "external"),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            defaults,
        )
        conn.commit()
        print(f"[AUTH] SQLite USER_DB 초기화: {_DB_PATH}")
    finally:
        conn.close()

# 서버 시작 시 DB 초기화
_init_db()

# ─── 사용자 조회 / 관리 ──────────────────────────────────────

def _get_user(username: str) -> Optional[Dict]:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

def add_user(username: str, password: str, role: str) -> bool:
    if role not in ALLOWED_ROLES:
        return False
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO users (username, password_hash, role, active) VALUES (?, ?, ?, 1)",
            (username, _hash_password(password), role),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[AUTH] add_user 오류: {e}")
        return False
    finally:
        conn.close()

def deactivate_user(username: str) -> bool:
    conn = _get_conn()
    try:
        conn.execute("UPDATE users SET active = 0 WHERE username = ?", (username,))
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

# ─── JWT 구현 ────────────────────────────────────────────────

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * (pad % 4))

def _sign(data: str) -> str:
    sig = hmac.new(JWT_SECRET.encode(), data.encode(), hashlib.sha256).digest()
    return _b64url_encode(sig)

def create_token(username: str, role: str) -> str:
    header  = _b64url_encode(json.dumps({"alg": JWT_ALGO, "typ": "JWT"}).encode())
    payload = _b64url_encode(json.dumps({
        "sub":  username,
        "role": role,
        "iat":  int(time.time()),
        "exp":  int(time.time()) + JWT_EXPIRE,
    }).encode())
    sig = _sign(f"{header}.{payload}")
    return f"{header}.{payload}.{sig}"

def verify_token(token: str) -> Optional[Dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, sig = parts

        expected = _sign(f"{header}.{payload}")
        if not hmac.compare_digest(sig, expected):
            print("[AUTH] 서명 검증 실패")
            return None

        data = json.loads(_b64url_decode(payload))
        if data.get("exp", 0) < time.time():
            print("[AUTH] 토큰 만료")
            return None

        role = data.get("role", "external")
        if role not in ALLOWED_ROLES:
            print(f"[AUTH] 허용되지 않은 role: {role}")
            return None

        return {"sub": data.get("sub"), "role": role}
    except Exception as e:
        print(f"[AUTH] 토큰 파싱 오류: {e}")
        return None

# ─── 인증 ────────────────────────────────────────────────────

def authenticate(username: str, password: str) -> Optional[Dict]:
    """로그인 → SQLite 조회 → token 반환"""
    user = _get_user(username)
    if not user:
        print(f"[AUTH] 사용자 없음: {username}")
        return None
    if not user.get("active"):
        print(f"[AUTH] 비활성 계정: {username}")
        return None

    pw_hash = _hash_password(password)
    if not hmac.compare_digest(pw_hash, user["password_hash"]):
        print(f"[AUTH] 비밀번호 불일치: {username}")
        return None

    role  = user["role"]
    token = create_token(username, role)
    print(f"[AUTH] 로그인 성공: {username} (role={role})")
    return {"token": token, "role": role, "username": username}

def get_role_from_token(token: str) -> str:
    data = verify_token(token)
    if data is None:
        return "external"
    return data.get("role", "external")

def get_current_role(authorization: str = "") -> str:
    if not authorization.startswith("Bearer "):
        return "external"
    token = authorization[7:].strip()
    return get_role_from_token(token)
