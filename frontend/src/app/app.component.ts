import { Component } from '@angular/core';
import { ApiService, URLCheckResult } from './services/api.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'URL Phishing Detector';
  url = '';
  loading = false;
  result: URLCheckResult | null = null;
  error: string | null = null;
  recentChecks: URLCheckResult[] = [];

  constructor(private apiService: ApiService) {
    this.loadRecentChecks();
  }

  checkURL() {
    if (!this.url.trim()) {
      this.error = 'Please enter a URL';
      return;
    }

    this.loading = true;
    this.error = null;
    this.result = null;

    this.apiService.checkURL({ url: this.url }).subscribe({
      next: (response) => {
        // Get the result
        this.apiService.getCheckResult(response.check_id).subscribe({
          next: (result) => {
            this.result = result;
            this.loading = false;
            this.loadRecentChecks();
          },
          error: (err) => {
            this.error = 'Failed to get result: ' + err.message;
            this.loading = false;
          }
        });
      },
      error: (err) => {
        this.error = 'Failed to check URL: ' + err.message;
        this.loading = false;
      }
    });
  }

  loadRecentChecks() {
    this.apiService.searchChecks({ limit: 10, offset: 0 }).subscribe({
      next: (response) => {
        this.recentChecks = response.results;
      },
      error: (err) => {
        console.error('Failed to load recent checks:', err);
      }
    });
  }

  getVerdictClass(verdict: string): string {
    switch (verdict.toLowerCase()) {
      case 'benign':
        return 'verdict-benign';
      case 'suspicious':
        return 'verdict-suspicious';
      case 'malicious':
        return 'verdict-malicious';
      default:
        return '';
    }
  }

  getVerdictIcon(verdict: string): string {
    switch (verdict.toLowerCase()) {
      case 'benign':
        return '✓';
      case 'suspicious':
        return '⚠';
      case 'malicious':
        return '✗';
      default:
        return '?';
    }
  }

  clearResult() {
    this.result = null;
    this.error = null;
    this.url = '';
  }
}
