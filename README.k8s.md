Kubernetes deployment

This project includes simple Kubernetes manifests for running the Flask app with SQLite.

Files created:
- `k8s/deployment.yaml` - Deployment with initContainer to run migrations and a PVC mount for the DB
- `k8s/service.yaml` - LoadBalancer Service exposing the app
- `k8s/secret.yaml` - Secret for `SECRET_KEY` (base64 encoded value)
- `k8s/pvc.yaml` - PersistentVolumeClaim for `products.db`

Config and Secrets

Instead of hardcoding values, create a ConfigMap and Secret and reference them in the Deployment:

# create configmap
kubectl apply -f k8s/configmap.yaml

# create secret
kubectl create secret generic flask-secret --from-literal=SECRET_KEY='change-this-in-prod'

The Deployment now uses `envFrom` to load both ConfigMap and Secret, so the app reads `SQLALCHEMY_DATABASE_URI`, `FLASK_ENV` and `SECRET_KEY` from environment variables.

Local (minikube / kind) quick start

1) Build the image locally:

   # from project root
   docker build -t flask-app:latest .

   # for kind (load image into cluster)
   kind load docker-image flask-app:latest

   # for minikube
   minikube image load flask-app:latest

2) Create secret (recommended to set your real SECRET_KEY):

   # generate base64 value
   echo -n 'change-this-in-prod' | base64

   # create secret (alternative to applying secret.yaml)
   kubectl create secret generic flask-secret --from-literal=SECRET_KEY='change-this-in-prod'

3) Apply manifests

   kubectl apply -f k8s/pvc.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml

4) Open service

   # minikube
   minikube service flask-service

   # or get external IP (LoadBalancer) / NodePort
   kubectl get svc flask-service

Notes for production (remote cluster)

- Build and push the Docker image to a registry (e.g. Docker Hub or your private registry):

  docker build -t <registry>/flask-app:latest .
  docker push <registry>/flask-app:latest

  Then update `k8s/deployment.yaml` image field and apply manifests.

- Make sure your cluster supports PersistentVolumeClaims (configure StorageClass / PVs).
- For migrations I used an `initContainer` that runs `flask db upgrade`. For highly-available setups consider a dedicated migration job and careful rollout strategy.

Troubleshooting

- If using SQLite on multi-replica pods you may hit file locking issues. Prefer a proper DB (Postgres/MySQL) in multi-instance production.
- If `initContainer` fails, inspect logs: `kubectl logs deploy/flask-app -c migrate`.

