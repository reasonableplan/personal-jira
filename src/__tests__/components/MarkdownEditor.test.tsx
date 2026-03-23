import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MarkdownEditor } from '../../components/MarkdownEditor';

describe('MarkdownEditor', () => {
  const defaultProps = {
    value: '',
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders textarea with value', () => {
    render(<MarkdownEditor {...defaultProps} value="# Hello" />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveValue('# Hello');
  });

  test('calls onChange when typing', () => {
    render(<MarkdownEditor {...defaultProps} />);
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: '## New' } });
    expect(defaultProps.onChange).toHaveBeenCalledWith('## New');
  });

  test('renders placeholder', () => {
    render(<MarkdownEditor {...defaultProps} placeholder="Write markdown..." />);
    expect(screen.getByPlaceholderText('Write markdown...')).toBeInTheDocument();
  });

  test('toggles between write and preview tabs', () => {
    render(<MarkdownEditor {...defaultProps} value="**bold**" />);
    const previewTab = screen.getByRole('tab', { name: /preview/i });
    fireEvent.click(previewTab);
    expect(screen.getByTestId('markdown-preview')).toBeInTheDocument();
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });

  test('renders markdown as HTML in preview', () => {
    render(<MarkdownEditor {...defaultProps} value="**bold**" />);
    fireEvent.click(screen.getByRole('tab', { name: /preview/i }));
    const preview = screen.getByTestId('markdown-preview');
    expect(preview.innerHTML).toContain('<strong>bold</strong>');
  });

  test('switches back to write tab', () => {
    render(<MarkdownEditor {...defaultProps} value="text" />);
    fireEvent.click(screen.getByRole('tab', { name: /preview/i }));
    fireEvent.click(screen.getByRole('tab', { name: /write/i }));
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  test('respects disabled prop', () => {
    render(<MarkdownEditor {...defaultProps} disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  test('applies minRows to textarea', () => {
    render(<MarkdownEditor {...defaultProps} minRows={8} />);
    expect(screen.getByRole('textbox')).toHaveAttribute('rows', '8');
  });
});
