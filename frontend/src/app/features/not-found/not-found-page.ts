import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PageHeader } from '../../shared/ui/page-header/page-header';

// Affichée pour toute URL qui ne correspond à aucune route.
@Component({
  selector: 'app-not-found-page',
  imports: [PageHeader, RouterLink],
  template: `
    <app-page-header
      heading="Page introuvable"
      description="L'adresse demandée ne correspond à aucune page du portail."
    />
    <a routerLink="/">Retour à l'accueil</a>
  `
})
export class NotFoundPage {}
