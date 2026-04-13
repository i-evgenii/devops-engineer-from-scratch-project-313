FROM node:20-slim AS frontend-builder

WORKDIR /build

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN mkdir -p /dist && cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /dist/

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

RUN apt-get update && apt-get install -y nginx curl nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY uv.lock pyproject.toml package.json package-lock.json* /app/

RUN uv sync --frozen --no-dev

RUN npm install

COPY . .

RUN mkdir -p /app/public

COPY --from=frontend-builder /dist /app/public

COPY nginx.conf /etc/nginx/sites-available/default

ENV PATH="/app/.venv/bin:$PATH"
ENV FLASK_RUN_HOST=0.0.0.0

# EXPOSE 5173 8080

# CMD ["npm", "run", "dev"]

EXPOSE 80

CMD ["npm", "run", "prod"]
