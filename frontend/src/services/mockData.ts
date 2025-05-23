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

import { addDays, subDays, subHours } from 'date-fns';
import { Alert, AlertSeverity, AlertStatus, Honeypot, Report, SecurityMetrics, SystemHealth, User } from '../types';

// Helper to generate random IDs
const generateId = () => Math.random().toString(36).substring(2, 15);

// Helper to get random enum value
const getRandomEnumValue = <T>(enumObject: T): T[keyof T] => {
  const values = Object.values(enumObject) as T[keyof T][];
  return values[Math.floor(Math.random() * values.length)];
};

// Mock severity levels
const severityLevels: Record<string, AlertSeverity> = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
  INFO: 'info',
};

// Mock alert status
const alertStatuses: Record<string, AlertStatus> = {
  NEW: 'new',
  ACKNOWLEDGED: 'acknowledged',
  IN_PROGRESS: 'in_progress',
  RESOLVED: 'resolved',
  FALSE_POSITIVE: 'false_positive',
};

// Mock MITRE ATT&CK technique IDs
const mitreTechniques = [
  'T1059', // Command and Scripting Interpreter
  'T1566', // Phishing
  'T1190', // Exploit Public-Facing Application
  'T1133', // External Remote Services
  'T1078', // Valid Accounts
  'T1486', // Data Encrypted for Impact
  'T1082', // System Information Discovery
  'T1016', // System Network Configuration Discovery
  'T1018', // Remote System Discovery
  'T1021', // Remote Services
];

// Mock alert types
const alertTypes = [
  'Honeypot Access',
  'Credential Theft Attempt',
  'Brute Force Attack',
  'SQL Injection Attempt',
  'Cross-Site Scripting',
  'Suspicious Command Execution',
  'Data Exfiltration Attempt',
  'Malware Detected',
  'Ransomware Activity',
  'Privilege Escalation',
];

// Mock IPs with country codes
const mockIPs = [
  { ip: '203.0.113.1', country: 'US', city: 'New York', asn: 'AS12345', org: 'Example ISP' },
  { ip: '198.51.100.2', country: 'RU', city: 'Moscow', asn: 'AS67890', org: 'Sample Telecom' },
  { ip: '192.0.2.3', country: 'CN', city: 'Beijing', asn: 'AS13579', org: 'Test Network' },
  { ip: '198.51.100.4', country: 'BR', city: 'Sao Paulo', asn: 'AS24680', org: 'Example Provider' },
  { ip: '203.0.113.5', country: 'IN', city: 'Mumbai', asn: 'AS11111', org: 'Global Internet' },
];

