import React, { useState } from 'react';
import CodeEditor, { LANGUAGE_OPTIONS, Language } from './CodeEditor';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './ui/dialog'; // Assuming shadcn dialog is in ui/dialog
import { Button } from './ui/button'; // Assuming shadcn button is in ui/button

// Simplified Prompt type used by this component
interface Prompt {
  title: string;
  body: string;
  output_format?: string;
  sample_input?: Record<string, unknown>;
  sample_output?: Record<string, unknown>;
  related_prompt_ids?: string[];
  link?: string;
}

interface PromptDetailModalProps {
  prompt: Prompt;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedPrompt: Prompt) => void;
}

const PromptDetailModal: React.FC<PromptDetailModalProps> = ({ prompt, isOpen, onClose, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState<Prompt>(prompt);
  const [language, setLanguage] = useState<Language>(
    prompt.output_format && LANGUAGE_OPTIONS.includes(prompt.output_format as Language)
      ? (prompt.output_format as Language)
      : 'plaintext'
  );

  const handleSave = () => {
    onSave(editedPrompt);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedPrompt(prompt);
    setIsEditing(false);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Prompt' : prompt.title}</DialogTitle>
          <DialogDescription>
            View or edit the details of your prompt.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Title */}
          <div className="grid grid-cols-4 items-center gap-4">
            <label htmlFor="title" className="text-right">Title</label>
            {isEditing ? (
              <input id="title" value={editedPrompt.title} onChange={(e) => setEditedPrompt({...editedPrompt, title: e.target.value})} className="col-span-3 p-2 border rounded" />
            ) : (
              <p className="col-span-3">{prompt.title}</p>
            )}
          </div>

          {/* Body */}
          <div className="grid grid-cols-4 items-start gap-4">
            <label htmlFor="body" className="text-right mt-2">Body</label>
            {isEditing ? (
              <div className="col-span-3">
                <select
                  className="mb-2 p-2 border rounded"
                  value={language}
                  onChange={(e) => {
                    const lang = e.target.value as Language;
                    setLanguage(lang);
                    setEditedPrompt({ ...editedPrompt, output_format: lang });
                  }}
                >
                  {LANGUAGE_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
                <CodeEditor
                  value={editedPrompt.body}
                  language={language}
                  onChange={(val) => setEditedPrompt({ ...editedPrompt, body: val })}
                />
              </div>
            ) : (
              <div className="col-span-3">
                <p className="whitespace-pre-wrap">{prompt.body}</p>
              </div>
            )}
          </div>

          {/* Sample Input */}
          <div className="grid grid-cols-4 items-start gap-4">
            <label htmlFor="sample_input" className="text-right mt-2">Sample Input</label>
            {isEditing ? (
                <div className="col-span-3">
                <CodeEditor
                  value={JSON.stringify(editedPrompt.sample_input ?? {}, null, 2)}
                  language="json"
                  onChange={(val) => {
                  try {
                    setEditedPrompt({
                    ...editedPrompt,
                    sample_input: JSON.parse(val || '{}'),
                    });
                  } catch (e) {
                    console.error('Invalid JSON in sample input:', e);
                  }
                  }}
                />
                </div>
            ) : (
              <pre className="col-span-3 whitespace-pre-wrap text-sm">
                {JSON.stringify(prompt.sample_input, null, 2)}
              </pre>
            )}
          </div>

          {/* Sample Output */}
          <div className="grid grid-cols-4 items-start gap-4">
            <label htmlFor="sample_output" className="text-right mt-2">Sample Output</label>
            {isEditing ? (
              <div className="col-span-3">
                <CodeEditor
                  value={JSON.stringify(editedPrompt.sample_output ?? {}, null, 2)}
                  language="json"
                  onChange={(val) => {
                  try {
                    setEditedPrompt({
                    ...editedPrompt,
                    sample_output: JSON.parse(val || '{}'),
                    });
                  } catch (e) {
                    console.error('Invalid JSON in sample output:', e);
                  }
                  }}
                />
              </div>
            ) : (
              <pre className="col-span-3 whitespace-pre-wrap text-sm">
                {JSON.stringify(prompt.sample_output, null, 2)}
              </pre>
            )}
          </div>

          {/* Related Prompts */}
          {prompt.related_prompt_ids && (
            <div className="grid grid-cols-4 items-center gap-4">
              <span className="text-right">Related</span>
              <div className="col-span-3 flex flex-col space-y-1">
                {prompt.related_prompt_ids.map((id) => (
                  <a key={id} href={`/prompts/${id}`} className="text-blue-500 underline">
                    {id}
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* External Link */}
          {prompt.link && (
            <div className="grid grid-cols-4 items-center gap-4">
              <span className="text-right">Link</span>
              <a href={prompt.link} className="col-span-3 text-blue-500 underline">
                {prompt.link}
              </a>
            </div>
          )}

        </div>

        <DialogFooter>
          {isEditing ? (
            <>
              <Button variant="outline" onClick={handleCancel}>Cancel</Button>
              <Button onClick={handleSave}>Save Changes</Button>
            </>
          ) : (
            <>
              <Button variant="outline" onClick={onClose}>Close</Button>
              <Button onClick={() => setIsEditing(true)}>Edit</Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default PromptDetailModal;
