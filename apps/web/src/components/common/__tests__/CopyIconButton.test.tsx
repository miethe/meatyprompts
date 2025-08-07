import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CopyIconButton from '../CopyIconButton';

describe('CopyIconButton', () => {
  it('copies text to clipboard when clicked', async () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: {
        writeText,
      },
    });

    render(<CopyIconButton text="copy me" />);
    fireEvent.click(screen.getByRole('button'));
    expect(writeText).toHaveBeenCalledWith('copy me');
  });
});
