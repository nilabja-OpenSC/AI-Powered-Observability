#!/bin/bash

################################################################################
# Kubernetes Cluster Health Check Script
#
# This script performs comprehensive health checks on a Kubernetes cluster:
# 1. Node scheduling status and pod distribution
# 2. Pod error detection and analysis
#
# Usage: ./k8s-cluster-healthcheck.sh -c <cluster-name> [OPTIONS]
# Options:
#   -c, --cluster <name>         Cluster name (REQUIRED)
#   -n, --namespace <namespace>  Check specific namespace only
#   -o, --output <file>          Save output to file
#   -d, --dry-run                Dry-run mode (show actions without executing)
#   -v, --verbose                Verbose output
#   -h, --help                   Show this help message
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default values
CLUSTER_NAME=""
NAMESPACE=""
OUTPUT_FILE=""
VERBOSE=false
DRY_RUN=false
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to print dry-run action
print_dry_run() {
    echo -e "${MAGENTA}[DRY-RUN] $1${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Kubernetes Cluster Health Check Script

Usage: $0 -c <cluster-name> [OPTIONS]

Required:
    -c, --cluster <name>         Cluster name (REQUIRED)

Options:
    -n, --namespace <namespace>  Check specific namespace only
    -o, --output <file>          Save output to file
    -d, --dry-run                Dry-run mode (show actions without executing)
    -v, --verbose                Verbose output
    -h, --help                   Show this help message

Examples:
    $0 -c prod-cluster                              # Check prod cluster
    $0 -c prod-cluster -n production                # Check production namespace
    $0 -c prod-cluster -o healthcheck.log           # Save output to file
    $0 -c prod-cluster -d                           # Dry-run mode
    $0 -c prod-cluster -n production -o prod.log    # Combined options

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--cluster)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$CLUSTER_NAME" ]]; then
    print_error "Cluster name is required!"
    echo ""
    show_usage
    exit 1
fi

# Redirect output to file if specified
if [[ -n "$OUTPUT_FILE" ]]; then
    exec > >(tee -a "$OUTPUT_FILE")
    exec 2>&1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl first."
    exit 1
fi

# Display configuration
print_header "Health Check Configuration"
print_info "Cluster: $CLUSTER_NAME"
print_info "Namespace: ${NAMESPACE:-All namespaces}"
print_info "Dry-run mode: $DRY_RUN"
print_info "Verbose: $VERBOSE"
if [[ -n "$OUTPUT_FILE" ]]; then
    print_info "Output file: $OUTPUT_FILE"
fi
echo ""

# Check cluster connectivity
print_header "Checking Cluster Connectivity"

if [[ "$DRY_RUN" == "true" ]]; then
    print_dry_run "Would check connectivity to cluster: $CLUSTER_NAME"
    print_dry_run "Would execute: kubectl cluster-info"
    print_dry_run "Would verify cluster context matches: $CLUSTER_NAME"
else
    # Verify cluster context
    CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "")
    
    if [[ -z "$CURRENT_CONTEXT" ]]; then
        print_error "No kubectl context set"
        exit 1
    fi
    
    # Check if current context matches cluster name
    if [[ "$CURRENT_CONTEXT" != *"$CLUSTER_NAME"* ]]; then
        print_warning "Current context '$CURRENT_CONTEXT' may not match cluster '$CLUSTER_NAME'"
        print_info "Attempting to switch to cluster context..."
        
        # Try to find and switch to matching context
        MATCHING_CONTEXT=$(kubectl config get-contexts -o name | grep -i "$CLUSTER_NAME" | head -1 || echo "")
        
        if [[ -n "$MATCHING_CONTEXT" ]]; then
            kubectl config use-context "$MATCHING_CONTEXT" &> /dev/null
            print_success "Switched to context: $MATCHING_CONTEXT"
        else
            print_error "No context found matching cluster name: $CLUSTER_NAME"
            print_info "Available contexts:"
            kubectl config get-contexts -o name | sed 's/^/  - /'
            exit 1
        fi
    fi
    
    if kubectl cluster-info &> /dev/null; then
        print_success "Connected to Kubernetes cluster: $CLUSTER_NAME"
        kubectl cluster-info | head -n 2
    else
        print_error "Cannot connect to Kubernetes cluster: $CLUSTER_NAME"
        exit 1
    fi
