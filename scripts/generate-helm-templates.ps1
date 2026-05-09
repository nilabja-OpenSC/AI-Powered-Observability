# PowerShell script to generate missing Helm chart templates
# This creates standard Kubernetes manifests for all charts

Write-Host "🚀 Generating missing Helm chart templates..." -ForegroundColor Green

# Function to create templates directory
function Create-TemplatesDir {
    param($ChartPath)
    $TemplatesPath = Join-Path $ChartPath "templates"
    if (-not (Test-Path $TemplatesPath)) {
        New-Item -ItemType Directory -Path $TemplatesPath -Force | Out-Null
        Write-Host "✅ Created templates directory: $TemplatesPath" -ForegroundColor Green
    }
}

# Function to create _helpers.tpl
function Create-Helpers {
    param($ChartPath, $ChartName)
    
    $Content = @"
{{/*
Expand the name of the chart.
*/}}
{{- define "$ChartName.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "$ChartName.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- `$name := default .Chart.Name .Values.nameOverride }}
{{- if contains `$name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name `$name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "$ChartName.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "$ChartName.labels" -}}
helm.sh/chart: {{ include "$ChartName.chart" . }}
{{ include "$ChartName.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "$ChartName.selectorLabels" -}}
app.kubernetes.io/name: {{ include "$ChartName.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: $ChartName
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "$ChartName.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "$ChartName.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\_helpers.tpl"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created _helpers.tpl for $ChartName" -ForegroundColor Green
}

# Function to create deployment.yaml
function Create-Deployment {
    param($ChartPath, $ChartName)
    
    $Content = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "$ChartName.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "$ChartName.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print `$.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "$ChartName.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "$ChartName.serviceAccountName" . }}
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
        {{- range `$key, `$value := .Values.env }}
        - name: {{ `$key }}
          value: {{ `$value | quote }}
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
"@
    
    $FilePath = Join-Path $ChartPath "templates\deployment.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created deployment.yaml for $ChartName" -ForegroundColor Green
}

# Function to create service.yaml
function Create-Service {
    param($ChartPath, $ChartName)
    
    $Content = @"
apiVersion: v1
kind: Service
metadata:
  name: {{ include "$ChartName.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: http
    protocol: TCP
    name: http
  selector:
    {{- include "$ChartName.selectorLabels" . | nindent 4 }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\service.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created service.yaml for $ChartName" -ForegroundColor Green
}

# Function to create configmap.yaml
function Create-ConfigMap {
    param($ChartPath, $ChartName)
    
    $Content = @"
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "$ChartName.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
data:
  {{- range `$key, `$value := .Values.env }}
  {{ `$key }}: {{ `$value | quote }}
  {{- end }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\configmap.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created configmap.yaml for $ChartName" -ForegroundColor Green
}

# Function to create servicemonitor.yaml
function Create-ServiceMonitor {
    param($ChartPath, $ChartName)
    
    $Content = @"
{{- if .Values.serviceMonitor.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "$ChartName.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- include "$ChartName.selectorLabels" . | nindent 6 }}
  endpoints:
  - port: http
    path: /metrics
    interval: {{ .Values.serviceMonitor.interval }}
    scrapeTimeout: {{ .Values.serviceMonitor.scrapeTimeout }}
{{- end }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\servicemonitor.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created servicemonitor.yaml for $ChartName" -ForegroundColor Green
}

# Function to create serviceaccount.yaml
function Create-ServiceAccount {
    param($ChartPath, $ChartName)
    
    $Content = @"
{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "$ChartName.serviceAccountName" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\serviceaccount.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created serviceaccount.yaml for $ChartName" -ForegroundColor Green
}

# Function to create role.yaml
function Create-Role {
    param($ChartPath, $ChartName)
    
    $Content = @"
{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "$ChartName.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
{{- end }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\role.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created role.yaml for $ChartName" -ForegroundColor Green
}

# Function to create rolebinding.yaml
function Create-RoleBinding {
    param($ChartPath, $ChartName)
    
    $Content = @"
{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "$ChartName.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: {{ include "$ChartName.fullname" . }}
subjects:
- kind: ServiceAccount
  name: {{ include "$ChartName.serviceAccountName" . }}
  namespace: {{ .Values.namespace }}
{{- end }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\rolebinding.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created rolebinding.yaml for $ChartName" -ForegroundColor Green
}

# Function to create secret.yaml
function Create-Secret {
    param($ChartPath, $ChartName)
    
    $Content = @"
{{- if .Values.secrets }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "$ChartName.fullname" . }}
  namespace: {{ .Values.namespace }}
  labels:
    {{- include "$ChartName.labels" . | nindent 4 }}
type: Opaque
data:
  {{- range `$key, `$value := .Values.secrets }}
  {{ `$key }}: {{ `$value | b64enc | quote }}
  {{- end }}
{{- end }}
"@
    
    $FilePath = Join-Path $ChartPath "templates\secret.yaml"
    $Content | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "✅ Created secret.yaml for $ChartName" -ForegroundColor Green
}

# Function to process a chart
function Process-Chart {
    param($ChartPath, $ChartName)
    
    Write-Host ""
    Write-Host "📦 Processing chart: $ChartName" -ForegroundColor Cyan
    Write-Host "   Path: $ChartPath" -ForegroundColor Gray
    
    $TemplatesPath = Join-Path $ChartPath "templates"
    if (-not (Test-Path $TemplatesPath)) {
        Create-TemplatesDir $ChartPath
        Create-Helpers $ChartPath $ChartName
        Create-Deployment $ChartPath $ChartName
        Create-Service $ChartPath $ChartName
        Create-ConfigMap $ChartPath $ChartName
        Create-ServiceMonitor $ChartPath $ChartName
        Create-ServiceAccount $ChartPath $ChartName
        Create-Role $ChartPath $ChartName
        Create-RoleBinding $ChartPath $ChartName
        Create-Secret $ChartPath $ChartName
    } else {
        Write-Host "⏭️  Templates directory already exists, skipping..." -ForegroundColor Yellow
    }
}

# E-commerce charts
Write-Host ""
Write-Host "=== E-commerce Application Charts ===" -ForegroundColor Magenta
Process-Chart "charts\ecommerce-app\frontend" "frontend"
Process-Chart "charts\ecommerce-app\chat-ui" "chat-ui"

# AI Agent charts
Write-Host ""
Write-Host "=== AI Agent Charts ===" -ForegroundColor Magenta
Process-Chart "charts\ai-agents\supervisor-agent" "supervisor-agent"
Process-Chart "charts\ai-agents\observability-agent" "observability-agent"
Process-Chart "charts\ai-agents\pod-recovery-agent" "pod-recovery-agent"
Process-Chart "charts\ai-agents\backup-restore-agent" "backup-restore-agent"

Write-Host ""
Write-Host "✅ All Helm chart templates generated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review generated templates in each chart's templates\ directory"
Write-Host "2. Customize templates as needed for your specific requirements"
Write-Host "3. Test charts with: helm template <chart-name> .\charts\<path-to-chart>"
Write-Host "4. Deploy with: helm install <release-name> .\charts\<path-to-chart>"

# Made with Bob
