import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApplicationService } from '../../core/services/application.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  applications: any[] = [];

  constructor(private applicationService: ApplicationService) { }

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
}
