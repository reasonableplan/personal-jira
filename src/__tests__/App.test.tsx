import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from '../App';

describe('App', () => {
  it('renders layout with sidebar on dashboard', () => {
    render(<App />);
    expect(screen.getByRole('complementary')).toBeInTheDocument();
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('renders dashboard by default', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: '대시보드' })).toBeInTheDocument();
  });

  it('renders not found for unknown routes', () => {
    window.history.pushState({}, '', '/unknown-path');
    render(<App />);
    expect(screen.getByText('404')).toBeInTheDocument();
  });
});
