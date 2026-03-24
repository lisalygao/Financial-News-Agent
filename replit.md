# Project Overview

A Flask web application configured for deployment to Vertex AI via Docker.

## Structure

- `main.py` — Flask application entry point
- `Dockerfile` — Container definition for Vertex AI deployment
- `requirements.txt` — Python dependencies
- `.dockerignore` — Files excluded from Docker build

## Running Locally (Replit)

The app runs on port 5000 via the "Start application" workflow (`python3 main.py`).

## Deployment (Vertex AI)

The `Dockerfile` is in the project root and ready for publishing to GitHub and deploying on Vertex AI.

- Listens on port 8080 inside the container (set via `PORT` environment variable)
- Uses `python:3.11-slim` base image
- Health check endpoint available at `/health`

## Dependencies

- Flask 2.2.5
- Werkzeug 2.2.3
- numpy 1.24.4
- urllib3 1.26.18
- gunicorn 21.2.0
