import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import PromptDetailModal from '../PromptDetailModal';

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

  it('copies body to clipboard', () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(
      <PromptDetailModal
        prompt={basePrompt}
        isOpen={true}
        onClose={() => {}}
        onSave={() => {}}
      />
    );
    fireEvent.click(screen.getByLabelText('Copy to clipboard'));
    expect(writeText).toHaveBeenCalledWith('initial');
  });

  it('renders duplicate button and fires handler', () => {
    const handleDuplicate = jest.fn();
    render(
      <PromptDetailModal
        prompt={basePrompt}
        isOpen={true}
        onClose={() => {}}
        onSave={() => {}}
        onDuplicate={handleDuplicate}
      />
    );
    const button = screen.getByLabelText('Duplicate prompt');
    fireEvent.click(button);
    expect(handleDuplicate).toHaveBeenCalled();
  });
});
