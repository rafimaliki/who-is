FROM node:22-slim

WORKDIR /app

RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 4321
# The dev-server lock file in .astro/ (bind-mounted, so it survives container restarts) records a
# PID from whichever container instance wrote it last - never valid for a fresh container start.
# `astro dev --force` overrides it by killing that PID, but in a fresh container PIDs restart
# from a low number too, so a stale lock can coincidentally name a real, unrelated process here -
# force killed it mid-startup in testing. Deleting the stale lock before starting is unambiguous:
# nothing to override, nothing to (mis)kill.
CMD sh -c "rm -rf .astro && exec pnpm astro dev --host 0.0.0.0"