fi

################################################################################
# TASK 1: Node Scheduling Status Check
################################################################################

print_header "TASK 1: Node Scheduling Status Analysis"

if [[ "$DRY_RUN" == "true" ]]; then
    print_dry_run "Would execute: kubectl get nodes --no-headers -o custom-columns=NAME:.metadata.name"
    print_dry_run "Would analyze each node for:"
    print_dry_run "  - Node status (Ready/NotReady)"
    print_dry_run "  - Scheduling status (Enabled/Disabled)"
    print_dry_run "  - Cordon duration calculation"
    print_dry_run "  - Pod distribution per node"
    print_dry_run "  - Namespace grouping"
    echo ""
    print_info "Dry-run: Skipping actual node analysis"
else
    # Get all nodes
    NODES=$(kubectl get nodes --no-headers -o custom-columns=NAME:.metadata.name)

    if [[ -z "$NODES" ]]; then
        print_error "No nodes found in the cluster"
        exit 1
    fi

    NODE_COUNT=$(echo "$NODES" | wc -l)
    print_info "Total nodes in cluster: $NODE_COUNT"
fi

# Analyze each node (skip in dry-run)
if [[ "$DRY_RUN" == "false" ]]; then
for NODE in $NODES; do
    echo ""
    print_info "Analyzing node: $NODE"
    echo "----------------------------------------"
    
    # Get node status
    NODE_STATUS=$(kubectl get node "$NODE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    SCHEDULABLE=$(kubectl get node "$NODE" -o jsonpath='{.spec.unschedulable}')
    
    # Check if node is ready
    if [[ "$NODE_STATUS" == "True" ]]; then
        print_success "Node Status: Ready"
    else
        print_error "Node Status: Not Ready"
    fi
    
    # Check if scheduling is disabled
    if [[ "$SCHEDULABLE" == "true" ]]; then
        print_warning "Scheduling: DISABLED (Cordoned)"
        
        # Try to get when it was cordoned (from node annotations or events)
        CORDON_TIME=$(kubectl get node "$NODE" -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/cordon-time}' 2>/dev/null || echo "Unknown")
        
        if [[ "$CORDON_TIME" != "Unknown" ]]; then
            # Calculate days since cordoned
            CORDON_EPOCH=$(date -d "$CORDON_TIME" +%s 2>/dev/null || echo "0")
            CURRENT_EPOCH=$(date +%s)
            DAYS_CORDONED=$(( (CURRENT_EPOCH - CORDON_EPOCH) / 86400 ))
            print_warning "Cordoned for: $DAYS_CORDONED days (since $CORDON_TIME)"
        else
            # Try to get from events
            CORDON_EVENT=$(kubectl get events --field-selector involvedObject.name="$NODE" --sort-by='.lastTimestamp' | grep -i "cordon\|unschedulable" | tail -1 || echo "")
            if [[ -n "$CORDON_EVENT" ]]; then
                print_warning "Recent cordon event found:"
                echo "$CORDON_EVENT"
            else
                print_warning "Cordon time: Unknown (no annotation or event found)"
            fi
        fi
    else
        print_success "Scheduling: ENABLED"
    fi
    
    # Get pods running on this node
    echo ""
    print_info "Pods running on node $NODE:"
    
    if [[ -n "$NAMESPACE" ]]; then
        PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector spec.nodeName="$NODE" --no-headers 2>/dev/null || echo "")
    else
        PODS=$(kubectl get pods -A --field-selector spec.nodeName="$NODE" --no-headers 2>/dev/null || echo "")
    fi
    
    if [[ -z "$PODS" ]]; then
        print_info "  No pods running on this node"
    else
        POD_COUNT=$(echo "$PODS" | wc -l)
        print_info "  Total pods: $POD_COUNT"
        
        # Group pods by namespace
        if [[ -n "$NAMESPACE" ]]; then
            NAMESPACES="$NAMESPACE"
        else
            NAMESPACES=$(echo "$PODS" | awk '{print $1}' | sort -u)
        fi
        
        for NS in $NAMESPACES; do
            echo ""
            print_info "  Namespace: $NS"
            
            if [[ -n "$NAMESPACE" ]]; then
                NS_PODS=$(kubectl get pods -n "$NS" --field-selector spec.nodeName="$NODE" --no-headers)
            else
                NS_PODS=$(echo "$PODS" | grep "^$NS ")
            fi
            
            NS_POD_COUNT=$(echo "$NS_PODS" | wc -l)
            echo "    Pod count: $NS_POD_COUNT"
            
            if [[ "$VERBOSE" == "true" ]]; then
                echo "    Pods:"
                echo "$NS_PODS" | awk '{printf "      - %s (Status: %s)\n", $2, $3}'
            else
                # Show summary by status
                echo "    Status summary:"
                echo "$NS_PODS" | awk '{print $3}' | sort | uniq -c | awk '{printf "      %s: %d\n", $2, $1}'
            fi
        done
    fi
    
    echo ""
