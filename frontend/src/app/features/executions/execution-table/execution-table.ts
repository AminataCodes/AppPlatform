import { DatePipe } from '@angular/common';
import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

import { Execution } from '../../../core/models/execution.model';
import { StatusBadge } from '../../../shared/ui/status-badge/status-badge';

/** Tableau d'exécutions, réutilisé par l'historique, le tableau de bord et le détail d'application. */
@Component({
  selector: 'app-execution-table',
  imports: [DatePipe, RouterLink, StatusBadge],
  templateUrl: './execution-table.html',
})
export class ExecutionTable {
  readonly executions = input.required<Execution[]>();
  readonly caption = input('Exécutions');
}
