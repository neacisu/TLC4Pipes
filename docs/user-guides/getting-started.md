# Getting Started Guide

## Prerequisites
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

## Quick Start (Production/Demo)

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/neacisu/TLC4Pipes.git
    cd TLC4Pipes
    ```

2.  **Run with Docker Compose**
    ```bash
    cd docker
    docker-compose up --build -d
    ```

3.  **Access the Application**
    - Open browser: `http://localhost`
    - API Documentation: `http://localhost:8000/docs`

## Development Environment Setup

### Backend (Python/FastAPI)
1.  Navigate to `backend/`.
2.  Create env: `python -m venv .venv`
3.  Activate: `source .venv/bin/activate`
4.  Install: `pip install -r requirements-dev.txt`
5.  Run: `uvicorn app.main:app --reload` (Port 8000)

### Frontend (React)
1.  Navigate to `frontend/`.
2.  Install: `pnpm install`
3.  Run: `pnpm dev` (Port 5173)

### Database
Ensure a local PostgreSQL instance is running or use `docker-compose up db`.
Configure `.env` with `DATABASE_URL`.
