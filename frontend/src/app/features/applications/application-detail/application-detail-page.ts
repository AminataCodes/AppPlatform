import { Component, DestroyRef, OnInit, computed, inject, input, numberAttribute, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { ApiError, toApiError } from '../../../core/http/api-error';
import { Application } from '../../../core/models/application.model';
import { Execution } from '../../../core/models/execution.model';
import { ApplicationApiService } from '../../../core/services/application-api.service';
import { ExecutionApiService } from '../../../core/services/execution-api.service';
import { EmptyState } from '../../../shared/ui/empty-state/empty-state';
import { ErrorState } from '../../../shared/ui/error-state/error-state';
import { LoadingState } from '../../../shared/ui/loading-state/loading-state';
import { ExecutionTable } from '../../executions/execution-table/execution-table';
import { EnvironmentCard } from '../environment-card/environment-card';

const RECENT_EXECUTIONS_COUNT = 5;

@Component({
  selector: 'app-application-detail-page',
  imports: [RouterLink, LoadingState, ErrorState, EmptyState, EnvironmentCard, ExecutionTable],
  templateUrl: './application-detail-page.html',
  styleUrl: './application-detail-page.scss',
})
export class ApplicationDetailPage implements OnInit {
  private readonly applicationApi = inject(ApplicationApiService);
  private readonly executionApi = inject(ExecutionApiService);
  private readonly destroyRef = inject(DestroyRef);

  readonly id = input.required({ transform: numberAttribute });

  protected readonly application = signal<Application | null>(null);
  /** Exécutions de cette application, de la plus récente à la plus ancienne. */
  protected readonly executions = signal<Execution[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal<ApiError | null>(null);

  protected readonly recentExecutions = computed(() => this.executions().slice(0, RECENT_EXECUTIONS_COUNT));

  /** Dernière exécution de chaque environnement (la liste est déjà triée, la première trouvée est la plus récente). */
  protected readonly lastExecutionByEnvironment = computed(() => {
    const lastExecutions = new Map<number, Execution>();
    for (const execution of this.executions()) {
      if (!lastExecutions.has(execution.environment.id)) {
        lastExecutions.set(execution.environment.id, execution);
      }
    }
    return lastExecutions;
  });

  ngOnInit(): void {
    this.load();
  }

  /** Environnements où une version donnée est actuellement déployée. */
  protected environmentsRunning(application: Application, version: string): string[] {
    return application.environments.filter((env) => env.deployed_version === version).map((env) => env.name);
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(null);
    // Les deux requêtes partent en parallèle ; forkJoin attend les deux réponses.
    forkJoin({
      application: this.applicationApi.getApplication(this.id()),
      executions: this.executionApi.getExecutions(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ application, executions }) => {
          this.application.set(application);
          this.executions.set(executions.filter((execution) => execution.application.id === application.id));
          this.loading.set(false);
        },
        error: (error: unknown) => {
          this.error.set(toApiError(error));
          this.loading.set(false);
        },
      });
  }
}
