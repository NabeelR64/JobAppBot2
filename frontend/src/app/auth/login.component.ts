import { Component, ElementRef, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from './auth.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="login-container">
      <h2>Sign in to Jinder</h2>
      <div #googleBtn></div>
    </div>
  `,
    styles: [`
    .login-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background-color: #f5f5f5;
    }
    h2 {
      margin-bottom: 2rem;
      color: #333;
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
        this.authService.renderButton(this.googleBtn.nativeElement);
    }
}
