import React, { useState } from 'react';
import ManualPromptForm from '../forms/ManualPromptForm';

const NewPromptModal = ({ onClose }) => {
  const [step, setStep] = useState(0);

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <div className="flex flex-col space-y-4">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 font-bold text-white bg-blue-500 rounded hover:bg-blue-700"
            >
              Manual
            </button>
            <button
              disabled
              className="px-4 py-2 font-bold text-white bg-gray-400 rounded cursor-not-allowed"
              aria-disabled="true"
            >
              AI Automated (Coming Soon)
            </button>
          </div>
        );
      case 1:
        return <ManualPromptForm onClose={onClose} />;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">New Prompt</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            &times;
          </button>
        </div>
        {renderStep()}
      </div>
    </div>
  );
};

export default NewPromptModal;
