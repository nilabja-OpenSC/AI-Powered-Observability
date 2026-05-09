#!/bin/bash

# AI-Powered Observability Platform - Automated Deployment Script
# This script deploys all components in the correct order

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="nilabja-haldar-dev"
HELM_TIMEOUT="5m"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    local deployment=$1
    local namespace=$2
    local timeout=${3:-300}
    
    print_info "Waiting for deployment/$deployment to be ready..."
    if oc wait --for=condition=available --timeout=${timeout}s deployment/$deployment -n $namespace 2>/dev/null; then
        print_success "Deployment $deployment is ready"
        return 0
    else
        print_warning "Deployment $deployment not ready within timeout"
        return 1
    fi
}

# Function to wait for statefulset to be ready
wait_for_statefulset() {
    local statefulset=$1
    local namespace=$2
    local timeout=${3:-300}
    
    print_info "Waiting for statefulset/$statefulset to be ready..."
    if oc wait --for=jsonpath='{.status.readyReplicas}'=1 --timeout=${timeout}s statefulset/$statefulset -n $namespace 2>/dev/null; then
        print_success "StatefulSet $statefulset is ready"
        return 0
    else
        print_warning "StatefulSet $statefulset not ready within timeout"
        return 1
    fi
}

# Function to wait for daemonset to be ready
wait_for_daemonset() {
    local daemonset=$1
    local namespace=$2
    local timeout=${3:-300}
    
    print_info "Waiting for daemonset/$daemonset to be ready..."
    sleep 10  # Give daemonset time to schedule
    print_success "DaemonSet $daemonset deployed"
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v oc &> /dev/null; then
    print_error "OpenShift CLI (oc) not found. Please install it first."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    print_error "Helm not found. Please install it first."
    exit 1
fi

if ! oc whoami &> /dev/null; then
    print_error "Not logged in to OpenShift. Please run 'oc login' first."
    exit 1
fi

print_success "Prerequisites check passed"

# Create namespace if it doesn't exist
print_info "Creating namespace $NAMESPACE..."
if oc get project $NAMESPACE &> /dev/null; then
    print_warning "Namespace $NAMESPACE already exists"
else
    oc new-project $NAMESPACE
    print_success "Namespace $NAMESPACE created"
fi

# Set current project
oc project $NAMESPACE

# ============================================================================
# PHASE 1: CREATE SECRETS
# ============================================================================
print_info "=========================================="
print_info "PHASE 1: Creating Secrets"
print_info "=========================================="

# Check if secrets already exist
if oc get secret postgresql-secret -n $NAMESPACE &> /dev/null; then
    print_warning "Secret postgresql-secret already exists, skipping..."
else
    print_info "Creating PostgreSQL secret..."
    read -sp "Enter PostgreSQL password: " POSTGRES_PASSWORD
    echo
    read -sp "Enter PostgreSQL replication password: " REPLICATION_PASSWORD
    echo
    
    oc create secret generic postgresql-secret \
        --from-literal=postgres-password="$POSTGRES_PASSWORD" \
        --from-literal=replication-password="$REPLICATION_PASSWORD" \
        -n $NAMESPACE
    print_success "PostgreSQL secret created"
fi

if oc get secret ai-agents-secret -n $NAMESPACE &> /dev/null; then
    print_warning "Secret ai-agents-secret already exists, skipping..."
else
    print_info "Creating AI Agents secret..."
    read -p "Enter OpenAI API Key: " OPENAI_API_KEY
    read -p "Enter Slack Webhook URL: " SLACK_WEBHOOK_URL
    read -p "Enter Slack Bot Token: " SLACK_BOT_TOKEN
    read -p "Enter Slack Signing Secret: " SLACK_SIGNING_SECRET
    
    oc create secret generic ai-agents-secret \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --from-literal=SLACK_WEBHOOK_URL="$SLACK_WEBHOOK_URL" \
        --from-literal=SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
        --from-literal=SLACK_SIGNING_SECRET="$SLACK_SIGNING_SECRET" \
        -n $NAMESPACE
    print_success "AI Agents secret created"
fi

# ============================================================================
# PHASE 2: DATA LAYER
# ============================================================================
print_info "=========================================="
print_info "PHASE 2: Deploying Data Layer"
print_info "=========================================="

print_info "Deploying PostgreSQL..."
helm upgrade --install postgresql charts/data-layer/postgresql \
    --namespace $NAMESPACE \
    --set secrets.name=postgresql-secret \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_statefulset postgresql $NAMESPACE
print_success "PostgreSQL deployed successfully"

# ============================================================================
# PHASE 3: OBSERVABILITY STACK
# ============================================================================
print_info "=========================================="
print_info "PHASE 3: Deploying Observability Stack"
print_info "=========================================="

print_info "Deploying Prometheus..."
helm upgrade --install prometheus charts/observability-stack/prometheus \
    --namespace $NAMESPACE \
    --set config.alertmanagerUrl=http://alertmanager:9093 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_statefulset prometheus $NAMESPACE
print_success "Prometheus deployed successfully"

print_info "Deploying Loki..."
helm upgrade --install loki charts/observability-stack/loki \
    --namespace $NAMESPACE \
    --set config.alertmanagerUrl=http://alertmanager:9093 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_statefulset loki $NAMESPACE
print_success "Loki deployed successfully"

print_info "Deploying Promtail..."
helm upgrade --install promtail charts/observability-stack/promtail \
    --namespace $NAMESPACE \
    --set config.lokiUrl=http://loki:3100 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_daemonset promtail $NAMESPACE
print_success "Promtail deployed successfully"

print_info "Deploying Alertmanager..."
if ! oc get secret alertmanager-secret -n $NAMESPACE &> /dev/null; then
    read -p "Enter Slack Webhook URL for Alertmanager: " ALERTMANAGER_SLACK_URL
    oc create secret generic alertmanager-secret \
        --from-literal=slack-webhook-url="$ALERTMANAGER_SLACK_URL" \
        -n $NAMESPACE
fi

helm upgrade --install alertmanager charts/observability-stack/alertmanager \
    --namespace $NAMESPACE \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_statefulset alertmanager $NAMESPACE
print_success "Alertmanager deployed successfully"

print_info "Deploying Thanos..."
if ! oc get secret thanos-s3-secret -n $NAMESPACE &> /dev/null; then
    read -p "Enter S3 Access Key for Thanos: " THANOS_ACCESS_KEY
    read -sp "Enter S3 Secret Key for Thanos: " THANOS_SECRET_KEY
    echo
    oc create secret generic thanos-s3-secret \
        --from-literal=access-key="$THANOS_ACCESS_KEY" \
        --from-literal=secret-key="$THANOS_SECRET_KEY" \
        -n $NAMESPACE
fi

read -p "Enter S3 Bucket Name for Thanos: " THANOS_BUCKET
read -p "Enter S3 Endpoint for Thanos (default: s3.amazonaws.com): " THANOS_ENDPOINT
THANOS_ENDPOINT=${THANOS_ENDPOINT:-s3.amazonaws.com}

helm upgrade --install thanos charts/observability-stack/thanos \
    --namespace $NAMESPACE \
    --set config.prometheusUrl=http://prometheus:9090 \
    --set config.s3Bucket=$THANOS_BUCKET \
    --set config.s3Endpoint=$THANOS_ENDPOINT \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment thanos-query $NAMESPACE
print_success "Thanos deployed successfully"

print_info "Deploying Grafana..."
if ! oc get secret grafana-secret -n $NAMESPACE &> /dev/null; then
    read -p "Enter Grafana admin username (default: admin): " GRAFANA_USER
    GRAFANA_USER=${GRAFANA_USER:-admin}
    read -sp "Enter Grafana admin password: " GRAFANA_PASSWORD
    echo
    oc create secret generic grafana-secret \
        --from-literal=admin-user="$GRAFANA_USER" \
        --from-literal=admin-password="$GRAFANA_PASSWORD" \
        -n $NAMESPACE
fi

helm upgrade --install grafana charts/observability-stack/grafana \
    --namespace $NAMESPACE \
    --set secrets.name=grafana-secret \
    --set config.prometheusUrl=http://prometheus:9090 \
    --set config.lokiUrl=http://loki:3100 \
    --set config.thanosUrl=http://thanos-query:10902 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment grafana $NAMESPACE
print_success "Grafana deployed successfully"

# ============================================================================
# PHASE 4: BACKUP/RESTORE STACK
# ============================================================================
print_info "=========================================="
print_info "PHASE 4: Deploying Backup/Restore Stack"
print_info "=========================================="

print_info "Deploying Velero..."
if ! oc get secret velero-credentials -n $NAMESPACE &> /dev/null; then
    read -p "Enter AWS Access Key for Velero: " VELERO_ACCESS_KEY
    read -sp "Enter AWS Secret Key for Velero: " VELERO_SECRET_KEY
    echo
    
    cat > /tmp/credentials-velero <<EOF
[default]
aws_access_key_id=$VELERO_ACCESS_KEY
aws_secret_access_key=$VELERO_SECRET_KEY
EOF
    
    oc create secret generic velero-credentials \
        --from-file=cloud=/tmp/credentials-velero \
        -n $NAMESPACE
    rm /tmp/credentials-velero
fi

read -p "Enter S3 Bucket Name for Velero: " VELERO_BUCKET
read -p "Enter AWS Region for Velero (default: us-east-1): " VELERO_REGION
VELERO_REGION=${VELERO_REGION:-us-east-1}

helm upgrade --install velero charts/backup-restore/velero \
    --namespace $NAMESPACE \
    --set secrets.name=velero-credentials \
    --set config.bucket=$VELERO_BUCKET \
    --set config.region=$VELERO_REGION \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment velero $NAMESPACE
print_success "Velero deployed successfully"

print_info "Deploying Argo Workflows..."
if ! oc get secret argo-workflows-secret -n $NAMESPACE &> /dev/null; then
    read -p "Enter S3 Access Key for Argo Workflows: " ARGO_ACCESS_KEY
    read -sp "Enter S3 Secret Key for Argo Workflows: " ARGO_SECRET_KEY
    echo
    oc create secret generic argo-workflows-secret \
        --from-literal=accesskey="$ARGO_ACCESS_KEY" \
        --from-literal=secretkey="$ARGO_SECRET_KEY" \
        -n $NAMESPACE
fi

read -p "Enter S3 Bucket Name for Argo Workflows: " ARGO_BUCKET

helm upgrade --install argo-workflows charts/backup-restore/argo-workflows \
    --namespace $NAMESPACE \
    --set secrets.name=argo-workflows-secret \
    --set config.artifactBucket=$ARGO_BUCKET \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment argo-workflows-server $NAMESPACE
print_success "Argo Workflows deployed successfully"

# ============================================================================
# PHASE 5: E-COMMERCE APPLICATION
# ============================================================================
print_info "=========================================="
print_info "PHASE 5: Deploying E-commerce Application"
print_info "=========================================="

print_info "Deploying Backend..."
helm upgrade --install backend charts/ecommerce-app/backend \
    --namespace $NAMESPACE \
    --set config.databaseUrl=postgresql://postgres:password@postgresql:5432/ecommerce \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment backend $NAMESPACE
print_success "Backend deployed successfully"

print_info "Deploying Frontend..."
helm upgrade --install frontend charts/ecommerce-app/frontend \
    --namespace $NAMESPACE \
    --set config.backendUrl=http://backend:8000 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment frontend $NAMESPACE

# Create route for frontend
if ! oc get route frontend -n $NAMESPACE &> /dev/null; then
    oc expose svc/frontend -n $NAMESPACE
    print_success "Frontend route created"
fi
print_success "Frontend deployed successfully"

print_info "Deploying Chat-UI..."
helm upgrade --install chat-ui charts/ecommerce-app/chat-ui \
    --namespace $NAMESPACE \
    --set config.backendUrl=http://backend:8000 \
    --set config.supervisorUrl=http://supervisor-agent:8080 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment chat-ui $NAMESPACE

# Create route for chat-ui
if ! oc get route chat-ui -n $NAMESPACE &> /dev/null; then
    oc expose svc/chat-ui -n $NAMESPACE
    print_success "Chat-UI route created"
fi
print_success "Chat-UI deployed successfully"

# ============================================================================
# PHASE 6: AI AGENTS
# ============================================================================
print_info "=========================================="
print_info "PHASE 6: Deploying AI Agents"
print_info "=========================================="

print_info "Deploying Supervisor Agent..."
helm upgrade --install supervisor-agent charts/ai-agents/supervisor-agent \
    --namespace $NAMESPACE \
    --set secrets.name=ai-agents-secret \
    --set config.llmProvider=openai \
    --set config.llmModel=gpt-4 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment supervisor-agent $NAMESPACE
print_success "Supervisor Agent deployed successfully"

print_info "Deploying Observability Agent..."
helm upgrade --install observability-agent charts/ai-agents/observability-agent \
    --namespace $NAMESPACE \
    --set secrets.name=ai-agents-secret \
    --set config.prometheusUrl=http://prometheus:9090 \
    --set config.grafanaUrl=http://grafana:3000 \
    --set config.lokiUrl=http://loki:3100 \
    --set config.supervisorUrl=http://supervisor-agent:8080 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment observability-agent $NAMESPACE
print_success "Observability Agent deployed successfully"

print_info "Deploying Pod Recovery Agent..."
helm upgrade --install pod-recovery-agent charts/ai-agents/pod-recovery-agent \
    --namespace $NAMESPACE \
    --set secrets.name=ai-agents-secret \
    --set config.prometheusUrl=http://prometheus:9090 \
    --set config.supervisorUrl=http://supervisor-agent:8080 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment pod-recovery-agent $NAMESPACE
print_success "Pod Recovery Agent deployed successfully"

print_info "Deploying Backup/Restore Agent..."
helm upgrade --install backup-restore-agent charts/ai-agents/backup-restore-agent \
    --namespace $NAMESPACE \
    --set secrets.name=ai-agents-secret \
    --set config.veleroNamespace=$NAMESPACE \
    --set config.argoWorkflowsNamespace=$NAMESPACE \
    --set config.supervisorUrl=http://supervisor-agent:8080 \
    --timeout $HELM_TIMEOUT \
    --wait

wait_for_deployment backup-restore-agent $NAMESPACE
print_success "Backup/Restore Agent deployed successfully"

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================
print_info "=========================================="
print_info "DEPLOYMENT SUMMARY"
print_info "=========================================="

print_success "All components deployed successfully!"
echo ""

print_info "Getting deployment status..."
oc get pods -n $NAMESPACE

echo ""
print_info "Getting routes..."
oc get routes -n $NAMESPACE

echo ""
print_info "Access URLs:"
FRONTEND_URL=$(oc get route frontend -n $NAMESPACE -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not exposed")
CHAT_UI_URL=$(oc get route chat-ui -n $NAMESPACE -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not exposed")

echo -e "${GREEN}Frontend:${NC} https://$FRONTEND_URL"
echo -e "${GREEN}Chat-UI:${NC} https://$CHAT_UI_URL"

echo ""
print_info "To access Grafana locally:"
echo "  oc port-forward svc/grafana 3000:3000 -n $NAMESPACE"
echo "  Then open: http://localhost:3000"

echo ""
print_info "To access Prometheus locally:"
echo "  oc port-forward svc/prometheus 9090:9090 -n $NAMESPACE"
echo "  Then open: http://localhost:9090"

echo ""
print_info "To access Argo Workflows locally:"
echo "  oc port-forward svc/argo-workflows-server 2746:2746 -n $NAMESPACE"
echo "  Then open: http://localhost:2746"

echo ""
print_success "Deployment complete! Check the deployment-guide.md for more details."

# Made with Bob
