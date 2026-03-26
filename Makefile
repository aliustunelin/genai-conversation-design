install:
	bash scripts/install.sh

run:
	bash scripts/run.sh

test:
	bash -c "source .venv/bin/activate && python -m pytest tests/ -v"

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

.PHONY: install run test docker-build docker-up docker-down
