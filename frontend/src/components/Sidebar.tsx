'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  PlusCircle, 
  LineChart, 
  LogOut,
  ChevronLeft,
  ChevronRight,
  IndianRupee,
  Receipt
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';

export default function Sidebar({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    document.cookie = 'token=; path=/; max-age=0';
    router.push('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Expenses', path: '/expenses', icon: Receipt },
    { name: 'Add Expense', path: '/expenses/add', icon: PlusCircle },
    { name: 'Analysis', path: '/insights', icon: LineChart },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50/50 dark:bg-slate-950">
      {/* Sidebar Navigation */}
      <motion.aside
        initial={false}
        animate={{ width: isCollapsed ? 80 : 280 }}
        className="relative z-20 flex flex-col hidden md:flex border-r border-gray-200/60 bg-white/80 backdrop-blur-xl h-screen sticky top-0 transition-all duration-300 shadow-sm dark:border-slate-700/60 dark:bg-slate-900/80"
      >
        <div className="flex h-16 items-center justify-between px-4 py-6 border-b border-gray-100 dark:border-slate-800">
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center gap-2"
              >
                <div className="bg-indigo-600 text-white p-1.5 rounded-lg">
                  <IndianRupee className="w-5 h-5" />
                </div>
                <span className="text-lg font-bold text-gray-900 tracking-tight dark:text-slate-50">FinOptimizer</span>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-900 transition-colors dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-50"
          >
            {isCollapsed ? <ChevronRight className="w-5 h-5 mx-auto" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        <div className="flex-1 py-6 px-3 space-y-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.path);
            const Icon = item.icon;
            
            return (
              <button
                key={item.path}
                onClick={() => router.push(item.path)}
                className={`w-full flex items-center relative group rounded-xl px-3 py-3 font-medium transition-all duration-200 ${
                  isActive 
                    ? 'text-indigo-700 bg-indigo-50/80 shadow-sm ring-1 ring-indigo-100 dark:text-indigo-300 dark:bg-indigo-950/50 dark:ring-indigo-900' 
                    : 'text-gray-600 hover:bg-gray-100/80 hover:text-gray-900 dark:text-slate-400 dark:hover:bg-slate-800/80 dark:hover:text-slate-50'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-indigo-600 rounded-r-full dark:bg-indigo-400"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  />
                )}
                <Icon className={`w-5 h-5 flex-shrink-0 ${isCollapsed ? 'mx-auto' : 'mr-3'} ${isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 group-hover:text-gray-700 dark:text-slate-500 dark:group-hover:text-slate-300'}`} />
                
                <AnimatePresence mode="wait">
                  {!isCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      className="whitespace-nowrap"
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </button>
            );
          })}
        </div>

        {/* Theme Toggle + Logout at bottom */}
        <div className="p-4 border-t border-gray-100 space-y-2 dark:border-slate-800">
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'px-3'}`}>
            <ThemeToggle />
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center group rounded-xl px-3 py-3 font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 transition-all duration-200 dark:text-slate-400 dark:hover:bg-red-950/50 dark:hover:text-red-400"
          >
            <LogOut className={`w-5 h-5 flex-shrink-0 ${isCollapsed ? 'mx-auto' : 'mr-3'} text-gray-400 group-hover:text-red-500 dark:text-slate-500 dark:group-hover:text-red-400`} />
            <AnimatePresence mode="wait">
              {!isCollapsed && (
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className="whitespace-nowrap"
                >
                  Logout
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <main className="flex-1 w-full overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
