import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Bell, Key, Lock, Mail, User } from 'lucide-react';
import { useAuthStore } from '../../features/auth/store/authStore';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import Input from '../../components/common/Input';

interface ProfileFormData {
  full_name: string;
  email: string;
  current_password: string;
  new_password: string;
  confirm_password: string;
}

const UserProfilePage: React.FC = () => {
  const { user } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ProfileFormData>({
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
    },
  });
  
  const onSubmit = async (data: ProfileFormData) => {
    console.log('Form data:', data);
    // TODO: Implement profile update
    setIsEditing(false);
  };
  
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-foreground">Profile Settings</h1>
      
      {/* Profile Information */}
      <Card className="max-w-2xl">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="border-b border-border pb-6">
            <h2 className="text-lg font-medium text-card-foreground">Profile Information</h2>
            <p className="mt-1 text-sm text-card-foreground/70">
              Update your account profile information and email address.
            </p>
          </div>
          
          <div className="space-y-4">
            <Input
              label="Full Name"
              {...register('full_name', { required: 'Full name is required' })}
              error={errors.full_name?.message}
              disabled={!isEditing}
              leftIcon={<User size={18} />}
            />
            
            <Input
              label="Email Address"
              type="email"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
              })}
              error={errors.email?.message}
              disabled={!isEditing}
              leftIcon={<Mail size={18} />}
            />
          </div>
          
          {isEditing ? (
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsEditing(false)}
              >
                Cancel
              </Button>
              <Button type="submit">Save Changes</Button>
            </div>
          ) : (
            <Button type="button" onClick={() => setIsEditing(true)}>
              Edit Profile
            </Button>
          )}
        </form>
      </Card>
      
      {/* Password Update */}
      <Card className="max-w-2xl">
        <div className="space-y-6">
          <div className="border-b border-border pb-6">
            <h2 className="text-lg font-medium text-card-foreground">Update Password</h2>
            <p className="mt-1 text-sm text-card-foreground/70">
              Ensure your account is using a long, random password to stay secure.
            </p>
          </div>
          
          <form className="space-y-4">
            <Input
              label="Current Password"
              type="password"
              {...register('current_password')}
              leftIcon={<Key size={18} />}
            />
            
            <Input
              label="New Password"
              type="password"
              {...register('new_password', {
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters',
                },
              })}
              error={errors.new_password?.message}
              leftIcon={<Lock size={18} />}
            />
            
            <Input
              label="Confirm New Password"
              type="password"
              {...register('confirm_password', {
                validate: (value) =>
                  value === watch('new_password') || 'Passwords do not match',
              })}
              error={errors.confirm_password?.message}
              leftIcon={<Lock size={18} />}
            />
            
            <div className="flex justify-end">
              <Button type="submit">Update Password</Button>
            </div>
          </form>
        </div>
      </Card>
      
      {/* Notification Preferences */}
      <Card className="max-w-2xl">
        <div className="space-y-6">
          <div className="border-b border-border pb-6">
            <h2 className="text-lg font-medium text-card-foreground">
              Notification Preferences
            </h2>
            <p className="mt-1 text-sm text-card-foreground/70">
              Manage how you receive security alerts and updates.
            </p>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="flex h-6 items-center">
                <input
                  id="critical_alerts"
                  type="checkbox"
                  className="h-4 w-4 rounded border-border bg-background text-primary focus:ring-primary"
                  defaultChecked
                />
              </div>
              <div className="ml-3">
                <label
                  htmlFor="critical_alerts"
                  className="text-sm font-medium text-card-foreground"
                >
                  Critical Security Alerts
                </label>
                <p className="text-sm text-card-foreground/70">
                  Receive immediate notifications for critical security incidents.
                </p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="flex h-6 items-center">
                <input
                  id="weekly_reports"
                  type="checkbox"
                  className="h-4 w-4 rounded border-border bg-background text-primary focus:ring-primary"
                  defaultChecked
                />
              </div>
              <div className="ml-3">
                <label
                  htmlFor="weekly_reports"
                  className="text-sm font-medium text-card-foreground"
                >
                  Weekly Security Reports
                </label>
                <p className="text-sm text-card-foreground/70">
                  Receive weekly summaries of security events and system status.
                </p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="flex h-6 items-center">
                <input
                  id="maintenance_updates"
                  type="checkbox"
                  className="h-4 w-4 rounded border-border bg-background text-primary focus:ring-primary"
                />
              </div>
              <div className="ml-3">
                <label
                  htmlFor="maintenance_updates"
                  className="text-sm font-medium text-card-foreground"
                >
                  Maintenance Updates
                </label>
                <p className="text-sm text-card-foreground/70">
                  Get notified about planned maintenance and system updates.
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end">
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Bell size={16} />}
            >
              Update Preferences
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default UserProfilePage;