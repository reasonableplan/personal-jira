import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ToastContainer } from '../toast-container';
import type { Toast } from '../../types/toast';

const mockRemoveToast = vi.fn();

vi.mock('../../hooks/use-toast', () => ({
  useToast: () => ({
    toasts: mockToasts,
    addToast: vi.fn(),
    removeToast: mockRemoveToast,
  }),
}));

let mockToasts: Toast[] = [];

describe('ToastContainer', () => {
  beforeEach(() => {
    mockToasts = [];
    vi.clearAllMocks();
  });

  it('renders nothing when no toasts', () => {
    const { container } = render(<ToastContainer />);
    expect(container.querySelector('[data-testid="toast-container"]')?.children).toHaveLength(0);
  });

  it('renders toast messages', () => {
    mockToasts = [
      { id: '1', type: 'success', message: 'Saved!' },
      { id: '2', type: 'error', message: 'Failed!' },
    ];
    render(<ToastContainer />);
    expect(screen.getByText('Saved!')).toBeInTheDocument();
    expect(screen.getByText('Failed!')).toBeInTheDocument();
  });

  it('applies correct type class', () => {
    mockToasts = [{ id: '1', type: 'error', message: 'Oops' }];
    render(<ToastContainer />);
    const toast = screen.getByText('Oops').closest('[data-testid="toast-item"]');
    expect(toast?.className).toContain('error');
  });

  it('calls removeToast on dismiss click', () => {
    mockToasts = [{ id: '1', type: 'info', message: 'Note' }];
    render(<ToastContainer />);
    fireEvent.click(screen.getByLabelText('dismiss'));
    expect(mockRemoveToast).toHaveBeenCalledWith('1');
  });

  it('renders toast type icons', () => {
    mockToasts = [
      { id: '1', type: 'success', message: 'OK' },
      { id: '2', type: 'error', message: 'Err' },
      { id: '3', type: 'warning', message: 'Warn' },
      { id: '4', type: 'info', message: 'Info' },
    ];
    render(<ToastContainer />);
    expect(screen.getAllByTestId('toast-icon')).toHaveLength(4);
  });
});
