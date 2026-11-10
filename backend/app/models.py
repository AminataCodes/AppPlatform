"""Modèles SQLAlchemy : la forme des tables dans SQLite."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text, TypeDecorator, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EnvironmentName(StrEnum):
    DEV = "DEV"
    STAGING = "STAGING"
    PROD = "PROD"


class ExecutionStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class LogLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class UTCDateTime(TypeDecorator):
    """Date toujours en UTC.

    SQLite ne conserve pas le fuseau horaire : sans ce type, une date relue
    serait « naïve » et le frontend ne saurait pas qu'elle est en UTC.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        # Écriture : conversion en UTC, puis stockage sans fuseau.
        if value is None:
            return None
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        # Lecture : la valeur stockée est en UTC, on le rend explicite.
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


def utc_now() -> datetime:
    return datetime.now(UTC)


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
    executions: Mapped[list["Execution"]] = relationship(back_populates="application")


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
    executions: Mapped[list["Execution"]] = relationship(back_populates="environment")


class Execution(Base):
    """Une demande de déploiement et son déroulement."""

    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Index : l'historique sera filtré par application et par environnement.
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), index=True)
    environment_id: Mapped[int] = mapped_column(ForeignKey("environments.id"), index=True)
    requested_version: Mapped[str] = mapped_column(String(50))
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, native_enum=False, create_constraint=True, length=10),
        default=ExecutionStatus.QUEUED,
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    # Vides tant que l'exécution n'a pas démarré / ne s'est pas terminée.
    started_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    application: Mapped[Application] = relationship(back_populates="executions")
    environment: Mapped[Environment] = relationship(back_populates="executions")
    # Logs dans l'ordre d'écriture ; supprimés avec leur exécution.
    logs: Mapped[list["ExecutionLog"]] = relationship(
        back_populates="execution",
        order_by="ExecutionLog.id",
        cascade="all, delete-orphan",
    )


class ExecutionLog(Base):
    """Un message produit pendant une exécution."""

    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_id: Mapped[int] = mapped_column(ForeignKey("executions.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel, native_enum=False, create_constraint=True, length=10),
        default=LogLevel.INFO,
    )
    message: Mapped[str] = mapped_column(Text)

    execution: Mapped[Execution] = relationship(back_populates="logs")
