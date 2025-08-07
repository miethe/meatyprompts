import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Plus } from 'lucide-react';
import ThemedButton from '../ThemedButton';
import { ThemeProvider, themes } from '@/theme';

describe('ThemedButton', () => {
  it('applies theme colors', () => {
    render(
      <ThemeProvider initialTheme="dark">
        <ThemedButton label="New Prompt" Icon={Plus} />
      </ThemeProvider>
    );
    const button = screen.getByRole('button');
    expect(button).toHaveStyle(`background-color: ${themes.dark.colors.primary}`);
  });

  it('handles click events', () => {
    const onClick = jest.fn();
    render(
      <ThemeProvider>
        <ThemedButton label="New Prompt" Icon={Plus} onClick={onClick} />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
