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

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../features/auth/store/authStore';
import Button from './Button';

/**
 * A component that allows bypassing the login page for development purposes
 * This creates a fake authentication session with a mock user
 */
const BypassLogin: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  // Function to create a fake authentication session
  const bypassLogin = () => {
    setIsLoading(true);

    try {
      console.log("Bypassing login for development...");

      // Create a fake JWT token (this is just for development/testing)
      const fakeToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBmaW5ndWFyZC5jb20iLCJleHAiOjk5OTk5OTk5OTl9.fake_signature';

      // Store the token in localStorage
      localStorage.setItem('access_token', fakeToken);

      // Create a mock user object with all required fields
      const mockUser = {
        id: '00000000-0000-0000-0000-000000000000',
        email: 'admin@finguard.com',
        full_name: 'Admin User',
        role: 'admin' as const,
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

      // Update the auth store directly
      useAuthStore.setState({
        isAuthenticated: true,
        user: mockUser,
        isLoading: false,
      });

      console.log("Auth store updated, navigating to dashboard...");

      // Navigate to the dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Error bypassing login:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-4 text-center">
      <Button
        onClick={bypassLogin}
        isLoading={isLoading}
        variant="outline"
        size="sm"
      >
        Bypass Login (Dev Only)
      </Button>
      <p className="mt-2 text-xs text-foreground/50">
        This creates a fake session without contacting the backend
      </p>
    </div>
  );
};

export default BypassLogin;
