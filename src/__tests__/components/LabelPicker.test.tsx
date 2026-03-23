import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { LabelPicker } from '../../components/LabelPicker';

const AVAILABLE = ['frontend', 'backend', 'bug', 'feature', 'urgent'];

describe('LabelPicker', () => {
  const defaultProps = {
    availableLabels: AVAILABLE,
    selected: [] as string[],
    onChange: jest.fn(),
  };

  beforeEach(() => jest.clearAllMocks());

  test('renders all available labels', () => {
    render(<LabelPicker {...defaultProps} />);
    for (const label of AVAILABLE) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
  });

  test('marks selected labels', () => {
    render(<LabelPicker {...defaultProps} selected={['bug', 'urgent']} />);
    expect(screen.getByText('bug').closest('button')).toHaveAttribute(
      'aria-pressed',
      'true'
    );
    expect(screen.getByText('frontend').closest('button')).toHaveAttribute(
      'aria-pressed',
      'false'
    );
  });

  test('adds label on click', () => {
    render(<LabelPicker {...defaultProps} selected={['bug']} />);
    fireEvent.click(screen.getByText('frontend'));
    expect(defaultProps.onChange).toHaveBeenCalledWith(['bug', 'frontend']);
  });

  test('removes label on click if already selected', () => {
    render(<LabelPicker {...defaultProps} selected={['bug', 'frontend']} />);
    fireEvent.click(screen.getByText('bug'));
    expect(defaultProps.onChange).toHaveBeenCalledWith(['frontend']);
  });

  test('renders custom input for new label', () => {
    render(<LabelPicker {...defaultProps} allowCustom />);
    expect(
      screen.getByPlaceholderText('Add label...')
    ).toBeInTheDocument();
  });

  test('adds custom label on Enter', () => {
    render(
      <LabelPicker {...defaultProps} selected={[]} allowCustom />
    );
    const input = screen.getByPlaceholderText('Add label...');
    fireEvent.change(input, { target: { value: 'custom-label' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(defaultProps.onChange).toHaveBeenCalledWith(['custom-label']);
  });

  test('does not add duplicate custom label', () => {
    render(
      <LabelPicker {...defaultProps} selected={['bug']} allowCustom />
    );
    const input = screen.getByPlaceholderText('Add label...');
    fireEvent.change(input, { target: { value: 'bug' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(defaultProps.onChange).not.toHaveBeenCalled();
  });
});
