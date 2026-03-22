'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getFinancialAnalysis, getCurrentSession } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  AlertTriangle, 
  Lightbulb,
  ArrowRight,
  Gift,
  Fuel,
  Building2
} from 'lucide-react';

export default function InsightsPage() {
  const router = useRouter();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dataFetched, setDataFetched] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      if (dataFetched) return; // Prevent duplicate fetches
      
      const session = await getCurrentSession();
      if (!session) {
        router.push('/login');
        return;
      }
      
      setDataFetched(true);
      fetchAnalysis();
    };
    
    checkAuth();
  }, [router, dataFetched]);

  const fetchAnalysis = async () => {
    try {
      console.log('[Insights] Starting analysis fetch');
      const storedProfile = localStorage.getItem('financial_profile');
      let profile = storedProfile ? JSON.parse(storedProfile) : { monthly_income: 50000 };

      const response = await getFinancialAnalysis({
        monthly_income: profile.monthly_income,
        medical_risk: profile.medical_risk || 'low',
        family_dependency: profile.family_dependency || 0
      });
      
      console.log('[Insights] Analysis data received');
      setAnalysis(response.data);
    } catch (error: any) {
      console.error('[Insights] Error fetching analysis:', error);
      if (error.response?.status === 401) {
        console.log('[Insights] Token expired, redirecting to login');
        localStorage.removeItem('token');
        localStorage.removeItem('userEmail');
        router.push('/login');
      }
    } finally {
      console.log('[Insights] Setting loading to false');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Sidebar>
        <div className="flex h-full items-center justify-center p-8">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm font-medium text-gray-500">Loading insights...</p>
          </div>
        </div>
      </Sidebar>
    );
  }

  return (
    <Sidebar>
      <div className="min-h-screen bg-gray-50/50 p-6 lg:p-10 space-y-8">
        
        {/* Header */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Financial Insights</h1>
          <p className="text-gray-500 mt-1">Detailed analysis powered by real Indian market data</p>
        </motion.div>

        {/* All Recommendations */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        >
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
            <Lightbulb className="w-5 h-5 text-amber-500" />
            AI-Powered Recommendations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysis?.recommendations?.map((rec: string, i: number) => (
              <motion.div 
                whileHover={{ scale: 1.02, y: -2 }} 
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + (i * 0.05) }}
              >
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

        {/* Deals & Offers Section */}
        {analysis?.deals && analysis.deals.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          >
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
              <Gift className="w-5 h-5 text-green-600" />
              Personalized Deals & Offers
            </h3>
            <p className="text-sm text-gray-600 mb-4">Based on your spending patterns</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.deals.map((deal: any, i: number) => (
                <motion.div 
                  whileHover={{ scale: 1.02 }} 
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + (i * 0.1) }}
                >
                  <Card className="border border-green-100 bg-gradient-to-br from-green-50 to-white">
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <p className="text-xs text-green-600 font-semibold uppercase tracking-wide">
                            {deal.category_trigger} Spending: ₹{deal.spend_amount?.toLocaleString()}
                          </p>
                          <h4 className="text-lg font-bold text-gray-900 mt-1">{deal.deal?.merchant}</h4>
                        </div>
                        <Badge className="bg-green-600 text-white">Active</Badge>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{deal.deal?.description}</p>
                      <div className="bg-gray-100 px-3 py-2 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Coupon Code</p>
                        <p className="text-sm font-mono font-bold text-gray-900">{deal.deal?.code}</p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Market Data Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* RBI EMI Impact */}
          {analysis?.emi_impact && analysis.emi_impact.current_repo_rate && (
            <motion.div 
              initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            >
              <Card className="border border-blue-100 bg-gradient-to-br from-blue-50 to-white h-full">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-900">
                    <Building2 className="w-5 h-5" />
                    RBI Repo Rate Impact
                  </CardTitle>
                  <CardDescription>Live data from Reserve Bank of India</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Current Repo Rate</span>
                    <span className="text-3xl font-bold text-blue-600">
                      {analysis.emi_impact.current_repo_rate}%
                    </span>
                  </div>
                  {analysis.emi_impact.projected_emi_increase > 0 && (
                    <div className="bg-blue-100 p-4 rounded-lg">
                      <p className="text-xs text-blue-800 font-semibold mb-1">Potential Impact on Your EMI</p>
                      <p className="text-lg font-bold text-blue-900">
                        +₹{analysis.emi_impact.projected_emi_increase} per month
                      </p>
                      <p className="text-xs text-blue-700 mt-1">If RBI raises rates by 0.25%</p>
                    </div>
                  )}
                  <p className="text-xs text-gray-600 leading-relaxed">
                    {analysis.emi_impact.alert_message}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Fuel Prices */}
          {analysis?.fuel_impact && analysis.fuel_impact.current_avg_petrol_price && (
            <motion.div 
              initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            >
              <Card className="border border-orange-100 bg-gradient-to-br from-orange-50 to-white h-full">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-orange-900">
                    <Fuel className="w-5 h-5" />
                    Fuel Price Tracker
                  </CardTitle>
                  <CardDescription>Real-time petrol prices across metros</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Average Petrol Price</span>
                    <span className="text-3xl font-bold text-orange-600">
                      ₹{analysis.fuel_impact.current_avg_petrol_price}
                    </span>
                  </div>
                  {analysis.fuel_impact.metro_prices && Object.keys(analysis.fuel_impact.metro_prices).length > 0 && (
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(analysis.fuel_impact.metro_prices).map(([city, price]: [string, any]) => (
                        <div key={city} className="bg-orange-100 p-3 rounded-lg text-center">
                          <p className="text-xs text-orange-700 font-semibold">{city}</p>
                          <p className="text-lg font-bold text-orange-900">₹{price}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="bg-orange-100 p-3 rounded-lg">
                    <p className="text-xs text-orange-900 leading-relaxed">
                      {analysis.fuel_impact.insight}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>

        {/* Inflation Insights */}
        {analysis?.insights && analysis.insights.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          >
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              Inflation Analysis
            </h3>
            <div className="grid grid-cols-1 gap-3">
              {analysis.insights.map((insight: string, i: number) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + (i * 0.05) }}
                >
                  <Card className="border border-purple-100 bg-white">
                    <CardContent className="p-4 flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-gray-700 leading-relaxed">{insight}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

      </div>
    </Sidebar>
  );
}
