/**
 * Live Attack Feed component
 */

'use client';

import { useEffect, useState } from 'react';
import { Attack } from '@/types';
import { Badge } from '../common/Badge';
import { Card } from '../common/Card';
import { Spinner } from '../common/Loading';
import { formatDate } from '@/lib/utils';
import { apiClient } from '@/lib/api';
import { getWebSocketClient } from '@/lib/websocket';

export function LiveAttackFeed() {
  const [attacks, setAttacks] = useState<Attack[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch initial attacks
    const fetchAttacks = async () => {
      try {
        const response = (await apiClient.getAttacksFeed(20)) as { data: Attack[] };
        setAttacks(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch attacks:', error);
        setLoading(false);
      }
    };

    fetchAttacks();

    // Connect to WebSocket for real-time updates
    const ws = getWebSocketClient();
    ws.connect().then(() => {
      ws.subscribe();
      
      ws.on('attack:new', (event: any) => {
        setAttacks(prev => [event.data, ...prev].slice(0, 50));
      });
    });

    return () => {
      ws.unsubscribe();
    };
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="space-y-3">
      {attacks.map((attack) => (
        <Card key={attack.id} size="sm" className="hover:border-primary/50 transition-colors cursor-pointer">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm text-gray-400">{attack.attacker_ip}</span>
                <Badge variant={attack.severity.toLowerCase() as any}>
                  {attack.severity}
                </Badge>
              </div>
              <p className="text-sm text-gray-400 mt-1">
                {formatDate(attack.timestamp)}
              </p>
              <p className="text-sm mt-2">{attack.event_type.toUpperCase()}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">{attack.country_code}</p>
              {attack.asn && <p className="text-xs text-gray-500">ASN {attack.asn}</p>}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
