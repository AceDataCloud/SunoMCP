set -eu

sed 's/\${TAG}/'"$BUILD_NUMBER"'/g' deploy/production/deployment.yaml | kubectl apply -f -
kubectl apply -f deploy/production/service.yaml
kubectl apply -f deploy/production/ingress.yaml
kubectl rollout status "deployment/$(grep '^  name:' deploy/production/deployment.yaml | head -1 | awk '{print $2}')" --timeout=300s
