import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import PromptDetailModal from '../PromptDetailModal';

jest.mock('@uiw/react-codemirror', () => {
  return ({ value, onChange }: { value: string; onChange: (val: string) => void }) => (
    <textarea data-testid="codemirror" value={value} onChange={(e) => onChange(e.target.value)} />
  );
});

describe('PromptDetailModal', () => {
  const basePrompt = {
    title: 'Test',
    body: 'initial',
    output_format: 'json',
    sample_input: { a: 1 },
    sample_output: { b: 2 },
  };

  it('defaults language to output_format', () => {
    render(
      <PromptDetailModal
        prompt={basePrompt}
        isOpen={true}
        onClose={() => {}}
        onSave={() => {}}
      />
    );

    fireEvent.click(screen.getByText('Edit'));
    const select = screen.getByRole('combobox');
    expect(select).toHaveValue('json');
  });

  it('switches language and serializes JSON', () => {
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
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'javascript' } });
    const editors = screen.getAllByTestId('codemirror');
    fireEvent.change(editors[1], { target: { value: '{"foo":1}' } });
    fireEvent.change(editors[2], { target: { value: '{"bar":2}' } });
    fireEvent.click(screen.getByText('Save Changes'));
    expect(handleSave).toHaveBeenCalledWith(
      expect.objectContaining({
        output_format: 'javascript',
        sample_input: { foo: 1 },
        sample_output: { bar: 2 },
      })
    );
  });
});
