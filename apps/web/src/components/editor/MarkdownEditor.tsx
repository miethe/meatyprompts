import React, { useEffect, useRef, useState, useCallback } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import { lineNumbers } from '@uiw/react-codemirror';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  onSave?: (value: string) => void;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({ value, onChange, onSave }) => {
  const editorRef = useRef<CodeMirror>(null);
  const [showPreview, setShowPreview] = useState(true);
  const [dirty, setDirty] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const saveNow = useCallback(() => {
    if (onSave) {
      onSave(value);
    }
    setDirty(false);
  }, [onSave, value]);

  useEffect(() => {
    setDirty(true);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      if (onSave) {
        onSave(value);
      }
      setDirty(false);
    }, 1500);
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, onSave]);

  const handleKey = useCallback(
    (e: KeyboardEvent) => {
      if (e.metaKey && e.key === 's') {
        e.preventDefault();
        saveNow();
      }
      if (e.metaKey && e.key === '/') {
        e.preventDefault();
        setShowPreview(prev => !prev);
      }
      if (e.key === 'Escape') {
        (e.target as HTMLElement).blur();
      }
    },
    [saveNow]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [handleKey]);

  const applyFormat = (wrap: string, wrapAfter?: string) => {
    const view = (editorRef.current as any)?.view;
    if (!view) return;
    const { from, to } = view.state.selection.main;
    const selected = view.state.sliceDoc(from, to);
    const after = wrapAfter ?? wrap;
    view.dispatch({
      changes: { from, to, insert: `${wrap}${selected}${after}` },
      selection: { anchor: from + wrap.length, head: from + wrap.length + selected.length },
    });
    view.focus();
  };

  return (
    <div className="border rounded">
      <div className="flex items-center border-b p-2 space-x-2">
        <button type="button" aria-label="Bold" onClick={() => applyFormat('**')}><b>B</b></button>
        <button type="button" aria-label="Italic" onClick={() => applyFormat('*')}><i>I</i></button>
        <button type="button" aria-label="Heading" onClick={() => applyFormat('# ' ,'')}><span className="font-bold">H</span></button>
        <button type="button" aria-label="Link" onClick={() => applyFormat('[', '](url)')}>🔗</button>
        <button type="button" aria-label="Code" onClick={() => applyFormat('`')}>{'{'}code{'}'}</button>
        <button type="button" aria-label="OL" onClick={() => applyFormat('1. ' ,'')}>&#35;.</button>
        <button type="button" aria-label="UL" onClick={() => applyFormat('- ' ,'')}>•</button>
        <span className="ml-auto text-sm" aria-label="dirty-state">{dirty ? '● Unsaved' : 'Saved'}</span>
      </div>
      <div className="flex">
        <div className="w-1/2">
          <CodeMirror
            ref={editorRef}
            value={value}
            height="200px"
            extensions={[lineNumbers(), markdown()]}
            onChange={onChange}
            className="text-black"
          />
        </div>
        {showPreview && (
          <div className="w-1/2 p-2 overflow-auto prose max-w-none" aria-label="preview">
            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
              {value}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarkdownEditor;
