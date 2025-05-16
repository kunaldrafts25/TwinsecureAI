# Frontend Testing Guide

This directory contains the testing setup and utilities for the TwinSecure frontend application.

## Testing Framework

We use the following tools for testing:

- **Vitest**: Fast and lightweight testing framework compatible with Vite
- **React Testing Library**: For testing React components
- **JSDOM**: For simulating a browser environment in Node.js

## Test Structure

- `setup.ts`: Global test setup and configuration
- `test-utils.tsx`: Custom render function with providers
- `component-test-helper.tsx`: Helper functions for component testing
- `simple.test.ts`: Simple tests that don't rely on DOM

## Running Tests

You can run tests using the following npm scripts:

```bash
# Run all tests
npm test

# Run tests in watch mode (for development)
npm run test:watch

# Run tests with UI
npm run test:ui

# Run tests with coverage report
npm run test:coverage

# Run only utility tests
npm run test:utils

# Run only component tests
npm run test:components
```

## Writing Tests

### Utility Tests

For utility functions, create a `.test.ts` file next to the utility file:

```typescript
import { describe, it, expect } from 'vitest';
import { myUtilityFunction } from './my-utility';

describe('myUtilityFunction', () => {
  it('should do something', () => {
    expect(myUtilityFunction()).toBe(expectedResult);
  });
});
```

### Component Tests

For React components, create a `.test.tsx` file next to the component file:

```typescript
import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '../../test/test-utils';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Mocking

You can mock dependencies using Vitest's mocking capabilities:

```typescript
import { vi } from 'vitest';

// Mock a module
vi.mock('../path/to/module', () => ({
  someFunction: vi.fn(),
}));

// Mock a function
const mockFn = vi.fn();
mockFn.mockReturnValue('mocked value');
```

## Best Practices

1. **Test behavior, not implementation**: Focus on what the component does, not how it does it.
2. **Use data-testid for test-specific selectors**: Avoid selecting elements by class or tag.
3. **Keep tests simple and focused**: Each test should verify one specific behavior.
4. **Use the custom render function**: This ensures components have access to necessary providers.
5. **Clean up after each test**: The setup file includes cleanup after each test.
6. **Mock external dependencies**: Use vi.mock() to mock API calls and other external dependencies.
7. **Test edge cases**: Include tests for error states, loading states, and edge cases.

## Coverage

Run `npm run test:coverage` to generate a coverage report. The report will show:

- Statement coverage
- Branch coverage
- Function coverage
- Line coverage

The coverage report will be generated in the `coverage` directory.
