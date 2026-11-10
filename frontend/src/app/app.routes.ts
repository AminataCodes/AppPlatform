import { Routes } from '@angular/router';

// Chaque page est chargée à la demande (loadComponent) : le navigateur
// ne télécharge le code d'une page que lorsqu'on la visite.
export const routes: Routes = [
  {
    path: '',
    title: 'Accueil · AppPlatform',
    loadComponent: () => import('./features/home/home-page').then((m) => m.HomePage)
  },
  // Sections prévues pour la phase 3 : page d'attente temporaire.
  {
    path: 'applications',
    title: 'Applications · AppPlatform',
    data: { heading: 'Applications' },
    loadComponent: () =>
      import('./features/coming-soon/coming-soon-page').then((m) => m.ComingSoonPage)
  },
  {
    path: 'executions',
    title: 'Historique · AppPlatform',
    data: { heading: 'Historique des exécutions' },
    loadComponent: () =>
      import('./features/coming-soon/coming-soon-page').then((m) => m.ComingSoonPage)
  },
  {
    path: '**',
    title: 'Page introuvable · AppPlatform',
    loadComponent: () => import('./features/not-found/not-found-page').then((m) => m.NotFoundPage)
  }
];
