import { Component, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProfileService } from '../../core/services/profile.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './onboarding.component.html',
  styleUrl: './onboarding.component.css'
})

export class OnboardingComponent {
  step = 1;
  viewMode = false;
  resumeFile: File | null = null;
  profile = {
    name: '',
    phone_number: '',
    desired_roles: '',
    desired_locations: '',
    desired_salary_min: null,
    desired_salary_max: null,
    remote_preference: 'REMOTE',
    seniority_preference: '',
    company_size_prefs: '',
    disallowed_categories: ''
  };

  // Backup for cancel
  private originalProfile: any = null;

  constructor(
    private profileService: ProfileService,
    private router: Router,
    public authService: AuthService
  ) {
    // Effect to fill profile if user loads
    effect(() => {
      const user = this.authService.currentUser();
      if (user && user.profile) {
        this.step = 2; // Skip to profile step if logged in
        this.viewMode = true;

        // Patch values (handling potentially missing fields)
        const p: any = user.profile;
        this.profile = {
          name: p.name || '',
          phone_number: p.phone_number || '',
          desired_roles: (p.desired_roles || []).join(', ') || '',
          desired_locations: (p.desired_locations || []).join(', ') || '',
          desired_salary_min: p.desired_salary_min || null,
          desired_salary_max: p.desired_salary_max || null,
          remote_preference: p.remote_preference || 'REMOTE',
          seniority_preference: p.seniority_preference || '',
          company_size_prefs: (p.company_size_prefs || []).join(', ') || '',
          disallowed_categories: (p.disallowed_categories || []).join(', ') || ''
        };
        this.originalProfile = { ...this.profile };
      }
    });
  }

  onFileSelected(event: any) {
    this.resumeFile = event.target.files[0];
  }

  uploadResume() {
    if (this.resumeFile) {
      this.profileService.uploadResume(this.resumeFile).subscribe({
        next: (res) => {
          console.log('Resume uploaded', res);
          // If we have extracted text data, we could potentially auto-fill profile here
          this.step = 2;
          this.viewMode = false; // Go to edit mode to verify/fill details
        },
        error: (err) => console.error('Upload failed', err)
      });
    }
  }

  submitProfile() {
    const profileData = {
      ...this.profile,
      desired_roles: this.profile.desired_roles.split(',').map(s => s.trim()).filter(s => s),
      desired_locations: this.profile.desired_locations.split(',').map(s => s.trim()).filter(s => s),
      company_size_prefs: this.profile.company_size_prefs.split(',').map(s => s.trim()).filter(s => s),
      disallowed_categories: this.profile.disallowed_categories.split(',').map(s => s.trim()).filter(s => s),
    };

    this.profileService.updateProfile(profileData).subscribe({
      next: (res) => {
        console.log('Profile updated', res);
        this.viewMode = true;
        this.originalProfile = { ...this.profile };
        // Determine if we should redirect or stay. 
        // If it was initial setup, maybe redirect. 
        // But for "Profile" page usage, stay.
        // We'll stay on page if it's an update, redirect if it was step 1->2 flow? 
        // Actually, let's just stay in view mode now. User can navigate away.
      },
      error: (err) => console.error('Update failed', err)
    });
  }

  toggleEdit() {
    this.viewMode = false;
  }

  cancelEdit() {
    this.profile = { ...this.originalProfile };
    this.viewMode = true;
  }

  downloadResume() {
    this.profileService.downloadResume().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume.pdf'; // Or detect type
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => console.error('Download failed', err)
    });
  }
}
