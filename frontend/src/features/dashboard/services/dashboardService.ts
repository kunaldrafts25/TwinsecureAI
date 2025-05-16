import { api, apiRequest } from '../../../services/api';
import { SecurityMetrics, SystemHealth } from '../../../types';
import { mockAlertTrendData, mockSecurityMetrics, mockSystemHealth, mockTTPFrequencyData } from '../../../services/mockData';

export const dashboardService = {
  // Get security metrics for dashboard
  getSecurityMetrics: async (): Promise<SecurityMetrics> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<SecurityMetrics>({
      //   method: 'GET',
      //   url: '/dashboard/security-metrics',
      // });

      // Mock implementation
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(mockSecurityMetrics);
        }, 500);
      });
    } catch (error) {
      console.error('Get security metrics error:', error);
      throw error;
    }
  },

  // Get system health status
  getSystemHealth: async (): Promise<SystemHealth> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<SystemHealth>({
      //   method: 'GET',
      //   url: '/system/health',
      // });

      // Mock implementation
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(mockSystemHealth);
        }, 300);
      });
    } catch (error) {
      console.error('Get system health error:', error);
      throw error;
    }
  },

  // Get alert trend data for charts
  getAlertTrends: async (days: number = 30): Promise<any[]> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<any[]>({
      //   method: 'GET',
      //   url: '/dashboard/alert-trends',
      //   params: { days },
      // });

      // Mock implementation
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(mockAlertTrendData);
        }, 700);
      });
    } catch (error) {
      console.error('Get alert trends error:', error);
      throw error;
    }
  },

  // Get MITRE TTP frequency data
  getTTPFrequency: async (): Promise<any[]> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<any[]>({
      //   method: 'GET',
      //   url: '/dashboard/ttp-frequency',
      // });

      // Mock implementation
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(mockTTPFrequencyData);
        }, 600);
      });
    } catch (error) {
      console.error('Get TTP frequency error:', error);
      throw error;
    }
  },
};