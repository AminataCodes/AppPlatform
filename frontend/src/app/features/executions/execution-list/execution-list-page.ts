import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

import { ApiError, toApiError } from '../../../core/http/api-error';
import { Execution } from '../../../core/models/execution.model';
import { ExecutionApiService } from '../../../core/services/execution-api.service';
import { EmptyState } from '../../../shared/ui/empty-state/empty-state';
import { ErrorState } from '../../../shared/ui/error-state/error-state';
import { LoadingState } from '../../../shared/ui/loading-state/loading-state';
import { PageHeader } from '../../../shared/ui/page-header/page-header';
import { ExecutionTable } from '../execution-table/execution-table';

@Component({
  selector: 'app-execution-list-page',
  imports: [RouterLink, PageHeader, LoadingState, ErrorState, EmptyState, ExecutionTable],
  template: `
    <app-page-header
      heading="Historique des exécutions"
      description="Toutes les demandes de déploiement, de la plus récente à la plus ancienne."
    />

    @if (loading()) {
      <app-loading-state label="Chargement de l'historique…" />
    } @else if (error(); as error) {
      <app-error-state [error]="error" (retry)="load()" />
    } @else if (executions().length === 0) {
      <app-empty-state
        heading="Aucune exécution pour le moment"
        message="Les demandes de déploiement apparaîtront ici dès qu'elles seront envoyées."
      >
        <a class="btn btn--primary" routerLink="/applications">Choisir une application</a>
      </app-empty-state>
    } @else {
      <app-execution-table [executions]="executions()" caption="Historique des exécutions" />
    }
  `,
})
export class ExecutionListPage {
  private readonly executionApi = inject(ExecutionApiService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly executions = signal<Execution[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal<ApiError | null>(null);

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.executionApi
      .getExecutions()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (executions) => {
          this.executions.set(executions);
          this.loading.set(false);
        },
        error: (error: unknown) => {
          this.error.set(toApiError(error));
          this.loading.set(false);
        },
      });
  }
}
