FROM astral-sh/uv:python3.12-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-install-project --no-dev

FROM python:3.12-alpine
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . /app
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
