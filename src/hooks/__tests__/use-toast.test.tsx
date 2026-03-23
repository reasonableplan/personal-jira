import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useToast, ToastProvider } from '../use-toast';
import { ReactNode } from 'react';

const wrapper = ({ children }: { children: ReactNode }) => (
  <ToastProvider>{children}</ToastProvider>
);

describe('useToast', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('throws when used outside provider', () => {
    expect(() => renderHook(() => useToast())).toThrow(
      'useToast must be used within ToastProvider'
    );
  });

  it('starts with empty toasts', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    expect(result.current.toasts).toEqual([]);
  });

  it('adds a toast with generated id', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    act(() => {
      result.current.addToast({ type: 'success', message: 'Created' });
    });
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0]).toMatchObject({
      type: 'success',
      message: 'Created',
    });
    expect(result.current.toasts[0].id).toBeDefined();
  });

  it('removes a toast by id', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    let toastId: string;
    act(() => {
      toastId = result.current.addToast({ type: 'info', message: 'Hello' });
    });
    act(() => {
      result.current.removeToast(toastId);
    });
    expect(result.current.toasts).toHaveLength(0);
  });

  it('auto-dismisses after duration', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    act(() => {
      result.current.addToast({
        type: 'success',
        message: 'Temp',
        duration: 3000,
      });
    });
    expect(result.current.toasts).toHaveLength(1);
    act(() => {
      vi.advanceTimersByTime(3000);
    });
    expect(result.current.toasts).toHaveLength(0);
  });

  it('uses default duration when not specified', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    act(() => {
      result.current.addToast({ type: 'info', message: 'Default' });
    });
    expect(result.current.toasts).toHaveLength(1);
    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(result.current.toasts).toHaveLength(0);
  });

  it('supports multiple toasts', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    act(() => {
      result.current.addToast({ type: 'success', message: 'First' });
      result.current.addToast({ type: 'error', message: 'Second' });
    });
    expect(result.current.toasts).toHaveLength(2);
  });

  it('limits max toasts', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    act(() => {
      for (let i = 0; i < 7; i++) {
        result.current.addToast({ type: 'info', message: `Toast ${i}` });
      }
    });
    expect(result.current.toasts.length).toBeLessThanOrEqual(5);
  });
});
