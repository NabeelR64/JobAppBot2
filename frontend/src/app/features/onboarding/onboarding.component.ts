import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProfileService } from '../../core/services/profile.service';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './onboarding.component.html',
  styleUrl: './onboarding.component.css'
})
export class OnboardingComponent {
  step = 1;
  resumeFile: File | null = null;
  profile = {
    name: '',
    desired_roles: '',
    desired_locations: '',
    desired_salary_min: null,
    desired_salary_max: null,
    remote_preference: 'REMOTE'
  };

  constructor(private profileService: ProfileService, private router: Router) { }

  onFileSelected(event: any) {
    this.resumeFile = event.target.files[0];
  }

  uploadResume() {
    if (this.resumeFile) {
      this.profileService.uploadResume(this.resumeFile).subscribe({
        next: (res) => {
          console.log('Resume uploaded', res);
          this.step = 2;
        },
        error: (err) => console.error('Upload failed', err)
      });
    }
  }

  submitProfile() {
    const profileData = {
      ...this.profile,
      desired_roles: this.profile.desired_roles.split(',').map(s => s.trim()),
      desired_locations: this.profile.desired_locations.split(',').map(s => s.trim())
    };

    this.profileService.updateProfile(profileData).subscribe({
      next: (res) => {
        console.log('Profile updated', res);
        this.router.navigate(['/swipe']);
      },
      error: (err) => console.error('Update failed', err)
    });
  }
}
