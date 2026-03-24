# Personal Jira

A containerized full-stack web application for project management with AI agent integration.

## Tech Stack

- **Backend**: Python (FastAPI)
- **Frontend**: TypeScript (React, Vite)
- **Database**: PostgreSQL 16
- **Infrastructure**: Docker Compose, nginx, GitHub Actions

## Directory Structure

```
.
├── backend/          # Python API server (FastAPI)
├── frontend/         # Frontend SPA (React + Vite)
├── .github/          # GitHub Actions CI/CD workflows
├── .editorconfig     # Editor configuration
├── .env.example      # Environment variable template
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## Local Development

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Start services:
   ```bash
   docker compose up -d
   ```

3. Run tests:
   ```bash
   pytest
   ```
