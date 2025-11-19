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
import { Alert, AlertFilters } from '../../../types';
import { mockAlerts, generateMockAlerts } from '../../../services/mockData';

export const alertService = {
  // Get all alerts with optional filtering
  getAlerts: async (filters?: AlertFilters): Promise<Alert[]> => {
    try {
      // Build query parameters from filters
      const params: Record<string, any> = {};
      if (filters) {
        if (filters.alert_type) params.alert_type = filters.alert_type;
        if (filters.severity) params.severity = filters.severity;
        if (filters.status) params.status = filters.status;
        if (filters.source_ip) params.source_ip = filters.source_ip;
        if (filters.honeypot_id) params.honeypot_id = filters.honeypot_id;
        if (filters.date_from) params.date_from = filters.date_from;
        if (filters.date_to) params.date_to = filters.date_to;
      }

      return await apiRequest<Alert[]>({
        method: 'GET',
        url: '/alerts',
        params,
      }, mockAlerts); // Fallback to mock data on error
    } catch (error) {
      console.error('Get alerts error:', error);
      // Return mock data as fallback
      return mockAlerts;
    }
  },

  // Get a single alert by ID
  getAlertById: async (id: string): Promise<Alert> => {
    try {
      return await apiRequest<Alert>({
        method: 'GET',
        url: `/alerts/${id}`,
      });
    } catch (error) {
      console.error(`Get alert ${id} error:`, error);
      // Try to find in mock data as fallback
      const alert = mockAlerts.find((a) => a.id === id);
      if (alert) {
        return alert;
      }
      throw error;
    }
  },

  // Update an alert
  updateAlert: async (id: string, data: Partial<Alert>): Promise<Alert> => {
    try {
      return await apiRequest<Alert>({
        method: 'PATCH',
        url: `/alerts/${id}`,
        data,
      });
    } catch (error) {
      console.error(`Update alert ${id} error:`, error);
      throw error;
    }
  },

  // Create a new alert
  createAlert: async (data: Partial<Alert>): Promise<Alert> => {
    try {
      return await apiRequest<Alert>({
        method: 'POST',
        url: '/alerts',
        data,
      });
    } catch (error) {
      console.error('Create alert error:', error);
      throw error;
    }
  },

  // Delete an alert
  deleteAlert: async (id: string): Promise<void> => {
    try {
      await apiRequest<void>({
        method: 'DELETE',
        url: `/alerts/${id}`,
      });
    } catch (error) {
      console.error(`Delete alert ${id} error:`, error);
      throw error;
    }
  },
};