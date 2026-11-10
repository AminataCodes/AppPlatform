"""Route de demande de déploiement."""

from fastapi import APIRouter, HTTPException, status

from app.database import DbSession
from app.schemas import DeploymentRequest, ExecutionRead
from app.services.deployment_service import (
    DeploymentConflictError,
    DeploymentRejectedError,
    NotFoundError,
    request_deployment,
)

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        404: {"description": "Application ou environnement introuvable"},
        409: {"description": "Un déploiement est déjà en cours sur cet environnement"},
        422: {"description": "Requête invalide ou règle métier non respectée"},
    },
)
def create_deployment(request: DeploymentRequest, db: DbSession) -> ExecutionRead:
    # 202 Accepted : la demande est enregistrée, mais le déploiement n'est pas encore exécuté.
    try:
        execution = request_deployment(db, request)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except DeploymentRejectedError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))
    except DeploymentConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    return ExecutionRead.model_validate(execution)
