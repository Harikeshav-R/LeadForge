<<<<<<< HEAD
# LeadForge

AI-Powered Sales Development Representative Platform

LeadForge automates and assists outbound sales workflows — from lead ingestion and enrichment through personalized outreach sequencing to intelligent reply handling and pipeline logging. This repository contains backend and frontend components, orchestration tooling, deployment helpers, and integration guides.

- Repository: https://github.com/Harikeshav-R/LeadForge
- Primary languages (approx.): Python (51%), TypeScript (30.9%), HTML (14%)
- Key top-level files & directories:
  - .env.dev.example — development environment variables template
  - .env.prod.example — production environment variables template
  - docker-compose.dev.yml — development compose stack
  - docker-compose.prod.yml — production compose stack
  - Makefile — common targets and developer commands
  - init-db.sh — DB initialization script
  - INTEGRATION_SUMMARY.md — summary of integrated providers
  - OUTREACH_INTEGRATION_GUIDE.md — outreach integration guide
  - backend/ — Python backend code and services
  - frontend/ — TypeScript frontend code (likely React/Next/Vite)
  - builder/ — builder service(s)
  - deployer/ — deployer service(s)
  - leads/ — lead ingestion/enrichment code
  - outreach/ — outreach & sequencing code
  - LICENSE

This README documents what I found in the repo, how to get started, environment variables (taken from .env.dev.example), recommended local workflows, and where to look for more detailed docs already included in the repository.

Table of contents
- Project overview
- What’s in this repository
- Quickstart — local development (docker-based)
- Local developer setup (non-docker)
- Environment variables (.env templates)
- Running services
- Common operations & Makefile
- Database initialization
- Integrations & guides
- Troubleshooting
- Contributing & license

Project overview
LeadForge provides an AI-first SDR platform that automates high-volume, personalized outreach while capturing replies and pipeline state. Typical components (present in this repo) include:
- backend: API, orchestration, workers, LLM orchestration (Python)
- frontend: UI/dashboard and operator tooling (TypeScript / HTML)
- builder & deployer: services to build and deploy frontends/sites
- leads & outreach: domain logic around lead ingestion, enrichment, and outreach sequencing

What’s in this repository (high-level)
- backend/ — the Python backend application built with FastAPI. Look here for API routes, dependency injection, background worker startup, and AI orchestration (LLM client integrations and prompt/template logic).
- frontend/ — the TypeScript UI application (dashboard and operator tooling). Inspect frontend/package.json to discover scripts (install, dev, build) and to confirm whether it uses React/Next/Vite.
- builder/ & deployer/ — services that build and deploy site artifacts (static site builds, packaging, and deployment hooks used by the orchestration).
- leads/ & outreach/ — domain subprojects focused on lead ingestion, enrichment, lead-models, campaign sequencing, and outreach channel adapters (email, SMS, voice, and webhooks).
- docker-compose.dev.yml & docker-compose.prod.yml — Docker Compose stacks to spin up the full system (PostgreSQL, Redis if present, backend API, frontend, builder/deployer, and worker services).
- init-db.sh — helper script that bootstraps required PostgreSQL databases and users for local/dev environments and CI.
- .env.dev.example & .env.prod.example — environment variable templates. Use them to create .env for local development or to drive production deployments (contains POSTGRES_* DB settings, LLM provider keys, Twilio and email settings, and other runtime configuration).
- INTEGRATION_SUMMARY.md & OUTREACH_INTEGRATION_GUIDE.md — integration documentation and provider-specific setup steps (e.g., Twilio, SMTP, LLM providers like Gemini/OpenAI, and CRM connectors).


Quickstart — recommended (Docker / docker-compose)
The repo includes docker-compose.dev.yml and docker-compose.prod.yml. The quickest path to run an isolated development instance is to use the development compose file.

1. Clone
```bash
git clone https://github.com/Harikeshav-R/LeadForge.git
cd LeadForge
```

