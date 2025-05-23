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

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  Clock, 
  Download, 
  RefreshCw, 
  Server, 
  Shield, 
  Zap 
} from 'lucide-react';
import Button from '../../../components/common/Button';
import DetailModal from '../../../components/dashboard/DetailModal';
import StatusIndicator from '../../../components/common/StatusIndicator';

// Mock data for charts - in a real app, this would come from an API
const mockTrafficData = [
  { time: '00:00', requests: 12 },
  { time: '01:00', requests: 8 },
  { time: '02:00', requests: 5 },
  { time: '03:00', requests: 2 },
  { time: '04:00', requests: 3 },
  { time: '05:00', requests: 7 },
  { time: '06:00', requests: 14 },
  { time: '07:00', requests: 22 },
  { time: '08:00', requests: 35 },
  { time: '09:00', requests: 42 },
  { time: '10:00', requests: 38 },
  { time: '11:00', requests: 35 },
  { time: '12:00', requests: 30 },
];

// Mock events
const mockEvents = [
  { id: 1, type: 'connection', source_ip: '192.168.1.105', timestamp: '2023-06-15T10:23:45Z', details: 'SSH connection attempt' },
  { id: 2, type: 'scan', source_ip: '203.0.113.42', timestamp: '2023-06-15T10:15:22Z', details: 'Port scan detected' },
  { id: 3, type: 'login', source_ip: '10.0.0.15', timestamp: '2023-06-15T09:58:11Z', details: 'Successful login' },
  { id: 4, type: 'request', source_ip: '198.51.100.73', timestamp: '2023-06-15T09:45:30Z', details: 'GET /admin.php' },
  { id: 5, type: 'error', source_ip: '192.168.1.105', timestamp: '2023-06-15T09:30:15Z', details: 'HTTP 500 error' },
];

interface DigitalTwinMonitorModalProps {
  isOpen: boolean;
  onClose: () => void;
  twinId: number;
  twinName: string;
  twinType: string;
  twinIp: string;
}

