import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, exhaustMap, takeWhile, timer } from 'rxjs';

import { DeploymentRequest, Execution, ExecutionDetail, isFinished } from '../models/execution.model';

export const POLLING_INTERVAL_MS = 1000;

@Injectable({ providedIn: 'root' })
export class ExecutionApiService {
  private readonly http = inject(HttpClient);

  getExecutions(): Observable<Execution[]> {
    return this.http.get<Execution[]>('/api/executions');
  }

  getExecution(id: number): Observable<ExecutionDetail> {
    return this.http.get<ExecutionDetail>(`/api/executions/${id}`);
  }

  /** Demande un déploiement : l'API répond 202 avec l'exécution au statut QUEUED. */
  requestDeployment(request: DeploymentRequest): Observable<Execution> {
    return this.http.post<Execution>('/api/deployments', request);
  }

  /**
   * Suit une exécution : relit son état toutes les secondes jusqu'à ce qu'elle soit terminée.
   *
   * - exhaustMap : pas de nouvelle requête tant que la précédente n'a pas répondu ;
   * - takeWhile(..., true) : l'état final est émis, puis le polling s'arrête.
   */
  watchExecution(id: number): Observable<ExecutionDetail> {
    return timer(0, POLLING_INTERVAL_MS).pipe(
      exhaustMap(() => this.getExecution(id)),
      takeWhile((execution) => !isFinished(execution.status), true),
    );
  }
}
