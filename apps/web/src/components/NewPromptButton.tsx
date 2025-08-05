import React from 'react';

const NewPromptButton = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 font-bold text-white bg-blue-500 rounded hover:bg-blue-700"
    >
      New Prompt
    </button>
  );
};

export default NewPromptButton;
