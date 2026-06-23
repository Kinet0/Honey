/**
 * Analytics page
 */

'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { Spinner } from '@/components/common/Loading';
import { TopItem } from '@/types';
import { apiClient } from '@/lib/api';

export default function AnalyticsPage() {
  const [topCountries, setTopCountries] = useState<TopItem[]>([]);
  const [topCommands, setTopCommands] = useState<TopItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [countriesRes, commandsRes] = await Promise.all([
          apiClient.getTopList('countries', 15) as Promise<{ data: TopItem[] }>,
          apiClient.getTopList('commands', 15) as Promise<{ data: TopItem[] }>,
        ]);

        setTopCountries(countriesRes.data || []);
        setTopCommands(commandsRes.data || []);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Analytics</h1>
        <p className="text-gray-400">Attack trends and statistics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Countries */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Top Attack Origins</h2>
          <div className="space-y-2">
            {topCountries.map((country) => (
              <Card key={country.rank} size="sm">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-semibold">{country.rank}. {country.name}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1 bg-panel rounded-full h-2 min-w-[100px]">
                      <div 
                        className="bg-primary rounded-full h-2" 
                        style={{ width: `${country.percentage * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-right font-mono text-sm">{country.value}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Top Commands */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Most Executed Commands</h2>
          <div className="space-y-2">
            {topCommands.map((cmd) => (
              <Card key={cmd.rank} size="sm">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-mono text-sm">{cmd.rank}. {cmd.name}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1 bg-panel rounded-full h-2 min-w-[100px]">
                      <div 
                        className="bg-warning rounded-full h-2" 
                        style={{ width: `${cmd.percentage * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-right font-mono text-sm">{cmd.value}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
