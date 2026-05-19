/**
 * Shopping Cart Page - Display cart items and checkout
 */

import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '@/components/Layout';
import { formatCurrency } from '@/lib/utils';

interface CartItem {
  id: number;
  productId: number;
  name: string;
  price: number;
  quantity: number;
  image_url?: string;
}

export default function Cart() {
  // Mock cart data - in a real app, this would come from state management or API
  const [cartItems, setCartItems] = useState<CartItem[]>([
    {
      id: 1,
      productId: 1,
      name: 'Sample Product 1',
      price: 29.99,
      quantity: 2,
      image_url: undefined,
    },
    {
      id: 2,
      productId: 2,
      name: 'Sample Product 2',
      price: 49.99,
      quantity: 1,
      image_url: undefined,
    },
  ]);

  const updateQuantity = (id: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    setCartItems(items =>
      items.map(item =>
        item.id === id ? { ...item, quantity: newQuantity } : item
      )
    );
  };

  const removeItem = (id: number) => {
    setCartItems(items => items.filter(item => item.id !== id));
  };

  const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const tax = subtotal * 0.1; // 10% tax
  const shipping = subtotal > 50 ? 0 : 5.99;
  const total = subtotal + tax + shipping;

  return (
    <>
      <Head>
        <title>Shopping Cart - E-commerce Platform</title>
        <meta name="description" content="Review your shopping cart" />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Page Header */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
            <p className="text-gray-600 mt-2">
              {cartItems.length} {cartItems.length === 1 ? 'item' : 'items'} in your cart
            </p>
          </div>

          {cartItems.length === 0 ? (
            /* Empty Cart */
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
              <svg
                className="w-24 h-24 text-gray-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                />
              </svg>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Your cart is empty</h2>
              <p className="text-gray-600 mb-6">Add some products to get started!</p>
              <Link href="/" className="btn btn-primary">
                Continue Shopping
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Cart Items */}
              <div className="lg:col-span-2 space-y-4">
                {cartItems.map((item) => (
                  <div key={item.id} className="bg-white rounded-lg shadow-sm p-6">
                    <div className="flex items-center space-x-4">
                      {/* Product Image */}
                      <div className="flex-shrink-0 w-24 h-24 bg-gray-200 rounded-lg overflow-hidden">
                        {item.image_url ? (
                          <img
                            src={item.image_url}
                            alt={item.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-primary-200">
                            <svg
                              className="w-12 h-12 text-primary-400"
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
                      <div className="flex-1 min-w-0">
                        <Link
                          href={`/products/${item.productId}`}
                          className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                        >
                          {item.name}
                        </Link>
                        <p className="text-primary-600 font-semibold mt-1">
                          {formatCurrency(item.price)}
                        </p>
                      </div>

                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="btn btn-outline px-3 py-1"
                        >
                          -
                        </button>
                        <span className="text-lg font-semibold w-8 text-center">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="btn btn-outline px-3 py-1"
                        >
                          +
                        </button>
                      </div>

                      {/* Item Total */}
                      <div className="text-right">
                        <p className="text-lg font-bold text-gray-900">
                          {formatCurrency(item.price * item.quantity)}
                        </p>
                      </div>

                      {/* Remove Button */}
                      <button
                        onClick={() => removeItem(item.id)}
                        className="text-red-600 hover:text-red-700"
                        title="Remove item"
                      >
                        <svg
                          className="w-6 h-6"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Order Summary */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow-sm p-6 sticky top-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>
                  
                  <div className="space-y-3 mb-4">
                    <div className="flex justify-between text-gray-600">
                      <span>Subtotal</span>
                      <span>{formatCurrency(subtotal)}</span>
                    </div>
                    <div className="flex justify-between text-gray-600">
                      <span>Tax (10%)</span>
                      <span>{formatCurrency(tax)}</span>
                    </div>
                    <div className="flex justify-between text-gray-600">
                      <span>Shipping</span>
                      <span>{shipping === 0 ? 'FREE' : formatCurrency(shipping)}</span>
                    </div>
                    {subtotal < 50 && (
                      <p className="text-sm text-gray-500">
                        Add {formatCurrency(50 - subtotal)} more for free shipping!
                      </p>
                    )}
                  </div>

                  <div className="border-t pt-4 mb-6">
                    <div className="flex justify-between text-lg font-bold text-gray-900">
                      <span>Total</span>
                      <span>{formatCurrency(total)}</span>
                    </div>
                  </div>

                  <button className="btn btn-primary w-full py-3 text-lg mb-3">
                    Proceed to Checkout
                  </button>
                  
                  <Link href="/" className="btn btn-outline w-full py-3 text-center">
                    Continue Shopping
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}

// Made with Bob