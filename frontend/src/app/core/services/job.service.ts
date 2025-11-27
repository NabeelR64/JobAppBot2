import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class JobService {
    private apiUrl = 'http://localhost:8000/api/v1/jobs';

    constructor(private http: HttpClient) { }

    getRecommendations(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/recommendations`);
    }

    swipeJob(jobId: number, direction: 'LEFT' | 'RIGHT'): Observable<any> {
        return this.http.post(`${this.apiUrl}/${jobId}/swipe`, { job_posting_id: jobId, direction });
    }
}
