import { useState, useEffect, useRef } from 'react'
import './App.css'

interface Message {
  id: string
  text: string
  sender: 'user' | 'agent'
  timestamp: Date
}

// Demo mode responses with agentic behaviors
const DEMO_RESPONSES: Record<string, string> = {
  // Follow-up responses for CPU
  'load balancer': `🤖 **Analyzing load balancer configuration...**
🔍 **Checking service mesh settings...**

⚖️ **Load Balancer Analysis**

**Current Configuration:**
- Algorithm: Round Robin
- Health Check Interval: 10s
- Timeout: 5s
- Unhealthy Threshold: 3 failures

**Backend Pod Distribution:**
- backend-7d9f8c6b5-x7k2m: 35% of traffic
- backend-7d9f8c6b5-9p4tn: 42% of traffic
- backend-7d9f8c6b5-m3w8q: 23% of traffic

**🧠 Root Cause Identified:**
The imbalance is caused by:
1. Pod m3w8q started 2 hours later (rolling update)
2. Connection draining not fully complete
3. Sticky sessions enabled for some clients

**💡 Recommendations:**
1. Switch to Least Connections algorithm
2. Disable sticky sessions (not needed for stateless API)
3. Adjust connection draining timeout to 60s

Would you like me to apply these optimizations?`,

  'cpu trends': `🤖 **Fetching CPU metrics from last 24 hours...**
📊 **Computing trend analysis...**

📈 **CPU Usage Trends (24h)**

**Hourly Breakdown:**
- 00:00-06:00: 25-30% (Low traffic)
- 06:00-09:00: 35-45% (Morning ramp-up)
- 09:00-12:00: 50-60% (Peak morning)
- 12:00-14:00: 45-55% (Lunch dip)
- 14:00-18:00: 55-65% (Peak afternoon)
- 18:00-24:00: 40-50% (Evening decline)

**Pattern Analysis:**
- Daily peak: 65% at 3 PM
- Daily low: 25% at 4 AM
- Average: 45%
- Trend: +2% week-over-week growth

**🎯 Capacity Planning:**
- Current headroom: 35%
- Projected usage in 30 days: 53%
- Recommended action: Monitor, no scaling needed yet

**⚠️ Anomalies Detected:**
- Spike to 78% on May 18 at 2:15 PM (deployment event)
- Unusual pattern on May 19 (weekend traffic higher than expected)

Should I investigate the weekend traffic anomaly?`,

  'cpu alert': `🤖 **Creating CPU threshold alerts...**
🔔 **Configuring notification channels...**

✅ **CPU Alerts Configured**

**Alert Rules Created:**
1. **High CPU Warning**
   - Threshold: > 70% for 5 minutes
   - Severity: Warning
   - Action: Slack notification to #ops-team

2. **Critical CPU Alert**
   - Threshold: > 85% for 2 minutes
   - Severity: Critical
   - Action: PagerDuty incident + Slack

3. **Sustained High CPU**
   - Threshold: > 60% for 30 minutes
   - Severity: Info
   - Action: Email to ops-team@company.com

4. **CPU Spike Detection**
   - Threshold: 20% increase in 1 minute
   - Severity: Warning
   - Action: Slack notification

**Notification Channels:**
- ✅ Slack: #ops-team
- ✅ PagerDuty: On-call rotation
- ✅ Email: ops-team@company.com

**Alert Status:** Active and monitoring

Would you like to test the alert system?`,

  // Follow-up responses for Health
  'automated fix': `🤖 **Initiating automated remediation...**
🔧 **Applying fixes with approval workflow...**

✅ **Automated Fixes Applied**

**Actions Taken:**

1. **observability-agent-4k9m7 (CrashLoopBackOff)**
   - ✅ Verified Prometheus service is running
   - ✅ Updated service endpoint in agent config
   - ✅ Restarted pod
   - ✅ Status: Running (0 restarts in last 5 min)

2. **backup-agent-3n8p5 (ImagePullBackOff)**
   - ✅ Checked image registry
   - ✅ Updated deployment to use v1.2.2 (latest stable)
   - ✅ Triggered new rollout
   - ✅ Status: Running (image pulled successfully)

**Verification:**
- All pods now in Running state
- Health check: 10/10 pods healthy
- No restart loops detected
- Resource usage normal

**Documentation:**
- Created incident report: INC-2024-0543
- Updated runbook with fix procedures
- Notified #ops-team on Slack

**🎉 All issues resolved!**

Should I set up monitoring to prevent similar issues?`,

  'restart history': `🤖 **Querying pod restart events...**
📊 **Analyzing restart patterns...**

🔄 **Pod Restart History (Last 7 Days)**

**High Restart Count:**
1. observability-agent-4k9m7: 47 restarts
   - Pattern: Every 15-20 minutes
   - Reason: Connection refused to Prometheus
   - First occurrence: May 18, 10:23 AM

2. backup-agent-3n8p5: 12 restarts
   - Pattern: Every 2-3 hours
   - Reason: ImagePullBackOff
   - First occurrence: May 19, 2:15 PM

**Normal Restart Count:**
3. backend-7d9f8c6b5-x7k2m: 2 restarts
   - Reason: Rolling update deployments
   - Last: May 17, 3:45 PM

4. frontend-6c8d9f7b4-k5m2p: 1 restart
   - Reason: OOMKilled (memory spike)
   - Last: May 16, 11:20 AM

**🧠 Analysis:**
- observability-agent: Configuration issue (now fixed)
- backup-agent: Image availability issue (now fixed)
- frontend: One-time memory spike (within limits)

**Trend:** Restart rate decreased 95% after recent fixes

All critical issues have been resolved!`,

  'incident report': `🤖 **Generating incident report...**
📝 **Compiling timeline and impact analysis...**

📋 **Incident Report Created**

**Incident ID:** INC-2024-0543
**Severity:** Medium
**Status:** Resolved
**Duration:** 2 hours 15 minutes

**Summary:**
Two pods experiencing restart loops affecting observability and backup capabilities.

**Timeline:**
- 14:23:45 - observability-agent enters CrashLoopBackOff
- 14:28:33 - Monitoring gaps detected
- 14:35:00 - backup-agent enters ImagePullBackOff
- 14:45:00 - AI Agent detected issues
- 15:10:00 - Root cause identified
- 15:30:00 - Fixes applied
- 16:38:45 - All systems restored

**Root Causes:**
1. Prometheus service endpoint changed during upgrade
2. Backup agent image v1.2.3 not published to registry

**Impact:**
- Observability: 2h 15m gap in metrics collection
- Backups: 2 scheduled backups missed
- User Impact: None (internal systems only)

**Resolution:**
- Updated observability-agent configuration
- Rolled back backup-agent to v1.2.2
- Verified all systems operational

**Prevention:**
- Added pre-deployment image verification
- Implemented config validation checks
- Enhanced monitoring for agent health

**Report saved to:** Confluence > Incidents > INC-2024-0543

Would you like me to share this with the team?`,

  // Follow-up responses for Errors
  'connection pool': `🤖 **Applying database connection pool optimization...**
⚙️ **Updating configuration...**

✅ **Connection Pool Optimized**

**Changes Applied:**
- Max Connections: 100 → 150 (+50%)
- Min Idle: 10 → 20
- Connection Timeout: 30s → 45s
- Idle Timeout: 10m → 15m
- Max Lifetime: 30m → 45m

**Before:**
- Active: 95/100 (95% utilization)
- Wait Time: 2.3s average
- Timeouts: 12 per hour

**After (5 min monitoring):**
- Active: 48/150 (32% utilization)
- Wait Time: 0.1s average
- Timeouts: 0

**Performance Impact:**
- API response time: 145ms → 98ms (-32%)
- Error rate: 0.8% → 0.1% (-87%)
- Database CPU: 65% → 58% (-7%)

**🎉 Optimization successful!**

The connection pool is now properly sized for current load.

Should I set up alerts for connection pool exhaustion?`,

  'ops alert': `🤖 **Sending alert to operations team...**
📢 **Notifying via Slack and email...**

✅ **Alert Sent Successfully**

**Slack Notification:**
- Channel: #ops-team
- Message: "🚨 Database connection pool exhaustion detected and resolved"
- Mentions: @ops-oncall
- Incident Link: INC-2024-0543
- Status: ✅ Delivered

**Email Notification:**
- To: ops-team@company.com
- Subject: "[RESOLVED] Database Connection Pool Issue"
- Attachments:
  - Error log summary
  - Performance graphs
  - Resolution steps
- Status: ✅ Sent

**PagerDuty:**
- Incident: #12345
- Status: Resolved
- Resolution Time: 45 minutes
- Assigned: @ops-oncall

**Team Response:**
- 👍 3 acknowledgments
- 💬 2 comments
- ✅ Incident closed

All stakeholders have been notified!`,

  'error trends': `🤖 **Analyzing error patterns over time...**
📊 **Computing trend analysis...**

📉 **Error Trends (Last 7 Days)**

**Daily Error Count:**
- May 14: 23 errors
- May 15: 31 errors
- May 16: 45 errors (spike)
- May 17: 28 errors
- May 18: 67 errors (major spike)
- May 19: 12 errors (after fixes)
- May 20: 3 errors (current)

**Error Categories:**
1. Database Timeouts: 45% (decreasing)
2. API 500 Errors: 30% (resolved)
3. Network Issues: 15% (stable)
4. Auth Failures: 10% (stable)

**🧠 Pattern Analysis:**
- Spike on May 16: Deployment issue
- Major spike on May 18: Connection pool exhaustion
- Sharp decline on May 19: Fixes applied
- Current: 95% reduction in errors

**Trend:** ⬇️ Decreasing (excellent)

**Forecast:**
- Expected errors tomorrow: 2-4
- Weekly average: 8 errors
- Status: Within SLO targets

System health is improving significantly!`,

  // Follow-up responses for Memory
  'cache efficiency': `🤖 **Analyzing Redis cache performance...**
📊 **Computing hit rates and efficiency metrics...**

💾 **Cache Efficiency Analysis**

**Redis Performance:**
- Cache Hit Rate: 65%
- Cache Miss Rate: 35%
- Eviction Rate: 12 keys/min
- Memory Usage: 256 MB / 512 MB (50%)

**Hit Rate by Key Pattern:**
- User sessions: 92% (excellent)
- Product catalog: 45% (poor)
- API responses: 78% (good)
- Search results: 38% (poor)

**🧠 Issues Identified:**
1. Product catalog TTL too short (5 min)
2. Search results not cached effectively
3. High eviction rate indicates memory pressure

**💡 Optimization Recommendations:**
1. Increase product catalog TTL: 5m → 30m
2. Implement search result caching
3. Increase Redis memory: 512 MB → 1 GB
4. Add cache warming for popular products

**Expected Impact:**
- Hit rate: 65% → 85% (+20%)
- API latency: -25%
- Database load: -40%

Should I apply these optimizations?`,

  'memory prediction': `🤖 **Running predictive memory analysis...**
🔮 **Using ML model for forecasting...**

🔮 **Memory Usage Prediction (Next 24h)**

**Current State:**
- Usage: 3.8 GB / 8 GB (47.5%)
- Trend: +0.5% per hour
- Pattern: Daily cycle detected

**Hourly Forecast:**
- 6 PM (now): 47.5%
- 9 PM: 52%
- 12 AM: 48%
- 6 AM: 42%
- 12 PM: 55%
- 6 PM (tomorrow): 58%

**Peak Predictions:**
- Tomorrow 3 PM: 62% (daily peak)
- Tomorrow 4 AM: 40% (daily low)

**🧠 Analysis:**
- No OOM risk in next 24h
- Comfortable headroom: 38%
- Growth rate: Normal
- Pattern: Predictable daily cycle

**⚠️ Long-term Forecast (30 days):**
- Projected usage: 68%
- Recommended action: Plan capacity increase
- Suggested timeline: 2-3 weeks

**Confidence:** 94% (based on 90 days historical data)

Should I create a capacity planning report?`,

  'memory optimize': `🤖 **Analyzing memory allocation...**
⚙️ **Identifying optimization opportunities...**

🎯 **Memory Optimization Plan**

**Current Allocation:**
- postgres-0: 2 GB (60% used = 1.2 GB)
- backend pods: 1 GB each (51% used = 512 MB)
- redis: 512 MB (50% used = 256 MB)
- frontend: 512 MB (35% used = 180 MB)

**Optimization Opportunities:**

1. **Frontend Pods** (High priority)
   - Current: 512 MB, using 180 MB
   - Recommended: 256 MB
   - Savings: 256 MB per pod × 3 = 768 MB

2. **Backend Pods** (Medium priority)
   - Current: 1 GB, using 512 MB
   - Recommended: 768 MB
   - Savings: 256 MB per pod × 3 = 768 MB

3. **Redis** (Low priority)
   - Current: 512 MB, using 256 MB
   - Keep as-is for cache growth

**Total Potential Savings:** 1.5 GB (19% of cluster)

**⚠️ Safety Margins:**
- All recommendations include 30% headroom
- Gradual rollout recommended
- Monitoring for 48h after changes

**Implementation Plan:**
1. Week 1: Optimize frontend pods
2. Week 2: Monitor and validate
3. Week 3: Optimize backend pods
4. Week 4: Final validation

Should I proceed with Phase 1 (frontend optimization)?`,

  // Follow-up responses for Metrics
  'performance report': `🤖 **Generating comprehensive performance report...**
📊 **Compiling metrics and analysis...**

📈 **Performance Report - May 20, 2024**

**Executive Summary:**
- Overall Health: ✅ Excellent (95/100)
- Availability: 99.95% (exceeds SLO)
- Performance: Within targets
- Incidents: 1 (resolved)

**Application Metrics:**
- Total Requests: 1.8M (24h)
- Success Rate: 99.2%
- Avg Response Time: 145ms
- P95 Latency: 320ms
- P99 Latency: 580ms

**Infrastructure:**
- CPU: 45% avg (healthy)
- Memory: 47.5% avg (healthy)
- Disk I/O: 23 MB/s (normal)
- Network: 156 MB/s (normal)

**Database Performance:**
- Query Time: 12ms avg
- Slow Queries: 3 (optimized)
- Connections: 48/150 (healthy)
- Cache Hit Rate: 65%

**Incidents & Issues:**
- Critical: 0
- High: 1 (resolved in 45m)
- Medium: 2 (resolved)
- Low: 5 (monitoring)

**Trends:**
- Traffic: +15% vs last week
- Performance: Stable
- Error Rate: -87% (improved)
- Availability: +0.05%

**Recommendations:**
1. Scale in 3 days (traffic growth)
2. Optimize cache (hit rate improvement)
3. Monitor slow queries

**Report saved to:** Confluence > Reports > Performance-2024-05-20

Would you like me to schedule this as a weekly report?`,

  'slow queries': `🤖 **Analyzing slow query patterns...**
🔍 **Identifying optimization opportunities...**

🐌 **Slow Query Analysis**

**Top 3 Slow Queries (Last Hour):**

1. **Product Search Query**
   - Execution Time: 2.3s
   - Frequency: 450 times/hour
   - Impact: High
   - Query: SELECT * FROM products WHERE name LIKE '%search%'
   
   **Issue:** Full table scan, no index on name
   **Fix:** Add index on name column
   **Expected improvement:** 2.3s → 45ms (-95%)

2. **Order History Query**
   - Execution Time: 1.8s
   - Frequency: 120 times/hour
   - Impact: Medium
   - Query: Complex JOIN across 4 tables
   
   **Issue:** Missing composite index
   **Fix:** Add composite index on (user_id, created_at)
   **Expected improvement:** 1.8s → 120ms (-93%)

3. **Analytics Aggregation**
   - Execution Time: 3.5s
   - Frequency: 30 times/hour
   - Impact: Low
   - Query: COUNT(*) with multiple GROUP BY
   
   **Issue:** No materialized view
   **Fix:** Create materialized view, refresh hourly
   **Expected improvement:** 3.5s → 50ms (-98%)

**Total Impact:**
- Queries affected: 600/hour
- Time saved: 1,200 seconds/hour
- Database load reduction: 35%

**🔧 Optimization Plan:**
1. Create indexes (5 min downtime)
2. Create materialized view (no downtime)
3. Update query patterns in code

Should I apply these optimizations?`,

  'auto scaling': `🤖 **Creating auto-scaling recommendations...**
📊 **Analyzing load patterns and capacity...**

⚖️ **Auto-Scaling Plan**

**Current Configuration:**
- Backend: 3 replicas (fixed)
- Frontend: 3 replicas (fixed)
- No auto-scaling enabled

**Recommended HPA Configuration:**

**Backend Pods:**
- Min Replicas: 3
- Max Replicas: 8
- Target CPU: 70%
- Target Memory: 80%
- Scale Up: +1 pod when CPU > 70% for 2 min
- Scale Down: -1 pod when CPU < 50% for 5 min

**Frontend Pods:**
- Min Replicas: 2
- Max Replicas: 6
- Target CPU: 65%
- Target Memory: 75%
- Scale Up: +1 pod when CPU > 65% for 2 min
- Scale Down: -1 pod when CPU < 45% for 5 min

**Cost-Benefit Analysis:**
- Current cost: $450/month (fixed)
- With auto-scaling: $320-580/month
- Average savings: 15%
- Peak capacity: +67%

**Scaling Scenarios:**
- Normal load: 3 backend, 2 frontend
- Peak load: 6 backend, 4 frontend
- High traffic: 8 backend, 6 frontend

**🎯 Benefits:**
- Automatic capacity adjustment
- Cost optimization during low traffic
- Better handling of traffic spikes
- Improved reliability

Should I create the HPA configurations?`,
  'cpu': `🤖 **Analyzing CPU metrics across your cluster...**

📊 **CPU Usage Analysis**

**Backend Pods:**
- backend-7d9f8c6b5-x7k2m: 45% (Normal)
- backend-7d9f8c6b5-9p4tn: 52% (Normal)
- backend-7d9f8c6b5-m3w8q: 38% (Normal)

**Average CPU Usage:** 45%
**Status:** ✅ All pods operating within normal parameters

**🧠 Agent Analysis:**
I've detected a slight imbalance in CPU distribution. Pod 9p4tn is handling 15% more load than m3w8q. This could indicate:
- Uneven traffic distribution
- Different request complexity
- Potential for better load balancing

**💡 Proactive Suggestion:**
Would you like me to:
1. Check if load balancer configuration needs adjustment?
2. Analyze request patterns to understand the imbalance?
3. Set up alerts for CPU threshold violations?`,

  'health': `🤖 **Running comprehensive health check...**
🔍 **Step 1:** Querying Kubernetes API for pod status
🔍 **Step 2:** Analyzing readiness probes
🔍 **Step 3:** Checking recent restart patterns

🏥 **Pod Health Status**

**Namespace: nilabja-haldar-dev**

✅ **Healthy Pods (8/10):**
- frontend-6c8d9f7b4-k5m2p: Running (Ready 2/2)
- backend-7d9f8c6b5-x7k2m: Running (Ready 1/1)
- backend-7d9f8c6b5-9p4tn: Running (Ready 1/1)
- postgres-0: Running (Ready 1/1)
- redis-master-0: Running (Ready 1/1)
- chat-ui-5f7c8d9e6-p8q3r: Running (Ready 1/1)

⚠️ **Issues Detected (2/10):**
- observability-agent-4k9m7: CrashLoopBackOff
  - Last restart: 2 minutes ago
  - Error: Connection refused to Prometheus
- backup-agent-3n8p5: ImagePullBackOff
  - Image: backup-agent:v1.2.3 not found

**Overall Health:** 80% - Action required for 2 pods

**🤖 Agent Reasoning:**
I've identified the root causes:
1. **observability-agent**: Prometheus service is likely not running or misconfigured
2. **backup-agent**: Image tag v1.2.3 doesn't exist in registry

**🔧 Automated Remediation Available:**
I can help fix these issues:
- For observability-agent: Check Prometheus service status and restart if needed
- For backup-agent: Update deployment to use latest stable image (v1.2.2)

Would you like me to proceed with automated fixes?`,

  'error': `🤖 **Aggregating error logs from Loki...**
🔍 **Analyzing patterns and correlations...**
🧠 **Identifying root causes...**

🔍 **Error Logs Analysis (Last Hour)**

**Critical Errors (3):**
1. **[Backend] Database Connection Timeout**
   - Time: 14:23:45
   - Pod: backend-7d9f8c6b5-x7k2m
   - Message: "Connection to postgres timed out after 30s"
   
2. **[Frontend] API Request Failed**
   - Time: 14:25:12
   - Pod: frontend-6c8d9f7b4-k5m2p
   - Message: "GET /api/products returned 500"

3. **[Observability] Prometheus Scrape Failed**
   - Time: 14:28:33
   - Pod: observability-agent-4k9m7
   - Message: "Failed to scrape metrics: connection refused"

**Warning Logs (12):**
- High memory usage warnings: 8
- Slow query warnings: 4

**🧠 Agent Analysis - Correlation Detected:**
I've identified a cascade failure pattern:
1. Database timeout (14:23:45) →
2. API failures (14:25:12) →
3. Monitoring disruption (14:28:33)

**Root Cause:** Database connection pool exhaustion likely triggered the cascade.

**💡 Intelligent Recommendations:**
1. **Immediate:** Increase database connection pool from 100 to 150
2. **Short-term:** Add connection pool monitoring alerts
3. **Long-term:** Implement circuit breaker pattern for database calls

**🔄 Next Steps:**
Should I:
- Create a Confluence incident report?
- Send alert to #ops-team Slack channel?
- Apply the connection pool fix automatically?`,

  'memory': `🤖 **Collecting memory metrics...**
📊 **Analyzing trends and anomalies...**

💾 **Memory Usage Report**

**Top Memory Consumers:**
1. postgres-0: 1.2 GB / 2 GB (60%)
2. backend-7d9f8c6b5-x7k2m: 512 MB / 1 GB (51%)
3. redis-master-0: 256 MB / 512 MB (50%)
4. frontend-6c8d9f7b4-k5m2p: 180 MB / 512 MB (35%)

**Cluster Total:**
- Used: 3.8 GB / 8 GB (47.5%)
- Available: 4.2 GB

**Memory Trends (Last 24h):**
- Average: 45%
- Peak: 68% (at 10:30 AM)
- Current: 47.5%

**Status:** ✅ Memory usage is within acceptable limits

**🧠 Predictive Analysis:**
Based on historical patterns, I predict:
- Memory will reach 55% by 6 PM (normal daily peak)
- No risk of OOM in next 24 hours
- Postgres memory growth rate: +2% per hour (normal)

**🎯 Optimization Opportunity:**
I notice redis-master-0 is at 50% capacity but cache hit rate is only 65%.
Would you like me to analyze cache efficiency and suggest optimizations?`,

  'metrics': `🤖 **Gathering metrics from Prometheus...**
📊 **Computing aggregations and percentiles...**
🎯 **Comparing against SLOs...**

📈 **Key Performance Metrics**

**Application Performance:**
- Request Rate: 1,247 req/min
- Average Response Time: 145ms
- Error Rate: 0.8%
- P95 Latency: 320ms
- P99 Latency: 580ms

**Infrastructure:**
- CPU Usage: 45% (Healthy)
- Memory Usage: 47.5% (Healthy)
- Disk I/O: 23 MB/s (Normal)
- Network Traffic: 156 MB/s

**Database:**
- Active Connections: 45/100
- Query Time (avg): 12ms
- Slow Queries: 3 in last hour

**Status:** ✅ All metrics within normal operating range

**🎯 SLO Compliance:**
- Availability SLO (99.9%): ✅ 99.95% (exceeding target)
- Latency SLO (P95 < 500ms): ✅ 320ms (well within target)
- Error Rate SLO (< 1%): ✅ 0.8% (meeting target)

**🧠 Intelligent Insights:**
1. P99 latency (580ms) is approaching threshold - investigating...
2. 3 slow queries detected - likely candidates for optimization
3. Request rate increased 15% vs yesterday - traffic growth detected

**📊 Trend Prediction:**
At current growth rate, you'll need to scale by +2 pods in ~3 days.

Would you like me to:
- Generate a detailed performance report?
- Create auto-scaling recommendations?
- Investigate those slow queries?`,

  'fix': `🤖 **Initiating automated remediation workflow...**

🔧 **Automated Fix Execution**

**Step 1:** Validating permissions ✅
**Step 2:** Creating backup of current configuration ✅
**Step 3:** Applying fixes...

**Actions Taken:**
1. ✅ Restarted observability-agent pod
2. ✅ Updated backup-agent image to v1.2.2
3. ✅ Increased database connection pool to 150
4. ✅ Applied circuit breaker configuration

**Step 4:** Verifying fixes ✅
**Step 5:** Monitoring for 60 seconds ✅

**Results:**
- observability-agent: Now Running (0 restarts)
- backup-agent: Image pulled successfully, pod Running
- Database connections: Stable at 48/150
- Error rate: Dropped from 0.8% to 0.1%

**📝 Documentation:**
- Created incident report: INC-2024-0542
- Updated Confluence runbook
- Sent notification to #ops-team

**🎉 All issues resolved successfully!**

Would you like me to set up preventive monitoring to avoid similar issues?`,

  'default': `🤖 **AI Observability Assistant - Agentic Mode**

Hello! I'm your intelligent observability agent with autonomous capabilities.

**🧠 What Makes Me Agentic:**
- **Proactive Monitoring:** I continuously analyze your infrastructure
- **Root Cause Analysis:** I correlate events to find underlying issues
- **Predictive Insights:** I forecast problems before they occur
- **Automated Remediation:** I can fix issues with your approval
- **Context Awareness:** I remember our conversation and learn from patterns

**💡 I Can Help You With:**

📊 **Intelligent Monitoring**
- Real-time metrics analysis with trend prediction
- Anomaly detection and alerting
- SLO compliance tracking

🔍 **Smart Troubleshooting**
- Multi-step root cause analysis
- Correlation of logs, metrics, and events
- Automated issue resolution

🤝 **Collaborative Actions**
- Create incident reports in Confluence
- Send alerts to Slack channels
- Generate detailed performance reports

**🎯 Try These Agentic Commands:**
- "Analyze and fix the pod health issues"
- "Predict when we'll need to scale"
- "Find the root cause of recent errors"
- "Optimize our resource usage"
- "Create an incident report for the outage"

I'm ready to help! What would you like me to investigate?`
}

