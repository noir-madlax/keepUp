export interface User {
  id: string
  email: string
  user_metadata: {
    avatar_url?: string
    full_name?: string
    user_name?: string
  }
}

export interface AuthState {
  user: User | null
  loading: boolean
} 