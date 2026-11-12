import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';

import { Application } from '../../../core/models/application.model';
import { DeploymentFormPage } from './deployment-form-page';

const CUSTOMER_API: Application = {
  id: 1,
  name: 'customer-api',
  description: 'API de gestion des données clients.',
  owner_team: 'Équipe Clients',
  environments: [
    { id: 1, name: 'DEV', deployed_version: '1.3.0' },
    { id: 2, name: 'STAGING', deployed_version: '1.2.0' },
    { id: 3, name: 'PROD', deployed_version: '1.1.0' },
  ],
  available_versions: ['1.0.0', '1.1.0', '1.2.0', '1.3.0', '1.4.0'],
};

describe('DeploymentFormPage', () => {
  let fixture: ComponentFixture<DeploymentFormPage>;
  let httpMock: HttpTestingController;
  let page: HTMLElement;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      imports: [DeploymentFormPage],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    httpMock = TestBed.inject(HttpTestingController);

    fixture = TestBed.createComponent(DeploymentFormPage);
    fixture.componentRef.setInput('id', 1);
    fixture.detectChanges();
    httpMock.expectOne('/api/applications/1').flush(CUSTOMER_API);
    httpMock.expectOne('/api/executions').flush([]);
    await fixture.whenStable();
    page = fixture.nativeElement as HTMLElement;
  });

  afterEach(() => httpMock.verify());

  async function choose(environmentName: string, version: string): Promise<void> {
    // Avec formControlName, la valeur d'un radio est gérée par Angular, pas par l'attribut DOM :
    // on le retrouve par sa position (même ordre que les environnements).
    const radios = page.querySelectorAll<HTMLInputElement>('input[type="radio"]');
    const index = CUSTOMER_API.environments.findIndex((env) => env.name === environmentName);
    radios[index].click();
    const select = page.querySelector<HTMLSelectElement>('select#version')!;
    select.value = version;
    select.dispatchEvent(new Event('change'));
    await fixture.whenStable();
  }

  async function clickSubmit(): Promise<void> {
    page.querySelector<HTMLButtonElement>('button[type="submit"]')!.click();
    await fixture.whenStable();
  }

  function stepTitle(): string {
    return page.querySelector('h2.form__title')!.textContent!.trim();
  }

  it('shows field errors and stays on the first step when nothing is selected', async () => {
    await clickSubmit();

    expect(stepTitle()).toBe('Environnement et version');
    expect(page.textContent).toContain('Choisissez un environnement.');
    expect(page.textContent).toContain('Choisissez une version.');
    expect(page.querySelector('select#version')!.getAttribute('aria-invalid')).toBe('true');
  });

  it('requires an explicit confirmation before deploying to PROD', async () => {
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
    await choose('PROD', '1.2.0');
    await clickSubmit();

    expect(stepTitle()).toBe('Vérifiez votre demande');
    const confirmButton = page.querySelector<HTMLButtonElement>('button[type="submit"]')!;
    expect(confirmButton.textContent).toContain('Confirmer le déploiement en PROD');
    expect(confirmButton.disabled).toBe(true);

    page.querySelector<HTMLInputElement>('input[type="checkbox"]')!.click();
    await fixture.whenStable();
    expect(confirmButton.disabled).toBe(false);

    await clickSubmit();
    const call = httpMock.expectOne('/api/deployments');
    expect(call.request.body).toEqual({
      application_id: 1,
      environment_id: 3,
      requested_version: '1.2.0',
      confirm_production: true,
    });
    call.flush({ id: 7 });
    expect(navigate).toHaveBeenCalledWith(['/executions', 7]);
  });

  it('does not ask for a confirmation outside PROD and warns about a redeployment', async () => {
    await choose('DEV', '1.3.0');
    expect(page.textContent).toContain('est déjà déployée en DEV');

    await clickSubmit();

    expect(page.querySelector('input[type="checkbox"]')).toBeNull();
    expect(page.querySelector<HTMLButtonElement>('button[type="submit"]')!.disabled).toBe(false);
  });

  it('displays the reason when the API rejects the request', async () => {
    await choose('STAGING', '1.4.0');
    await clickSubmit();
    await clickSubmit();

    httpMock
      .expectOne('/api/deployments')
      .flush(
        { detail: 'Un déploiement est déjà en cours sur customer-api STAGING (exécution 4).' },
        { status: 409, statusText: 'Conflict' },
      );
    await fixture.whenStable();

    const alert = page.querySelector('[role="alert"]')!;
    expect(alert.textContent).toContain('La demande a été refusée.');
    expect(alert.textContent).toContain('Un déploiement est déjà en cours sur customer-api STAGING');
    expect(page.querySelector<HTMLButtonElement>('button[type="submit"]')!.disabled).toBe(false);
  });
});
