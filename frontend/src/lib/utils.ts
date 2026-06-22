/**
 * Utility functions for severity, status, and data formatting
 */

import { Severity, SessionStatus, ThreatLevel, CommandClassification } from '@/types';

export function getSeverityColor(severity: Severity): string {
  switch (severity) {
    case Severity.INFO:
      return 'text-blue-400';
    case Severity.LOW:
      return 'text-yellow-400';
    case Severity.MEDIUM:
      return 'text-orange-400';
    case Severity.HIGH:
      return 'text-red-400';
    case Severity.CRITICAL:
      return 'text-red-600';
    default:
      return 'text-gray-400';
  }
}

export function getSeverityBg(severity: Severity): string {
  switch (severity) {
    case Severity.INFO:
      return 'bg-blue-900/30 border-blue-700/50';
    case Severity.LOW:
      return 'bg-yellow-900/30 border-yellow-700/50';
    case Severity.MEDIUM:
      return 'bg-orange-900/30 border-orange-700/50';
    case Severity.HIGH:
      return 'bg-red-900/30 border-red-700/50';
    case Severity.CRITICAL:
      return 'bg-red-900/50 border-red-600';
    default:
      return 'bg-gray-900/30 border-gray-700/50';
  }
}

export function getStatusColor(status: SessionStatus | string): string {
  switch (status) {
    case SessionStatus.ACTIVE:
      return 'text-green-400';
    case SessionStatus.COMPLETE:
      return 'text-gray-400';
    case SessionStatus.FAILED:
      return 'text-red-400';
    default:
      return 'text-gray-400';
  }
}

export function getStatusBg(status: SessionStatus | string): string {
  switch (status) {
    case SessionStatus.ACTIVE:
      return 'bg-green-900/30 border-green-700/50';
    case SessionStatus.COMPLETE:
      return 'bg-gray-900/30 border-gray-700/50';
    case SessionStatus.FAILED:
      return 'bg-red-900/30 border-red-700/50';
    default:
      return 'bg-gray-900/30 border-gray-700/50';
  }
}

export function getThreatLevelColor(level: ThreatLevel | string): string {
  switch (level) {
    case ThreatLevel.LOW:
      return 'text-yellow-400';
    case ThreatLevel.MEDIUM:
      return 'text-orange-400';
    case ThreatLevel.HIGH:
      return 'text-red-400';
    case ThreatLevel.CRITICAL:
      return 'text-red-600';
    default:
      return 'text-gray-400';
  }
}

export function formatDate(dateString: string): string {
  try {
    return new Date(dateString).toLocaleString();
  } catch {
    return dateString;
  }
}

export function formatTime(dateString: string): string {
  try {
    return new Date(dateString).toLocaleTimeString();
  } catch {
    return dateString;
  }
}

export function formatDuration(seconds: number | undefined): string {
  if (!seconds) return '0s';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  const parts = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);
  
  return parts.join(' ');
}

export function formatBytes(bytes: number | undefined): string {
  if (!bytes) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

export function getCommandClassificationColor(classification: CommandClassification | string): string {
  switch (classification) {
    case CommandClassification.RECONNAISSANCE:
      return 'text-blue-400';
    case CommandClassification.FILE_DOWNLOAD:
      return 'text-yellow-400';
    case CommandClassification.EXECUTION:
      return 'text-red-400';
    case CommandClassification.PERSISTENCE:
      return 'text-red-600';
    case CommandClassification.NETWORKING:
      return 'text-purple-400';
    case CommandClassification.PRIVILEGE_ESCALATION:
      return 'text-red-700';
    default:
      return 'text-gray-400';
  }
}

export function truncateString(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.substring(0, length) + '...';
}
