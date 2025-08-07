import React from 'react';
import CodeMirror, { lineNumbers } from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import {
  defaultHighlightStyle, syntaxHighlighting,
  bracketMatching, foldGutter
} from "@codemirror/language"
import {
  closeBrackets
} from "@codemirror/autocomplete"

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
      extensions= {[
        extensionsForLanguage(language),
        // A line number gutter
        lineNumbers(),
        foldGutter(),
        // A gutter with code folding markers
        syntaxHighlighting(defaultHighlightStyle),
        // Highlight matching brackets near cursor
        bracketMatching(),
        // Automatically close brackets
        closeBrackets()
      ]}
      onChange={(val) => onChange(val)}
      className='text-black'
    />
  );
};

export default CodeEditor;
