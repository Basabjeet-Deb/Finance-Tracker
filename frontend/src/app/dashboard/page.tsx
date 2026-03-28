'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Sidebar from '@/components/Sidebar';
import { getDashboard, getFinancialAnalysis, getCurrentSession } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { 
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  IndianRupee, 
  PiggyBank, 
  ShieldAlert, 
  TrendingUp, 
  AlertTriangle,
  Lightbulb,
  ArrowRight,
  Wallet,
  Activity,
  HeartPulse,
  Banknote,
  Info
} from 'lucide-react';

// Custom CountUp Component
const CountUp = ({ to, prefix = '', suffix = '' }: { to: number, prefix?: string, suffix?: string }) => {
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
  return <span>{prefix}{count.toLocaleString('en-IN', { maximumFractionDigits: 1 })}{suffix}</span>;
};

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<any>({ monthly_income: 0 });
  const [dataFetched, setDataFetched] = useState(false); // Prevent duplicate fetches

  useEffect(() => {
    const checkAuth = async () => {
      if (dataFetched) return; // Skip if already fetched
      
      try {
        console.log('[Dashboard] Checking auth...');
        const session = await getCurrentSession();
        console.log('[Dashboard] Session:', session);
        
        if (!session) {
          console.log('[Dashboard] No session, redirecting to login');
          router.push('/login');
          return;
        }
        
        console.log('[Dashboard] Auth OK, fetching data...');
        setDataFetched(true); // Mark as fetched
        fetchData();
      } catch (error) {
        console.error('[Dashboard] Auth check error:', error);
        router.push('/login');
      }
    };
    
    checkAuth();
  }, [router, dataFetched]);

  const fetchData = async () => {
    try {
      const storedProfile = localStorage.getItem('financial_profile');
      let currentProfile = storedProfile ? JSON.parse(storedProfile) : { monthly_income: 50000 };
      setProfile(currentProfile);
      
      // Only fetch dashboard data (fast)
      const dashboardRes = await getDashboard().catch(() => ({ data: null }));
      
      if (dashboardRes?.data) setData(dashboardRes.data);
      
    } catch (error: any) {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Sidebar>
        <div className="flex h-full items-center justify-center p-8 bg-slate-50 dark:bg-transparent">
          <div className="space-y-4 text-center">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto dark:border-indigo-800 dark:border-t-indigo-400" />
            <p className="text-sm font-bold tracking-widest text-indigo-600/80 animate-pulse dark:text-indigo-400/80">
              LOADING INSIGHTS...
            </p>
          </div>
        </div>
      </Sidebar>
    );
  }

  // Animation variants
  const container: Variants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };
  const item: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };
  const slideIn: Variants = {
    hidden: { opacity: 0, x: 20 },
    show: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  const getRiskColor = (level: string) => {
    if (level === 'high') return 'bg-red-500/10 text-red-600 border-red-200 dark:bg-red-500/20 dark:text-red-400 dark:border-red-800';
    if (level === 'medium') return 'bg-amber-500/10 text-amber-600 border-amber-200 dark:bg-amber-500/20 dark:text-amber-400 dark:border-amber-800';
    return 'bg-emerald-500/10 text-emerald-600 border-emerald-200 dark:bg-emerald-500/20 dark:text-emerald-400 dark:border-emerald-800';
  };

  const categoryColors: Record<string, string> = {
    Food: '#10B981', Rent: '#3B82F6', Transport: '#F59E0B', 
    Bills: '#EF4444', Entertainment: '#8B5CF6', Other: '#6B7280', Lifestyle: '#EC4899', Subscriptions: '#14B8A6'
  };

  const getSeverityStyle = (impact: string) => {
    if (impact?.toLowerCase() === 'high') return "bg-red-50 text-red-700 border-red-100 dark:bg-red-950/50 dark:text-red-300 dark:border-red-900";
    if (impact?.toLowerCase() === 'medium') return "bg-amber-50 text-amber-700 border-amber-100 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-900";
    return "bg-yellow-50 text-yellow-700 border-yellow-100 dark:bg-yellow-950/50 dark:text-yellow-300 dark:border-yellow-900";
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-xl shadow-lg border border-gray-100 dark:bg-slate-800 dark:border-slate-700">
          <p className="font-semibold text-gray-800 dark:text-slate-50">{payload[0].name}</p>
          <p className="text-indigo-600 font-medium dark:text-indigo-400">{formatCurrency(payload[0].value)}</p>
        </div>
      );
    }
    return null;
  };

  // Custom Legend for PieChart
  const renderLegend = (props: any) => {
    const { payload } = props;
    const total = data?.category_breakdown?.reduce((sum: number, entry: any) => sum + entry.amount, 0) || 1;
    
    return (
      <ul className="flex flex-wrap justify-center gap-3 mt-4">
        {payload.map((entry: any, index: number) => {
          const itemTotal = data?.category_breakdown?.find((item: any) => item.category === entry.value)?.amount || 0;
          const percentage = ((itemTotal / total) * 100).toFixed(1);
          return (
            <li key={`item-${index}`} className="flex items-center text-xs font-medium text-gray-700 dark:text-slate-300">
              <span className="w-3 h-3 rounded-full mr-1.5" style={{ backgroundColor: entry.color }} />
              {entry.value}: {percentage}% ({formatCurrency(itemTotal)})
            </li>
          );
        })}
      </ul>
    );
  };

  const totalSpent = data?.monthly_total || 0;
  const income = profile?.monthly_income || 50000;
  const savingsRate = income > 0 ? ((income - totalSpent) / income * 100) : 0;
  const targetSavingsRate = 20;

  // Emergency readiness dummy data calculation for demonstration:
  const monthlyFixedExpenses = (totalSpent * 0.5); // assuming 50% are fixed
  const emergencyFund = profile?.emergency_fund || (income * 1.5); 
  const emergencyMonths = monthlyFixedExpenses > 0 ? (emergencyFund / monthlyFixedExpenses).toFixed(1) : "0";

  return (
    <Sidebar>
      <div className="min-h-screen bg-slate-50 p-6 lg:p-10 space-y-8 dark:bg-transparent">
        
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight dark:text-slate-50">Financial Overview</h1>
            <p className="text-slate-500 mt-1 dark:text-slate-400">AI-powered insights driving your financial health.</p>
          </div>
          <div className="flex gap-3">
            {analysis?.risk_level && (
              <div className={`px-4 py-1.5 rounded-full border text-sm font-semibold flex items-center gap-2 ${getRiskColor(analysis.risk_level)}`}>
                <Activity className="w-4 h-4" />
                Risk Level: {analysis.risk_level.toUpperCase()}
              </div>
            )}
            <div className="px-4 py-1.5 rounded-full border bg-white border-slate-200 text-slate-700 text-sm font-semibold flex items-center gap-2 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300">
              <Banknote className="w-4 h-4 text-emerald-500" />
              Target Savings: 20%
            </div>
          </div>
        </motion.div>

        {/* 1. Top Row (4 KPI Cards) */}
        <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Income */}
          <motion.div variants={item} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Card className="border-0 shadow-sm bg-white hover:shadow-md transition-shadow relative overflow-hidden group h-full dark:bg-slate-900">
              <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-blue-400 to-blue-600 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-blue-50 text-blue-600 rounded-lg dark:bg-blue-950/50 dark:text-blue-400">
                    <Wallet className="w-5 h-5" />
                  </div>
                  <Badge variant="outline" className="text-slate-500 bg-slate-50 font-medium dark:text-slate-400 dark:bg-slate-800">Monthly</Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Total Income</p>
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                    <CountUp prefix="₹" to={income} />
                  </h3>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Savings Rate */}
          <motion.div variants={item} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Card className="border-0 shadow-sm bg-white hover:shadow-md transition-shadow relative overflow-hidden group h-full dark:bg-slate-900">
              <div className={`absolute bottom-0 left-0 h-1.5 bg-emerald-500`} style={{ width: `${Math.min(savingsRate, 100)}%`, transition: 'width 1s ease-in-out' }} />
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg dark:bg-emerald-950/50 dark:text-emerald-400">
                    <PiggyBank className="w-5 h-5" />
                  </div>
                  <Badge variant="outline" className="text-slate-500 bg-slate-50 font-medium dark:text-slate-400 dark:bg-slate-800">Target {targetSavingsRate}%</Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Savings Rate</p>
                  <div className="flex items-end gap-2">
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                      <CountUp to={savingsRate} suffix="%" />
                    </h3>
                    {savingsRate < targetSavingsRate ? (
                      <span className="text-xs font-semibold text-red-500 mb-1 flex items-center bg-red-50 px-1.5 py-0.5 rounded dark:bg-red-950/50 dark:text-red-400">-{(targetSavingsRate - savingsRate).toFixed(1)}% off</span>
                    ) : (
                      <span className="text-xs font-semibold text-emerald-600 mb-1 flex items-center bg-emerald-50 px-1.5 py-0.5 rounded dark:bg-emerald-950/50 dark:text-emerald-400">On track</span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Risk Score */}
          <motion.div variants={item} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Card className="border-0 shadow-sm bg-white hover:shadow-md transition-shadow relative overflow-hidden group h-full dark:bg-slate-900">
              <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-orange-400 to-orange-600 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-orange-50 text-orange-600 rounded-lg dark:bg-orange-950/50 dark:text-orange-400">
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <Badge variant="outline" className="text-slate-500 bg-slate-50 font-medium dark:text-slate-400 dark:bg-slate-800">Health</Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Financial Health</p>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50">
                    {savingsRate >= 20 ? 'Good' : savingsRate >= 10 ? 'Fair' : 'Needs Work'}
                  </h3>
                  <p className="text-xs text-slate-400">View detailed analysis in Insights</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Inflation Pressure */}
          <motion.div variants={item} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Card className="border-0 shadow-sm bg-white hover:shadow-md transition-shadow relative overflow-hidden group h-full dark:bg-slate-900">
              <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-purple-400 to-purple-600 transform origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-purple-50 text-purple-600 rounded-lg dark:bg-purple-950/50 dark:text-purple-400">
                    <TrendingUp className="w-5 h-5" />
                  </div>
                  <Badge variant="outline" className="text-slate-500 bg-slate-50 font-medium dark:text-slate-400 dark:bg-slate-800">CPI</Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Budget Status</p>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50">
                    {savingsRate >= 20 ? 'On Track' : 'Review Needed'}
                  </h3>
                  <p className="text-xs text-slate-400">Check Insights for details</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>

        {/* 2. Main Section (2 Columns) */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          
          {/* LEFT: Spending Distribution */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }} 
            animate={{ opacity: 1, scale: 1 }} 
            transition={{ delay: 0.2 }}
            className="lg:col-span-3"
          >
            <Card className="h-full border-0 shadow-sm flex flex-col dark:bg-slate-900">
              <CardHeader className="pb-2 border-b border-slate-50 mb-2 dark:border-slate-800">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-lg dark:text-slate-50">Spending Distribution</CardTitle>
                  <Info className="w-5 h-5 text-slate-400" />
                </div>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-between">
                <div className="h-[280px] w-full">
                  {data?.category_breakdown?.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={data.category_breakdown.map((d: any) => ({...d, value: d.amount}))}
                          dataKey="amount"
                          nameKey="category"
                          cx="50%"
                          cy="45%"
                          innerRadius={70}
                          outerRadius={105}
                          paddingAngle={2}
                          stroke="none"
                          animationDuration={1500}
                          animationEasing="ease-out"
                        >
                          {data.category_breakdown.map((entry: any) => (
                            <Cell key={entry.category} fill={categoryColors[entry.category] || '#E5E7EB'} />
                          ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend content={renderLegend} verticalAlign="bottom" />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:text-slate-500">
                      <PieChart className="w-8 h-8 mb-2 opacity-50" />
                      <p className="text-sm font-medium">No spending data available yet</p>
                      <p className="text-xs mt-1">Add expenses to see your breakdown.</p>
                    </div>
                  )}
                </div>
                
                {/* Summary Text below chart */}
                {data?.category_breakdown?.length > 0 && (
                  <div className="mt-4 p-4 bg-indigo-50/50 rounded-xl text-sm text-indigo-900 border border-indigo-100/50 flex items-start gap-3 dark:bg-indigo-950/30 dark:text-indigo-200 dark:border-indigo-900/50">
                    <HeartPulse className="w-5 h-5 text-indigo-500 mt-0.5 shrink-0 dark:text-indigo-400" />
                    <div className="leading-relaxed">
                      <span className="font-semibold">Key Insight: </span>
                      {(() => {
                        const topCategory = [...data.category_breakdown].sort((a: any, b: any) => b.amount - a.amount)[0];
                        const pct = ((topCategory.amount / totalSpent) * 100).toFixed(0);
                        return `You spend ${pct}% of your expenses on ${topCategory.category}. We recommend trying to keep this under 30% to improve savings.`;
                      })()}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* RIGHT: Quick Actions Panel */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }} 
            animate={{ opacity: 1, x: 0 }} 
            transition={{ delay: 0.3 }}
            className="lg:col-span-2"
          >
            <Card className="h-full border border-indigo-100 shadow-sm flex flex-col bg-indigo-50/30 dark:border-indigo-900/50 dark:bg-indigo-950/20">
              <CardHeader className="pb-4 border-b border-indigo-100/50 bg-white/50 backdrop-blur-sm rounded-t-xl dark:border-indigo-900/30 dark:bg-slate-900/50">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-lg flex items-center gap-2 text-slate-800 dark:text-slate-50">
                    <Lightbulb className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                    Quick Actions
                  </CardTitle>
                </div>
                <CardDescription className="text-slate-500 pt-1 dark:text-slate-400">Improve your financial health</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 p-6">
                <div className="space-y-3">
                  <Link href="/expenses/add">
                    <div className="p-4 bg-white rounded-xl border border-indigo-100 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800/80 dark:border-indigo-900/30 dark:hover:bg-slate-800">
                      <h4 className="font-semibold text-sm mb-1 dark:text-slate-50">Track an Expense</h4>
                      <p className="text-xs text-slate-600 dark:text-slate-400">Keep your spending records up to date</p>
                    </div>
                  </Link>
                  <Link href="/insights">
                    <div className="p-4 bg-white rounded-xl border border-indigo-100 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800/80 dark:border-indigo-900/30 dark:hover:bg-slate-800">
                      <h4 className="font-semibold text-sm mb-1 dark:text-slate-50">View Detailed Analysis</h4>
                      <p className="text-xs text-slate-600 dark:text-slate-400">Get AI-powered financial insights</p>
                    </div>
                  </Link>
                  <Link href="/expenses">
                    <div className="p-4 bg-white rounded-xl border border-indigo-100 hover:shadow-md transition-shadow cursor-pointer dark:bg-slate-800/80 dark:border-indigo-900/30 dark:hover:bg-slate-800">
                      <h4 className="font-semibold text-sm mb-1 dark:text-slate-50">Manage Expenses</h4>
                      <p className="text-xs text-slate-600 dark:text-slate-400">View, edit, or delete your expenses</p>
                    </div>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* 3. Financial Health Summary */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 className="text-xl font-bold text-slate-900 mb-4 px-1 dark:text-slate-50">Financial Health Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            
            <motion.div whileHover={{ y: -4, scale: 1.01 }} className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-start gap-4 hover:shadow-md transition-all dark:bg-slate-900 dark:border-slate-800">
              <div className="p-3 bg-red-50 text-red-600 rounded-xl shrink-0 dark:bg-red-950/50 dark:text-red-400">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="pt-0.5">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1 dark:text-slate-200">Fixed Expenses</h4>
                <p className="text-sm text-slate-600 leading-relaxed dark:text-slate-400"><span className="font-semibold text-red-600 dark:text-red-400">Too High ({(monthlyFixedExpenses/(income||1)*100).toFixed(0)}%)</span>. Your fixed costs are consuming too much baseline income. Consider downsizing.</p>
              </div>
            </motion.div>

            <motion.div whileHover={{ y: -4, scale: 1.01 }} className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-start gap-4 hover:shadow-md transition-all dark:bg-slate-900 dark:border-slate-800">
              <div className="p-3 bg-amber-50 text-amber-600 rounded-xl shrink-0 dark:bg-amber-950/50 dark:text-amber-400">
                <PiggyBank className="w-6 h-6" />
              </div>
              <div className="pt-0.5">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1 dark:text-slate-200">Savings Rate</h4>
                <p className="text-sm text-slate-600 leading-relaxed dark:text-slate-400"><span className="font-semibold text-amber-600 dark:text-amber-400">Below Target</span>. Your savings rate is <span className="font-medium text-slate-800 dark:text-slate-200">{savingsRate.toFixed(0)}%</span>, missing the {targetSavingsRate}% target. Immediate action required.</p>
              </div>
            </motion.div>

            <motion.div whileHover={{ y: -4, scale: 1.01 }} className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 flex items-start gap-4 hover:shadow-md transition-all dark:bg-slate-900 dark:border-slate-800">
              <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl shrink-0 dark:bg-indigo-950/50 dark:text-indigo-400">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div className="pt-0.5">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1 dark:text-slate-200">Emergency Readiness</h4>
                <p className="text-sm text-slate-600 leading-relaxed dark:text-slate-400">You can survive <span className="font-bold text-indigo-600 bg-indigo-50 px-1 rounded dark:text-indigo-400 dark:bg-indigo-950/50">{emergencyMonths} months</span> on your current emergency fund if income stops.</p>
              </div>
            </motion.div>

          </div>
        </motion.div>

        {/* 4. Recommendations Section */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <h3 className="text-xl font-bold text-slate-900 mb-4 px-1 flex items-center gap-2 dark:text-slate-50">
            <Lightbulb className="w-6 h-6 text-amber-500 dark:text-amber-400" />
            Actionable Recommendations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {analysis?.recommendations?.length > 0 ? (
              analysis.recommendations.map((rec: string, i: number) => (
                <motion.div whileHover={{ scale: 1.03, y: -5 }} whileTap={{ scale: 0.98 }} key={i} className="h-full">
                  <Card className="h-full border border-slate-200 shadow-sm hover:shadow-lg hover:border-indigo-300 transition-all cursor-pointer bg-white group dark:border-slate-700 dark:bg-slate-900 dark:hover:border-indigo-700">
                    <CardContent className="p-6 flex flex-col h-full relative overflow-hidden">
                      <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-indigo-50 to-transparent rounded-bl-full opacity-50 transition-transform group-hover:scale-110 dark:from-indigo-950/50" />
                      <div className="bg-indigo-50 w-10 h-10 rounded-full flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors dark:bg-indigo-950/50">
                        <ArrowRight className="w-5 h-5 text-indigo-600 group-hover:text-white transition-colors dark:text-indigo-400" />
                      </div>
                      <p className="text-sm text-slate-700 font-medium leading-relaxed flex-1 group-hover:text-slate-900 transition-colors dark:text-slate-300 dark:group-hover:text-slate-50">{rec}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            ) : (
              <div className="col-span-full bg-white border border-dashed border-slate-300 rounded-2xl p-10 flex flex-col items-center justify-center text-slate-500 shadow-sm dark:bg-slate-900 dark:border-slate-700 dark:text-slate-400">
                <Lightbulb className="w-10 h-10 mb-3 text-amber-400 opacity-60" />
                <p className="text-base font-semibold text-slate-700 dark:text-slate-300">No actions required right now</p>
                <p className="text-sm mt-1">Keep up the excellent financial habits!</p>
              </div>
            )}
          </div>
        </motion.div>

      </div>
    </Sidebar>
  );
}
