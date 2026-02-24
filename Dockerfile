FROM node:20-slim AS base

RUN npm install -g bun

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "start"]
