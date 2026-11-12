import { HttpErrorResponse } from '@angular/common/http';

export type ApiErrorKind = 'network' | 'not-found' | 'conflict' | 'validation' | 'server' | 'unknown';

/** Erreur d'API sous une forme unique, prête à être affichée. */
export interface ApiError {
  kind: ApiErrorKind;
  status: number;
  message: string;
}

/**
 * Normalise une erreur HTTP.
 *
 * FastAPI renvoie toujours `{ "detail": ... }` :
 * - erreur métier (404, 409, 422 métier) : `detail` est un texte en français, affiché tel quel ;
 * - erreur de validation Pydantic (422) : `detail` est une liste technique, remplacée par un message générique.
 */
export function toApiError(error: unknown): ApiError {
  if (!(error instanceof HttpErrorResponse)) {
    return { kind: 'unknown', status: 0, message: 'Une erreur inattendue est survenue.' };
  }

  if (error.status === 0) {
    return {
      kind: 'network',
      status: 0,
      message: "Impossible de joindre le serveur. Vérifiez votre connexion et que l'API est démarrée.",
    };
  }

  const detail: unknown = error.error?.detail;
  const businessMessage = typeof detail === 'string' ? detail : null;

  switch (error.status) {
    case 404:
      return { kind: 'not-found', status: 404, message: businessMessage ?? 'La ressource demandée est introuvable.' };
    case 409:
      return { kind: 'conflict', status: 409, message: businessMessage ?? 'Une opération est déjà en cours.' };
    case 422:
      return { kind: 'validation', status: 422, message: businessMessage ?? 'La demande contient des données invalides.' };
  }

  if (error.status >= 500) {
    return {
      kind: 'server',
      status: error.status,
      message: 'Le serveur est indisponible ou a rencontré une erreur. Réessayez dans quelques instants.',
    };
  }

  return { kind: 'unknown', status: error.status, message: businessMessage ?? 'Une erreur inattendue est survenue.' };
}
