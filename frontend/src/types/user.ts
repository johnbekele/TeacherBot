export interface UserSettings {
  focus_mode: boolean;
  break_reminders: boolean;
  pace_preference: 'slow' | 'medium' | 'fast';
  adhd_mode: boolean;
}

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  onboarding_completed: boolean;
  settings: UserSettings;
  created_at: string;
  last_login?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
