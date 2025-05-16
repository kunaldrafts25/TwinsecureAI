import { create } from 'zustand';
import { dashboardService } from '../services/dashboardService';
import { SecurityMetrics, SystemHealth } from '../../../types';
import { toast } from 'react-toastify';

interface DashboardState {
  securityMetrics: SecurityMetrics | null;
  systemHealth: SystemHealth | null;
  alertTrends: any[];
  ttpFrequency: any[];
  isLoading: boolean;
  
  getSecurityMetrics: () => Promise<void>;
  getSystemHealth: () => Promise<void>;
  getAlertTrends: (days?: number) => Promise<void>;
  getTTPFrequency: () => Promise<void>;
  loadDashboardData: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  securityMetrics: null,
  systemHealth: null,
  alertTrends: [],
  ttpFrequency: [],
  isLoading: false,
  
  getSecurityMetrics: async () => {
    try {
      const metrics = await dashboardService.getSecurityMetrics();
      set({ securityMetrics: metrics });
    } catch (error) {
      toast.error('Failed to load security metrics');
    }
  },
  
  getSystemHealth: async () => {
    try {
      const health = await dashboardService.getSystemHealth();
      set({ systemHealth: health });
    } catch (error) {
      toast.error('Failed to load system health status');
    }
  },
  
  getAlertTrends: async (days = 30) => {
    try {
      const trends = await dashboardService.getAlertTrends(days);
      set({ alertTrends: trends });
    } catch (error) {
      toast.error('Failed to load alert trends');
    }
  },
  
  getTTPFrequency: async () => {
    try {
      const frequency = await dashboardService.getTTPFrequency();
      set({ ttpFrequency: frequency });
    } catch (error) {
      toast.error('Failed to load MITRE TTP frequency data');
    }
  },
  
  loadDashboardData: async () => {
    set({ isLoading: true });
    try {
      // Load all dashboard data in parallel
      await Promise.all([
        get().getSecurityMetrics(),
        get().getSystemHealth(),
        get().getAlertTrends(),
        get().getTTPFrequency(),
      ]);
      set({ isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      toast.error('Failed to load dashboard data');
    }
  },
}));