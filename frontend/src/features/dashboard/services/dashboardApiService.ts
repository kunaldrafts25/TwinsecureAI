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

import { api } from '../../../services/api';
import { 
  SecurityMetrics, 
  SystemHealth, 
  AlertTrend, 
  AlertSeverityDistribution,
  AttackVector,
  Attacker,
  ComplianceStatus,
  DigitalTwinStatus
} from '../../../types';

/**
 * Service for fetching dashboard-related data from the API
 */
export const dashboardApiService = {
  /**
   * Get security metrics for dashboard
   */
  getSecurityMetrics: async (): Promise<SecurityMetrics> => {
    try {
      const response = await api.get('/api/v1/dashboard/security-metrics');
      return response.data;
    } catch (error) {
      console.error('Error fetching security metrics:', error);
      throw error;
    }
  },

  /**
   * Get system health status
   */
  getSystemHealth: async (): Promise<SystemHealth> => {
    try {
      const response = await api.get('/api/v1/system/health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      throw error;
    }
  },

  /**
   * Get alert trends for a specific time period
   */
  getAlertTrends: async (days: number = 30): Promise<AlertTrend[]> => {
    try {
      const response = await api.get(`/api/v1/alerts/trends?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching alert trends:', error);
      throw error;
    }
  },

  /**
   * Get alert severity distribution
   */
  getAlertSeverityDistribution: async (): Promise<AlertSeverityDistribution[]> => {
    try {
      const response = await api.get('/api/v1/alerts/distribution');
      return response.data;
    } catch (error) {
      console.error('Error fetching alert severity distribution:', error);
      throw error;
    }
  },

  /**
   * Get top attack vectors
   */
  getTopAttackVectors: async (limit: number = 5): Promise<AttackVector[]> => {
    try {
      const response = await api.get(`/api/v1/alerts/attack-vectors?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching top attack vectors:', error);
      throw error;
    }
  },

  /**
   * Get top attackers
   */
  getTopAttackers: async (limit: number = 5): Promise<Attacker[]> => {
    try {
      const response = await api.get(`/api/v1/alerts/attackers?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching top attackers:', error);
      throw error;
    }
  },

  /**
   * Get compliance status
   */
  getComplianceStatus: async (): Promise<ComplianceStatus> => {
    try {
      const response = await api.get('/api/v1/reports/compliance');
      return response.data;
    } catch (error) {
      console.error('Error fetching compliance status:', error);
      throw error;
    }
  },

  /**
   * Get digital twin status
   */
  getDigitalTwinStatus: async (): Promise<DigitalTwinStatus> => {
    try {
      const response = await api.get('/api/v1/honeypot/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching digital twin status:', error);
      throw error;
    }
  },

  /**
   * Get all dashboard data in a single call
   */
  getDashboardData: async (days: number = 30): Promise<{
    securityMetrics: SecurityMetrics;
    alertTrends: AlertTrend[];
    alertSeverityDistribution: AlertSeverityDistribution[];
    topAttackVectors: AttackVector[];
    topAttackers: Attacker[];
    complianceStatus: ComplianceStatus;
    digitalTwinStatus: DigitalTwinStatus;
  }> => {
    try {
      const response = await api.get(`/api/v1/dashboard?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }
};
