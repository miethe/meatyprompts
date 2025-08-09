// Central API client for all HTTP requests
export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface ApiRequestOptions {
  method?: ApiMethod;
  endpoint: string;
  body?: any;
  query?: Record<string, string | number | boolean | undefined>;
  headers?: Record<string, string>;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest<T = any>({
  method = 'GET',
  endpoint,
  body,
  query,
  headers = {},
}: ApiRequestOptions): Promise<T> {
  let url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  if (query) {
    const params = new URLSearchParams();
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined) params.append(k, String(v));
    });
    url += (url.includes('?') ? '&' : '?') + params.toString();
  }
  let token: string | undefined;
  if (typeof window !== 'undefined' && (window as any).Clerk?.session) {
    token = await (window as any).Clerk.session.getToken();
  }
  const fetchOptions: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  };
  if (body !== undefined) {
    fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
  }
  const response = await fetch(url, fetchOptions);
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error: ${response.status} ${response.statusText} - ${errorText}`);
  }
  // Try to parse JSON, fallback to text
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }
  return response.text() as any;
}
