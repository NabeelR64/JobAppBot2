import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApplicationService } from '../../core/services/application.service';
import { ProfileService } from '../../core/services/profile.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  applications: any[] = [];

  constructor(
    private applicationService: ApplicationService,
    private profileService: ProfileService,
    private authService: AuthService
  ) { }

  ngOnInit() {
    this.loadApplications();
  }

  loadApplications() {
    this.applicationService.getApplications().subscribe({
      next: (apps) => {
        this.applications = apps;
      },
      error: (err) => console.error('Failed to load applications', err)
    });
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
