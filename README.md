# AI Optimizer

A full-stack application with FastAPI async backend and Next.js frontend, designed for building AI agent workflows using OpenAI's Agents SDK.

## Project Structure

```
aioptimizer/
├── backend/              # FastAPI async backend
│   ├── models/          # SQLAlchemy 2.0 ORM models
│   │   ├── __init__.py  # Database engine & session
│   │   └── user.py      # User model
│   ├── routers/         # API endpoints
│   │   ├── api.py       # Health check
│   │   └── user.py      # User CRUD endpoints
│   ├── schemas/         # Pydantic schemas
│   │   ├── request/     # Request models
│   │   └── response/    # Response models
│   ├── services/        # Business logic layer
│   │   └── user_service.py  # User service with DI
│   ├── dependencies/    # Dependency injection
│   │   └── __init__.py  # DB session & service deps
│   ├── migrations/      # Alembic database migrations
│   ├── tests/          # Backend tests
│   ├── main.py         # FastAPI app entry point
│   └── settings.py     # Configuration
├── frontend/           # Next.js frontend
│   ├── app/           # Next.js app directory
│   ├── components/    # React components
│   └── lib/          # Utilities and helpers
├── docker-compose.yml
├── AGENTS.md          # OpenAI Agents SDK documentation
└── CLAUDE.md          # Claude Code setup guide
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- Poetry
- MySQL 8.0
- Redis

### Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Copy environment variables
cp .env.example .env
# Edit .env with your database credentials and OpenAI API key

# Run database migrations
poetry run alembic upgrade head

# Start the server
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### Docker Setup

```bash
# Start all services (MySQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Async ORM with type hints
- **Alembic** - Database migrations
- **aiomysql** - Async MySQL driver
- **OpenAI Agents SDK** - Multi-agent workflow framework
- **Pydantic v2** - Data validation
- **Python 3.13** - Latest Python version

### Frontend
- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **Zustand** - State management
- **TanStack Query** - Data fetching & caching
- **Axios** - HTTP client

## Architecture Patterns

### Layered Architecture
```
Controllers (Routers) → Services → Models → Database
```

### Dependency Injection
Services are injected into route handlers using FastAPI's `Depends()`:

```python
@router.get("/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_by_id(user_id)
```

### Async/Await Throughout
- Async database sessions
- Async route handlers
- Async service methods
- Async OpenAI Agent workflows

## Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

## Code Quality

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Configured tools:
- Black (code formatting)
- isort (import sorting)
- Ruff (linting)
- mypy (type checking)
- ESLint (frontend linting)

## Development Workflow

1. Create a feature branch
2. Make changes
3. Run tests: `poetry run pytest`
4. Commit (pre-commit hooks run automatically)
5. Push and create PR

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### Users
- `GET /users` - List all users (paginated)
- `GET /users/{user_id}` - Get user by ID
- `POST /users` - Create new user
- `PATCH /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

## Environment Variables

### Backend (.env)
```bash
RELEASE_STAGE=local
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_NAME=aioptimizer
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Frontend - Cloudflare Pages

The frontend is automatically deployed to Cloudflare Pages via GitHub integration on every push to `master`.

**Production URL**: https://aioptimizer.pages.dev/

#### Cloudflare Pages Setup

Cloudflare Pages is configured to:
- Watch the GitHub repository: `synweap15/aioptimizer`
- Production branch: `master`
- Build command: `npm run build`
- Build output directory: `.next`
- Root directory: `frontend`

#### Manual Deployment

```bash
# Switch to Node.js v24
nvm use v24

# Build and deploy
cd frontend
npm run build
CLOUDFLARE_ACCOUNT_ID=d371c76d7e486fbae757ae73a6349bc6 wrangler pages deploy .next --project-name=aioptimizer
```

#### Cloudflare Account

- Account ID: `d371c76d7e486fbae757ae73a6349bc6`
- Account: Shamdog+cloudflare@gmail.com's Account
- Project: aioptimizer

### Backend - Docker/VPS Deployment

Backend can be deployed using Docker:

```bash
# Production deployment
docker-compose -f docker-compose.production.yml up -d
```

Or manually on a VPS:

```bash
cd backend
poetry install --no-dev
poetry run alembic upgrade head
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Next.js Documentation](https://nextjs.org/docs)
- See [AGENTS.md](./AGENTS.md) for OpenAI Agents SDK guide
- See [CLAUDE.md](./CLAUDE.md) for Claude Code setup

## License

MIT
