/**
 * ProductList component - Display grid of products with search
 */

import React, { useState, useEffect } from 'react';
import { Product } from '@/lib/types';
import { api } from '@/lib/api';
import { debounce, getErrorMessage } from '@/lib/utils';
import ProductCard from './ProductCard';

// Sample catalog data for fallback when backend is unavailable
const SAMPLE_PRODUCTS: Product[] = [
  {
    id: 1,
    name: "Wireless Bluetooth Headphones",
    description: "Premium noise-cancelling headphones with 30-hour battery life",
    price: 129.99,
    stock: 50,
    category: "Electronics",
    image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    name: "Smart Watch Series 5",
    description: "Fitness tracking, heart rate monitor, GPS enabled",
    price: 299.99,
    stock: 30,
    category: "Electronics",
    image_url: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 3,
    name: "Laptop Backpack",
    description: "Water-resistant backpack with USB charging port",
    price: 49.99,
    stock: 100,
    category: "Accessories",
    image_url: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 4,
    name: "Mechanical Keyboard",
    description: "RGB backlit gaming keyboard with blue switches",
    price: 89.99,
    stock: 45,
    category: "Electronics",
    image_url: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 5,
    name: "Wireless Mouse",
    description: "Ergonomic design with adjustable DPI settings",
    price: 34.99,
    stock: 75,
    category: "Electronics",
    image_url: "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 6,
    name: "USB-C Hub",
    description: "7-in-1 adapter with HDMI, USB 3.0, and SD card reader",
    price: 39.99,
    stock: 60,
    category: "Accessories",
    image_url: "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=400",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export default function ProductList() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [usingSampleData, setUsingSampleData] = useState(false);

  // Fetch products
  const fetchProducts = async (query?: string) => {
    try {
      setLoading(true);
      setError(null);
      setUsingSampleData(false);
      
      const data = query
        ? await api.searchProducts(query)
        : await api.getProducts();
      
      setProducts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch products, using sample data:', err);
      setError(getErrorMessage(err));
      // Use sample data as fallback
      setUsingSampleData(true);
      const filteredSamples = query
        ? SAMPLE_PRODUCTS.filter(p =>
            p.name.toLowerCase().includes(query.toLowerCase()) ||
            p.description.toLowerCase().includes(query.toLowerCase()) ||
            p.category.toLowerCase().includes(query.toLowerCase())
          )
        : SAMPLE_PRODUCTS;
      setProducts(filteredSamples);
    } finally {
      setLoading(false);
    }
  };

  // Debounced search
  const debouncedSearch = debounce((query: string) => {
    fetchProducts(query || undefined);
  }, 500);

  // Initial load
  useEffect(() => {
    fetchProducts();
  }, []);

  // Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    debouncedSearch(query);
  };

  if (loading && products.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sample Data Banner */}
      {usingSampleData && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg
              className="w-6 h-6 text-yellow-600 mr-3 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-yellow-900 mb-1">
                Using Sample Catalog
              </h3>
              <p className="text-sm text-yellow-700 mb-2">
                Backend service is unavailable. Displaying sample products for demonstration.
              </p>
              <button
                onClick={() => fetchProducts()}
                className="text-sm text-yellow-800 hover:text-yellow-900 font-medium underline"
              >
                Try connecting again
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search products..."
            className="input w-full pl-10"
          />
          <svg
            className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Products Grid */}
      {products.length === 0 ? (
        <div className="text-center py-12">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Products Found</h3>
          <p className="text-gray-600">
            {searchQuery ? 'Try a different search term' : 'No products available yet'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}

      {/* Loading Overlay */}
      {loading && products.length > 0 && (
        <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 flex items-center space-x-3">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
          <span className="text-sm text-gray-700">Updating...</span>
        </div>
      )}
    </div>
  );
}

// Made with Bob
