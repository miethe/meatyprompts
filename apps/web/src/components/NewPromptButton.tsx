import React, { useState } from 'react';
import NewPromptModal from './modals/NewPromptModal';

const NewPromptButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className="px-4 py-2 font-bold text-white bg-blue-500 rounded hover:bg-blue-700"
      >
        New Prompt
      </button>
      {isModalOpen && <NewPromptModal onClose={() => setIsModalOpen(false)} />}
    </>
  );
};

export default NewPromptButton;
