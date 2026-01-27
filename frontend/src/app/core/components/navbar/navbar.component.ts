import { Component, OnInit, NgZone, effect, Injector, runInInjectionContext } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit {

  showDropdown = false;

  constructor(public authService: AuthService, private ngZone: NgZone) { }

  ngOnInit(): void {
    // Initialize the Google client helper
    this.authService.initializeGoogleSignIn();

    // Attempt to render the button if we are not authenticated
    if (!this.authService.isAuthenticated()) {
      // We give a slight delay to ensure the DOM element #google-btn is present
      // (since it's inside an *ngTemplate driven by *ngIf)
      setTimeout(() => this.renderGoogleButton(), 500);
    }
  }

  renderGoogleButton() {
    const btnDiv = document.getElementById('google-btn');
    if (btnDiv) {
      this.authService.renderGoogleButton(btnDiv);
    }
  }

  toggleDropdown() {
    this.showDropdown = !this.showDropdown;
  }

  logout() {
    this.authService.logout();
    this.showDropdown = false;
    // Re-render button after logout updates the view
    setTimeout(() => this.renderGoogleButton(), 100);
  }
}
