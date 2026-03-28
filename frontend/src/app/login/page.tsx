'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login } from '@/lib/api';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import Link from 'next/link';
import { AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('[Login] Attempting login...');
      
      // Login with Supabase Auth
      const result = await login(email, password);
      
      console.log('[Login] Login successful:', result);
      
      // Small delay to ensure session is set
      await new Promise(resolve => setTimeout(resolve, 500));
      
      console.log('[Login] Redirecting to dashboard...');
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      console.error('[Login] Login error:', err);
      setError(
        err.message || 'Invalid credentials. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-100/50 via-gray-50 to-white px-4 dark:bg-slate-950 dark:from-indigo-950/30 dark:via-slate-950 dark:to-slate-950">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md"
      >
        <Card className="border-0 shadow-2xl shadow-indigo-500/10 bg-white/80 backdrop-blur-xl dark:shadow-indigo-500/5 dark:bg-slate-900/80">
          <CardHeader className="space-y-3 pb-6 text-center">
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
            >
              <div className="mx-auto bg-indigo-600/10 w-12 h-12 rounded-xl flex items-center justify-center mb-4 dark:bg-indigo-400/10">
                <span className="text-2xl">🇮🇳</span>
              </div>
            </motion.div>
            <CardTitle className="text-2xl font-bold tracking-tight text-gray-900 dark:text-slate-50">
              Welcome back
            </CardTitle>
            <CardDescription className="text-gray-500 font-medium dark:text-slate-400">
              Sign in to your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Email Address</label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="bg-white/50 dark:bg-slate-800/50"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Password</label>
                  <Link href="#" className="text-xs font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
                    Forgot password?
                  </Link>
                </div>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="bg-white/50 dark:bg-slate-800/50"
                />
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-100 dark:bg-red-950/50 dark:text-red-400 dark:border-red-900/50"
                >
                  <AlertCircle className="w-4 h-4" />
                  <p>{error}</p>
                </motion.div>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20 dark:bg-indigo-500 dark:hover:bg-indigo-600 dark:shadow-indigo-500/10"
              >
                {loading ? 'Signing in...' : 'Continue'}
              </Button>
            </form>

            <div className="mt-8 text-center text-sm">
              <p className="text-gray-500 dark:text-slate-400">
                Don't have an account?{' '}
                <Link href="/signup" className="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
                  Sign up
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