// Follow-up suggestions based on context
const FOLLOW_UP_SUGGESTIONS: Record<string, string[]> = {
  'cpu': [
    'Analyze load balancer configuration',
    'Show CPU trends over last 24 hours',
    'Set up CPU threshold alerts'
  ],
  'health': [
    'Apply automated fixes for failing pods',
    'Show pod restart history',
    'Create incident report'
  ],
  'error': [
    'Apply database connection pool fix',
    'Send alert to ops team',
    'Show error trends over time'
  ],
  'memory': [
    'Analyze cache efficiency',
    'Predict memory usage for next 24h',
    'Optimize memory allocation'
  ],
  'metrics': [
    'Generate performance report',
    'Investigate slow queries',
    'Create auto-scaling plan'
  ]
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [demoMode, setDemoMode] = useState(false)
  const [lastQueryType, setLastQueryType] = useState<string>('default')
  const [showFollowUps, setShowFollowUps] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8080'
  const WS_URL = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8080/ws'

  useEffect(() => {
    // Try to connect to WebSocket
    const ws = new WebSocket(WS_URL)
    let connectionTimeout: ReturnType<typeof setTimeout>
    
    // Set timeout to enable demo mode if connection fails
    connectionTimeout = setTimeout(() => {
      if (!isConnected) {
        console.log('Backend unavailable, enabling demo mode')
        setDemoMode(true)
        setIsConnected(true)
        addMessage('System', '🎭 Demo Mode Active - Backend unavailable, showing sample responses', 'agent')
      }
    }, 3000)
    
    ws.onopen = () => {
      clearTimeout(connectionTimeout)
      console.log('Connected to supervisor agent')
      setIsConnected(true)
      setDemoMode(false)
      addMessage('System', 'Connected to AI Observability Agent', 'agent')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      addMessage(data.id || Date.now().toString(), data.text || data.message, 'agent')
      setIsLoading(false)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      clearTimeout(connectionTimeout)
      if (!demoMode) {
        setDemoMode(true)
        setIsConnected(true)
        addMessage('System', '🎭 Demo Mode Active - Backend unavailable, showing sample responses', 'agent')
      }
    }

    ws.onclose = () => {
      console.log('Disconnected from supervisor agent')
      clearTimeout(connectionTimeout)
      if (!demoMode) {
        setDemoMode(true)
        setIsConnected(true)
        addMessage('System', '🎭 Demo Mode Active - Backend unavailable, showing sample responses', 'agent')
      }
    }

    wsRef.current = ws

    return () => {
      clearTimeout(connectionTimeout)
      ws.close()
    }
  }, [WS_URL])

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (id: string, text: string, sender: 'user' | 'agent') => {
    setMessages(prev => [...prev, {
      id,
      text,
      sender,
      timestamp: new Date()
    }])
  }

  const getDemoResponse = (query: string): { response: string; type: string } => {
    const lowerQuery = query.toLowerCase()
    
    // Follow-up responses - check these first for more specific matches
    if (lowerQuery.includes('load balancer') || lowerQuery.includes('load-balancer')) {
      return { response: DEMO_RESPONSES['load balancer'], type: 'cpu' }
    }
    if (lowerQuery.includes('cpu trends') || lowerQuery.includes('cpu') && lowerQuery.includes('trend')) {
      return { response: DEMO_RESPONSES['cpu trends'], type: 'cpu' }
    }
    if (lowerQuery.includes('cpu alert') || (lowerQuery.includes('alert') && lowerQuery.includes('cpu'))) {
      return { response: DEMO_RESPONSES['cpu alert'], type: 'cpu' }
    }
    if (lowerQuery.includes('automated fix') || lowerQuery.includes('apply') && lowerQuery.includes('fix')) {
      return { response: DEMO_RESPONSES['automated fix'], type: 'health' }
    }
    if (lowerQuery.includes('restart history') || lowerQuery.includes('restart')) {
      return { response: DEMO_RESPONSES['restart history'], type: 'health' }
    }
    if (lowerQuery.includes('incident report') || lowerQuery.includes('create') && lowerQuery.includes('report')) {
      return { response: DEMO_RESPONSES['incident report'], type: 'health' }
    }
    if (lowerQuery.includes('connection pool') || lowerQuery.includes('database') && lowerQuery.includes('fix')) {
      return { response: DEMO_RESPONSES['connection pool'], type: 'error' }
    }
    if (lowerQuery.includes('ops alert') || lowerQuery.includes('send alert') || lowerQuery.includes('ops team')) {
      return { response: DEMO_RESPONSES['ops alert'], type: 'error' }
    }
    if (lowerQuery.includes('error trends') || lowerQuery.includes('error') && lowerQuery.includes('trend')) {
      return { response: DEMO_RESPONSES['error trends'], type: 'error' }
    }
    if (lowerQuery.includes('cache efficiency') || lowerQuery.includes('cache')) {
      return { response: DEMO_RESPONSES['cache efficiency'], type: 'memory' }
    }
    if (lowerQuery.includes('memory prediction') || lowerQuery.includes('predict') && lowerQuery.includes('memory')) {
      return { response: DEMO_RESPONSES['memory prediction'], type: 'memory' }
    }
    if (lowerQuery.includes('memory optimize') || lowerQuery.includes('optimize') && lowerQuery.includes('memory')) {
      return { response: DEMO_RESPONSES['memory optimize'], type: 'memory' }
    }
    if (lowerQuery.includes('performance report') || lowerQuery.includes('generate') && lowerQuery.includes('report')) {
      return { response: DEMO_RESPONSES['performance report'], type: 'metrics' }
    }
    if (lowerQuery.includes('slow queries') || lowerQuery.includes('slow query') || lowerQuery.includes('investigate')) {
      return { response: DEMO_RESPONSES['slow queries'], type: 'metrics' }
    }
    if (lowerQuery.includes('auto scaling') || lowerQuery.includes('auto-scaling') || lowerQuery.includes('scaling plan')) {
      return { response: DEMO_RESPONSES['auto scaling'], type: 'metrics' }
    }
    
    // Main category responses
    if (lowerQuery.includes('fix') || lowerQuery.includes('remediate')) {
      return { response: DEMO_RESPONSES.fix, type: 'fix' }
    }
    if (lowerQuery.includes('cpu')) {
      return { response: DEMO_RESPONSES.cpu, type: 'cpu' }
    }
    if (lowerQuery.includes('health') || lowerQuery.includes('pod')) {
      return { response: DEMO_RESPONSES.health, type: 'health' }
    }
    if (lowerQuery.includes('error') || lowerQuery.includes('log')) {
      return { response: DEMO_RESPONSES.error, type: 'error' }
    }
    if (lowerQuery.includes('memory') || lowerQuery.includes('ram')) {
      return { response: DEMO_RESPONSES.memory, type: 'memory' }
    }
    if (lowerQuery.includes('metric') || lowerQuery.includes('performance')) {
      return { response: DEMO_RESPONSES.metrics, type: 'metrics' }
    }
    
    return { response: DEMO_RESPONSES.default, type: 'default' }
  }

  const sendMessage = async () => {
    if (!input.trim() || !isConnected) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message
    addMessage(Date.now().toString(), userMessage, 'user')

    // Demo mode - use canned responses
    if (demoMode) {
      setTimeout(() => {
        const { response, type } = getDemoResponse(userMessage)
        addMessage(Date.now().toString(), response, 'agent')
        setLastQueryType(type)
        setShowFollowUps(type !== 'default' && type !== 'fix')
        setIsLoading(false)
      }, 1500) // Simulate network delay with thinking time
      return
    }

    // Send via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        query: userMessage,
        timestamp: new Date().toISOString()
      }))
    } else {
      // Fallback to HTTP if WebSocket not available
      try {
        const response = await fetch(`${API_URL}/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userMessage })
        })
        const data = await response.json()
        addMessage(Date.now().toString(), data.response || data.message, 'agent')
      } catch (error) {
        // Enable demo mode on error
        setDemoMode(true)
        const { response, type } = getDemoResponse(userMessage)
        addMessage(Date.now().toString(), response, 'agent')
        setLastQueryType(type)
        setShowFollowUps(type !== 'default' && type !== 'fix')
      } finally {
        setIsLoading(false)
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 AI Observability Chat</h1>
        <div className="status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{demoMode ? '🎭 Demo Mode' : isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              <div className="message-content">
                <div className="message-text">{msg.text}</div>
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message agent">
              <div className="message-content">
                <div className="message-text">
                  <span className="loading">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about metrics, logs, or pod health..."
            disabled={!isConnected}
            rows={2}
          />
          <button 
            onClick={sendMessage} 
            disabled={!isConnected || !input.trim() || isLoading}
          >
            Send
          </button>
        </div>

        {showFollowUps && FOLLOW_UP_SUGGESTIONS[lastQueryType] && (
          <div className="follow-ups">
            <p>🤖 Suggested next actions:</p>
            {FOLLOW_UP_SUGGESTIONS[lastQueryType].map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInput(suggestion)
                  setShowFollowUps(false)
                }}
                className="follow-up-btn"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        <div className="examples">
          <p>Try asking:</p>
          <button onClick={() => setInput("Show CPU usage for backend pods")}>
            📊 Show CPU usage
          </button>
          <button onClick={() => setInput("Check pod health in namespace nilabja-haldar-dev")}>
            🏥 Check pod health
          </button>
          <button onClick={() => setInput("Show error logs from last hour")}>
            🔍 Show error logs
          </button>
          <button onClick={() => setInput("What's the memory usage?")}>
            💾 Memory usage
          </button>
          <button onClick={() => setInput("Show me key metrics")}>
            📈 Key metrics
          </button>
        </div>
      </div>
    </div>
  )
}

export default App

// Made with Bob
