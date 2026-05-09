# API Reference

Complete API documentation for all services in the AI-Powered Observability Platform.

## Table of Contents

- [Supervisor Agent API](#supervisor-agent-api)
- [Observability Agent API](#observability-agent-api)
- [Pod Recovery Agent API](#pod-recovery-agent-api)
- [Backup/Restore Agent API](#backuprestore-agent-api)
- [Backend API](#backend-api)
- [WebSocket API](#websocket-api)

---

## Supervisor Agent API

**Base URL:** `http://supervisor-agent:8080`

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-09T07:00:00Z"
}
```

### Query Endpoint

```http
POST /query
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Show me CPU usage for backend pods",
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "intent": "observability_query",
  "routed_to": "observability-agent",
  "response": {
    "query_type": "prometheus",
    "promql": "rate(container_cpu_usage_seconds_total{namespace=\"nilabja-haldar-dev\",pod=~\"backend-.*\"}[5m])",
    "results": [
      {
        "metric": {"pod": "backend-abc123"},
        "value": [1715241600, "0.25"]
      }
    ]
  },
  "timestamp": "2026-05-09T07:00:00Z"
}
```

### Classify Intent

```http
POST /classify
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Restart the backend pod"
}
```

**Response:**
```json
{
  "intent": "pod_recovery",
  "confidence": 0.95,
  "reasoning": "Query contains pod recovery action keyword 'restart'"
}
```

---

## Observability Agent API

**Base URL:** `http://observability-agent:8081`

### Health Check

```http
GET /health
```

### Generate Query

```http
POST /generate-query
Content-Type: application/json
```

**Request Body:**
```json
{
  "natural_language": "Show me error rate for backend service in the last hour",
  "query_type": "prometheus"
}
```

**Response:**
```json
{
  "query_type": "prometheus",
  "promql": "rate(http_requests_total{namespace=\"nilabja-haldar-dev\",app=\"backend\",status=~\"5..\"}[1h])",
  "explanation": "This query calculates the rate of HTTP 5xx errors for the backend service over the last hour"
}
```

### Detect Issues

```http
POST /detect-issues
Content-Type: application/json
```

**Request Body:**
```json
{
  "time_range": "5m",
  "severity_threshold": "medium"
}
```

**Response:**
```json
{
  "issues": [
    {
      "id": "issue-001",
      "type": "high_cpu_usage",
      "severity": "high",
      "summary": "Backend pod CPU usage above 80%",
      "affected_resources": ["backend-abc123"],
      "metrics": {
        "current_value": 0.85,
        "threshold": 0.80
      },
      "detected_at": "2026-05-09T07:00:00Z"
    }
  ],
  "total_issues": 1
}
```

### Create Dashboard

```http
POST /create-dashboard
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Backend Service Dashboard",
  "app": "backend",
  "panels": ["cpu", "memory", "requests", "errors"]
}
```

**Response:**
```json
{
  "dashboard_id": "dashboard-123",
  "url": "http://grafana:3000/d/dashboard-123",
  "panels_created": 4
}
```

### Send Notification

```http
POST /notify
Content-Type: application/json
```

**Request Body:**
```json
{
  "issue": {
    "id": "issue-001",
    "type": "high_cpu_usage",
    "severity": "high",
    "summary": "Backend pod CPU usage above 80%",
    "affected_resources": ["backend-abc123"]
  }
}
```

**Response:**
```json
{
  "notification_sent": true,
  "channel": "#observability-alerts",
  "message_ts": "1715241600.123456"
}
```

---

## Pod Recovery Agent API

**Base URL:** `http://pod-recovery-agent:8082`

### Health Check

```http
GET /health
```

### Monitor Pod Health

```http
POST /monitor
Content-Type: application/json
```

**Request Body:**
```json
{
  "pod_name": "backend-abc123",
  "namespace": "nilabja-haldar-dev"
}
```

**Response:**
```json
{
  "pod_name": "backend-abc123",
  "namespace": "nilabja-haldar-dev",
  "status": "Running",
  "health": "healthy",
  "restarts": 0,
  "age": "2h",
  "conditions": [
    {"type": "Ready", "status": "True"},
    {"type": "ContainersReady", "status": "True"}
  ]
}
```

### Diagnose Pod

```http
POST /diagnose
Content-Type: application/json
```

**Request Body:**
```json
{
  "pod_name": "backend-abc123",
  "namespace": "nilabja-haldar-dev",
  "include_logs": true
}
```

**Response:**
```json
{
  "pod_name": "backend-abc123",
  "diagnosis": {
    "root_cause": "OOMKilled - Container exceeded memory limit",
    "confidence": 0.92,
    "evidence": [
      "Last termination reason: OOMKilled",
      "Memory usage: 512Mi/512Mi (100%)",
      "Recent log errors: OutOfMemoryError"
    ],
    "recommended_actions": [
      "Increase memory limit to 1Gi",
      "Investigate memory leaks in application",
      "Add memory profiling"
    ]
  },
  "timestamp": "2026-05-09T07:00:00Z"
}
```

### Execute Recovery Action

```http
POST /recover
Content-Type: application/json
```

**Request Body:**
```json
{
  "pod_name": "backend-abc123",
  "namespace": "nilabja-haldar-dev",
  "action": "restart",
  "execute": false
}
```

**Response (Plan Mode):**
```json
{
  "mode": "PLAN_ONLY",
  "action": "restart",
  "plan": {
    "steps": [
      "Delete pod backend-abc123",
      "Wait for new pod to be created by deployment",
      "Verify new pod is running and healthy"
    ],
    "estimated_downtime": "30s",
    "risks": ["Brief service interruption"]
  },
  "approval_required": true
}
```

**Response (Execute Mode with Approval):**
```json
{
  "action": "restart",
  "status": "success",
  "approval": {
    "requested_at": "2026-05-09T07:00:00Z",
    "approved_by": "user@company.com",
    "approved_at": "2026-05-09T07:01:00Z"
  },
  "result": {
    "old_pod": "backend-abc123",
    "new_pod": "backend-def456",
    "downtime": "28s"
  },
  "confluence_doc": "https://confluence.company.com/incident-001"
}
```

---

## Backup/Restore Agent API

**Base URL:** `http://backup-restore-agent:8083`

### Health Check

```http
GET /health
```

### List Backups

```http
GET /backups
```

**Response:**
```json
{
  "backups": [
    {
      "name": "backup-20260509-070000",
      "namespace": "nilabja-haldar-dev",
      "status": "Completed",
      "created_at": "2026-05-09T07:00:00Z",
      "size": "1.2GB",
      "expiration": "2026-06-08T07:00:00Z"
    }
  ],
  "total": 1
}
```

### Create Backup

```http
POST /backups
Content-Type: application/json
```

**Request Body:**
```json
{
  "namespace": "nilabja-haldar-dev",
  "include_resources": ["deployments", "services", "configmaps", "secrets"],
  "ttl": "720h"
}
```

**Response:**
```json
{
  "backup_name": "backup-20260509-070000",
  "status": "InProgress",
  "created_at": "2026-05-09T07:00:00Z",
  "estimated_completion": "2026-05-09T07:05:00Z"
}
```

### Restore Backup

```http
POST /restore
Content-Type: application/json
```

**Request Body:**
```json
{
  "backup_name": "backup-20260509-070000",
  "namespace": "nilabja-haldar-dev",
  "execute": false
}
```

**Response (Plan Mode):**
```json
{
  "mode": "PLAN_ONLY",
  "backup_name": "backup-20260509-070000",
  "plan": {
    "resources_to_restore": 45,
    "estimated_duration": "5m",
    "warnings": [
      "Existing resources will be overwritten",
      "Services may experience brief downtime"
    ]
  },
  "approval_required": true
}
```

### Schedule Backup

```http
POST /schedule
Content-Type: application/json
```

**Request Body:**
```json
{
  "namespace": "nilabja-haldar-dev",
  "schedule": "0 2 * * *",
  "retention_days": 30
}
```

**Response:**
```json
{
  "schedule_name": "daily-backup",
  "cron": "0 2 * * *",
  "next_run": "2026-05-10T02:00:00Z",
  "status": "active"
}
```

---

## Backend API

**Base URL:** `http://backend:8000`

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-05-09T07:00:00Z"
}
```

### Metrics

```http
GET /metrics
```

**Response:** Prometheus metrics in text format

### Products

#### List Products

```http
GET /api/products?page=1&limit=10
```

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Product 1",
      "description": "Description",
      "price": 29.99,
      "stock": 100,
      "created_at": "2026-05-09T07:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 10
}
```

#### Get Product

```http
GET /api/products/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Product 1",
  "description": "Description",
  "price": 29.99,
  "stock": 100,
  "created_at": "2026-05-09T07:00:00Z"
}
```

#### Create Product

```http
POST /api/products
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 39.99,
  "stock": 50
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Product",
  "description": "Product description",
  "price": 39.99,
  "stock": 50,
  "created_at": "2026-05-09T07:00:00Z"
}
```

### Orders

#### Create Order

```http
POST /api/orders
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 2, "quantity": 1}
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "total": 99.97,
  "status": "pending",
  "items": [
    {"product_id": 1, "quantity": 2, "price": 29.99},
    {"product_id": 2, "quantity": 1, "price": 39.99}
  ],
  "created_at": "2026-05-09T07:00:00Z"
}
```

#### Get Order

```http
GET /api/orders/{id}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "total": 99.97,
  "status": "pending",
  "items": [...],
  "created_at": "2026-05-09T07:00:00Z"
}
```

---

## WebSocket API

**Base URL:** `ws://supervisor-agent:8080/ws`

### Connect

```javascript
const ws = new WebSocket('ws://supervisor-agent:8080/ws');

ws.onopen = () => {
  console.log('Connected to supervisor agent');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Send Query

```javascript
ws.send(JSON.stringify({
  type: 'query',
  query: 'Show me CPU usage for backend pods',
  context: {
    user_id: 'user123',
    session_id: 'session456'
  }
}));
```

### Receive Response

```json
{
  "type": "response",
  "intent": "observability_query",
  "response": {
    "query_type": "prometheus",
    "results": [...]
  },
  "timestamp": "2026-05-09T07:00:00Z"
}
```

### Receive Notification

```json
{
  "type": "notification",
  "severity": "high",
  "message": "Backend pod CPU usage above 80%",
  "issue_id": "issue-001",
  "timestamp": "2026-05-09T07:00:00Z"
}
```

---

## Error Responses

All APIs use standard HTTP status codes and return errors in this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: query",
    "details": {
      "field": "query",
      "reason": "Field is required"
    }
  },
  "timestamp": "2026-05-09T07:00:00Z"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## Rate Limiting

All APIs are rate-limited to prevent abuse:

- **Default:** 100 requests per minute per IP
- **Authenticated:** 1000 requests per minute per user

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1715241660
```

---

## Authentication

Currently, the platform uses namespace-based authentication. All requests must include:

```http
X-Namespace: nilabja-haldar-dev
```

Future versions will support:
- API keys
- OAuth 2.0
- JWT tokens

---

**Made with Bob** 🤖