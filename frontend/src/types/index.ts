export interface Alert {
  id: string;
  type: 'Honeypot Triggered' | 'Anomaly Detected' | 'Brute Force' | 'SQL Injection' | 'XSS Attempt';
  severity: 'low' | 'medium' | 'high' | 'critical';
  ip: string;
  location: string;
  country: string;
  payload?: string;
  timestamp: string;
  status: 'new' | 'investigating' | 'resolved' | 'false-positive';
  enrichment?: {
    abuseScore?: number;
    previousIncidents?: number;
    knownMalicious?: boolean;
  };
}

export interface AttackOrigin {
  country: string;
  count: number;
  coordinates: [number, number];
}

export interface AttackTrend {
  date: string;
  honeypotHits: number;
  blockedAttacks: number;
  anomalies: number;
}

export interface PayloadType {
  type: string;
  count: number;
  percentage: number;
}

export interface SystemMetric {
  timestamp: string;
  cpu: number;
  memory: number;
  requests: number;
  errorRate: number;
}

export interface Report {
  id: string;
  title: string;
  date: string;
  summary: string;
  downloadUrl: string;
  type: 'weekly' | 'monthly' | 'incident' | 'audit';
  status: 'draft' | 'published';
}

export interface HoneypotEvent {
  id: string;
  timestamp: string;
  ip: string;
  location: string;
  protocol: string;
  port: number;
  payload: string;
  tags: string[];
  malwareSignature?: string;
}

export interface AnomalyEvent {
  id: string;
  timestamp: string;
  type: 'network' | 'system' | 'application' | 'database' | 'user';
  severity: 'low' | 'medium' | 'high' | 'critical';
  metric: string;
  expected: number;
  actual: number;
  description: string;
}

export interface SecurityMetric {
  id: string;
  name: string;
  value: number;
  trend: number;
  status: 'good' | 'warning' | 'critical';
  category: 'performance' | 'security' | 'compliance';
}

export interface ComplianceCheck {
  id: string;
  standard: string;
  control: string;
  status: 'passed' | 'failed' | 'warning';
  lastCheck: string;
  nextCheck: string;
  details: string;
}

export interface VulnerabilityScan {
  id: string;
  timestamp: string;
  target: string;
  findings: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  status: 'complete' | 'in-progress' | 'scheduled';
}