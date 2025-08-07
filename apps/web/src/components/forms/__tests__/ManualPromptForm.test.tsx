import { manualPromptFormSchema } from '../ManualPromptForm';

describe('manualPromptFormSchema', () => {
  const base = {
    title: 'Test',
    body: 'Body',
    use_cases: ['example'],
    target_models: ['gpt-4'],
    access_control: 'public',
  };

  it('parses JSON fields to objects', () => {
    const result = manualPromptFormSchema.parse({
      ...base,
      llm_parameters: '{"temperature":0.7}',
    });
    expect(result.llm_parameters).toEqual({ temperature: 0.7 });
  });

  it('throws on invalid JSON', () => {
    expect(() => manualPromptFormSchema.parse({
      ...base,
      input_schema: '{invalid}',
    })).toThrow();
  });
});
