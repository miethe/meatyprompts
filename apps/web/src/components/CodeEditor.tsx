import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';

export const LANGUAGE_OPTIONS = ['plaintext', 'json', 'javascript', 'python'] as const;
export type Language = typeof LANGUAGE_OPTIONS[number];

const extensionsForLanguage = (language: Language) => {
  switch (language) {
    case 'json':
      return [json()];
    case 'javascript':
      return [javascript()];
    case 'python':
      return [python()];
    default:
      return [];
  }
};

interface CodeEditorProps {
  value: string;
  language: Language;
  onChange: (value: string) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ value, language, onChange }) => {
  return (
    <CodeMirror
      value={value}
      height="200px"
      extensions={extensionsForLanguage(language)}
      onChange={(val) => onChange(val)}
    />
  );
};

export default CodeEditor;
