import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(DATA_DIR / 'leaderboard.db').as_posix()}")
APP_HOST = os.getenv("HOST", "127.0.0.1")
APP_PORT = int(os.getenv("PORT", "8000"))
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()]
DEMO_ACTIVITY_ENABLED = os.getenv("DEMO_ACTIVITY_ENABLED", "false").lower() == "true"
CLICK_LIMIT_PER_MINUTE = int(os.getenv("CLICK_LIMIT_PER_MINUTE", "800"))
ACTIVE_USER_SECONDS = int(os.getenv("ACTIVE_USER_SECONDS", "60"))
RATING_REFRESH_SECONDS = int(os.getenv("RATING_REFRESH_SECONDS", "5"))
STATS_REFRESH_SECONDS = int(os.getenv("STATS_REFRESH_SECONDS", "30"))

ABOUT_TEXT = os.getenv(
    "ABOUT_TEXT",
    "Kaliningrad School Leaderboard — интерактивный рейтинг учебных заведений Калининграда. "
    "Выберите своё учебное заведение и поддерживайте его кликами."
)
