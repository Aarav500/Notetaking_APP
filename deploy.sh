#!/usr/bin/env bash
# deploy.sh - VM-side idempotent deploy script
# Expectations:
#  - GITHUB_ENV_B64 env var contains base64 of deploy.env (set by workflow remote ssh)
#  - deploy_bundle/deploy.env will also be present (copied by scp)
#
set -euo pipefail
LOGFILE=${LOGFILE:-/var/log/pansophy_deploy.log}
WORKDIR=${WORKDIR:-/opt/pansophy}
BUNDLE_DIR=${BUNDLE_DIR:-${WORKDIR}/deploy_bundle}
K8S_DIR=${K8S_DIR:-${BUNDLE_DIR}/k8s}
IMAGE_PREFIX=${IMAGE_PREFIX:-ghcr.io/Aarav500/Notetaking_APP}
SERVICES=(frontend nestjs_backend ideater)

timestamp(){ date -u +'%Y-%m-%dT%H:%M:%SZ'; }
log(){ echo "$(timestamp) - $*" | tee -a "$LOGFILE"; }

# ensure log exists
mkdir -p "$(dirname "$LOGFILE")" || true
touch "$LOGFILE" || true
chmod 644 "$LOGFILE" || true

log "=== Starting deploy.sh on VM ==="
log "WORKDIR=$WORKDIR, BUNDLE_DIR=$BUNDLE_DIR, K8S_DIR=$K8S_DIR"

# If base64 env is provided, decode it into bundle (this duplicates but is robust)
if [[ -n "${GITHUB_ENV_B64:-}" ]]; then
  log "Decoding GITHUB_ENV_B64 into $BUNDLE_DIR/deploy.env"
  mkdir -p "$BUNDLE_DIR"
  echo "$GITHUB_ENV_B64" | base64 -d > "$BUNDLE_DIR/deploy.env" || true
fi

# 1) Basic system update and install dependencies
log "Running apt update/upgrade and installing packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y
apt-get install -y git curl ca-certificates apt-transport-https software-properties-common wget gnupg lsb-release build-essential python3 python3-pip python3-venv

# Node.js (>=16) and npm
if ! command -v node >/dev/null 2>&1 || [[ "$(node -v 2>/dev/null | cut -d. -f1 | tr -d v)" -lt 16 ]]; then
  log "Installing Node.js 18 LTS..."
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash - || true
  apt-get install -y nodejs
fi

# Graphviz install
log "Installing graphviz..."
apt-get install -y graphviz

# mermaid-cli (mmdc)
if ! command -v mmdc >/dev/null 2>&1; then
  log "Installing mermaid-cli globally via npm..."
  npm install -g @mermaid-js/mermaid-cli || true
fi
MMDCCMD="$(command -v mmdc || true)"
log "mmdc at: ${MMDCCMD:-not-found}"

# Docker install (if not present)
if ! command -v docker >/dev/null 2>&1; then
  log "Installing Docker CE..."
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io || true
  # ensure current (non-root) user has docker access — note we are running as sudo from Actions
  if [[ -n "${SUDO_USER:-}" ]]; then
    usermod -aG docker "${SUDO_USER}" || true
  fi
fi
log "docker: $(docker --version 2>/dev/null || echo 'not available')"

# kubectl or microk8s detection
if command -v microk8s >/dev/null 2>&1; then
  KUBECTL="microk8s kubectl"
  log "Using microk8s kubectl"
else
  KUBECTL=${KUBECTL:-kubectl}
  log "Using kubectl: $KUBECTL"
fi

# 2) Docker cleanup to reclaim space (safe)
if command -v docker >/dev/null 2>&1; then
  log "Pruning stopped containers and dangling images..."
  docker container prune -f || true
  docker image prune -af || true
fi

# 3) Prepare .env file on VM
ENV_FILE="${WORKDIR}/.env"
if [[ -f "${BUNDLE_DIR}/deploy.env" ]]; then
  log "Using ${BUNDLE_DIR}/deploy.env to populate $ENV_FILE"
  mkdir -p "$WORKDIR"
  cp "${BUNDLE_DIR}/deploy.env" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
else
  log "No deploy.env found in bundle. Creating minimal $ENV_FILE"
  mkdir -p "$WORKDIR"
  cat > "$ENV_FILE" <<EOF
APP_ENV=production
EOF
  chmod 600 "$ENV_FILE"
fi

# small helper to set key in .env
set_env_kv() {
  local file="$1" key="$2" value="$3"
  # escape slashes for sed
  local esc
  esc="$(printf '%s' "$value" | sed -e 's/[&/\]/\\&/g')"
  if grep -qE "^${key}=" "$file"; then
    sed -i -E "s#^(${key}=).*#\\1${esc}#g" "$file"
  else
    echo "${key}=${value}" >> "$file"
  fi
}

