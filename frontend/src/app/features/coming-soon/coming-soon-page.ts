import { Component, input } from '@angular/core';

import { PageHeader } from '../../shared/ui/page-header/page-header';

// Page d'attente temporaire pour les sections prévues en phase 3.
// `heading` est rempli automatiquement depuis `data` de la route.
@Component({
  selector: 'app-coming-soon-page',
  imports: [PageHeader],
  template: `
    <app-page-header
      [heading]="heading()"
      description="Cette section sera disponible dans une prochaine étape du projet."
    />
  `
})
export class ComingSoonPage {
  readonly heading = input.required<string>();
}
