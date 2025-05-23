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

import React, { useState } from 'react';
import { cn } from '../../utils/lib';

interface TabItem {
  id: string;
  label: React.ReactNode;
  content: React.ReactNode;
}

interface TabsProps {
  items: TabItem[];
  defaultTab?: string;
  className?: string;
}

const Tabs: React.FC<TabsProps> = ({ items, defaultTab, className }) => {
  const [activeTab, setActiveTab] = useState<string>(defaultTab || items[0]?.id || '');

  return (
    <div className={className}>
      <div className="border-b border-border">
        <nav className="-mb-px flex space-x-4" aria-label="Tabs">
          {items.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'whitespace-nowrap border-b-2 px-4 py-2 text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-foreground/60 hover:border-foreground/30 hover:text-foreground/80'
              )}
              aria-current={activeTab === tab.id ? 'page' : undefined}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
      <div className="mt-4">
        {items.map((tab) => (
          <div
            key={tab.id}
            className={cn(activeTab === tab.id ? 'block' : 'hidden')}
            role="tabpanel"
            aria-labelledby={`tab-${tab.id}`}
          >
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tabs;