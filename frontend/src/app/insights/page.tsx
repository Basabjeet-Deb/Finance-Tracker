'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { analyzeFinancialHealth, getCurrentSession } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  AlertTriangle, 
  Lightbulb, 
  PiggyBank,
  Activity,
  Target,
  Zap,
  DollarSign,
  Shield,
  Info
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function InsightsPage() {
  const router = useRouter();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkAuthAndFetch = async () => {
      try {
        const session = await getCurrentSession();
        if (!session) {
          router.push('/login');
          return;
        }
        
        await fetchAnalysis();
      } catch (error) {
        console.error('[Insights] Auth check error:', error);
        router.push('/login');
      }
    };
    
    checkAuthAndFetch();
  }, [router]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get user profile from localStorage
      const storedProfile = localStorage.getItem('financial_profile');
      const profile = storedProfile ? JSON.parse(storedProfile) : { monthly_income: 50000 };
      
      // Call unified analysis API
      const response = await analyzeFinancialHealth({
        user_profile: {
          monthly_income: profile.monthly_income || 50000,
          emi_amount: profile.emi_amount || 0,
          medical_risk: profile.medical_risk || 'low',
          family_dependency: profile.dependents || 0,
          has_emergency_fund: profile.has_emergency_fund || false
        },
        use_current_month: true
      });
      
      setAnalysis(response.data);
    } catch (error: any) {
      console.error('[Insights] Error fetching analysis:', error);
      setError(error.response?.data?.detail?.message || 'Failed to load analysis');
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
              ANALYZING YOUR FINANCES...
            </p>
          </div>
        </div>
      </Sidebar>
    );
  }

  if (error) {
    return (
      <Sidebar>
        <div className="flex h-full items-center justify-center p-8 bg-slate-50 dark:bg-transparent">
          <Card className="max-w-md">
            <CardContent className="p-6 text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4 dark:text-red-400" />
              <h3 className="text-lg font-bold text-slate-900 mb-2 dark:text-slate-50">Analysis Failed</h3>
              <p className="text-sm text-slate-600 mb-4 dark:text-slate-400">{error}</p>
              <button
                onClick={fetchAnalysis}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors dark:bg-indigo-500 dark:hover:bg-indigo-600"
              >
                Try Again
              </button>
            </CardContent>
          </Card>
        </div>
      </Sidebar>
    );
  }

  if (!analysis) {
    return (
      <Sidebar>
        <div className="flex h-full items-center justify-center p-8 bg-slate-50 dark:bg-transparent">
          <p className="text-slate-500 dark:text-slate-400">No analysis data available</p>
        </div>
      </Sidebar>
    );
  }

  const getRiskColor = (level: string) => {
    if (level === 'critical') return 'bg-gradient-to-r from-red-500 to-red-600';
    if (level === 'high') return 'bg-gradient-to-r from-orange-500 to-orange-600';
    if (level === 'medium') return 'bg-gradient-to-r from-amber-500 to-amber-600';
    return 'bg-gradient-to-r from-emerald-500 to-emerald-600';
  };

  const getRiskBorderColor = (level: string) => {
    if (level === 'critical') return 'border-red-300 bg-red-50/50 dark:border-red-800 dark:bg-red-950/30';
    if (level === 'high') return 'border-orange-300 bg-orange-50/50 dark:border-orange-800 dark:bg-orange-950/30';
    if (level === 'medium') return 'border-amber-300 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-950/30';
    return 'border-emerald-300 bg-emerald-50/50 dark:border-emerald-800 dark:bg-emerald-950/30';
  };

  const getRiskIcon = (level: string) => {
    if (level === 'critical') return '🚨';
    if (level === 'high') return '⚠️';
    if (level === 'medium') return '⚡';
    return '✅';
  };

  return (
    <Sidebar>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 p-6 lg:p-10 space-y-8 dark:from-slate-950 dark:via-slate-950 dark:to-slate-950">
        
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }} 
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
        >
          <div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-slate-50 dark:to-slate-300">
              Financial Insights
            </h1>
            <p className="text-slate-600 mt-2 font-medium dark:text-slate-400">AI-powered analysis of your financial health</p>
          </div>
          <div className="flex gap-3 items-center">
            <Badge className={`${getRiskColor(analysis.risk_level)} text-white px-6 py-2.5 text-sm font-bold shadow-lg`}>
              {getRiskIcon(analysis.risk_level)} {analysis.risk_level.toUpperCase()}
            </Badge>
            <Badge variant="outline" className="px-6 py-2.5 text-sm font-bold border-2 bg-white shadow-sm dark:bg-slate-800 dark:border-slate-700">
              Score: {analysis.risk_score}/100
            </Badge>
          </div>
        </motion.div>

        {/* Risk Overview - Enhanced */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card className={`border-2 ${getRiskBorderColor(analysis.risk_level)} shadow-xl`}>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl dark:text-slate-50">
                <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                Financial Health Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <motion.div 
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="text-center p-6 bg-gradient-to-br from-emerald-50 to-emerald-100/50 rounded-2xl border-2 border-emerald-200 shadow-sm dark:from-emerald-950/50 dark:to-emerald-900/30 dark:border-emerald-800"
                >
                  <PiggyBank className="w-8 h-8 mx-auto mb-3 text-emerald-600 dark:text-emerald-400" />
                  <p className="text-xs font-bold text-emerald-700 mb-2 uppercase tracking-wider dark:text-emerald-300">Savings Rate</p>
                  <p className="text-3xl font-black text-emerald-900 dark:text-emerald-100">{analysis.allocation.savings?.toFixed(1)}%</p>
                </motion.div>
                <motion.div 
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100/50 rounded-2xl border-2 border-purple-200 shadow-sm dark:from-purple-950/50 dark:to-purple-900/30 dark:border-purple-800"
                >
                  <TrendingUp className="w-8 h-8 mx-auto mb-3 text-purple-600 dark:text-purple-400" />
                  <p className="text-xs font-bold text-purple-700 mb-2 uppercase tracking-wider dark:text-purple-300">Inflation</p>
                  <p className="text-3xl font-black text-purple-900 capitalize dark:text-purple-100">{analysis.inflation.pressure}</p>
                </motion.div>
                <motion.div 
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-2xl border-2 border-blue-200 shadow-sm dark:from-blue-950/50 dark:to-blue-900/30 dark:border-blue-800"
                >
                  <Shield className="w-8 h-8 mx-auto mb-3 text-blue-600 dark:text-blue-400" />
                  <p className="text-xs font-bold text-blue-700 mb-2 uppercase tracking-wider dark:text-blue-300">Survival</p>
                  <p className="text-3xl font-black text-blue-900 dark:text-blue-100">{analysis.survival_months} mo</p>
                </motion.div>
                <motion.div 
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="text-center p-6 bg-gradient-to-br from-orange-50 to-orange-100/50 rounded-2xl border-2 border-orange-200 shadow-sm dark:from-orange-950/50 dark:to-orange-900/30 dark:border-orange-800"
                >
                  <DollarSign className="w-8 h-8 mx-auto mb-3 text-orange-600 dark:text-orange-400" />
                  <p className="text-xs font-bold text-orange-700 mb-2 uppercase tracking-wider dark:text-orange-300">Spending</p>
                  <p className="text-2xl font-black text-orange-900 dark:text-orange-100">₹{(analysis.total_monthly_spending/1000).toFixed(0)}k</p>
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Spending Allocation - Enhanced */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="shadow-xl border-2 border-slate-200 dark:border-slate-700">
            <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100/50 border-b dark:from-slate-800/50 dark:to-slate-900/50 dark:border-slate-700">
              <CardTitle className="flex items-center gap-3 text-xl dark:text-slate-50">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                Spending Allocation
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-6">
                {Object.entries(analysis.allocation).map(([category, percentage]: [string, any]) => {
                  const status = analysis.spending_status[category];
                  const amount = analysis.amounts[category];
                  const threshold = analysis.adjusted_thresholds[category];
                  
                  const getBarColor = () => {
                    if (status === 'high' || status === 'low') return 'from-red-500 to-red-600';
                    if (category === 'savings') return 'from-emerald-500 to-emerald-600';
                    if (category === 'fixed') return 'from-blue-500 to-blue-600';
                    if (category === 'essential') return 'from-purple-500 to-purple-600';
                    return 'from-orange-500 to-orange-600';
                  };
                  
                  return (
                    <div key={category} className="space-y-3">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-bold text-slate-800 capitalize min-w-[100px] dark:text-slate-200">{category}</span>
                          {status === 'high' && (
                            <Badge variant="destructive" className="text-xs font-bold">⚠️ High</Badge>
                          )}
                          {status === 'low' && (
                            <Badge variant="destructive" className="text-xs font-bold">⚠️ Low</Badge>
                          )}
                          {status === 'good' && (
                            <Badge className="bg-emerald-500 text-white text-xs font-bold">✓ Good</Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-lg font-black text-slate-900 dark:text-slate-50">{percentage?.toFixed(1)}%</span>
                          <span className="text-sm text-slate-600 font-medium dark:text-slate-400">₹{amount?.toLocaleString()}</span>
                        </div>
                      </div>
                      <div className="relative h-3 bg-slate-100 rounded-full overflow-hidden shadow-inner dark:bg-slate-800">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(percentage, 100)}%` }}
                          transition={{ duration: 1, ease: "easeOut" }}
                          className={`absolute left-0 top-0 h-full bg-gradient-to-r ${getBarColor()} shadow-sm`}
                        />
                        {threshold && (
                          <div
                            className="absolute top-0 h-full w-1 bg-slate-700 shadow-md dark:bg-slate-300"
                            style={{ left: `${threshold}%` }}
                            title={`Target: ${threshold}%`}
                          />
                        )}
                      </div>
                      {threshold && (
                        <p className="text-xs text-slate-500 font-medium dark:text-slate-400">Target: {threshold}% {percentage > threshold ? `(${(percentage - threshold).toFixed(1)}% over)` : `(${(threshold - percentage).toFixed(1)}% under)`}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Priority Actions - Enhanced */}
        {analysis.priority_actions?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="border-2 border-orange-200 bg-gradient-to-br from-orange-50/50 to-amber-50/30 shadow-xl dark:border-orange-800 dark:from-orange-950/20 dark:to-amber-950/10">
              <CardHeader className="bg-gradient-to-r from-orange-100/50 to-amber-100/50 border-b border-orange-200 dark:from-orange-900/30 dark:to-amber-900/30 dark:border-orange-800">
                <CardTitle className="flex items-center gap-3 text-xl text-orange-900 dark:text-orange-200">
                  <div className="p-2 bg-gradient-to-br from-orange-500 to-amber-600 rounded-lg animate-pulse">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                  Priority Actions
                  <Badge className="bg-orange-500 text-white ml-auto">Urgent</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {analysis.priority_actions.map((action: string, index: number) => (
                    <motion.div 
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                      whileHover={{ scale: 1.02, x: 5 }}
                      className="flex items-start gap-4 p-5 bg-white rounded-xl border-2 border-orange-200 shadow-md hover:shadow-lg transition-all dark:bg-slate-900/80 dark:border-orange-800/50"
                    >
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-600 text-white rounded-full flex items-center justify-center text-lg font-black shadow-md">
                        {index + 1}
                      </div>
                      <p className="text-sm text-slate-800 flex-1 font-medium leading-relaxed pt-2 dark:text-slate-200">{action}</p>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Money Leaks - Enhanced */}
        {analysis.money_leaks?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="border-2 border-red-200 shadow-xl dark:border-red-800">
              <CardHeader className="bg-gradient-to-r from-red-50 to-rose-50 border-b border-red-200 dark:from-red-950/30 dark:to-rose-950/30 dark:border-red-800">
                <CardTitle className="flex items-center gap-3 text-xl text-red-900 dark:text-red-200">
                  <div className="p-2 bg-gradient-to-br from-red-500 to-rose-600 rounded-lg">
                    <AlertTriangle className="w-6 h-6 text-white" />
                  </div>
                  Money Leaks Detected
                  <Badge variant="destructive" className="ml-auto font-bold">{analysis.money_leaks.length} Found</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {analysis.money_leaks.map((leak: any, index: number) => (
                    <motion.div 
                      key={index}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                      whileHover={{ scale: 1.02 }}
                      className="p-6 bg-gradient-to-br from-red-50 to-rose-50 rounded-xl border-2 border-red-200 shadow-md dark:from-red-950/30 dark:to-rose-950/30 dark:border-red-800/50"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-black text-lg text-slate-900 dark:text-slate-50">{leak.category}</h4>
                        <Badge variant="destructive" className="font-bold text-sm">{leak.percentage?.toFixed(1)}% of income</Badge>
                      </div>
                      <p className="text-sm text-slate-700 mb-4 font-medium leading-relaxed dark:text-slate-300">{leak.message}</p>
                      <div className="flex gap-6 text-xs text-slate-600 bg-white/50 p-3 rounded-lg dark:bg-slate-900/50 dark:text-slate-400">
                        <span className="font-bold">💰 Amount: ₹{leak.amount?.toLocaleString()}</span>
                        <span className="font-bold">📊 Reason: {leak.reason?.replace('_', ' ')}</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Recommendations */}
        {analysis.recommendations?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 dark:text-slate-50">
                  <Lightbulb className="w-5 h-5 text-amber-500 dark:text-amber-400" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.recommendations.map((rec: string, index: number) => (
                    <div key={index} className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-indigo-300 transition-colors dark:bg-slate-800/50 dark:border-slate-700 dark:hover:border-indigo-700">
                      <p className="text-sm text-slate-700 dark:text-slate-300">{rec}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Cost Optimization Opportunities */}
        {analysis.optimization_opportunities?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card className="border-emerald-200 bg-emerald-50/30 dark:border-emerald-800 dark:bg-emerald-950/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-emerald-900 dark:text-emerald-200">
                  <DollarSign className="w-5 h-5" />
                  Cost Optimization Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.optimization_opportunities.map((opp: any, index: number) => (
                    <div key={index} className="p-5 bg-white rounded-lg border border-emerald-200 dark:bg-slate-900/80 dark:border-emerald-800/50">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-semibold text-slate-900 dark:text-slate-50">{opp.category}</h4>
                          <p className="text-xs text-slate-500 mt-1 dark:text-slate-400">{opp.issue}</p>
                        </div>
                        <Badge className="bg-emerald-500 text-white">
                          Save ₹{opp.optimization.potential_monthly_savings?.toLocaleString()}/mo
                        </Badge>
                      </div>
                      <div className="p-3 bg-emerald-50 rounded-lg mb-3 dark:bg-emerald-950/30">
                        <p className="text-sm font-medium text-emerald-900 mb-1 dark:text-emerald-200">{opp.optimization.description}</p>
                        <p className="text-xs text-emerald-700 dark:text-emerald-400">{opp.optimization.condition}</p>
                      </div>
                      <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400">
                        <span>Current: ₹{opp.current_spending?.toLocaleString()}/mo ({opp.percentage_of_income}%)</span>
                        <span className="font-semibold text-emerald-600 dark:text-emerald-400">Annual Impact: ₹{opp.optimization.annual_impact?.toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Violations */}
        {analysis.violations?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 dark:text-slate-50">
                  <Info className="w-5 h-5" />
                  Budget Violations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {analysis.violations.map((violation: any, index: number) => (
                    <div key={index} className="p-3 bg-amber-50 rounded-lg border border-amber-100 text-sm dark:bg-amber-950/30 dark:border-amber-800/50">
                      <p className="text-slate-700 dark:text-slate-300">{violation.message}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Refresh Button */}
        <div className="flex justify-center pt-4">
          <button
            onClick={fetchAnalysis}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium flex items-center gap-2 dark:bg-indigo-500 dark:hover:bg-indigo-600"
          >
            <TrendingUp className="w-4 h-4" />
            Refresh Analysis
          </button>
        </div>

      </div>
    </Sidebar>
  );
}
