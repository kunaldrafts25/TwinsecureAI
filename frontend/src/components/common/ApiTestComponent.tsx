import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import Button from './Button';

/**
 * A simple component to test API connectivity
 * This is for development purposes only and should be removed in production
 */
const ApiTestComponent: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [apiResponse, setApiResponse] = useState<string>('');

  const testApiConnection = async () => {
    setApiStatus('loading');
    try {
      // Test the health endpoint
      const response = await api.get('/health');
      setApiResponse(JSON.stringify(response.data, null, 2));
      setApiStatus('success');
    } catch (error) {
      console.error('API test failed:', error);

      // Try the root endpoint as fallback
      try {
        console.log('Trying root endpoint as fallback...');
        const rootResponse = await api.get('/');
        setApiResponse(JSON.stringify(rootResponse.data, null, 2) + '\n\n(Used root endpoint as fallback)');
        setApiStatus('success');
      } catch (rootError) {
        console.error('Root endpoint test failed:', rootError);
        setApiResponse(JSON.stringify(error, null, 2));
        setApiStatus('error');
      }
    }
  };

  return (
    <div className="rounded-lg border border-border p-4 mt-4">
      <h3 className="text-lg font-medium mb-2">API Connection Test</h3>
      <Button
        onClick={testApiConnection}
        isLoading={apiStatus === 'loading'}
        className="mb-4"
      >
        Test API Connection
      </Button>

      {apiStatus !== 'idle' && (
        <div className="mt-2">
          <h4 className="font-medium mb-1">
            Status:
            <span className={
              apiStatus === 'success'
                ? 'text-green-500 ml-2'
                : apiStatus === 'error'
                  ? 'text-red-500 ml-2'
                  : 'ml-2'
            }>
              {apiStatus.toUpperCase()}
            </span>
          </h4>
          <pre className="bg-foreground/5 p-3 rounded-md overflow-auto max-h-60 text-sm">
            {apiResponse}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ApiTestComponent;
