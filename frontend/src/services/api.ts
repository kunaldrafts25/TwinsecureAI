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

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { toast } from 'react-toastify';

// Base API configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// For development, log the API URL
console.log('API URL:', API_URL);

export const createApiClient = (baseURL = API_URL): AxiosInstance => {
  const api = axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
    // Add timeout to prevent hanging requests
    timeout: 10000,
  });

  // Request interceptor for adding auth token
  api.interceptors.request.use(
    (config) => {
      console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`);

      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      console.error('Request error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor for handling errors
  api.interceptors.response.use(
    (response) => {
      console.log(`Response from ${response.config.url}: Status ${response.status}`);
      return response;
    },
    (error: AxiosError) => {
      const { response, request, config } = error;

      console.error('API Error:', {
        url: config?.url,
        method: config?.method,
        status: response?.status,
        data: response?.data,
      });

      if (response) {
        // Handle specific error codes
        switch (response.status) {
          case 401:
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem('access_token');
            window.location.href = '/auth';
            toast.error('Session expired. Please log in again.');
            break;
          case 403:
            toast.error('You do not have permission to perform this action.');
            break;
          case 404:
            toast.error('Resource not found.');
            break;
          case 422:
            toast.error('Validation error. Please check your input.');
            break;
          case 500:
            toast.error('Server error. Please try again later.');
            break;
          default:
            toast.error(`An error occurred: ${response.statusText}`);
        }
      } else if (request) {
        // Network error
        toast.error('Network error. Please check your connection.');
        console.error('Network Error:', error.message);
      } else {
        // Something happened in setting up the request
        toast.error('Error setting up request. Please try again.');
        console.error('Request Setup Error:', error.message);
      }

      return Promise.reject(error);
    }
  );

  return api;
};

// Create default API client
export const api = createApiClient();

// Generic API request function with error handling and fallback
export const apiRequest = async <T>(
  config: AxiosRequestConfig,
  fallbackData?: T
): Promise<T> => {
  try {
    const response = await api(config);
    return response.data;
  } catch (error) {
    // Error is already handled by the interceptor
    console.error('API request failed:', error);

    // If fallback data is provided, return it instead of throwing
    if (fallbackData !== undefined) {
      console.log('Using fallback data for failed request');
      return fallbackData;
    }

    throw error;
  }
};