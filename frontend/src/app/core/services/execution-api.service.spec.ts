import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ExecutionDetail, ExecutionStatus } from '../models/execution.model';
import { ExecutionApiService, POLLING_INTERVAL_MS } from './execution-api.service';

function executionDetail(status: ExecutionStatus): ExecutionDetail {
  return {
    id: 7,
    application: { id: 1, name: 'customer-api' },
    environment: { id: 1, name: 'DEV' },
    requested_version: '1.2.0',
    status,
    created_at: '2026-11-10T15:00:00Z',
    started_at: null,
    completed_at: null,
    logs: [],
  };
}

describe('ExecutionApiService', () => {
  let service: ExecutionApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(ExecutionApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    vi.useRealTimers();
    httpMock.verify();
  });

  it('sends the deployment request to POST /api/deployments', () => {
    const request = { application_id: 1, environment_id: 3, requested_version: '1.2.0', confirm_production: true };

    service.requestDeployment(request).subscribe();

    const call = httpMock.expectOne('/api/deployments');
    expect(call.request.method).toBe('POST');
    expect(call.request.body).toEqual(request);
    call.flush(executionDetail('QUEUED'));
  });

  it('polls the execution every second and stops once it is finished', () => {
    vi.useFakeTimers();
    const statuses: ExecutionStatus[] = [];
    let completed = false;

    service.watchExecution(7).subscribe({
      next: (execution) => statuses.push(execution.status),
      complete: () => (completed = true),
    });

    vi.advanceTimersByTime(0);
    httpMock.expectOne('/api/executions/7').flush(executionDetail('QUEUED'));
    vi.advanceTimersByTime(POLLING_INTERVAL_MS);
    httpMock.expectOne('/api/executions/7').flush(executionDetail('RUNNING'));
    vi.advanceTimersByTime(POLLING_INTERVAL_MS);
    httpMock.expectOne('/api/executions/7').flush(executionDetail('SUCCEEDED'));

    expect(statuses).toEqual(['QUEUED', 'RUNNING', 'SUCCEEDED']);
    expect(completed).toBe(true);

    // Plus aucune requête après l'état final.
    vi.advanceTimersByTime(POLLING_INTERVAL_MS * 3);
    httpMock.expectNone('/api/executions/7');
  });
});
