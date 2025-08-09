import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import MarkdownEditor from '../MarkdownEditor';

jest.mock('@uiw/react-codemirror', () => {
  const React = require('react');
  return {
    __esModule: true,
    default: React.forwardRef(({ value, onChange }: any, ref) =>
      React.createElement('textarea', { ref, value, onChange: (e: any) => onChange(e.target.value) })
    ),
    lineNumbers: () => () => null,
  };
});

jest.useFakeTimers();

describe('MarkdownEditor', () => {
  it('updates preview and autosaves', () => {
    const handleSave = jest.fn();
    const handleChange = jest.fn();
    render(<MarkdownEditor value="" onChange={handleChange} onSave={handleSave} />);
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: '**bold**' } });
    act(() => {
      jest.advanceTimersByTime(1600);
    });
    expect(handleSave).toHaveBeenCalledWith('**bold**');
    const preview = screen.getByLabelText('preview');
    expect(preview.querySelector('strong')).toBeTruthy();
  });

  it('handles keyboard shortcuts', () => {
    const handleSave = jest.fn();
    render(<MarkdownEditor value="text" onChange={() => {}} onSave={handleSave} />);
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 's', metaKey: true }));
    });
    expect(handleSave).toHaveBeenCalled();
    const preview = screen.getByLabelText('preview');
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: '/', metaKey: true }));
    });
    expect(screen.queryByLabelText('preview')).toBeNull();
    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: '/', metaKey: true }));
    });
    expect(screen.queryByLabelText('preview')).toBeTruthy();
  });
});
