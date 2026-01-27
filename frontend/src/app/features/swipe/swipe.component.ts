import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { JobService } from '../../core/services/job.service';

@Component({
  selector: 'app-swipe',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './swipe.component.html',
  styleUrl: './swipe.component.css'
})
export class SwipeComponent implements OnInit {
  jobs: any[] = [];
  currentJob: any = null;

  constructor(private jobService: JobService) { }

  ngOnInit() {
    this.loadJobs();
  }

  loadJobs() {
    this.jobService.getRecommendations().subscribe({
      next: (jobs) => {
        this.jobs = jobs;
        if (this.jobs.length > 0) {
          this.currentJob = this.jobs[0];
        } else {
          this.currentJob = null;
        }
      },
      error: (err) => console.error('Failed to load jobs', err)
    });
  }

  swipe(direction: 'LEFT' | 'RIGHT') {
    if (!this.currentJob) return;

    this.jobService.swipeJob(this.currentJob.id, direction).subscribe({
      next: () => {
        console.log(`Swiped ${direction}`);
        // Remove current job and show next
        this.jobs.shift();
        if (this.jobs.length > 0) {
          this.currentJob = this.jobs[0];
        } else {
          this.currentJob = null;
          // Try to load more
          this.loadJobs();
        }
      },
      error: (err) => console.error('Swipe failed', err)
    });
  }

  get truncatedDescription(): string {
    if (!this.currentJob?.description) return '';
    const desc = this.currentJob.description;
    return desc.length > 300 ? desc.substring(0, 300) + '...' : desc;
  }
}