done
fi

################################################################################
# TASK 2: Pod Error Detection and Analysis
################################################################################

print_header "TASK 2: Pod Error Detection and Analysis"

# Get all pods with errors
if [[ -n "$NAMESPACE" ]]; then
    ERROR_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -E "Error|CrashLoopBackOff|ImagePullBackOff|ErrImagePull|Pending|Unknown|Terminating|ContainerCreating" || echo "")
else
    ERROR_PODS=$(kubectl get pods -A --no-headers 2>/dev/null | grep -E "Error|CrashLoopBackOff|ImagePullBackOff|ErrImagePull|Pending|Unknown|Terminating|ContainerCreating" || echo "")
fi

if [[ -z "$ERROR_PODS" ]]; then
    print_success "No pods with errors found!"
else
    ERROR_COUNT=$(echo "$ERROR_PODS" | wc -l)
    print_warning "Found $ERROR_COUNT pod(s) with issues"
    
    # Categorize errors
    declare -A ERROR_CATEGORIES
    
    while IFS= read -r POD_LINE; do
        if [[ -n "$NAMESPACE" ]]; then
            POD_NS="$NAMESPACE"
            POD_NAME=$(echo "$POD_LINE" | awk '{print $1}')
            POD_STATUS=$(echo "$POD_LINE" | awk '{print $3}')
        else
            POD_NS=$(echo "$POD_LINE" | awk '{print $1}')
            POD_NAME=$(echo "$POD_LINE" | awk '{print $2}')
            POD_STATUS=$(echo "$POD_LINE" | awk '{print $4}')
        fi
        
        # Increment error category count
        ERROR_CATEGORIES["$POD_STATUS"]=$((${ERROR_CATEGORIES["$POD_STATUS"]:-0} + 1))
        
        echo ""
        print_error "Pod: $POD_NS/$POD_NAME"
        echo "  Status: $POD_STATUS"
        
        # Get detailed error information
        case "$POD_STATUS" in
            *CrashLoopBackOff*)
                print_error "  Error Type: CrashLoopBackOff"
                echo "  Description: Container is crashing repeatedly"
                
                # Get container logs
                echo "  Recent logs:"
                kubectl logs -n "$POD_NS" "$POD_NAME" --tail=5 2>/dev/null | sed 's/^/    /' || echo "    (Unable to fetch logs)"
                
                # Get previous container logs if available
                echo "  Previous container logs:"
                kubectl logs -n "$POD_NS" "$POD_NAME" --previous --tail=5 2>/dev/null | sed 's/^/    /' || echo "    (No previous logs available)"
                
                # Get restart count
                RESTARTS=$(kubectl get pod -n "$POD_NS" "$POD_NAME" -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null || echo "Unknown")
                echo "  Restart count: $RESTARTS"
                ;;
                
            *ImagePullBackOff*|*ErrImagePull*)
                print_error "  Error Type: Image Pull Error"
                echo "  Description: Unable to pull container image"
                
                # Get image name
                IMAGE=$(kubectl get pod -n "$POD_NS" "$POD_NAME" -o jsonpath='{.spec.containers[0].image}' 2>/dev/null || echo "Unknown")
                echo "  Image: $IMAGE"
                
                # Get detailed error message
                ERROR_MSG=$(kubectl describe pod -n "$POD_NS" "$POD_NAME" 2>/dev/null | grep -A 5 "Failed to pull image" | sed 's/^/    /')
                if [[ -n "$ERROR_MSG" ]]; then
                    echo "  Error details:"
                    echo "$ERROR_MSG"
                fi
                ;;
                
            *Error*)
                print_error "  Error Type: Generic Error"
                
                # Get exit code and reason
                EXIT_CODE=$(kubectl get pod -n "$POD_NS" "$POD_NAME" -o jsonpath='{.status.containerStatuses[0].state.terminated.exitCode}' 2>/dev/null || echo "Unknown")
                REASON=$(kubectl get pod -n "$POD_NS" "$POD_NAME" -o jsonpath='{.status.containerStatuses[0].state.terminated.reason}' 2>/dev/null || echo "Unknown")
                
                echo "  Exit code: $EXIT_CODE"
                echo "  Reason: $REASON"
                
                # Get logs
                echo "  Recent logs:"
                kubectl logs -n "$POD_NS" "$POD_NAME" --tail=5 2>/dev/null | sed 's/^/    /' || echo "    (Unable to fetch logs)"
                ;;
                
            *Pending*)
                print_warning "  Error Type: Pending"
                echo "  Description: Pod is waiting to be scheduled"
                
                # Get pending reason
                PENDING_REASON=$(kubectl describe pod -n "$POD_NS" "$POD_NAME" 2>/dev/null | grep -A 3 "Events:" | grep "Warning" | tail -1 | sed 's/^/    /')
                if [[ -n "$PENDING_REASON" ]]; then
                    echo "  Reason:"
                    echo "$PENDING_REASON"
                fi
                
                # Check for resource constraints
                RESOURCE_ISSUE=$(kubectl describe pod -n "$POD_NS" "$POD_NAME" 2>/dev/null | grep -i "insufficient\|unschedulable" | sed 's/^/    /')
                if [[ -n "$RESOURCE_ISSUE" ]]; then
                    echo "  Resource constraints:"
                    echo "$RESOURCE_ISSUE"
                fi
                ;;
                
            *ContainerCreating*)
                print_warning "  Error Type: ContainerCreating"
                echo "  Description: Container is being created (may be stuck)"
                
                # Get creation time
                AGE=$(kubectl get pod -n "$POD_NS" "$POD_NAME" -o jsonpath='{.metadata.creationTimestamp}' 2>/dev/null || echo "Unknown")
                echo "  Created: $AGE"
                
                # Get events
                EVENTS=$(kubectl describe pod -n "$POD_NS" "$POD_NAME" 2>/dev/null | grep -A 5 "Events:" | tail -5 | sed 's/^/    /')
                if [[ -n "$EVENTS" ]]; then
                    echo "  Recent events:"
                    echo "$EVENTS"
                fi
                ;;
                
            *)
                print_warning "  Error Type: $POD_STATUS"
                
                # Get generic pod description
                echo "  Pod events:"
                kubectl describe pod -n "$POD_NS" "$POD_NAME" 2>/dev/null | grep -A 5 "Events:" | tail -5 | sed 's/^/    /' || echo "    (No events available)"
                ;;
        esac
        
        # Get pod age
        POD_AGE=$(kubectl get pod -n "$POD_NS" "$POD_NAME" -o jsonpath='{.metadata.creationTimestamp}' 2>/dev/null || echo "Unknown")
        echo "  Age: $POD_AGE"
        
        # Get node assignment
        POD_NODE=$(kubectl get pod -n "$POD_NS" "$POD_NAME" -o jsonpath='{.spec.nodeName}' 2>/dev/null || echo "Not assigned")
        echo "  Node: $POD_NODE"
        
    done <<< "$ERROR_PODS"
    
    # Print error summary
    echo ""
    print_header "Error Summary"
    for ERROR_TYPE in "${!ERROR_CATEGORIES[@]}"; do
        echo "  $ERROR_TYPE: ${ERROR_CATEGORIES[$ERROR_TYPE]}"
    done
    fi
