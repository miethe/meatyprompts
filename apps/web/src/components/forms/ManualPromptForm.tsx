import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { ManualPromptInput } from '@/types/Prompt';
import { usePrompt } from '@/contexts/PromptContext';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  purpose: z.string().optional(),
  models: z.array(z.string()).min(1, 'At least one model is required'),
  tools: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
  body: z.string().min(1, 'Prompt text is required'),
  visibility: z.enum(['private', 'public', 'team']),
});

const ManualPromptForm = ({ onClose }) => {
  const { createPrompt } = usePrompt();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ManualPromptInput>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: ManualPromptInput) => {
    await createPrompt(data);
    onClose();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title
        </label>
        <input
          id="title"
          {...register('title')}
          className="block w-full mt-1"
        />
        {errors.title && <p className="text-red-500">{errors.title.message}</p>}
      </div>
      <div>
        <label htmlFor="body" className="block text-sm font-medium text-gray-700">
          Prompt Text
        </label>
        <textarea
          id="body"
          {...register('body')}
          className="block w-full mt-1"
        />
        {errors.body && <p className="text-red-500">{errors.body.message}</p>}
      </div>
      {/* Add other form fields here */}
      <div className="flex justify-end mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 mr-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 font-bold text-white bg-blue-500 rounded hover:bg-blue-700"
        >
          Submit
        </button>
      </div>
    </form>
  );
};

export default ManualPromptForm;
