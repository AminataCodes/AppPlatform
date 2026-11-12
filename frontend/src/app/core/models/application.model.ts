// Types identiques aux réponses JSON de l'API (mêmes noms de champs).

export type EnvironmentName = 'DEV' | 'STAGING' | 'PROD';

export interface Environment {
  id: number;
  name: EnvironmentName;
  deployed_version: string;
}

export interface Application {
  id: number;
  name: string;
  description: string;
  owner_team: string;
  environments: Environment[];
  available_versions: string[];
}
