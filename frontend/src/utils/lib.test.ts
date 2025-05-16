import { describe, it, expect, vi } from 'vitest';
import { formatDate, truncateText, getInitials, severityToColor, statusToColor } from './lib';

describe('Utility Functions', () => {
  describe('formatDate', () => {
    it('should format a date string correctly', () => {
      const result = formatDate('2023-01-15T12:30:00Z');
      expect(result).toContain('Jan 15, 2023');
    });

    it('should handle null or undefined', () => {
      expect(formatDate(null)).toBe('N/A');
      expect(formatDate(undefined)).toBe('N/A');
    });

    it('should handle invalid date strings', () => {
      expect(formatDate('not-a-date')).toBe('Invalid date');
    });
  });

  describe('truncateText', () => {
    it('should truncate text that exceeds max length', () => {
      const text = 'This is a long text that should be truncated';
      expect(truncateText(text, 10)).toBe('This is a ...');
    });

    it('should not truncate text that is shorter than max length', () => {
      const text = 'Short text';
      expect(truncateText(text, 20)).toBe('Short text');
    });

    it('should handle text that is exactly max length', () => {
      const text = 'Exact length';
      expect(truncateText(text, 12)).toBe('Exact length');
    });
  });

  describe('getInitials', () => {
    it('should get initials from a name', () => {
      expect(getInitials('John Doe')).toBe('JD');
    });

    it('should handle single names', () => {
      expect(getInitials('John')).toBe('J');
    });

    it('should handle null or undefined', () => {
      expect(getInitials(null)).toBe('U');
      expect(getInitials(undefined)).toBe('U');
    });

    it('should handle empty strings', () => {
      expect(getInitials('')).toBe('U');
    });

    it('should handle multiple spaces', () => {
      expect(getInitials('John  Doe')).toBe('JD');
    });
  });

  describe('severityToColor', () => {
    it('should return the correct color class for critical severity', () => {
      expect(severityToColor('critical')).toContain('text-severity-critical');
    });

    it('should return the correct color class for high severity', () => {
      expect(severityToColor('high')).toContain('text-severity-high');
    });

    it('should return the correct color class for medium severity', () => {
      expect(severityToColor('medium')).toContain('text-severity-medium');
    });

    it('should return the correct color class for low severity', () => {
      expect(severityToColor('low')).toContain('text-severity-low');
    });

    it('should return the default color class for unknown severity', () => {
      expect(severityToColor('unknown')).toContain('text-severity-info');
    });
  });

  describe('statusToColor', () => {
    it('should return the correct color class for new status', () => {
      expect(statusToColor('new')).toContain('text-error-foreground');
    });

    it('should return the correct color class for acknowledged status', () => {
      expect(statusToColor('acknowledged')).toContain('text-warning-foreground');
    });

    it('should return the correct color class for in_progress status', () => {
      expect(statusToColor('in_progress')).toContain('text-accent-foreground');
    });

    it('should return the correct color class for resolved status', () => {
      expect(statusToColor('resolved')).toContain('text-success-foreground');
    });

    it('should return the correct color class for false_positive status', () => {
      expect(statusToColor('false_positive')).toContain('text-secondary-foreground');
    });

    it('should return the default color class for unknown status', () => {
      expect(statusToColor('unknown')).toContain('text-primary-foreground');
    });
  });
});
