/**
 * Attackers page
 */

'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Spinner } from '@/components/common/Loading';
import { Attacker } from '@/types';
import { apiClient } from '@/lib/api';
import { formatDate } from '@/lib/utils';

export default function AttackersPage() {
  const [attackers, setAttackers] = useState<Attacker[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttackers = async () => {
      try {
        const response = (await apiClient.listAttackers(undefined, undefined, 100)) as { data: Attacker[] };
        setAttackers(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch attackers:', error);
        setLoading(false);
      }
    };

    fetchAttackers();
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Attackers</h1>
        <p className="text-gray-400">Top threat actors and their profiles</p>
      </div>

      <div className="grid gap-6">
        {attackers.map((attacker) => (
          <Card key={attacker.ip_address} className="hover:border-primary/50 transition-colors cursor-pointer">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <p className="text-xs text-gray-400 uppercase">IP Address</p>
                <p className="font-mono text-white mt-1">{attacker.ip_address}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase">Country</p>
                <p className="text-white mt-1">{attacker.country_code}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase">Sessions</p>
                <p className="text-white mt-1">{attacker.total_sessions}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase">Commands</p>
                <p className="text-white mt-1">{attacker.total_commands}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase">Threat Level</p>
                <Badge variant={attacker.threat_level.toLowerCase() as any} className="mt-1">
                  {attacker.threat_level.toUpperCase()}
                </Badge>
              </div>
            </div>
            <hr className="border-border my-4" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">First Seen:</span>
                <p className="text-gray-300">{formatDate(attacker.first_seen)}</p>
              </div>
              <div>
                <span className="text-gray-400">Last Seen:</span>
                <p className="text-gray-300">{formatDate(attacker.last_seen)}</p>
              </div>
              <div>
                <span className="text-gray-400">ASN:</span>
                <p className="text-gray-300">{attacker.asn || 'N/A'}</p>
              </div>
              <div>
                <span className="text-gray-400">Downloads:</span>
                <p className="text-gray-300">{attacker.total_downloads}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
