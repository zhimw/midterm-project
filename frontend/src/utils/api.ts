import axios from 'axios';
import type { UserProfile, ChatResponse } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  createSession: async (): Promise<{ session_id: string }> => {
    const response = await api.post('/session/new');
    return response.data;
  },

  createProfile: async (sessionId: string, profile: UserProfile): Promise<void> => {
    await api.post('/profile/create', {
      session_id: sessionId,
      profile,
    });
  },

  updateProfile: async (sessionId: string, profile: UserProfile): Promise<void> => {
    await api.post('/profile/update', {
      session_id: sessionId,
      profile,
    });
  },

  getProfile: async (sessionId: string): Promise<UserProfile> => {
    const response = await api.get(`/profile/${sessionId}`);
    return response.data.profile;
  },

  sendMessage: async (
    sessionId: string,
    message: string,
    userProfile?: UserProfile
  ): Promise<ChatResponse> => {
    const response = await api.post('/chat', {
      session_id: sessionId,
      message,
      user_profile: userProfile,
    });
    return response.data;
  },

  getHistory: async (sessionId: string): Promise<any> => {
    const response = await api.get(`/history/${sessionId}`);
    return response.data;
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/session/${sessionId}`);
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
