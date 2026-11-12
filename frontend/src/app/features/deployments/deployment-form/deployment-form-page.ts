import {
  Component,
  DestroyRef,
  ElementRef,
  Injector,
  OnInit,
  afterNextRender,
  computed,
  inject,
  input,
  numberAttribute,
  signal,
  viewChild,
} from '@angular/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { ApiError, toApiError } from '../../../core/http/api-error';
import { Application } from '../../../core/models/application.model';
import { Execution, isFinished } from '../../../core/models/execution.model';
import { ApplicationApiService } from '../../../core/services/application-api.service';
import { ExecutionApiService } from '../../../core/services/execution-api.service';
import { ErrorState } from '../../../shared/ui/error-state/error-state';
import { LoadingState } from '../../../shared/ui/loading-state/loading-state';
import { PageHeader } from '../../../shared/ui/page-header/page-header';

type Step = 'edit' | 'review';

@Component({
  selector: 'app-deployment-form-page',
  imports: [ReactiveFormsModule, RouterLink, PageHeader, LoadingState, ErrorState],
  templateUrl: './deployment-form-page.html',
  styleUrl: './deployment-form-page.scss',
})
export class DeploymentFormPage implements OnInit {
  private readonly applicationApi = inject(ApplicationApiService);
  private readonly executionApi = inject(ExecutionApiService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly injector = inject(Injector);
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly stepHeading = viewChild<ElementRef<HTMLElement>>('stepHeading');

  readonly id = input.required({ transform: numberAttribute });

  protected readonly application = signal<Application | null>(null);
  /** Exécutions encore QUEUED ou RUNNING de cette application. */
  protected readonly activeExecutions = signal<Execution[]>([]);
  protected readonly loading = signal(true);
  protected readonly loadError = signal<ApiError | null>(null);

  protected readonly step = signal<Step>('edit');
  protected readonly submitAttempted = signal(false);
  protected readonly submitting = signal(false);
  protected readonly submitError = signal<ApiError | null>(null);

  protected readonly form = this.formBuilder.group({
    environmentId: this.formBuilder.control<number | null>(null, Validators.required),
    version: this.formBuilder.control('', Validators.required),
    confirmProduction: this.formBuilder.control(false),
  });

  // Les valeurs du formulaire sous forme de signal, pour les calculs ci-dessous.
  protected readonly formValue = toSignal(this.form.valueChanges, { initialValue: this.form.getRawValue() });

  protected readonly selectedEnvironment = computed(() =>
    this.application()?.environments.find((env) => env.id === this.formValue().environmentId),
  );
  protected readonly isProduction = computed(() => this.selectedEnvironment()?.name === 'PROD');
  /** La version choisie est déjà celle déployée : autorisé, mais on prévient. */
  protected readonly isRedeploy = computed(
    () => this.selectedEnvironment()?.deployed_version === this.formValue().version,
  );
  protected readonly activeExecution = computed(() =>
    this.activeExecutions().find((execution) => execution.environment.id === this.selectedEnvironment()?.id),
  );
  protected readonly canSubmit = computed(
    () =>
      !this.submitting() &&
      !this.activeExecution() &&
      (!this.isProduction() || this.formValue().confirmProduction === true),
  );

  ngOnInit(): void {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.loadError.set(null);
    forkJoin({
      application: this.applicationApi.getApplication(this.id()),
      executions: this.executionApi.getExecutions(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ application, executions }) => {
          this.application.set(application);
          this.activeExecutions.set(
            executions.filter(
              (execution) => execution.application.id === application.id && !isFinished(execution.status),
            ),
          );
          this.loading.set(false);
        },
        error: (error: unknown) => {
          this.loadError.set(toApiError(error));
          this.loading.set(false);
        },
      });
  }

  /** Affiche l'erreur d'un champ après une interaction ou une tentative de validation. */
  protected showError(field: 'environmentId' | 'version'): boolean {
    const control = this.form.controls[field];
    return control.invalid && (control.touched || this.submitAttempted());
  }

  protected onSubmit(): void {
    if (this.step() === 'edit') {
      this.goToReview();
    } else {
      this.submit();
    }
  }

  protected backToEdit(): void {
    this.form.controls.confirmProduction.setValue(false);
    this.submitError.set(null);
    this.step.set('edit');
    this.focusStepHeading();
  }

  private goToReview(): void {
    this.submitAttempted.set(true);
    if (this.form.invalid || this.activeExecution()) {
      this.form.markAllAsTouched();
      return;
    }
    this.step.set('review');
    this.focusStepHeading();
  }

  private submit(): void {
    const application = this.application();
    const environment = this.selectedEnvironment();
    if (!application || !environment || !this.canSubmit()) {
      return;
    }

    this.submitting.set(true);
    this.submitError.set(null);
    this.executionApi
      .requestDeployment({
        application_id: application.id,
        environment_id: environment.id,
        requested_version: this.form.controls.version.value,
        confirm_production: this.isProduction() && this.form.controls.confirmProduction.value,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        // 202 : la demande est acceptée, on suit l'exécution sur sa page.
        next: (execution) => this.router.navigate(['/executions', execution.id]),
        error: (error: unknown) => {
          this.submitError.set(toApiError(error));
          this.submitting.set(false);
        },
      });
  }

  /** Après un changement d'étape, le focus va au titre de l'étape (utile au clavier et aux lecteurs d'écran). */
  private focusStepHeading(): void {
    afterNextRender(() => this.stepHeading()?.nativeElement.focus(), { injector: this.injector });
  }
}
