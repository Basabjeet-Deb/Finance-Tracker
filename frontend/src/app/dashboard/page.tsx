'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { checkAdminAccess, requireAdmin } from '@/lib/auth';
import Sidebar from '@/components/Sidebar';
import { getDashboard, getExpenses, getFinancialAnalysis } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { 
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer 
} from 'recharts';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  IndianRupee, 
  PiggyBank, 
  ShieldAlert, 
  TrendingUp, 
  AlertTriangle,
  Lightbulb,
  ArrowRight
} from 'lucide-react';

// Custom CountUp Component
const CountUp = ({ to, prefix = '' }: { to: number, prefix?: string }) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const increment = to / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= to) {
        setCount(to);
        clearInterval(timer);
      } else {
        setCount(start);
      }
    }, 16);
    return () => clearInterval(timer);
  }, [to]);
  return <span>{prefix}{count.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>;
};

const MotionCard = motion(Card);

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('Dashboard useEffect running...');
    
    const token = localStorage.getItem('token');
    const userEmail = localStorage.getItem('userEmail');
    
    console.log('Token:', token ? 'exists' : 'missing');
    console.log('UserEmail:', userEmail);
    
    if (!token || !userEmail) {
      console.log('Missing credentials, redirecting to login');
      router.push('/login');
      return;
    }
    
    if (userEmail !== 'admin@admin.com') {
      console.log('Not admin, redirecting to login');
      router.push('/login');
      return;
    }
    
    console.log('Auth checks passed, fetching data...');
    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      const storedProfile = localStorage.getItem('financial_profile');
      let profile = storedProfile ? JSON.parse(storedProfile) : { monthly_income: 50000 };

      console.log('Fetching dashboard data...');
      
      const [dashboardRes, analysisRes] = await Promise.all([
        getDashboard().catch(err => {
          console.error('Dashboard API error:', err);
          throw err;
        }),
        getFinancialAnalysis({
          monthly_income: profile.monthly_income,
          medical_risk: profile.medical_risk || 'low',
          family_dependency: profile.family_dependency || 0
        }).catch(err => {
          console.error('Analysis API error:', err);
          return { data: null };
        })
      ]);
      
      console.log('Dashboard data received:', dashboardRes.data);
      console.log('Analysis data received:', analysisRes?.data);
      
      setData(dashboardRes.data);
      if (analysisRes?.data) setAnalysis(analysisRes.data);
      
    } catch (error) {
      console.error('Error fetching data:', error);
      // If authentication fails, redirect to login
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        router.push('/login');
      }
    } finally {
      console.log('Setting loading to false');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Sidebar>
        <div className="flex h-full items-center justify-center p-8 bg-gray-50/50">
          <div className="space-y-4 text-center">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto" />
            <p className="text-sm font-medium text-gray-500 tracking-wide animate-pulse">
              SYNCING ENGINE...
            </p>
          </div>
        </div>
      </Sidebar>
    );
  }

  // Animation variants
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };
  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  const getRiskColor = (level: string) => {
    if (level === 'high') return 'destructive';
    if (level === 'medium') return 'warning';
    return 'success';
  };

  const categoryColors: Record<string, string> = {
    Food: '#10B981', Rent: '#3B82F6', Transport: '#F59E0B', 
    Bills: '#EF4444', Entertainment: '#8B5CF6', Other: '#6B7280'
  };

  return (
    <Sidebar>
      <div className="min-h-screen bg-gray-50/50 p-6 lg:p-10 space-y-8">
        
        {/* Header */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Financial Overview</h1>
            <p className="text-gray-500 mt-1">AI-powered insights based on real-world Indian inflation.</p>
          </div>
          {analysis?.risk_level && (
            <Badge variant={getRiskColor(analysis.risk_level)} className="text-sm px-4 py-1.5 shadow-sm">
              Risk Level: {analysis.risk_level.toUpperCase()}
            </Badge>
          )}
        </motion.div>

        {/* Top KPI Cards */}
        <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <MotionCard variants={item} className="overflow-hidden relative group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Monthly Spend</CardTitle>
              <IndianRupee className="w-4 h-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                <CountUp prefix="₹" to={data?.monthly_total || 0} />
              </div>
              <p className="text-xs text-gray-500 mt-1">Calculated from all expenses</p>
            </CardContent>
          </MotionCard>

          <MotionCard variants={item} className="overflow-hidden relative group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-emerald-400 to-emerald-600 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Savings Rate</CardTitle>
              <PiggyBank className="w-4 h-4 text-emerald-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                <CountUp to={analysis?.savings_rate || 0} />%
              </div>
              <div className="w-full bg-gray-100 h-1.5 mt-2 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }} 
                  animate={{ width: `${Math.min(analysis?.savings_rate || 0, 100)}%` }} 
                  transition={{ duration: 1.5, delay: 0.5 }}
                  className="h-full bg-emerald-500"
                />
              </div>
            </CardContent>
          </MotionCard>

          <MotionCard variants={item} className="overflow-hidden relative group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-orange-400 to-red-500 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Risk Score</CardTitle>
              <ShieldAlert className="w-4 h-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                <CountUp to={analysis?.risk_score || 0} />/100
              </div>
              <p className="text-xs text-gray-500 mt-1">Lower is better</p>
            </CardContent>
          </MotionCard>

          <MotionCard variants={item} className="overflow-hidden relative group">
            <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-purple-500 to-pink-500 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Inflation Impact</CardTitle>
              <TrendingUp className="w-4 h-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                <CountUp to={analysis?.inflation?.general || 0} />%
              </div>
              <p className="text-xs text-gray-500 mt-1">Current YoY India CPI</p>
            </CardContent>
          </MotionCard>
        </motion.div>

        {/* Main Grid section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Chart */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }} 
            animate={{ opacity: 1, scale: 1 }} 
            transition={{ delay: 0.3 }}
            className="lg:col-span-2"
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Spending Distribution</CardTitle>
                <CardDescription>Hover over sectors to see exact splits</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] w-full">
                  {data?.category_breakdown?.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={data.category_breakdown}
                          dataKey="amount"
                          nameKey="category"
                          cx="50%"
                          cy="50%"
                          innerRadius={80}
                          outerRadius={110}
                          paddingAngle={3}
                          stroke="none"
                        >
                          {data.category_breakdown.map((entry: any) => (
                            <Cell key={entry.category} fill={categoryColors[entry.category] || '#E5E7EB'} />
                          ))}
                        </Pie>
                        <Tooltip 
                          formatter={(value: any) => formatCurrency(value)} 
                          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-400">No chart data</div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Right Money Leaks Panel */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }} 
            animate={{ opacity: 1, x: 0 }} 
            transition={{ delay: 0.4 }}
          >
            <Card className="h-full bg-gradient-to-br from-indigo-900 to-slate-900 border-0 text-white shadow-xl shadow-indigo-900/20">
              <CardHeader>
                <CardTitle className="text-indigo-100 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                  Money Leaks
                </CardTitle>
                <CardDescription className="text-indigo-200/70">
                  Areas where you're overspending relative to inflation.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysis?.impacted_categories?.length > 0 ? (
                  analysis.impacted_categories.map((cat: any, i: number) => (
                    <motion.div 
                      initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + (i * 0.1) }}
                      key={i} className="flex items-center justify-between bg-white/10 p-4 rounded-xl backdrop-blur-sm border border-white/5"
                    >
                      <div className="flex flex-col gap-1">
                        <span className="font-medium text-sm">{cat.category || cat}</span>
                        {cat.estimated_increase_pct && (
                          <span className="text-xs text-indigo-300/70">
                            +{cat.estimated_increase_pct}% inflation impact
                          </span>
                        )}
                      </div>
                      <Badge className="bg-amber-400/20 text-amber-300 hover:bg-amber-400/30 border-0">
                        {cat.impact_level || 'Trim'} impact
                      </Badge>
                    </motion.div>
                  ))
                ) : (
                  <div className="text-center p-6 text-indigo-300/50">
                    <ShieldAlert className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>No major money leaks detected</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Actionable Recommendations (Bottom Section) */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
        >
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
            <Lightbulb className="w-5 h-5 text-amber-500" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysis?.recommendations?.slice(0, 3).map((rec: string, i: number) => (
              <motion.div whileHover={{ scale: 1.02, y: -2 }} key={i}>
                <Card className="h-full border border-indigo-100/50 shadow-sm hover:shadow-md transition-all cursor-pointer group bg-white">
                  <CardContent className="p-5 flex gap-4 items-start">
                    <div className="bg-indigo-50 p-2 rounded-lg group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-300">
                      <ArrowRight className="w-4 h-4 text-indigo-500 group-hover:text-white" />
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed font-medium">{rec}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

      </div>
    </Sidebar>
  );
}
