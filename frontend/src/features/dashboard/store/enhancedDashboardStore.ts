import { create } from 'zustand';
import { toast } from 'react-toastify';
import { dashboardApiService } from '../services/dashboardApiService';
import {
  SecurityMetrics,
  SystemHealth,
  AlertTrend,
  AlertSeverityDistribution,
  AttackVector,
  Attacker,
  ComplianceStatus,
  DigitalTwinStatus,
  DashboardFilters
} from '../../../types';

// Mock data for fallback when API fails
import {
  mockSecurityMetrics,
  mockAlertTrendData,
  mockAlertSeverityDistribution,
  mockAttackVectors,
  mockAttackers,
  mockComplianceStatus,
  mockDigitalTwinStatus
} from '../../../services/mockData';

interface EnhancedDashboardState {
  // Data
  securityMetrics: SecurityMetrics | null;
  systemHealth: SystemHealth | null;
  alertTrends: AlertTrend[];
  alertSeverityDistribution: AlertSeverityDistribution[];
  topAttackVectors: AttackVector[];
  topAttackers: Attacker[];
  complianceStatus: ComplianceStatus | null;
  digitalTwinStatus: DigitalTwinStatus | null;

  // UI state
  isLoading: boolean;
  lastUpdated: Date | null;
  filters: DashboardFilters;
  refreshIntervalId: number | null;

  // Drill-down state
  selectedAlert: string | null;
  selectedAttacker: string | null;
  selectedAttackVector: string | null;

  // Actions
  setFilters: (filters: Partial<DashboardFilters>) => void;
  refreshData: () => Promise<void>;
  startAutoRefresh: () => void;
  stopAutoRefresh: () => void;

  // Data fetching actions
  fetchSecurityMetrics: () => Promise<void>;
  fetchAlertTrends: () => Promise<void>;
  fetchAlertSeverityDistribution: () => Promise<void>;
  fetchTopAttackVectors: () => Promise<void>;
  fetchTopAttackers: () => Promise<void>;
  fetchComplianceStatus: () => Promise<void>;
  fetchDigitalTwinStatus: () => Promise<void>;

  // Drill-down actions
  setSelectedAlert: (alertId: string | null) => void;
  setSelectedAttacker: (ip: string | null) => void;
  setSelectedAttackVector: (vector: string | null) => void;
}

// Helper to get days from time range
const getDaysFromTimeRange = (timeRange: DashboardFilters['timeRange']): number => {
  switch (timeRange) {
    case '24h': return 1;
    case '7d': return 7;
    case '30d': return 30;
    case '90d': return 90;
    case 'custom': return 30; // Default to 30 days for custom range
    default: return 30;
  }
};

