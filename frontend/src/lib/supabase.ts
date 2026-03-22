/**
 * Supabase client for authentication
 */
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Missing Supabase environment variables!')
  console.error('NEXT_PUBLIC_SUPABASE_URL:', supabaseUrl ? '✓ Set' : '✗ Missing')
  console.error('NEXT_PUBLIC_SUPABASE_ANON_KEY:', supabaseAnonKey ? '✓ Set' : '✗ Missing')
  console.error('Please check your .env.local file')
}

if (supabaseAnonKey === 'your-anon-key-here') {
  console.error('❌ NEXT_PUBLIC_SUPABASE_ANON_KEY is still set to placeholder!')
  console.error('Please replace it with your actual Supabase anon key from the dashboard')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
