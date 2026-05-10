/**
 * Home Page - Product listing with search
 */

import React from 'react';
import Head from 'next/head';
import Layout from '@/components/Layout';
import ProductList from '@/components/ProductList';

export default function Home() {
  return (
    <>
      <Head>
        <title>E-commerce Platform - AI-Powered Observability</title>
        <meta name="description" content="Browse our product catalog" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Page Header */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Product Catalog
            </h1>
            <p className="text-gray-600">
              Browse our collection of products. Use the search bar to find specific items.
            </p>
          </div>

          {/* Product List */}
          <ProductList />
        </div>
      </Layout>
    </>
  );
}

// Made with Bob
