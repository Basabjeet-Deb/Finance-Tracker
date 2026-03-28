'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import { useState } from 'react';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const [showTooltip, setShowTooltip] = useState(false);
  const isDark = theme === 'dark';

  return (
    <div className="relative">
      <motion.button
        onClick={toggleTheme}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={`
          relative p-2 rounded-xl transition-colors duration-200
          ${isDark
            ? 'bg-slate-800 hover:bg-slate-700 text-amber-400'
            : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-600'
          }
        `}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      >
        <AnimatePresence mode="wait" initial={false}>
          {isDark ? (
            <motion.div
              key="moon"
              initial={{ scale: 0, rotate: -90, opacity: 0 }}
              animate={{ scale: 1, rotate: 0, opacity: 1 }}
              exit={{ scale: 0, rotate: 90, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
            >
              <Moon className="w-5 h-5" />
            </motion.div>
          ) : (
            <motion.div
              key="sun"
              initial={{ scale: 0, rotate: 90, opacity: 0 }}
              animate={{ scale: 1, rotate: 0, opacity: 1 }}
              exit={{ scale: 0, rotate: -90, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
            >
              <Sun className="w-5 h-5" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Tooltip */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full mt-2 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs font-medium rounded-lg whitespace-nowrap shadow-xl z-50"
          >
            Toggle theme
            <span className="ml-1.5 text-slate-400 dark:text-slate-500">Ctrl+Shift+L</span>
            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-slate-900 dark:bg-slate-100 rotate-45" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
