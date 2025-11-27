import { Routes } from '@angular/router';
import { LandingComponent } from './features/landing/landing.component';
import { OnboardingComponent } from './features/onboarding/onboarding.component';
import { SwipeComponent } from './features/swipe/swipe.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';

export const routes: Routes = [
    { path: '', component: LandingComponent },
    { path: 'onboarding', component: OnboardingComponent },
    { path: 'swipe', component: SwipeComponent },
    { path: 'dashboard', component: DashboardComponent },
    { path: '**', redirectTo: '' }
];
