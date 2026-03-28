import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  
  const variants: Record<string, string> = {
    default: "border-transparent bg-gray-900 text-gray-50 hover:bg-gray-900/80 dark:bg-slate-50 dark:text-slate-900 dark:hover:bg-slate-50/80",
    secondary: "border-transparent bg-gray-100 text-gray-900 hover:bg-gray-100/80 dark:bg-slate-800 dark:text-slate-50 dark:hover:bg-slate-800/80",
    destructive: "border-transparent bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300",
    success: "border-transparent bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300",
    warning: "border-transparent bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300",
    outline: "text-gray-950 dark:text-slate-50",
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
