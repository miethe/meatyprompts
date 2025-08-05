import React, { useState } from 'react';

const PromptWizard = ({ onClose }) => {
  const [model, setModel] = useState('');
  const [task, setTask] = useState('');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">New Prompt</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            &times;
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700">
              Model
            </label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="block w-full mt-1"
            >
              <option value="">Select a model</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
            </select>
          </div>
          <div>
            <label htmlFor="task" className="block text-sm font-medium text-gray-700">
              Task
            </label>
            <select
              id="task"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              className="block w-full mt-1"
            >
              <option value="">Select a task</option>
              <option value="summarize">Summarize</option>
              <option value="translate">Translate</option>
            </select>
          </div>
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 mr-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
          <button className="px-4 py-2 font-bold text-white bg-blue-500 rounded hover:bg-blue-700">
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default PromptWizard;
