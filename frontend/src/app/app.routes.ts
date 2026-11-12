import { Routes } from '@angular/router';

// Chaque page est chargée à la demande (loadComponent) : le navigateur
// ne télécharge le code d'une page que lorsqu'on la visite.
// Les paramètres (:id) sont transmis aux inputs des pages (withComponentInputBinding).
export const routes: Routes = [
  {
    path: '',
    title: 'Tableau de bord · AppPlatform',
    loadComponent: () => import('./features/dashboard/dashboard-page').then((m) => m.DashboardPage),
  },
  {
    path: 'applications',
    title: 'Applications · AppPlatform',
    loadComponent: () =>
      import('./features/applications/application-list/application-list-page').then((m) => m.ApplicationListPage),
  },
  {
    path: 'applications/:id',
    title: "Détail de l'application · AppPlatform",
    loadComponent: () =>
      import('./features/applications/application-detail/application-detail-page').then(
        (m) => m.ApplicationDetailPage,
      ),
  },
  {
    path: 'applications/:id/deploy',
    title: 'Demande de déploiement · AppPlatform',
    loadComponent: () =>
      import('./features/deployments/deployment-form/deployment-form-page').then((m) => m.DeploymentFormPage),
  },
  {
    path: 'executions',
    title: 'Historique · AppPlatform',
    loadComponent: () =>
      import('./features/executions/execution-list/execution-list-page').then((m) => m.ExecutionListPage),
  },
  {
    path: 'executions/:id',
    title: "Suivi d'exécution · AppPlatform",
    loadComponent: () =>
      import('./features/executions/execution-detail/execution-detail-page').then((m) => m.ExecutionDetailPage),
  },
  {
    path: '**',
    title: 'Page introuvable · AppPlatform',
    loadComponent: () => import('./features/not-found/not-found-page').then((m) => m.NotFoundPage),
  },
];
