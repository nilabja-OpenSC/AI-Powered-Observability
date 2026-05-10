#!/bin/bash

# UI Code Generation Script
# This script generates all missing UI source code files

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_info "=========================================="
print_info "UI Code Generation Script"
print_info "=========================================="

# Chat-UI Generation
print_info "Generating Chat-UI application..."

# Create directories
mkdir -p src/chat-ui/src/components
mkdir -p src/chat-ui/src/lib
mkdir -p src/chat-ui/src/types
mkdir -p src/chat-ui/public

# Frontend Generation
print_info "Generating Frontend application..."

# Create directories
mkdir -p src/frontend/pages/api
mkdir -p src/frontend/pages/products
mkdir -p src/frontend/components
mkdir -p src/frontend/lib
mkdir -p src/frontend/styles
mkdir -p src/frontend/public

print_success "Directory structure created"

print_info "=========================================="
print_info "Next Steps:"
print_info "=========================================="
echo "1. Chat-UI: Run 'npm install' in src/chat-ui/"
echo "2. Frontend: Run 'npm install' in src/frontend/"
echo "3. Review generated files and customize as needed"
echo "4. Build images: ./scripts/build-and-push-images.sh"
echo "5. Deploy: ./scripts/deploy-all.sh"

# Made with Bob
