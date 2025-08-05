import React, { useContext } from 'react';
import { PromptContext } from '@/contexts/PromptContext';
import PromptCard from '@/components/PromptCard';

const PromptsPage = () => {
  const { state } = useContext(PromptContext);

  return (
    <div>
      <h1 className="text-2xl font-bold">Prompts</h1>
      <div className="grid grid-cols-1 gap-4 mt-4 sm:grid-cols-2 lg:grid-cols-3">
        {state.prompts.length > 0 ? (
          state.prompts.map((prompt) => (
            <PromptCard key={prompt.id} prompt={prompt} />
          ))
        ) : (
          <p>No prompts found.</p>
        )}
      </div>
    </div>
  );
};

export default PromptsPage;
