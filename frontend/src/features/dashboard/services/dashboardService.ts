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

import { api, apiRequest } from '../../../services/api';
import { SecurityMetrics, SystemHealth } from '../../../types';
import { mockAlertTrendData, mockSecurityMetrics, mockSystemHealth, mockTTPFrequencyData } from '../../../services/mockData';

export const dashboardService = {
  // Get security metrics for dashboard
  getSecurityMetrics: async (): Promise<SecurityMetrics> => {
    try {
      return await apiRequest<SecurityMetrics>({
        method: 'GET',
        url: '/dashboard/security-metrics',
      }, mockSecurityMetrics); // Fallback to mock data on error
    } catch (error) {
      console.error('Get security metrics error:', error);
      // Return mock data as fallback
      return mockSecurityMetrics;
    }
  },

  // Get system health status
  getSystemHealth: async (): Promise<SystemHealth> => {
    try {
      return await apiRequest<SystemHealth>({
        method: 'GET',
        url: '/system/health',
      }, mockSystemHealth); // Fallback to mock data on error
    } catch (error) {
      console.error('Get system health error:', error);
      // Return mock data as fallback
      return mockSystemHealth;
    }
  },

  // Get alert trend data for charts
  getAlertTrends: async (days: number = 30): Promise<any[]> => {
    try {
      return await apiRequest<any[]>({
        method: 'GET',
        url: '/dashboard/alert-trends',
        params: { days },
      }, mockAlertTrendData); // Fallback to mock data on error
    } catch (error) {
      console.error('Get alert trends error:', error);
      // Return mock data as fallback
      return mockAlertTrendData;
    }
  },

  // Get MITRE TTP frequency data
  getTTPFrequency: async (): Promise<any[]> => {
    try {
      // Note: This endpoint may need to be implemented in the backend
      // For now, using mock data with API call attempt
      return await apiRequest<any[]>({
        method: 'GET',
        url: '/dashboard/ttp-frequency',
      }, mockTTPFrequencyData); // Fallback to mock data on error
    } catch (error) {
      console.error('Get TTP frequency error:', error);
      // Return mock data as fallback
      return mockTTPFrequencyData;
    }
  },
};