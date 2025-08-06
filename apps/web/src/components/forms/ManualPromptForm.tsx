import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { ManualPromptInput } from '@/types/Prompt';
import { usePrompt } from '@/contexts/PromptContext';
import CreatableMultiSelect from '../form/CreatableMultiSelect';
import TagInput from '../form/TagInput';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  purpose: z.array(z.string()).optional(),
  models: z.array(z.string()).min(1, 'At least one model is required'),
  tools: z.array(z.string()).optional(),
  platforms: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
  body: z.string().min(1, 'Prompt text is required'),
  visibility: z.enum(['private', 'public', 'team']),
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
      models: [],
      tools: [],
      platforms: [],
      purpose: [],
      tags: [],
    }
  });

  const onSubmit = async (data: ManualPromptInput) => {
    console.log('ManualPromptForm submitted:', data);
    // This will now pass the correct data structure to the context/API
    // await createPrompt(data);
    onClose();
  };

  const handleCreateOption = (type: 'models' | 'tools' | 'platforms' | 'purposes') => (inputValue: string) => {
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

      {/* Models */}
      <div>
        <label htmlFor="models" className="block text-sm font-medium text-gray-700">
          Models
        </label>
        <Controller
          name="models"
          control={control}
          render={({ field }) => (
            <CreatableMultiSelect
              isLoading={lookups.loading}
              options={lookups.models}
              value={lookups.models.filter(o => field.value?.includes(o.value))}
              onChange={(options) => field.onChange(options.map(o => o.value))}
              onCreateOption={handleCreateOption('models')}
              placeholder="Select or create models..."
            />
          )}
        />
        {errors.models && <p className="text-red-500">{errors.models.message}</p>}
      </div>

      {/* Purpose */}
      <div>
        <label htmlFor="purpose" className="block text-sm font-medium text-gray-700">Purpose</label>
        <Controller name="purpose" control={control} render={({ field }) => (
            <CreatableMultiSelect isLoading={lookups.loading} options={lookups.purposes} value={lookups.purposes.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('purposes')} />
        )} />
        {errors.purpose && <p className="text-red-500">{errors.purpose.message}</p>}
      </div>

      {/* Tools */}
      <div>
        <label htmlFor="tools" className="block text-sm font-medium text-gray-700">Tools</label>
        <Controller name="tools" control={control} render={({ field }) => (
            <CreatableMultiSelect isLoading={lookups.loading} options={lookups.tools} value={lookups.tools.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('tools')} />
        )} />
        {errors.tools && <p className="text-red-500">{errors.tools.message}</p>}
      </div>

      {/* Platforms */}
      <div>
        <label htmlFor="platforms" className="block text-sm font-medium text-gray-700">Platforms</label>
        <Controller name="platforms" control={control} render={({ field }) => (
            <CreatableMultiSelect isLoading={lookups.loading} options={lookups.platforms} value={lookups.platforms.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('platforms')} />
        )} />
        {errors.platforms && <p className="text-red-500">{errors.platforms.message}</p>}
      </div>

      {/* Tags */}
      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700">Tags</label>
        <Controller name="tags" control={control} render={({ field }) => (
            <TagInput tags={field.value?.map(t => ({id: t, text: t})) || []} setTags={(newTags) => field.onChange(newTags.map(t => t.text))} placeholder="Add tags..." />
        )} />
        {errors.tags && <p className="text-red-500">{errors.tags.message}</p>}
      </div>

      <div>
        <label htmlFor="visibility" className="block text-sm font-medium text-gray-700">
          Visibility
        </label>
        <select
          id="visibility"
          {...register('visibility')}
          className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md"
        >
          <option value="private">Private</option>
          <option value="public">Public</option>
          <option value="team">Team</option>
        </select>
        {errors.visibility && <p className="text-red-500">{errors.visibility.message}</p>}
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
