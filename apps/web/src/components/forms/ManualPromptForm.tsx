import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { ManualPromptInput } from '@/types/Prompt';
import { usePrompt } from '@/contexts/PromptContext';
import CreatableMultiSelect from '../form/CreatableMultiSelect';
import TagInput from '../form/TagInput';
import { useLookups } from '@/contexts/LookupContext';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  use_cases: z.array(z.string()).min(1, 'Use case is required'),
  target_models: z.array(z.string()).min(1, 'At least one model is required'),
  providers: z.array(z.string()).optional(),
  integrations: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
  body: z.string().min(1, 'Prompt text is required'),
  access_control: z.enum(['public', 'private', 'team-only', 'role-based']),
});

const ManualPromptForm = ({ onClose }) => {
  const { createPrompt } = usePrompt();
  const { lookups, addLookup } = useLookups();


  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ManualPromptInput>({
    resolver: zodResolver(schema),
    defaultValues: {
      target_models: [],
      providers: [],
      integrations: [],
      use_cases: [],
      tags: [],
    }
  });

  const onSubmit = async (data: ManualPromptInput) => {
    console.log('ManualPromptForm submitted:', data);
    try {
      await createPrompt(data);
      onClose();
    } catch (error) {
      console.error('Failed to create prompt:', error);
      // Optionally show error to user
    }
  };

  const handleCreateOption = (type: 'target_models' | 'providers' | 'integrations' | 'use_cases') => (inputValue: string) => {
    addLookup(type, inputValue);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Title and Body are unchanged */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title
        </label>
        <input
          id="title"
          {...register('title')}
          className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md"
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
          className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md"
        />
        {errors.body && <p className="text-red-500">{errors.body.message}</p>}
      </div>

      {/* Target Models */}
      <div>
        <label htmlFor="target_models" className="block text-sm font-medium text-gray-700">
          Target Models
        </label>
        <Controller
          name="target_models"
          control={control}
          render={({ field }) => (
            <CreatableMultiSelect
              isLoading={lookups.loading}
              options={lookups.target_models}
              value={lookups.target_models.filter(o => field.value?.includes(o.value))}
              onChange={(options) => field.onChange(options.map(o => o.value))}
              onCreateOption={handleCreateOption('target_models')}
              placeholder="Select or create models..."
            />
          )}
        />
        {errors.target_models && <p className="text-red-500">{errors.target_models.message}</p>}
      </div>

      {/* Use Cases */}
      <div>
        <label htmlFor="use_cases" className="block text-sm font-medium text-gray-700">Use Cases</label>
        <Controller name="use_cases" control={control} render={({ field }) => (
            <CreatableMultiSelect isLoading={lookups.loading} options={lookups.use_cases} value={lookups.use_cases.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('use_cases')} />
        )} />
        {errors.use_cases && <p className="text-red-500">{errors.use_cases.message}</p>}
      </div>

      {/* Providers */}
      <div>
        <label htmlFor="providers" className="block text-sm font-medium text-gray-700">Providers</label>
        <Controller name="providers" control={control} render={({ field }) => (
            <CreatableMultiSelect isLoading={lookups.loading} options={lookups.providers} value={lookups.providers.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('providers')} />
        )} />
        {errors.providers && <p className="text-red-500">{errors.providers.message}</p>}
      </div>

      {/* Integrations */}
      <div>
        <label htmlFor="integrations" className="block text-sm font-medium text-gray-700">Integrations</label>
        <Controller name="integrations" control={control} render={({ field }) => (
            <CreatableMultiSelect isLoading={lookups.loading} options={lookups.integrations} value={lookups.integrations.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('integrations')} />
        )} />
        {errors.integrations && <p className="text-red-500">{errors.integrations.message}</p>}
      </div>

      {/* Tags */}
      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700">Tags</label>
        <Controller name="tags" control={control} render={({ field }) => (
            <TagInput tags={field.value?.map(t => ({id: t, text: t, className: ''})) || []} setTags={(newTags) => field.onChange(newTags.map(t => t.text))} placeholder="Add tags..." />
        )} />
        {errors.tags && <p className="text-red-500">{errors.tags.message}</p>}
      </div>

      <div>
        <label htmlFor="access_control" className="block text-sm font-medium text-gray-700">
          Access Control
        </label>
        <select
          id="access_control"
          {...register('access_control')}
          className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md"
        >
          <option value="public">Public</option>
          <option value="private">Private</option>
          <option value="team-only">Team Only</option>
          <option value="role-based">Role Based</option>
        </select>
        {errors.access_control && <p className="text-red-500">{errors.access_control.message}</p>}
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
