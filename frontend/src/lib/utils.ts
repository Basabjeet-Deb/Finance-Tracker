import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
};

export const getCurrentMonth = (): string => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
};

export const categories = [
  'Food',
  'Rent',
  'Transport',
  'Bills',
  'Entertainment',
  'Other',
];

export const categoryColors: { [key: string]: string } = {
  Food: '#10B981',
  Rent: '#3B82F6',
  Transport: '#F59E0B',
  Bills: '#EF4444',
  Entertainment: '#8B5CF6',
  Other: '#6B7280',
};
