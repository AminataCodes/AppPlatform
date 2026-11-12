import { Component, input, output } from '@angular/core';

import { ApiError } from '../../../core/http/api-error';

/** État d'erreur : message compréhensible + bouton « Réessayer ». role="alert" l'annonce immédiatement. */
@Component({
  selector: 'app-error-state',
  template: `
    <div class="alert alert--danger error-state" role="alert">
      <p class="error-state__title">{{ heading() }}</p>
      <p>{{ error().message }}</p>
      <button type="button" class="btn btn--secondary" (click)="retry.emit()">Réessayer</button>
    </div>
  `,
  styles: `
    .error-state {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-2);
    }

    .error-state__title {
      font-weight: var(--font-weight-semibold);
    }
  `,
})
export class ErrorState {
  readonly error = input.required<ApiError>();
  readonly heading = input('Impossible de charger les données');
  readonly retry = output<void>();
}
