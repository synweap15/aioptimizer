# Claude Code Setup Guide

This document provides guidance for using Claude Code (Anthropic's AI coding assistant) with this project.

## Project Overview

**AI Optimizer** is an SEO investigation and optimization platform powered by AI agents.

### Purpose
The platform autonomously investigates websites, researches competitors, and provides actionable SEO recommendations. It uses OpenAI's Agents SDK to enable agents to:
- Fetch and analyze webpage content
- Query Google for keyword research
- Compare competitor strategies
- Generate prioritized optimization recommendations

### Tech Stack
- **Backend**: FastAPI async with SQLAlchemy 2.0, OpenAI Agents SDK
- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, Zustand
- **External APIs**: SerpAPI (Google search), OpenAI (GPT-4o agents)
- **Deployment**: Cloudflare Workers (frontend), VPS/Docker (backend)

## Architecture Patterns

### Backend Architecture

**Layered Architecture with Agent Integration:**
```
Routers → Services → OpenAI Agents → External APIs
              ↓
           Models → Database
```

**Key Patterns:**
1. **Dependency Injection**: Services injected via `Depends()`
2. **Async/Await**: All database operations and route handlers are async
3. **SQLAlchemy 2.0**: Uses `Mapped` and `mapped_column` for type safety
4. **Service Layer**: Business logic separated from route handlers
5. **Multi-Agent Orchestration**: OpenAI Agents SDK for autonomous workflows
6. **SSE Streaming**: Real-time progress updates via Server-Sent Events

### Example Service with DI

```python
# services/user_service.py
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

# dependencies/__init__.py
def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)

# routers/user.py
@router.get("/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_by_id(user_id)
```

## Code Style Guidelines

### Python (Backend)

**Follow these conventions:**

1. **Type Hints**: Always use type hints with SQLAlchemy 2.0 `Mapped`
```python
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
```

2. **Async/Await**: All database operations must be async
```python
# Good
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# Bad - Never use sync operations
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

3. **Service Layer**: Business logic goes in services, not routers
```python
# Good - Logic in service
class UserService:
    async def create_with_validation(self, email: str, password: str):
        if await self.get_by_email(email):
            return None
        return await self.create(email, password)

# Bad - Logic in router
@router.post("")
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email exists")
    # ...
```

4. **Pydantic Schemas**: Separate request/response models
```python
# schemas/request/user.py
class UserCreateRequest(BaseSchema):
    email: EmailStr
    password: str

# schemas/response/user.py
class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    # No password field!
```

5. **Error Handling**: Use HTTPException with proper status codes
```python
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
```

### Code Formatting

Run before committing:
```bash
cd backend
poetry run black .
poetry run isort .
poetry run ruff check --fix .
poetry run mypy .
```

Or use pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files
```

## Common Tasks for Claude

### 1. Creating a New Model

```
Create a new SQLAlchemy 2.0 model for [entity name] with these fields:
- [field1]: [type and constraints]
- [field2]: [type and constraints]

Follow the User model pattern in backend/models/user.py
Use Mapped[] type hints and proper relationships if needed.
```

### 2. Creating a New Service

```
Create a service for [entity name] following the UserService pattern:
- Include CRUD operations (create, get_by_id, get_all, update, delete)
- Use dependency injection pattern
- Add to dependencies/__init__.py

Location: backend/services/[entity]_service.py
```

### 3. Creating a New Router

```
Create REST API endpoints for [entity name]:
- GET /[entities] - List with pagination
- GET /[entities]/{id} - Get by ID
- POST /[entities] - Create
- PATCH /[entities]/{id} - Update
- DELETE /[entities]/{id} - Delete

Use service dependency injection.
Location: backend/routers/[entity].py
```

### 4. Creating Schemas

```
Create Pydantic schemas for [entity name]:
- Request schemas in backend/schemas/request/[entity].py
- Response schemas in backend/schemas/response/[entity].py

Follow the user schema pattern.
```

### 5. Database Migrations

```
I've created/modified the [Model] model. Please:
1. Generate an Alembic migration
2. Review the migration file
3. Apply it to the database

Use: alembic revision --autogenerate -m "description"
```

### 6. OpenAI Agents Implementation

```
Create an OpenAI Agent for [use case]:
- Create agent service in backend/services/[name]_service.py
- Include tools: [list of tools]
- Add router endpoints for running the agent
- Use async/await patterns
- Implement SSE streaming for real-time updates

See AGENTS.md for reference patterns.
See InvestigationService for complete agent implementation example.
```

## Project-Specific Context

### SEO Investigation Agent System

The core feature uses a multi-agent system (`backend/services/investigation_service.py`):

**1. Web Investigator Agent** - Has tools to:
- `search_google(query, location)` - Query Google via SerpAPI
- `fetch_url_content(url)` - Fetch and parse webpage content

**2. SEO Analyzer Agent**
- Analyzes investigation data
- Identifies SEO opportunities

**3. SEO Optimizer Agent**
- Generates actionable recommendations
- Can hand off to Analyzer if needed

**API Endpoint:**
```python
POST /investigate
{
  "url": "https://example.com",
  "keywords": ["seo", "optimization"],
  "location": "United States"
}

# Returns SSE stream with real-time progress
```

**Tool Pattern for Agents:**
```python
def search_google(query: str, location: str = "United States") -> str:
    """Tool function for agent - must return string (JSON)"""
    # Tool logic here
    return json.dumps(results)

agent = Agent(
    name="Investigator",
    instructions="...",
    tools=[search_google, fetch_url_content],
    model="gpt-4o",
)
```

### Database Configuration

- **Engine**: Async SQLAlchemy with aiomysql
- **Connection Pool**: 24 connections, 48 max overflow
- **Lifecycle**: Managed via FastAPI lifespan events
- **Location**: `backend/models/__init__.py`

### Authentication Pattern

When implementing auth:
1. Use `passlib` with bcrypt for password hashing
2. JWT tokens with `python-jose`
3. Store hashed passwords, never plain text
4. See `UserService.authenticate()` for reference

### Testing Pattern

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/users",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
```

## File Locations

### Backend
```
backend/
├── models/          # Database models (SQLAlchemy)
├── services/        # Business logic
├── routers/         # API endpoints
├── schemas/
│   ├── request/    # Request validation
│   └── response/   # Response serialization
├── dependencies/    # Dependency injection
├── migrations/      # Alembic migrations
└── tests/          # Test files
```

### Frontend
```
frontend/
├── app/            # Next.js pages and layouts
├── components/     # React components
└── lib/           # Utilities
```

## Common Issues

### 1. Import Errors

**Problem**: Circular imports between models and dependencies

**Solution**: Use lazy imports in dependencies:
```python
def get_user_service(db: AsyncSession = Depends(get_db)):
    from services.user_service import UserService  # Import here
    return UserService(db)
```

### 2. Async Session Errors

**Problem**: "AsyncSession object has no attribute 'query'"

**Solution**: Don't use legacy query API, use select():
```python
# Good
stmt = select(User).where(User.id == user_id)
result = await db.execute(stmt)

# Bad
result = db.query(User).filter(User.id == user_id)  # Not async
```

### 3. Pydantic Validation Errors

**Problem**: "model_validate() missing 1 required positional argument"

**Solution**: Use `.model_validate()` not `from_orm()`:
```python
# Good (Pydantic v2)
return UserResponse.model_validate(user)

# Bad (Pydantic v1)
return UserResponse.from_orm(user)
```

## Environment Setup

### Required Environment Variables

Backend requires these in `.env`:
```bash
# Database
DATABASE_HOST=localhost
DATABASE_PASSWORD=your_password
DATABASE_NAME=aioptimizer

# AI & External APIs (REQUIRED for investigation)
OPENAI_API_KEY=sk-...              # OpenAI API for agents
SERPAPI_API_KEY=...                # SerpAPI for Google search

# Security
SECRET_KEY=your-secret-key
```

### Running the Project

```bash
# Backend
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker (everything)
docker-compose up -d
```

## Best Practices for AI Assistance

### When Asking for Help

1. **Be Specific**: "Create a User model with email and password" ✓
2. **Reference Patterns**: "Follow the UserService pattern" ✓
3. **Include Context**: "This is for authentication" ✓
4. **Specify Location**: "In backend/models/user.py" ✓

### What to Review

When Claude generates code, always check:
1. **Async/Await**: All DB operations are async
2. **Type Hints**: Proper use of `Mapped[]` in models
3. **Imports**: Correct and not circular
4. **Error Handling**: Proper HTTP exceptions
5. **Security**: No plain text passwords, proper validation

## Deployment (Cloudflare Workers)

### Important: Pages → Workers Migration (2025)

Cloudflare has transitioned from Pages to Workers for static sites. The project uses **Cloudflare Workers** with static assets.

**Key Configuration:**

```toml
# frontend/wrangler.toml
name = "aioptimizer"
main = "src/index.js"
compatibility_date = "2025-01-17"
account_id = "d371c76d7e486fbae757ae73a6349bc6"

[assets]
directory = ".next/static"
binding = "ASSETS"
```

**Deploy Command (Cloudflare Dashboard):**
- Build command: `npm run build`
- Deploy command: `npx wrangler deploy` ⚠️ **REQUIRED** (NOT `wrangler pages deploy`)
- Root directory: `frontend`
- Environment: `NODE_VERSION=24`

**Manual Deployment:**
```bash
cd frontend
npm run build
CLOUDFLARE_ACCOUNT_ID=d371c76d7e486fbae757ae73a6349bc6 wrangler deploy
```

**Differences from Pages:**
- Uses `main` field (Worker entry point) instead of `pages_build_output_dir`
- Uses `[assets]` section for static files
- Deploy with `wrangler deploy` (NOT `wrangler pages deploy`)
- Access to Workers features: Durable Objects, Cron Triggers, etc.

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide.

## Resources

- **Project README**: See [README.md](./README.md)
- **Deployment Guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **OpenAI Agents**: See [AGENTS.md](./AGENTS.md)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Pydantic v2**: https://docs.pydantic.dev/2.0/
- **Cloudflare Workers**: https://developers.cloudflare.com/workers/

## Quick Reference Commands

```bash
# Backend
poetry add <package>                    # Add dependency
poetry run pytest                       # Run tests
poetry run alembic upgrade head         # Run migrations
poetry run black .                      # Format code

# Frontend
npm install <package>                   # Add dependency
npm run dev                            # Start dev server
npm run build                          # Build for production

# Cloudflare Deployment (use Node v24)
nvm use v24
wrangler deploy                        # Deploy to Workers

# Git
git add .                              # Stage changes
git commit -m "message"                # Commit (runs pre-commit)
git push                               # Push to GitHub

# Docker
docker-compose up -d                   # Start services
docker-compose logs -f                 # View logs
docker-compose down                    # Stop services
```

## Tips for Efficient Development

1. **Use the Service Layer**: Don't put business logic in routers
2. **Follow the Patterns**:
   - User CRUD: `UserService` pattern
   - Agent workflows: `InvestigationService` pattern
   - SSE streaming: `POST /investigate` pattern
3. **Test as You Go**: Write tests for new features
4. **Commit Often**: Small, focused commits with descriptive messages
5. **Use Type Hints**: They help catch errors early
6. **Agent Tools**: Return JSON strings, keep functions synchronous (use executor if needed)

## Project Goals & Assumptions

### Core Goal
Build an AI-powered SEO investigation platform where agents autonomously:
1. Fetch and analyze target website content
2. Research Google rankings and competitors
3. Generate actionable SEO recommendations
4. Stream real-time progress to users

### Key Assumptions
- Agents have web research capabilities (Google search, webpage fetching)
- Users want real-time progress updates (SSE streaming)
- Investigations are compute-intensive (async throughout)
- Results should be actionable and prioritized by impact
- System should be extensible (easy to add more agent tools)

### Future Direction
- Store investigation history in database
- Build frontend UI for investigation requests
- Add more SEO analysis tools (Lighthouse, backlinks, etc.)
- Implement caching and rate limiting
- Add authentication for user-specific investigations

## Getting Help

When stuck, ask Claude:
- "How does [feature] work in this project?"
- "Show me an example of [pattern] from the codebase"
- "What's wrong with this code?" (provide the code and error)
- "How would you implement [feature] following this project's patterns?"

Remember: Claude has full context of the project structure and patterns. Reference existing implementations when asking for help!
