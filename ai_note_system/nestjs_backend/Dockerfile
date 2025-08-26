# Multi-stage Dockerfile for NestJS backend
# Build stage
FROM node:20-bullseye-slim AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Runtime stage
FROM node:20-bullseye-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

# Install only production deps
COPY --from=builder /app/package*.json ./
RUN npm install --omit=dev

# Copy built artifacts
COPY --from=builder /app/dist ./dist

# Optional: include example env for reference
COPY --from=builder /app/.env.example ./.env.example

# Stub directory for Oracle Wallet (can be mounted in K8s)
RUN mkdir -p /opt/oracle/wallet

ENV PORT=3000
EXPOSE 3000

CMD ["node", "dist/main.js"]
