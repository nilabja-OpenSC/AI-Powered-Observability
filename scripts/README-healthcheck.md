# Kubernetes Cluster Health Check Script

## Overview

The `k8s-cluster-healthcheck.sh` script performs comprehensive health checks on Kubernetes clusters, focusing on:

1. **Node Scheduling Status** - Identifies cordoned nodes, duration, and pod distribution
2. **Pod Error Detection** - Analyzes all pod errors with detailed diagnostics

**Key Features**:
- ✅ **Required cluster name** - Ensures you're checking the correct cluster
- ✅ **Dry-run mode** - Preview actions without executing commands
- ✅ **Automatic context switching** - Switches to matching cluster context

## Features

### Task 1: Node Analysis
- ✅ Checks if nodes are schedulable or cordoned
- ✅ Calculates how many days nodes have been cordoned
- ✅ Lists all pods running on each node
- ✅ Groups pods by namespace
- ✅ Provides pod status summaries

### Task 2: Pod Error Analysis
- ✅ Detects pods in error states (Error, CrashLoopBackOff, ImagePullBackOff, etc.)
- ✅ Categorizes different error types
- ✅ Provides detailed diagnostics for each error:
  - **CrashLoopBackOff**: Container logs, restart count
  - **ImagePullBackOff**: Image name, pull error details
  - **Error**: Exit code, reason, logs
  - **Pending**: Scheduling issues, resource constraints
  - **ContainerCreating**: Creation time, events
- ✅ Generates error summary report

## Usage

### Basic Usage

```bash
# Check entire cluster (cluster name REQUIRED)
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster

# Dry-run mode (show what would be executed)
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster --dry-run

# Check specific namespace
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster -n production

# Save output to file
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster -o healthcheck.log

# Verbose output with all pod details
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster -v

# Combine options
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster -n production -o prod-check.log -v

# Dry-run with output file
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster -d -o dry-run.log
```

### Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `-c, --cluster <name>` | Cluster name | **YES** |
| `-n, --namespace <namespace>` | Check specific namespace only | No |
| `-o, --output <file>` | Save output to file | No |
| `-d, --dry-run` | Dry-run mode (show actions without executing) | No |
| `-v, --verbose` | Show detailed pod information | No |
| `-h, --help` | Display help message | No |

## Prerequisites

1. **kubectl** must be installed and configured
2. **Cluster access** with appropriate RBAC permissions
3. **Bash shell** (Linux/macOS/WSL)
4. **Cluster context** configured in kubectl (script will auto-switch if name matches)

### Required Permissions

The script requires the following Kubernetes permissions:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-healthcheck
rules:
- apiGroups: [""]
  resources:
    - nodes
    - pods
    - pods/log
    - events
  verbs:
    - get
    - list
- apiGroups: [""]
  resources:
    - pods/status
  verbs:
    - get
```

## Cluster Name Requirement

The script **requires** a cluster name to be specified with `-c` or `--cluster`. This ensures:

1. **Safety**: Prevents accidental execution on wrong cluster
2. **Context Verification**: Validates kubectl context matches cluster name
3. **Auto-Switching**: Automatically switches to matching context if available
4. **Audit Trail**: Logs clearly show which cluster was checked

### Error Handling

```bash
# Missing cluster name - will exit with error
$ ./scripts/k8s-cluster-healthcheck.sh
✗ Cluster name is required!

Usage: ./scripts/k8s-cluster-healthcheck.sh -c <cluster-name> [OPTIONS]
```

### Context Matching

The script will:
1. Check if current context contains the cluster name
2. If not, search for a context matching the cluster name
3. Automatically switch to the matching context
4. Exit with error if no matching context found

```bash
# Example: Switching contexts
$ ./scripts/k8s-cluster-healthcheck.sh -c production
⚠ Current context 'dev-cluster' may not match cluster 'production'
ℹ Attempting to switch to cluster context...
✓ Switched to context: production-cluster
✓ Connected to Kubernetes cluster: production
```

## Dry-Run Mode

Use `--dry-run` or `-d` to preview what the script would do **without executing any commands**.

### Dry-Run Output Example

```bash
$ ./scripts/k8s-cluster-healthcheck.sh -c prod-cluster --dry-run

========================================
Health Check Configuration
========================================

ℹ Cluster: prod-cluster
ℹ Namespace: All namespaces
ℹ Dry-run mode: true
ℹ Verbose: false

========================================
Checking Cluster Connectivity
========================================

