from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Index
from .config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class School(Base):
    __tablename__ = "schools"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    category_label: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    folder: Mapped[str] = mapped_column(String(255), unique=True)
    real_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    artificial_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

class Visitor(Base):
    __tablename__ = "visitors"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True)
    rate_window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rate_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)



def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    from .schools import SCHOOLS
    with SessionLocal() as db:
        existing = {row.id for row in db.query(School).all()}
        for spec in SCHOOLS:
            if spec.id not in existing:
                db.add(School(
                    id=spec.id,
                    category=spec.category,
                    category_label=spec.category_label,
                    name=spec.name,
                    folder=spec.folder,
                    real_clicks=0,
                    artificial_clicks=0,
                ))
        db.commit()
