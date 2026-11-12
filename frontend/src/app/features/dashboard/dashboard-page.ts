import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { ApiError, toApiError } from '../../core/http/api-error';
import { Application } from '../../core/models/application.model';
import { Execution, ExecutionStatus, isFinished } from '../../core/models/execution.model';
import { ApplicationApiService } from '../../core/services/application-api.service';
import { ExecutionApiService } from '../../core/services/execution-api.service';
import { EmptyState } from '../../shared/ui/empty-state/empty-state';
import { ErrorState } from '../../shared/ui/error-state/error-state';
import { LoadingState } from '../../shared/ui/loading-state/loading-state';
import { PageHeader } from '../../shared/ui/page-header/page-header';
import { ExecutionTable } from '../executions/execution-table/execution-table';

const RECENT_EXECUTIONS_COUNT = 5;

// Indicateurs calculés à partir des endpoints existants (pas d'endpoint dédié au tableau de bord).
@Component({
  selector: 'app-dashboard-page',
  imports: [RouterLink, PageHeader, LoadingState, ErrorState, EmptyState, ExecutionTable],
  templateUrl: './dashboard-page.html',
  styleUrl: './dashboard-page.scss',
})
export class DashboardPage {
  private readonly applicationApi = inject(ApplicationApiService);
  private readonly executionApi = inject(ExecutionApiService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly applications = signal<Application[]>([]);
  protected readonly executions = signal<Execution[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal<ApiError | null>(null);

  protected readonly recentExecutions = computed(() => this.executions().slice(0, RECENT_EXECUTIONS_COUNT));
  protected readonly succeededCount = computed(() => this.countByStatus('SUCCEEDED'));
  protected readonly failedCount = computed(() => this.countByStatus('FAILED'));
  protected readonly activeCount = computed(
    () => this.executions().filter((execution) => !isFinished(execution.status)).length,
  );

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      applications: this.applicationApi.getApplications(),
      executions: this.executionApi.getExecutions(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ applications, executions }) => {
          this.applications.set(applications);
          this.executions.set(executions);
          this.loading.set(false);
        },
        error: (error: unknown) => {
          this.error.set(toApiError(error));
          this.loading.set(false);
        },
      });
  }

  private countByStatus(status: ExecutionStatus): number {
    return this.executions().filter((execution) => execution.status === status).length;
  }
}
