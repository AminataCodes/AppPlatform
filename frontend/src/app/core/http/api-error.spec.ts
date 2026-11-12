import { HttpErrorResponse } from '@angular/common/http';

import { toApiError } from './api-error';

function httpError(status: number, body: unknown = null): HttpErrorResponse {
  return new HttpErrorResponse({ status, error: body });
}

describe('toApiError', () => {
  it('reports a network error when the server cannot be reached', () => {
    const error = toApiError(httpError(0));

    expect(error.kind).toBe('network');
    expect(error.message).toContain('Impossible de joindre le serveur');
  });

  it('keeps the business message returned by the API', () => {
    expect(toApiError(httpError(404, { detail: 'Application 9999 introuvable.' }))).toEqual({
      kind: 'not-found',
      status: 404,
      message: 'Application 9999 introuvable.',
    });
    expect(toApiError(httpError(409, { detail: 'Un déploiement est déjà en cours.' })).kind).toBe('conflict');
    expect(toApiError(httpError(422, { detail: 'Un déploiement en PROD doit être explicitement confirmé.' }))).toEqual({
      kind: 'validation',
      status: 422,
      message: 'Un déploiement en PROD doit être explicitement confirmé.',
    });
  });

  it('replaces a technical Pydantic error list with a readable message', () => {
    const body = { detail: [{ type: 'missing', loc: ['body', 'application_id'], msg: 'Field required' }] };

    const error = toApiError(httpError(422, body));

    expect(error.kind).toBe('validation');
    expect(error.message).toBe('La demande contient des données invalides.');
  });

  it('hides server error details', () => {
    const error = toApiError(httpError(500, 'Traceback (most recent call last)…'));

    expect(error.kind).toBe('server');
    expect(error.message).not.toContain('Traceback');
  });

  it('handles errors that are not HTTP errors', () => {
    expect(toApiError(new Error('boom')).kind).toBe('unknown');
  });
});
