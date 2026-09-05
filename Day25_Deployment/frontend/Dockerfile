# =========================================================
# Frontend Dockerfile — React (multi-stage: Node build -> Nginx)
# =========================================================
# ONLY needed if you're self-hosting the frontend as a container
# (e.g. alongside the backend on the same VM, or on a Docker-based host).
#
# If you're deploying the frontend to Vercel instead, DO NOT use this
# file — skip it entirely and let Vercel run `npm run build` and serve
# the static output via its own CDN. This file is provided for the
# self-hosted alternative path only.

# ---- Stage 1: build the static assets ----
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite reads VITE_* vars, CRA reads REACT_APP_* vars, at BUILD time —
# they get baked into the JS bundle, so pass them as build args if the
# API base URL needs to differ per environment/build.
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}

RUN npm run build

# ---- Stage 2: serve with Nginx ----
FROM nginx:1.27-alpine AS serve

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
