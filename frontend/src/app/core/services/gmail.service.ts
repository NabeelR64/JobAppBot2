import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class GmailService {
    private apiUrl = 'http://localhost:8000/api/v1/gmail';

    constructor(private http: HttpClient) { }

    /**
     * Get the OAuth authorization URL to connect Gmail.
     * Frontend should open this URL in a new window/tab.
     */
    connect(): Observable<{ auth_url: string }> {
        return this.http.get<{ auth_url: string }>(`${this.apiUrl}/connect`);
    }

    /**
     * Check if the user's Gmail is connected.
     */
    getStatus(): Observable<{ connected: boolean; connected_at: string | null }> {
        return this.http.get<{ connected: boolean; connected_at: string | null }>(`${this.apiUrl}/status`);
    }

    /**
     * Disconnect Gmail — clears stored refresh token.
     */
    disconnect(): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/disconnect`, {});
    }

    /**
     * Manually trigger Gmail polling for the current user.
     */
    poll(): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/poll`, {});
    }
}
