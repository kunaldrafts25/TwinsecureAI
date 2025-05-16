import { create } from 'zustand';
import { alertService } from '../services/alertService';
import { Alert, AlertFilters } from '../../../types';
import { toast } from 'react-toastify';

interface AlertState {
  alerts: Alert[];
  selectedAlert: Alert | null;
  isLoading: boolean;
  filters: AlertFilters;
  totalAlerts: number;
  
  getAlerts: (filters?: AlertFilters) => Promise<void>;
  getAlertById: (id: string) => Promise<void>;
  updateAlert: (id: string, data: Partial<Alert>) => Promise<void>;
  createAlert: (data: Partial<Alert>) => Promise<void>;
  deleteAlert: (id: string) => Promise<void>;
  setFilters: (filters: AlertFilters) => void;
  clearFilters: () => void;
  setSelectedAlert: (alert: Alert | null) => void;
}

export const useAlertStore = create<AlertState>((set, get) => ({
  alerts: [],
  selectedAlert: null,
  isLoading: false,
  filters: {},
  totalAlerts: 0,
  
  getAlerts: async (filters?: AlertFilters) => {
    set({ isLoading: true });
    try {
      const appliedFilters = filters || get().filters;
      const alerts = await alertService.getAlerts(appliedFilters);
      set({
        alerts,
        totalAlerts: alerts.length,
        isLoading: false,
        filters: appliedFilters,
      });
    } catch (error) {
      set({ isLoading: false });
      toast.error('Failed to load alerts');
    }
  },
  
  getAlertById: async (id: string) => {
    set({ isLoading: true });
    try {
      const alert = await alertService.getAlertById(id);
      set({
        selectedAlert: alert,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      toast.error('Failed to load alert details');
    }
  },
  
  updateAlert: async (id: string, data: Partial<Alert>) => {
    set({ isLoading: true });
    try {
      const updatedAlert = await alertService.updateAlert(id, data);
      
      // Update the alert in the alerts array
      set((state) => ({
        alerts: state.alerts.map((alert) => 
          alert.id === id ? updatedAlert : alert
        ),
        selectedAlert: state.selectedAlert?.id === id ? updatedAlert : state.selectedAlert,
        isLoading: false,
      }));
      
      toast.success('Alert updated successfully');
    } catch (error) {
      set({ isLoading: false });
      toast.error('Failed to update alert');
    }
  },
  
  createAlert: async (data: Partial<Alert>) => {
    set({ isLoading: true });
    try {
      const newAlert = await alertService.createAlert(data);
      
      // Add the new alert to the alerts array
      set((state) => ({
        alerts: [newAlert, ...state.alerts],
        totalAlerts: state.totalAlerts + 1,
        isLoading: false,
      }));
      
      toast.success('Alert created successfully');
    } catch (error) {
      set({ isLoading: false });
      toast.error('Failed to create alert');
    }
  },
  
  deleteAlert: async (id: string) => {
    set({ isLoading: true });
    try {
      await alertService.deleteAlert(id);
      
      // Remove the alert from the alerts array
      set((state) => ({
        alerts: state.alerts.filter((alert) => alert.id !== id),
        selectedAlert: state.selectedAlert?.id === id ? null : state.selectedAlert,
        totalAlerts: state.totalAlerts - 1,
        isLoading: false,
      }));
      
      toast.success('Alert deleted successfully');
    } catch (error) {
      set({ isLoading: false });
      toast.error('Failed to delete alert');
    }
  },
  
  setFilters: (filters: AlertFilters) => {
    set({ filters });
  },
  
  clearFilters: () => {
    set({ filters: {} });
  },
  
  setSelectedAlert: (alert: Alert | null) => {
    set({ selectedAlert: alert });
  },
}));