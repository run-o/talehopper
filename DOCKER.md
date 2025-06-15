# Docker Setup for TaleHopper

This document explains how to run TaleHopper using Docker containers for both development and production environments.

## Prerequisites

[Docker](https://docs.docker.com/get-docker/)

## Environment Setup

Before running the application, make sure you have set up the environment variables:

1. Create a `.env` file in the `backend` directory using the [`.env.example`](backend/.env.example) as a template:
2. Edit the `.env` file to include your LLM API keys and other configuration settings.

## Running in Production Mode

To run the application in production mode:
```bash
docker compose up -d
```

This will:
- Build and start the backend FastAPI service on port 8000
- Build and start the frontend React application on port 3000
- Set up a network for communication between services

To access the application, open a browser to: `http://localhost:3000/index.html`

To stop the application:
```bash
docker compose down
```

## Running in Development Mode

For development with hot-reloading:

```bash
docker compose -f docker-compose.dev.yml up -d
```

This development setup includes:
- Hot-reloading for both frontend and backend
- Volume mounts for real-time code changes
- Development-specific configurations

Run the backend tests with (assuming the backend container is running):
```bash
docker compose -f docker-compose.dev.yml exec backend python -m pytest
```

Or as a one-off container (if backend is not running):
```bash
docker compose -f docker-compose.dev.yml run --rm backend python -m pytest
```
To force a rebuild and run tests as a one-off:
```bash
docker compose -f docker-compose.dev.yml run --rm --build backend python -m pytest
```

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Developing inside the containers with VSCode

- Install the Dev Containers extension in VSCode: `ms-vscode-remote.remote-containers`
- Run command (Shift+Command+P): `Dev Containers: Reopen in Container`
- This will start a VSCode session inside the container of choice (by default `backend` as specified in [`.devcontainer.json`](.devcontainer/devcontainer.json))


## Container Management

List running containers:
```bash
docker compose ps
```

View/tail logs:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs backend -f 
docker compose logs frontend -f
```

Restart services:
```bash
docker compose restart backend
docker compose restart frontend
```

In order to force a rebuild of the frontend image:
```bash
docker compose -f docker-compose.dev.yml build frontend --no-cache
```

## Extending the Setup

### Adding a Database

To add a database service (e.g., PostgreSQL), update the `docker-compose.yml` file:

```yaml
services:
  # ... existing services

  db:
    image: postgres:14
    container_name: talehopper-db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=talehopper
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - talehopper-network

volumes:
  postgres_data:
```

Then update the backend service to depend on the database:

```yaml
backend:
  # ... existing configuration
  depends_on:
    - db
```

### Adding Redis for Caching

Similarly, you can add Redis for caching:

```yaml
services:
  # ... existing services

  redis:
    image: redis:alpine
    container_name: talehopper-redis
    ports:
      - "6379:6379"
    networks:
      - talehopper-network
```
