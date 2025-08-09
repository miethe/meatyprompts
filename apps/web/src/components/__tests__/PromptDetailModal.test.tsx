import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import PromptDetailModal from '../PromptDetailModal';
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

jest.mock('@uiw/react-codemirror', () => ({
  __esModule: true,
  default: ({ value, onChange }: { value: string; onChange: (val: string) => void }) => (
    <textarea data-testid="codemirror" value={value} onChange={(e) => onChange(e.target.value)} />
  ),
  lineNumbers: () => () => null,
}));

jest.mock('../editor/MarkdownEditor', () => {
  const React = require('react');
  return {
    __esModule: true,
    default: ({ value, onChange }: any) => (
      <textarea data-testid="mdeditor" value={value} onChange={(e) => onChange(e.target.value)} />
    ),
  };
});

describe('PromptDetailModal', () => {
  const basePrompt = {
    title: 'Test',
    body: 'initial',
    sample_input: { a: 1 },
    sample_output: { b: 2 },
  };

  it('renders markdown editor when editing', () => {
    render(
      <PromptDetailModal
        prompt={basePrompt}
        isOpen={true}
        onClose={() => {}}
        onSave={() => {}}
      />
    );

    fireEvent.click(screen.getByText('Edit'));
    expect(screen.getByTestId('mdeditor')).toBeInTheDocument();
  });

  it('serializes JSON', () => {
    const handleSave = jest.fn();
    render(
      <PromptDetailModal
        prompt={basePrompt}
        isOpen={true}
        onClose={() => {}}
        onSave={handleSave}
      />
    );
    fireEvent.click(screen.getByText('Edit'));
    const editors = screen.getAllByTestId('codemirror');
    fireEvent.change(editors[0], { target: { value: '{"foo":1}' } });
    fireEvent.change(editors[1], { target: { value: '{"bar":2}' } });
    fireEvent.click(screen.getByText('Save Changes'));
    expect(handleSave).toHaveBeenCalledWith(
      expect.objectContaining({
        sample_input: { foo: 1 },
        sample_output: { bar: 2 },
      })
    );
  });

  it('copies body to clipboard', async () => {
    (copyText as jest.Mock).mockResolvedValue(undefined);
    render(
      <PromptDetailModal
        prompt={basePrompt}
        isOpen={true}
        onClose={() => {}}
        onSave={() => {}}
      />
    );
    fireEvent.click(screen.getByLabelText('Copy body'));
    await waitFor(() => expect(copyText).toHaveBeenCalledWith('initial'));
    expect(track).toHaveBeenCalledWith('prompt_copied', expect.objectContaining({ variant: 'body', source: 'detail' }));
  });
});
