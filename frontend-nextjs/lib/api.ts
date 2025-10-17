import axios, { AxiosResponse } from 'axios';
import {
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationCreate,
  Message,
  UserSettings,
  ChatDocument,
  HealthResponse,
  ApiError,
  User,
  UserQuestion,
  AIPrompt,
  ContextAwarenessData,
  QuestionDetails
} from './types';

// Create axios instance with default config
const api = axios.create({
  baseURL: '', // Use Next.js API routes
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: any) => {
    // More robust error logging
    if (error.response) {
      // Server responded with error status
      console.error('API Response Error:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        url: error.config?.url,
        method: error.config?.method
      });
    } else if (error.request) {
      // Request was made but no response received
      console.error('API Request Error (No Response):', {
        message: error.message,
        url: error.config?.url,
        method: error.config?.method
      });
    } else {
      // Something else happened
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Health check
export async function checkHealth(): Promise<HealthResponse> {
  const response: AxiosResponse<HealthResponse> = await api.get('/api/health');
  return response.data;
}

// Chat operations
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response: AxiosResponse<ChatResponse> = await api.post('/api/chat/stream', request);
  return response.data;
}

// Conversation operations
export async function createConversation(data: ConversationCreate): Promise<Conversation> {
  const response: AxiosResponse<Conversation> = await api.post('/api/chat/conversations', data);
  return response.data;
}

export async function getConversations(userId?: string): Promise<Conversation[]> {
  const params = userId ? { user_id: userId } : {};
  const response: AxiosResponse<Conversation[]> = await api.get('/api/chat/conversations', { params });
  return response.data;
}

export async function getConversation(conversationId: string): Promise<Conversation> {
  const response: AxiosResponse<Conversation> = await api.get(`/api/chat/conversations/${conversationId}`);
  return response.data;
}

// User Session operations
export async function getCurrentUser(sessionKey: string = 'default_session'): Promise<string | null> {
  try {
    const response: AxiosResponse<{ current_user_id: string }> = await api.get(`/api/user-sessions/${sessionKey}`);
    return response.data.current_user_id;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return null; // Session not found
    }
    throw error;
  }
}

export async function setCurrentUser(userId: string, sessionKey: string = 'default_session'): Promise<void> {
  try {
    console.log('Setting current user:', userId, 'for session:', sessionKey);
    const response = await api.post(`/api/user-sessions/${sessionKey}/set-user/${userId}`);
    console.log('User set successfully:', response.data);
  } catch (error) {
    console.error('Error in setCurrentUser API call:', error);
    throw error;
  }
}

export async function updateConversation(conversationId: string, data: Partial<Conversation>): Promise<Conversation> {
  const response: AxiosResponse<Conversation> = await api.put(`/api/chat/conversations/${conversationId}`, data);
  return response.data;
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await api.delete(`/api/chat/conversations/${conversationId}`);
}

// Message operations
export async function getMessages(conversationId: string): Promise<Message[]> {
  const response: AxiosResponse<Message[]> = await api.get(`/api/chat/conversations/${conversationId}/messages`);
  return response.data;
}

// User settings operations
export async function getUserSettings(userId: string): Promise<UserSettings> {
  const response: AxiosResponse<UserSettings> = await api.get(`/api/user-settings/${userId}`);
  return response.data;
}

export async function updateUserSettings(userId: string, settings: Partial<UserSettings>): Promise<UserSettings> {
  try {
    console.log('Updating user settings for user:', userId, 'with settings:', settings);
    const response: AxiosResponse<UserSettings> = await api.put(`/api/user-settings/${userId}`, settings);
    console.log('User settings updated successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in updateUserSettings API call:', error);
    throw error;
  }
}

