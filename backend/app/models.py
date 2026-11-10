"""Modèles SQLAlchemy : la forme des tables dans SQLite."""

from enum import StrEnum

from sqlalchemy import JSON, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EnvironmentName(StrEnum):
    DEV = "DEV"
    STAGING = "STAGING"
    PROD = "PROD"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(500))
    owner_team: Mapped[str] = mapped_column(String(100))
    # Liste de versions stockée en JSON : pas de table Version en V1.
    available_versions: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Environnements triés par id : le seed les crée dans l'ordre DEV, STAGING, PROD.
    environments: Mapped[list["Environment"]] = relationship(
        back_populates="application",
        order_by="Environment.id",
        cascade="all, delete-orphan",
    )


class Environment(Base):
    __tablename__ = "environments"
    # Un seul environnement de chaque type par application.
    __table_args__ = (UniqueConstraint("application_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    # Stocké en texte, avec une contrainte CHECK limitée à DEV / STAGING / PROD.
    name: Mapped[EnvironmentName] = mapped_column(
        Enum(EnvironmentName, native_enum=False, create_constraint=True, length=10)
    )
    deployed_version: Mapped[str] = mapped_column(String(50))

    application: Mapped[Application] = relationship(back_populates="environments")
