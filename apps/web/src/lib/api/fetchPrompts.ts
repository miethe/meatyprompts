import { Prompt } from '@/types/Prompt';

export const fetchPrompts = async (): Promise<Prompt[]> => {
  const response = await fetch('http://localhost:8000/api/v1/prompts');
  if (!response.ok) {
    throw new Error('Failed to fetch prompts');
  }
  return response.json();
};
