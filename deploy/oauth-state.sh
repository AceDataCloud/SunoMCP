#!/bin/sh
# Sourced by each hosted MCP's deploy/run.sh before applying its Deployment.
set -eu

oauth_deployment_name=$(awk '/^  name:/ { print $2; exit }' deploy/production/deployment.yaml)
case "$oauth_deployment_name" in
  mcp-*) ;;
  *) echo "OAuth state setup: invalid Deployment name" >&2; exit 1 ;;
esac
oauth_secret_name="${oauth_deployment_name}-oauth-state"

if ! kubectl -n acedatacloud get secret "$oauth_secret_name" >/dev/null 2>&1; then
  oauth_key_marker=$(kubectl -n acedatacloud get deployment "$oauth_deployment_name" \
    -o go-template='{{index .metadata.annotations "mcp.acedata.cloud/oauth-state-key-initialized"}}' \
    2>/dev/null || true)
  if [ "$oauth_key_marker" = true ]; then
    echo "OAuth state key is missing; restore $oauth_secret_name before deployment" >&2
    exit 1
  fi
  oauth_state_key=$(openssl rand -hex 32)
  kubectl -n acedatacloud create secret generic "$oauth_secret_name" \
    --from-literal=state_key="$oauth_state_key" >/dev/null
  unset oauth_state_key
fi

oauth_state_key_ready=$(kubectl -n acedatacloud get secret "$oauth_secret_name" \
  -o go-template='{{if index .data "state_key"}}yes{{end}}')
if [ "$oauth_state_key_ready" != yes ]; then
  echo "OAuth state Secret $oauth_secret_name has no state_key" >&2
  exit 1
fi

kubectl -n acedatacloud rollout status statefulset/mcp-acedatacloud-oauth-redis --timeout=300s

mark_oauth_key_initialized() {
  kubectl -n acedatacloud annotate deployment "$oauth_deployment_name" \
    'mcp.acedata.cloud/oauth-state-key-initialized=true' --overwrite >/dev/null
  kubectl -n acedatacloud rollout status "deployment/$oauth_deployment_name" --timeout=900s
}
