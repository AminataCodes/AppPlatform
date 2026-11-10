import { Component } from '@angular/core';

import { PageHeader } from '../../shared/ui/page-header/page-header';

// Page d'accueil temporaire : sera remplacée par le tableau de bord.
@Component({
  selector: 'app-home-page',
  imports: [PageHeader],
  templateUrl: './home-page.html',
  styleUrl: './home-page.scss'
})
export class HomePage {}
