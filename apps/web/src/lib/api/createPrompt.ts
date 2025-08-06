import { ManualPromptInput, Prompt } from '@/types/Prompt';

export async function createPrompt(data: ManualPromptInput): Promise<Prompt> {
  const response = await fetch('http://localhost:8000/api/v1/prompts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to create prompt');
  }

  return response.json();
}
