install:
	uv sync

run:
	uv run flask --app main run --port 8080
