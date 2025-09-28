'use client'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Logo({ size = 'md', className = '' }: LogoProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  }

  return (
    <div className={`${sizeClasses[size]} ${className}`}>
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Dark green circular background */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="#047857"
          stroke="#065f46"
          strokeWidth="2"
        />
        
        {/* Refrigerator outline */}
        <rect
          x="25"
          y="20"
          width="50"
          height="60"
          rx="4"
          ry="4"
          fill="none"
          stroke="#000000"
          strokeWidth="2"
        />
        
        {/* Refrigerator doors */}
        <line
          x1="50"
          y1="20"
          x2="50"
          y2="80"
          stroke="#000000"
          strokeWidth="2"
        />
        
        {/* Door handles */}
        <line
          x1="35"
          y1="30"
          x2="35"
          y2="35"
          stroke="#000000"
          strokeWidth="2"
        />
        <line
          x1="65"
          y1="30"
          x2="65"
          y2="35"
          stroke="#000000"
          strokeWidth="2"
        />
        
        {/* Refrigerator feet */}
        <rect
          x="30"
          y="75"
          width="6"
          height="4"
          rx="1"
          fill="#000000"
        />
        <rect
          x="64"
          y="75"
          width="6"
          height="4"
          rx="1"
          fill="#000000"
        />
        
        {/* Leaf on bottom door */}
        <path
          d="M 60 55 Q 65 50 70 55 Q 65 60 60 55"
          fill="none"
          stroke="#000000"
          strokeWidth="2"
        />
        <path
          d="M 65 55 L 65 50"
          stroke="#000000"
          strokeWidth="2"
        />
      </svg>
    </div>
  )
}
