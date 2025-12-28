import { Routes } from '@angular/router';
import { LandingComponent } from './features/landing/landing.component';
import { OnboardingComponent } from './features/onboarding/onboarding.component';
import { SwipeComponent } from './features/swipe/swipe.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { authGuard } from './auth/auth.guard';

export const routes: Routes = [
    { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    { path: 'login', loadComponent: () => import('./auth/login.component').then(m => m.LoginComponent) },
    {
        path: '',
        canActivate: [authGuard],
        children: [
            { path: 'landing', component: LandingComponent }, // Maybe public? But let's protect for now or leaving as is. Actually landing implies public.
            { path: 'onboarding', component: OnboardingComponent },
            { path: 'swipe', component: SwipeComponent },
            { path: 'dashboard', component: DashboardComponent },
        ]
    },
    { path: '**', redirectTo: 'dashboard' }
];
