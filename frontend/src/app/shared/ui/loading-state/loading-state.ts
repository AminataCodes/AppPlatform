import { Component, input } from '@angular/core';

/** État de chargement : role="status" annonce le message aux lecteurs d'écran. */
@Component({
  selector: 'app-loading-state',
  template: `
    <div class="state" role="status">
      <span class="spinner" aria-hidden="true"></span>
      <p>{{ label() }}</p>
    </div>
  `,
  styles: `
    .state {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-8) var(--space-6);
      color: var(--color-text-muted);
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
    }

    .spinner {
      width: 1.25rem;
      height: 1.25rem;
      border: 3px solid var(--color-border);
      border-top-color: var(--color-primary);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  `,
})
export class LoadingState {
  readonly label = input('Chargement…');
}