// Document operations
export async function uploadDocument(file: File, conversationId: string): Promise<ChatDocument> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('conversation_id', conversationId);

  const response: AxiosResponse<ChatDocument> = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function getConversationDocuments(conversationId: string): Promise<ChatDocument[]> {
  const response: AxiosResponse<ChatDocument[]> = await api.get(`/api/v1/chat/documents/${conversationId}`);
  return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/api/v1/chat/documents/${documentId}`);
}

// Model operations
export async function getAvailableModels(): Promise<string[]> {
  const response: AxiosResponse<string[]> = await api.get('/api/chat/models');
  return response.data;
}

// User operations
export async function getUsers(): Promise<User[]> {
  const response: AxiosResponse<User[]> = await api.get('/api/users');
  return response.data;
}

export async function getUser(userId: string): Promise<User> {
  const response: AxiosResponse<User> = await api.get(`/api/users/${userId}`);
  return response.data;
}

export async function createUser(userData: { username: string; email?: string }): Promise<User> {
  const response: AxiosResponse<User> = await api.post('/api/users', userData);
  return response.data;
}

export async function checkUsernameExists(username: string): Promise<{ username: string; exists: boolean; user_id?: string }> {
  const response: AxiosResponse<{ username: string; exists: boolean; user_id?: string }> = await api.get(`/api/users/check-username/${encodeURIComponent(username)}`);
  return response.data;
}

export async function deleteUser(userId: string): Promise<{ message: string }> {
  try {
    const response: AxiosResponse<{ message: string }> = await api.delete(`/api/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error in deleteUser API call:', error);
    throw error;
  }
}

export async function deleteUserByUsername(username: string): Promise<{ message: string }> {
  try {
    const response: AxiosResponse<{ message: string }> = await api.delete(`/api/users/username/${username}`);
    return response.data;
  } catch (error) {
    console.error('Error in deleteUserByUsername API call:', error);
    throw error;
  }
}

// Error handling utility
export function handleApiError(error: any): string {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
}

// View Prompts Context API Functions
export async function getQuestionPrompt(questionId: string): Promise<AIPrompt> {
  const response: AxiosResponse<AIPrompt> = await api.get(`/api/view-prompts-context/questions/${questionId}/prompt`);
  return response.data;
}

export async function getQuestionContext(questionId: string): Promise<ContextAwarenessData[]> {
  const response: AxiosResponse<ContextAwarenessData[]> = await api.get(`/api/view-prompts-context/questions/${questionId}/context`);
  return response.data;
}

export async function getQuestionDetails(questionId: string): Promise<QuestionDetails> {
  const response: AxiosResponse<QuestionDetails> = await api.get(`/api/view-prompts-context/questions/${questionId}/details`);
  return response.data;
}

export async function getConversationQuestions(conversationId: string, limit: number = 100): Promise<UserQuestion[]> {
  const response: AxiosResponse<UserQuestion[]> = await api.get(`/api/view-prompts-context/conversations/${conversationId}/questions?limit=${limit}`);
  return response.data;
}

export async function getConversationPrompts(conversationId: string, limit: number = 100): Promise<AIPrompt[]> {
  const response: AxiosResponse<AIPrompt[]> = await api.get(`/api/view-prompts-context/conversations/${conversationId}/prompts?limit=${limit}`);
  return response.data;
}

export async function getConversationContext(conversationId: string, limit: number = 100): Promise<ContextAwarenessData[]> {
  const response: AxiosResponse<ContextAwarenessData[]> = await api.get(`/api/view-prompts-context/conversations/${conversationId}/context?limit=${limit}`);
  return response.data;
}

export async function getUserQuestions(userId: string, limit: number = 100): Promise<UserQuestion[]> {
  const response: AxiosResponse<UserQuestion[]> = await api.get(`/api/view-prompts-context/users/${userId}/questions?limit=${limit}`);
  return response.data;
}

export async function getUserPrompts(userId: string, limit: number = 100): Promise<AIPrompt[]> {
  const response: AxiosResponse<AIPrompt[]> = await api.get(`/api/view-prompts-context/users/${userId}/prompts?limit=${limit}`);
  return response.data;
}

export async function getUserContext(userId: string, limit: number = 100): Promise<ContextAwarenessData[]> {
  const response: AxiosResponse<ContextAwarenessData[]> = await api.get(`/api/view-prompts-context/users/${userId}/context?limit=${limit}`);
  return response.data;
}

export default api;
