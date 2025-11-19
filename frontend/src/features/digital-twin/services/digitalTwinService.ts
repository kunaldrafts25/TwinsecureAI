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
import { DigitalTwin, DigitalTwinCreate, DigitalTwinUpdate, NetworkTopology, TwinEngagement } from '../../../types';

export const digitalTwinService = {
  /**
   * List all digital twins with optional filtering
   */
  listDigitalTwins: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    is_honeypot?: boolean;
  }): Promise<DigitalTwin[]> => {
    try {
      const response = await api.get('/digital-twins', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching digital twins:', error);
      throw error;
    }
  },

  /**
   * Get a specific digital twin by ID
   */
  getDigitalTwin: async (twinId: string): Promise<DigitalTwin> => {
    try {
      const response = await api.get(`/digital-twins/${twinId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching digital twin ${twinId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new digital twin
   */
  createDigitalTwin: async (data: DigitalTwinCreate): Promise<DigitalTwin> => {
    try {
      const response = await api.post('/digital-twins', data);
      return response.data;
    } catch (error) {
      console.error('Error creating digital twin:', error);
      throw error;
    }
  },

  /**
   * Update an existing digital twin
   */
  updateDigitalTwin: async (twinId: string, data: DigitalTwinUpdate): Promise<DigitalTwin> => {
    try {
      const response = await api.patch(`/digital-twins/${twinId}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating digital twin ${twinId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a digital twin
   */
  deleteDigitalTwin: async (twinId: string): Promise<void> => {
    try {
      await api.delete(`/digital-twins/${twinId}`);
    } catch (error) {
      console.error(`Error deleting digital twin ${twinId}:`, error);
      throw error;
    }
  },

  /**
   * Get network topology for a digital twin
   */
  getTopology: async (twinId: string): Promise<NetworkTopology[]> => {
    try {
      const response = await api.get(`/digital-twins/${twinId}/topology`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching topology for twin ${twinId}:`, error);
      throw error;
    }
  },

  /**
   * Create network topology entry
   */
  createTopology: async (data: any): Promise<NetworkTopology> => {
    try {
      const response = await api.post('/digital-twins/topology', data);
      return response.data;
    } catch (error) {
      console.error('Error creating topology:', error);
      throw error;
    }
  },

  /**
   * Get engagements for a digital twin
   */
  getEngagements: async (twinId: string): Promise<TwinEngagement[]> => {
    try {
      const response = await api.get(`/digital-twins/${twinId}/engagements`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching engagements for twin ${twinId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new engagement for a digital twin
   */
  createEngagement: async (twinId: string, data: any): Promise<TwinEngagement> => {
    try {
      const response = await api.post(`/digital-twins/${twinId}/engagements`, data);
      return response.data;
    } catch (error) {
      console.error(`Error creating engagement for twin ${twinId}:`, error);
      throw error;
    }
  },

  /**
   * Get network topology map
   */
  getNetworkTopology: async (): Promise<any> => {
    try {
      const response = await api.get('/digital-twins/network/topology');
      return response.data;
    } catch (error) {
      console.error('Error fetching network topology:', error);
      throw error;
    }
  },

  /**
   * Get network map for a specific twin
   */
  getNetworkMap: async (twinId: string): Promise<any> => {
    try {
      const response = await api.get(`/digital-twins/network/map/${twinId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching network map for twin ${twinId}:`, error);
      throw error;
    }
  },
};










