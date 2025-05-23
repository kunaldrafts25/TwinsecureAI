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

import { create } from 'zustand';
import { authService } from '../services/authService';
import { LoginRequest, User } from '../../../types';
import { toast } from 'react-toastify';
import axios from 'axios';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isAuthenticated: false,
  isLoading: false,
  user: null,

  login: async (credentials: LoginRequest) => {
    set({ isLoading: true });
    try {
      console.log('Auth store: Attempting login with credentials', credentials.email);
      const response = await authService.login(credentials);
      console.log('Auth store: Login successful, response:', response);

      // Store token in local storage
      localStorage.setItem('access_token', response.access_token);

      set({
        isAuthenticated: true,
        user: response.user,
        isLoading: false,
      });

      toast.success(`Welcome, ${response.user.full_name}!`);
    } catch (error) {
      console.error('Auth store: Login error details:', error);
      set({ isLoading: false });

      // More specific error messages based on the error type
      if (axios.isAxiosError(error)) {
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          if (error.response.status === 401) {
            toast.error('Invalid credentials. Please check your email and password.');
          } else if (error.response.status === 404) {
            toast.error('Authentication service not found. Please contact support.');
          } else if (error.response.status === 500) {
            toast.error('Server error. Please try again later.');
          } else {
            toast.error(`Login failed: ${error.response.data?.detail || 'Unknown error'}`);
          }
        } else if (error.request) {
          // The request was made but no response was received
          toast.error('No response from server. Please check your connection.');
        } else {
          // Something happened in setting up the request that triggered an Error
          toast.error('Login request failed. Please try again.');
        }
      } else {
        toast.error('Login failed. Please check your credentials.');
      }

      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await authService.logout();

      // Remove token from local storage
      localStorage.removeItem('access_token');

      set({
        isAuthenticated: false,
        user: null,
        isLoading: false,
      });

      toast.info('You have been logged out.');
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.log('No token found in localStorage');
      set({ isAuthenticated: false, user: null });
      return;
    }

    console.log('Token found, checking validity');
    set({ isLoading: true });
    try {
      const user = await authService.getCurrentUser();
      console.log('User authenticated successfully:', user);
      set({
        isAuthenticated: true,
        user,
        isLoading: false,
      });
    } catch (error) {
      console.error('Token validation failed:', error);

      // If token is invalid, clear it
      localStorage.removeItem('access_token');
      set({
        isAuthenticated: false,
        user: null,
        isLoading: false,
      });

      // Don't show error toast during initial auth check
      // as this is a normal flow when the token is expired
    }
  },
}));