import asyncio
import hashlib
import os
import random
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import Cookie, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import func

from .config import (
    ACTIVE_USER_SECONDS, ABOUT_TEXT, APP_HOST, APP_PORT, CLICK_LIMIT_PER_MINUTE,
    COOKIE_SECURE, CORS_ORIGINS, DEMO_ACTIVITY_ENABLED
)
from .db import SessionLocal, School, Visitor, init_db
from .schools import CATEGORY_LABELS, CATEGORY_ORDER, SCHOOL_BY_ID, asset_paths

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
CLICK_COOKIE = "ksl_visitor"

class ClickPayload(BaseModel):
    school_id: str
    clicks: int = Field(ge=1, le=10000)

class HeartbeatPayload(BaseModel):
    school_id: str | None = None


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def ensure_visitor(response: Response | None = None, token: str | None = None):
    # Helper used by endpoints; returns (visitor, new_token).
    new_token = False
    if not token:
        token = secrets.token_urlsafe(32)
        new_token = True
    token_hash = hash_token(token)
    with SessionLocal() as db:
        visitor = db.get(Visitor, token_hash)
        if visitor is None:
            visitor = Visitor(token_hash=token_hash, created_at=now_utc(), last_seen=now_utc(), rate_clicks=0)
            db.add(visitor)
            db.commit()
        else:
            visitor.last_seen = now_utc()
            db.commit()
    return token, new_token


def apply_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        CLICK_COOKIE,
        token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def totals_from_school(school: School) -> int:
    return school.real_clicks + school.artificial_clicks


async def demo_activity_loop() -> None:
    # Optional synthetic activity. It is kept separate in artificial_clicks and is off by default.
    while True:
        await asyncio.sleep(random.randint(15, 45))
        now = now_utc()
        with SessionLocal() as db:
            schools = db.query(School).all()
            if not schools:
                continue
            for school in random.sample(schools, k=min(random.randint(1, 4), len(schools))):
                chunk = random.randint(5, 55)
                school.artificial_clicks += chunk
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = None
    if DEMO_ACTIVITY_ENABLED:
        task = asyncio.create_task(demo_activity_loop())
    yield
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="Kaliningrad School Leaderboard", version="1.0.0", lifespan=lifespan)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

app.mount("/assets", StaticFiles(directory=str(STATIC_DIR)), name="assets")

@app.get("/api/session")
def session(response: Response, ksl_visitor: str | None = Cookie(default=None)):
    token, new_token = ensure_visitor(token=ksl_visitor)
    if new_token:
        apply_cookie(response, token)
    return {"ok": True}

@app.get("/api/schools")
def schools():
    grouped = []
    for category in CATEGORY_ORDER:
        items = []
        for spec in SCHOOL_BY_ID.values():
            if spec.category != category:
                continue
            items.append({
                "id": spec.id,
                "name": spec.name,
                "category": spec.category,
                "category_label": spec.category_label,
                "images": asset_paths(spec),
            })
        grouped.append({"id": category, "name": CATEGORY_LABELS[category], "schools": items})
    return {"categories": grouped}

@app.get("/api/leaderboard")
def leaderboard():
    with SessionLocal() as db:
        rows = db.query(School).all()
        rows.sort(key=totals_from_school, reverse=True)
        result = []
        for idx, school in enumerate(rows, start=1):
            result.append({
                "rank": idx,
                "id": school.id,
                "name": school.name,
                "category": school.category,
                "clicks": totals_from_school(school),
                "real_clicks": school.real_clicks,
                "artificial_clicks": school.artificial_clicks,
            })
        return {"items": result}

@app.get("/api/stats")
def stats():
    cutoff = now_utc() - timedelta(seconds=ACTIVE_USER_SECONDS)
    with SessionLocal() as db:
        users = db.query(func.count(Visitor.token_hash)).scalar() or 0
        active = db.query(func.count(Visitor.token_hash)).filter(Visitor.last_seen >= cutoff).scalar() or 0
        real = db.query(func.coalesce(func.sum(School.real_clicks), 0)).scalar() or 0
        artificial = db.query(func.coalesce(func.sum(School.artificial_clicks), 0)).scalar() or 0
        return {
            "users": int(users),
            "active_users": int(active),
            "total_clicks": int(real + artificial),
            "real_clicks": int(real),
            "artificial_clicks": int(artificial),
        }

@app.get("/api/about")
def about():
    return {"title": "О проекте", "text": ABOUT_TEXT}

@app.post("/api/heartbeat")
def heartbeat(payload: HeartbeatPayload, response: Response, ksl_visitor: str | None = Cookie(default=None)):
    token, new_token = ensure_visitor(token=ksl_visitor)
    if new_token:
        apply_cookie(response, token)
    return {"ok": True}

@app.post("/api/clicks")
def clicks(payload: ClickPayload, request: Request, response: Response, ksl_visitor: str | None = Cookie(default=None)):
    if payload.school_id not in SCHOOL_BY_ID:
        raise HTTPException(status_code=404, detail="Учебное заведение не найдено")

    token, new_token = ensure_visitor(token=ksl_visitor)
    if new_token:
        apply_cookie(response, token)

    now = now_utc()
    token_hash = hash_token(token)
    with SessionLocal() as db:
        visitor = db.get(Visitor, token_hash)
        if visitor is None:
            visitor = Visitor(token_hash=token_hash, created_at=now, last_seen=now, rate_clicks=0)
            db.add(visitor)
            db.flush()

        visitor.last_seen = now
        if not visitor.rate_window_start or (now - visitor.rate_window_start).total_seconds() >= 60:
            visitor.rate_window_start = now
            visitor.rate_clicks = 0

        remaining = max(0, CLICK_LIMIT_PER_MINUTE - visitor.rate_clicks)
        accepted = min(payload.clicks, remaining)
        rejected = payload.clicks - accepted

        if accepted:
            db.query(School).filter(School.id == payload.school_id).update(
                {School.real_clicks: School.real_clicks + accepted},
                synchronize_session=False,
            )
            visitor.rate_clicks += accepted
        db.commit()

    return {
        "ok": True,
        "accepted": accepted,
        "rejected": rejected,
        "limit_per_minute": CLICK_LIMIT_PER_MINUTE,
        "remaining": max(0, CLICK_LIMIT_PER_MINUTE - visitor.rate_clicks),
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "kaliningrad-school-leaderboard"}

@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")

# Cache immutable branding and photographs for a year. The HTML/JS/CSS stay revalidated normally.
@app.middleware("http")
async def cache_assets(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/assets/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
