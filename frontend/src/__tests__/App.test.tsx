import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(document.querySelector('#root, [data-testid], main, div')).toBeTruthy();
  });

  it('displays app title', () => {
    render(<App />);
    expect(screen.getByText(/Personal Jira/i)).toBeInTheDocument();
  });
});
