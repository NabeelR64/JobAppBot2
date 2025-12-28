import { Injectable, NgZone } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { authConfig } from './auth.config';
import { Router } from '@angular/router';

declare global {
    interface Window {
        google: any;
    }
}

interface User {
    id: number;
    email: string;
    name?: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = 'http://localhost:8000/api/v1'; // Adjust if needed
    private tokenKey = 'jinder_auth_token'; // In-memory logic preferred, but for service state we often hold it here. 
    // Requirement: "Auth state persists only in-memory for the current browser session". 
    // So we won't use localStorage for persistence across tabs/closes, BUT we need to store it in the service instance.

    private token: string | null = null;
    private currentUserSubject = new BehaviorSubject<User | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();

    constructor(
        private http: HttpClient,
        private router: Router,
        private ngZone: NgZone
    ) { }

    initializeGoogleSignIn() {
        if (window.google) {
            window.google.accounts.id.initialize({
                client_id: authConfig.googleClientId,
                callback: (response: any) => this.handleGoogleCredential(response),
                // TODO: Future Gmail Scopes
                // To request Gmail access (gmail.readonly), we will need to use the
                // google.accounts.oauth2.initCodeClient() model instead of the current
                // Sign-In with Google (GIS) ID token flow, or request additional scopes incrementally.
                // const client = google.accounts.oauth2.initCodeClient({...});
            });
        }
    }

    renderButton(element: HTMLElement) {
        if (window.google) {
            window.google.accounts.id.renderButton(element, {
                theme: 'outline',
                size: 'large',
                type: 'standard'
            });
        }
    }

    private handleGoogleCredential(response: any) {
        console.log('Google response', response);
        this.verifyGoogleToken(response.credential).subscribe({
            next: (res: any) => {
                console.log('Backend auth success', res);
                this.setSession(res.access_token);
                this.fetchMe();
            },
            error: (err) => console.error('Backend auth failed', err)
        });
    }

    verifyGoogleToken(credential: string) {
        return this.http.post(`${this.apiUrl}/auth/google`, { credential });
    }

    private setSession(token: string) {
        this.token = token;
        // For now, simple in-memory. If we needed session persistence within tab refresh we might use sessionStorage,
        // but requirements say "Auth state persists only in-memory... no cookies yet". 
        // Wait, if I refresh, JS state is lost. If I want to persist "for the current browser session", sessionStorage IS appropriate.
        // "Auth state persists only in-memory for the current browser session (no cookies yet)" usually implies sessionStorage or just variable.
        // If I refresh and it logs out, that's strictly "in-memory (JS heap)". If I want it to survive refresh, I need sessionStorage.
        // User said: "Auth state persists only in-memory for the current browser session". 
        // Usually "current browser session" implies sessionStorage. But "in-memory" implies NOT persistent storage.
        // I will use memory ONLY (JS variable). Refresh = Logout. This matches "persist only in-memory".

        // However, validation plan said "Refresh: Verify user is logged out". So definitely just JS variable.
    }

    fetchMe() {
        if (!this.token) return;
        this.http.get<User>(`${this.apiUrl}/auth/me`, {
            headers: { Authorization: `Bearer ${this.token}` }
        }).subscribe({
            next: (user) => {
                this.currentUserSubject.next(user);
                this.ngZone.run(() => this.router.navigate(['/']));
            },
            error: () => this.logout()
        });
    }

    getToken() {
        return this.token;
    }

    isAuthenticated(): boolean {
        return !!this.token;
    }

    logout() {
        this.token = null;
        this.currentUserSubject.next(null);
        this.router.navigate(['/login']);
    }
}
