#!/bin/bash

# Script to generate missing Helm chart templates
# This creates standard Kubernetes manifests for all charts

set -e

echo "🚀 Generating missing Helm chart templates..."

# Function to create templates directory
create_templates_dir() {
    local chart_path=$1
    mkdir -p "$chart_path/templates"
    echo "✅ Created templates directory: $chart_path/templates"
}

# Function to create _helpers.tpl
create_helpers() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/_helpers.tpl" <<'EOF'
{{/*
Expand the name of the chart.
*/}}
{{- define "CHART_NAME.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "CHART_NAME.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "CHART_NAME.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "CHART_NAME.labels" -}}
helm.sh/chart: {{ include "CHART_NAME.chart" . }}
{{ include "CHART_NAME.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "CHART_NAME.selectorLabels" -}}
app.kubernetes.io/name: {{ include "CHART_NAME.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: CHART_NAME
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "CHART_NAME.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "CHART_NAME.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
EOF
    
    # Replace CHART_NAME with actual chart name
    sed -i "s/CHART_NAME/$chart_name/g" "$chart_path/templates/_helpers.tpl"
    echo "✅ Created _helpers.tpl for $chart_name"
}

# Function to create deployment.yaml
create_deployment() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/deployment.yaml" <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "$chart_name.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "$chart_name.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print \$.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "$chart_name.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "$chart_name.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        securityContext:
          {{- toYaml .Values.securityContext | nindent 12 }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.port }}
          protocol: TCP
        {{- if .Values.env }}
        env:
        {{- range \$key, \$value := .Values.env }}
        - name: {{ \$key }}
          value: {{ \$value | quote }}
        {{- end }}
        {{- end }}
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
EOF
    echo "✅ Created deployment.yaml for $chart_name"
}

# Function to create service.yaml
create_service() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/service.yaml" <<EOF
apiVersion: v1
kind: Service
metadata:
  name: {{ include "$chart_name.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: http
    protocol: TCP
    name: http
  selector:
    {{- include "$chart_name.selectorLabels" . | nindent 4 }}
EOF
    echo "✅ Created service.yaml for $chart_name"
}

# Function to create configmap.yaml
create_configmap() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/configmap.yaml" <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "$chart_name.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
data:
  {{- range \$key, \$value := .Values.env }}
  {{ \$key }}: {{ \$value | quote }}
  {{- end }}
EOF
    echo "✅ Created configmap.yaml for $chart_name"
}

# Function to create servicemonitor.yaml
create_servicemonitor() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/servicemonitor.yaml" <<EOF
{{- if .Values.serviceMonitor.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "$chart_name.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- include "$chart_name.selectorLabels" . | nindent 6 }}
  endpoints:
  - port: http
    path: /metrics
    interval: {{ .Values.serviceMonitor.interval }}
    scrapeTimeout: {{ .Values.serviceMonitor.scrapeTimeout }}
{{- end }}
EOF
    echo "✅ Created servicemonitor.yaml for $chart_name"
}

# Function to create serviceaccount.yaml
create_serviceaccount() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/serviceaccount.yaml" <<EOF
{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "$chart_name.serviceAccountName" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
EOF
    echo "✅ Created serviceaccount.yaml for $chart_name"
}

# Function to create role.yaml
create_role() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/role.yaml" <<EOF
{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "$chart_name.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
{{- end }}
EOF
    echo "✅ Created role.yaml for $chart_name"
}

# Function to create rolebinding.yaml
create_rolebinding() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/rolebinding.yaml" <<EOF
{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "$chart_name.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: {{ include "$chart_name.fullname" . }}
subjects:
- kind: ServiceAccount
  name: {{ include "$chart_name.serviceAccountName" . }}
  namespace: {{ .Values.namespace }}
{{- end }}
EOF
    echo "✅ Created rolebinding.yaml for $chart_name"
}

# Function to create secret.yaml
create_secret() {
    local chart_path=$1
    local chart_name=$2
    
    cat > "$chart_path/templates/secret.yaml" <<EOF
{{- if .Values.secrets }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "$chart_name.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$chart_name.labels" . | nindent 4 }}
type: Opaque
data:
  {{- range \$key, \$value := .Values.secrets }}
  {{ \$key }}: {{ \$value | b64enc | quote }}
  {{- end }}
{{- end }}
EOF
    echo "✅ Created secret.yaml for $chart_name"
}

# Function to process a chart
process_chart() {
    local chart_path=$1
    local chart_name=$2
    
    echo ""
    echo "📦 Processing chart: $chart_name"
    echo "   Path: $chart_path"
    
    # Check if templates directory exists
    if [ ! -d "$chart_path/templates" ]; then
        create_templates_dir "$chart_path"
        create_helpers "$chart_path" "$chart_name"
        create_deployment "$chart_path" "$chart_name"
        create_service "$chart_path" "$chart_name"
        create_configmap "$chart_path" "$chart_name"
        create_servicemonitor "$chart_path" "$chart_name"
        create_serviceaccount "$chart_path" "$chart_name"
        create_role "$chart_path" "$chart_name"
        create_rolebinding "$chart_path" "$chart_name"
        create_secret "$chart_path" "$chart_name"
    else
        echo "⏭️  Templates directory already exists, skipping..."
    fi
}

# E-commerce charts
echo ""
echo "=== E-commerce Application Charts ==="
process_chart "charts/ecommerce-app/frontend" "frontend"
process_chart "charts/ecommerce-app/chat-ui" "chat-ui"

# AI Agent charts
echo ""
echo "=== AI Agent Charts ==="
process_chart "charts/ai-agents/supervisor-agent" "supervisor-agent"
process_chart "charts/ai-agents/observability-agent" "observability-agent"
process_chart "charts/ai-agents/pod-recovery-agent" "pod-recovery-agent"
process_chart "charts/ai-agents/backup-restore-agent" "backup-restore-agent"

echo ""
echo "✅ All Helm chart templates generated successfully!"
echo ""
echo "Next steps:"
echo "1. Review generated templates in each chart's templates/ directory"
echo "2. Customize templates as needed for your specific requirements"
echo "3. Test charts with: helm template <chart-name> ./charts/<path-to-chart>"
echo "4. Deploy with: helm install <release-name> ./charts/<path-to-chart>"

# Made with Bob
