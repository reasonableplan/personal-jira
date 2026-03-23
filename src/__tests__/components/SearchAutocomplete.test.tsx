import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { SearchAutocomplete } from '../../components/SearchAutocomplete';
import type { SearchSuggestion } from '../../types/search';

const DEBOUNCE_MS = 300;

const MOCK_SUGGESTIONS: SearchSuggestion[] = [
  { id: '1', text: 'Login page bug', type: 'issue', status: 'open' },
  { id: '2', text: 'Login API endpoint', type: 'issue', status: 'closed' },
  { id: '3', text: 'Dashboard layout', type: 'issue', status: 'in_progress' },
];

describe('SearchAutocomplete', () => {
  const onSearch = vi.fn();
  const onSelect = vi.fn();
  const fetchSuggestions = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    fetchSuggestions.mockResolvedValue(MOCK_SUGGESTIONS);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders search input with placeholder', () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
        placeholder="Search issues..."
      />
    );
    expect(screen.getByPlaceholderText('Search issues...')).toBeInTheDocument();
  });

  it('debounces input before fetching suggestions', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Log' } });
    });
    expect(fetchSuggestions).not.toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });
    expect(fetchSuggestions).toHaveBeenCalledWith('Log');
  });

  it('shows suggestions dropdown after fetching', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    await waitFor(() => {
      expect(screen.getByText('Login page bug')).toBeInTheDocument();
      expect(screen.getByText('Login API endpoint')).toBeInTheDocument();
    });
  });

  it('does not fetch for queries shorter than minimum length', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
        minQueryLength={3}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Lo' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    expect(fetchSuggestions).not.toHaveBeenCalled();
  });

  it('navigates suggestions with arrow keys', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    await waitFor(() => {
      expect(screen.getByText('Login page bug')).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(screen.getByText('Login page bug').closest('li')).toHaveClass('highlighted');

    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(screen.getByText('Login API endpoint').closest('li')).toHaveClass('highlighted');

    fireEvent.keyDown(input, { key: 'ArrowUp' });
    expect(screen.getByText('Login page bug').closest('li')).toHaveClass('highlighted');
  });

  it('selects suggestion on Enter key', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    await waitFor(() => {
      expect(screen.getByText('Login page bug')).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(onSelect).toHaveBeenCalledWith(MOCK_SUGGESTIONS[0]);
  });

  it('selects suggestion on click', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    await waitFor(() => {
      expect(screen.getByText('Login page bug')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Login page bug'));
    expect(onSelect).toHaveBeenCalledWith(MOCK_SUGGESTIONS[0]);
  });

  it('closes dropdown on Escape', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    await waitFor(() => {
      expect(screen.getByText('Login page bug')).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: 'Escape' });
    expect(screen.queryByText('Login page bug')).not.toBeInTheDocument();
  });

  it('calls onSearch on form submit', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
    });

    fireEvent.submit(input.closest('form')!);
    expect(onSearch).toHaveBeenCalledWith('Login');
  });

  it('shows loading spinner while fetching', async () => {
    fetchSuggestions.mockReturnValue(new Promise(() => {}));
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    expect(screen.getByTestId('search-spinner')).toBeInTheDocument();
  });

  it('displays status badges on suggestions', async () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Login' } });
      vi.advanceTimersByTime(DEBOUNCE_MS);
    });

    await waitFor(() => {
      expect(screen.getByText('open')).toBeInTheDocument();
      expect(screen.getByText('closed')).toBeInTheDocument();
    });
  });

  it('has correct aria attributes for accessibility', () => {
    render(
      <SearchAutocomplete
        onSearch={onSearch}
        onSelect={onSelect}
        fetchSuggestions={fetchSuggestions}
      />
    );
    const input = screen.getByRole('combobox');
    expect(input).toHaveAttribute('aria-autocomplete', 'list');
    expect(input).toHaveAttribute('aria-expanded', 'false');
  });
});
