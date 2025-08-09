import React, { useState } from 'react';
import CodeEditor from './CodeEditor';
import MarkdownEditor from './editor/MarkdownEditor';
import CopyMenu from './common/CopyMenu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './ui/dialog'; // Assuming shadcn dialog is in ui/dialog
import { Button } from './ui/button'; // Assuming shadcn button is in ui/button
import { Prompt } from '@/types/Prompt';

interface PromptDetailModalProps {
  prompt: Prompt;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedPrompt: Prompt) => void;
  onDuplicate?: () => void;
}

const PromptDetailModal: React.FC<PromptDetailModalProps> = ({ prompt, isOpen, onClose, onSave, onDuplicate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState<Prompt>(prompt);

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
                <div className="flex items-center mb-2">
                  <CopyMenu prompt={editedPrompt as any} source="detail" />
                </div>
                <MarkdownEditor
                  value={editedPrompt.body}
                  onChange={(val) => setEditedPrompt({ ...editedPrompt, body: val })}
                />
              </div>
            ) : (
              <div className="col-span-3 flex items-start">
                <p className="whitespace-pre-wrap flex-1">{prompt.body}</p>
                <CopyMenu prompt={prompt as any} source="detail" />
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
              {onDuplicate && (
                <Button variant="outline" aria-label="Duplicate prompt" onClick={onDuplicate}>Duplicate</Button>
              )}
              <Button variant="outline" onClick={() => setIsEditing(true)}>Edit</Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default PromptDetailModal;
