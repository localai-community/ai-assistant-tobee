// TypeScript types matching backend schemas

export interface User {
  id: string;
  username: string;
  email?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email?: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tokens_used?: number;
  model_used?: string;
  created_at: string;
}

export interface MessageCreate {
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tokens_used?: number;
  model_used?: string;
}

export interface Conversation {
  id: string;
  title?: string;
  model: string;
  user_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationCreate {
  title?: string;
  model?: string;
  user_id?: string;
}

export interface ChatDocument {
  id: string;
  conversation_id: string;
  user_id?: string;
  filename: string;
  file_type: string;
  file_size: number;
  file_path: string;
  upload_timestamp: string;
  summary_text?: string;
  summary_type?: string;
  processing_status: string;
  created_at: string;
  updated_at: string;
}

export interface ChatDocumentCreate {
  conversation_id: string;
  user_id?: string;
  filename: string;
  file_type: string;
  file_size: number;
  file_path: string;
}

export interface UserSettings {
  user_id: string;
  enable_context_awareness?: boolean;
  include_memory?: boolean;
  context_strategy?: string;
  selected_model?: string;
  use_streaming?: boolean;
  use_rag?: boolean;
  use_advanced_rag?: boolean;
  use_phase2_reasoning?: boolean;
  use_reasoning_chat?: boolean;
  use_phase3_reasoning?: boolean;
  selected_phase2_engine?: string;
  selected_phase3_strategy?: string;
  temperature?: number;
  use_unified_reasoning?: boolean;
  selected_reasoning_mode?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
  model?: string;
  temperature?: number;
  user_id?: string;
  use_rag?: boolean;
  use_advanced_rag?: boolean;
  use_phase2_reasoning?: boolean;
  use_reasoning_chat?: boolean;
  use_phase3_reasoning?: boolean;
  use_unified_reasoning?: boolean;
  selected_reasoning_mode?: string;
  selected_phase2_engine?: string;
  selected_phase3_strategy?: string;
  enable_context_awareness?: boolean;
  include_memory?: boolean;
  context_strategy?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  model_used: string;
  tokens_used?: number;
  is_complete: boolean;
}

export interface SSEEvent {
  type: 'message' | 'error' | 'complete';
  data: any;
}

export interface ApiError {
  detail: string;
  error_code?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

// View Prompts Context Types
export interface UserQuestion {
  id: string;
  conversation_id: string;
  user_id: string;
  question_text: string;
  question_timestamp: string;
  created_at: string;
  updated_at: string;
}

export interface AIPrompt {
  id: string;
  question_id: string;
  conversation_id: string;
  user_id: string;
  final_prompt: string;
  model_used: string;
  temperature?: number;
  max_tokens?: number;
  prompt_timestamp: string;
  created_at: string;
}

export interface ContextAwarenessData {
  id: string;
  question_id: string;
  conversation_id: string;
  user_id: string;
  context_type: string;
  context_data: any;
  context_metadata?: any;
  context_timestamp: string;
  created_at: string;
}

export interface QuestionDetails {
  question: UserQuestion;
  prompt?: AIPrompt;
  context_data: ContextAwarenessData[];
}
