import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-application-card',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './application-card.component.html',
    styleUrl: './application-card.component.css'
})
export class ApplicationCardComponent {
    @Input() application: any;
    @Output() statusChanged = new EventEmitter<{ applicationId: number, status: string }>();

    get companyInitial(): string {
        return (this.application?.job_posting?.company_name || '?')[0].toUpperCase();
    }

    get avatarColor(): string {
        const colors = ['#4f46e5', '#0891b2', '#059669', '#d97706', '#dc2626', '#7c3aed', '#db2777', '#2563eb'];
        const name = this.application?.job_posting?.company_name || '';
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    }

    get statusLabel(): string {
        const labels: Record<string, string> = {
            'PENDING_AUTOMATION': 'Pending',
            'APPLIED': 'Applied',
            'EMAIL_CONFIRMATION_RECEIVED': 'Confirmed',
            'INTERVIEW_INVITED': 'Interview',
            'REJECTED': 'Rejected',
            'FOLLOW_UP_RECEIVED': 'Follow-Up',
            'OTHER_UPDATE': 'Other',
            'FAILED': 'Failed',
            'MANUAL_INTERVENTION_REQUIRED': 'Needs Action'
        };
        return labels[this.application?.status] || this.application?.status;
    }

    get statusClass(): string {
        return (this.application?.status || '').toLowerCase();
    }

    onStatusChange(event: Event) {
        const select = event.target as HTMLSelectElement;
        this.statusChanged.emit({
            applicationId: this.application.id,
            status: select.value
        });
    }
}
