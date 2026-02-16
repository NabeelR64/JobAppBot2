import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CdkDragDrop, DragDropModule, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { ApplicationService } from '../../core/services/application.service';
import { ProfileService } from '../../core/services/profile.service';
import { AuthService } from '../../core/services/auth.service';
import { ApplicationCardComponent } from './application-card/application-card.component';

interface KanbanColumn {
  id: string;
  title: string;
  icon: string;
  statuses: string[];
  applications: any[];
  color: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule, ApplicationCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  allApplications: any[] = [];
  columns: KanbanColumn[] = [];
  searchQuery: string = '';
  sortMode: 'date' | 'alpha' = 'date';
  loading: boolean = true;

  private columnDefs: Omit<KanbanColumn, 'applications'>[] = [
    { id: 'pending', title: 'Pending', icon: '🔄', statuses: ['PENDING_AUTOMATION'], color: '#f59e0b' },
    { id: 'needs_input', title: 'Needs Input', icon: '✍️', statuses: ['USER_INPUT_NEEDED'], color: '#f97316' },
    { id: 'applied', title: 'Applied', icon: '✅', statuses: ['APPLIED', 'EMAIL_CONFIRMATION_RECEIVED'], color: '#3b82f6' },
    { id: 'interview', title: 'Interview', icon: '💬', statuses: ['INTERVIEW_INVITED', 'FOLLOW_UP_RECEIVED'], color: '#8b5cf6' },
    { id: 'offer', title: 'Offer / Other', icon: '🎉', statuses: ['OTHER_UPDATE'], color: '#10b981' },
    { id: 'rejected', title: 'Rejected', icon: '❌', statuses: ['REJECTED', 'FAILED', 'MANUAL_INTERVENTION_REQUIRED'], color: '#ef4444' },
  ];

  constructor(
    private applicationService: ApplicationService,
    private profileService: ProfileService,
    private authService: AuthService
  ) { }

  ngOnInit() {
    this.loadApplications();
  }

  loadApplications() {
    this.loading = true;
    this.applicationService.getApplications().subscribe({
      next: (apps) => {
        this.allApplications = apps;
        this.distributeToColumns();
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load applications', err);
        this.loading = false;
      }
    });
  }

  distributeToColumns() {
    let filtered = this.allApplications;

    // Apply search filter
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(app =>
        app.job_posting.company_name.toLowerCase().includes(query) ||
        app.job_posting.title.toLowerCase().includes(query)
      );
    }

    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
      if (this.sortMode === 'date') {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      } else {
        return a.job_posting.company_name.localeCompare(b.job_posting.company_name);
      }
    });

    // Distribute into columns
    this.columns = this.columnDefs.map(def => ({
      ...def,
      applications: filtered.filter(app => def.statuses.includes(app.status))
    }));
  }

  get connectedDropLists(): string[] {
    return this.columns.map(col => col.id);
  }

  get totalApplications(): number {
    return this.allApplications.length;
  }

  onDrop(event: CdkDragDrop<any[]>, targetColumn: KanbanColumn) {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      const app = event.previousContainer.data[event.previousIndex];
      const newStatus = targetColumn.statuses[0]; // Use the first status of the target column

      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );

      // Update in backend
      this.applicationService.updateStatus(app.id, newStatus).subscribe({
        next: (updated) => {
          app.status = updated.status;
        },
        error: (err) => {
          console.error('Failed to update status', err);
          // Revert on failure
          this.distributeToColumns();
        }
      });
    }
  }

  onCardStatusChanged(event: { applicationId: number, status: string }) {
    this.applicationService.updateStatus(event.applicationId, event.status).subscribe({
      next: (updated) => {
        const app = this.allApplications.find(a => a.id === event.applicationId);
        if (app) {
          app.status = updated.status;
        }
        this.distributeToColumns();
      },
      error: (err) => {
        console.error('Failed to update status', err);
      }
    });
  }

  onSearchChange() {
    this.distributeToColumns();
  }

  toggleSort() {
    this.sortMode = this.sortMode === 'date' ? 'alpha' : 'date';
    this.distributeToColumns();
  }

  deleteAccount() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone and will remove all your data including applications and profile.')) {
      this.profileService.deleteAccount().subscribe({
        next: () => {
          alert('Account deleted successfully.');
          this.authService.logout();
        },
        error: (err) => {
          console.error('Delete failed', err);
          alert('Failed to delete account. Please try again.');
        }
      });
    }
  }
}
