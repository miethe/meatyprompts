import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { ManualPromptInput } from '@/types/Prompt';
import { usePrompt } from '@/contexts/PromptContext';
import CreatableMultiSelect from '../form/CreatableMultiSelect';
import TagInput from '../form/TagInput';
import { useLookups } from '@/contexts/LookupContext';
import CodeEditor, { LANGUAGE_OPTIONS, Language } from '../CodeEditor';
import { useFieldHelp } from '@/contexts/FieldHelpContext';
import RadixTooltip from '../ui/RadixTooltip';
import LanguageSelect from '../form/LanguageSelect';
import { useTranslation } from 'react-i18next';

const jsonField = z
  .string()
  .optional()
  .refine(val => {
    if (!val || val.trim() === '') return true;
    try {
      JSON.parse(val);
      return true;
    } catch {
      return false;
    }
  }, { message: 'Invalid JSON' })
  .transform(val => {
    if (val && val.trim() !== '') {
      try {
        return JSON.parse(val);
      } catch {
        return undefined;
      }
    }
    return undefined;
  });

export const manualPromptFormSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  use_cases: z.array(z.string()).min(1, 'Use case is required'),
  target_models: z.array(z.string()).min(1, 'At least one model is required'),
  providers: z.array(z.string()).optional(),
  integrations: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
  body: z.string().min(1, 'Prompt text is required'),
  category: z.string().optional(),
  complexity: z.string().optional(),
  audience: z.string().optional(),
  status: z.string().optional(),
  input_schema: jsonField,
  llm_parameters: jsonField,
  sample_input: jsonField,
  sample_output: jsonField,
  related_prompt_ids: z.array(z.string()).optional(),
  link: z.string().optional(),
  output_format: z.string().optional(),
  sample_input_language: z.string().optional(),
  sample_output_language: z.string().optional(),
  access_control: z.enum(['public', 'private', 'team-only', 'role-based']),
});

type ManualPromptFormProps = {
  onClose: () => void;
  readOnly?: boolean;
};

