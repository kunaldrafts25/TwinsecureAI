import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date?: Date | string | null): string {
  if (!date) {
    return 'N/A';
  }

  try {
    let dateObj: Date;
    if (typeof date === 'string') {
      dateObj = new Date(date);
      // Check if the date is valid
      if (isNaN(dateObj.getTime())) {
        return 'Invalid date';
      }
    } else {
      dateObj = date;
    }

    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Error formatting date';
  }
}

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

export function getInitials(name?: string | null): string {
  // Return a default value if name is null, undefined, or empty
  if (!name) return 'U';

  // Safely split the name and get initials
  return name
    .split(' ')
    .filter(part => part.length > 0) // Filter out empty parts
    .map((n) => n[0] || '') // Handle empty strings
    .join('')
    .toUpperCase() || 'U'; // Provide a fallback if result is empty
}

export function severityToColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-severity-critical bg-severity-critical/10 border-severity-critical/20';
    case 'high':
      return 'text-severity-high bg-severity-high/10 border-severity-high/20';
    case 'medium':
      return 'text-severity-medium bg-severity-medium/10 border-severity-medium/20';
    case 'low':
      return 'text-severity-low bg-severity-low/10 border-severity-low/20';
    default:
      return 'text-severity-info bg-severity-info/10 border-severity-info/20';
  }
}

export function statusToColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'new':
      return 'text-error-foreground bg-error border-error';
    case 'acknowledged':
      return 'text-warning-foreground bg-warning border-warning';
    case 'in_progress':
      return 'text-accent-foreground bg-accent border-accent';
    case 'resolved':
      return 'text-success-foreground bg-success border-success';
    case 'false_positive':
      return 'text-secondary-foreground bg-secondary border-secondary';
    default:
      return 'text-primary-foreground bg-primary border-primary';
  }
}