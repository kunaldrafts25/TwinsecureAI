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

/**
 * Debug utilities for troubleshooting application issues
 */

/**
 * Logs user authentication information to the console
 * This is useful for debugging role-based access issues
 */
export const logUserAuthInfo = () => {
  try {
    // Get token from localStorage
    const token = localStorage.getItem('access_token');
    const tokenStatus = token ? 'Found' : 'Not found';
    
    // Get user info from localStorage if available
    const userJson = localStorage.getItem('user');
    let userInfo = 'Not found';
    
    if (userJson) {
      try {
        const user = JSON.parse(userJson);
        userInfo = {
          id: user.id,
          email: user.email,
          role: user.role,
          is_active: user.is_active,
          is_superuser: user.is_superuser
        };
      } catch (e) {
        userInfo = 'Invalid JSON';
      }
    }
    
    // Log the information
    console.group('User Authentication Debug Info');
    console.log('Access Token:', tokenStatus);
    console.log('User Info:', userInfo);
    console.groupEnd();
    
    return { tokenStatus, userInfo };
  } catch (error) {
    console.error('Error in logUserAuthInfo:', error);
    return { error: String(error) };
  }
};