// Generate mock user data
export const mockUsers: User[] = [
  {
    id: '1',
    email: 'admin@sme.com',
    full_name: 'SME Admin',
    role: 'sme_admin',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    email: 'user@sme.com',
    full_name: 'SME User',
    role: 'sme_user',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '3',
    email: 'mssp@provider.com',
    full_name: 'MSSP Partner',
    role: 'mssp_user',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '4',
    email: 'super@twinsecure.ai',
    full_name: 'System Administrator',
    role: 'superuser',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

// Generate mock alerts
export const generateMockAlerts = (count: number): Alert[] => {
  const alerts: Alert[] = [];

  for (let i = 0; i < count; i++) {
    const createdDate = subDays(new Date(), Math.floor(Math.random() * 30));
    const updatedDate = subHours(new Date(), Math.floor(Math.random() * 24));
    const severity = getRandomEnumValue(severityLevels);
    const status = getRandomEnumValue(alertStatuses);
    const mockIpInfo = mockIPs[Math.floor(Math.random() * mockIPs.length)];

    alerts.push({
      id: generateId(),
      alert_type: alertTypes[Math.floor(Math.random() * alertTypes.length)],
      source_ip: mockIpInfo.ip,
      destination_ip: '10.0.0.' + Math.floor(Math.random() * 255),
      ip_info: {
        country: mockIpInfo.country,
        city: mockIpInfo.city,
        asn: mockIpInfo.asn,
        org: mockIpInfo.org,
      },
      payload_snippet: `POST /admin/login.php HTTP/1.1\nHost: target.com\nUser-Agent: Mozilla/5.0\nContent-Type: application/x-www-form-urlencoded\n\nusername=admin&password=123456'OR 1=1--`,
      raw_log_id: generateId(),
      honeypot_id: 'hp-' + Math.floor(Math.random() * 5),
      digital_twin_asset_id: 'dt-' + Math.floor(Math.random() * 10),
      abuse_score: Math.floor(Math.random() * 100),
      severity,
      status,
      notes: status === 'resolved' ? 'Issue has been analyzed and resolved.' : '',
      mitre_ttp_codes: [
        mitreTechniques[Math.floor(Math.random() * mitreTechniques.length)],
        mitreTechniques[Math.floor(Math.random() * mitreTechniques.length)],
      ],
      assigned_to_user_id: Math.random() > 0.5 ? mockUsers[Math.floor(Math.random() * mockUsers.length)].id : null,
      created_at: createdDate.toISOString(),
      updated_at: updatedDate.toISOString(),
      resolved_at: status === 'resolved' ? updatedDate.toISOString() : null,
    });
  }

  return alerts;
};

// Mock honeypots
export const mockHoneypots: Honeypot[] = [
  {
    id: 'hp-1',
    name: 'Web Server Honeypot',
    type: 'web-server',
    status: 'active',
    last_activity: subHours(new Date(), 2).toISOString(),
    total_engagements: 25,
    created_at: subDays(new Date(), 45).toISOString(),
  },
  {
    id: 'hp-2',
    name: 'Database Honeypot',
    type: 'database',
    status: 'engaged',
    last_activity: new Date().toISOString(),
    total_engagements: 12,
    created_at: subDays(new Date(), 30).toISOString(),
  },
  {
    id: 'hp-3',
    name: 'SSH Server Honeypot',
    type: 'ssh',
    status: 'active',
    last_activity: subDays(new Date(), 1).toISOString(),
    total_engagements: 78,
    created_at: subDays(new Date(), 60).toISOString(),
  },
  {
    id: 'hp-4',
    name: 'IoT Device Honeypot',
    type: 'iot',
    status: 'inactive',
    last_activity: subDays(new Date(), 15).toISOString(),
    total_engagements: 3,
    created_at: subDays(new Date(), 20).toISOString(),
  },
];

// Mock reports
export const mockReports: Report[] = [
  {
    id: 'rep-1',
    name: 'Monthly Security Summary - April 2025',
    type: 'monthly',
    created_at: subDays(new Date(), 15).toISOString(),
    download_url: '#',
  },
  {
    id: 'rep-2',
    name: 'Threat Intelligence Report',
    type: 'threat',
    created_at: subDays(new Date(), 7).toISOString(),
    download_url: '#',
  },
  {
    id: 'rep-3',
    name: 'Honeypot Activity Analysis',
    type: 'activity',
    created_at: subDays(new Date(), 3).toISOString(),
    download_url: '#',
  },
  {
    id: 'rep-4',
    name: 'Compliance Status - DPDP Act',
    type: 'compliance',
    created_at: subDays(new Date(), 10).toISOString(),
    download_url: '#',
  },
];

// Mock system health
export const mockSystemHealth: SystemHealth = {
  status: 'healthy',
  components: {
    api: 'up',
    database: 'up',
    honeypots: 'up',
  },
  last_updated: new Date().toISOString(),
};

// Mock security metrics
export const mockSecurityMetrics: SecurityMetrics = {
  total_alerts: 127,
  alerts_by_severity: {
    critical: 12,
    high: 35,
    medium: 48,
    low: 25,
    info: 7,
  },
  alerts_by_status: {
    new: 37,
    acknowledged: 28,
    in_progress: 24,
    resolved: 32,
    false_positive: 6,
  },
  top_attack_vectors: [
    { name: 'Brute Force', count: 42 },
    { name: 'SQL Injection', count: 27 },
    { name: 'Credential Theft', count: 18 },
    { name: 'XSS', count: 15 },
  ],
  top_attackers: [
    { ip: '203.0.113.1', country: 'US', count: 35 },
    { ip: '198.51.100.2', country: 'RU', count: 28 },
    { ip: '192.0.2.3', country: 'CN', count: 22 },
  ],
  risk_score: 72,
};

// Dates for trend data
const getDatesForTrendData = (days: number) => {
  const dates = [];
  for (let i = days; i >= 0; i--) {
    dates.push(subDays(new Date(), i).toISOString().split('T')[0]);
  }
  return dates;
};

// Alert trend data for charts
export const mockAlertTrendData = getDatesForTrendData(30).map((date) => ({
  date,
  critical: Math.floor(Math.random() * 5),
  high: Math.floor(Math.random() * 10),
  medium: Math.floor(Math.random() * 15),
  low: Math.floor(Math.random() * 10),
  info: Math.floor(Math.random() * 5),
}));

// Mock alert severity distribution for pie chart
export const mockAlertSeverityDistribution = [
  { name: 'critical', value: 12, color: '#EF4444' },
  { name: 'high', value: 35, color: '#F59E0B' },
  { name: 'medium', value: 48, color: '#FBBF24' },
  { name: 'low', value: 25, color: '#10B981' },
  { name: 'info', value: 7, color: '#3B82F6' },
];

// Mock attack vectors with percentage
export const mockAttackVectors = [
  { name: 'Brute Force', count: 42, percentage: 32.8 },
  { name: 'SQL Injection', count: 27, percentage: 21.1 },
  { name: 'Credential Theft', count: 18, percentage: 14.1 },
  { name: 'XSS', count: 15, percentage: 11.7 },
  { name: 'Command Injection', count: 12, percentage: 9.4 },
];

// Mock attackers with last seen timestamp
export const mockAttackers = [
  { ip: '203.0.113.1', country: 'US', count: 35, last_seen: subHours(new Date(), 2).toISOString() },
  { ip: '198.51.100.2', country: 'RU', count: 28, last_seen: subHours(new Date(), 5).toISOString() },
  { ip: '192.0.2.3', country: 'CN', count: 22, last_seen: subHours(new Date(), 8).toISOString() },
  { ip: '198.51.100.4', country: 'BR', count: 19, last_seen: subHours(new Date(), 12).toISOString() },
  { ip: '203.0.113.5', country: 'IN', count: 15, last_seen: subHours(new Date(), 18).toISOString() },
];

// Mock compliance status
export const mockComplianceStatus = {
  dpdp: { status: 'Compliant', compliant: true, last_checked: subDays(new Date(), 5).toISOString() },
  gdpr: { status: 'Review needed', compliant: false, last_checked: subDays(new Date(), 10).toISOString() },
  iso27001: { status: 'Compliant', compliant: true, last_checked: subDays(new Date(), 15).toISOString() },
};

// Mock digital twin status
export const mockDigitalTwinStatus = {
  activeTwins: 12,
  honeypots: 8,
  engagements: 24,
  last_engagement: subHours(new Date(), 3).toISOString(),
};

// Mock MITRE TTP frequency data
export const mockTTPFrequencyData = mitreTechniques.map((techniqueId) => ({
  id: techniqueId,
  count: Math.floor(Math.random() * 50) + 5,
  description: `MITRE ATT&CK Technique ${techniqueId}`,
}));

// Generated alerts using the function
export const mockAlerts = generateMockAlerts(50);