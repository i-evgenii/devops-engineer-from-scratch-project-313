FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY uv.lock pyproject.toml package.json package-lock.json* /app/

RUN uv sync --frozen --no-dev
RUN npm install

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5173 8080

CMD ["npm", "run", "dev"]
