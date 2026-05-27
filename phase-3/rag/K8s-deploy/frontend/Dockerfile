# Stage 1: build React app
FROM node:22-slim AS builder

WORKDIR /app

ENV REACT_APP_PROXY=/api

COPY package*.json ./
RUN npm install

COPY public/ ./public/
COPY src/ ./src/

RUN npm run build

# Stage 2: runtime (prod deps + built assets only)
FROM node:22-slim

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY server.js ./
COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["node", "server.js"]
