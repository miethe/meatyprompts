import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PromptCard from '../PromptCard';

describe('PromptCard', () => {
  const prompt = {
    id: '1',
    title: 'Test Prompt',
    body: 'This is the body of the prompt.',
    version: 1,
    purpose: ['testing'],
    models: ['gpt-4'],
    tags: ['tag1', 'tag2'],
  };

  it('renders the prompt title, body, version, and tags', () => {
    render(<PromptCard prompt={prompt} onClick={() => {}} />);

    expect(screen.getByText('Test Prompt')).toBeInTheDocument();
    expect(screen.getByText('This is the body of the prompt.')).toBeInTheDocument();
    expect(screen.getByText('v1')).toBeInTheDocument();
    expect(screen.getByText('tag1')).toBeInTheDocument();
  });

  it('calls the onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<PromptCard prompt={prompt} onClick={handleClick} />);

    fireEvent.click(screen.getByText('Test Prompt'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('copies body text when copy icon clicked', () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(<PromptCard prompt={prompt} onClick={() => {}} />);
    const button = screen.getByLabelText('Copy to clipboard');
    fireEvent.click(button);
    expect(writeText).toHaveBeenCalledWith('This is the body of the prompt.');
  });
});
