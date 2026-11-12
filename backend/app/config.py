"""Configuration minimale de l'application.

Des constantes simples suffisent pour la V1 : pas de bibliothèque de configuration
supplémentaire. Seule l'adresse de la base peut être changée par variable
d'environnement, ce qui permet aux tests d'utiliser leur propre base.
"""

import os
from pathlib import Path

APP_NAME = "AppPlatform API"
APP_VERSION = "0.1.0"

# Préfixe commun à toutes les routes : /api/health, /api/applications...
API_PREFIX = "/api"

# Base SQLite de développement : backend/appplatform.db (ignorée par Git).
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.environ.get(
    "APPPLATFORM_DATABASE_URL",
    f"sqlite:///{BACKEND_DIR / 'appplatform.db'}",
)

# Pause entre deux étapes de la simulation : assez courte pour une démo,
# assez longue pour voir le statut RUNNING. Les tests la mettent à 0.
SIMULATION_STEP_DELAY_SECONDS = float(os.environ.get("APPPLATFORM_SIMULATION_STEP_DELAY_SECONDS", "1.0"))
