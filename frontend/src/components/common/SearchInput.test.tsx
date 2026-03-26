import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { SearchInput } from './SearchInput';

describe('SearchInput', () => {
  it('renders with placeholder', () => {
    render(<SearchInput onSearch={vi.fn()} placeholder="Search tasks..." />);
    expect(screen.getByPlaceholderText('Search tasks...')).toBeInTheDocument();
  });

  it('renders with default placeholder', () => {
    render(<SearchInput onSearch={vi.fn()} />);
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
  });

  it('calls onSearch with debounced value', async () => {
    vi.useFakeTimers();
    const onSearch = vi.fn();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    render(<SearchInput onSearch={onSearch} />);

    const input = screen.getByPlaceholderText('Search...');
    await user.type(input, 'test');

    // onSearch should have been called with '' initially (mount)
    expect(onSearch).toHaveBeenCalledWith('');

    // Advance timers to trigger debounce
    vi.advanceTimersByTime(300);

    expect(onSearch).toHaveBeenCalledWith('test');

    vi.useRealTimers();
  });

  it('accepts external value prop', () => {
    render(<SearchInput onSearch={vi.fn()} value="external" />);
    expect(screen.getByDisplayValue('external')).toBeInTheDocument();
  });
});
