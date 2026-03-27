# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy lock file first so Docker layer caching works correctly
COPY frontend/package.json frontend/package-lock.json ./

# npm ci uses the exact versions in package-lock.json — reproducible and fast
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build


# ── Stage 2: FastAPI runtime ───────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ENV PORT=8080
EXPOSE 8080

# FastAPI serves the pre-built React SPA + all /api/* routes
CMD exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT
