/**
 * Intelligence page
 */

'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { Spinner } from '@/components/common/Loading';
import { apiClient } from '@/lib/api';

interface CommandData {
  command: string;
  count: number;
  classification?: string;
  success_rate: number;
}

interface CredentialData {
  username?: string;
  password?: string;
  count: number;
  success_count: number;
  success_rate: number;
}

export default function IntelligencePage() {
  const [commands, setCommands] = useState<CommandData[]>([]);
  const [credentials, setCredentials] = useState<CredentialData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cmdRes, credRes] = await Promise.all([
          apiClient.getCommandFrequency(20) as Promise<{ data: CommandData[] }>,
          apiClient.getCredentialsAnalysis('usernames', 20) as Promise<{ top_usernames: CredentialData[] }>,
        ]);

        setCommands(cmdRes.data || []);
        setCredentials(credRes.top_usernames || []);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch intelligence:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Threat Intelligence</h1>
        <p className="text-gray-400">Attack patterns and attacker behavior analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Commands */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Top Commands</h2>
          <div className="space-y-2">
            {commands.map((cmd, idx) => (
              <Card key={idx} size="sm" className="flex items-center justify-between">
                <div>
                  <p className="font-mono text-sm">{cmd.command}</p>
                  <p className="text-xs text-gray-400 mt-1">{cmd.classification || 'Unknown'}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold">{cmd.count}</p>
                  <p className="text-xs text-gray-400">{(cmd.success_rate * 100).toFixed(0)}% success</p>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Top Usernames */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Top Usernames</h2>
          <div className="space-y-2">
            {credentials.map((cred, idx) => (
              <Card key={idx} size="sm" className="flex items-center justify-between">
                <div>
                  <p className="font-mono text-sm">{cred.username}</p>
                  <p className="text-xs text-gray-400 mt-1">{cred.success_count} successful</p>
                </div>
                <div className="text-right">
                  <p className="font-bold">{cred.count}</p>
                  <p className="text-xs text-gray-400">{(cred.success_rate * 100).toFixed(0)}% success</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
