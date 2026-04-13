install:
	uv sync

run:
	uv run flask --app app.main run --port 8080

test:
	uv run ruff check
	PYTHONPATH=. uv run pytest -v

ui:
	npm run dev
