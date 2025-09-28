'use client'

import { X, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'

interface ErrorMessageProps {
  message: string
  onDismiss?: () => void
  type?: 'error' | 'warning' | 'info'
}

export function ErrorMessage({ message, onDismiss, type = 'error' }: ErrorMessageProps) {
  const typeStyles = {
    error: 'bg-error-50 border-error-200 text-error-800',
    warning: 'bg-warning-50 border-warning-200 text-warning-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  }

  const iconColors = {
    error: 'text-error-600',
    warning: 'text-warning-600',
    info: 'text-blue-600'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`rounded-lg border p-4 ${typeStyles[type]}`}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <AlertCircle className={`w-5 h-5 ${iconColors[type]}`} />
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm font-medium">{message}</p>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                onClick={onDismiss}
                className={`inline-flex rounded-md p-1.5 hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                  type === 'error' 
                    ? 'text-error-500 hover:bg-error-100 focus:ring-error-600' 
                    : type === 'warning'
                    ? 'text-warning-500 hover:bg-warning-100 focus:ring-warning-600'
                    : 'text-blue-500 hover:bg-blue-100 focus:ring-blue-600'
                }`}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}


