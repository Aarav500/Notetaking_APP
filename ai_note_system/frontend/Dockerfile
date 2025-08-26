# Multi-stage Dockerfile for Vite React frontend
# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
# Allow overriding API URL at build time (used by Vite)
ARG VITE_API_URL=http://localhost:3000/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Runtime stage (static file server)
FROM nginx:alpine AS runner
# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback to index.html for client-side routing
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
