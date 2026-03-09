import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class JobService {
    private apiUrl = `${environment.apiUrl}/jobs`;

    constructor(private http: HttpClient) { }

    getRecommendations(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/recommendations`);
    }

    swipeJob(jobId: number, direction: 'LEFT' | 'RIGHT'): Observable<any> {
        return this.http.post(`${this.apiUrl}/${jobId}/swipe`, { job_posting_id: jobId, direction });
    }
}
