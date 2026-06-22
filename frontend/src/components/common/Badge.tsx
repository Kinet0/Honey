/**
 * Badge component
 */

import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'info' | 'low' | 'medium' | 'high' | 'critical' | 'active' | 'complete' | 'failed';
  className?: string;
}

const variantStyles = {
  info: 'severity-info',
  low: 'severity-low',
  medium: 'severity-medium',
  high: 'severity-high',
  critical: 'severity-critical',
  active: 'bg-green-900/30 text-green-300 border border-green-700/50',
  complete: 'bg-gray-900/30 text-gray-300 border border-gray-700/50',
  failed: 'bg-red-900/30 text-red-300 border border-red-700/50',
};

export function Badge({ children, variant = 'info', className = '' }: BadgeProps) {
  const variantClass = variantStyles[variant];
  
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border ${variantClass} ${className}`}>
      {children}
    </span>
  );
}
