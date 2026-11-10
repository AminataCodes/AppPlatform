import { Component, input } from '@angular/core';

// Titre de page réutilisable : un seul <h1> par page, suivi d'une description facultative.
@Component({
  selector: 'app-page-header',
  templateUrl: './page-header.html',
  styleUrl: './page-header.scss'
})
export class PageHeader {
  readonly heading = input.required<string>();
  readonly description = input<string>();
}
