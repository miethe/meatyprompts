import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PromptCard from '../PromptCard';
import { copyText } from '../../lib/clipboard';
import { track } from '../../lib/analytics';

jest.mock('../../lib/clipboard');
jest.mock('../../lib/analytics');
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: any) => {
      const translations: Record<string, string> = {
        'copy.quick': 'Copy body',
        'copy.menuTitle': 'Copy options',
        'copy.body': 'Copy body',
        'toast.copied': `Copied ${opts?.variant}`,
      };
      return translations[key] || key;
    },
  }),
}));

describe('PromptCard', () => {
  const prompt = {
    id: '1',
    title: 'Test Prompt',
    body: 'This is the body of the prompt.',
    version: '1',
    purpose: ['testing'],
    models: ['gpt-4'],
    tags: ['tag1', 'tag2'],
  };

  beforeEach(() => {
    (copyText as jest.Mock).mockResolvedValue(undefined);
  });

  it('renders the prompt title, body, version, and tags', () => {
    render(<PromptCard prompt={prompt} onClick={() => {}} onDuplicate={() => {}} />);

    expect(screen.getByText('Test Prompt')).toBeInTheDocument();
    expect(screen.getByText('This is the body of the prompt.')).toBeInTheDocument();
    expect(screen.getByText('v1')).toBeInTheDocument();
    expect(screen.getByText('tag1')).toBeInTheDocument();
    expect(screen.getByLabelText('Duplicate prompt')).toBeInTheDocument();
  });

  it('calls the onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<PromptCard prompt={prompt} onClick={handleClick} />);

    fireEvent.click(screen.getByText('Test Prompt'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('copies body text when quick copy clicked', async () => {
    render(<PromptCard prompt={prompt} onClick={() => {}} />);
    const button = screen.getByLabelText('Copy body');
    fireEvent.click(button);
    await waitFor(() => expect(copyText).toHaveBeenCalledWith('This is the body of the prompt.'));
    expect(track).toHaveBeenCalledWith('prompt_copied', expect.objectContaining({ variant: 'body', source: 'card' }));
    expect(screen.getByText('Copied Copy body')).toBeInTheDocument();
  });

  it('calls onDuplicate when duplicate clicked', () => {
    const handleDuplicate = jest.fn();
    render(<PromptCard prompt={prompt} onClick={() => {}} onDuplicate={handleDuplicate} />);
    const button = screen.getByLabelText('Duplicate prompt');
    fireEvent.click(button);
    expect(handleDuplicate).toHaveBeenCalled();
  });
});
