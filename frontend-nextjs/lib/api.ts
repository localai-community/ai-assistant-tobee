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
  User
} from './types';

// Create axios instance with default config
const api = axios.create({
  baseURL: '', // Use relative URLs to call Next.js API routes
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
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Health check
export async function checkHealth(): Promise<HealthResponse> {
  const response: AxiosResponse<HealthResponse> = await api.get('/health');
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
  const response: AxiosResponse<UserSettings> = await api.put(`/api/user-settings/${userId}`, settings);
  return response.data;
}

// Document operations
export async function uploadDocument(file: File, conversationId: string): Promise<ChatDocument> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('conversation_id', conversationId);

  const response: AxiosResponse<ChatDocument> = await api.post('/api/v1/chat/upload', formData, {
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

export default api;
