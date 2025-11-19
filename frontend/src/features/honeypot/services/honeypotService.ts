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
import { HoneypotData } from '../../../types';

export const honeypotService = {
  /**
   * Submit honeypot data for processing
   * This triggers enrichment, attack detection, and alerting
   */
  submitHoneypotData: async (data: HoneypotData): Promise<{ message: string }> => {
    try {
      const response = await api.post('/honeypot', data);
      return response.data;
    } catch (error) {
      console.error('Error submitting honeypot data:', error);
      throw error;
    }
  },
};










