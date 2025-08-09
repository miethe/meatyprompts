import React from 'react';
import CopyMenu from './common/CopyMenu';
import { Prompt } from '@/types/Prompt';

interface PromptCardProps {
  prompt: Prompt;
  onClick: () => void;
  onDuplicate?: () => void;
}

const Tag: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span className="bg-gray-700 text-gray-300 text-xs font-medium me-2 px-2.5 py-0.5 rounded">
    {children}
  </span>
);

const PromptCard: React.FC<PromptCardProps> = ({ prompt, onClick, onDuplicate }) => {
  const allTags = prompt.tags || [];
  const firstLine = (prompt.body ?? '').split('\n')[0];

  return (
    <div
      className="p-4 bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer flex flex-col justify-between h-full"
      onClick={onClick}
    >
      <div>
        <h3 className="text-lg font-bold text-white truncate">{prompt.title}</h3>
        <div className="flex items-start mt-1">
          <p className="text-sm text-gray-400 truncate flex-1">{firstLine}</p>
          <CopyMenu prompt={prompt as any} source="card" />
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {allTags.slice(0, 4).map((tag, index) => (
            <Tag key={index}>{tag}</Tag>
          ))}
          {allTags.length > 4 && <Tag>...</Tag>}
        </div>
      </div>
      <div className="mt-4 flex justify-between items-center">
        <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-teal-600 bg-teal-200">
          v{prompt.version}
        </span>
        {onDuplicate && (
          <button
            type="button"
            className="text-xs text-blue-500 underline"
            aria-label="Duplicate prompt"
            onClick={(e) => {
              e.stopPropagation();
              onDuplicate();
            }}
          >
            Duplicate
          </button>
        )}
      </div>
    </div>
  );
};

export default PromptCard;
