/**
 * Layout component - Main page wrapper with header and navigation
 */

import React from 'react';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container py-8">
        {children}
      </main>
      <footer className="bg-white border-t mt-auto">
        <div className="container py-6">
          <p className="text-center text-sm text-gray-600">
            © 2026 E-commerce Platform - AI-Powered Observability
          </p>
        </div>
      </footer>
    </div>
  );
}

// Made with Bob