2. Copy environment template and fill required variables
```bash
cp .env.dev.example .env
# Edit .env to fill values (DB credentials, API keys, LLM provider keys, Twilio, SMTP, etc.)
```

3. Start development stack (uses docker-compose.dev.yml)
```bash
docker-compose -f docker-compose.dev.yml up --build
```

4. Initialize databases (if needed)
```bash
# local helper script included in repository
./init-db.sh
# or run DB migration command provided by the backend (see backend docs)
```

5. Access services
- Frontend: typically http://localhost:3000 (depends on frontend compose config)
- Backend API: typically http://localhost:8000 (depends on backend compose config)
- Worker logs and other services appear in docker-compose logs

Local developer setup (non-docker)
If you prefer running services locally (Python virtualenv, Node install, Postgres/Redis locally), follow these general steps and adapt them to actual scripts found in backend/ and frontend/:

1. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
# Install dependencies (requirements.txt or pyproject.toml)
pip install -r requirements.txt
# Export environment variables from .env
# Run DB migrations (framework-specific)
# Example (FastAPI + Alembic): alembic upgrade head
# Start dev server (example): uvicorn app.main:app --reload --port 8000
```

2. Frontend
```bash
cd frontend
# Use npm / pnpm / yarn depending on package.json
npm install
npm run dev
# Open http://localhost:3000
```

Environment variables
The repository provides .env.dev.example and .env.prod.example templates. Below is the development template exactly as found in the repository — copy this into .env (and fill the values) or adapt for your environment:

```env
# .env.dev.example (exact contents from repository)
# Set debug mode
DEBUG=true

# PostgreSQL DB Settings
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=

POSTGRES_DB=
POSTGRES_BUILDER_DB=
POSTGRES_DEPLOYER_DB=
POSTGRES_LEADS_DB=
POSTGRES_OUTREACH_DB=

# Deployed sites
DEPLOYED_SITES_DIR=

# API KEYS
GEMINI_API_KEY=
GOOGLE_MAPS_API_KEY=

# LLM Settings
MODEL_NAME=
MODEL_PROVIDER=

# Email Settings
SENDER_EMAIL_ADDRESS=
SENDER_EMAIL_PASSWORD=

