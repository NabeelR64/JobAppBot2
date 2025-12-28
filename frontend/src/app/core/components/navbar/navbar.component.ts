import { Component, OnInit, NgZone } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

declare const google: any;

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit {
  constructor(public authService: AuthService, private ngZone: NgZone) { }

  ngOnInit(): void {
    // We need to wait for the script to load, but typically it loads fast in head.
    // In a production app we might check if 'google' is defined or listen for load.
    if (typeof google !== 'undefined') {
      this.initializeGoogleSignIn();
    } else {
      // Simple retry mechanism or window.onload listener could be here
      // For MVP, assuming it loads by the time this component inits
      setTimeout(() => this.initializeGoogleSignIn(), 1000);
    }
  }

  initializeGoogleSignIn() {
    if (!google) return;

    google.accounts.id.initialize({
      client_id: '800074565628-ekda343qa4971qssthafiqc4j5bmh5ot.apps.googleusercontent.com',
      callback: (response: any) => this.handleCredentialResponse(response)
    });
    this.renderGoogleButton();
  }

  handleCredentialResponse(response: any) {
    // Angular runs outside of Zone for global callbacks, so re-enter zone
    this.ngZone.run(() => {
      this.authService.loginWithGoogle(response.credential).subscribe({
        next: () => console.log('Logged in with Google'),
        error: (err) => console.error('Google login failed', err)
      });
    });
  }

  renderGoogleButton() {
    // We need a div in the HTML to render the button
    const btnDiv = document.getElementById('google-btn');
    if (btnDiv && google) {
      google.accounts.id.renderButton(
        btnDiv,
        { theme: 'outline', size: 'large' }  // customization attributes
      );
    }
  }

  // We call render button when the user is NOT authenticated.
  // We can use an effect or just call it after init if not logged in.
  // However, since we have an *ngIf in the template, we should verify when the element exists.
  // A simple way is to use a setter or AfterViewChecked, but for MVP:
  // We'll trust the button appears and we render it.

  logout() {
    this.authService.logout();
    // Allow *ngIf to update UI then render button
    setTimeout(() => this.renderGoogleButton(), 100);
  }
}
