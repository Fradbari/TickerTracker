# Multi-stage production build for TickerTracker Frontend

# Stage 1: Build static assets
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve via Nginx
FROM nginx:alpine
# Copy built output from stage 1 to nginx html served folder
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom nginx configuration specifying proxy rules
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
