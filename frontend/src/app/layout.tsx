/**
 * Layout component
 */

'use client';

import React from 'react';
import Link from 'next/link';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Honeypot Dashboard - Live Attack Monitoring</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-background text-gray-100">
        <nav className="bg-panel border-b border-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <span className="text-black font-bold text-lg">🔍</span>
                </div>
                <span className="text-xl font-bold text-primary">Honeypot Monitor</span>
              </Link>
              
              <div className="hidden md:flex space-x-8">
                <Link href="/" className="hover:text-primary transition-colors">Dashboard</Link>
                <Link href="/attackers" className="hover:text-primary transition-colors">Attackers</Link>
                <Link href="/intelligence" className="hover:text-primary transition-colors">Intelligence</Link>
                <Link href="/analytics" className="hover:text-primary transition-colors">Analytics</Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="min-h-screen bg-background">
          {children}
        </main>

        <footer className="bg-panel border-t border-border py-6 mt-12">
          <div className="max-w-7xl mx-auto px-4 text-center text-gray-400">
            <p>© 2024 Honeypot Dashboard - Real-time Attack Monitoring & Analysis</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
