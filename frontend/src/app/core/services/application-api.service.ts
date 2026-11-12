import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { Application } from '../models/application.model';

// Seul endroit qui connaît les URL du catalogue. Les composants appellent ces méthodes.
@Injectable({ providedIn: 'root' })
export class ApplicationApiService {
  private readonly http = inject(HttpClient);

  getApplications(): Observable<Application[]> {
    return this.http.get<Application[]>('/api/applications');
  }

  getApplication(id: number): Observable<Application> {
    return this.http.get<Application>(`/api/applications/${id}`);
  }
}
