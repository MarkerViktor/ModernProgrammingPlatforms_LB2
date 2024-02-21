FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install

COPY ./src ./src
COPY ./public ./public
RUN npm run build

FROM nginx:alpine3.18-slim

COPY --from=builder /app/build /frontend
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

VOLUME /storage

EXPOSE 80

ENV HOST=localhost \
    PORT=80 \
    BACKEND_HOST=localhost \
    BACKEND_PORT=8080