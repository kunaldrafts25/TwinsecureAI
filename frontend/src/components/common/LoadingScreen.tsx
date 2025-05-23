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

import React, { useEffect } from 'react';
import { ShieldCheck } from 'lucide-react';

const LoadingScreen: React.FC = () => {
  useEffect(() => {
    console.log("LoadingScreen component rendered");

    // Force body background to be neutral during loading
    document.body.style.backgroundColor = '#1e293b'; // slate-800

    // Cleanup function to restore original background
    return () => {
      document.body.style.backgroundColor = '';
    };
  }, []);

  return (
    <div className="loading-screen fixed inset-0 flex min-h-screen items-center justify-center bg-slate-800">
      <div className="flex flex-col items-center gap-4 bg-white p-8 rounded-lg shadow-lg">
        <ShieldCheck className="h-16 w-16 animate-pulse text-blue-500" />
        <h1 className="text-3xl font-bold text-black">TwinSecure AI</h1>
        <div className="h-4 w-64 overflow-hidden rounded-full bg-gray-200">
          <div className="h-full w-1/2 animate-[pulse_1.5s_ease-in-out_infinite] bg-blue-500"></div>
        </div>
        <p className="text-lg text-gray-700">Loading secure environment...</p>
        <p className="text-sm text-gray-500 mt-4">If you see this screen, the app is loading correctly.</p>
      </div>
    </div>
  );
};

export default LoadingScreen;