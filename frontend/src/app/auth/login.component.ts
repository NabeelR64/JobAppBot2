import { Component, ElementRef, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="login-container">
      <div class="login-card">
        <div class="login-logo">⚡</div>
        <h2>Welcome to <span class="brand">Jinder</span></h2>
        <p class="login-subtitle">Sign in to start swiping on your dream job</p>
        <div class="google-btn-wrapper" #googleBtn></div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: calc(100vh - var(--navbar-height));
      background: var(--gradient-hero);
      padding: 2rem;
    }
    .login-card {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(16px);
      border-radius: var(--radius-xl);
      padding: 3rem 2.5rem;
      text-align: center;
      max-width: 400px;
      width: 100%;
      animation: fadeInUp 0.6s ease;
    }
    .login-logo {
      font-size: 2.5rem;
      margin-bottom: 1rem;
    }
    h2 {
      color: white;
      font-size: 1.5rem;
      font-weight: 700;
      margin: 0 0 0.5rem;
    }
    .brand {
      background: linear-gradient(135deg, #818cf8, #c084fc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .login-subtitle {
      color: rgba(255, 255, 255, 0.5);
      font-size: 0.9375rem;
      margin: 0 0 2rem;
    }
    .google-btn-wrapper {
      display: flex;
      justify-content: center;
    }
  `]
})
export class LoginComponent implements OnInit, AfterViewInit {
  @ViewChild('googleBtn') googleBtn!: ElementRef;

  constructor(private authService: AuthService) { }

  ngOnInit(): void {
    // Initialize callback
    this.authService.initializeGoogleSignIn();
  }

  ngAfterViewInit(): void {
    // Render button
    this.authService.renderGoogleButton(this.googleBtn.nativeElement);
  }
}

