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

import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Clock,
  Shield,
  ShieldCheck,
  AlertOctagon,
  FileText,
  Server,
  Users,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

// Mock data to match the screenshot
const mockData = {
  securityScore: 72,
  alerts: {
    critical: 12,
    high: 35,
    medium: 48
  },
  twinStatus: {
    activeTwins: 12,
    honeypots: 8,
    engagements: 24
  },
  compliance: {
    dpdp: { status: 'Compliant', compliant: true },
    gdpr: { status: 'Review needed', compliant: false },
    iso27001: { status: 'Compliant', compliant: true }
  },
  attackVectors: [
    { name: 'Brute Force', count: 42 },
    { name: 'SQL Injection', count: 27 },
    { name: 'Credential Theft', count: 18 }
  ],
  attackers: [
    { ip: '203.0.113.1', country: 'US', count: 35 },
    { ip: '198.51.100.2', country: 'RU', count: 28 },
    { ip: '192.0.2.3', country: 'CN', count: 22 }
  ],
  // Generate mock data for alert trends (last 30 days)
  alertTrends: Array.from({ length: 30 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (29 - i));
    return {
      date: date.toISOString().split('T')[0],
      critical: Math.floor(Math.random() * 5),
      high: Math.floor(Math.random() * 10),
      medium: Math.floor(Math.random() * 15),
      low: Math.floor(Math.random() * 8)
    };
  }),
  // Alert severity distribution for pie chart
  alertSeverityDistribution: [
    { name: 'Critical', value: 12, color: '#EF4444' },
    { name: 'High', value: 35, color: '#F59E0B' },
    { name: 'Medium', value: 48, color: '#FBBF24' },
    { name: 'Low', value: 25, color: '#10B981' },
    { name: 'Info', value: 7, color: '#3B82F6' }
  ]
};

const SecurityDashboardPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Simulate loading data
    setIsLoading(true);
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Security Dashboard</h1>
          <p className="text-muted-foreground">Overview of your organization's security posture</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Last updated: May 15, 2023, 01:00 PM</span>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Clock size={14} />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Top cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {/* Security Posture */}
        <Card
          className="col-span-1"
          title="Security Posture"
        >
          <div className="flex flex-col items-center">
            <div className="relative w-32 h-32">
              <svg viewBox="0 0 100 50" className="w-full">
                {/* Background arc */}
                <path
                  d="M 0,50 A 50,50 0 0,1 100,50"
                  fill="none"
                  stroke="#1f2937"
                  strokeWidth="10"
                  strokeLinecap="round"
                />
                {/* Foreground arc (colored based on score) */}
                <path
                  d="M 0,50 A 50,50 0 0,1 100,50"
                  fill="none"
                  stroke="#f59e0b"
                  strokeWidth="10"
                  strokeDasharray="157"
                  strokeDashoffset={157 - (157 * mockData.securityScore) / 100}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">{mockData.securityScore}</span>
                <span className="text-xs text-amber-500">High Risk</span>
              </div>
            </div>
            <p className="mt-2 text-sm text-center text-muted-foreground">
              Your security posture requires attention. Review critical alerts.
            </p>
          </div>
        </Card>

        {/* Active Alerts */}
        <Card
          className="col-span-1"
          title="Active Alerts"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertOctagon className="h-5 w-5 text-red-500" />
                <span>Critical</span>
              </div>
              <span className="font-bold text-red-500">{mockData.alerts.critical}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                <span>High</span>
              </div>
              <span className="font-bold text-amber-500">{mockData.alerts.high}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                <span>Medium</span>
              </div>
              <span className="font-bold text-yellow-500">{mockData.alerts.medium}</span>
            </div>
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View all alerts
              </Button>
            </div>
          </div>
        </Card>

        {/* Digital Twin Status */}
        <Card
          className="col-span-1"
          title="Digital Twin Status"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-blue-500" />
                <span>Active Twins</span>
              </div>
              <span className="font-bold">{mockData.twinStatus.activeTwins}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="h-5 w-5 text-blue-500" />
                <span>Honeypots</span>
              </div>
              <span className="font-bold">{mockData.twinStatus.honeypots}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-500" />
                <span>Engagements (24h)</span>
              </div>
              <span className="font-bold">{mockData.twinStatus.engagements}</span>
            </div>
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View details
              </Button>
            </div>
          </div>
        </Card>

        {/* Compliance Status */}
        <Card
          className="col-span-1"
          title="Compliance Status"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-gray-500" />
                <span>DPDP Act</span>
              </div>
              <span className={`font-bold ${mockData.compliance.dpdp.compliant ? 'text-green-500' : 'text-red-500'}`}>
                {mockData.compliance.dpdp.status}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-gray-500" />
                <span>GDPR</span>
              </div>
              <span className={`font-bold ${mockData.compliance.gdpr.compliant ? 'text-green-500' : 'text-amber-500'}`}>
                {mockData.compliance.gdpr.status}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-gray-500" />
                <span>ISO 27001</span>
              </div>
              <span className={`font-bold ${mockData.compliance.iso27001.compliant ? 'text-green-500' : 'text-red-500'}`}>
                {mockData.compliance.iso27001.status}
              </span>
            </div>
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View reports
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts section */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Alert Trends */}
        <Card
          className="col-span-1 lg:col-span-2"
          title="Alert Trends"
          subtitle="Last 30 days"
        >
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={mockData.alertTrends}
                margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
                stackOffset="sign"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).getDate().toString()}
                  fontSize={12}
                />
                <YAxis fontSize={12} />
                <Tooltip
                  formatter={(value, name) => [value, name.charAt(0).toUpperCase() + name.slice(1)]}
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                />
                <Bar dataKey="critical" stackId="a" fill="#EF4444" />
                <Bar dataKey="high" stackId="a" fill="#F59E0B" />
                <Bar dataKey="medium" stackId="a" fill="#FBBF24" />
                <Bar dataKey="low" stackId="a" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Alert Severity Distribution */}
        <Card
          className="col-span-1"
          title="Alert Severity Distribution"
        >
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={mockData.alertSeverityDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                  labelLine={false}
                >
                  {mockData.alertSeverityDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => [`${value} alerts`, '']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Bottom section */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Top Attack Vectors */}
        <Card
          title="Top Attack Vectors"
        >
          <div className="space-y-3 p-4">
            {mockData.attackVectors.map((vector, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                    {index + 1}
                  </span>
                  <span>{vector.name}</span>
                </div>
                <span className="font-medium">{vector.count} alerts</span>
              </div>
            ))}
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View all attack vectors
              </Button>
            </div>
          </div>
        </Card>

        {/* Top Attackers */}
        <Card
          title="Top Attackers"
        >
          <div className="space-y-3 p-4">
            {mockData.attackers.map((attacker, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-xs font-medium text-red-800 dark:bg-red-900/30 dark:text-red-400">
                    {index + 1}
                  </span>
                  <span>{attacker.ip}</span>
                  <span className="text-xs text-muted-foreground">{attacker.country}</span>
                </div>
                <span className="font-medium">{attacker.count} attempts</span>
              </div>
            ))}
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View all attackers
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SecurityDashboardPage;