const DigitalTwinMonitorModal: React.FC<DigitalTwinMonitorModalProps> = ({
  isOpen,
  onClose,
  twinId,
  twinName,
  twinType,
  twinIp,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'traffic' | 'events' | 'logs'>('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [cpuUsage, setCpuUsage] = useState(42);
  const [memoryUsage, setMemoryUsage] = useState(28);
  const [diskUsage, setDiskUsage] = useState(65);
  const [networkUsage, setNetworkUsage] = useState(15);
  
  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setCpuUsage(Math.floor(Math.random() * 30) + 30); // 30-60%
      setMemoryUsage(Math.floor(Math.random() * 20) + 20); // 20-40%
      setDiskUsage(Math.floor(Math.random() * 10) + 60); // 60-70%
      setNetworkUsage(Math.floor(Math.random() * 20) + 10); // 10-30%
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Handle refresh
  const handleRefresh = () => {
    setIsRefreshing(true);
    
    // Simulate API call
    setTimeout(() => {
      setCpuUsage(Math.floor(Math.random() * 30) + 30);
      setMemoryUsage(Math.floor(Math.random() * 20) + 20);
      setDiskUsage(Math.floor(Math.random() * 10) + 60);
      setNetworkUsage(Math.floor(Math.random() * 20) + 10);
      setIsRefreshing(false);
    }, 1000);
  };
  
  return (
    <DetailModal
      title={`Monitor Digital Twin: ${twinName}`}
      isOpen={isOpen}
      onClose={onClose}
    >
      <div className="space-y-6">
        {/* Status Summary */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
              <Server className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-medium">{twinName}</h3>
              <p className="text-sm text-foreground/70">{twinIp}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <StatusIndicator type="status" value="active" />
            <span className="text-sm font-medium">Active</span>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="border-b border-border">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('overview')}
              className={`border-b-2 py-4 px-1 text-sm font-medium ${
                activeTab === 'overview'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-foreground/60 hover:border-foreground/30 hover:text-foreground/80'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('traffic')}
              className={`border-b-2 py-4 px-1 text-sm font-medium ${
                activeTab === 'traffic'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-foreground/60 hover:border-foreground/30 hover:text-foreground/80'
              }`}
            >
              Traffic
            </button>
            <button
              onClick={() => setActiveTab('events')}
              className={`border-b-2 py-4 px-1 text-sm font-medium ${
                activeTab === 'events'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-foreground/60 hover:border-foreground/30 hover:text-foreground/80'
              }`}
            >
              Events
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`border-b-2 py-4 px-1 text-sm font-medium ${
                activeTab === 'logs'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-foreground/60 hover:border-foreground/30 hover:text-foreground/80'
              }`}
            >
              Logs
            </button>
          </nav>
        </div>
        
        {/* Tab Content */}
        <div className="relative">
          <div className="absolute right-0 top-0">
            <Button
              variant="outline"
              size="sm"
              leftIcon={<RefreshCw size={14} />}
              isLoading={isRefreshing}
              onClick={handleRefresh}
            >
              Refresh
            </Button>
          </div>
          
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6 pt-10">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div className="rounded-lg border border-border p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-foreground/70">CPU</span>
                    <span className={`text-sm font-medium ${cpuUsage > 50 ? 'text-orange-500' : 'text-green-500'}`}>
                      {cpuUsage}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-foreground/10">
                    <div 
                      className={`h-2 rounded-full ${cpuUsage > 50 ? 'bg-orange-500' : 'bg-green-500'}`} 
                      style={{ width: `${cpuUsage}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="rounded-lg border border-border p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-foreground/70">Memory</span>
                    <span className="text-sm font-medium text-green-500">
                      {memoryUsage}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-foreground/10">
                    <div 
                      className="h-2 rounded-full bg-green-500" 
                      style={{ width: `${memoryUsage}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="rounded-lg border border-border p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-foreground/70">Disk</span>
                    <span className={`text-sm font-medium ${diskUsage > 80 ? 'text-red-500' : diskUsage > 60 ? 'text-orange-500' : 'text-green-500'}`}>
                      {diskUsage}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-foreground/10">
                    <div 
                      className={`h-2 rounded-full ${diskUsage > 80 ? 'bg-red-500' : diskUsage > 60 ? 'bg-orange-500' : 'bg-green-500'}`} 
                      style={{ width: `${diskUsage}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="rounded-lg border border-border p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-foreground/70">Network</span>
                    <span className="text-sm font-medium text-green-500">
                      {networkUsage}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-foreground/10">
                    <div 
                      className="h-2 rounded-full bg-green-500" 
                      style={{ width: `${networkUsage}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div className="rounded-lg border border-border p-4">
                <h4 className="mb-4 text-sm font-medium">System Information</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-foreground/70">Operating System:</span>
                    <span className="text-sm">Ubuntu 22.04 LTS</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-foreground/70">Kernel Version:</span>
                    <span className="text-sm">5.15.0-76-generic</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-foreground/70">Uptime:</span>
                    <span className="text-sm">15 days, 7 hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-foreground/70">Last Patched:</span>
                    <span className="text-sm">2023-06-01</span>
                  </div>
                </div>
              </div>
              
              <div className="rounded-lg border border-border p-4">
                <h4 className="mb-4 text-sm font-medium">Recent Activity</h4>
                <div className="space-y-3">
                  {mockEvents.slice(0, 3).map((event) => (
                    <div key={event.id} className="flex items-start gap-3">
                      <div className="mt-0.5 rounded-full bg-primary/10 p-1">
                        <Activity size={12} className="text-primary" />
                      </div>
                      <div>
                        <p className="text-sm">{event.details}</p>
                        <p className="text-xs text-foreground/70">
                          {new Date(event.timestamp).toLocaleString()} • {event.source_ip}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {/* Traffic Tab */}
          {activeTab === 'traffic' && (
            <div className="space-y-6 pt-10">
              <div className="rounded-lg border border-border p-4">
                <h4 className="mb-4 text-sm font-medium">Traffic Overview</h4>
                <div className="h-64 w-full">
                  {/* In a real app, this would be a chart component */}
                  <div className="flex h-full items-end justify-between">
                    {mockTrafficData.map((data, index) => (
                      <div key={index} className="flex flex-col items-center">
                        <div 
                          className="w-8 bg-primary" 
                          style={{ height: `${data.requests * 2}px` }}
                        ></div>
                        <span className="mt-2 text-xs">{data.time}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="rounded-lg border border-border p-4">
                  <h4 className="text-lg font-medium">245</h4>
                  <p className="text-sm text-foreground/70">Total Requests (24h)</p>
                </div>
                <div className="rounded-lg border border-border p-4">
                  <h4 className="text-lg font-medium">12</h4>
                  <p className="text-sm text-foreground/70">Unique IPs</p>
                </div>
                <div className="rounded-lg border border-border p-4">
                  <h4 className="text-lg font-medium">3</h4>
                  <p className="text-sm text-foreground/70">Suspicious Requests</p>
                </div>
              </div>
            </div>
          )}
          
          {/* Events Tab */}
          {activeTab === 'events' && (
            <div className="space-y-6 pt-10">
              <div className="rounded-lg border border-border">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-border">
                    <thead>
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Source IP</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Timestamp</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Details</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {mockEvents.map((event) => (
                        <tr key={event.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                              {event.type}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            {event.source_ip}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            {new Date(event.timestamp).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            {event.details}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<Download size={14} />}
                >
                  Export Events
                </Button>
              </div>
            </div>
          )}
          
          {/* Logs Tab */}
          {activeTab === 'logs' && (
            <div className="space-y-6 pt-10">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium">System Logs</h4>
                <div className="flex gap-2">
                  <select className="rounded-md border border-input bg-transparent px-3 py-1 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                    <option value="all">All Logs</option>
                    <option value="system">System</option>
                    <option value="auth">Authentication</option>
                    <option value="app">Application</option>
                  </select>
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<Download size={14} />}
                  >
                    Download
                  </Button>
                </div>
              </div>
              
              <div className="rounded-lg border border-border p-4">
                <pre className="h-96 overflow-auto text-xs">
                  <code>
                    {`Jun 15 10:23:45 webserver sshd[12345]: Connection from 192.168.1.105 port 52413
Jun 15 10:23:46 webserver sshd[12345]: Failed password for invalid user admin from 192.168.1.105 port 52413 ssh2
Jun 15 10:23:48 webserver sshd[12345]: Failed password for invalid user admin from 192.168.1.105 port 52413 ssh2
Jun 15 10:23:50 webserver sshd[12345]: Failed password for invalid user admin from 192.168.1.105 port 52413 ssh2
Jun 15 10:23:52 webserver sshd[12345]: Connection closed by 192.168.1.105 port 52413 [preauth]
Jun 15 10:15:22 webserver kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:00:00:00:00:00:00:00:00:00:00:00:00:00 SRC=203.0.113.42 DST=10.0.0.5 LEN=40 TOS=0x00 PREC=0x00 TTL=249 ID=54321 PROTO=TCP SPT=45678 DPT=22 WINDOW=1024 RES=0x00 SYN URGP=0
Jun 15 10:15:22 webserver kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:00:00:00:00:00:00:00:00:00:00:00:00:00 SRC=203.0.113.42 DST=10.0.0.5 LEN=40 TOS=0x00 PREC=0x00 TTL=249 ID=54322 PROTO=TCP SPT=45678 DPT=80 WINDOW=1024 RES=0x00 SYN URGP=0
Jun 15 10:15:22 webserver kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:00:00:00:00:00:00:00:00:00:00:00:00:00 SRC=203.0.113.42 DST=10.0.0.5 LEN=40 TOS=0x00 PREC=0x00 TTL=249 ID=54323 PROTO=TCP SPT=45678 DPT=443 WINDOW=1024 RES=0x00 SYN URGP=0
Jun 15 09:58:11 webserver sshd[12346]: Accepted password for user from 10.0.0.15 port 54321 ssh2
Jun 15 09:58:11 webserver sshd[12346]: pam_unix(sshd:session): session opened for user admin by (uid=0)
Jun 15 09:45:30 webserver apache2[12347]: 198.51.100.73 - - [15/Jun/2023:09:45:30 +0000] "GET /admin.php HTTP/1.1" 404 196 "-" "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
Jun 15 09:30:15 webserver apache2[12348]: 192.168.1.105 - - [15/Jun/2023:09:30:15 +0000] "GET /index.php HTTP/1.1" 500 728 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
Jun 15 09:30:15 webserver apache2[12348]: PHP Fatal error: Uncaught Error: Call to undefined function connect_db() in /var/www/html/index.php:25`}
                  </code>
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </DetailModal>
  );
};

export default DigitalTwinMonitorModal;
