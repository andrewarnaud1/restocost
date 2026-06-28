# RestoCost 🍽️

[![CI/CD Status](https://github.com/andrewarnaud1/restocost/actions/workflows/ci.yml/badge.svg)](https://github.com/andrewarnaud1/restocost/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)

**Production-ready restaurant cost management system** - Calculate recipe costs, manage suppliers, and optimize menu pricing.

**Status:** 🟢 **Development** - Sprint 1: Infrastructure & Auth

## ✨ Features (Planned)

### Core Features
- 📊 **Recipe Cost Calculation** - Automatic cost calculations with waste percentages
- 🏪 **Supplier Management** - Manage suppliers and ingredient pricing (mercuriale)
- 💰 **Menu Pricing** - Calculate optimal menu prices based on costs
- 🧾 **Quote Generation** - Generate quotes with custom overrides per supplier
- 📈 **Cost Analytics** - Track cost trends and optimize purchasing

### Quality & DevOps
- 🛡️ **Type Safety** - 100% TypeScript strict mode + Pyright
- ✅ **Test Coverage** - 80%+ enforced via GitHub Actions
- 🔒 **Security** - Pre-commit hooks, Bandit, Safety, npm audit
- 🤖 **AI-Powered Development** - Claude Code for automated features & fixes
- 🐳 **Docker** - Containerized backend & PostgreSQL
- 📚 **Documentation** - Auto-generated API docs

## 🛠️ Tech Stack

### Backend
| Component | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.136.1 | Web framework (Python 3.13+) |
| **SQLAlchemy** | 2.0.30+ | ORM & database abstraction |
| **Pydantic** | 2.13.3+ | Data validation & serialization |
| **PostgreSQL** | 16 | Production database |
| **asyncpg** | 0.30+ | Async PostgreSQL driver |
| **Alembic** | 1.14+ | Database migrations |

### Frontend
| Component | Version | Purpose |
|-----------|---------|---------|
| **React** | 19.0-rc.1 | UI framework |
| **TypeScript** | 5.5.4 | Type-safe JavaScript |
| **Vite** | 5.4.10 | Build tool & dev server |
| **TailwindCSS** | 4.3.1 | Utility-first CSS |
| **React Query** | 5.60.0 | Server state management |
| **Zustand** | 4.5.5 | Client state management |

### DevOps & Quality
| Component | Version | Purpose |
|-----------|---------|---------|
| **GitHub Actions** | - | CI/CD pipeline |
| **Docker** | latest | Containerization |
| **Pytest** | 8.3+ | Testing framework |
| **Pyright** | 1.1.391+ | Type checking (strict) |
| **Ruff** | 0.6.5+ | Fast linting |
| **ESLint** | 9.17+ | TypeScript/JS linting |
| **Claude Code** | - | AI-powered development |

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** ([Download](https://www.python.org/downloads/))
- **Node.js 20+ LTS** ([Download](https://nodejs.org/))
- **PostgreSQL 16** ([Download](https://www.postgresql.org/download/) or use Docker)
- **Git** ([Download](https://git-scm.com/))

### Backend Setup

```bash
# Clone repository
git clone https://github.com/andrewarnaud1/restocost.git
cd restocost

# Create Python virtual environment
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e backend[dev]

# Setup database (Docker)
docker-compose up -d postgres

# Run migrations
cd backend
alembic upgrade head

# Create super admin (FIRST TIME ONLY)
python create_admin.py
# Follow prompts to create admin account

# Start backend
uvicorn app.main:app --reload
# API available at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

> 📖 **See [User Management Guide](./backend/docs/USER_MANAGEMENT.md) for complete user creation documentation**

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm ci

# Start development server
npm run dev
# Available at: http://localhost:5173
```

### Quality Checks

```bash
# Backend quality checks
cd backend
pyright app              # Type checking (strict)
ruff check .            # Linting
black --check .         # Code formatting
pytest --cov=app        # Tests + coverage

# Frontend quality checks
cd ../frontend
npm run type-check      # TypeScript strict
npm run lint            # ESLint
npm run build           # Production build
npm test                # Unit tests
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks (from project root)
pip install pre-commit
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

## 📁 Project Structure

```
restocost/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── api/
│   │   │   └── endpoints/       # Route handlers
│   │   ├── core/
│   │   │   └── security.py      # JWT, bcrypt
│   │   ├── db/
│   │   │   └── session.py       # SQLAlchemy session
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # Business logic
│   ├── tests/                   # Pytest tests
│   ├── migrations/              # Alembic migrations
│   └── pyproject.toml           # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── api/                 # API client
│   │   ├── stores/              # Zustand state
│   │   └── types/               # TypeScript types
│   ├── package.json             # Node dependencies
│   └── vite.config.ts           # Vite configuration
│
├── .github/
│   └── workflows/
│       ├── ci.yml               # CI/CD pipeline
│       ├── claude.yml           # Claude Code for features
│       └── claude-review.yml    # Claude Code for reviews
│
├── CLAUDE.md                    # Claude Code conventions
├── .pre-commit-config.yaml      # Pre-commit hooks
├── docker-compose.yml           # Local database setup
└── README.md                    # This file
```

## 📚 Documentation

- **[User Management Guide](./backend/docs/USER_MANAGEMENT.md)** - Complete guide for creating and managing users
- **[Architecture](./docs/ARCHITECTURE.md)** - System design & component overview
- **[Setup Guide](./docs/SETUP.md)** - Detailed local development setup
- **[API Reference](./docs/API.md)** - FastAPI endpoints documentation
- **[Database Schema](./docs/DATABASE.md)** - Entity relationships & migrations
- **[Claude Code Guide](./CLAUDE.md)** - AI-powered development conventions

## 🔄 Development Workflow

### 1. **Create an Issue**
Every feature/fix starts with a GitHub issue:
- `[FEATURE-NNN]` for new features
- `[BUG-NNN]` for bug fixes
- `[INFRA-NNN]` for infrastructure

Example: `[FEATURE-001] Add user authentication`

### 2. **Create a Feature Branch**
```bash
git checkout -b feature/FEATURE-001-user-auth
```

### 3. **Develop & Test**
- Write code following project conventions
- Run pre-commit hooks: `pre-commit run --all-files`
- Run tests: `pytest` (backend) & `npm test` (frontend)
- Ensure coverage stays >80%

### 4. **Commit & Push**
```bash
git add .
git commit -m "feat: add user authentication with JWT"
git push origin feature/FEATURE-001-user-auth
```

### 5. **Create Pull Request**
- Link to issue: "Closes #123"
- Wait for CI/CD to pass ✅
- Request review
- Merge when approved

## 🤖 Claude Code Integration

This project uses **Claude Code** for automated feature development and code reviews.

### Commands in Issues/PRs

#### For Features/Fixes
```
@claude Please implement [FEATURE-001] User Authentication
Follow the conventions in CLAUDE.md
```

Claude will:
- ✅ Read CLAUDE.md for project conventions
- ✅ Create a feature branch
- ✅ Implement the feature
- ✅ Run tests & linters
- ✅ Create a pull request

#### For Code Reviews
```
@claude-review
```

Claude will:
- ✅ Review code for style & security
- ✅ Check type safety
- ✅ Verify test coverage
- ✅ Provide actionable feedback

## 🛡️ Code Quality Standards

### Type Safety
- **TypeScript**: Strict mode (`tsconfig.json`)
- **Python**: Pyright strict mode (100% coverage)
- **No `any` types** in TypeScript
- **All functions typed** with return types

### Testing
- **Coverage**: 80%+ enforced
- **Unit tests**: For all services
- **Integration tests**: For API endpoints
- **Test naming**: `test_<function>_<scenario>`

### Linting & Formatting
- **Backend**: Ruff + Black + isort
- **Frontend**: ESLint + Prettier
- **Pre-commit hooks**: Run automatically on commit

### Security
- **Secrets detection**: detect-secrets
- **Dependency scanning**: Safety (Python) + npm audit
- **No hardcoded credentials**
- **All passwords hashed with bcrypt**

### Documentation
- **Docstrings**: All public functions
- **Type hints**: All parameters & returns
- **Comments**: Complex logic only
- **API docs**: Auto-generated from docstrings

## 🧪 Running Tests

### Backend
```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py::test_login_success
```

### Frontend
```bash
cd frontend

# Run all tests
npm test

# Run specific test file
npm test -- src/components/Login.test.tsx

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

## 🐳 Docker

### Development
```bash
# Start PostgreSQL
docker-compose up -d

# Check logs
docker-compose logs postgres

# Stop
docker-compose down
```

### Production (Planned)
```bash
# Build images
docker build -t restocost-backend ./backend
docker build -t restocost-frontend ./frontend

# Run containers
docker run -p 8000:8000 restocost-backend
docker run -p 80:5173 restocost-frontend
```

## 📊 CI/CD Pipeline

GitHub Actions runs on every push/PR:

| Job | Status | Purpose |
|-----|--------|---------|
| **Backend Tests** | ✅ | Pyright + Ruff + Pytest |
| **Frontend Tests** | ✅ | TypeScript + ESLint + Vitest |
| **Security Scan** | ✅ | Bandit + Safety + npm audit |
| **Docker Build** | ✅ | Build & scan images |

All checks must pass before merging to `main`.

## 🤝 Contributing

1. **Check open issues** - Find something to work on
2. **Create feature branch** - `git checkout -b feature/ISSUE-NNN`
3. **Follow conventions** - See [CLAUDE.md](./CLAUDE.md)
4. **Run checks** - `pytest`, `npm test`, pre-commit hooks
5. **Create PR** - Link to issue, wait for CI/CD
6. **Get approved** - Respond to review feedback
7. **Merge** - Congratulations! 🎉

## 📝 Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code refactoring (no feature change)
- `test:` Adding/updating tests
- `docs:` Documentation changes
- `chore:` Build, dependencies, tooling
- `ci:` CI/CD changes

### Examples
```
feat(auth): add JWT token refresh endpoint
fix(recipe): correct cost calculation for waste percentage
docs(api): add authentication examples to API docs
test(costing): add unit tests for service
```

## 🐛 Debugging

### Backend
```bash
# With logs
LOGLEVEL=DEBUG uvicorn app.main:app --reload

# With debugger
import pdb; pdb.set_trace()

# With ipdb (better)
import ipdb; ipdb.set_trace()
```

### Frontend
```bash
# Browser DevTools
F12 or Cmd+Option+I

# React DevTools browser extension
# Redux DevTools browser extension (if using Redux)

# VS Code Debugger
# Add launch.json and set breakpoints
```

## 📦 Deployment

Deployment is planned for **Sprint 4**. Supported platforms:
- Railway ([railway.app](https://railway.app))
- Render ([render.com](https://render.com))
- Heroku ([heroku.com](https://www.heroku.com))
- AWS/GCP (advanced setup)

## 📈 Project Roadmap

### ✅ Sprint 1: Infrastructure & Auth (Current)
- FastAPI + PostgreSQL setup
- JWT authentication
- React + TypeScript setup
- GitHub Actions CI/CD
- Pre-commit hooks

### 🔄 Sprint 2: Core Features
- Ingredient & Supplier models
- Recipe cost calculation
- CRUD endpoints

### 🔄 Sprint 3: Advanced Features
- Quote generation
- Cost analytics
- Frontend integration

### 🔄 Sprint 4: Polish & Deployment
- Complete documentation
- Integration tests
- Production deployment

## 💬 FAQ

**Q: Why Python 3.13?**
A: Latest stable version (Oct 2024) with 5 years of support. Better performance & security patches.

**Q: Why React 19 RC?**  
A: Stable release candidate with new hooks and better performance. Easy to upgrade when stable.

**Q: Can I use the same database for tests?**  
A: No. Tests use SQLite in-memory for speed. Use separate test PostgreSQL if needed.

**Q: How do I update dependencies?**  
A: `pip install --upgrade <package>` (Python) or `npm update` (Node). Test thoroughly afterward.

## 📞 Support

- **Documentation**: See `/docs` directory
- **Issues**: Create GitHub issue for bugs/features
- **Discussions**: Use GitHub Discussions for questions

## 📄 License

MIT License - see [LICENSE](./LICENSE) file

## 👤 Author

**Andrew Arnaud**
- GitHub: [@andrewarnaud1](https://github.com/andrewarnaud1)
- LinkedIn: [andrew-arnaud](https://www.linkedin.com/in/andrew-arnaud/)

---

**Last Updated:** January 2025  
**Current Sprint:** Sprint 1: Infrastructure & Auth  
**Status:** 🟢 Active Development
