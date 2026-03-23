import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DarkModeToggle } from '../../components/DarkModeToggle';
import * as useDarkModeModule from '../../hooks/useDarkMode';

describe('DarkModeToggle', () => {
  const createMockHook = (isDark: boolean): useDarkModeModule.DarkModeReturn => ({
    isDark,
    toggle: vi.fn(),
    enable: vi.fn(),
    disable: vi.fn(),
  });

  it('renders sun icon in dark mode', () => {
    const mock = createMockHook(true);
    vi.spyOn(useDarkModeModule, 'useDarkMode').mockReturnValue(mock);
    render(<DarkModeToggle />);
    expect(screen.getByRole('button', { name: /라이트 모드로 전환/i })).toBeInTheDocument();
    expect(screen.getByTestId('sun-icon')).toBeInTheDocument();
  });

  it('renders moon icon in light mode', () => {
    const mock = createMockHook(false);
    vi.spyOn(useDarkModeModule, 'useDarkMode').mockReturnValue(mock);
    render(<DarkModeToggle />);
    expect(screen.getByRole('button', { name: /다크 모드로 전환/i })).toBeInTheDocument();
    expect(screen.getByTestId('moon-icon')).toBeInTheDocument();
  });

  it('calls toggle on click', () => {
    const mock = createMockHook(false);
    vi.spyOn(useDarkModeModule, 'useDarkMode').mockReturnValue(mock);
    render(<DarkModeToggle />);
    fireEvent.click(screen.getByRole('button'));
    expect(mock.toggle).toHaveBeenCalledOnce();
  });
});
