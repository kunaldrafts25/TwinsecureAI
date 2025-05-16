import { describe, it, expect } from 'vitest';

// A simple test suite that doesn't rely on DOM
describe('Simple Tests', () => {
  it('should pass basic arithmetic', () => {
    expect(1 + 1).toBe(2);
  });

  it('should handle string operations', () => {
    expect('hello ' + 'world').toBe('hello world');
  });

  it('should work with arrays', () => {
    const arr = [1, 2, 3];
    expect(arr.length).toBe(3);
    expect(arr).toContain(2);
  });

  it('should work with objects', () => {
    const obj = { name: 'TwinSecure', type: 'Security Platform' };
    expect(obj.name).toBe('TwinSecure');
    expect(obj).toHaveProperty('type');
  });
});
