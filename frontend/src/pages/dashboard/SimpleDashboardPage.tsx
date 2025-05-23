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

import React from 'react';
import { Shield, AlertTriangle, Server, Users } from 'lucide-react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';

/**
 * A simplified dashboard page that doesn't rely on complex data fetching
 * This is used as a fallback when the enhanced dashboard has issues
 */
const SimpleDashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Security Dashboard</h1>
          <p className="text-muted-foreground">Overview of your organization's security posture</p>
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
                  stroke="#10b981"
                  strokeWidth="10"
                  strokeDasharray="157"
                  strokeDashoffset={157 - (157 * 72) / 100}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">72</span>
                <span className="text-xs text-amber-500">
                  Medium Risk
                </span>
              </div>
            </div>
            <p className="mt-2 text-sm text-center text-muted-foreground">
              Your security posture needs improvement.
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
                <AlertTriangle className="h-5 w-5 text-red-500" />
                <span>Critical</span>
              </div>
              <span className="font-bold text-red-500">12</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                <span>High</span>
              </div>
              <span className="font-bold text-amber-500">35</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                <span>Medium</span>
              </div>
              <span className="font-bold text-yellow-500">48</span>
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
              <span className="font-bold">12</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="h-5 w-5 text-blue-500" />
                <span>Honeypots</span>
              </div>
              <span className="font-bold">8</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-500" />
                <span>Engagements (24h)</span>
              </div>
              <span className="font-bold">24</span>
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
              <span>DPDP Act</span>
              <span className="font-bold text-green-500">
                Compliant
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>GDPR</span>
              <span className="font-bold text-amber-500">
                Review needed
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>ISO 27001</span>
              <span className="font-bold text-green-500">
                Compliant
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Main content area */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Recent Alerts">
          <div className="p-4">
            <p className="text-center py-8">
              Welcome to TwinSecure AI Dashboard!
            </p>
            <p className="text-center">
              This is a simplified dashboard that loads without complex data fetching.
            </p>
            <div className="flex justify-center mt-4">
              <Button
                variant="primary"
                onClick={() => window.location.href = '/twin'}
              >
                Go to Digital Twin Management
              </Button>
            </div>
          </div>
        </Card>
        
        <Card title="System Status">
          <div className="p-4">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>Backend API</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Operational</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Database</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Operational</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Monitoring</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Operational</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SimpleDashboardPage;
