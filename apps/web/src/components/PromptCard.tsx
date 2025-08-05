import React from 'react';

const PromptCard = ({ prompt }) => {
  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h3 className="text-lg font-bold">{prompt.title}</h3>
      <p className="text-sm text-gray-400">{prompt.subtitle}</p>
    </div>
  );
};

export default PromptCard;
