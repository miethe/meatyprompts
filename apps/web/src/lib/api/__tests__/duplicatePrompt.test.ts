import { duplicatePrompt } from '../duplicatePrompt';
import { apiRequest } from '../api_client';

jest.mock('../api_client');

describe('duplicatePrompt', () => {
  it('calls API with correct endpoint', async () => {
    (apiRequest as jest.Mock).mockResolvedValue({});
    await duplicatePrompt('abc');
    expect(apiRequest).toHaveBeenCalledWith({
      endpoint: '/api/v1/prompts/abc/duplicate',
      method: 'POST',
    });
  });
});
