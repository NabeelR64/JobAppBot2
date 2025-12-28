import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, switchMap, of, catchError } from 'rxjs';

export interface User {
    id: number;
    email: string;
    profile?: {
        name?: string;
    };
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = 'http://localhost:8000/api/v1/auth';
    private _accessToken: string | null = null;

    // Signal for reactive state
    currentUser = signal<User | null>(null);
    isAuthenticated = computed(() => !!this.currentUser());

    constructor(private http: HttpClient) { }

    get accessToken(): string | null {
        return this._accessToken;
    }

    loginWithGoogle(credential: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/google`, { credential }).pipe(
            tap((response: any) => {
                this.handleAuthResponse(response);
            }),
            switchMap(() => this.fetchCurrentUser())
        );
    }

    // loginStub removed as per requirements

    logout(): void {
        this._accessToken = null;
        this.currentUser.set(null);
    }


    private handleAuthResponse(response: any): void {
        this._accessToken = response.access_token;
    }

    private fetchCurrentUser(): Observable<User> {
        // We need manually add auth header here since we don't have an interceptor setup yet
        // or we can rely on interceptor if it exists. 
        // Assuming we need to implement/use interceptor or pass header explicitly.
        // For now, let's assume we'll pass it in the options or fix interceptor.
        // Actually, best practice is to have an interceptor. 
        // Let's check if interceptor exists.
        return this.http.get<User>('http://localhost:8000/api/v1/users/me', {
            headers: { Authorization: `Bearer ${this._accessToken}` }
        }).pipe(
            tap(user => this.currentUser.set(user))
        );
    }
}
