import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SelectField } from '../../components/SelectField';

const OPTIONS = [
  { value: 'a', label: 'Alpha' },
  { value: 'b', label: 'Beta' },
  { value: 'c', label: 'Charlie' },
];

describe('SelectField', () => {
  const defaultProps = {
    label: 'Test Select',
    value: 'a',
    options: OPTIONS,
    onChange: jest.fn(),
  };

  beforeEach(() => jest.clearAllMocks());

  test('renders label', () => {
    render(<SelectField {...defaultProps} />);
    expect(screen.getByLabelText('Test Select')).toBeInTheDocument();
  });

  test('renders all options', () => {
    render(<SelectField {...defaultProps} />);
    const select = screen.getByLabelText('Test Select');
    expect(select.querySelectorAll('option')).toHaveLength(3);
  });

  test('selects current value', () => {
    render(<SelectField {...defaultProps} value="b" />);
    expect(screen.getByLabelText('Test Select')).toHaveValue('b');
  });

  test('calls onChange with new value', () => {
    render(<SelectField {...defaultProps} />);
    fireEvent.change(screen.getByLabelText('Test Select'), {
      target: { value: 'c' },
    });
    expect(defaultProps.onChange).toHaveBeenCalledWith('c');
  });

  test('renders error message', () => {
    render(<SelectField {...defaultProps} error="Required" />);
    expect(screen.getByText('Required')).toBeInTheDocument();
  });

  test('disables when disabled prop set', () => {
    render(<SelectField {...defaultProps} disabled />);
    expect(screen.getByLabelText('Test Select')).toBeDisabled();
  });
});
