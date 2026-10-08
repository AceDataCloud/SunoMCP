set -eu
. ./deploy/oauth-state.sh

sed 's/\${TAG}/'"$BUILD_NUMBER"'/g' deploy/production/deployment.yaml | kubectl apply -f -
mark_oauth_key_initialized
kubectl apply -f deploy/production/service.yaml
kubectl apply -f deploy/production/ingress.yaml
kubectl -n acedatacloud rollout status "deployment/$(grep '^  name:' deploy/production/deployment.yaml | head -1 | awk '{print $2}')" --timeout=300s
