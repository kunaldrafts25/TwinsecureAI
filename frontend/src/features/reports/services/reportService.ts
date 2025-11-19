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
import { Report, ReportFilters, ReportGenerationParams } from '../../../types';

export const reportService = {
  /**
   * List all reports with optional filtering
   */
  listReports: async (filters?: ReportFilters): Promise<Report[]> => {
    try {
      const params: Record<string, any> = {};
      if (filters) {
        if (filters.report_type) params.report_type = filters.report_type;
        if (filters.date_from) params.date_from = filters.date_from;
        if (filters.date_to) params.date_to = filters.date_to;
      }

      const response = await api.get('/reports', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching reports:', error);
      throw error;
    }
  },

  /**
   * Get a specific report by ID
   */
  getReport: async (reportId: string): Promise<Report> => {
    try {
      const response = await api.get(`/reports/${reportId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching report ${reportId}:`, error);
      throw error;
    }
  },

  /**
   * Download a report PDF file
   */
  downloadReport: async (reportId: string): Promise<Blob> => {
    try {
      const response = await api.get(`/reports/${reportId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error(`Error downloading report ${reportId}:`, error);
      throw error;
    }
  },

  /**
   * Trigger report generation (superuser only)
   */
  generateReport: async (params: ReportGenerationParams): Promise<{ message: string }> => {
    try {
      const response = await api.post('/reports/generate', params);
      return response.data;
    } catch (error) {
      console.error('Error triggering report generation:', error);
      throw error;
    }
  },
};










