startd:
	docker-compose -f docker-compose.local.yml up -d --build \
		&& docker-compose run --rm fast-api-docker-poetry poetry run alembic upgrade head

stopd:
	docker-compose -f docker-compose.local.yml down

startslimd:
	docker-compose up -d --build \
		&& docker-compose run --rm fast-api-docker-poetry poetry run alembic upgrade head

testd:
	docker-compose up -d --build \
		&& docker-compose run --rm fast-api-docker-poetry poetry run pytest -v --durations=10 --durations-min=0.5

startp:
	docker-compose up fast-api-postgres -d --build \
	&& poetry run alembic upgrade head \
	&& poetry run python -m app.main

testp:
	docker-compose up fast-api-postgres -d --build \
	&& poetry run pytest -v --durations=10 --durations-min=0.5

create-migration: ## Create an alembic migration
	@read -p "Enter rev id: " message; \
	poetry run alembic revision --autogenerate --rev-id "$$message"

#formatp:
#	poetry run black app tests
