import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useDarkMode } from '../../hooks/useDarkMode';

const STORAGE_KEY = 'theme-mode';

describe('useDarkMode', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
  });

  it('defaults to light mode when no stored preference', () => {
    const { result } = renderHook(() => useDarkMode());
    expect(result.current.isDark).toBe(false);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('restores dark mode from localStorage', () => {
    localStorage.setItem(STORAGE_KEY, 'dark');
    const { result } = renderHook(() => useDarkMode());
    expect(result.current.isDark).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('restores light mode from localStorage', () => {
    localStorage.setItem(STORAGE_KEY, 'light');
    const { result } = renderHook(() => useDarkMode());
    expect(result.current.isDark).toBe(false);
  });

  it('toggles from light to dark', () => {
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.toggle());
    expect(result.current.isDark).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
  });

  it('toggles from dark to light', () => {
    localStorage.setItem(STORAGE_KEY, 'dark');
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.toggle());
    expect(result.current.isDark).toBe(false);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(localStorage.getItem(STORAGE_KEY)).toBe('light');
  });

  it('enables dark mode explicitly', () => {
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.enable());
    expect(result.current.isDark).toBe(true);
    expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
  });

  it('disables dark mode explicitly', () => {
    localStorage.setItem(STORAGE_KEY, 'dark');
    const { result } = renderHook(() => useDarkMode());
    act(() => result.current.disable());
    expect(result.current.isDark).toBe(false);
    expect(localStorage.getItem(STORAGE_KEY)).toBe('light');
  });

  it('respects prefers-color-scheme when no stored preference', () => {
    const matchMediaMock = vi.fn().mockReturnValue({ matches: true });
    Object.defineProperty(window, 'matchMedia', { value: matchMediaMock, writable: true });
    const { result } = renderHook(() => useDarkMode());
    expect(result.current.isDark).toBe(true);
  });
});
