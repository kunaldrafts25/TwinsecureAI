# TwinSecure Frontend Documentation

This document provides detailed information about the TwinSecure frontend architecture, components, and usage.

## Directory Structure

- **components/**: Reusable UI components
  - **common/**: Common UI elements (buttons, inputs, etc.)
  - **layout/**: Layout components (header, footer, sidebar)
  - **charts/**: Chart and visualization components
  - **forms/**: Form components and utilities
  - **modals/**: Modal dialog components
  - **tables/**: Table components

- **features/**: Feature-specific modules
  - **auth/**: Authentication-related components and logic
  - **alerts/**: Alert management components and logic
  - **dashboard/**: Dashboard components and logic
  - **reports/**: Report management components and logic
  - **settings/**: Settings components and logic
  - **digital-twins/**: Digital twin management components

- **layouts/**: Page layout templates
  - **AuthLayout.tsx**: Layout for authentication pages
  - **DashboardLayout.tsx**: Layout for dashboard pages
  - **SettingsLayout.tsx**: Layout for settings pages

- **pages/**: Page components
  - **auth/**: Authentication pages (login, register, etc.)
  - **dashboard/**: Dashboard pages
  - **alerts/**: Alert management pages
  - **reports/**: Report management pages
  - **settings/**: Settings pages
  - **digital-twins/**: Digital twin management pages

- **services/**: API service clients
  - **api.ts**: Base API client
  - **auth.ts**: Authentication service
  - **alerts.ts**: Alerts service
  - **reports.ts**: Reports service
  - **users.ts**: Users service

- **store/**: State management
  - **authStore.ts**: Authentication state
  - **alertStore.ts**: Alerts state
  - **reportStore.ts**: Reports state
  - **settingsStore.ts**: Settings state
  - **themeStore.ts**: Theme state

- **utils/**: Utility functions
  - **date.ts**: Date formatting utilities
  - **validation.ts**: Form validation utilities
  - **formatting.ts**: Text formatting utilities
  - **storage.ts**: Local storage utilities

## Component Architecture

TwinSecure follows a component-based architecture with the following principles:

1. **Atomic Design**: Components are organized following atomic design principles
   - Atoms: Basic UI elements (buttons, inputs)
   - Molecules: Combinations of atoms (form fields, alert cards)
   - Organisms: Complex UI sections (navigation, alert lists)
   - Templates: Page layouts
   - Pages: Complete pages

2. **Feature-First Organization**: Code is organized by feature rather than by type
   - Each feature has its own components, services, and state
   - Shared components are placed in the common directory

3. **Container/Presentation Pattern**: Components are separated into:
   - Container components: Handle data fetching and state
   - Presentation components: Handle rendering and UI

## State Management

TwinSecure uses Zustand for state management:

1. **Store Structure**:
   - Each feature has its own store
   - Global state is managed in dedicated stores
   - Stores are modular and focused on specific concerns

2. **Authentication State**:
   - Manages user authentication state
   - Handles login, logout, and token refresh
   - Provides user information to components

3. **Feature State**:
   - Manages feature-specific state
   - Handles data fetching and caching
   - Provides data and actions to components

## Routing

TwinSecure uses React Router for routing:

1. **Route Structure**:
   - Public routes: Accessible without authentication
   - Protected routes: Require authentication
   - Role-based routes: Require specific user roles

2. **Route Guards**:
   - AuthGuard: Prevents access to protected routes without authentication
   - RoleGuard: Prevents access to routes without required roles

## Styling

TwinSecure uses Tailwind CSS for styling:

1. **Utility-First Approach**:
   - Components are styled using utility classes
   - Custom components extend Tailwind's utility classes

2. **Theme Customization**:
   - Theme colors and styles are defined in tailwind.config.js
   - Dark mode support is implemented using Tailwind's dark mode

3. **Component Styling**:
   - Components use consistent styling patterns
   - Responsive design is implemented using Tailwind's responsive utilities

## API Integration

TwinSecure integrates with the backend API using Axios:

1. **API Client**:
   - Base API client handles common functionality
   - Feature-specific services extend the base client

2. **Request/Response Handling**:
   - Requests are formatted according to API specifications
   - Responses are parsed and transformed as needed

3. **Error Handling**:
   - API errors are caught and handled appropriately
   - Error messages are displayed to users

## Authentication

TwinSecure implements JWT-based authentication:

1. **Login Flow**:
   - User submits credentials
   - Backend validates credentials and returns tokens
   - Tokens are stored in local storage
   - User is redirected to dashboard

2. **Token Management**:
   - Access token is used for API requests
   - Refresh token is used to obtain new access tokens
   - Tokens are automatically refreshed when expired

3. **Logout Flow**:
   - Tokens are removed from local storage
   - User is redirected to login page

## Form Handling

TwinSecure uses React Hook Form for form handling:

1. **Form Structure**:
   - Forms are created using React Hook Form
   - Validation is implemented using Yup schemas

2. **Form Submission**:
   - Form data is validated before submission
   - Submission errors are displayed to users

## Testing

TwinSecure uses Vitest for testing:

1. **Test Structure**:
   - Unit tests for utilities and hooks
   - Component tests for UI components
   - Integration tests for feature workflows

2. **Test Utilities**:
   - Custom render function with providers
   - Mock services for API testing
   - Test fixtures for common test data
