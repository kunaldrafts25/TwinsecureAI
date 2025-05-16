import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ApiTestComponent from './ApiTestComponent';

// Mock the api module
vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

// Mock the Button component
vi.mock('./Button', () => ({
  default: ({ children, onClick, isLoading }: any) => (
    <button
      onClick={onClick}
      disabled={isLoading}
      data-testid="mock-button"
      data-loading={isLoading ? 'true' : 'false'}
    >
      {children}
    </button>
  ),
}));

// Import the mocked api
import { api } from '../../services/api';

describe('ApiTestComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<ApiTestComponent />);
    expect(screen.getByText('API Connection Test')).toBeInTheDocument();
    expect(screen.getByTestId('mock-button')).toBeInTheDocument();
  });

  it('shows loading state when testing API connection', async () => {
    // Mock the API response
    const mockApiResponse = { data: { status: 'ok' } };
    (api.get as any).mockResolvedValue(mockApiResponse);

    render(<ApiTestComponent />);

    // Click the test button
    const button = screen.getByTestId('mock-button');
    fireEvent.click(button);

    // Check that the button is in loading state
    expect(button.getAttribute('data-loading')).toBe('true');

    // Wait for the API call to resolve
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(1);
    });
  });

  it('displays success message when API call succeeds', async () => {
    // Mock the API response
    const mockApiResponse = { data: { status: 'ok' } };
    (api.get as any).mockResolvedValue(mockApiResponse);

    render(<ApiTestComponent />);

    // Click the test button
    fireEvent.click(screen.getByTestId('mock-button'));

    // Wait for the success message
    await waitFor(() => {
      expect(screen.getByText(/SUCCESS/i)).toBeInTheDocument();
    });
  });

  it('displays error message when API call fails', async () => {
    // Mock the API error
    const mockError = new Error('API Error');
    (api.get as any).mockRejectedValue(mockError);

    render(<ApiTestComponent />);

    // Click the test button
    fireEvent.click(screen.getByTestId('mock-button'));

    // Wait for the error message
    await waitFor(() => {
      expect(screen.getByText(/ERROR/i)).toBeInTheDocument();
    });
  });
});
