import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, ArrowLeft } from 'lucide-react';
import Button from '../components/common/Button';

const NotFoundPage: React.FC = () => {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <div className="text-center">
        <Shield className="mx-auto h-16 w-16 text-primary" />
        <h1 className="mt-4 text-4xl font-bold text-foreground">404</h1>
        <h2 className="mt-2 text-xl font-medium text-foreground">Page not found</h2>
        <p className="mt-4 text-foreground/70">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="mt-8">
          <Link to="/">
            <Button variant="primary" leftIcon={<ArrowLeft size={16} />}>
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;