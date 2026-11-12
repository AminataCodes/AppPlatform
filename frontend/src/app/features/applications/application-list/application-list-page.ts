import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';

import { ApiError, toApiError } from '../../../core/http/api-error';
import { Application } from '../../../core/models/application.model';
import { ApplicationApiService } from '../../../core/services/application-api.service';
import { EmptyState } from '../../../shared/ui/empty-state/empty-state';
import { ErrorState } from '../../../shared/ui/error-state/error-state';
import { LoadingState } from '../../../shared/ui/loading-state/loading-state';
import { PageHeader } from '../../../shared/ui/page-header/page-header';

@Component({
  selector: 'app-application-list-page',
  imports: [RouterLink, PageHeader, LoadingState, ErrorState, EmptyState],
  templateUrl: './application-list-page.html',
  styleUrl: './application-list-page.scss',
})
export class ApplicationListPage {
  private readonly applicationApi = inject(ApplicationApiService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly applications = signal<Application[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal<ApiError | null>(null);

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.applicationApi
      .getApplications()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (applications) => {
          this.applications.set(applications);
          this.loading.set(false);
        },
        error: (error: unknown) => {
          this.error.set(toApiError(error));
          this.loading.set(false);
        },
      });
  }
}
