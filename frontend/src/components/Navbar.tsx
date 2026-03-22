'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getStoredEmail, clearAuth } from '@/lib/auth';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    setUserEmail(getStoredEmail());
  }, []);

  const handleLogout = () => {
    clearAuth();
    router.push('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Add Expense', path: '/expenses/add' },
    { name: 'Insights', path: '/insights' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold text-indigo-600">
              🇮🇳 Finance Tracker
            </h1>
            <div className="hidden md:flex space-x-4">
              {navItems.map((item) => (
                <button
                  key={item.path}
                  onClick={() => router.push(item.path)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                    pathname === item.path
                      ? 'bg-indigo-50 text-indigo-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {item.name}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {userEmail && (
              <div className="flex items-center space-x-2">
                <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-semibold">
                  ADMIN
                </span>
                <span className="text-sm text-gray-600 hidden sm:inline">
                  {userEmail}
                </span>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="text-sm text-gray-600 hover:text-gray-800 font-medium px-3 py-2 rounded-md hover:bg-gray-50 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
