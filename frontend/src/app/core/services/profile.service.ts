import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class ProfileService {
    private apiUrl = environment.apiUrl;

    constructor(private http: HttpClient) { }

    uploadResume(file: File): Observable<any> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post(`${this.apiUrl}/resume/upload`, formData);
    }

    updateProfile(profileData: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/users/me/profile`, profileData);
    }

    deleteAccount(): Observable<any> {
        return this.http.delete(`${this.apiUrl}/users/me`);
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
