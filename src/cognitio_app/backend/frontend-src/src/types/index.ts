// Cognitio Chat Framework Types

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session: string;
  message: string;
  response: string;
  message_type: 'user' | 'assistant';
  created_at: string;
}

export interface WebLLMConfig {
  models: string[];
  default_model: string;
  temperature: number;
  max_tokens: number;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface WebLLMMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface WebLLMResponse {
  content: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
