import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Terminal, Shield, AlertTriangle } from 'lucide-react';
import { HoneypotEvent } from '../types';

const mockHoneypotEvents: HoneypotEvent[] = [
  {
    id: '1',
    timestamp: new Date().toISOString(),
    ip: '192.168.1.100',
    location: 'Beijing, China',
    protocol: 'SSH',
    port: 22,
    payload: 'root:password123',
    tags: ['bruteforce', 'ssh'],
    malwareSignature: 'MITRE-T1110'
  },
  {
    id: '2',
    timestamp: new Date().toISOString(),
    ip: '10.0.0.50',
    location: 'Moscow, Russia',
    protocol: 'HTTP',
    port: 80,
    payload: 'GET /wp-admin/install.php',
    tags: ['wordpress', 'scan']
  },
  // Add more mock events as needed
];

export const HoneypotPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
              <Terminal size={24} className="text-amber-600 dark:text-amber-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Active Sessions</h3>
              <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">12</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
              <Shield size={24} className="text-indigo-600 dark:text-indigo-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Captured Payloads</h3>
              <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">487</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <AlertTriangle size={24} className="text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Malware Detected</h3>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">23</p>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Live Honeypot Activity">
        <div className="space-y-4">
          {mockHoneypotEvents.map(event => (
            <div key={event.id} className="border-b border-slate-200 dark:border-slate-700/50 last:border-0 pb-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-slate-900 dark:text-white">{event.protocol}</span>
                    <span className="text-slate-400">|</span>
                    <span className="text-slate-600 dark:text-slate-300">{event.ip}</span>
                    <span className="text-slate-400">|</span>
                    <span className="text-slate-600 dark:text-slate-300">Port {event.port}</span>
                  </div>
                  <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {event.location} • {new Date(event.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="flex space-x-2">
                  {event.tags.map(tag => (
                    <Badge key={tag} variant="neutral">{tag}</Badge>
                  ))}
                </div>
              </div>
              <div className="mt-2">
                <pre className="bg-slate-50 dark:bg-slate-800 p-2 rounded text-sm font-mono overflow-x-auto">
                  {event.payload}
                </pre>
              </div>
              {event.malwareSignature && (
                <div className="mt-2">
                  <Badge variant="critical">Malware Signature: {event.malwareSignature}</Badge>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Top Attack Vectors">
          {/* Add attack vectors visualization */}
        </Card>
        <Card title="Geographic Distribution">
          {/* Add geographic distribution chart */}
        </Card>
      </div>
    </div>
  );
};