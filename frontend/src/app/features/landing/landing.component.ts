import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.css'
})
export class LandingComponent {

  constructor(private authService: AuthService, private router: Router) { }

  signInWithGoogle() {
    // In a real app, this would trigger the Google Sign-In popup
    // For MVP UI flow, we'll simulate a successful login
    console.log('Sign in with Google clicked');
    this.authService.mockLogin().subscribe({
      next: (res) => {
        console.log('Logged in', res);
        // Store token
        localStorage.setItem('token', res.access_token);
        // Redirect to onboarding
        this.router.navigate(['/onboarding']);
      },
      error: (err) => console.error('Login failed', err)
    });
  }
}
