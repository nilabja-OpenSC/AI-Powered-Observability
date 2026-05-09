# eCommerce Demo Application

## Objectives

You are an **expert Full‑Stack + Cloud‑Native Application Generation Agent.**

Your task is to DESIGN and GENERATE a **complete sample e‑commerce application, that is intentionally simple in business features but production‑realistic for demonstrating Observability, Reliability, Incident Management, Backup, and Agentic AI use cases.**

**The application must be:**
1. No paid third party services
2. Visually polished and production-like
3. Full end-to-end to deplpy in openshift cluster
4. Data driven using local or mock data

## Special Notes: 

You MUST generate the application from scratch without referencing,
searching, or assuming any existing files, repositories, or templates.

## Architecture and tech stack

The application will be built using the following technologies:


────────────────────────────────────────────
# PRIMARY OBJECTIVE
────────────────────────────────────────────
**Create a minimal yet complete e‑commerce system consisting of:**
- Frontend (Next.js)
- Backend (Python)
- Database (PVC‑backed) (Postgress Sql Ref:        Platform-Observability-Tools-Creation-Agent-prompt.md)
- Swagger / OpenAPI
- Styling (Tailwind CSS)
- Chat UI for Observability interaction

**The application should intentionally produce:**
- Traces (HTTP requests)
- Metrics (latency, error rate, throughput)
- Logs (structured, searchable)
- Failure scenarios (pod restarts, slow DB, failed requests)
so that Observability and Agentic AI tools can act on them.

────────────────────────────────────────────
# FUNCTIONAL REQUIREMENTS
────────────────────────────────────────────

────────────────────────────────────────────
## 1. **FRONTEND (Next.js)**
────────────────────────────────────────────
**The application should have the following pages:**

You must generate a Next.js UI with the following pages:

a. **Product Search Page**
   - List all products
   - Search by product name
   - Call backend GET /products
   - Show loading and error states

b. **Product Add Page - Access to admin user**
   - Add a new product (name, price, stock)
   - Call backend POST /products
   - Log client-side errors

c. **User Cart Page**
   - Add/remove products from cart
   - View cart summary
   - Call backend cart APIs

d. **Dummy Checkout Page**
   - Simulate checkout
   - Introduce artificial delay (to generate latency metrics)
   - Randomly fail some requests (to generate error metrics)

e. **User Add Page - Access to admin user**
   - Create a new user
   - Store user data in backend
   - Associate carts with users

f. Create 10 user, 1 admin user, 10 product category, 100 sample products

**All frontend calls must include:**
- Request IDs (headers)
- Proper error handling
- Logs sent to console (assumed to be collected by Loki)

────────────────────────────────────────────
## 2. BACKEND (Python)
────────────────────────────────────────────

- Language: Python
- Framework: FastAPI (preferred for Swagger)
- Architecture:
  - controllers (routes)
  - services (business logic)
  - models (DB schema)
  - observability wrapper

**You MUST implement:**
- CRUD for products
- Product CRUD
- User CRUD
- Cart operations (add/remove/list)
- Checkout simulation endpoint

**Observability requirements in backend:**
- Structured logging (JSON logs)
- Request/response latency measurement
- Custom metrics exposed at /metrics (Prometheus format)
- Correlation ID propagation

**Intentional chaos:**
- Optional error injection via environment variable
- Artificial DB latency toggle
- Random 5xx failures on checkout (configurable)

────────────────────────────────────────────
## 3. DATABASE
────────────────────────────────────────────

- Use a simple database suitable for Kubernetes demo:
  - PostgreSQL or SQLite (PVC backed)
- Schema:
  - users(id, name, email)
  - products(id, name, price, stock)
  - carts(id, user_id)
  - cart_items(cart_id, product_id, quantity)

**Requirements:**
- Database must run as a separate pod
- Storage must be via PVC
- Backend connects via service name
- Include sample seed data logic

────────────────────────────────────────────
## 4. SWAGGER / OPENAPI
────────────────────────────────────────────

- Swagger UI must be available at:
  /docs or /swagger
- Every endpoint must include:
  - Description
  - Request/response schema
  - Error responses

The Swagger UI is a key demo artifact.

────────────────────────────────────────────
## 5. CHAT UI FOR OBSERVABILITY
────────────────────────────────────────────

**You must create a simple Chat UI (can be in Next.js) that:**
- Connects to Observability Agent via service name
- Sends natural language queries
- Displays responses from Observability Agent
- Example queries:
  - "Why is checkout slow?"
  - "Show error rate for product service"
  - "Create a dashboard for cart latency"

This UI does NOT directly query Prometheus or Grafana.
It acts as a frontend for Agentic Observability interaction.

────────────────────────────────────────────
# NON‑FUNCTIONAL REQUIREMENTS
────────────────────────────────────────────

- Code must be:
  - Readable
  - Modular
  - Demo‑ready
- No authentication required (keep simple)
- Assume single namespace deployment:
  nilabja-haldar-dev
- Design must align with Kubernetes, Helm, and Observability tooling

────────────────────────────────────────────
# OUTPUT REQUIREMENTS
────────────────────────────────────────────

**For every component, you MUST output:**

1. High‑level architecture explanation
2. Folder structure
3. Key files with representative code
4. Environment variables used
5. Endpoints exposed
6. Observability signals generated (logs, metrics, traces – even if traces are mock)

Do NOT generate Helm charts in this step.
Focus purely on **application creation**.

────────────────────────────────────────────
# TONE & ROLE
────────────────────────────────────────────

**Act as:**
- Senior Staff Engineer
- Cloud‑Native Architect
- Observability‑driven developer

**Explain choices briefly but clearly.**
**Write in a friendly, conversational tone.**
**Be concise.**
**Avoid unnecessary theory.**
**Focus on demo realism and agent compatibility.**

**Begin by generating:**
1) Overall architecture
2) Backend service
3) Database
4) Frontend UI
5) Chat UI
in that order.