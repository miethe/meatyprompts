import { Prompt } from '@/types/Prompt';

const prompts: Prompt[] = [
  {
    id: '1',
    title: 'Summarize this article',
    subtitle: 'A prompt for summarizing articles',
    model: 'gpt-3.5-turbo',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    title: 'Translate this text to French',
    subtitle: 'A prompt for translating text to French',
    model: 'gpt-4',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export const fetchPrompts = async (): Promise<Prompt[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(prompts);
    }, 500);
  });
};
