import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LabelBadge } from './LabelBadge';
import type { Label } from '@/types/label';

describe('LabelBadge', () => {
  const label: Label = {
    id: '1',
    name: 'backend',
    color: '#3b82f6',
    created_at: '2026-03-20T08:00:00Z',
  };

  it('renders the label name', () => {
    render(<LabelBadge label={label} />);
    expect(screen.getByText('backend')).toBeInTheDocument();
  });

  it('applies the label color as background', () => {
    render(<LabelBadge label={label} />);
    const badge = screen.getByText('backend');
    expect(badge).toHaveStyle({ backgroundColor: '#3b82f6' });
  });

  it('applies custom className', () => {
    render(<LabelBadge label={label} className="custom-class" />);
    expect(screen.getByText('backend')).toHaveClass('custom-class');
  });
});
