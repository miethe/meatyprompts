import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { useRouter } from 'next/router';
import Sidebar from '@/components/Sidebar';

jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

describe('Navigation', () => {
  it('navigates to the dashboard page when the dashboard link is clicked', () => {
    const push = jest.fn();
    (useRouter as unknown as jest.Mock).mockImplementation(() => ({
      push,
      pathname: '/',
    }));

    render(<Sidebar />);
    fireEvent.click(screen.getByText('Dashboard'));
    expect(push).toHaveBeenCalledWith('/dashboard');
  });

  it('navigates to the prompts page when the prompts link is clicked', () => {
    const push = jest.fn();
    (useRouter as unknown as jest.Mock).mockImplementation(() => ({
      push,
      pathname: '/',
    }));

    render(<Sidebar />);
    fireEvent.click(screen.getByText('Prompts'));
    expect(push).toHaveBeenCalledWith('/prompts');
  });

  it('navigates to the new prompt page when the button is clicked', () => {
    const push = jest.fn();
    (useRouter as unknown as jest.Mock).mockImplementation(() => ({
      push,
      pathname: '/',
    }));

    render(<Sidebar />);
    fireEvent.click(screen.getByText('New Prompt'));
    expect(push).toHaveBeenCalledWith('/prompts/new');
  });
});