# Twilio Settings
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# WebSocket Settings
BASE_WS_URL=
```

Notes about env vars:
- Multiple POSTGRES_* variables indicate the repo uses multiple databases or DBs per component (builder, deployer, leads, outreach). Ensure your DB server contains all required databases or the init script creates them.
- MODEL_PROVIDER and MODEL_NAME indicate LLM provider integration (e.g., OpenAI, Gemini, etc.) — fill with the provider your deployment will use and the model name.
- GEMINI_API_KEY suggests a provider; confirm with integration docs.

Database initialization
- The repository includes init-db.sh to help create required DBs and users. Run this script from the repo root or inspect it for required DB names/credentials.
- If the backend uses a migration system (Alembic, Django migrations), run the corresponding migration command after installing dependencies and connecting to DB.

Docker & production
- docker-compose.prod.yml is provided for production-style composition. Use a secrets manager for production env variables and do not commit secrets to the repo.
- Typical production flow:
  - Build images: docker-compose -f docker-compose.prod.yml build
  - Run: docker-compose -f docker-compose.prod.yml up -d
  - Use the deployer/ components to deploy built frontends to DEPLOYED_SITES_DIR or external hosting.

Makefile
A Makefile exists in the repo root. Typical targets to look for and use:
- make build
- make up / make dev
- make down
- make test
- make lint
Open the Makefile to see exact targets and usage examples.

Integrations & guides
The repository contains two helpful guides:
- INTEGRATION_SUMMARY.md — summary of integrated providers and connectors
  - Link: https://github.com/Harikeshav-R/LeadForge/blob/main/INTEGRATION_SUMMARY.md
- OUTREACH_INTEGRATION_GUIDE.md — outreach integration instructions
  - Link: https://github.com/Harikeshav-R/LeadForge/blob/main/OUTREACH_INTEGRATION_GUIDE.md

These files are your first stop for provider-specific setup (Twilio, SMTP, CRM connectors, LLM provider setup).

API docs and routes
- Check backend/ for route definitions and any auto-generated docs. If the backend uses FastAPI, OpenAPI docs are usually available at /docs or /redoc.
- If you cannot find OpenAPI, look for routers, endpoints, and any README inside backend/.

Developer workflows & CI
- Look in .github/workflows/ if present to learn the CI steps (lint, test, build).
- Use the Makefile for standard local tasks. If you run into test failures, run with verbose flags and inspect the logs in the backend and worker containers.

Troubleshooting tips
- If services fail to connect to DB: double-check POSTGRES_* variables in .env and run init-db.sh.
- If LLM calls fail: ensure MODEL_PROVIDER, MODEL_NAME, and API keys like GEMINI_API_KEY are set and valid.
- If emails are not delivered: check SENDER_EMAIL_* credentials and SMTP provider restrictions (sandbox, 2FA).
- If Twilio calls/texts fail: confirm TWILIO_* vars and that the phone number is provisioned.

Security & secrets
- Do not commit .env with real credentials. Use your environment, Docker secrets, or a secret manager for production.
- Protect API keys and LLM provider keys; set strict access controls.

What to inspect next in the repo (where to find exact commands & endpoints)
- backend/:
  - requirements.txt or pyproject.toml — exact Python dependencies
  - entrypoint (app/main.py or manage.py) — exact command to run the server
  - migrations/ or alembic/ — migration tooling and DB schema
  - worker configuration (celery.py, rq worker, etc.) — how to run background jobs
- frontend/:
  - package.json — install/build/start/test scripts and the package manager used
  - next.config.js / vite.config.js — build configuration
- dockerfiles:
  - Look inside backend/, frontend/, builder/, deployer/ for Dockerfile(s) to learn image build steps
- Makefile — exact target names and commands
- init-db.sh — what DBs/tables are created and which user is required

Contributing
- Add a CONTRIBUTING.md to define contribution process (PR style, code style, tests).
- Follow repository coding standards and run lint/test targets before submitting PRs.

License
- This repository includes a LICENSE file. Inspect it to see the precise license (e.g., MIT, Apache-2.0).

Useful links (from repository)
- Root README (this file): https://github.com/Harikeshav-R/LeadForge/blob/main/README.md
- .env.dev.example: https://github.com/Harikeshav-R/LeadForge/blob/main/.env.dev.example
- INTEGRATION_SUMMARY.md: https://github.com/Harikeshav-R/LeadForge/blob/main/INTEGRATION_SUMMARY.md
- OUTREACH_INTEGRATION_GUIDE.md: https://github.com/Harikeshav-R/LeadForge/blob/main/OUTREACH_INTEGRATION_GUIDE.md
- init-db.sh: https://github.com/Harikeshav-R/LeadForge/blob/main/init-db.sh
- docker-compose.dev.yml: https://github.com/Harikeshav-R/LeadForge/blob/main/docker-compose.dev.yml
- docker-compose.prod.yml: https://github.com/Harikeshav-R/LeadForge/blob/main/docker-compose.prod.yml

---

If you want, I can refine this README to include:
- Exact backend start/migration commands (extracted from backend/ files)
- Exact frontend build/start commands and port information (extracted from frontend/package.json)
- Precise Makefile targets and example usage
- A generated API reference (endpoints, request examples) from backend route definitions

To do that I will need the files listed in the "What to inspect next" section (or repo read access). Thank you — this README is based on the files currently present in the repository (including the .env.dev.example and top-level structure).````
=======
# HackOHIO
AI Powered Sales Development Representative System
>>>>>>> main-holder
