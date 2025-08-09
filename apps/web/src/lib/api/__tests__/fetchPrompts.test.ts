import { fetchPrompts } from '../fetchPrompts';
import { apiRequest } from '../api_client';

jest.mock('../api_client');

describe('fetchPrompts', () => {
  it('builds query string from filters', async () => {
    (apiRequest as jest.Mock).mockResolvedValue([]);
    await fetchPrompts({ model: 'gpt-4', tool: 'toolA', purpose: 'demo' });
    expect(apiRequest).toHaveBeenCalledWith({
      endpoint: '/api/v1/prompts?model=gpt-4&tool=toolA&purpose=demo',
      method: 'GET',
    });
  });
});