[DRY-RUN] Would check connectivity to cluster: prod-cluster
[DRY-RUN] Would execute: kubectl cluster-info
[DRY-RUN] Would verify cluster context matches: prod-cluster

========================================
TASK 1: Node Scheduling Status Analysis
========================================

[DRY-RUN] Would execute: kubectl get nodes --no-headers -o custom-columns=NAME:.metadata.name
[DRY-RUN] Would analyze each node for:
[DRY-RUN]   - Node status (Ready/NotReady)
[DRY-RUN]   - Scheduling status (Enabled/Disabled)
[DRY-RUN]   - Cordon duration calculation
[DRY-RUN]   - Pod distribution per node
[DRY-RUN]   - Namespace grouping

========================================
TASK 2: Pod Error Detection and Analysis
========================================

[DRY-RUN] Would execute: kubectl get pods -A --no-headers
[DRY-RUN] Would filter for error states: Error, CrashLoopBackOff, ImagePullBackOff, etc.
[DRY-RUN] Would analyze each error pod for:
[DRY-RUN]   - Error type categorization
[DRY-RUN]   - Container logs retrieval
[DRY-RUN]   - Exit codes and reasons
[DRY-RUN]   - Pod events and descriptions
[DRY-RUN]   - Resource constraints

========================================
Health Check Summary
========================================

[DRY-RUN] Would execute: kubectl get nodes --no-headers | wc -l
[DRY-RUN] Would execute: kubectl get pods -A --no-headers | wc -l
[DRY-RUN] Would calculate:
[DRY-RUN]   - Total nodes, ready nodes, cordoned nodes
[DRY-RUN]   - Total pods, running pods, pods with issues
[DRY-RUN]   - Overall cluster health status

ℹ Dry-run mode completed successfully
ℹ Cluster: prod-cluster
ℹ No actual commands were executed

ℹ Health check completed at: 2024-05-13 12:30:00
ℹ Cluster: prod-cluster
ℹ Mode: DRY-RUN (no commands executed)
```

### When to Use Dry-Run

- **Testing**: Verify script behavior before actual execution
- **Documentation**: Generate command list for manual execution
- **Auditing**: Review what commands would be run
- **Training**: Show team members what the script does
- **CI/CD**: Validate script in pipeline without affecting cluster

## Output Format

### Configuration Display

```
========================================
Health Check Configuration
========================================

ℹ Cluster: prod-cluster
ℹ Namespace: production
ℹ Dry-run mode: false
ℹ Verbose: true
ℹ Output file: healthcheck.log
```

### Node Analysis Output

```
========================================
TASK 1: Node Scheduling Status Analysis
========================================

ℹ Total nodes in cluster: 3

ℹ Analyzing node: worker-node-1
----------------------------------------
✓ Node Status: Ready
✓ Scheduling: ENABLED

ℹ Pods running on node worker-node-1:
ℹ   Total pods: 15

  ℹ Namespace: kube-system
    Pod count: 5
    Status summary:
      Running: 5

  ℹ Namespace: production
    Pod count: 10
    Status summary:
      Running: 9
      CrashLoopBackOff: 1
```

### Pod Error Analysis Output

```
========================================
TASK 2: Pod Error Detection and Analysis
========================================

⚠ Found 3 pod(s) with issues

✗ Pod: production/backend-api-7d8f9c-xyz
  Status: CrashLoopBackOff
  ✗ Error Type: CrashLoopBackOff
  Description: Container is crashing repeatedly
  Recent logs:
    Error: Cannot connect to database
    Connection refused at 10.0.0.5:5432
  Restart count: 15
  Age: 2024-05-13T10:30:00Z
  Node: worker-node-2
```

### Summary Report

```
========================================
Health Check Summary
========================================

Nodes:
  Total: 3
  Ready: 3
  Cordoned: 0

Pods:
  Total: 45
  Running: 42
  With Issues: 3

✓ Cluster Health: DEGRADED (Pod issues detected)

ℹ Health check completed at: 2024-05-13 12:30:00
```

## Error Types Detected

| Error Type | Description | Diagnostics Provided |
|------------|-------------|---------------------|
| **CrashLoopBackOff** | Container crashes repeatedly | Logs, restart count, previous logs |
| **ImagePullBackOff** | Cannot pull container image | Image name, pull error details |
| **ErrImagePull** | Image pull failed | Image name, error message |
| **Error** | Generic container error | Exit code, reason, logs |
| **Pending** | Pod waiting to be scheduled | Scheduling issues, resource constraints |
| **ContainerCreating** | Container stuck creating | Creation time, events |
| **Unknown** | Unknown pod state | Pod events, description |

## Examples

### Example 1: Dry-Run Before Execution

```bash
# First, dry-run to see what will be executed
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster --dry-run

