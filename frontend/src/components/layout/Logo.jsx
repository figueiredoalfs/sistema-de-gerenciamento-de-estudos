import React from 'react';
const Logo = ({ className = "h-12", showText = true }) => {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <svg
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="h-full w-auto drop-shadow-[0_0_8px_rgba(6,182,212,0.4)]"
      >
        <defs>
          <linearGradient id="skolai-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stopColor="#06B6D4" />
            <stop offset="50%"  stopColor="#6366F1" />
            <stop offset="100%" stopColor="#A855F7" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="1.5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <g stroke="url(#skolai-grad)" strokeWidth="2.5" strokeOpacity="0.4">
          <path d="M30 25 L70 25 L30 50 L70 50 L30 75 L70 75" strokeLinecap="round" />
          <path d="M30 25 L50 40 L30 50" />
          <path d="M70 25 L50 40 L70 50" />
          <path d="M30 50 L50 65 L30 75" />
          <path d="M70 50 L50 65 L70 75" />
        </g>
        <circle cx="30" cy="25" r="5" fill="#06B6D4" filter="url(#glow)" />
        <circle cx="70" cy="25" r="5" fill="#06B6D4" />
        <circle cx="50" cy="40" r="5" fill="#6366F1" filter="url(#glow)" />
        <circle cx="30" cy="50" r="5" fill="#6366F1" />
        <circle cx="70" cy="50" r="5" fill="#6366F1" />
        <circle cx="50" cy="65" r="5" fill="#A855F7" filter="url(#glow)" />
        <circle cx="30" cy="75" r="5" fill="#A855F7" />
        <circle cx="70" cy="75" r="5" fill="#A855F7" filter="url(#glow)" />
      </svg>
      {showText && (
        <span className="text-2xl font-black tracking-tighter flex">
          <span className="text-brand-text">Skol</span>
          <span className="bg-clip-text text-transparent bg-gradient-to-br from-cyan-400 via-indigo-500 to-purple-600">
            AI
          </span>
        </span>
      )}
    </div>
  );
};
export default Logo;
