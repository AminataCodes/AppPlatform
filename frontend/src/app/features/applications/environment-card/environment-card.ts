import { DatePipe } from '@angular/common';
import { Component, computed, input } from '@angular/core';
import { RouterLink } from '@angular/router';

import { Environment } from '../../../core/models/application.model';
import { Execution, isFinished } from '../../../core/models/execution.model';
import { StatusBadge } from '../../../shared/ui/status-badge/status-badge';

/** Un environnement d'une application : version déployée et dernier déploiement. */
@Component({
  selector: 'app-environment-card',
  imports: [DatePipe, RouterLink, StatusBadge],
  template: `
    <article class="card environment" [class.environment--prod]="environment().name === 'PROD'">
      <h3 class="environment__name">
        <span class="env-tag" [class.env-tag--prod]="environment().name === 'PROD'">{{ environment().name }}</span>
      </h3>

      <p class="environment__label">Version déployée</p>
      <p class="environment__version version">{{ environment().deployed_version }}</p>

      <div class="environment__last">
        @if (lastExecution(); as execution) {
          <p class="environment__label">
            {{ inProgress() ? 'Déploiement en cours' : 'Dernier déploiement' }}
          </p>
          <p class="environment__execution">
            <app-status-badge [status]="execution.status" />
            <span class="version">{{ execution.requested_version }}</span>
            <span class="environment__date">{{ execution.created_at | date: 'dd/MM/yyyy HH:mm' }}</span>
          </p>
          <a [routerLink]="['/executions', execution.id]">
            {{ inProgress() ? 'Suivre le déploiement' : 'Voir l’exécution' }}
            <span class="visually-hidden"> sur {{ environment().name }}</span>
          </a>
        } @else {
          <p class="environment__label">Aucun déploiement demandé depuis AppPlatform.</p>
        }
      </div>
    </article>
  `,
  styles: `
    .environment {
      display: flex;
      flex-direction: column;
      height: 100%;
    }

    .environment--prod {
      border-top: 4px solid var(--color-danger);
    }

    .environment__name {
      margin-bottom: var(--space-4);
    }

    .environment__label {
      font-size: var(--font-size-sm);
      color: var(--color-text-muted);
    }

    .environment__version {
      margin-bottom: var(--space-4);
      font-size: var(--font-size-2xl);
      font-weight: var(--font-weight-semibold);
    }

    .environment__last {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: var(--space-1);
      margin-top: auto;
      padding-top: var(--space-4);
      border-top: 1px solid var(--color-border);
    }

    .environment__execution {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: var(--space-2);
    }

    .environment__date {
      font-size: var(--font-size-sm);
      color: var(--color-text-muted);
    }
  `,
})
export class EnvironmentCard {
  readonly environment = input.required<Environment>();
  readonly lastExecution = input<Execution>();

  protected readonly inProgress = computed(() => {
    const execution = this.lastExecution();
    return execution !== undefined && !isFinished(execution.status);
  });
}
