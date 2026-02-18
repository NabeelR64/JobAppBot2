import { Component, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ProfileService } from '../../core/services/profile.service';
import { AuthService } from '../../core/services/auth.service';
import { GmailService } from '../../core/services/gmail.service';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './onboarding.component.html',
  styleUrl: './onboarding.component.css'
})

export class OnboardingComponent {
  step = 0; // Start at 0 for basic info
  viewMode = false;
  resumeFile: File | null = null;
  resumePreviewUrl: SafeResourceUrl | null = null;
  showResumePreview = false;
  gmailConnected = false;
  gmailConnecting = false;
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
    disallowed_categories: '',
    // New fields
    age: null,
    address: '',
    region: '',
    location: '',
    field_of_work: '',
    experience: [] as any[], // Array of { company, title, years, description }
    education: [] as any[]   // Array of { school, degree, years }
  };

  // Backup for cancel
  originalProfile: any = null;

  constructor(
    private profileService: ProfileService,
    private router: Router,
    private route: ActivatedRoute,
    public authService: AuthService,
    private sanitizer: DomSanitizer,
    private gmailService: GmailService
  ) {
    // Check for Gmail callback query param
    this.route.queryParams.subscribe(params => {
      if (params['gmail'] === 'connected') {
        this.gmailConnected = true;
        this.step = 2;
        this.viewMode = true;
      }
    });

    // Check Gmail connection status on load
    this.gmailService.getStatus().subscribe({
      next: (status) => { this.gmailConnected = status.connected; },
      error: () => { /* Not logged in yet, ignore */ }
    });

    // Effect to fill profile if user loads
    effect(() => {
      const user = this.authService.currentUser();
      if (user && user.profile) {
        // If we have a profile but no phone number, we treat it as incomplete -> Step 0
        // (The form will be pre-filled with what we have, e.g. name)
        if (user.profile.phone_number) {
          this.step = 2; // Skip to profile step if logged in AND has profile AND phone number
          this.viewMode = true;
        }

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
          disallowed_categories: (p.disallowed_categories || []).join(', ') || '',
          age: p.age || null,
          address: p.address || '',
          region: p.region || '',
          location: p.location || '',
          field_of_work: p.field_of_work || '',
          experience: Array.isArray(p.experience) ? p.experience : [],
          education: Array.isArray(p.education) ? p.education : []
        };
        this.originalProfile = { ...this.profile };
      }
    });
  }


  nextStep() {
    this.step++;
  }


  onFileSelected(event: any) {
    this.resumeFile = event.target.files[0];
  }

  uploadResume() {
    if (this.resumeFile) {
      this.profileService.uploadResume(this.resumeFile).subscribe({
        next: (res: any) => {
          console.log('Resume uploaded', res);

          if (res.suggested_profile) {
            const suggestion = res.suggested_profile;
            // Auto-fill fields if not already set by user in Step 0
            if (!this.profile.name && suggestion.name) this.profile.name = suggestion.name;
            if (!this.profile.phone_number && suggestion.phone_number) this.profile.phone_number = suggestion.phone_number;
            // We can also extract other fields later if parser improves
          }

          this.step = 2;
          this.viewMode = false; // Go to edit mode to verify/fill details
        },
        error: (err) => console.error('Upload failed', err)
      });
    }
  }

  // Experience Management
  addExperience() {
    this.profile.experience.push({ company: '', title: '', years: '', description: '' });
  }

  removeExperience(index: number) {
    this.profile.experience.splice(index, 1);
  }

  // Education Management
  addEducation() {
    this.profile.education.push({ school: '', degree: '', years: '' });
  }

  removeEducation(index: number) {
    this.profile.education.splice(index, 1);
  }

  submitProfile() {
    const profileData = {
      ...this.profile,
      desired_roles: this.profile.desired_roles.split(',').map(s => s.trim()).filter(s => s),
      desired_locations: this.profile.desired_locations.split(',').map(s => s.trim()).filter(s => s),
      company_size_prefs: this.profile.company_size_prefs.split(',').map(s => s.trim()).filter(s => s),
      disallowed_categories: this.profile.disallowed_categories.split(',').map(s => s.trim()).filter(s => s),
      // Arrays are already in correct format
      experience: this.profile.experience,
      education: this.profile.education
    };

    this.profileService.updateProfile(profileData).subscribe({
      next: (res) => {
        console.log('Profile updated', res);
        if (!this.gmailConnected && !this.originalProfile) {
          // First time completing profile — show Gmail step
          this.step = 3;
        } else {
          this.viewMode = true;
        }
        this.originalProfile = JSON.parse(JSON.stringify(this.profile)); // Deep copy
      },
      error: (err) => console.error('Update failed', err)
    });
  }

  toggleEdit() {
    this.viewMode = false;
  }

  cancelEdit() {
    this.profile = JSON.parse(JSON.stringify(this.originalProfile)); // Deep copy restore
    this.viewMode = true;
  }

  downloadResume() {
    // Keep for legacy download button if needed, but primary use is preview now
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

  toggleResumePreview() {
    if (this.showResumePreview) {
      this.showResumePreview = false;
      return;
    }

    this.profileService.downloadResume().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        this.resumePreviewUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
        this.showResumePreview = true;
      },
      error: (err) => console.error('Preview fetch failed', err)

    });
  }

  deleteAccount() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone and will remove all your data including applications and profile.')) {
      this.profileService.deleteAccount().subscribe({
        next: () => {
          alert('Account deleted successfully.');
          // Logout via auth service
          this.authService.logout();
        },
        error: (err) => {
          console.error('Delete failed', err);
          alert('Failed to delete account. Please try again.');
        }
      });
    }
  }

  connectGmail() {
    this.gmailConnecting = true;
    this.gmailService.connect().subscribe({
      next: (res) => {
        // Open OAuth URL — will redirect back to /onboarding?gmail=connected
        window.location.href = res.auth_url;
      },
      error: (err) => {
        console.error('Gmail connect failed', err);
        this.gmailConnecting = false;
        alert('Failed to start Gmail connection. Please try again.');
      }
    });
  }

  skipGmail() {
    this.step = 2;
    this.viewMode = true;
  }

  disconnectGmail() {
    this.gmailService.disconnect().subscribe({
      next: () => {
        this.gmailConnected = false;
      },
      error: (err) => console.error('Gmail disconnect failed', err)
    });
  }
}
