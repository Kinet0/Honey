/**
 * Card component
 */

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function Card({ children, className = '', size = 'md' }: CardProps) {
  const sizeClass = size === 'sm' ? 'p-4' : size === 'lg' ? 'p-8' : 'p-6';
  
  return (
    <div className={`bg-panel border border-border rounded-lg ${sizeClass} ${className}`}>
      {children}
    </div>
  );
}
