# TickerTracker Frontend — Development Dockerfile
# Node 20 Alpine, runs Vite dev server with HMR on port 3000
FROM node:20-alpine

WORKDIR /app

# Install dependencies first (cached layer)
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000

# Start Vite dev server
# VITE_API_TARGET env var is injected by docker-compose to point to the backend service
CMD ["npm", "run", "dev"]
