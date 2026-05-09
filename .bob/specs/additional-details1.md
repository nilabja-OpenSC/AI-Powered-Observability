These are the details provided which is asked in the interaction symmary summarizzed in the file "internal-monologue/2026-05-07_requirements-analysis-summary.md"


## Additional Details Needed
Identified 24 critical pieces of information across categories:
- Infrastructure (object storage, cluster details, registry)
- AI/LLM configuration (provider, API keys, vector store)
- Application specifics (domain, TLS, authentication)
- Observability config (retention, thresholds, schedules)
- Development/testing (local setup, CI/CD, testing strategy)


## Infrastructure & Deployment
**Object Storage Configuration for Thanos/Velero** : **efs-sc(efs.csi.aws.com)**

**Slack Webhook URL for notifications** : Keep the demo placeholder in the code like https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX, I will include later

**Confluence API details** : keep demo placeholder in the code like https://example.com/confluence/api/content, I will include later

**OpenShift ROSA cluster details** : I will deplpy the code manually

**Container registry for application images** : icr.io/nilabja-reg, but I will create the image and push

**Resource limits/requests preferences for all components** : Dont set any resource limits/requests for now

**PVC storage class and size requirements** : efs.csi.aws.com, 10GB

## AI/LLM Configuration

**LLM provider choice** :  OpenAI

**API keys/endpoints for chosen LLM** : Key I will add, keep placeholder, https://api.groq.com/openai/v1

**Vector store preference for agent memory** : Chroma

**Agent execution framework preferences** :  LangChain

## Application Specifics

**Domain/ingress configuration for frontend/backend access** : No custom domain, use openshift route  for exposure, if required then istio can be used for ingress
**TLS/certificate requirements** : No TLS required
**Authentication mechanism (if needed beyond simple admin flag)** : simple password 
**Sample data preferences (product categories, realistic data)** : use from any generic e-commecer site

## Observability Configuration

**Metrics retention periods (Prometheus, Thanos)** : 10 days
**Log retention policies (Loki)** : use any standard policy
**Alert severity thresholds (latency SLOs, error rates)** : set to 100%
**Dashboard refresh intervals** : 10s
**Backup schedule preferences (daily, weekly, retention)** : daily

## Development & Testing

**Local development setup requirements** : NA
**CI/CD pipeline preferences (if any)** : NR
**Testing strategy (unit, integration, e2e)** : NR
**Documentation format preferences** : USe default format (MD)
