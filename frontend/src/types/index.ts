export interface UserProfile {
  age: number;
  income: number;
  filing_status: string;
  state: string;
  assets: {
    cash?: number;
    stocks?: number;
    bonds?: number;
    real_estate?: number;
    business?: number;
    other?: number;
  };
  family: {
    marital_status?: string;
    children?: number;
  };
  life_events: string[];
  goals: string[];
  investment_goals: string[];
  estate_goals: string[];
  risk_tolerance: string;
  time_horizon: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface Evidence {
  doc_id: string;
  category: string;
  snippet: string;
  full_text?: string;
}

export interface TaxBreakdown {
  strategies: string[];
  key_considerations: string[];
}

export interface InvestmentBreakdown {
  risk_profile: string;
  allocation: Record<string, number>;
  tax_efficiency_score: number;
}

export interface EstateBreakdown {
  estate_value: number;
  triggers: string[];
  structures: Array<{
    type: string;
    purpose: string;
  }>;
}

export interface Breakdown {
  tax?: TaxBreakdown;
  investment?: InvestmentBreakdown;
  estate?: EstateBreakdown;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  breakdown: Breakdown;
  evidence: Evidence[];
  modules_used: string[];
  conversation_history: ChatMessage[];
}
