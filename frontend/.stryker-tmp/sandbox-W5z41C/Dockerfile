# syntax=docker/dockerfile:1
# Stage 1: build — compile TypeScript and bundle assets
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# Stage 2: serve — nginx serving the static SPA
FROM nginx:alpine AS runtime

# Remove default nginx config and replace with SPA config
RUN rm /etc/nginx/conf.d/default.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
