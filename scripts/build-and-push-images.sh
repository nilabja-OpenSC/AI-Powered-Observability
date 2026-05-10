#!/bin/bash

# AI-Powered Observability Platform - Image Build and Push Script
# This script builds all custom container images and pushes them to a registry

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="${REGISTRY:-docker.io}"
USERNAME="${USERNAME:-your-username}"
TAG="${TAG:-v1.0.0}"
BUILD_TOOL="${BUILD_TOOL:-docker}"  # docker or podman

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

# Function to build and push image
build_and_push() {
    local name=$1
    local context=$2
    local dockerfile=${3:-Dockerfile}
    
    local image_name="${REGISTRY}/${USERNAME}/${name}"
    
    print_info "Building ${name}:${TAG}..."
    
    # Build image
    if [ "$dockerfile" = "Dockerfile" ]; then
        ${BUILD_TOOL} build -t ${image_name}:${TAG} ${context}
    else
        ${BUILD_TOOL} build -f ${dockerfile} -t ${image_name}:${TAG} ${context}
    fi
    
    if [ $? -ne 0 ]; then
        print_error "Failed to build ${name}"
        return 1
    fi
    
    # Tag as latest
    ${BUILD_TOOL} tag ${image_name}:${TAG} ${image_name}:latest
    
    print_info "Pushing ${name}:${TAG}..."
    
    # Push versioned tag
    ${BUILD_TOOL} push ${image_name}:${TAG}
    if [ $? -ne 0 ]; then
        print_error "Failed to push ${name}:${TAG}"
        return 1
    fi
    
    # Push latest tag
    ${BUILD_TOOL} push ${image_name}:latest
    if [ $? -ne 0 ]; then
        print_error "Failed to push ${name}:latest"
        return 1
    fi
    
    print_success "${name} built and pushed successfully"
    return 0
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v ${BUILD_TOOL} &> /dev/null; then
    print_error "${BUILD_TOOL} not found. Please install it first."
    exit 1
fi

print_success "Prerequisites check passed"

# Display configuration
print_info "=========================================="
print_info "Build Configuration"
print_info "=========================================="
echo "Registry: ${REGISTRY}"
echo "Username: ${USERNAME}"
echo "Tag: ${TAG}"
echo "Build Tool: ${BUILD_TOOL}"
print_info "=========================================="

# Confirm before proceeding
read -p "Proceed with build? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Build cancelled by user"
    exit 0
fi

# Track build status
FAILED_BUILDS=()
SUCCESSFUL_BUILDS=()

# Build Backend
print_info "=========================================="
print_info "Building Backend Image"
print_info "=========================================="
if build_and_push "observability-backend" "src/backend"; then
    SUCCESSFUL_BUILDS+=("observability-backend")
else
    FAILED_BUILDS+=("observability-backend")
fi

# Build Frontend
print_info "=========================================="
print_info "Building Frontend Image"
print_info "=========================================="
if build_and_push "observability-frontend" "src/frontend"; then
    SUCCESSFUL_BUILDS+=("observability-frontend")
else
    FAILED_BUILDS+=("observability-frontend")
fi

# Build Chat-UI
print_info "=========================================="
print_info "Building Chat-UI Image"
print_info "=========================================="
if build_and_push "observability-chat-ui" "src/chat-ui"; then
    SUCCESSFUL_BUILDS+=("observability-chat-ui")
else
    FAILED_BUILDS+=("observability-chat-ui")
fi

# Build Supervisor Agent
print_info "=========================================="
print_info "Building Supervisor Agent Image"
print_info "=========================================="
if build_and_push "supervisor-agent" "src/agents/supervisor" "src/agents/Dockerfile"; then
    SUCCESSFUL_BUILDS+=("supervisor-agent")
else
    FAILED_BUILDS+=("supervisor-agent")
fi

# Build Observability Agent
print_info "=========================================="
print_info "Building Observability Agent Image"
print_info "=========================================="
if build_and_push "observability-agent" "src/agents/observability" "src/agents/Dockerfile"; then
    SUCCESSFUL_BUILDS+=("observability-agent")
else
    FAILED_BUILDS+=("observability-agent")
fi

# Build Pod Recovery Agent
print_info "=========================================="
print_info "Building Pod Recovery Agent Image"
print_info "=========================================="
if build_and_push "pod-recovery-agent" "src/agents/pod-recovery" "src/agents/Dockerfile"; then
    SUCCESSFUL_BUILDS+=("pod-recovery-agent")
else
    FAILED_BUILDS+=("pod-recovery-agent")
fi

# Build Backup/Restore Agent
print_info "=========================================="
print_info "Building Backup/Restore Agent Image"
print_info "=========================================="
if build_and_push "backup-restore-agent" "src/agents/backup-restore" "src/agents/Dockerfile"; then
    SUCCESSFUL_BUILDS+=("backup-restore-agent")
else
    FAILED_BUILDS+=("backup-restore-agent")
fi

# Summary
print_info "=========================================="
print_info "Build Summary"
print_info "=========================================="

if [ ${#SUCCESSFUL_BUILDS[@]} -gt 0 ]; then
    print_success "Successfully built and pushed ${#SUCCESSFUL_BUILDS[@]} images:"
    for image in "${SUCCESSFUL_BUILDS[@]}"; do
        echo "  ✓ ${image}"
    done
fi

if [ ${#FAILED_BUILDS[@]} -gt 0 ]; then
    print_error "Failed to build ${#FAILED_BUILDS[@]} images:"
    for image in "${FAILED_BUILDS[@]}"; do
        echo "  ✗ ${image}"
    done
    exit 1
fi

print_success "All images built and pushed successfully!"

# Display next steps
print_info "=========================================="
print_info "Next Steps"
print_info "=========================================="
echo "1. Update Helm chart values with image references:"
echo "   - charts/ecommerce-app/backend/values.yaml"
echo "   - charts/ecommerce-app/frontend/values.yaml"
echo "   - charts/ecommerce-app/chat-ui/values.yaml"
echo "   - charts/ai-agents/*/values.yaml"
echo ""
echo "2. Set image repository and tag in values.yaml:"
echo "   image:"
echo "     repository: ${REGISTRY}/${USERNAME}/<image-name>"
echo "     tag: ${TAG}"
echo ""
echo "3. Deploy using the deployment guide:"
echo "   ./scripts/deploy-all.sh"

# Made with Bob
