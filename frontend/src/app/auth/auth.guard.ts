import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    if (authService.isAuthenticated()) {
        const user = authService.currentUser();
        console.log('AuthGuard Check:', { url: state.url, user, profile: user?.profile, phone: user?.profile?.phone_number });

        // If user is logged in but has no phone number, force onboarding
        // unless we are already ON the onboarding page
        if (state.url !== '/onboarding' && (!user?.profile?.phone_number)) {
            console.log('AuthGuard: Redirecting to onboarding due to missing phone');
            return router.parseUrl('/onboarding');
        }
        return true;
    }

    // Optional: Redirect to login
    return router.parseUrl('/login');
};
