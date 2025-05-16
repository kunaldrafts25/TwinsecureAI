import React from 'react';
import { Outlet } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { useThemeStore } from '../store/themeStore';

const AuthLayout: React.FC = () => {
  const { toggleTheme, theme } = useThemeStore();
  
  return (
    <div className="flex h-screen flex-col md:flex-row">
      {/* Left side - branding & info */}
      <div className="honeycomb-bg hidden flex-1 flex-col bg-primary p-8 text-primary-foreground md:flex">
        <div className="flex items-center gap-2">
          <Shield className="h-8 w-8" />
          <h1 className="text-2xl font-bold">TwinSecure AI</h1>
        </div>
        
        <div className="mt-auto max-w-md">
          <h2 className="text-3xl font-bold">AI-Powered Cybersecurity for SMEs</h2>
          <p className="mt-4 text-lg text-primary-foreground/90">
            Advanced protection for your business through digital twin technology, AI-driven monitoring,
            and adaptive honeypots.
          </p>
          <div className="mt-8 flex flex-col gap-4">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-white/10 p-1">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-medium">Digital Twin Technology</h3>
                <p className="text-sm text-primary-foreground/80">
                  High-fidelity replicas of your digital assets for maximum protection
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-white/10 p-1">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-medium">AI-Enhanced Monitoring</h3>
                <p className="text-sm text-primary-foreground/80">
                  Continuous threat detection and anomaly identification
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-white/10 p-1">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-medium">Deception Technologies</h3>
                <p className="text-sm text-primary-foreground/80">
                  Honeypots that detect, analyze, and neutralize threats in isolation
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-8 text-sm">
          &copy; 2025 TwinSecure AI. All rights reserved.
        </div>
      </div>
      
      {/* Right side - auth forms */}
      <div className="flex flex-1 flex-col">
        <div className="flex h-16 items-center justify-between border-b border-border px-6 md:justify-end">
          <div className="flex items-center gap-2 md:hidden">
            <Shield className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold">TwinSecure AI</span>
          </div>
          
          <button
            onClick={toggleTheme}
            className="flex h-9 w-9 items-center justify-center rounded-full text-foreground/70 hover:bg-foreground/5 hover:text-foreground"
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="4"></circle>
                <path d="M12 2v2"></path>
                <path d="M12 20v2"></path>
                <path d="m4.93 4.93 1.41 1.41"></path>
                <path d="m17.66 17.66 1.41 1.41"></path>
                <path d="M2 12h2"></path>
                <path d="M20 12h2"></path>
                <path d="m6.34 17.66-1.41 1.41"></path>
                <path d="m19.07 4.93-1.41 1.41"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>
              </svg>
            )}
          </button>
        </div>
        
        <div className="flex flex-1 items-center justify-center p-6">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;