export const useEnhancedDashboardStore = create<EnhancedDashboardState>((set, get) => ({
  // Initial data state
  securityMetrics: null,
  systemHealth: null,
  alertTrends: [],
  alertSeverityDistribution: [],
  topAttackVectors: [],
  topAttackers: [],
  complianceStatus: null,
  digitalTwinStatus: null,

  // Initial UI state
  isLoading: false,
  lastUpdated: null,
  filters: {
    timeRange: '30d',
    refreshInterval: null,
  },
  refreshIntervalId: null,

  // Initial drill-down state
  selectedAlert: null,
  selectedAttacker: null,
  selectedAttackVector: null,

  // Actions
  setFilters: (filters) => {
    set((state) => ({
      filters: { ...state.filters, ...filters }
    }));

    // If time range changed, refresh data
    if (filters.timeRange) {
      get().refreshData();
    }

    // Handle auto-refresh changes
    if (filters.refreshInterval !== undefined) {
      const { refreshIntervalId } = get();

      // Clear existing interval if any
      if (refreshIntervalId !== null) {
        window.clearInterval(refreshIntervalId);
        set({ refreshIntervalId: null });
      }

      // Set up new interval if needed
      if (filters.refreshInterval !== null) {
        const id = window.setInterval(() => {
          get().refreshData();
        }, filters.refreshInterval * 1000);
        set({ refreshIntervalId: id });
      }
    }
  },

  refreshData: async () => {
    set({ isLoading: true });

    try {
      // Get days from time range
      const { filters } = get();
      const days = getDaysFromTimeRange(filters.timeRange);

      // Fetch all data in parallel
      await Promise.all([
        get().fetchSecurityMetrics(),
        get().fetchAlertTrends(),
        get().fetchAlertSeverityDistribution(),
        get().fetchTopAttackVectors(),
        get().fetchTopAttackers(),
        get().fetchComplianceStatus(),
        get().fetchDigitalTwinStatus(),
      ]);

      set({
        isLoading: false,
        lastUpdated: new Date()
      });
    } catch (error) {
      console.error('Error refreshing dashboard data:', error);
      toast.error('Failed to refresh dashboard data');
      set({ isLoading: false });
    }
  },

  startAutoRefresh: () => {
    const { refreshIntervalId, filters } = get();

    // Clear existing interval if any
    if (refreshIntervalId !== null) {
      window.clearInterval(refreshIntervalId);
    }

    // Default to 30 seconds if not set
    const interval = filters.refreshInterval || 30;

    // Set up new interval
    const id = window.setInterval(() => {
      get().refreshData();
    }, interval * 1000);

    set({
      refreshIntervalId: id,
      filters: { ...filters, refreshInterval: interval }
    });
  },

  stopAutoRefresh: () => {
    const { refreshIntervalId, filters } = get();

    if (refreshIntervalId !== null) {
      window.clearInterval(refreshIntervalId);
      set({
        refreshIntervalId: null,
        filters: { ...filters, refreshInterval: null }
      });
    }
  },

  // Data fetching actions
  fetchSecurityMetrics: async () => {
    try {
      const metrics = await dashboardApiService.getSecurityMetrics();
      set({ securityMetrics: metrics });
      return metrics;
    } catch (error) {
      console.error('Error fetching security metrics:', error);
      // Fall back to mock data in development
      if (process.env.NODE_ENV === 'development') {
        set({ securityMetrics: mockSecurityMetrics });
      }
      return null;
    }
  },

  fetchAlertTrends: async () => {
    try {
      const { filters } = get();
      const days = getDaysFromTimeRange(filters.timeRange);
      const trends = await dashboardApiService.getAlertTrends(days);
      set({ alertTrends: trends });
      return trends;
    } catch (error) {
      console.error('Error fetching alert trends:', error);
      // Fall back to mock data in development
      if (process.env.NODE_ENV === 'development') {
        set({ alertTrends: mockAlertTrendData });
      }
      return [];
    }
  },

  fetchAlertSeverityDistribution: async () => {
    try {
      const distribution = await dashboardApiService.getAlertSeverityDistribution();
      set({ alertSeverityDistribution: distribution });
      return distribution;
    } catch (error) {
      console.error('Error fetching alert severity distribution:', error);
      // Fall back to mock data in development
      if (process.env.NODE_ENV === 'development') {
        set({ alertSeverityDistribution: mockAlertSeverityDistribution });
      }
      return [];
    }
  },

  fetchTopAttackVectors: async () => {
    try {
      const vectors = await dashboardApiService.getTopAttackVectors();
      set({ topAttackVectors: vectors });
      return vectors;
    } catch (error) {
      console.error('Error fetching top attack vectors:', error);
      // Fall back to mock data in development
      if (process.env.NODE_ENV === 'development') {
        set({ topAttackVectors: mockAttackVectors });
      }
      return [];
    }
  },

  fetchTopAttackers: async () => {
    try {
      const attackers = await dashboardApiService.getTopAttackers();
      set({ topAttackers: attackers });
      return attackers;
    } catch (error) {
      console.error('Error fetching top attackers:', error);
      // Fall back to mock data in development
      if (process.env.NODE_ENV === 'development') {
        set({ topAttackers: mockAttackers });
      }
      return [];
    }
  },

  fetchComplianceStatus: async () => {
    try {
      const status = await dashboardApiService.getComplianceStatus();
      set({ complianceStatus: status });
      return status;
    } catch (error) {
      console.error('Error fetching compliance status:', error);
      // Fall back to mock data in development
      if (process.env.NODE_ENV === 'development') {
        set({ complianceStatus: mockComplianceStatus });
      }
      return null;
    }
  },

  fetchDigitalTwinStatus: async () => {
    try {
      const status = await dashboardApiService.getDigitalTwinStatus();
      set({ digitalTwinStatus: status });
      return status;
    } catch (error) {
      console.error('Error fetching digital twin status:', error);
      // Fall back to mock data in development
      if (process.env.NODE_ENV === 'development') {
        set({ digitalTwinStatus: mockDigitalTwinStatus });
      }
      return null;
    }
  },

  // Drill-down actions
  setSelectedAlert: (alertId) => {
    set({ selectedAlert: alertId });
  },

  setSelectedAttacker: (ip) => {
    set({ selectedAttacker: ip });
  },

  setSelectedAttackVector: (vector) => {
    set({ selectedAttackVector: vector });
  }
}));
