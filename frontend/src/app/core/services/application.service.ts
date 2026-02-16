import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ApplicationService {
    private apiUrl = 'http://localhost:8000/api/v1/applications';

    constructor(private http: HttpClient) { }

    getApplications(): Observable<any[]> {
        return this.http.get<any[]>(this.apiUrl);
    }

    updateStatus(applicationId: number, status: string): Observable<any> {
        return this.http.patch<any>(`${this.apiUrl}/${applicationId}/status`, { status });
    }

    provideFields(applicationId: number, fields: Record<string, string>): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/${applicationId}/provide-fields`, { fields });
    }
}
