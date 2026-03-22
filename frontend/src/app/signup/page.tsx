'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signup } from '@/lib/api';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import Link from 'next/link';
import { AlertCircle } from 'lucide-react';

export default function SignupPage() {
  const router = useRouter();
  
  // Auth fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  
  // Financial Profile Fields
  const [monthlyIncome, setMonthlyIncome] = useState('');
  const [dependents, setDependents] = useState('0');
  const [medicalRisk, setMedicalRisk] = useState('low');
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!monthlyIncome || isNaN(Number(monthlyIncome))) {
      setError('Please enter a valid monthly income.');
      return;
    }
    
    setLoading(true);

    try {
      const response = await signup(email, password);
      localStorage.setItem('token', response.data.access_token);
      
      // Store financial profile locally for the /financial-analysis engine
      const profile = {
        name,
        monthly_income: Number(monthlyIncome),
        family_dependency: Number(dependents),
        medical_risk: medicalRisk,
      };
      localStorage.setItem('financial_profile', JSON.stringify(profile));
      
      router.push('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'An error occurred during registration.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-100/50 via-gray-50 to-white px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md"
      >
        <Card className="border-0 shadow-2xl shadow-indigo-500/10 bg-white/80 backdrop-blur-xl">
          <CardHeader className="space-y-2 pb-6 text-center">
            <CardTitle className="text-2xl font-bold tracking-tight text-gray-900">
              Create an account
            </CardTitle>
            <CardDescription className="text-gray-500 font-medium">
              Enter your details to generate your financial profile
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <label className="text-sm font-semibold text-gray-700">Full Name</label>
                  <Input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Rahul Sharma"
                    required
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <label className="text-sm font-semibold text-gray-700">Email Address</label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    required
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <label className="text-sm font-semibold text-gray-700">Password</label>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>

                <div className="col-span-2 my-2">
                  <div className="h-px bg-gray-200 w-full" />
                </div>

                <div className="space-y-2 col-span-2">
                  <label className="text-sm font-semibold text-gray-700">Monthly Income (₹)</label>
                  <Input
                    type="number"
                    value={monthlyIncome}
                    onChange={(e) => setMonthlyIncome(e.target.value)}
                    placeholder="50000"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-gray-700">Dependents</label>
                  <Input
                    type="number"
                    value={dependents}
                    onChange={(e) => setDependents(e.target.value)}
                    placeholder="0"
                    min="0"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-semibold text-gray-700">Medical Risk</label>
                  <select
                    value={medicalRisk}
                    onChange={(e) => setMedicalRisk(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-gray-200 bg-white/50 px-3 py-2 text-sm ring-offset-background outline-none focus:ring-2 focus:ring-indigo-600 transition-all"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-100"
                >
                  <AlertCircle className="w-4 h-4" />
                  <p>{error}</p>
                </motion.div>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20 mt-4"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <p className="text-gray-500">
                Already have an account?{' '}
                <Link href="/login" className="font-semibold text-indigo-600 hover:text-indigo-500">
                  Sign in
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
