/**
 * Statistics card component
 */

import React from 'react';
import { Card } from './Card';

interface StatCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  trend?: number; // percentage change
  icon?: React.ReactNode;
}

export function StatCard({ label, value, subtitle, trend, icon }: StatCardProps) {
  return (
    <Card size="sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{label}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
          {subtitle && <p className="text-gray-500 text-sm mt-1">{subtitle}</p>}
        </div>
        {icon && <div className="text-2xl">{icon}</div>}
      </div>
      {trend !== undefined && (
        <div className="mt-3 pt-3 border-t border-border">
          <span className={trend >= 0 ? 'text-red-400' : 'text-green-400'}>
            {trend > 0 ? '+' : ''}{trend}% vs last period
          </span>
        </div>
      )}
    </Card>
  );
}
