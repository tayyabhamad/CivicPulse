# syntax=docker/dockerfile:1
FROM node:22.12.0-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# The unprivileged official image runs as nginx (UID 101) and listens on 8080.
FROM nginxinc/nginx-unprivileged:1.27.3-alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 8080
