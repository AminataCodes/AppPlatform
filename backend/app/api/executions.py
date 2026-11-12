"""Routes de consultation des exécutions (lecture seule)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.database import DbSession
from app.models import Execution
from app.schemas import ExecutionDetail, ExecutionRead

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("")
def list_executions(db: DbSession) -> list[ExecutionRead]:
    # joinedload : l'application et l'environnement de chaque exécution sont lus
    # dans la même requête SQL (jointure), au lieu d'une requête par exécution.
    query = (
        select(Execution)
        .options(joinedload(Execution.application), joinedload(Execution.environment))
        .order_by(Execution.created_at.desc(), Execution.id.desc())
    )
    executions = db.scalars(query).all()
    return [ExecutionRead.model_validate(execution) for execution in executions]


@router.get("/{execution_id}")
def get_execution(execution_id: int, db: DbSession) -> ExecutionDetail:
    execution = db.get(
        Execution,
        execution_id,
        # selectinload pour la liste des logs (une requête de plus, pas une par log).
        # Les logs sont triés par ordre d'écriture (voir la relation Execution.logs).
        options=[
            joinedload(Execution.application),
            joinedload(Execution.environment),
            selectinload(Execution.logs),
        ],
    )
    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exécution {execution_id} introuvable.",
        )
    return ExecutionDetail.model_validate(execution)