# If satisfied, run actual check
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster
```

### Example 2: Check Production Namespace

```bash
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster -n production -o prod-health.log
```

**Output**: Analyzes only production namespace and saves to `prod-health.log`

### Example 3: Full Cluster Check with Verbose Output

```bash
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster -v -o cluster-health-$(date +%Y%m%d).log
```

**Output**: Complete cluster analysis with all pod details, saved to dated log file

### Example 4: Quick Error Check

```bash
./scripts/k8s-cluster-healthcheck.sh -c prod-cluster | grep -A 10 "Pod Error"
```

**Output**: Shows only pod errors from the health check

### Example 5: Multiple Clusters

```bash
# Check multiple clusters in sequence
for cluster in prod-cluster staging-cluster dev-cluster; do
    echo "Checking $cluster..."
    ./scripts/k8s-cluster-healthcheck.sh -c $cluster -o ${cluster}-health.log
done
```

## Troubleshooting

### Issue: "Cluster name is required"

**Solution**: Always provide cluster name with `-c` flag
```bash
./scripts/k8s-cluster-healthcheck.sh -c your-cluster-name
```

### Issue: "No context found matching cluster name"

**Solution**: List available contexts and use exact name
```bash
# List contexts
kubectl config get-contexts

# Use matching context name
./scripts/k8s-cluster-healthcheck.sh -c <context-name>
```

### Issue: "kubectl not found"

**Solution**: Install kubectl
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### Issue: "Cannot connect to Kubernetes cluster"

**Solution**: Configure kubectl context
```bash
# List available contexts
kubectl config get-contexts

# Set context
kubectl config use-context <context-name>

# Verify connection
kubectl cluster-info
```

### Issue: "Permission denied" when running script

**Solution**: Make script executable
```bash
chmod +x scripts/k8s-cluster-healthcheck.sh
```

### Issue: "Insufficient permissions"

**Solution**: Ensure your service account has required RBAC permissions (see Prerequisites section)

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Cluster Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  healthcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
      
      - name: Run Health Check
        run: |
          chmod +x scripts/k8s-cluster-healthcheck.sh
          ./scripts/k8s-cluster-healthcheck.sh -o healthcheck-$(date +%Y%m%d-%H%M%S).log
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: healthcheck-report
          path: healthcheck-*.log
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    triggers {
        cron('H */6 * * *')  // Every 6 hours
    }
    
    stages {
        stage('Health Check') {
            steps {
                script {
                    sh '''
                        chmod +x scripts/k8s-cluster-healthcheck.sh
                        ./scripts/k8s-cluster-healthcheck.sh -o healthcheck-${BUILD_NUMBER}.log
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'healthcheck-*.log', fingerprint: true
            }
        }
    }
}
```

## Monitoring Integration

### Prometheus Alert Example

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: cluster-health-alerts
spec:
  groups:
  - name: cluster-health
    interval: 5m
    rules:
    - alert: PodsInCrashLoop
      expr: kube_pod_container_status_restarts_total > 5
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping"
        description: "Run: ./scripts/k8s-cluster-healthcheck.sh -n {{ $labels.namespace }}"
```

## Best Practices

1. **Regular Checks**: Run health checks at least daily
2. **Namespace Isolation**: Check critical namespaces separately
3. **Log Retention**: Keep health check logs for at least 30 days
4. **Alerting**: Integrate with monitoring systems for automated alerts
5. **Documentation**: Document any recurring issues found

## Advanced Usage

### Custom Error Detection

Modify the script to detect custom error patterns:

```bash
# Add to ERROR_PODS detection
ERROR_PODS=$(kubectl get pods -A --no-headers 2>/dev/null | \
    grep -E "Error|CrashLoopBackOff|YourCustomError" || echo "")
```

### Export to JSON

```bash
# Pipe output through jq for JSON formatting
./scripts/k8s-cluster-healthcheck.sh | \
    grep -A 20 "Pod:" | \
    # Custom parsing to JSON
```

## Contributing

To add new features or error detection:

1. Add error pattern to `ERROR_PODS` grep
2. Add case statement in error analysis section
3. Update this README with new error type
4. Test with sample pods in error state

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Create an issue in the repository
- Contact: observability@example.com

---

**Last Updated**: 2026-05-13
**Version**: 1.0.0
**Maintainer**: AI-Powered Observability Team