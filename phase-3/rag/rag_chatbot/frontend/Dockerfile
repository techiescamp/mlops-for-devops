FROM node:22-slim

WORKDIR /app

ENV REACT_APP_PROXY=/api

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source files
COPY public/ ./public/
COPY src/ ./src/
COPY server.js ./

# Build the React app
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Command to run the server
CMD ["node", "server.js"]