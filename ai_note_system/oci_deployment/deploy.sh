#!/bin/bash
# Deployment script for AI Note System on Oracle Cloud Infrastructure

# Exit on any error
set -e

# Configuration
APP_NAME="ai-note-system"
VERSION=$(date +"%Y%m%d%H%M%S")
REGISTRY_PATH="<REGISTRY_REGION>.ocir.io/<TENANCY_NAMESPACE>/${APP_NAME}"
IMAGE_TAG="${REGISTRY_PATH}:${VERSION}"
LATEST_TAG="${REGISTRY_PATH}:latest"

# OCI Kubernetes Engine (OKE) configuration
CLUSTER_ID="<OKE_CLUSTER_ID>"
COMPARTMENT_ID="<COMPARTMENT_ID>"
NAMESPACE="ai-note-system"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display step information
step() {
    echo -e "${GREEN}==>${NC} $1"
}

# Function to display warning
warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Function to display error and exit
error() {
    echo -e "${RED}ERROR:${NC} $1"
    exit 1
}

# Check if OCI CLI is installed
if ! command -v oci &> /dev/null; then
    error "OCI CLI is not installed. Please install it first: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install it first: https://docs.docker.com/get-docker/"
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    error "kubectl is not installed. Please install it first: https://kubernetes.io/docs/tasks/tools/install-kubectl/"
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    error "Helm is not installed. Please install it first: https://helm.sh/docs/intro/install/"
fi

# Check if required environment variables are set
if [[ -z "${ORACLE_CONNECTION_STRING}" ]]; then
    warning "ORACLE_CONNECTION_STRING environment variable is not set. Make sure it's set in the Kubernetes deployment."
fi

if [[ -z "${ORACLE_USERNAME}" ]]; then
    warning "ORACLE_USERNAME environment variable is not set. Make sure it's set in the Kubernetes deployment."
fi

if [[ -z "${ORACLE_PASSWORD}" ]]; then
    warning "ORACLE_PASSWORD environment variable is not set. Make sure it's set in the Kubernetes deployment."
fi

# Step 1: Build Docker image
step "Building Docker image: ${IMAGE_TAG}"
docker build -t ${IMAGE_TAG} -t ${LATEST_TAG} -f oci_deployment/Dockerfile .

# Step 2: Push Docker image to OCI Registry
step "Pushing Docker image to OCI Registry"
# Log in to OCI Registry
echo "Logging in to OCI Registry..."
docker login -u <TENANCY_NAMESPACE>/<OCI_USERNAME> <REGISTRY_REGION>.ocir.io

# Push images
docker push ${IMAGE_TAG}
docker push ${LATEST_TAG}

# Step 3: Configure kubectl for OKE
step "Configuring kubectl for OKE"
oci ce cluster create-kubeconfig --cluster-id ${CLUSTER_ID} --file ~/.kube/config --region <REGION> --token-version 2.0.0

# Step 4: Create namespace if it doesn't exist
step "Creating Kubernetes namespace if it doesn't exist"
kubectl get namespace ${NAMESPACE} || kubectl create namespace ${NAMESPACE}

# Step 5: Deploy using Helm
step "Deploying application using Helm"
helm upgrade --install ${APP_NAME} oci_deployment/helm \
    --namespace ${NAMESPACE} \
    --set image.repository=${REGISTRY_PATH} \
    --set image.tag=${VERSION} \
    --set env.oracleConnectionString=${ORACLE_CONNECTION_STRING} \
    --set env.oracleUsername=${ORACLE_USERNAME} \
    --set env.oraclePassword=${ORACLE_PASSWORD} \
    --set env.oracleWalletLocation="/app/wallet" \
    --wait

# Step 6: Verify deployment
step "Verifying deployment"
kubectl get pods -n ${NAMESPACE}
kubectl get services -n ${NAMESPACE}

# Step 7: Set up monitoring
step "Setting up monitoring"
# Apply Prometheus ServiceMonitor
kubectl apply -f oci_deployment/monitoring/service-monitor.yaml -n ${NAMESPACE}

# Success message
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "Application is now running on OCI Kubernetes Engine."
echo "You can access it at: https://<LOAD_BALANCER_IP>"
echo "API documentation is available at: https://<LOAD_BALANCER_IP>/docs"