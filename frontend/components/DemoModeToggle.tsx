'use client'

import { Camera, CameraOff } from 'lucide-react'
import { motion } from 'framer-motion'

interface DemoModeToggleProps {
  isDemoMode: boolean
  onToggle: (enabled: boolean) => void
}

export function DemoModeToggle({ isDemoMode, onToggle }: DemoModeToggleProps) {
  return (
    <div className="flex items-center space-x-3">
      <span className="text-sm font-medium text-gray-700">
        Demo Mode
      </span>
      <button
        onClick={() => onToggle(!isDemoMode)}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
          ${isDemoMode ? 'bg-primary-600' : 'bg-gray-200'}
        `}
      >
        <motion.span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
          `}
          animate={{
            x: isDemoMode ? 24 : 4
          }}
          transition={{
            type: 'spring',
            stiffness: 500,
            damping: 30
          }}
        />
      </button>
      <div className="flex items-center text-xs text-gray-500">
        {isDemoMode ? (
          <>
            <Camera className="w-3 h-3 mr-1" />
            On
          </>
        ) : (
          <>
            <CameraOff className="w-3 h-3 mr-1" />
            Off
          </>
        )}
      </div>
    </div>
  )
}


