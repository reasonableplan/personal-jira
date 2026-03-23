import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchAutocomplete } from '../../components/SearchAutocomplete';
import { searchIssues } from '../../services/issueApi';

jest.mock('../../services/issueApi');
jest.useFakeTimers();

const mockSearchIssues = searchIssues as jest.MockedFunction<typeof searchIssues>;

const MOCK_RESULTS = [
  { id: '1', title: 'Fix login bug', labels: ['bug', 'auth'] },
  { id: '2', title: 'Add dashboard', labels: ['feature'] },
];

describe('SearchAutocomplete', () => {
  const onSelect = jest.fn();

  beforeEach(() => {
    onSelect.mockReset();
    mockSearchIssues.mockReset();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  it('renders search input with placeholder', () => {
    render(<SearchAutocomplete onSelect={onSelect} />);
    expect(screen.getByPlaceholderText('이슈 검색...')).toBeInTheDocument();
  });

  it('renders custom placeholder', () => {
    render(<SearchAutocomplete onSelect={onSelect} placeholder="Search" />);
    expect(screen.getByPlaceholderText('Search')).toBeInTheDocument();
  });

  it('shows dropdown with results after typing', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');

    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByText('Fix login bug')).toBeInTheDocument();
      expect(screen.getByText('Add dashboard')).toBeInTheDocument();
    });
  });

  it('displays labels as badges', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');
    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByText('bug')).toBeInTheDocument();
      expect(screen.getByText('auth')).toBeInTheDocument();
      expect(screen.getByText('feature')).toBeInTheDocument();
    });
  });

  it('calls onSelect when clicking a result', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');
    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByText('Fix login bug')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Fix login bug'));
    expect(onSelect).toHaveBeenCalledWith(MOCK_RESULTS[0]);
  });

  it('closes dropdown after selection', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');
    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByText('Fix login bug')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Fix login bug'));

    await waitFor(() => {
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });
  });

  it('shows loading indicator', async () => {
    mockSearchIssues.mockImplementation(() => new Promise(() => {}));
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');
    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  it('shows error message on failure', async () => {
    mockSearchIssues.mockRejectedValue(new Error('fail'));
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');
    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  it('navigates results with keyboard', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');
    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByText('Fix login bug')).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(screen.getAllByRole('option')[0]).toHaveAttribute('aria-selected', 'true');

    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(screen.getAllByRole('option')[1]).toHaveAttribute('aria-selected', 'true');

    fireEvent.keyDown(input, { key: 'Enter' });
    expect(onSelect).toHaveBeenCalledWith(MOCK_RESULTS[1]);
  });

  it('closes dropdown on Escape', async () => {
    mockSearchIssues.mockResolvedValue(MOCK_RESULTS);
    render(<SearchAutocomplete onSelect={onSelect} />);

    const input = screen.getByRole('combobox');
    await userEvent.setup({ advanceTimers: jest.advanceTimersByTime }).type(input, 'Fix');
    await act(async () => { jest.advanceTimersByTime(300); });

    await waitFor(() => {
      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: 'Escape' });

    await waitFor(() => {
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });
  });

  it('has correct aria attributes', () => {
    render(<SearchAutocomplete onSelect={onSelect} />);
    const input = screen.getByRole('combobox');
    expect(input).toHaveAttribute('aria-autocomplete', 'list');
    expect(input).toHaveAttribute('aria-expanded', 'false');
  });
});

function act(callback: () => Promise<void>): Promise<void> {
  return require('react').act(callback);
}
