#!/bin/bash

# Configuration
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
APPS_DIR="${REPO_ROOT}/apps"
WF_DIR="${REPO_ROOT}/.github/workflows"
WF_FILE="${WF_DIR}/vercel-matrix-deploy.yml"
VERCEL_SCOPE="${VERCEL_SCOPE:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
echo_error() { echo -e "${RED}❌ $1${NC}"; }

echo_info "Starting Vercel Secrets Sync..."

# Create apps directory if it doesn't exist
mkdir -p "$APPS_DIR"

echo_info "Current app structure:"
if command -v tree &> /dev/null; then
    tree -L 2 "$APPS_DIR" 2>/dev/null || ls -la "$APPS_DIR"
else
    ls -la "$APPS_DIR"
fi

echo_success "Script completed successfully!"
