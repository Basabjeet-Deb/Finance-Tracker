'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { createExpense, createBudget } from '@/lib/api';
import { categories, getCurrentMonth } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertCircle, PlusCircle, Target } from 'lucide-react';

export default function AddExpensePage() {
  const router = useRouter();
  
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('Food');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [note, setNote] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [showBudget, setShowBudget] = useState(false);
  const [budget, setBudget] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await createExpense({
        amount: parseFloat(amount),
        category,
        date,
        note: note || undefined,
      });
      setSuccess('Expense added successfully! Redirecting...');
      setTimeout(() => router.push('/dashboard'), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add expense');
    } finally {
      setLoading(false);
    }
  };

  const handleBudgetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await createBudget(parseFloat(budget), getCurrentMonth());
      setSuccess('Budget allocated for the month!');
      setBudget('');
      setTimeout(() => setShowBudget(false), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to set budget');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Sidebar>
      <div className="min-h-screen bg-gray-50/50 p-6 lg:p-10 dark:bg-transparent">
        
        <div className="max-w-2xl mx-auto space-y-8">
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight dark:text-slate-50">Record Transaction</h1>
            <p className="text-gray-500 mt-1 dark:text-slate-400">Log an expense or set your monthly spending limit.</p>
          </motion.div>

          {/* Toggle Tabs */}
          <div className="flex bg-gray-200/50 p-1 rounded-xl w-fit dark:bg-slate-800/50">
            <button
              onClick={() => setShowBudget(false)}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-medium transition-all ${!showBudget ? 'bg-white text-indigo-700 shadow-sm dark:bg-slate-700 dark:text-indigo-300' : 'text-gray-500 hover:text-gray-900 dark:text-slate-400 dark:hover:text-slate-50'}`}
            >
              <PlusCircle className="w-4 h-4" /> Add Expense
            </button>
            <button
              onClick={() => setShowBudget(true)}
              className={`flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-medium transition-all ${showBudget ? 'bg-white text-indigo-700 shadow-sm dark:bg-slate-700 dark:text-indigo-300' : 'text-gray-500 hover:text-gray-900 dark:text-slate-400 dark:hover:text-slate-50'}`}
            >
              <Target className="w-4 h-4" /> Set Budget
            </button>
          </div>

          <AnimatePresence mode="wait">
            {!showBudget ? (
              <motion.div
                key="expense-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.2 }}
              >
                <Card>
                  <CardContent className="pt-6">
                    <form onSubmit={handleSubmit} className="space-y-5">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div className="space-y-2">
                          <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Amount (₹)</label>
                          <Input
                            type="number"
                            step="0.01"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            placeholder="e.g. 1500"
                            required
                            className="text-lg bg-gray-50/50 dark:bg-slate-800/50"
                          />
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Category</label>
                          <select
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="flex h-10 w-full rounded-md border border-gray-200 bg-gray-50/50 px-3 py-2 text-sm ring-offset-background outline-none hover:bg-white focus:bg-white transition-all focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-50 dark:hover:bg-slate-800 dark:focus:bg-slate-800 dark:focus:ring-indigo-400"
                          >
                            {categories.map((cat) => (
                              <option key={cat} value={cat}>{cat}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Date</label>
                        <Input
                          type="date"
                          value={date}
                          onChange={(e) => setDate(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Notes (Optional)</label>
                        <textarea
                          value={note}
                          onChange={(e) => setNote(e.target.value)}
                          className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none bg-gray-50/50 hover:bg-white focus:bg-white transition-all resize-none dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-50 dark:placeholder:text-slate-400 dark:hover:bg-slate-800 dark:focus:bg-slate-800 dark:focus:ring-indigo-400"
                          placeholder="Lunch with team..."
                          rows={3}
                        />
                      </div>

                      <StatusMessage error={error} success={success} />

                      <Button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/20 dark:bg-indigo-500 dark:hover:bg-indigo-600 dark:shadow-indigo-500/10">
                        {loading ? 'Processing...' : 'Save Transaction'}
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              <motion.div
                key="budget-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.2 }}
              >
                <Card>
                  <CardContent className="pt-6">
                    <form onSubmit={handleBudgetSubmit} className="space-y-5">
                      <div className="space-y-2">
                        <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Monthly Budget (₹)</label>
                        <Input
                          type="number"
                          step="0.01"
                          value={budget}
                          onChange={(e) => setBudget(e.target.value)}
                          placeholder="50000"
                          required
                          className="text-lg bg-gray-50/50 dark:bg-slate-800/50"
                        />
                        <p className="text-xs text-gray-500 mt-1 dark:text-slate-400">Configuring base budget for {getCurrentMonth()}</p>
                      </div>

                      <StatusMessage error={error} success={success} />

                      <Button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/20 dark:bg-indigo-500 dark:hover:bg-indigo-600 dark:shadow-indigo-500/10">
                        {loading ? 'Allocating...' : 'Set Baseline'}
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </Sidebar>
  );
}

const StatusMessage = ({ error, success }: { error: string; success: string }) => {
  if (!error && !success) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-center gap-2 p-3 rounded-lg text-sm font-medium ${
        error
          ? 'bg-red-50 text-red-600 border border-red-100 dark:bg-red-950/50 dark:text-red-400 dark:border-red-900/50'
          : 'bg-emerald-50 text-emerald-600 border border-emerald-100 dark:bg-emerald-950/50 dark:text-emerald-400 dark:border-emerald-900/50'
      }`}
    >
      {error ? <AlertCircle className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
      <p>{error || success}</p>
    </motion.div>
  );
};
