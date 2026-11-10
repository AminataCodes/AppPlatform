"""Données de démonstration (applications fictives).

Le seed est idempotent : une application déjà présente (même nom) n'est ni
recréée ni modifiée. Les versions changées plus tard par des déploiements
ne sont donc jamais écrasées au redémarrage.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Application, Environment, EnvironmentName

# Chaque version déployée fait partie des versions disponibles de l'application.
SEED_APPLICATIONS = [
    {
        "name": "customer-api",
        "description": "API de gestion des données clients : profils, coordonnées et préférences.",
        "owner_team": "Équipe Clients",
        "available_versions": ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"],
        "deployed_versions": {"DEV": "1.3.0", "STAGING": "1.2.0", "PROD": "1.1.0"},
    },
    {
        "name": "payment-api",
        "description": "API de traitement des paiements par carte et des remboursements.",
        "owner_team": "Équipe Paiements",
        "available_versions": ["2.0.0", "2.1.0", "2.1.1", "2.2.0", "2.3.0"],
        "deployed_versions": {"DEV": "2.2.0", "STAGING": "2.2.0", "PROD": "2.1.1"},
    },
    {
        "name": "banking-portal",
        "description": "Portail web de banque en ligne destiné aux clients particuliers.",
        "owner_team": "Équipe Portail Web",
        "available_versions": ["3.4.0", "3.5.0", "3.5.1", "3.6.0"],
        "deployed_versions": {"DEV": "3.6.0", "STAGING": "3.5.1", "PROD": "3.5.0"},
    },
]


def seed_database(session: Session) -> int:
    """Insère les applications manquantes et renvoie le nombre d'applications créées."""
    existing_names = set(session.scalars(select(Application.name)))
    created = 0

    for data in SEED_APPLICATIONS:
        if data["name"] in existing_names:
            continue

        application = Application(
            name=data["name"],
            description=data["description"],
            owner_team=data["owner_team"],
            available_versions=data["available_versions"],
            # Parcourir l'enum garantit l'ordre DEV, STAGING, PROD.
            environments=[
                Environment(name=env_name, deployed_version=data["deployed_versions"][env_name])
                for env_name in EnvironmentName
            ],
        )
        session.add(application)
        created += 1

    session.commit()
    return created
