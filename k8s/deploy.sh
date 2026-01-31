#!/bin/bash
# ==============================================================================
# TechNova IKS Deployment Script
# ==============================================================================
# This script deploys the TechNova Support API and Frontend to IBM Kubernetes Service
#
# Prerequisites:
#   - IBM Cloud CLI installed (ibmcloud)
#   - kubectl installed and configured
#   - IKS cluster created
#
# Usage:
#   ./deploy.sh <cluster-name> <namespace>
#
# Example:
#   ./deploy.sh my-iks-cluster technova
# ==============================================================================

set -e

CLUSTER_NAME=${1:-"my-iks-cluster"}
NAMESPACE=${2:-"default"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "TechNova IKS Deployment"
echo "=================================================="
echo "Cluster: $CLUSTER_NAME"
echo "Namespace: $NAMESPACE"
echo "=================================================="

# Connect to the cluster
echo ""
echo "📡 Connecting to IKS cluster..."
ibmcloud ks cluster config --cluster "$CLUSTER_NAME"

# Create namespace if it doesn't exist
echo ""
echo "📦 Creating namespace '$NAMESPACE' if it doesn't exist..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Set context to the namespace
kubectl config set-context --current --namespace="$NAMESPACE"

# Check if secrets exist
echo ""
echo "🔐 Checking for required secrets..."
if ! kubectl get secret technova-api-secrets -n "$NAMESPACE" &> /dev/null; then
    echo ""
    echo "⚠️  Secret 'technova-api-secrets' not found!"
    echo ""
    echo "Please create it by running:"
    echo ""
    echo "  kubectl create secret generic technova-api-secrets \\"
    echo "    --namespace=$NAMESPACE \\"
    echo "    --from-literal=SERVICENOW_INSTANCE=<your-instance> \\"
    echo "    --from-literal=SERVICENOW_USERNAME=<your-username> \\"
    echo "    --from-literal=SERVICENOW_PASSWORD=<your-password> \\"
    echo "    --from-literal=SLACK_BOT_TOKEN=<your-slack-token> \\"
    echo "    --from-literal=SLACK_DEFAULT_CHANNEL=<your-channel> \\"
    echo "    --from-literal=GITHUB_TOKEN=<your-github-token> \\"
    echo "    --from-literal=GITHUB_DEFAULT_REPO=<owner/repo>"
    echo ""
    exit 1
fi

if ! kubectl get secret icr-io-secret -n "$NAMESPACE" &> /dev/null; then
    echo ""
    echo "⚠️  Secret 'icr-io-secret' not found!"
    echo ""
    echo "Please create it by running:"
    echo ""
    echo "  kubectl create secret docker-registry icr-io-secret \\"
    echo "    --namespace=$NAMESPACE \\"
    echo "    --docker-server=icr.io \\"
    echo "    --docker-username=iamapikey \\"
    echo "    --docker-password=<your-ibm-api-key> \\"
    echo "    --docker-email=<your-email>"
    echo ""
    exit 1
fi

echo "✅ Secrets found"

# Deploy API
echo ""
echo "🚀 Deploying API..."
kubectl apply -f "$SCRIPT_DIR/api-deployment.yaml" -n "$NAMESPACE"

# Deploy Frontend
echo ""
echo "🚀 Deploying Frontend..."
kubectl apply -f "$SCRIPT_DIR/frontend-deployment.yaml" -n "$NAMESPACE"

# Wait for deployments to be ready
echo ""
echo "⏳ Waiting for API deployment to be ready..."
kubectl rollout status deployment/technova-api -n "$NAMESPACE" --timeout=120s

echo ""
echo "⏳ Waiting for Frontend deployment to be ready..."
kubectl rollout status deployment/technova-frontend -n "$NAMESPACE" --timeout=120s

# Get service info
echo ""
echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "📊 Deployment Status:"
kubectl get deployments -n "$NAMESPACE" -l "app in (technova-api, technova-frontend)"

echo ""
echo "🌐 Services:"
kubectl get services -n "$NAMESPACE" -l "app in (technova-api, technova-frontend)"

echo ""
echo "📦 Pods:"
kubectl get pods -n "$NAMESPACE" -l "app in (technova-api, technova-frontend)"

# Get external IP for frontend
echo ""
echo "=================================================="
echo "🔗 Access Information"
echo "=================================================="
FRONTEND_IP=$(kubectl get svc technova-frontend-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
if [ "$FRONTEND_IP" = "pending" ] || [ -z "$FRONTEND_IP" ]; then
    echo "Frontend LoadBalancer IP is still being assigned..."
    echo "Run: kubectl get svc technova-frontend-service -n $NAMESPACE"
else
    echo "Frontend URL: http://$FRONTEND_IP"
fi

echo ""
echo "To apply Ingress (optional):"
echo "  kubectl apply -f $SCRIPT_DIR/ingress.yaml -n $NAMESPACE"
