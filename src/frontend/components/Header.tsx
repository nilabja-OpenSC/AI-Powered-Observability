/**
 * Header component - Navigation bar with links
 */

import React from 'react';
import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <nav className="container">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-xl font-bold text-primary-600 hover:text-primary-700">
              E-commerce Platform
            </Link>
            <div className="hidden md:flex space-x-4">
              <Link
                href="/"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Products
              </Link>
              <Link
                href="/products/add"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Add Product
              </Link>
              <Link
                href="/users/add"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Add User
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <a
              href="http://chat-ui:3001"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary px-4 py-2"
            >
              Chat with AI
            </a>
          </div>
        </div>
      </nav>
    </header>
  );
}

// Made with Bob
