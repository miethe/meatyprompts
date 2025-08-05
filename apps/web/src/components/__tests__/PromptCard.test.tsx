import React from 'react';
import { render, screen } from '@testing-library/react';
import PromptCard from '../PromptCard';

describe('PromptCard', () => {
  it('renders the prompt title and subtitle', () => {
    const prompt = {
      id: '1',
      title: 'Test Prompt',
      subtitle: 'Test Subtitle',
      model: 'gpt-3.5-turbo',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    render(<PromptCard prompt={prompt} />);
    expect(screen.getByText('Test Prompt')).toBeInTheDocument();
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
  });
});
