.PHONY: help
help:
	@echo "Available targets:"
	@echo "  test             			Run all tests (backend only for now)"
	@echo "  test-backend     			Run backend tests"
	@echo "  test-docker-backend 		Run backend tests in Docker (Dev environment)"
	@echo "  test-frontend    			Run frontend tests"
	@echo "  test-docker-frontend 		Run frontend tests in Docker (Dev environment)"
	@echo "  docker-up        			Start all prod services"
	@echo "  docker-down      			Stop all prod services"
	@echo "  docker-dev-up    			Start all dev services (hot reload)"
	@echo "  docker-dev-down  			Stop all dev services"
	@echo "  docker-logs      			Show logs for all prod services"
	@echo "  docker-dev-logs   			Show logs for all dev services"
	@echo "  docker-dev-backend-logs	Show logs for backend dev service"
	@echo "  docker-dev-frontend-logs	Show logs for frontend dev service"

.PHONY: test
test:
	test-backend

.PHONY: test-backend
test-backend:
	cd backend && python -m pytest

.PHONY: test-docker-backend
test-docker-backend:
	docker compose -f docker-compose.dev.yml exec backend python -m pytest

.PHONY: test-frontend
test-frontend:
	cd frontend && npm test

.PHONY: test-docker-frontend
test-docker-frontend:
	docker compose -f docker-compose.dev.yml exec frontend npm test

.PHONY: docker-up
docker-up:
	docker compose up -d

.PHONY: docker-down
docker-down:
	docker compose down

.PHONY: docker-dev-up
docker-dev-up:
	docker compose -f docker-compose.dev.yml up --build

.PHONY: docker-dev-down
docker-dev-down:
	docker compose -f docker-compose.dev.yml down

.PHONY: docker-logs
docker-logs:
	docker compose logs -f

.PHONY: docker-dev-logs
docker-dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

.PHONY: docker-dev-backend-logs
docker-dev-backend-logs:
	docker compose -f docker-compose.dev.yml logs -f backend

.PHONY: docker-dev-frontend-logs
docker-dev-frontend-logs:
	docker compose -f docker-compose.dev.yml logs -f frontend