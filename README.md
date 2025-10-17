# AI Optimizer

A full-stack application with FastAPI backend and Next.js frontend.

## Project Structure

```
aioptimizer/
├── backend/           # FastAPI backend
│   ├── models/       # SQLAlchemy ORM models
│   ├── routers/      # API endpoints
│   ├── schemas/      # Pydantic request/response schemas
│   ├── services/     # Business logic
│   ├── dependencies/ # Dependency injection
│   ├── tests/        # Backend tests
│   └── main.py       # FastAPI app entry point
├── frontend/         # Next.js frontend
│   ├── app/          # Next.js app directory
│   ├── components/   # React components
│   └── lib/          # Utilities and helpers
└── docker-compose.yml
```

## Getting Started

### Backend

```bash
cd backend
poetry install
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up -d
```

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- Alembic (migrations)
- PyMySQL
- Python 3.13

### Frontend
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Zustand (state management)
- TanStack Query (data fetching)