const ManualPromptForm = ({ onClose, readOnly = false }: ManualPromptFormProps) => {
  const { createPrompt } = usePrompt();
  const { lookups, addLookup } = useLookups();
  const [activeTab, setActiveTab] = useState<'basic' | 'advanced' | 'governance'>('basic');
  const { help } = useFieldHelp();
  const { t } = useTranslation();

  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(manualPromptFormSchema),
    defaultValues: {
      target_models: [],
      providers: [],
      integrations: [],
      use_cases: [],
      tags: [],
      related_prompt_ids: [],
      category: '',
      complexity: '',
      audience: '',
      status: '',
      input_schema: '',
      llm_parameters: '',
      sample_input: '',
      sample_output: '',
      link: '',
      access_control: 'public',
      body: '',
      output_format: 'plaintext',
      sample_input_language: 'json',
      sample_output_language: 'json',
    }
  });

  const [language, setLanguage] = useState<Language>(control._defaultValues.output_format || 'plaintext');
  const [sampleInputLanguage, setSampleInputLanguage] = useState<Language>(control._defaultValues.sample_input_language || 'json');
  const [sampleOutputLanguage, setSampleOutputLanguage] = useState<Language>(control._defaultValues.sample_output_language || 'json');

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
      <div className="flex mb-4 space-x-4 border-b">
        <button type="button" onClick={() => setActiveTab('basic')} className={`px-3 py-1 text-black ${activeTab === 'basic' ? 'border-b-2 border-blue-500' : ''}`}>{t('form.basic')}</button>
        <button type="button" onClick={() => setActiveTab('advanced')} className={`px-3 py-1 text-black ${activeTab === 'advanced' ? 'border-b-2 border-blue-500' : ''}`}>{t('form.advanced')}</button>
        <button type="button" onClick={() => setActiveTab('governance')} className={`px-3 py-1 text-black ${activeTab === 'governance' ? 'border-b-2 border-blue-500' : ''}`}>{t('form.governance')}</button>
      </div>

      {activeTab === 'basic' && (
        <div className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              {t('form.title')}
            </label>
            <input
              id="title"
              {...register('title')}
              className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md"
              readOnly={readOnly}
              disabled={readOnly}
            />
            {typeof errors.title?.message === 'string' && <p className="text-red-500">{errors.title.message}</p>}
          </div>
          <div>
            <label htmlFor="body" className="block text-sm font-medium text-gray-700">
              {t('form.promptText')}
            </label>
            <LanguageSelect
              value={language}
              onChange={(lang) => {
                setLanguage(lang);
                setValue('output_format', lang);
              }}
              disabled={readOnly}
            />
            <Controller
              name="body"
              control={control}
              render={({ field }) => (
                <CodeEditor
                  value={field.value}
                  language={language}
                  onChange={field.onChange}
                  readOnly={readOnly}
                />
              )}
            />
            <input type="hidden" {...register('output_format')} />
            {typeof errors.body?.message === 'string' && <p className="text-red-500">{errors.body.message}</p>}
          </div>
          <div>
            <label htmlFor="target_models" className="block text-sm font-medium text-gray-700">
              {t('form.targetModels')}{help.target_models && (
                <RadixTooltip content={help.target_models}>
                  <span className="ml-1 text-gray-400 cursor-help" role="img" aria-label="Information">ⓘ</span>
                </RadixTooltip>
              )}
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
                  placeholder={t('form.selectOrCreateModels')}
                />
              )}
            />
            {typeof errors.target_models?.message === 'string' && <p className="text-red-500">{errors.target_models.message}</p>}
          </div>
          <div>
            <label htmlFor="use_cases" className="block text-sm font-medium text-gray-700">{t('form.useCases')}</label>
            <Controller name="use_cases" control={control} render={({ field }) => (
                <CreatableMultiSelect isLoading={lookups.loading} options={lookups.use_cases} value={lookups.use_cases.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('use_cases')} />
            )} />
            {typeof errors.use_cases?.message === 'string' && <p className="text-red-500">{errors.use_cases.message}</p>}
          </div>
          <div>
            <label htmlFor="providers" className="block text-sm font-medium text-gray-700">{t('form.providers')}{help.providers && (
              <RadixTooltip content={help.providers}>
                <span className="ml-1 text-gray-400 cursor-help" role="img" aria-label="Information">ⓘ</span>
              </RadixTooltip>
            )}</label>
            <Controller name="providers" control={control} render={({ field }) => (
                <CreatableMultiSelect isLoading={lookups.loading} options={lookups.providers} value={lookups.providers.filter(o => field.value?.includes(o.value))} onChange={(options) => field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('providers')} />
            )} />
            {typeof errors.providers?.message === 'string' && <p className="text-red-500">{errors.providers.message}</p>}
          </div>
          <div>
            <label htmlFor="integrations" className="block text-sm font-medium text-gray-700">
              {t('form.integrations')}
              {help.integrations && (
                <RadixTooltip content={help.integrations}>
                  <span className="ml-1 text-gray-400 cursor-help" role="img" aria-label="Information">ⓘ</span>
                </RadixTooltip>
              )}
            </label>
            <Controller name="integrations" control={control} render={({ field }) => (
                <CreatableMultiSelect isLoading={lookups.loading} options={lookups.integrations}
                  value={lookups.integrations.filter(o => field.value?.includes(o.value))} onChange={(options) =>
                  field.onChange(options.map(o => o.value))} onCreateOption={handleCreateOption('integrations')}
                />
            )} />
            {typeof errors.integrations?.message === 'string' && <p className="text-red-500">{errors.integrations.message}</p>}
          </div>
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700">{t('form.tags')}</label>
            <Controller name="tags" control={control} render={({ field }) => (
                <TagInput tags={field.value?.map((t: string) => ({id: t, text: t, className: ''})) || []}
                  setTags={(newTags) => field.onChange(newTags.map(t => t.text))} placeholder={t('form.addTags')}
                />
            )} />
            {typeof errors.tags?.message === 'string' && <p className="text-red-500">{errors.tags.message}</p>}
          </div>
        </div>
      )}

      {activeTab === 'advanced' && (
        <div className="space-y-4">
          <div>
            <label htmlFor="input_schema" className="block text-sm font-medium text-gray-700">{t('form.inputSchema')}</label>
            <textarea id="input_schema" {...register('input_schema')} className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md" />
            {errors.input_schema && <p className="text-red-500">{errors.input_schema.message as string}</p>}
          </div>
          <div>
            <label htmlFor="llm_parameters" className="block text-sm font-medium text-gray-700">{t('form.llmParameters')}</label>
            <textarea id="llm_parameters" {...register('llm_parameters')} className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md" />
            {errors.llm_parameters && <p className="text-red-500">{errors.llm_parameters.message as string}</p>}
          </div>
          <div>
            <label htmlFor="sample_input" className="block text-sm font-medium text-gray-700">{t('form.sampleInput')}</label>
            <LanguageSelect
              value={sampleInputLanguage}
              onChange={(lang) => {
                setSampleInputLanguage(lang);
                setValue('sample_input_language', lang);
              }}
              disabled={readOnly}
            />
            <Controller
              name="sample_input"
              control={control}
              render={({ field }) => (
                <CodeEditor
                  value={field.value}
                  language={sampleInputLanguage}
                  onChange={field.onChange}
                  readOnly={readOnly}
                />
              )}
            />
            {errors.sample_input && <p className="text-red-500">{errors.sample_input.message as string}</p>}
          </div>
          <div>
            <label htmlFor="sample_output" className="block text-sm font-medium text-gray-700">{t('form.sampleOutput')}</label>
            <LanguageSelect
              value={sampleOutputLanguage}
              onChange={(lang) => {
                setSampleOutputLanguage(lang);
                setValue('sample_output_language', lang);
              }}
              disabled={readOnly}
            />
            <Controller
              name="sample_output"
              control={control}
              render={({ field }) => (
                <CodeEditor
                  value={field.value}
                  language={sampleOutputLanguage}
                  onChange={field.onChange}
                  readOnly={readOnly}
                />
              )}
            />
            {typeof errors.sample_output?.message === 'string' && <p className="text-red-500">{errors.sample_output.message}</p>}
          </div>
          <div>
            <label htmlFor="related_prompt_ids" className="block text-sm font-medium text-gray-700">{t('form.relatedPromptIds')}</label>
            <Controller name="related_prompt_ids" control={control} render={({ field }) => (
                <TagInput tags={field.value?.map((t: string) => ({ id: t, text: t, className: '' })) || []} setTags={(newTags) => field.onChange(newTags.map(t => t.text))} placeholder={t('form.addPromptIds')} />
            )} />
            {typeof errors.related_prompt_ids?.message === 'string' && <p className="text-red-500">{errors.related_prompt_ids.message}</p>}
          </div>
        </div>
      )}

      {activeTab === 'governance' && (
        <div className="space-y-4">
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700">{t('form.category')}</label>
            <input id="category" {...register('category')} className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md" />
            {typeof errors.category?.message === 'string' && <p className="text-red-500">{errors.category.message}</p>}
          </div>
          <div>
            <label htmlFor="complexity" className="block text-sm font-medium text-gray-700">{t('form.complexity')}</label>
            <input id="complexity" {...register('complexity')} className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md" />
            {typeof errors.complexity?.message === 'string' && <p className="text-red-500">{errors.complexity.message}</p>}
          </div>
          <div>
            <label htmlFor="audience" className="block text-sm font-medium text-gray-700">{t('form.audience')}</label>
            <input id="audience" {...register('audience')} className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md" />
            {typeof errors.audience?.message === 'string' && <p className="text-red-500">{errors.audience.message}</p>}
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">{t('form.status')}</label>
            <input id="status" {...register('status')} className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md" />
            {typeof errors.status?.message === 'string' && <p className="text-red-500">{errors.status.message}</p>}
          </div>
          <div>
            <label htmlFor="link" className="block text-sm font-medium text-gray-700">{t('form.link')}</label>
            <input id="link" {...register('link')} className="block w-full mt-1 text-black border-gray-300 rounded-md shadow-md" />
            {typeof errors.link?.message === 'string' && <p className="text-red-500">{errors.link.message}</p>}
          </div>
          <div>
            <label htmlFor="access_control" className="block text-sm font-medium text-gray-700">
              {t('form.accessControl')}
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
            {typeof errors.access_control?.message === 'string' && <p className="text-red-500">{errors.access_control.message}</p>}
          </div>
        </div>
      )}

      {/* Add other form fields here */}
      <div className="flex justify-end mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 mr-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
        >
          {t('form.cancel')}
        </button>
        <button
          type="submit"
          className="px-4 py-2 font-bold text-white bg-blue-500 rounded hover:bg-blue-700"
        >
          {t('form.submit')}
        </button>
      </div>
    </form>
  );
};

export default ManualPromptForm;
