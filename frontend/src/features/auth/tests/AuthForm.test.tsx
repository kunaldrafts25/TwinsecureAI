/**
 * Tests for the AuthForm component
 * 
 * This file contains tests for the authentication form component,
 * including form validation, submission, and error handling.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { useAuthStore } from '../store/authStore';

// Mock the auth store
vi.mock('../store/authStore', () => ({
  useAuthStore: vi.fn()
}));

// Mock the API service
vi.mock('../../../services/api', () => ({
  api: {
    post: vi.fn()
  }
}));

describe('AuthForm Component', () => {
  // Setup common mocks before each test
  beforeEach(() => {
    // Reset mocks
    vi.resetAllMocks();
    
    // Mock the auth store with default values
    (useAuthStore as any).mockReturnValue({
      login: vi.fn(),
      isLoading: false,
      error: null
    });
  });

  it('renders the login form correctly', () => {
    // Render the component
    render(
      <BrowserRouter>
        <AuthForm />
      </BrowserRouter>
    );
    
    // Check that the form elements are rendered
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('validates email format', async () => {
    // Render the component
    render(
      <BrowserRouter>
        <AuthForm />
      </BrowserRouter>
    );
    
    // Get form elements
    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Enter invalid email
    await userEvent.type(emailInput, 'invalid-email');
    
    // Submit the form
    fireEvent.click(submitButton);
    
    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
    });
    
    // Verify login function was not called
    expect(useAuthStore().login).not.toHaveBeenCalled();
  });

  it('validates required fields', async () => {
    // Render the component
    render(
      <BrowserRouter>
        <AuthForm />
      </BrowserRouter>
    );
    
    // Get form elements
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Submit the form without entering any data
    fireEvent.click(submitButton);
    
    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
    
    // Verify login function was not called
    expect(useAuthStore().login).not.toHaveBeenCalled();
  });

  it('submits the form with valid data', async () => {
    // Mock successful login
    const mockLogin = vi.fn().mockResolvedValue(undefined);
    (useAuthStore as any).mockReturnValue({
      login: mockLogin,
      isLoading: false,
      error: null
    });
    
    // Render the component
    render(
      <BrowserRouter>
        <AuthForm />
      </BrowserRouter>
    );
    
    // Get form elements
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Enter valid data
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    
    // Submit the form
    fireEvent.click(submitButton);
    
    // Verify login function was called with correct data
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });

  it('displays loading state during form submission', async () => {
    // Mock loading state
    (useAuthStore as any).mockReturnValue({
      login: vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100))),
      isLoading: true,
      error: null
    });
    
    // Render the component
    render(
      <BrowserRouter>
        <AuthForm />
      </BrowserRouter>
    );
    
    // Get form elements
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Enter valid data
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    
    // Submit the form
    fireEvent.click(submitButton);
    
    // Check for loading indicator
    expect(screen.getByText(/signing in/i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('displays error message on login failure', async () => {
    // Mock login error
    const errorMessage = 'Invalid credentials';
    (useAuthStore as any).mockReturnValue({
      login: vi.fn().mockRejectedValue(new Error(errorMessage)),
      isLoading: false,
      error: errorMessage
    });
    
    // Render the component
    render(
      <BrowserRouter>
        <AuthForm />
      </BrowserRouter>
    );
    
    // Get form elements
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Enter valid data
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    
    // Submit the form
    fireEvent.click(submitButton);
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('toggles password visibility', async () => {
    // Render the component
    render(
      <BrowserRouter>
        <AuthForm />
      </BrowserRouter>
    );
    
    // Get password input and toggle button
    const passwordInput = screen.getByLabelText(/password/i);
    const toggleButton = screen.getByRole('button', { name: /toggle password visibility/i });
    
    // Check initial state (password is hidden)
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle button
    fireEvent.click(toggleButton);
    
    // Check that password is now visible
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click toggle button again
    fireEvent.click(toggleButton);
    
    // Check that password is hidden again
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
});
