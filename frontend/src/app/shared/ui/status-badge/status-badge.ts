import { Component, computed, input } from '@angular/core';

import { ExecutionStatus } from '../../../core/models/execution.model';

// Tracés SVG (grille 24 × 24) : chaque statut a sa propre forme,
// pour ne pas dépendre de la couleur seule.
const STATUS_ICONS: Record<ExecutionStatus, string> = {
  QUEUED: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3 2',
  RUNNING: 'M21 12a9 9 0 1 1-6.2-8.56',
  SUCCEEDED: 'M5 12.5l4.5 4.5L19 7.5',
  FAILED: 'M6 6l12 12M18 6L6 18',
};

/** Statut d'exécution : icône + texte + couleur. Le texte reste en anglais (valeur métier). */
@Component({
  selector: 'app-status-badge',
  template: `
    <span class="status-badge" [class]="'status-badge status-badge--' + status().toLowerCase()">
      <svg class="status-badge__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path [attr.d]="icon()" />
      </svg>
      <span class="visually-hidden">Statut :</span>
      {{ status() }}
    </span>
  `,
  styles: `
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      padding: 0.125rem var(--space-2);
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-semibold);
      letter-spacing: 0.02em;
      white-space: nowrap;
      border: 1px solid currentColor;
      border-radius: 999px;
    }

    .status-badge__icon {
      width: 0.875rem;
      height: 0.875rem;
      fill: none;
      stroke: currentColor;
      stroke-width: 2.5;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .status-badge--queued {
      color: var(--color-text-muted);
      background: var(--color-bg);
    }

    .status-badge--running {
      color: var(--color-info);
      background: var(--color-info-soft);
    }

    .status-badge--running .status-badge__icon {
      animation: spin 1s linear infinite;
    }

    .status-badge--succeeded {
      color: var(--color-success);
      background: var(--color-success-soft);
    }

    .status-badge--failed {
      color: var(--color-danger);
      background: var(--color-danger-soft);
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  `,
})
export class StatusBadge {
  readonly status = input.required<ExecutionStatus>();

  protected readonly icon = computed(() => STATUS_ICONS[this.status()]);
}
