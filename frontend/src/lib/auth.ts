/**
 * Authentication utilities
 */

const ADMIN_EMAIL = 'admin@admin.com';

export function isAdmin(email: string | null): boolean {
  return email === ADMIN_EMAIL;
}

export function getStoredEmail(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('userEmail');
}

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

export function clearAuth(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('token');
  localStorage.removeItem('userEmail');
  document.cookie = 'token=; path=/; max-age=0';
}

export function checkAdminAccess(): boolean {
  const email = getStoredEmail();
  const token = getStoredToken();
  
  if (!token || !email) {
    return false;
  }
  
  return isAdmin(email);
}

export function requireAdmin(): void {
  if (!checkAdminAccess()) {
    if (typeof window !== 'undefined') {
      clearAuth();
      window.location.href = '/login';
    }
  }
}
