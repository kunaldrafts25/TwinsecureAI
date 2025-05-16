import React from 'react';
import { render } from './test-utils';
import { vi } from 'vitest';

// Mock the cn utility function that's commonly used in components
vi.mock('../utils/lib', async () => {
  const actual = await vi.importActual('../utils/lib');
  return {
    ...actual,
    cn: (...inputs: any[]) => inputs.filter(Boolean).join(' '),
  };
});

// Helper function to test basic component rendering
export const testComponentRendering = (
  Component: React.ComponentType<any>,
  props: Record<string, any> = {},
  testId: string = 'component'
) => {
  it('renders without crashing', () => {
    const { getByTestId } = render(
      <div data-testid={testId}>
        <Component {...props} />
      </div>
    );
    expect(getByTestId(testId)).toBeInTheDocument();
  });
};

// Helper function to test if a component applies className correctly
export const testComponentClassName = (
  Component: React.ComponentType<any>,
  className: string,
  props: Record<string, any> = {}
) => {
  it(`applies the className "${className}"`, () => {
    const { container } = render(
      <Component {...props} className={className} />
    );
    // Find the first element with the className
    const element = container.querySelector(`.${className}`);
    expect(element).toBeInTheDocument();
  });
};
