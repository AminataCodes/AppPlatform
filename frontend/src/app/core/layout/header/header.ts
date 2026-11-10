import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

// En-tête global : identité du portail et rappel que les déploiements sont simulés.
@Component({
  selector: 'app-header',
  imports: [RouterLink],
  templateUrl: './header.html',
  styleUrl: './header.scss'
})
export class Header {}
