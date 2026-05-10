# Missing Source Code Guide

## Overview
The frontend and chat-ui applications currently only have Dockerfiles but lack the actual source code. This guide documents what needs to be implemented.

## Current Status

### ✅ Complete Components
- Backend API (FastAPI) - Fully implemented in `src/backend/`
- AI Agents - All 4 agents fully implemented in `src/agents/`
- Helm Charts - All 14 charts with templates
- Dockerfiles - All 4 Dockerfiles created
- Documentation - Deployment and container image guides

### ❌ Missing Components
- Frontend (Next.js) - Only Dockerfile exists
- Chat-UI (React) - Only Dockerfile exists

## Frontend Application (Next.js)

### Required Files

**Configuration Files:**
1. `src/frontend/package.json` ✅ Created
2. `src/frontend/next.config.js` - Next.js configuration
3. `src/frontend/tailwind.config.js` - Tailwind CSS configuration
4. `src/frontend/tsconfig.json` - TypeScript configuration
5. `src/frontend/postcss.config.js` - PostCSS configuration
6. `src/frontend/.eslintrc.json` - ESLint configuration

**Pages (src/frontend/pages/):**
1. `_app.tsx` - App wrapper with global styles
2. `_document.tsx` - HTML document structure
3. `index.tsx` - Home page with product list
4. `products/[id].tsx` - Product detail page
5. `cart.tsx` - Shopping cart page
6. `checkout.tsx` - Checkout page
7. `api/health.ts` - Health check API route

**Components (src/frontend/components/):**
1. `Layout.tsx` - Page layout wrapper
2. `Header.tsx` - Navigation header
3. `Footer.tsx` - Page footer
4. `ProductCard.tsx` - Product display card
5. `ProductList.tsx` - Product grid/list
6. `CartItem.tsx` - Cart item component
7. `LoadingSpinner.tsx` - Loading indicator

**Library Files (src/frontend/lib/):**
1. `api.ts` - API client for backend
2. `types.ts` - TypeScript type definitions
3. `utils.ts` - Utility functions

**Styles:**
1. `src/frontend/styles/globals.css` - Global styles

### Minimal Implementation

Since full implementation would require 20+ files, here's a minimal viable approach:

**Option 1: Use Pre-built Image**
```yaml
# In charts/ecommerce-app/frontend/values.yaml
image:
  repository: nginx
  tag: alpine
  pullPolicy: IfNotPresent
```

Mount a simple static HTML page via ConfigMap.

**Option 2: Simple Next.js Starter**
```bash
cd src/frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
```

Then customize with API integration.

**Option 3: Reference Implementation**
Use the package.json already created and implement minimal pages:

```typescript
// src/frontend/pages/index.tsx
import { useEffect, useState } from 'react';

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(process.env.NEXT_PUBLIC_API_URL + '/api/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Products</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {products.map((product: any) => (
          <div key={product.id} className="border p-4 rounded">
            <h2 className="text-xl font-semibold">{product.name}</h2>
            <p className="text-gray-600">${product.price}</p>
            <button className="mt-2 bg-blue-500 text-white px-4 py-2 rounded">
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Chat-UI Application (React)

### Required Files

**Configuration Files:**
1. `src/chat-ui/package.json` - NPM dependencies
2. `src/chat-ui/tsconfig.json` - TypeScript configuration
3. `src/chat-ui/tailwind.config.js` - Tailwind CSS configuration
4. `src/chat-ui/vite.config.ts` - Vite build configuration (if using Vite)

**Source Files (src/chat-ui/src/):**
1. `main.tsx` - Application entry point
2. `App.tsx` - Main app component
3. `components/ChatInterface.tsx` - Chat UI component
4. `components/MessageBubble.tsx` - Message display
5. `components/InputBox.tsx` - Message input
6. `lib/websocket.ts` - WebSocket client
7. `lib/api.ts` - HTTP API client
8. `types/index.ts` - TypeScript types

**Public Files:**
1. `src/chat-ui/public/index.html` - HTML template
2. `src/chat-ui/public/favicon.ico` - Favicon

### Minimal Implementation

**Option 1: Simple Chat Interface**
```typescript
// src/chat-ui/src/App.tsx
import { useState, useEffect } from 'react';

