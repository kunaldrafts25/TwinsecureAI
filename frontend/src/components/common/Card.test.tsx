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

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import Card from './Card';

// Mock the cn utility function
vi.mock('../../utils/lib', async () => {
  const actual = await vi.importActual('../../utils/lib');
  return {
    ...actual,
    cn: (...inputs: any[]) => inputs.filter(Boolean).join(' '),
  };
});

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <div data-testid="card-content">Card Content</div>
      </Card>
    );
    expect(screen.getByTestId('card-content')).toBeInTheDocument();
    expect(screen.getByText('Card Content')).toBeInTheDocument();
  });

  it('renders title and subtitle when provided', () => {
    render(
      <Card title="Card Title" subtitle="Card Subtitle">
        <div>Card Content</div>
      </Card>
    );
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card Subtitle')).toBeInTheDocument();
  });

  it('renders action when provided', () => {
    render(
      <Card
        title="Card Title"
        action={<button data-testid="card-action">Action</button>}
      >
        <div>Card Content</div>
      </Card>
    );
    expect(screen.getByTestId('card-action')).toBeInTheDocument();
  });

  it('shows loading state when isLoading is true', () => {
    const { container } = render(
      <Card isLoading>
        <div>This content should not be visible</div>
      </Card>
    );

    // The content should not be visible when loading
    expect(screen.queryByText('This content should not be visible')).not.toBeInTheDocument();

    // Instead, we should see loading placeholders
    const loadingElement = container.querySelector('.animate-pulse');
    expect(loadingElement).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <Card className="custom-class">
        <div>Card Content</div>
      </Card>
    );

    const cardElement = container.querySelector('.custom-class');
    expect(cardElement).toBeInTheDocument();
  });

  it('renders without title, subtitle, or action', () => {
    render(
      <Card>
        <div data-testid="simple-content">Simple Content</div>
      </Card>
    );
    expect(screen.getByTestId('simple-content')).toBeInTheDocument();
  });

  it('renders with title but no subtitle or action', () => {
    render(
      <Card title="Only Title">
        <div>Content</div>
      </Card>
    );
    expect(screen.getByText('Only Title')).toBeInTheDocument();
  });
});
