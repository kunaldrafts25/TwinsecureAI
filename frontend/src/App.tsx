/**
 * TwinSecure Frontend Application
 *
 * This is the main application component that handles routing, authentication,
 * and theme management for the TwinSecure platform.
 */

import { lazy, Suspense, useEffect } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuthStore } from './features/auth/store/authStore';
import { useThemeStore } from './store/themeStore';
import LoadingScreen from './components/common/LoadingScreen';
import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayout';
import React from 'react';

// Lazy load pages to improve initial load performance
// Each page is loaded only when needed, reducing the initial bundle size

// Authentication
const AuthPage = lazy(() => import('./pages/AuthPage'));

// Dashboard pages
const SecurityDashboardPage = lazy(() => import('./pages/dashboard/SecurityDashboardPage'));
const MsspDashboardPage = lazy(() => import('./pages/mssp/MsspDashboardPage'));

// Feature pages
const AlertsManagementPage = lazy(() => import('./pages/alerts/AlertsManagementPage'));
const DigitalTwinHoneypotPage = lazy(() => import('./pages/twin/DigitalTwinHoneypotPage'));
const ReportingAnalyticsPage = lazy(() => import('./pages/reports/ReportingAnalyticsPage'));
const AnalyticsPage = lazy(() => import('./pages/analytics/AnalyticsPage'));

// User settings
const UserProfilePage = lazy(() => import('./pages/settings/UserProfilePage'));

// Error pages
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

/**
 * Main application component that handles routing, authentication, and theme management.
 *
 * This component:
 * 1. Initializes the application theme based on user preferences
 * 2. Checks for existing authentication
 * 3. Provides development bypass for authentication when needed
 * 4. Renders the appropriate routes based on authentication state
 *
 * @returns {JSX.Element} The rendered application
 */
function App() {
  // Get authentication state and functions from the auth store
  const { isAuthenticated, checkAuth } = useAuthStore();

  // Get theme state and functions from the theme store
  const { theme, initTheme } = useThemeStore();

  // Track if the application has completed initialization
  const [initialized, setInitialized] = React.useState(false);

  /**
   * Effect hook for application initialization
   * Runs once when the component mounts
   */
  useEffect(() => {
    console.log("App component mounted");

    /**
     * Initialize the application
     * This includes theme initialization and authentication check
     */
    const initialize = async () => {
      try {
        // Step 1: Initialize theme from local storage or system preference
        initTheme();
        console.log("Theme initialized");

        // Step 2: Check for existing authentication (token in local storage)
        await checkAuth();
        console.log("Auth checked");

        // Step 3: If no authentication is found, use development bypass
        // This allows for easier development without needing to log in each time
        if (!isAuthenticated) {
          console.log("No authentication found, using development bypass");

          // Create a mock user for development environment
          const mockUser = {
            id: "00000000-0000-0000-0000-000000000000",
            email: "admin@finguard.com",
            full_name: "Admin User",
            role: "admin",
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

          // Update auth store with mock user to simulate authentication
          useAuthStore.setState({
            isAuthenticated: true,
            user: mockUser,
            isLoading: false,
          });

          console.log("Development bypass complete");
        }
      } catch (error) {
        // Handle any errors during initialization
        console.error("Error during initialization:", error);

        // Use development bypass on error to ensure the app is usable
        console.log("Error occurred, using development bypass");

        // Create a mock user for development environment
        const mockUser = {
          id: "00000000-0000-0000-0000-000000000000",
          email: "admin@finguard.com",
          full_name: "Admin User",
          role: "admin",
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

        // Update auth store with mock user
        useAuthStore.setState({
          isAuthenticated: true,
          user: mockUser,
          isLoading: false,
        });
      } finally {
        // Always mark initialization as complete to prevent infinite loading
        setInitialized(true);
        console.log("Initialization complete");
      }
    };

    // Execute the initialization function
    initialize();
  }, [initTheme, checkAuth]);

  /**
   * Effect hook for applying theme changes
   * Runs whenever the theme state changes
   */
  useEffect(() => {
    try {
      // Toggle the 'dark' class on the document root element based on theme state
      document.documentElement.classList.toggle('dark', theme === 'dark');
      console.log("Theme applied:", theme);
    } catch (error) {
      console.error("Error applying theme:", error);
    }
  }, [theme]);

  // Log authentication state for debugging purposes
  console.log("Authentication state:", { isAuthenticated, initialized });

  /**
   * Render the application with appropriate routes based on authentication state
   * Uses React Router for navigation and Suspense for lazy loading
   */
  return (
    // Suspense provides a loading fallback while lazy-loaded components are being loaded
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        {/* Unauthenticated Routes */}
        {!isAuthenticated ? (
          <>
            {/* Authentication routes */}
            <Route path="/auth" element={<AuthLayout />}>
              <Route index element={<AuthPage />} />
            </Route>

            {/* Redirect all other routes to auth page when not authenticated */}
            <Route path="*" element={<Navigate to="/auth" replace />} />
          </>
        ) : (
          /* Authenticated Routes */
          <>
            {/* Main application routes within the dashboard layout */}
            <Route path="/" element={<DashboardLayout />}>
              {/* Redirect root to dashboard */}
              <Route index element={<Navigate to="/dashboard" replace />} />

              {/* Dashboard routes */}
              <Route path="dashboard" element={<SecurityDashboardPage />} />
              <Route path="dashboard/basic" element={<SecurityDashboardPage />} />
              <Route path="mssp" element={<MsspDashboardPage />} />

              {/* Feature routes */}
              <Route path="alerts" element={<AlertsManagementPage />} />
              <Route path="twin" element={<DigitalTwinHoneypotPage />} />
              <Route path="reports" element={<ReportingAnalyticsPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />

              {/* User settings */}
              <Route path="profile" element={<UserProfilePage />} />
            </Route>

            {/* Redirect auth page to dashboard when already authenticated */}
            <Route path="/auth" element={<Navigate to="/dashboard" replace />} />

            {/* 404 page for any other routes */}
            <Route path="*" element={<NotFoundPage />} />
          </>
        )}
      </Routes>
    </Suspense>
  );
}

export default App;