export default function App() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const websocket = new WebSocket(
      process.env.REACT_APP_WS_URL || 'ws://localhost:8080/ws'
    );
    
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };
    
    setWs(websocket);
    
    return () => websocket.close();
  }, []);

  const sendMessage = () => {
    if (ws && input.trim()) {
      ws.send(JSON.stringify({ text: input, timestamp: new Date() }));
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <div key={i} className="mb-2 p-2 bg-gray-100 rounded">
            {msg.text}
          </div>
        ))}
      </div>
      <div className="p-4 border-t">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className="w-full p-2 border rounded"
          placeholder="Ask about observability metrics..."
        />
      </div>
    </div>
  );
}
```

## Recommended Approach

Given the scope of work, I recommend:

### For Hackathon/Demo:
1. **Use the backend API** (already complete)
2. **Deploy observability stack** (already complete)
3. **Deploy AI agents** (already complete)
4. **For frontend**: Use a simple static page or API testing tool (Postman, Swagger UI)
5. **For chat-ui**: Use Slack integration directly (already implemented in agents)

### For Production:
1. Generate full Next.js frontend using `create-next-app`
2. Generate full React chat-ui using `create-react-app` or Vite
3. Implement all pages and components per the manifest
4. Add proper error handling, loading states, and UX polish

## Quick Start Commands

### Generate Frontend Skeleton:
```bash
cd src/frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install axios swr @headlessui/react @heroicons/react
```

### Generate Chat-UI Skeleton:
```bash
cd src/chat-ui
npm create vite@latest . -- --template react-ts
npm install
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## Environment Variables

### Frontend (.env.local):
```bash
NEXT_PUBLIC_API_URL=http://backend:8000
NEXT_PUBLIC_CHAT_WS_URL=ws://supervisor-agent:8080/ws
```

### Chat-UI (.env):
```bash
REACT_APP_API_URL=http://backend:8000
REACT_APP_WS_URL=ws://supervisor-agent:8080/ws
REACT_APP_SUPERVISOR_URL=http://supervisor-agent:8080
```

## Integration Points

### Frontend → Backend API:
- GET `/api/products` - List products
- GET `/api/products/{id}` - Get product details
- POST `/api/orders` - Create order
- GET `/api/orders/{id}` - Get order status

### Chat-UI → Supervisor Agent:
- WebSocket `/ws` - Real-time chat
- POST `/query` - Send observability query
- GET `/health` - Health check

### Both → Observability:
- Prometheus metrics exposed on `/metrics`
- Structured logging to stdout (collected by Promtail)
- Error tracking and alerting

## Testing Without Full Implementation

### Test Backend API:
```bash
# Port-forward backend
kubectl port-forward svc/backend 8000:8000 -n nilabja-haldar-dev

# Test endpoints
curl http://localhost:8000/api/products
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

### Test AI Agents:
```bash
# Port-forward supervisor agent
kubectl port-forward svc/supervisor-agent 8080:8080 -n nilabja-haldar-dev

# Send query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me CPU usage for backend pods"}'
```

### Use Swagger UI:
The backend API includes automatic Swagger documentation at `/docs`

## Summary

**What Exists:**
- ✅ Backend API (complete)
- ✅ AI Agents (complete)
- ✅ Helm Charts (complete)
- ✅ Dockerfiles (complete)
- ✅ Deployment guides (complete)

**What's Missing:**
- ❌ Frontend source code (20+ files)
- ❌ Chat-UI source code (10+ files)

**Recommendation:**
For the hackathon demo, focus on:
1. Backend API + Observability Stack (working)
2. AI Agents + Slack integration (working)
3. Use Swagger UI or Postman for frontend testing
4. Use Slack for chat interface (already integrated)

This allows you to demonstrate the core value proposition (AI-powered observability) without spending time on UI development.