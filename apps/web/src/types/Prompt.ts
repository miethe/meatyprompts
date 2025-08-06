export interface Prompt {
  id: string;
  prompt_id: string;
  version: string;
  title: string;
  body: string;
  use_cases: string[];
  access_control: 'public' | 'private' | 'team-only' | 'role-based';
  target_models?: string[];
  providers?: string[];
  integrations?: string[];
  category?: string;
  complexity?: string;
  audience?: string;
  status?: string;
  input_schema?: Record<string, unknown>;
  output_format?: string;
  llm_parameters?: Record<string, unknown>;
  success_metrics?: Record<string, unknown>;
  sample_input?: Record<string, unknown>;
  sample_output?: Record<string, unknown>;
  related_prompt_ids?: string[];
  link?: string;
  tags?: string[];
  createdAt: string;
  updatedAt: string;
}

export type ManualPromptInput = Omit<Prompt, 'id' | 'version' | 'createdAt' | 'updatedAt' | 'prompt_id'>;
