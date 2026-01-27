import { Injectable, signal, computed, NgZone, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, switchMap, of, catchError } from 'rxjs';
import { Router } from '@angular/router';
import { authConfig } from '../../auth/auth.config';

export interface User {
    id: number;
    email: string;
    profile?: {
        name?: string;
        phone_number?: string;
    };
}

declare global {
    interface Window {
        google: any;
    }
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = 'http://localhost:8000/api/v1/auth';
    private _accessToken: string | null = null;

    // Dependency Injection
    private http = inject(HttpClient);
    private ngZone = inject(NgZone);
    private router = inject(Router);

    // Signal for reactive state
    currentUser = signal<User | null>(null);
    isAuthenticated = computed(() => !!this.currentUser());

    constructor() { }

    get accessToken(): string | null {
        return this._accessToken;
    }

    initializeGoogleSignIn() {
        if (typeof window === 'undefined' || !window.google) return;

        window.google.accounts.id.initialize({
            client_id: authConfig.googleClientId,
            callback: (response: any) => this.handleGoogleCredential(response),
            auto_select: false,
            cancel_on_tap_outside: true
        });
    }

    renderGoogleButton(element: HTMLElement) {
        if (typeof window === 'undefined' || !window.google) return;

        window.google.accounts.id.renderButton(element, {
            theme: 'outline',
            size: 'large',
            type: 'standard'
        });
    }

    private handleGoogleCredential(response: any) {
        this.ngZone.run(() => {
            this.loginWithGoogle(response.credential).subscribe({
                next: (user) => {
                    console.log('Login Success. User:', user);
                    // Check if profile is complete (now defined as having a phone number)
                    if (!user.profile || !user.profile.name || !user.profile.phone_number) {
                        console.log('Login: Incomplete profile, going to onboarding');
                        this.router.navigate(['/onboarding']);
                    } else {
                        console.log('Login: Complete profile, going to dashboard');
                        this.router.navigate(['/dashboard']);
                    }
                },
                error: (err) => console.error('Login failed', err)
            });
        });
    }

    loginWithGoogle(credential: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/google`, { credential }).pipe(
            tap((response: any) => {
                this.handleAuthResponse(response);
            }),
            switchMap(() => this.fetchCurrentUser())
        );
    }

    logout(): void {
        this._accessToken = null;
        this.currentUser.set(null);
        this.router.navigate(['/login']);
    }

    private handleAuthResponse(response: any): void {
        this._accessToken = response.access_token;
    }

    private fetchCurrentUser(): Observable<User> {
        if (!this._accessToken) return of(null as any);

        return this.http.get<User>('http://localhost:8000/api/v1/users/me', {
            headers: { Authorization: `Bearer ${this._accessToken}` }
        }).pipe(
            tap(user => this.currentUser.set(user)),
            catchError(() => {
                this.logout();
                return of(null as any);
            })
        );
    }
}
