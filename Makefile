install:
	uv sync

run:
	uv run flask --app main run --port 8080

test:
	uv run ruff check
	uv run pytest