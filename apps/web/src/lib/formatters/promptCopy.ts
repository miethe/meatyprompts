import type { Prompt } from '../../types/Prompt';

// Helper functions to format prompts into various copy-friendly strings.

// Returns only the body text of the prompt.
export function toBody(prompt: Prompt): string {
  return prompt.body;
}

// Serializes a prompt with YAML front-matter containing key metadata.
export function toFrontMatter(prompt: Prompt): string {
  const lines: string[] = [];
  lines.push('---');
  lines.push(`title: ${JSON.stringify(prompt.title)}`);
  lines.push(`tags: [${(prompt.tags || []).map((t) => JSON.stringify(t)).join(', ')}]`);
  lines.push(`target_models: [${(prompt.target_models || []).map((m) => JSON.stringify(m)).join(', ')}]`);
  lines.push(`providers: [${(prompt.providers || []).map((p) => JSON.stringify(p)).join(', ')}]`);
  lines.push(`link: ${JSON.stringify(prompt.link || '')}`);
  lines.push(`access_control: ${JSON.stringify(prompt.access_control)}`);
  lines.push(`version: ${JSON.stringify(prompt.version)}`);
  lines.push(`updated_at: ${JSON.stringify(prompt.updatedAt)}`);
  lines.push('# input_schema:');
  lines.push('# llm_parameters:');
  lines.push('# sample_input:');
  lines.push('# sample_output:');
  lines.push('---');
  lines.push('');
  lines.push(prompt.body);
  return lines.join('\n');
}

// Serializes a prompt to a stable JSON shape mirroring the API response.
export function toJson(prompt: Prompt): string {
  const obj = {
    id: prompt.id,
    prompt_id: prompt.prompt_id,
    version: prompt.version,
    title: prompt.title,
    body: prompt.body,
    tags: prompt.tags || [],
    use_cases: prompt.use_cases || [],
    target_models: prompt.target_models || [],
    providers: prompt.providers || [],
    link: prompt.link || '',
    access_control: prompt.access_control,
    created_at: (prompt as any).createdAt,
    updated_at: prompt.updatedAt,
  };
  return JSON.stringify(obj, null, 2);
}
