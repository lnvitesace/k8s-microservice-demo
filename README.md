# k8s-microservice-demo

A hands-on learning project that demonstrates how to build, containerize, and deploy a simple microservice architecture on Kubernetes. The application is a hit counter -- an Nginx frontend proxies API requests to a FastAPI backend, which records and counts page hits in a PostgreSQL database.

## Architecture

```
                         ┌──────────────────────────────────────────┐
                         │           Kubernetes Cluster             │
                         │                                          │
  Browser ──────────────▶│  ┌───────────┐        ┌──────────────┐   │
        NodePort 30080   │  │ Frontend  │  /api/ │   Backend    │   │
                         │  │  (Nginx)  │───────▶│  (FastAPI)   │   │
                         │  │  1 replica│  proxy │  2 replicas  │   │
                         │  └───────────┘        └──────┬───────┘   │
                         │                              │           │
                         │                              ▼           │
                         │                       ┌──────────────┐   │
                         │                       │  PostgreSQL  │   │
                         │                       │  (Alpine)    │   │
                         │                       └──────────────┘   │
                         └──────────────────────────────────────────┘
```

**Three services communicate inside the cluster:**

| Service    | Technology       | Role                                              |
|------------|------------------|----------------------------------------------------|
| Frontend   | Nginx (Alpine)   | Serves static HTML, reverse-proxies `/api/*` to Backend |
| Backend    | Python / FastAPI | REST API that tracks page hits in PostgreSQL        |
| Database   | PostgreSQL 18    | Stores a `hits` table with path and timestamp       |

## Project Structure

```
k8s-microservice-demo/
├── backend/
│   ├── main.py            # FastAPI application (hit counter API)
│   ├── Dockerfile          # Python 3.14-slim + uv package manager
│   ├── compose.yml         # Docker Compose for local development
│   ├── pyproject.toml      # Python dependencies (FastAPI, psycopg, uvicorn)
│   └── uv.lock             # Locked dependency versions
├── frontend/
│   ├── nginx.conf          # Nginx config with /api/ proxy_pass
│   └── Dockerfile          # Nginx Alpine image
└── k8s/
    ├── configmap.yaml      # Database connection config
    ├── secret.yaml         # Database password (base64-encoded)
    ├── postgres.yaml       # PostgreSQL Deployment + ClusterIP Service
    ├── backend.yaml        # Backend Deployment (2 replicas) + ClusterIP Service
    └── frontend.yaml       # Frontend Deployment + NodePort Service
```

## API Endpoints

| Method | Path        | Description                                   |
|--------|-------------|-----------------------------------------------|
| GET    | `/`         | Returns `{"hello!": "world", "hits": <count>}` |
| GET    | `/{name}`   | Returns `{"hello!": "<name>", "hits": <count>}` |
| GET    | `/health`   | Health check for Kubernetes probes             |

Each request to `/` or `/{name}` inserts a row into the `hits` table and returns the total hit count.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- A local Kubernetes cluster (e.g. [minikube](https://minikube.sigs.k8s.io/docs/start/), [kind](https://kind.sigs.k8s.io/), or [Docker Desktop](https://docs.docker.com/desktop/kubernetes/))

## Getting Started

### Option 1 -- Local development with Docker Compose

The `backend/compose.yml` spins up just the backend and a PostgreSQL database for quick iteration:

```bash
cd backend
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Option 2 -- Full stack on Kubernetes

1. **Start your local cluster** (example with minikube):

   ```bash
   minikube start
   ```

2. **Point Docker to the cluster's daemon** so locally-built images are available (minikube-specific):

   ```bash
   eval $(minikube docker-env)
   ```

3. **Build the container images:**

   ```bash
   docker build -t backend:latest  ./backend
   docker build -t frontend:latest ./frontend
   ```

4. **Apply the Kubernetes manifests:**

   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/postgres.yaml
   kubectl apply -f k8s/backend.yaml
   kubectl apply -f k8s/frontend.yaml
   ```

5. **Access the application:**

   ```bash
   # If using minikube:
   minikube service frontend-service --url

   # Or directly via NodePort:
   curl http://<node-ip>:30080          # Static page
   curl http://<node-ip>:30080/api/     # Hit counter API
   ```

6. **Verify everything is running:**

   ```bash
   kubectl get pods
   kubectl get services
   ```

## Kubernetes Concepts Demonstrated

| Concept                | Where it's used                                              |
|------------------------|--------------------------------------------------------------|
| **Deployments**        | All three services use Deployments with RollingUpdate strategy |
| **Services**           | ClusterIP (backend, postgres) and NodePort (frontend)        |
| **ConfigMaps**         | Database connection parameters (`k8s/configmap.yaml`)        |
| **Secrets**            | Database password stored as an Opaque Secret                 |
| **Liveness Probes**    | HTTP GET `/health` (backend), HTTP GET `/` (frontend), `pg_isready` (postgres) |
| **Readiness Probes**   | Same endpoints as liveness, gates traffic until ready         |
| **Rolling Updates**    | `maxSurge: 1, maxUnavailable: 0` for zero-downtime deploys  |
| **Service Discovery**  | Services communicate via Kubernetes DNS (`backend`, `postgresdb`) |
| **Replica Scaling**    | Backend runs 2 replicas to demonstrate scaling               |
| **imagePullPolicy**    | Set to `Never` for locally-built images                      |

## Tech Stack

- **Python 3.14** with FastAPI and psycopg
- **Nginx** (Alpine) as reverse proxy / static server
- **PostgreSQL 18** (Alpine) for persistence
- **Docker** for containerization
- **uv** for fast Python dependency management
- **Kubernetes** for orchestration

## Cleanup

```bash
# Remove all Kubernetes resources
kubectl delete -f k8s/

# Stop minikube (if applicable)
minikube stop
```

## License

This is a personal learning project. Feel free to use it as a reference.
