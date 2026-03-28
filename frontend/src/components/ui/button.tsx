import * as React from "react"
import { motion, HTMLMotionProps } from "framer-motion"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
    
    const variants: Record<string, string> = {
      default: "bg-gray-900 text-white hover:bg-gray-800 shadow-sm dark:bg-slate-50 dark:text-slate-900 dark:hover:bg-slate-200",
      destructive: "bg-red-500 text-white hover:bg-red-600 shadow-sm dark:bg-red-600 dark:hover:bg-red-700",
      outline: "border border-gray-200 bg-white hover:bg-gray-100 text-gray-900 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800 dark:text-slate-50",
      secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-slate-800 dark:text-slate-50 dark:hover:bg-slate-700",
      ghost: "hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-slate-800 dark:hover:text-slate-50",
      link: "text-primary underline-offset-4 hover:underline dark:text-indigo-400",
    }
    
    const sizes: Record<string, string> = {
      default: "h-10 px-4 py-2",
      sm: "h-9 rounded-md px-3",
      lg: "h-11 rounded-md px-8",
      icon: "h-10 w-10",
    }

    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...(props as any)}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
