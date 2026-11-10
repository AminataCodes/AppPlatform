import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

interface NavItem {
  label: string;
  path: string;
  // Tracé SVG de l'icône (grille 24 × 24)
  icon: string;
  // true : le lien n'est actif que sur l'URL exacte (utile pour l'accueil « / »)
  exact: boolean;
}

// Navigation principale du portail.
@Component({
  selector: 'app-main-nav',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './main-nav.html',
  styleUrl: './main-nav.scss'
})
export class MainNav {
  protected readonly items: NavItem[] = [
    { label: 'Accueil', path: '/', icon: 'M3 10.5 12 3l9 7.5V21h-6v-6H9v6H3z', exact: true },
    {
      label: 'Applications',
      path: '/applications',
      icon: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
      exact: false
    },
    {
      label: 'Historique',
      path: '/executions',
      icon: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3 2',
      exact: false
    }
  ];
}
