/**
 * API types and interfaces
 */

export enum EventType {
  CONNECTION = "connection",
  AUTH_ATTEMPT = "auth_attempt",
  LOGIN = "login",
  COMMAND = "command",
  DOWNLOAD = "download",
}

export enum Severity {
  INFO = "INFO",
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum SessionStatus {
  ACTIVE = "active",
  COMPLETE = "complete",
  FAILED = "failed",
}

export enum CommandClassification {
  RECONNAISSANCE = "reconnaissance",
  FILE_DOWNLOAD = "file_download",
  EXECUTION = "execution",
  PERSISTENCE = "persistence",
  NETWORKING = "networking",
  PRIVILEGE_ESCALATION = "privilege_escalation",
}

export enum ThreatLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

// Attack
export interface Attack {
  id: string;
  timestamp: string;
  session_id?: string;
  attacker_ip: string;
  country_code?: string;
  event_type: EventType;
  severity: Severity;
  asn?: number;
  metadata?: Record<string, any>;
}

// Session
export interface Session {
  id: string;
  attacker_ip: string;
  start_time: string;
  end_time?: string;
  duration_seconds?: number;
  status: SessionStatus;
  total_commands: number;
  protocol: string;
}

export interface SessionDetails extends Session {
  attacker: {
    country: string;
    asn?: number;
    isp?: string;
    first_seen: string;
    last_seen: string;
    session_count: number;
    command_count: number;
  };
  commands: Command[];
  downloads: Download[];
  credentials_attempted: Credential[];
}

// Command
export interface Command {
  id: string;
  timestamp: string;
  command: string;
  classification?: CommandClassification;
  success: boolean;
  output?: string;
}

// Download
export interface Download {
  id: string;
  timestamp: string;
  filename: string;
  file_hash?: string;
  file_size?: number;
  url?: string;
  file_type?: string;
}

// Credential
export interface Credential {
  id: string;
  username: string;
  password: string;
  timestamp: string;
  success: boolean;
}

// Attacker
export interface Attacker {
  ip_address: string;
  country_code: string;
  asn?: number;
  isp?: string;
  first_seen: string;
  last_seen: string;
  total_sessions: number;
  total_commands: number;
  total_downloads: number;
  max_severity: Severity;
  threat_level: ThreatLevel;
}

export interface AttackerProfile extends Attacker {
  recent_sessions: Array<{
    id: string;
    start_time: string;
    end_time?: string;
    status: SessionStatus;
    command_count: number;
  }>;
  top_commands: Array<{
    command: string;
    count: number;
  }>;
}

// Statistics
export interface AttackStatistics {
  attacks_today: number;
  attacks_this_week: number;
  attacks_this_month: number;
  unique_attackers: number;
  unique_countries: number;
  total_commands: number;
  total_downloads: number;
  avg_session_duration?: number;
}

// Timeline
export interface TimelineEvent {
  stage: string;
  timestamp: string;
  details: string;
  session_id?: string;
}

// Top List
export interface TopItem {
  rank: number;
  name: string;
  code?: string;
  value: number;
  percentage: number;
}

export interface TopList {
  type: string;
  data: TopItem[];
}

// Analytics
export interface TrendData {
  timestamp: string;
  attacks: number;
  unique_attackers: number;
  unique_countries: number;
}

export interface TrendResponse {
  period: string;
  data: TrendData[];
}

export interface MapData {
  country_code: string;
  country_name: string;
  latitude: number;
  longitude: number;
  attack_count: number;
  unique_attackers: number;
  intensity: number;
}

export interface MapResponse {
  data: MapData[];
}

// Generic responses
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface SearchResponse<T> extends PaginatedResponse<T> {
  filters_applied?: Record<string, any>;
}

// WebSocket
export interface WebSocketEvent {
  type: string;
  data?: any;
  timestamp?: string;
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  filters?: Record<string, any>;
}
