import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CopyMenu from '../CopyMenu';
import { copyText } from '../../../lib/clipboard';
import { track } from '../../../lib/analytics';
import type { Prompt } from '../../../types/Prompt';

jest.mock('../../../lib/clipboard');
jest.mock('../../../lib/analytics');

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: any) => {
      const translations: Record<string, string> = {
        'copy.quick': 'Copy body',
        'copy.menuTitle': 'Copy options',
        'copy.body': 'Copy body',
        'copy.frontMatter': 'Copy body + front-matter',
        'copy.json': 'Copy JSON',
        'toast.copied': `Copied ${opts?.variant}`,
      };
      return translations[key] || key;
    },
  }),
}));

describe('CopyMenu', () => {
  const prompt: Prompt = {
    id: '1',
    prompt_id: 'p1',
    version: 'v1',
    title: 'T',
    body: 'Body text',
    use_cases: [],
    access_control: 'private',
    createdAt: '',
    updatedAt: '',
  } as any;

  beforeEach(() => {
    (copyText as jest.Mock).mockResolvedValue(undefined);
  });

  it('renders quick copy button and menu', () => {
    render(<CopyMenu prompt={prompt} source="card" />);
    expect(screen.getByLabelText('Copy body')).toBeInTheDocument();
    expect(screen.getByLabelText('Copy options')).toBeInTheDocument();
  });

  it('copies body on quick copy', async () => {
    render(<CopyMenu prompt={prompt} source="card" />);
    fireEvent.click(screen.getByLabelText('Copy body'));
    await waitFor(() => expect(copyText).toHaveBeenCalledWith('Body text'));
    expect(track).toHaveBeenCalledWith('prompt_copied', expect.objectContaining({ prompt_id: '1', variant: 'body', source: 'card' }));
    expect(screen.getByText('Copied Copy body')).toBeInTheDocument();
  });

  it('provides three menu options', () => {
    render(<CopyMenu prompt={prompt} source="card" />);
    fireEvent.click(screen.getByLabelText('Copy options'));
    expect(screen.getByText('Copy body')).toBeInTheDocument();
    expect(screen.getByText('Copy body + front-matter')).toBeInTheDocument();
    expect(screen.getByText('Copy JSON')).toBeInTheDocument();
  });

  it('handles JSON variant selection', async () => {
    render(<CopyMenu prompt={prompt} source="detail" />);
    fireEvent.click(screen.getByLabelText('Copy options'));
    fireEvent.click(screen.getByText('Copy JSON'));
    await waitFor(() => expect(copyText).toHaveBeenCalledWith(expect.stringContaining('"body": "Body text"')));
    expect(track).toHaveBeenCalledWith('prompt_copied', expect.objectContaining({ variant: 'json', source: 'detail' }));
  });
});
