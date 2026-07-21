"""
Base de données GUELANE — SQLAlchemy.

Développement : SQLite (fichier prophet.db, zéro installation).
Production : PostgreSQL (il suffira de changer DATABASE_URL dans .env).
Le code ne change pas grâce à SQLAlchemy.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# En local : SQLite. En prod Railway : DATABASE_URL pointera vers PostgreSQL.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./prophet.db")

# Railway fournit parfois des URL "postgres://" — SQLAlchemy veut "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# connect_args nécessaire seulement pour SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nom = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    plan = Column(String, default="gratuit")  # "gratuit" | "premium"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatUsage(Base):
    """Compte les messages de chat par utilisateur et par jour (pour la limite gratuite)."""
    __tablename__ = "chat_usage"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    jour = Column(String, index=True, nullable=False)  # format "AAAA-MM-JJ"
    count = Column(Integer, default=0)


def init_db():
    """Crée les tables si elles n'existent pas."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Fournit une session DB (à fermer après usage)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
