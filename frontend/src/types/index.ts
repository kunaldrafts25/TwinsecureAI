// User types
// Backend uses different role enum, we need to map it
export type UserRole = 'admin' | 'analyst' | 'viewer' | 'api_user';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Alert types
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type AlertStatus = 'new' | 'acknowledged' | 'in_progress' | 'resolved' | 'false_positive';

export interface IpInfo {
  country: string;
  city: string;
  asn: string;
  org: string;
}

export interface Alert {
  id: string;
  alert_type: string;
  source_ip: string;
  destination_ip: string;
  ip_info: IpInfo;
  payload_snippet: string;
  raw_log_id: string;
  honeypot_id: string;
  digital_twin_asset_id: string;
  abuse_score: number;
  severity: AlertSeverity;
  status: AlertStatus;
  notes: string;
  mitre_ttp_codes: string[];
  assigned_to_user_id: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface AlertFilters {
  alert_type?: string;
  severity?: AlertSeverity;
  status?: AlertStatus;
  source_ip?: string;
  honeypot_id?: string;
  date_from?: string;
  date_to?: string;
}

// Honeypot types
export interface Honeypot {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'engaged';
  last_activity: string;
  total_engagements: number;
  created_at: string;
}

export interface HoneypotActivity {
  id: string;
  honeypot_id: string;
  timestamp: string;
  source_ip: string;
  action_type: string;
  details: Record<string, any>;
}

// Report types
export interface Report {
  id: string;
  name: string;
  type: string;
  created_at: string;
  download_url: string;
}

// System metrics
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    api: 'up' | 'down';
    database: 'up' | 'down';
    honeypots: 'up' | 'down';
  };
  last_updated: string;
}

export interface SecurityMetrics {
  total_alerts: number;
  alerts_by_severity: Record<AlertSeverity, number>;
  alerts_by_status: Record<AlertStatus, number>;
  top_attack_vectors: AttackVector[];
  top_attackers: Attacker[];
  risk_score: number;
}

// Dashboard specific types
export interface AlertTrend {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface AlertSeverityDistribution {
  name: AlertSeverity;
  value: number;
  color: string;
}

export interface AttackVector {
  name: string;
  count: number;
  percentage?: number;
}

export interface Attacker {
  ip: string;
  country: string;
  count: number;
  last_seen?: string;
}

export interface ComplianceStatus {
  dpdp: { status: string; compliant: boolean; last_checked?: string };
  gdpr: { status: string; compliant: boolean; last_checked?: string };
  iso27001: { status: string; compliant: boolean; last_checked?: string };
}

export interface DigitalTwinStatus {
  activeTwins: number;
  honeypots: number;
  engagements: number;
  last_engagement?: string;
}

// Dashboard filter types
export interface DashboardFilters {
  timeRange: '24h' | '7d' | '30d' | '90d' | 'custom';
  startDate?: string;
  endDate?: string;
  refreshInterval: number | null; // null means no auto-refresh, number is seconds
}