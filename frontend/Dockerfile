FROM node:22-slim

WORKDIR /app

RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 4321
CMD ["pnpm", "astro", "dev", "--host", "0.0.0.0"]
