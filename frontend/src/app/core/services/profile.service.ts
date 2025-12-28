import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ProfileService {
    private apiUrl = 'http://localhost:8000/api/v1';

    constructor(private http: HttpClient) { }

    uploadResume(file: File): Observable<any> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post(`${this.apiUrl}/resume/upload`, formData);
    }

    updateProfile(profileData: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/users/me/profile`, profileData);
    }


    getProfile(): Observable<any> {
        return this.http.get(`${this.apiUrl}/users/me`);
    }

    downloadResume(): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/resume/download`, {
            responseType: 'blob'
        });
    }
}
