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
    const onSearch = vi.fn();

    render(<SearchInput onSearch={onSearch} />);

    // onSearch should have been called with '' initially (mount)
    expect(onSearch).toHaveBeenCalledWith('');

    const input = screen.getByPlaceholderText('Search...');
    await userEvent.type(input, 'test');

    // Wait for debounce (300ms) to trigger
    await vi.waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test');
    });
  });

  it('accepts external value prop', () => {
    render(<SearchInput onSearch={vi.fn()} value="external" />);
    expect(screen.getByDisplayValue('external')).toBeInTheDocument();
  });
});
