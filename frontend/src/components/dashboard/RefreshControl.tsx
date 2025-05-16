import React, { useState } from 'react';
import { Clock, Pause, Play, RefreshCw } from 'lucide-react';
import Button from '../common/Button';

interface RefreshControlProps {
  lastUpdated: Date | null;
  isLoading: boolean;
  refreshInterval: number | null;
  onRefresh: () => void;
  onAutoRefreshChange: (interval: number | null) => void;
}

const RefreshControl: React.FC<RefreshControlProps> = ({
  lastUpdated,
  isLoading,
  refreshInterval,
  onRefresh,
  onAutoRefreshChange,
}) => {
  const [showIntervalOptions, setShowIntervalOptions] = useState(false);
  
  const formatLastUpdated = (date: Date) => {
    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffSeconds < 60) {
      return `${diffSeconds} seconds ago`;
    } else if (diffSeconds < 3600) {
      return `${Math.floor(diffSeconds / 60)} minutes ago`;
    } else if (diffSeconds < 86400) {
      return `${Math.floor(diffSeconds / 3600)} hours ago`;
    } else {
      return date.toLocaleString();
    }
  };
  
  const intervalOptions = [
    { value: 30, label: '30s' },
    { value: 60, label: '1m' },
    { value: 300, label: '5m' },
    { value: 600, label: '10m' },
  ];
  
  return (
    <div className="flex items-center gap-2">
      {lastUpdated && (
        <div className="flex items-center text-sm text-muted-foreground">
          <Clock size={14} className="mr-1" />
          <span>Last updated: {formatLastUpdated(lastUpdated)}</span>
        </div>
      )}
      
      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          leftIcon={<RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />}
          onClick={onRefresh}
          disabled={isLoading}
        >
          Refresh
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          leftIcon={refreshInterval ? <Pause size={14} /> : <Play size={14} />}
          onClick={() => {
            if (refreshInterval) {
              onAutoRefreshChange(null);
            } else {
              setShowIntervalOptions(!showIntervalOptions);
            }
          }}
          className="ml-2"
        >
          {refreshInterval ? 'Stop Auto-refresh' : 'Auto-refresh'}
        </Button>
        
        {showIntervalOptions && (
          <div className="absolute right-0 mt-1 w-48 rounded-md shadow-lg bg-background border border-border z-10">
            <div className="py-1">
              <div className="px-4 py-2 text-sm font-medium border-b border-border">
                Refresh interval
              </div>
              {intervalOptions.map((option) => (
                <button
                  key={option.value}
                  className="block w-full text-left px-4 py-2 text-sm hover:bg-muted"
                  onClick={() => {
                    onAutoRefreshChange(option.value);
                    setShowIntervalOptions(false);
                  }}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RefreshControl;
