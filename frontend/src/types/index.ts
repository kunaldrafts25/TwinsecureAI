/*
 * TwinSecure - Advanced Cybersecurity Platform
 * Copyright © 2024 TwinSecure. All rights reserved.
 *
 * This file is part of TwinSecure, a proprietary cybersecurity platform.
 * Unauthorized copying, distribution, modification, or use of this software
 * is strictly prohibited without explicit written permission.
 *
 * For licensing inquiries: kunalsingh2514@gmail.com
 */

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

export interface ReportFilters {
  report_type?: string;
  date_from?: string;
  date_to?: string;
}

export interface ReportGenerationParams {
  report_type: string;
  start_date?: string;
  end_date?: string;
  include_charts?: boolean;
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

// Digital Twin types
export interface DigitalTwin {
  id: string;
  name: string;
  description?: string;
  twin_type: string;
  ip_address?: string;
  hostname?: string;
  network_segment?: string;
  exposed_ports?: number[];
  services?: string[];
  is_honeypot: boolean;
  honeypot_type?: string;
  vulnerability_level?: string;
  configuration?: Record<string, any>;
  status: string;
  engagement_count: number;
  total_attacks_detected: number;
  created_at: string;
  updated_at?: string;
}

export interface DigitalTwinCreate {
  name: string;
  description?: string;
  twin_type: string;
  ip_address?: string;
  hostname?: string;
  network_segment?: string;
  exposed_ports?: number[];
  services?: string[];
  is_honeypot?: boolean;
  honeypot_type?: string;
  vulnerability_level?: string;
  configuration?: Record<string, any>;
}

export interface DigitalTwinUpdate {
  name?: string;
  description?: string;
  twin_type?: string;
  ip_address?: string;
  hostname?: string;
  network_segment?: string;
  exposed_ports?: number[];
  services?: string[];
  is_honeypot?: boolean;
  honeypot_type?: string;
  vulnerability_level?: string;
  status?: string;
  configuration?: Record<string, any>;
}

export interface NetworkTopology {
  id: string;
  source_twin_id: string;
  destination_twin_id: string;
  connection_type?: string;
  protocol?: string;
  ports?: number[];
  created_at: string;
}

export interface TwinEngagement {
  id: string;
  twin_id: string;
  attacker_ip: string;
  engagement_type: string;
  severity: string;
  attack_vector?: string;
  payload?: Record<string, any>;
  started_at: string;
  ended_at?: string;
}

// Honeypot data types
export interface HoneypotData {
  timestamp: string;
  sourceIp: string; // Backend accepts both sourceIp and source_ip
  source_ip?: string; // Alternative format
  requestId?: string;
  request_id?: string; // Alternative format
  httpMethod?: string;
  http_method?: string; // Alternative format
  uri?: string;
  headers?: Record<string, any>;
  queryString?: string;
  query_string?: string; // Alternative format
  body?: string;
  action?: string; // WAF action: ALLOW, BLOCK
  waf_action?: string; // Alternative format
  ruleGroupList?: any[];
  rule_group_list?: any[]; // Alternative format
  // Legacy fields for backward compatibility
  destination_ip?: string;
  protocol?: string;
  port?: number;
  url?: string;
  method?: string;
  user_agent?: string;
  payload?: string;
  request_count?: number;
  response_time_ms?: number;
  status_code?: number;
  bytes_sent?: number;
  bytes_received?: number;
  duration_seconds?: number;
  honeypot_id?: string;
  digital_twin_id?: string;
}

// User management types
export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
  role?: UserRole;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdate {
  email?: string;
  password?: string;
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
  is_superuser?: boolean;
}

// Dashboard filter types
export interface DashboardFilters {
  timeRange: '24h' | '7d' | '30d' | '90d' | 'custom';
  startDate?: string;
  endDate?: string;
  refreshInterval: number | null; // null means no auto-refresh, number is seconds
}