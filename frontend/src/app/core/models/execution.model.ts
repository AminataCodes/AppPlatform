import { EnvironmentName } from './application.model';

export type ExecutionStatus = 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'FAILED';

export type LogLevel = 'INFO' | 'WARNING' | 'ERROR';

export interface ApplicationRef {
  id: number;
  name: string;
}

export interface EnvironmentRef {
  id: number;
  name: EnvironmentName;
}

export interface Execution {
  id: number;
  application: ApplicationRef;
  environment: EnvironmentRef;
  requested_version: string;
  status: ExecutionStatus;
  // Dates ISO 8601 en UTC (suffixe « Z »), affichées en heure locale par le DatePipe.
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface ExecutionLog {
  id: number;
  timestamp: string;
  level: LogLevel;
  message: string;
}

export interface ExecutionDetail extends Execution {
  logs: ExecutionLog[];
}

// Corps de POST /api/deployments.
export interface DeploymentRequest {
  application_id: number;
  environment_id: number;
  requested_version: string;
  confirm_production: boolean;
}

/** Une exécution terminée ne change plus : SUCCEEDED ou FAILED. */
export function isFinished(status: ExecutionStatus): boolean {
  return status === 'SUCCEEDED' || status === 'FAILED';
}
