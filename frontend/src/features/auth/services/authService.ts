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
import { AuthResponse, LoginRequest, User } from '../../../types';

export const authService = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      console.log('Login attempt with credentials:', credentials.email);
      console.log('API URL:', import.meta.env.VITE_API_URL);

      let response;

      // Use OAuth2 format expected by the backend
      const formData = new URLSearchParams();
      formData.append('username', credentials.email); // Backend expects 'username' for email
      formData.append('password', credentials.password);

      // Make the API call to the login endpoint
      response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log('Login response:', response.data);

      // Store the token immediately so subsequent requests include it
      localStorage.setItem('access_token', response.data.access_token);

      // Get the user data after successful login
      const userData = await authService.getCurrentUser();
      console.log('User data retrieved:', userData);

      // Return combined response with token and user data
      return {
        access_token: response.data.access_token,
        token_type: response.data.token_type,
        user: userData,
      };
    } catch (error) {
      console.error('Login error:', error);
      // Enhanced error logging
      if (axios.isAxiosError(error)) {
        console.error('Request failed with status:', error.response?.status);
        console.error('Response data:', error.response?.data);
        console.error('Request config:', error.config);
      }
      // Ensure token is cleared if login flow fails after storing it
      localStorage.removeItem('access_token');
      throw error;
    }
  },

  logout: async (): Promise<void> => {
    try {
      console.log('Logging out user');

      // Call the logout endpoint
      await api.post('/auth/logout');

      console.log('Logout successful');
    } catch (error) {
      console.error('Logout error:', error);
      // Even if the server-side logout fails, we still want to clear local storage
      // as JWT is stateless and the main logout action happens client-side
    }
  },

  getCurrentUser: async (): Promise<User> => {
    try {
      console.log('Fetching current user data');

      // Get the current user from the backend
      const response = await api.get('/auth/me');
      console.log('Current user data response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  },
};