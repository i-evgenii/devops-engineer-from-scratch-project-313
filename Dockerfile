FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y nodejs npm nginx curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY uv.lock pyproject.toml package.json package-lock.json* /app/

RUN uv sync --frozen --no-dev
RUN npm install

COPY . /app
COPY nginx.conf /etc/nginx/sites-available/default

RUN mkdir -p /app/public && \
    cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

ENV PATH="/app/.venv/bin:$PATH"
ENV FLASK_RUN_HOST=0.0.0.0

# EXPOSE 5173 8080

# CMD ["npm", "run", "dev"]

EXPOSE 80

CMD ["npm", "run", "prod"]
