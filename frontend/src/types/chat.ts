export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatAction {
  type: string;
  data: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  mode: string;
  actions: ChatAction[];
  next_step?: string;
}