# 4) Detect mermaid and graphviz paths (unless present)
log "Detecting MERMAID_PATH and GRAPHVIZ_PATH..."
# If provided by deploy.env, keep that
if grep -qE "^MERMAID_PATH=" "$ENV_FILE"; then
  log "MERMAID_PATH specified in $ENV_FILE"
else
  MERMAID_PATH="$(command -v mmdc 2>/dev/null || true)"
  if [[ -z "$MERMAID_PATH" ]]; then
    MERMAID_PATH="$(npm root -g 2>/dev/null)/@mermaid-js/mermaid-cli/bin/mmdc"
  fi
  MERMAID_PATH="${MERMAID_PATH:-/usr/bin/mmdc}"
  set_env_kv "$ENV_FILE" "MERMAID_PATH" "$MERMAID_PATH"
  log "Set MERMAID_PATH=$MERMAID_PATH"
fi

if grep -qE "^GRAPHVIZ_PATH=" "$ENV_FILE"; then
  log "GRAPHVIZ_PATH specified in $ENV_FILE"
else
  GRAPHVIZ_PATH="$(command -v dot 2>/dev/null || true)"
  GRAPHVIZ_PATH="${GRAPHVIZ_PATH:-/usr/bin/dot}"
  set_env_kv "$ENV_FILE" "GRAPHVIZ_PATH" "$GRAPHVIZ_PATH"
  log "Set GRAPHVIZ_PATH=$GRAPHVIZ_PATH"
fi

if grep -qE "^LOG_FILE_PATH=" "$ENV_FILE"; then
  log "LOG_FILE_PATH specified in $ENV_FILE"
else
  LOG_FILE_PATH="${LOG_FILE_PATH:-/var/log/pansophy_app.log}"
  mkdir -p "$(dirname "$LOG_FILE_PATH")" || true
  touch "$LOG_FILE_PATH" || true
  set_env_kv "$ENV_FILE" "LOG_FILE_PATH" "$LOG_FILE_PATH"
  log "Set LOG_FILE_PATH=$LOG_FILE_PATH"
fi

# 5) Create namespace & imagePullSecret if GHCR creds are available
log "Creating Kubernetes namespace and imagePullSecret (if GHCR creds supplied)..."
$KUBECTL create namespace pansophy --dry-run=client -o yaml | $KUBECTL apply -f - || true

# read GHCR creds from .env if present
GHCR_USER=$(grep -E '^GHCR_USER=' "$ENV_FILE" | cut -d'=' -f2- || true)
GHCR_PAT=$(grep -E '^GHCR_PAT=' "$ENV_FILE" | cut -d'=' -f2- || true)

if [[ -n "$GHCR_USER" && -n "$GHCR_PAT" ]]; then
  log "Creating imagePullSecret 'ghcr-registry' in namespace 'pansophy'"
  echo "$GHCR_PAT" >/tmp/ghcr_pat.tmp
  $KUBECTL create secret docker-registry ghcr-registry \
    --docker-server=ghcr.io \
    --docker-username="${GHCR_USER}" \
    --docker-password="$(cat /tmp/ghcr_pat.tmp)" \
    --docker-email="${GHCR_USER}@users.noreply.github.com" \
    -n pansophy --dry-run=client -o yaml | $KUBECTL apply -f - || true
  rm -f /tmp/ghcr_pat.tmp

  # patch default serviceAccount to use imagePullSecret so pods pull images without changes to manifests
  $KUBECTL patch serviceaccount default -n pansophy -p '{"imagePullSecrets":[{"name":"ghcr-registry"}]}' || true
else
  log "GHCR_USER/GHCR_PAT not found in .env; skipping imagePullSecret creation. If private images, cluster must have pull access."
fi

# 6) Apply k8s manifests from bundle
if [[ -d "$K8S_DIR" && -n "$(ls -A "$K8S_DIR" 2>/dev/null)" ]]; then
  log "Applying Kubernetes manifests from $K8S_DIR"
  $KUBECTL apply -n pansophy -f "$K8S_DIR" || log "kubectl apply returned non-zero code"
else
  log "ERROR: k8s manifests missing in $K8S_DIR"
  exit 2
fi

# 7) Try to pull latest images locally (best-effort)
for svc in "${SERVICES[@]}"; do
  image="${IMAGE_PREFIX}-${svc}:latest"
  log "docker pull (best-effort) $image"
  docker pull "$image" || log "docker pull failed (private images may require registry login or imagePullSecret)"
done

# 8) Rollout status checks
for svc in "${SERVICES[@]}"; do
  log "Checking rollout status for deployment/$svc"
  $KUBECTL rollout status -n pansophy deployment/$svc --timeout=120s || log "rollout status failed for $svc"
done

log "=== Deploy finished successfully ==="
exit 0
