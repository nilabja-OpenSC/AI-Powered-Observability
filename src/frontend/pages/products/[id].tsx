/**
 * Product Detail Page - Display individual product details
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '@/components/Layout';
import { Product } from '@/lib/types';
import { api } from '@/lib/api';
import { formatCurrency, getErrorMessage } from '@/lib/utils';

export default function ProductDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    if (id) {
      fetchProduct(Number(id));
    }
  }, [id]);

  const fetchProduct = async (productId: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProduct(productId);
      setProduct(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    // TODO: Implement cart functionality
    alert(`Added ${quantity} ${product?.name} to cart!`);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading product...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !product) {
    return (
      <Layout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <svg
            className="w-12 h-12 text-red-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Product</h3>
          <p className="text-red-700 mb-4">{error || 'Product not found'}</p>
          <Link href="/" className="btn btn-primary">
            Back to Products
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Head>
        <title>{product.name} - E-commerce Platform</title>
        <meta name="description" content={product.description} />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Breadcrumb */}
          <nav className="flex items-center space-x-2 text-sm text-gray-600">
            <Link href="/" className="hover:text-primary-600">
              Products
            </Link>
            <span>/</span>
            <span className="text-gray-900">{product.name}</span>
          </nav>

          {/* Product Details */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-6">
              {/* Product Image */}
              <div className="aspect-w-1 aspect-h-1 bg-gray-200 rounded-lg overflow-hidden">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-primary-200">
                    <svg
                      className="w-32 h-32 text-primary-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                      />
                    </svg>
                  </div>
                )}
              </div>

              {/* Product Info */}
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    {product.name}
                  </h1>
                  <div className="flex items-center space-x-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                      {product.category}
                    </span>
                    <span className={`text-sm font-medium ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                    </span>
                  </div>
                </div>

                <div className="border-t border-b py-4">
                  <p className="text-4xl font-bold text-primary-600">
                    {formatCurrency(product.price)}
                  </p>
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">Description</h2>
                  <p className="text-gray-600 leading-relaxed">
                    {product.description}
                  </p>
                </div>

                {/* Quantity Selector */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity
                  </label>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      className="btn btn-outline px-3 py-2"
                      disabled={quantity <= 1}
                    >
                      -
                    </button>
                    <input
                      type="number"
                      min="1"
                      max={product.stock}
                      value={quantity}
                      onChange={(e) => setQuantity(Math.max(1, Math.min(product.stock, Number(e.target.value))))}
                      className="input w-20 text-center"
                    />
                    <button
                      onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                      className="btn btn-outline px-3 py-2"
                      disabled={quantity >= product.stock}
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* Add to Cart Button */}
                <div className="space-y-3">
                  <button
                    onClick={handleAddToCart}
                    disabled={product.stock === 0}
                    className="btn btn-primary w-full py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
                  </button>
                  <Link href="/" className="btn btn-outline w-full py-3 text-center">
                    Continue Shopping
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}

// Made with Bob