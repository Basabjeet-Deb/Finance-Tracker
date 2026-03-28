'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Always redirect to login page first
    router.push('/login');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-950">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4 dark:border-indigo-800 dark:border-t-indigo-400" />
        <h1 className="text-xl font-semibold text-gray-800 dark:text-slate-200">Redirecting to login...</h1>
      </div>
    </div>
  );
}
