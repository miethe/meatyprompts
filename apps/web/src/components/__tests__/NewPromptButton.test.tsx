import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import NewPromptButton from '../NewPromptButton';

describe('NewPromptButton', () => {
  it('calls the onClick handler when clicked', () => {
    const onClick = jest.fn();
    render(<NewPromptButton onClick={onClick} />);
    fireEvent.click(screen.getByText('New Prompt'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
