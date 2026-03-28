'use client';

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  // Return safe fallback during SSG or when ThemeProvider isn't mounted yet
  if (!context) {
    return { theme: 'light', toggleTheme: () => {} };
  }
  return context;
}

// Toast notification for keyboard shortcut toggle
function ThemeToast({ message, visible }: { message: string; visible: boolean }) {
  if (!visible) return null;

  return (
    <div
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] pointer-events-none"
      role="status"
      aria-live="polite"
    >
      <div className="bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 px-5 py-2.5 rounded-full text-sm font-medium shadow-2xl animate-fade-in-up flex items-center gap-2">
        <span className="text-base">{message.includes('Dark') ? '🌙' : '☀️'}</span>
        {message}
      </div>
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-up {
          animation: fadeInUp 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);
  const [toast, setToast] = useState<{ message: string; visible: boolean }>({
    message: '',
    visible: false,
  });

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const stored = localStorage.getItem('theme') as Theme | null;
    if (stored === 'dark' || stored === 'light') {
      setTheme(stored);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
    }
    setMounted(true);
  }, []);

  // Apply theme class to <html>
  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);

    // Enable transitions after a brief delay (prevents FOUC)
    requestAnimationFrame(() => {
      root.classList.add('theme-transition');
    });
  }, [theme, mounted]);

  const showToast = useCallback((message: string) => {
    setToast({ message, visible: true });
    setTimeout(() => setToast({ message: '', visible: false }), 2000);
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next = prev === 'light' ? 'dark' : 'light';
      return next;
    });
  }, []);

  // Keyboard shortcut: Ctrl+Shift+L (Cmd+Shift+L on Mac)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        setTheme((prev) => {
          const next = prev === 'light' ? 'dark' : 'light';
          showToast(`${next === 'dark' ? 'Dark' : 'Light'} mode activated`);
          return next;
        });
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showToast]);

  // Prevent hydration mismatch — render children only after mount
  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
      <ThemeToast message={toast.message} visible={toast.visible} />
    </ThemeContext.Provider>
  );
}
