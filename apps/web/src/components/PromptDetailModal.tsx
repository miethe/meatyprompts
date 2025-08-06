import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './ui/dialog'; // Assuming shadcn dialog is in ui/dialog
import { Button } from './ui/button'; // Assuming shadcn button is in ui/button

// This is a placeholder for the actual Prompt data type
interface Prompt {
  title: string;
  purpose: string[];
  models: string[];
  platforms: string[];
  body: string;
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
           <div className="grid grid-cols-4 items-center gap-4">
            <label htmlFor="body" className="text-right">Body</label>
            {isEditing ? (
              <textarea id="body" value={editedPrompt.body} onChange={(e) => setEditedPrompt({...editedPrompt, body: e.target.value})} className="col-span-3 p-2 border rounded h-24" />
            ) : (
              <p className="col-span-3 whitespace-pre-wrap">{prompt.body}</p>
            )}
          </div>

          {/* Add other fields here (Purpose, Models, Platforms) in a similar fashion */}

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
