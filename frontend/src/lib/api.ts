/**
 * API client for Honeypot Dashboard backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Attacks
  getAttacksFeed(limit = 50, offset = 0, severity?: string) {
    let endpoint = `/attacks/feed?limit=${limit}&offset=${offset}`;
    if (severity) endpoint += `&severity=${severity}`;
    return this.request(endpoint);
  }

  getAttackStatistics() {
    return this.request('/attacks/statistics');
  }

  searchAttacks(filters: any) {
    return this.request('/attacks/search', {
      method: 'POST',
      body: JSON.stringify(filters),
    });
  }

  getAttackDetails(attackId: string) {
    return this.request(`/attacks/${attackId}`);
  }

  // Sessions
  listSessions(status?: string, limit = 50, offset = 0) {
    let endpoint = `/sessions?limit=${limit}&offset=${offset}`;
    if (status) endpoint += `&status=${status}`;
    return this.request(endpoint);
  }

  getSessionDetails(sessionId: string) {
    return this.request(`/sessions/${sessionId}`);
  }

  getSessionReplay(sessionId: string) {
    return this.request(`/sessions/${sessionId}/replay`);
  }

  // Attackers
  listAttackers(threatLevel?: string, country?: string, limit = 50, offset = 0) {
    let endpoint = `/attackers?limit=${limit}&offset=${offset}`;
    if (threatLevel) endpoint += `&threat_level=${threatLevel}`;
    if (country) endpoint += `&country=${country}`;
    return this.request(endpoint);
  }

  getAttackerProfile(ip: string) {
    return this.request(`/attackers/${ip}`);
  }

  getAttackerTimeline(ip: string) {
    return this.request(`/attackers/${ip}/timeline`);
  }

  // Intelligence
  getCommandFrequency(limit = 20, classification?: string) {
    let endpoint = `/intelligence/commands?limit=${limit}`;
    if (classification) endpoint += `&classification=${classification}`;
    return this.request(endpoint);
  }

  getCredentialsAnalysis(type = 'usernames', limit = 20) {
    return this.request(`/intelligence/credentials?credential_type=${type}&limit=${limit}`);
  }

  getPayloadsAnalysis(limit = 20) {
    return this.request(`/intelligence/payloads?limit=${limit}`);
  }

  // Analytics
  getActivityTrends(period = 'hourly', days = 7) {
    return this.request(`/analytics/trends?period=${period}&days=${days}`);
  }

  getWorldMapData() {
    return this.request('/analytics/map');
  }

  getTopList(type: string, limit = 20) {
    return this.request(`/analytics/toplist/${type}?limit=${limit}`);
  }

  // Health
  getHealth() {
    return this.request('/health');
  }
}

export const apiClient = new ApiClient();
