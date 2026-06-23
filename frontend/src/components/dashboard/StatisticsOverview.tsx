/**
 * Statistics Overview component
 */

'use client';

import { useEffect, useState } from 'react';
import { AttackStatistics } from '@/types';
import { StatCard } from '../common/StatCard';
import { apiClient } from '@/lib/api';

export function StatisticsOverview() {
  const [stats, setStats] = useState<AttackStatistics | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = (await apiClient.getAttackStatistics()) as AttackStatistics;
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch statistics:', error);
      }
    };

    fetchStats();

    // Refresh every 10 seconds
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Attacks Today"
        value={stats.attacks_today}
        icon="⚡"
      />
      <StatCard
        label="Unique Attackers"
        value={stats.unique_attackers}
        icon="👤"
      />
      <StatCard
        label="Unique Countries"
        value={stats.unique_countries}
        icon="🌍"
      />
      <StatCard
        label="Commands Executed"
        value={stats.total_commands}
        icon="⌨️"
      />
    </div>
  );
}
