"""Routes du catalogue d'applications (lecture seule)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import DbSession
from app.models import Application
from app.schemas import ApplicationRead

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("")
def list_applications(db: DbSession) -> list[ApplicationRead]:
    # selectinload charge les environnements de toutes les applications en une
    # seule requête supplémentaire, au lieu d'une requête par application.
    query = select(Application).options(selectinload(Application.environments)).order_by(Application.id)
    applications = db.scalars(query).all()
    return [ApplicationRead.model_validate(application) for application in applications]


@router.get("/{application_id}")
def get_application(application_id: int, db: DbSession) -> ApplicationRead:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} introuvable.",
        )
    return ApplicationRead.model_validate(application)
