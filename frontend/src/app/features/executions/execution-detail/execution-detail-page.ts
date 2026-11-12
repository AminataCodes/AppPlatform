import { DatePipe } from '@angular/common';
import { Component, DestroyRef, OnInit, computed, inject, input, numberAttribute, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { ApiError, toApiError } from '../../../core/http/api-error';
import { ExecutionDetail, ExecutionStatus } from '../../../core/models/execution.model';
import { ExecutionApiService } from '../../../core/services/execution-api.service';
import { ErrorState } from '../../../shared/ui/error-state/error-state';
import { LoadingState } from '../../../shared/ui/loading-state/loading-state';
import { StatusBadge } from '../../../shared/ui/status-badge/status-badge';

// Phrase annoncée aux lecteurs d'écran à chaque changement de statut.
const STATUS_ANNOUNCEMENTS: Record<ExecutionStatus, string> = {
  QUEUED: 'Demande en attente de traitement.',
  RUNNING: 'Déploiement en cours.',
  SUCCEEDED: 'Déploiement réussi.',
  FAILED: 'Déploiement échoué.',
};

@Component({
  selector: 'app-execution-detail-page',
  imports: [DatePipe, RouterLink, StatusBadge, LoadingState, ErrorState],
  templateUrl: './execution-detail-page.html',
  styleUrl: './execution-detail-page.scss',
})
export class ExecutionDetailPage implements OnInit {
  private readonly executionApi = inject(ExecutionApiService);
  private readonly destroyRef = inject(DestroyRef);
  private subscription?: Subscription;

  /** Paramètre de route :id, transmis grâce à withComponentInputBinding. */
  readonly id = input.required({ transform: numberAttribute });

  protected readonly execution = signal<ExecutionDetail | null>(null);
  protected readonly error = signal<ApiError | null>(null);

  protected readonly loading = computed(() => this.execution() === null && this.error() === null);
  protected readonly announcement = computed(() => {
    const execution = this.execution();
    return execution ? STATUS_ANNOUNCEMENTS[execution.status] : '';
  });
  protected readonly durationSeconds = computed(() => {
    const execution = this.execution();
    if (!execution?.started_at || !execution.completed_at) {
      return null;
    }
    const milliseconds = Date.parse(execution.completed_at) - Date.parse(execution.started_at);
    return Math.round(milliseconds / 1000);
  });

  ngOnInit(): void {
    this.watch();
  }

  /** Démarre (ou relance après une erreur) le suivi de l'exécution. */
  protected watch(): void {
    this.error.set(null);
    this.subscription?.unsubscribe();
    // Le polling s'arrête seul quand l'exécution est terminée, ou quand on quitte la page.
    this.subscription = this.executionApi
      .watchExecution(this.id())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (execution) => this.execution.set(execution),
        error: (error: unknown) => this.error.set(toApiError(error)),
      });
  }
}
