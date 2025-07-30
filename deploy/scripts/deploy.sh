#!/bin/bash
# SERP Strategist API - Production Deployment Script
# Enterprise-grade deployment with validation and rollback

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOY_DIR="${PROJECT_ROOT}/deploy"
BACKUP_DIR="${PROJECT_ROOT}/backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${PROJECT_ROOT}/logs/deployment_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOG_FILE}"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOG_FILE}"
}

# Validation functions
validate_environment() {
    log "🔍 Validating deployment environment..."
    
    # Check required commands
    for cmd in docker docker-compose python3 openssl; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command '$cmd' not found"
        fi
    done
    
    # Check environment variables
    required_vars=(
        "GOOGLE_API_KEY"
        "GOOGLE_CUSTOM_SEARCH_ENGINE_ID" 
        "GEMINI_API_KEY"
        "SECRET_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable '$var' not set"
        fi
    done
    
    success "Environment validation passed"
}

create_ssl_certificates() {
    log "🔐 Creating SSL certificates..."
    
    SSL_DIR="${DEPLOY_DIR}/nginx/ssl"
    mkdir -p "${SSL_DIR}"
    
    if [[ ! -f "${SSL_DIR}/cert.pem" ]]; then
        # Create self-signed certificate for development
        # In production, replace with real certificates
        openssl req -x509 -newkey rsa:4096 -keyout "${SSL_DIR}/key.pem" \
            -out "${SSL_DIR}/cert.pem" -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        success "SSL certificates created"
    else
        log "SSL certificates already exist"
    fi
}

backup_current_deployment() {
    log "💾 Creating deployment backup..."
    
    mkdir -p "${BACKUP_DIR}"
    
    # Backup database if exists
    if [[ -f "${PROJECT_ROOT}/data/serp_strategist_prod.db" ]]; then
        cp "${PROJECT_ROOT}/data/serp_strategist_prod.db" "${BACKUP_DIR}/"
    fi
    
    # Backup logs
    if [[ -d "${PROJECT_ROOT}/logs" ]]; then
        cp -r "${PROJECT_ROOT}/logs" "${BACKUP_DIR}/"
    fi
    
    # Backup configuration
    if [[ -f "${PROJECT_ROOT}/.env" ]]; then
        cp "${PROJECT_ROOT}/.env" "${BACKUP_DIR}/"
    fi
    
    success "Backup created at ${BACKUP_DIR}"
}

build_application() {
    log "🏗️ Building application..."
    
    cd "${PROJECT_ROOT}"
    
    # Build Docker images
    docker-compose -f "${DEPLOY_DIR}/docker-compose.production.yml" build --no-cache
    
    success "Application built successfully"
}

run_pre_deployment_tests() {
    log "🧪 Running pre-deployment tests..."
    
    cd "${PROJECT_ROOT}"
    
    # Validate Python syntax
    python3 -m py_compile src/main.py
    
    # Run basic tests
    if [[ -f "test-files/validate_google_apis_environment.py" ]]; then
        python3 test-files/validate_google_apis_environment.py
    fi
    
    success "Pre-deployment tests passed"
}

deploy_application() {
    log "🚀 Deploying application..."
    
    cd "${PROJECT_ROOT}"
    
    # Stop existing services gracefully
    docker-compose -f "${DEPLOY_DIR}/docker-compose.production.yml" down --timeout 30
    
    # Start services
    docker-compose -f "${DEPLOY_DIR}/docker-compose.production.yml" up -d
    
    # Wait for services to be ready
    log "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if ! curl -f http://localhost/health &> /dev/null; then
        error "Health check failed after deployment"
    fi
    
    success "Application deployed successfully"
}

run_post_deployment_tests() {
    log "✅ Running post-deployment validation..."
    
    # Health check
    if curl -f http://localhost/health; then
        success "Health check passed"
    else
        error "Health check failed"
    fi
    
    # API test
    if curl -f http://localhost/api/status; then
        success "API test passed"
    else
        warning "API test failed - check logs"
    fi
    
    # Load test (basic)
    log "🔄 Running basic load test..."
    for i in {1..10}; do
        curl -s http://localhost/health > /dev/null || error "Load test failed on attempt $i"
    done
    success "Basic load test passed"
}

setup_monitoring() {
    log "📊 Setting up monitoring..."
    
    # Ensure monitoring services are running
    docker-compose -f "${DEPLOY_DIR}/docker-compose.production.yml" up -d prometheus grafana
    
    log "📊 Monitoring dashboard available at http://localhost:3000"
    log "📊 Prometheus metrics at http://localhost:9090"
    
    success "Monitoring setup complete"
}

cleanup() {
    log "🧹 Cleaning up..."
    
    # Remove old Docker images
    docker image prune -f
    
    # Clean old logs (keep last 7 days)
    find "${PROJECT_ROOT}/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    success "Cleanup complete"
}

rollback() {
    error "🔄 Rolling back deployment..."
    
    # Stop current deployment
    docker-compose -f "${DEPLOY_DIR}/docker-compose.production.yml" down
    
    # Restore from backup if available
    if [[ -d "${BACKUP_DIR}" ]]; then
        log "Restoring from backup: ${BACKUP_DIR}"
        
        # Restore database
        if [[ -f "${BACKUP_DIR}/serp_strategist_prod.db" ]]; then
            cp "${BACKUP_DIR}/serp_strategist_prod.db" "${PROJECT_ROOT}/data/"
        fi
        
        # Restore configuration
        if [[ -f "${BACKUP_DIR}/.env" ]]; then
            cp "${BACKUP_DIR}/.env" "${PROJECT_ROOT}/"
        fi
    fi
    
    error "Rollback completed - manual intervention required"
}

# Main deployment flow
main() {
    log "🚀 Starting SERP Strategist API Production Deployment"
    log "📁 Project root: ${PROJECT_ROOT}"
    log "📄 Log file: ${LOG_FILE}"
    
    # Set trap for cleanup on exit
    trap rollback ERR
    
    # Create necessary directories
    mkdir -p "${PROJECT_ROOT}/logs" "${PROJECT_ROOT}/data" "${PROJECT_ROOT}/backups"
    
    # Deployment steps
    validate_environment
    create_ssl_certificates
    backup_current_deployment
    build_application
    run_pre_deployment_tests
    deploy_application
    run_post_deployment_tests
    setup_monitoring
    cleanup
    
    success "🎉 Deployment completed successfully!"
    log "🌐 Application available at: https://localhost"
    log "📊 Monitoring dashboard: http://localhost:3000 (admin/admin)"
    log "📈 Metrics endpoint: http://localhost:9090"
    log "📄 Deployment log: ${LOG_FILE}"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "test")
        run_post_deployment_tests
        ;;
    "monitor")
        setup_monitoring
        ;;
    *)
        echo "Usage: $0 [deploy|rollback|test|monitor]"
        exit 1
        ;;
esac