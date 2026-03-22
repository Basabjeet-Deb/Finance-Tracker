import axios from 'axios';
import { supabase } from './supabase';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Supabase token to requests
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  
  return config;
});

// Handle 401 errors globally
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      console.error('[API] 401 Unauthorized - Session expired');
      // Sign out from Supabase
      await supabase.auth.signOut();
      // Redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth - Now handled by Supabase directly
export const signup = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: `${window.location.origin}/dashboard`,
      // Skip email confirmation for development
      data: {
        email_confirm: true
      }
    }
  });
  if (error) throw error;
  return data;
};

export const login = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  if (error) throw error;
  return data;
};

export const logout = async () => {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
};

export const getCurrentSession = async () => {
  try {
    console.log('[API] Getting current session...');
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error) {
      console.error('[API] Session error:', error);
      return null;
    }
    
    console.log('[API] Session retrieved:', session ? 'Valid session' : 'No session');
    return session;
  } catch (error) {
    console.error('[API] Exception getting session:', error);
    return null;
  }
};

// User Profile
export const getUserProfile = () => api.get('/auth/me');

export const updateUserProfile = (data: {
  income?: number;
  dependents?: number;
  medical_risk?: string;
}) => api.put('/auth/profile', data);

// Expenses
export const getExpenses = () => api.get('/expenses');

export const createExpense = (data: {
  amount: number;
  category: string;
  date: string;
  note?: string;
}) => api.post('/expenses', data);

export const updateExpense = (id: number, data: any) =>
  api.put(`/expenses/${id}`, data);

export const deleteExpense = (id: string) => api.delete(`/expenses/${id}`);

// Budget
export const createBudget = (monthly_budget: number, month: string) =>
  api.post('/budget', { monthly_budget, month });

export const getBudget = (month: string) => api.get(`/budget/${month}`);

// Dashboard
export const getDashboard = () => api.get('/dashboard');

// Insights
export const getInsights = () => api.get('/insights');

// External Data
export const getCPIData = () => api.get('/external/cpi');
export const getFuelData = () => api.get('/external/fuel');

export interface FinancialAnalysisParams {
  monthly_income?: number;
  emi_amount?: number;
  medical_risk?: string;
  family_dependency?: number;
  has_emergency_fund?: boolean;
}

export const getFinancialAnalysis = (params: FinancialAnalysisParams) =>
  api.get('/financial-analysis', { params });

export const getAnalysisHistory = (limit: number = 10) =>
  api.get('/analysis-history', { params: { limit } });

// NEW: Unified Analysis API
export interface UnifiedAnalysisRequest {
  user_profile: {
    monthly_income: number;
    emi_amount?: number;
    medical_risk?: 'low' | 'medium' | 'high';
    family_dependency?: number;
    has_emergency_fund?: boolean;
  };
  expenses?: Array<{
    category: string;
    amount: number;
    note?: string;
  }>;
  use_current_month?: boolean;
}

export const analyzeFinancialHealth = (request: UnifiedAnalysisRequest) =>
  api.post('/api/analyze', request);

export const getQuickAnalysis = () =>
  api.get('/api/analyze/quick');

export const getAnalysisStatus = () =>
  api.get('/api/analyze/status');

export default api;

