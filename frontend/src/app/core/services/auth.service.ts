import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = 'http://localhost:8000/api/v1/auth';

    constructor(private http: HttpClient) { }

    loginWithGoogle(credential: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/login/google`, { credential });
    }

    // Mock login for MVP UI testing
    mockLogin(): Observable<any> {
        return of({ access_token: 'fake-token', token_type: 'bearer' });
    }
}
