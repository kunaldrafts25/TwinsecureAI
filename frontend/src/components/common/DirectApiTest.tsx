import React, { useState } from 'react';
import axios from 'axios';
import Button from './Button';

/**
 * A component to directly test API connectivity without using the configured API client
 * This is for debugging purposes only
 */
const DirectApiTest: React.FC = () => {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [response, setResponse] = useState<string>('');
  const [error, setError] = useState<string>('');
  const apiUrl = import.meta.env.VITE_API_URL;

  const testDirectConnection = async () => {
    setStatus('loading');
    try {
      // Test the health endpoint directly
      const result = await axios.get(`${apiUrl}/health`);
      setResponse(JSON.stringify(result.data, null, 2));
      setStatus('success');
      setError('');
    } catch (err) {
      console.error('Health endpoint test failed, trying root endpoint as fallback...');
      try {
        // Try the root endpoint as fallback
        const rootResult = await axios.get(`${apiUrl}/`);
        setResponse(JSON.stringify(rootResult.data, null, 2) + '\n\n(Used root endpoint as fallback)');
        setStatus('success');
        setError('');
      } catch (rootErr) {
        setStatus('error');
        if (axios.isAxiosError(err)) {
          setError(
            `Error: ${err.message}\n` +
            `Status: ${err.response?.status}\n` +
            `Data: ${JSON.stringify(err.response?.data, null, 2)}\n` +
            `Headers: ${JSON.stringify(err.response?.headers, null, 2)}`
          );
        } else {
          setError(`Unknown error: ${String(err)}`);
        }
      }
    }
  };

  const testLoginEndpoint = async () => {
    setStatus('loading');
    try {
      // Create form data for login test
      const formData = new URLSearchParams();
      formData.append('username', 'admin@finguard.com');
      formData.append('password', '123456789');

      // Test the login endpoint directly
      const result = await axios.post(`${apiUrl}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      setResponse(JSON.stringify(result.data, null, 2));
      setStatus('success');
      setError('');
    } catch (err) {
      console.error('Login endpoint test failed:', err);

      // Try with email instead of username
      try {
        console.log('Trying with email parameter instead of username...');
        const emailFormData = new URLSearchParams();
        emailFormData.append('email', 'admin@finguard.com');
        emailFormData.append('password', '123456789');

        const emailResult = await axios.post(`${apiUrl}/auth/login`, emailFormData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });

        setResponse(JSON.stringify(emailResult.data, null, 2) + '\n\n(Used email parameter instead of username)');
        setStatus('success');
        setError('');
      } catch (emailErr) {
        // Try with JSON format
        try {
          console.log('Trying with JSON format...');
          const jsonResult = await axios.post(`${apiUrl}/auth/login`, {
            email: 'admin@finguard.com',
            password: '123456789'
          }, {
            headers: {
              'Content-Type': 'application/json',
            },
          });

          setResponse(JSON.stringify(jsonResult.data, null, 2) + '\n\n(Used JSON format)');
          setStatus('success');
          setError('');
        } catch (jsonErr) {
          setStatus('error');
          if (axios.isAxiosError(err)) {
            setError(
              `Error: ${err.message}\n` +
              `Status: ${err.response?.status}\n` +
              `Data: ${JSON.stringify(err.response?.data, null, 2)}\n` +
              `Headers: ${JSON.stringify(err.response?.headers, null, 2)}`
            );
          } else {
            setError(`Unknown error: ${String(err)}`);
          }
        }
      }
    }
  };

  return (
    <div className="rounded-lg border border-border p-4 mt-4">
      <h3 className="text-lg font-medium mb-2">Direct API Connection Test</h3>
      <p className="text-sm text-foreground/70 mb-4">
        Testing direct connection to: <code className="bg-foreground/5 px-1 py-0.5 rounded">{apiUrl}</code>
      </p>

      <div className="flex gap-2 mb-4">
        <Button
          onClick={testDirectConnection}
          isLoading={status === 'loading'}
          size="sm"
        >
          Test Health Endpoint
        </Button>

        <Button
          onClick={testLoginEndpoint}
          isLoading={status === 'loading'}
          size="sm"
          variant="outline"
        >
          Test Login Endpoint
        </Button>
      </div>

      {status !== 'idle' && (
        <div className="mt-2">
          <h4 className="font-medium mb-1">
            Status:
            <span className={
              status === 'success'
                ? 'text-green-500 ml-2'
                : status === 'error'
                  ? 'text-red-500 ml-2'
                  : 'ml-2'
            }>
              {status.toUpperCase()}
            </span>
          </h4>

          {status === 'success' && (
            <pre className="bg-foreground/5 p-3 rounded-md overflow-auto max-h-60 text-sm">
              {response}
            </pre>
          )}

          {status === 'error' && (
            <pre className="bg-red-500/10 p-3 rounded-md overflow-auto max-h-60 text-sm text-red-500">
              {error}
            </pre>
          )}
        </div>
      )}
    </div>
  );
};

export default DirectApiTest;
