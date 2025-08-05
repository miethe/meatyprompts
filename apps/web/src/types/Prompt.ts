export interface Prompt {
  id: string;
  title: string;
  purpose?: string;
  models: string[];
  tools?: string[];
  tags?: string[];
  body: string;
  visibility: 'private' | 'public' | 'team';
  version: number;
  createdAt: string;
  prompt_id: string;
}

export type ManualPromptInput = Omit<Prompt, 'id' | 'version' | 'createdAt' | 'prompt_id'>;
