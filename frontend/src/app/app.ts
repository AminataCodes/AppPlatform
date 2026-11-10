import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { Header } from './core/layout/header/header';
import { MainNav } from './core/layout/main-nav/main-nav';

// Composant racine : la coquille commune à toutes les pages
// (en-tête, navigation et zone de contenu où s'affiche la page active).
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, MainNav],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {}
