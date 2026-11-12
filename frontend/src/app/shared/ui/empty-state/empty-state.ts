import { Component, input } from '@angular/core';

/** État vide : explique pourquoi il n'y a rien et, via <ng-content>, propose une action. */
@Component({
  selector: 'app-empty-state',
  template: `
    <div class="state">
      <p class="state__title">{{ heading() }}</p>
      @if (message()) {
        <p class="state__message">{{ message() }}</p>
      }
      <ng-content />
    </div>
  `,
  styles: `
    .state {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-2);
      padding: var(--space-8) var(--space-6);
      background: var(--color-surface);
      border: 1px dashed var(--color-border);
      border-radius: var(--radius-md);
    }

    .state__title {
      font-weight: var(--font-weight-semibold);
    }

    .state__message {
      color: var(--color-text-muted);
    }
  `,
})
export class EmptyState {
  readonly heading = input.required<string>();
  readonly message = input<string>();
}
