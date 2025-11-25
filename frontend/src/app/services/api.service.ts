import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface URLCheckRequest {
    url: string;
    metadata?: any;
}

export interface URLCheckResponse {
    check_id: string;
    status: string;
    estimated_time_seconds?: number;
}

export interface FeatureContribution {
    name: string;
    value: number;
    contribution: number;
}

export interface URLCheckResult {
    check_id: string;
    url: string;
    verdict: string;
    confidence: number;
    model_version: string;
    top_features: FeatureContribution[];
    processing_time_ms?: number;
    timestamp: string;
}

export interface SearchParams {
    domain?: string;
    verdict?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
}

export interface SearchResult {
    total: number;
    results: URLCheckResult[];
}

export interface StatsResponse {
    total_checks: number;
    verdict_distribution: { [key: string]: number };
    top_domains: Array<{ domain: string; count: number }>;
    avg_confidence: number;
    date_range: { first: string; last: string };
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private baseUrl = environment.apiUrl;

    constructor(private http: HttpClient) { }

    checkURL(request: URLCheckRequest): Observable<URLCheckResponse> {
        return this.http.post<URLCheckResponse>(`${this.baseUrl}/url/check`, request);
    }

    getCheckResult(checkId: string): Observable<URLCheckResult> {
        return this.http.get<URLCheckResult>(`${this.baseUrl}/url/${checkId}`);
    }

    searchChecks(params: SearchParams): Observable<SearchResult> {
        return this.http.post<SearchResult>(`${this.baseUrl}/url/search`, params);
    }

    getStats(): Observable<StatsResponse> {
        return this.http.get<StatsResponse>(`${this.baseUrl}/url/stats`);
    }
}
