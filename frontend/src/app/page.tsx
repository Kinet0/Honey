/**
 * Home page / main dashboard
 */

'use client';

import { Card } from '@/components/common/Card';
import { StatisticsOverview } from '@/components/dashboard/StatisticsOverview';
import { LiveAttackFeed } from '@/components/dashboard/LiveAttackFeed';

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Honeypot Dashboard</h1>
        <p className="text-gray-400">Real-time attack monitoring and analysis</p>
      </div>

      {/* Statistics */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-white mb-6">Attack Statistics</h2>
        <StatisticsOverview />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Live Feed */}
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold text-white mb-6">Live Attack Feed</h2>
          <LiveAttackFeed />
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          {/* Quick Stats */}
          <Card>
            <h3 className="text-lg font-bold text-white mb-4">Quick Info</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-400">System Status</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-400">Online</span>
                </div>
              </div>
              <hr className="border-border" />
              <div>
                <p className="text-sm text-gray-400">Honeypot Version</p>
                <p className="text-white mt-1">Cowrie 2.x</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Uptime</p>
                <p className="text-white mt-1">24h 12m</p>
              </div>
            </div>
          </Card>

          {/* Info Card */}
          <Card>
            <h3 className="text-lg font-bold text-white mb-4">About</h3>
            <p className="text-sm text-gray-400">
              This dashboard monitors real attack activity captured by a Cowrie SSH/Telnet honeypot.
              All data is real and sourced from actual attack attempts.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
