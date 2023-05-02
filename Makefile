startd:
	TARGET=release docker-compose up -d --build \
		&& docker-compose run --rm fast-api-docker-poetry poetry run alembic upgrade head

testd:
	docker-compose up -d --build \
		&& docker-compose run --rm fast-api-docker-poetry poetry run pytest -v

startp:
	docker-compose up fast-api-postgres -d --build \
	&& poetry run alembic upgrade head \
	&& poetry run python -m app.main

testp:
	docker-compose up fast-api-postgres -d --build \
	&& poetry run pytest -v

formatp:
	poetry run black app tests
