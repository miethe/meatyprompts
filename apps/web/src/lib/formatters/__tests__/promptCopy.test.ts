import { toBody, toFrontMatter, toJson } from '../promptCopy';
import type { Prompt } from '../../../types/Prompt';

describe('promptCopy formatters', () => {
  const prompt: Prompt = {
    id: '1',
    prompt_id: 'p1',
    version: 'v1',
    title: 'Test',
    body: 'Hello world',
    tags: ['tag1'],
    use_cases: ['test'],
    access_control: 'private',
    target_models: ['gpt-4o'],
    providers: ['openai'],
    link: 'http://example.com',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z',
  } as unknown as Prompt;

  it('returns body', () => {
    expect(toBody(prompt)).toBe('Hello world');
  });

  it('creates front matter with required fields', () => {
    const fm = toFrontMatter(prompt);
    expect(fm).toContain('title: "Test"');
    expect(fm).toContain('tags: ["tag1"]');
    expect(fm).toContain('updated_at: "2024-01-02T00:00:00Z"');
    expect(fm).toContain('Hello world');
  });

  it('creates stable JSON', () => {
    const json = JSON.parse(toJson(prompt));
    expect(json).toEqual({
      id: '1',
      prompt_id: 'p1',
      version: 'v1',
      title: 'Test',
      body: 'Hello world',
      tags: ['tag1'],
      use_cases: ['test'],
      target_models: ['gpt-4o'],
      providers: ['openai'],
      link: 'http://example.com',
      access_control: 'private',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    });
  });
});
