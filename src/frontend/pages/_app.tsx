/**
 * Next.js App Component - Global app wrapper
 */

import type { AppProps } from 'next/app';
import '@/styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

// Made with Bob
