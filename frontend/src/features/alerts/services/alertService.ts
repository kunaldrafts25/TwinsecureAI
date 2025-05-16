import { api, apiRequest } from '../../../services/api';
import { Alert, AlertFilters } from '../../../types';
import { mockAlerts, generateMockAlerts } from '../../../services/mockData';

export const alertService = {
  // Get all alerts with optional filtering
  getAlerts: async (filters?: AlertFilters): Promise<Alert[]> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<Alert[]>({
      //   method: 'GET',
      //   url: '/alerts',
      //   params: filters,
      // });

      // Mock implementation with filtering
      return new Promise((resolve) => {
        setTimeout(() => {
          let filteredAlerts = [...mockAlerts];
          
          if (filters) {
            if (filters.alert_type) {
              filteredAlerts = filteredAlerts.filter(
                (alert) => alert.alert_type.toLowerCase().includes(filters.alert_type!.toLowerCase())
              );
            }
            
            if (filters.severity) {
              filteredAlerts = filteredAlerts.filter(
                (alert) => alert.severity === filters.severity
              );
            }
            
            if (filters.status) {
              filteredAlerts = filteredAlerts.filter(
                (alert) => alert.status === filters.status
              );
            }
            
            if (filters.source_ip) {
              filteredAlerts = filteredAlerts.filter(
                (alert) => alert.source_ip.includes(filters.source_ip!)
              );
            }
            
            if (filters.honeypot_id) {
              filteredAlerts = filteredAlerts.filter(
                (alert) => alert.honeypot_id === filters.honeypot_id
              );
            }
            
            if (filters.date_from) {
              const fromDate = new Date(filters.date_from).getTime();
              filteredAlerts = filteredAlerts.filter(
                (alert) => new Date(alert.created_at).getTime() >= fromDate
              );
            }
            
            if (filters.date_to) {
              const toDate = new Date(filters.date_to).getTime();
              filteredAlerts = filteredAlerts.filter(
                (alert) => new Date(alert.created_at).getTime() <= toDate
              );
            }
          }
          
          resolve(filteredAlerts);
        }, 500);
      });
    } catch (error) {
      console.error('Get alerts error:', error);
      throw error;
    }
  },

  // Get a single alert by ID
  getAlertById: async (id: string): Promise<Alert> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<Alert>({
      //   method: 'GET',
      //   url: `/alerts/${id}`,
      // });

      // Mock implementation
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const alert = mockAlerts.find((a) => a.id === id);
          if (alert) {
            resolve(alert);
          } else {
            reject(new Error('Alert not found'));
          }
        }, 300);
      });
    } catch (error) {
      console.error(`Get alert ${id} error:`, error);
      throw error;
    }
  },

  // Update an alert
  updateAlert: async (id: string, data: Partial<Alert>): Promise<Alert> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<Alert>({
      //   method: 'PATCH',
      //   url: `/alerts/${id}`,
      //   data,
      // });

      // Mock implementation
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const alertIndex = mockAlerts.findIndex((a) => a.id === id);
          if (alertIndex !== -1) {
            const updatedAlert = {
              ...mockAlerts[alertIndex],
              ...data,
              updated_at: new Date().toISOString(),
            };
            mockAlerts[alertIndex] = updatedAlert;
            resolve(updatedAlert);
          } else {
            reject(new Error('Alert not found'));
          }
        }, 300);
      });
    } catch (error) {
      console.error(`Update alert ${id} error:`, error);
      throw error;
    }
  },

  // Create a new alert
  createAlert: async (data: Partial<Alert>): Promise<Alert> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<Alert>({
      //   method: 'POST',
      //   url: '/alerts',
      //   data,
      // });

      // Mock implementation
      return new Promise((resolve) => {
        setTimeout(() => {
          const newAlert = generateMockAlerts(1)[0];
          const mergedAlert = { ...newAlert, ...data };
          mockAlerts.unshift(mergedAlert);
          resolve(mergedAlert);
        }, 300);
      });
    } catch (error) {
      console.error('Create alert error:', error);
      throw error;
    }
  },

  // Delete an alert
  deleteAlert: async (id: string): Promise<void> => {
    try {
      // In a real app, this would call the API
      // return await apiRequest<void>({
      //   method: 'DELETE',
      //   url: `/alerts/${id}`,
      // });

      // Mock implementation
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          const alertIndex = mockAlerts.findIndex((a) => a.id === id);
          if (alertIndex !== -1) {
            mockAlerts.splice(alertIndex, 1);
            resolve();
          } else {
            reject(new Error('Alert not found'));
          }
        }, 300);
      });
    } catch (error) {
      console.error(`Delete alert ${id} error:`, error);
      throw error;
    }
  },
};