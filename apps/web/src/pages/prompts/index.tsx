import React, { useContext, useState } from 'react';
import { PromptContext } from '@/contexts/PromptContext';
import PromptCard from '@/components/PromptCard';
import PromptListFilters from '@/components/filters/PromptListFilters';
import PromptDetailModal from '@/components/PromptDetailModal';
import NewPromptModal from '@/components/modals/NewPromptModal';
import { Button } from '@/components/ui/button';

// Placeholder for the actual Prompt data type
interface Prompt {
  id: string;
  title: string;
  body: string;
  version: number;
  tags?: string[];
  purpose?: string[];
  models?: string[];
  tools?: string[];
  platforms?: string[];
}


const PromptsPage = () => {
  const { state } = useContext(PromptContext);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isNewPromptOpen, setIsNewPromptOpen] = useState(false);

  const handleCardClick = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedPrompt(null);
  };

  const handleSavePrompt = (updatedPrompt: Prompt) => {
    console.log('Saving prompt:', updatedPrompt);
    handleCloseModal();
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Prompts</h1>
        <PromptListFilters />
      </div>

      <div className="grid grid-cols-1 gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-3">
        {state.prompts.length > 0 ? (
          state.prompts.map((prompt) => (
            <PromptCard
              key={prompt.id}
              prompt={prompt}
              onClick={() => handleCardClick(prompt)}
            />
          ))
        ) : (
          <div className="col-span-full text-center py-10">
            <p className="mb-4">No prompts found.</p>
            <Button onClick={() => setIsNewPromptOpen(true)}>New Prompt</Button>
          </div>
        )}
      </div>

      {selectedPrompt && (
        <PromptDetailModal
          prompt={selectedPrompt}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onSave={handleSavePrompt}
        />
      )}
      {isNewPromptOpen && (
        <NewPromptModal onClose={() => setIsNewPromptOpen(false)} />
      )}
    </div>
  );
};

export default PromptsPage;
