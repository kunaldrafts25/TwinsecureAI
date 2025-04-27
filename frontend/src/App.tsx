import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Dashboard } from './pages/Dashboard';
import { AlertsPage } from './pages/AlertsPage';
import { HoneypotPage } from './pages/HoneypotPage';
import { ThreatMapPage } from './pages/ThreatMapPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AnomalyDetectionPage } from './pages/AnomalyDetectionPage';
import { ReportsPage } from './pages/ReportsPage';
import { alerts } from './data/mockData';

function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(false);
  const [newAlertCount, setNewAlertCount] = useState(0);
  
  useEffect(() => {
    // Count new alerts
    const count = alerts.filter(alert => alert.status === 'new').length;
    setNewAlertCount(count);
    
    // Check system preference for dark mode
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true);
    }
    
    // Update document title
    document.title = "TwinSecure AI | Security Dashboard";
  }, []);
  
  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };
  
  // Get current page title
  const getPageTitle = () => {
    switch (activePage) {
      case 'dashboard':
        return 'Security Dashboard';
      case 'alerts':
        return 'Security Alerts';
      case 'threats':
        return 'Threat Map';
      case 'honeypot':
        return 'Honeypot Activity';
      case 'analytics':
        return 'Security Analytics';
      case 'anomalies':
        return 'Anomaly Detection';
      case 'reports':
        return 'Security Reports';
      case 'settings':
        return 'Settings';
      case 'help':
        return 'Help & Support';
      default:
        return 'TwinSecure AI';
    }
  };
  
  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'alerts':
        return <AlertsPage />;
      case 'honeypot':
        return <HoneypotPage />;
      case 'threats':
        return <ThreatMapPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'anomalies':
        return <AnomalyDetectionPage />;
      case 'reports':
        return <ReportsPage />;
      default:
        return (
          <div className="flex items-center justify-center h-[calc(100vh-4rem)] text-slate-400">
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-2">{getPageTitle()}</h2>
              <p>This page is not implemented in the demo.</p>
            </div>
          </div>
        );
    }
  };
  
  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white">
        <Sidebar activePage={activePage} onPageChange={setActivePage} />
        
        <div className="ml-56">
          <Header 
            title={getPageTitle()} 
            alertCount={newAlertCount} 
            darkMode={darkMode} 
            toggleDarkMode={toggleDarkMode} 
          />
          
          <main>
            {renderPage()}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;