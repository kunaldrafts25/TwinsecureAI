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

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Eye, EyeOff, Mail, Lock, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../features/auth/store/authStore';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import BypassLogin from '../components/common/BypassLogin';
import { LoginRequest } from '../types';
import axios from 'axios';

const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>({
    defaultValues: {
      email: 'admin@finguard.com', // Pre-filled for demo purposes - matches FIRST_SUPERUSER in docker-compose.yml
      password: '123456789', // Pre-filled for demo purposes - matches FIRST_SUPERUSER_PASSWORD in docker-compose.yml
    },
  });

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const onSubmit = async (data: LoginRequest) => {
    // Clear any previous errors
    setLoginError(null);

    try {
      await login(data);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);

      // Set a more specific error message
      if (axios.isAxiosError(error)) {
        if (error.response) {
          if (error.response.status === 401) {
            setLoginError('Invalid credentials. Please check your email and password.');
          } else if (error.response.status === 404) {
            setLoginError('Authentication service not found. Please contact support.');
          } else if (error.response.status === 500) {
            setLoginError('Server error. Please try again later.');
          } else {
            setLoginError(`Login failed: ${error.response.data?.detail || 'Unknown error'}`);
          }
        } else if (error.request) {
          setLoginError('No response from server. Please check your connection.');
        } else {
          setLoginError('Login request failed. Please try again.');
        }
      } else {
        setLoginError('An unexpected error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-foreground">Welcome back</h1>
        <p className="mt-2 text-sm text-foreground/70">
          Sign in to your TwinSecure AI account
        </p>
      </div>

      <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
        {loginError && (
          <div className="rounded-md bg-red-50 p-4 dark:bg-red-900/20">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertCircle className="h-5 w-5 text-red-400 dark:text-red-500" aria-hidden="true" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Login Error</h3>
                <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                  <p>{loginError}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <Input
            label="Email"
            type="email"
            id="email"
            leftIcon={<Mail size={18} />}
            placeholder="Enter your email"
            error={errors.email?.message}
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                message: 'Please enter a valid email',
              },
            })}
          />

          <Input
            label="Password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            leftIcon={<Lock size={18} />}
            rightIcon={
              <button
                type="button"
                onClick={togglePasswordVisibility}
                className="text-foreground/50 hover:text-foreground"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            }
            placeholder="Enter your password"
            error={errors.password?.message}
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters',
              },
            })}
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 rounded border-border bg-card text-primary focus:ring-primary"
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm text-foreground">
              Remember me
            </label>
          </div>

          <div className="text-sm">
            <a href="#" className="font-medium text-primary hover:text-primary/80">
              Forgot your password?
            </a>
          </div>
        </div>

        <Button type="submit" className="w-full" isLoading={isLoading}>
          Sign in
        </Button>

        <p className="mt-4 text-center text-sm text-foreground/70">
          Don't have an account?{' '}
          <a href="#" className="font-medium text-primary hover:text-primary/80">
            Contact your administrator
          </a>
        </p>
      </form>

      <div className="mt-6 border-t border-border pt-6">
        <div className="text-center text-sm text-foreground/50">
          For demo purposes, you can use:
          <div className="mt-2 rounded-md bg-foreground/5 p-2 text-left">
            <p>Email: admin@finguard.com</p>
            <p>Password: 123456789</p>
          </div>
        </div>

        {/* Development bypass option */}
        <BypassLogin />
      </div>
    </div>
  );
};

export default AuthPage;