fi

################################################################################
# Summary Report
################################################################################

print_header "Health Check Summary"

if [[ "$DRY_RUN" == "true" ]]; then
    print_dry_run "Would execute: kubectl get nodes --no-headers | wc -l"
    print_dry_run "Would execute: kubectl get pods -A --no-headers | wc -l"
    print_dry_run "Would calculate:"
    print_dry_run "  - Total nodes, ready nodes, cordoned nodes"
    print_dry_run "  - Total pods, running pods, pods with issues"
    print_dry_run "  - Overall cluster health status"
    echo ""
    print_info "Dry-run mode completed successfully"
    print_info "Cluster: $CLUSTER_NAME"
    print_info "No actual commands were executed"
else
    # Node summary
    TOTAL_NODES=$(kubectl get nodes --no-headers | wc -l)
    READY_NODES=$(kubectl get nodes --no-headers | grep -c " Ready " || echo "0")
    CORDONED_NODES=$(kubectl get nodes --no-headers | grep -c "SchedulingDisabled" || echo "0")

    echo "Nodes:"
    echo "  Total: $TOTAL_NODES"
    echo "  Ready: $READY_NODES"
    echo "  Cordoned: $CORDONED_NODES"

    # Pod summary
    if [[ -n "$NAMESPACE" ]]; then
        TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
        RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c "Running" || echo "0")
    else
        TOTAL_PODS=$(kubectl get pods -A --no-headers 2>/dev/null | wc -l)
        RUNNING_PODS=$(kubectl get pods -A --no-headers 2>/dev/null | grep -c "Running" || echo "0")
    fi

    echo ""
    echo "Pods:"
    echo "  Total: $TOTAL_PODS"
    echo "  Running: $RUNNING_PODS"
    echo "  With Issues: ${ERROR_COUNT:-0}"

    # Overall health status
    echo ""
    if [[ ${ERROR_COUNT:-0} -eq 0 ]] && [[ $CORDONED_NODES -eq 0 ]]; then
        print_success "Cluster Health: HEALTHY"
    elif [[ ${ERROR_COUNT:-0} -gt 0 ]] && [[ $CORDONED_NODES -eq 0 ]]; then
        print_warning "Cluster Health: DEGRADED (Pod issues detected)"
    elif [[ ${ERROR_COUNT:-0} -eq 0 ]] && [[ $CORDONED_NODES -gt 0 ]]; then
        print_warning "Cluster Health: DEGRADED (Cordoned nodes detected)"
    else
        print_error "Cluster Health: UNHEALTHY (Multiple issues detected)"
    fi
fi

echo ""
print_info "Health check completed at: $(date)"
print_info "Cluster: $CLUSTER_NAME"

if [[ "$DRY_RUN" == "true" ]]; then
    print_info "Mode: DRY-RUN (no commands executed)"
fi

if [[ -n "$OUTPUT_FILE" ]]; then
    print_success "Report saved to: $OUTPUT_FILE"
fi

echo ""

# Made with Bob
