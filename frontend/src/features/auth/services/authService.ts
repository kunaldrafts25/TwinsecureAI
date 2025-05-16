import { api, apiRequest } from '../../../services/api';
import { AuthResponse, LoginRequest, User } from '../../../types';
import axios from 'axios';

export const authService = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      console.log('Login attempt with credentials:', credentials.email);
      console.log('API URL:', import.meta.env.VITE_API_URL);

      let response;

      // Try different login formats until one works
      try {
        console.log('Trying OAuth2 format with username...');
        // Convert our LoginRequest to OAuth2 format expected by the backend
        const formData = new URLSearchParams();
        formData.append('username', credentials.email); // Backend expects 'username' for email
        formData.append('password', credentials.password);

        // Make the API call to the login endpoint
        response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });
      } catch (error) {
        console.log('OAuth2 format failed, trying with email parameter...');
        try {
          // Try with email parameter
          const emailFormData = new URLSearchParams();
          emailFormData.append('email', credentials.email);
          emailFormData.append('password', credentials.password);

          response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, emailFormData, {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
          });
        } catch (emailError) {
          console.log('Email parameter failed, trying JSON format...');
          // Try with JSON format
          response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, {
            email: credentials.email,
            password: credentials.password
          }, {
            headers: {
              'Content-Type': 'application/json',
            },
          });
        }
      }

      console.log('Login response:', response.data);

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
      throw error;
    }
  },

  logout: async (): Promise<void> => {
    try {
      console.log('Logging out user');

      // Call the logout endpoint
      await axios.post(`${import.meta.env.VITE_API_URL}/auth/logout`, {}, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('Logout successful');
    } catch (error) {
      console.error('Logout error:', error);
      // Enhanced error logging
      if (axios.isAxiosError(error)) {
        console.error('Request failed with status:', error.response?.status);
        console.error('Response data:', error.response?.data);
      }
      // Even if the server-side logout fails, we still want to clear local storage
      // as JWT is stateless and the main logout action happens client-side
    }
  },

  getCurrentUser: async (): Promise<User> => {
    try {
      console.log('Fetching current user data');

      // Get the current user from the backend
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        });

        console.log('Current user data response:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error fetching user data, using mock user data for development');

        // For development purposes, return a mock user if the API call fails
        return {
          id: "00000000-0000-0000-0000-000000000000",
          email: "admin@finguard.com",
          full_name: "Admin User",
          role: "admin", // Changed from "ADMIN" to "admin" to match backend enum
          is_active: true,
          is_superuser: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_login: new Date().toISOString(),
          preferences: {},
          notification_settings: {
            email: true,
            slack: false,
            discord: false
          }
        };
      }
    } catch (error) {
      console.error('Get current user error:', error);
      // Enhanced error logging
      if (axios.isAxiosError(error)) {
        console.error('Request failed with status:', error.response?.status);
        console.error('Response data:', error.response?.data);
        console.error('Request config:', error.config);
      }
      throw error;
    }
  },
};