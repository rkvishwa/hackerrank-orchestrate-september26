#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/opt/buy-or-wait}"
REPO_URL="${REPO_URL:-}"
GIT_REF="${GIT_REF:-main}"
DOMAIN="${DOMAIN:-financeagent.knurdz.org}"
EXPECTED_IP="${EXPECTED_IP:-20.40.49.59}"
COMPOSE_FILE="${APP_DIR}/code/docker-compose.yml"
LOCK_FILE="/tmp/buy-or-wait-deploy.lock"
LOG_DIR="${APP_DIR}/logs"

log() { echo "[$(date -Iseconds)] $*"; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing command: $1"; exit 1; }
}

check_dns() {
  local resolved
  resolved="$(getent hosts "$DOMAIN" | awk '{print $1; exit}')"
  if [[ "$resolved" != "$EXPECTED_IP" ]]; then
    echo "DNS check failed: $DOMAIN resolved to ${resolved:-unknown}, expected $EXPECTED_IP"
    exit 1
  fi
}

install_repo() {
  require_cmd git
  require_cmd docker
  docker compose version >/dev/null
  mkdir -p "$APP_DIR" "$LOG_DIR"
  if [[ ! -d "$APP_DIR/.git" ]]; then
    [[ -n "$REPO_URL" ]] || { echo "REPO_URL required for first install"; exit 1; }
    git clone "$REPO_URL" "$APP_DIR"
  fi
  cd "$APP_DIR"
  git fetch --all --prune
  git checkout "$GIT_REF"
  git pull --ff-only origin "$GIT_REF" || true
}

deploy_stack() {
  cd "$APP_DIR/code"
  [[ -f .env ]] || cp .env.example .env
  docker compose -f "$COMPOSE_FILE" build
  docker compose -f "$COMPOSE_FILE" up -d postgres redis
  docker compose -f "$COMPOSE_FILE" run --rm migrate
  docker compose -f "$COMPOSE_FILE" up -d api worker caddy
}

wait_ready() {
  local attempts=30
  while (( attempts > 0 )); do
    if docker compose -f "$COMPOSE_FILE" exec -T api curl -fsS "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
      log "API health check passed"
      return 0
    fi
    attempts=$((attempts - 1))
    sleep 5
  done
  echo "Readiness check failed"
  return 1
}

cmd="${1:-install}"
case "$cmd" in
  install|update)
    exec 9>"$LOCK_FILE"
    flock -n 9 || { echo "Deployment already running"; exit 1; }
    check_dns
    install_repo
    deploy_stack
    wait_ready
    log "Deployment complete"
    ;;
  status)
    docker compose -f "$COMPOSE_FILE" ps
    ;;
  logs)
    docker compose -f "$COMPOSE_FILE" logs -f --tail=200
    ;;
  run-batch)
    docker compose -f "$COMPOSE_FILE" exec -T api python main.py --deterministic --emit-usage-report
    log "Output: ${APP_DIR}/artifacts/output.csv; reports: ${APP_DIR}/artifacts/evaluation"
    ;;
  rollback)
    cd "$APP_DIR"
    git reset --hard HEAD~1
    deploy_stack
    ;;
  *)
    echo "Usage: $0 {install|update|status|logs|run-batch|rollback}"
    exit 1
    ;;
esac
