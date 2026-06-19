# CLAUDE.md - Project Conventions for AI-Powered Development

This file guides Claude Code on how to develop features in RestoCost. Claude will read this before implementing any feature.

---

## 🎯 Project Overview

**RestoCost** is a production-ready restaurant cost management system.

- **Backend**: FastAPI (Python 3.14+) with async/await
- **Frontend**: React 19 with TypeScript strict mode
- **Database**: PostgreSQL 16 with async SQLAlchemy 2.0
- **Quality**: 100% type-safe, 80%+ test coverage enforced

---

## 🏗️ Architecture

### Backend Structure
```
backend/app/
├── main.py              # FastAPI app initialization
├── dependencies.py      # Centralized dependency injection (get_db, etc.)
├── core/
│   ├── config.py        # Pydantic Settings
│   ├── security.py      # JWT, bcrypt, password hashing
│   ├── exceptions.py    # Custom exceptions
│   └── logger.py        # Logging setup
├── db/
│   └── database.py      # SQLAlchemy Base + session + connection check
├── routers/             # Route handlers (organized by feature)
│   ├── health.py        # Health check endpoints
│   ├── auth.py          # Authentication routes
│   ├── ingredients.py
│   ├── suppliers.py
│   ├── recipes.py
│   └── quotes.py
├── models/              # SQLAlchemy ORM models
│   ├── base.py
│   ├── user.py
│   ├── ingredient.py
│   ├── supplier.py
│   ├── recipe.py
│   └── quote.py
├── schemas/             # Pydantic request/response models
│   ├── user.py
│   ├── ingredient.py
│   └── recipe.py
└── services/            # Business logic (services layer)
    ├── auth_service.py
    ├── ingredient_service.py
    └── costing_service.py
```

### Frontend Structure
```
frontend/src/
├── main.tsx             # React entry point
├── App.tsx              # Root component
├── components/          # Reusable UI components
│   ├── Header.tsx
│   ├── Navigation.tsx
│   └── Layout.tsx
├── pages/               # Page-level components (routing)
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   └── RecipesPage.tsx
├── api/                 # API client functions
│   ├── auth.ts
│   ├── recipes.ts
│   └── index.ts
├── stores/              # Zustand state management
│   ├── authStore.ts
│   └── recipeStore.ts
└── types/               # TypeScript interfaces
    ├── index.ts
    └── api.ts
```

---

## 🔴 Critical Rules - NEVER Violate These

### Type Safety
```python
# ✅ CORRECT
def get_user(user_id: int) -> User:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

# ❌ WRONG - Missing type hints
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()

# ❌ WRONG - Using any
def get_user(user_id: int) -> Any:
    ...
```

### Async/Await
```python
# ✅ CORRECT - Always async for database operations
async def get_user_async(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ❌ WRONG - Blocking call in async context
async def get_user_async(db: AsyncSession, user_id: int):
    return db.query(User).filter(User.id == user_id).first()  # ❌ BLOCKING
```

### Test Coverage
```python
# ✅ CORRECT - Every function tested
def test_get_user_success(db: Session):
    """Test successful user retrieval."""
    user = create_test_user(db)
    result = get_user(db, user.id)
    assert result.id == user.id
    assert result.email == user.email

def test_get_user_not_found(db: Session):
    """Test user not found."""
    result = get_user(db, 99999)
    assert result is None

# ❌ WRONG - No tests
def get_user(db: Session, user_id: int):
    ...  # No tests for this!
```

### Frontend Type Safety
```typescript
// ✅ CORRECT - Full TypeScript types
interface User {
  id: number;
  email: string;
  password: string;
}

async function loginUser(email: string, password: string): Promise<User> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  return response.json();
}

// ❌ WRONG - Using any
function loginUser(email: any, password: any): any {
  ...
}
```

---

## 📝 Code Style & Conventions

### Python Backend

#### Naming Conventions
```python
# Functions and variables: snake_case
def create_user(email: str, password: str) -> User:
    pass

user_id = 123
is_active = True

# Classes: PascalCase
class UserService:
    pass

class AuthenticationException(Exception):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_TOKEN_EXPIRY = 30
```

#### Imports Order
```python
# 1. Standard library
from datetime import datetime
from typing import Optional

# 2. Third-party
from fastapi import FastAPI, Depends
from sqlalchemy import Column, String

# 3. Local
from app.core.config import Settings
from app.models.user import User
from app.dependencies import get_db
```

#### Docstring Format (Google Style)
```python
def create_recipe(
    db: AsyncSession,
    recipe_name: str,
    yield_servings: int,
) -> Recipe:
    """Create a new recipe.
    
    Args:
        db: Database session.
        recipe_name: Name of the recipe.
        yield_servings: Number of servings.
        
    Returns:
        The created Recipe object.
        
    Raises:
        ValueError: If recipe_name is empty.
    """
    if not recipe_name:
        raise ValueError("Recipe name cannot be empty")
    
    recipe = Recipe(name=recipe_name, yield_servings=yield_servings)
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return recipe
```

#### Error Handling
```python
# ✅ CORRECT - Specific exceptions, proper logging
class RecipeNotFoundError(Exception):
    """Raised when recipe is not found."""
    pass

async def get_recipe(db: AsyncSession, recipe_id: int) -> Recipe:
    """Get recipe by ID."""
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        logger.warning(f"Recipe {recipe_id} not found")
        raise RecipeNotFoundError(f"Recipe {recipe_id} not found")
    
    return recipe

# ❌ WRONG - Generic Exception
raise Exception("Something went wrong")

# ❌ WRONG - Silent failure
return None  # Without logging
```

### TypeScript Frontend

#### Naming Conventions
```typescript
// Functions and variables: camelCase
function createRecipe(name: string): void { }
const isLoading = true;

// Types/Interfaces: PascalCase
interface Recipe {
  id: number;
  name: string;
}

type RecipeStatus = 'draft' | 'published' | 'archived';

// Components: PascalCase
function RecipeCard({ recipe }: Props) { }

// Constants: UPPER_SNAKE_CASE
const MAX_RECIPE_NAME_LENGTH = 100;
const API_BASE_URL = 'http://localhost:8000';
```

#### Component Structure
```typescript
// ✅ CORRECT - Functional component with types
interface RecipeCardProps {
  recipe: Recipe;
  onDelete: (id: number) => void;
}

export function RecipeCard({ recipe, onDelete }: RecipeCardProps): JSX.Element {
  return (
    <div>
      <h2>{recipe.name}</h2>
      <button onClick={() => onDelete(recipe.id)}>Delete</button>
    </div>
  );
}

// ❌ WRONG - No types
function RecipeCard({ recipe, onDelete }) {
  ...
}

// ❌ WRONG - Class component (use functional)
class RecipeCard extends React.Component {
  ...
}
```

---

## 🧪 Testing Standards

### Backend - Pytest

#### Test File Location
```
tests/
├── test_auth.py          # Tests for auth endpoints
├── test_recipes.py       # Tests for recipe endpoints
└── conftest.py           # Pytest fixtures
```

#### Test Template
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_recipe_success(db: AsyncSession):
    """Test successful recipe creation."""
    # Arrange
    recipe_data = {
        "name": "Pasta Carbonara",
        "yield_servings": 4,
    }
    
    # Act
    recipe = await create_recipe(db, **recipe_data)
    
    # Assert
    assert recipe.id is not None
    assert recipe.name == "Pasta Carbonara"
    assert recipe.yield_servings == 4

@pytest.mark.asyncio
async def test_create_recipe_empty_name(db: AsyncSession):
    """Test recipe creation with empty name fails."""
    # Arrange
    recipe_data = {"name": "", "yield_servings": 4}
    
    # Act & Assert
    with pytest.raises(ValueError):
        await create_recipe(db, **recipe_data)

@pytest.mark.asyncio
async def test_get_recipe_not_found(db: AsyncSession):
    """Test getting non-existent recipe returns None."""
    # Act
    recipe = await get_recipe(db, 99999)
    
    # Assert
    assert recipe is None
```

#### Fixtures (conftest.py)
```python
# ✅ CORRECT - Reusable fixtures
@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide async database session for tests."""
    async with async_session_maker() as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_user_data() -> dict:
    """Provide test user data."""
    return {
        "email": "test@example.com",
        "password": "secure_password_123",
    }

@pytest.fixture
async def authenticated_client(client: TestClient, test_user_data: dict):
    """Provide authenticated test client."""
    response = client.post("/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### Frontend - Vitest

#### Test File Location
```
src/
├── components/
│   └── RecipeCard.test.tsx
├── pages/
│   └── RecipesPage.test.tsx
└── stores/
    └── recipeStore.test.ts
```

#### Test Template
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RecipeCard } from './RecipeCard';

describe('RecipeCard', () => {
  const mockRecipe = {
    id: 1,
    name: 'Pasta Carbonara',
    cost: 5.50,
  };
  
  const mockOnDelete = vi.fn();

  it('renders recipe name', () => {
    // Arrange
    render(<RecipeCard recipe={mockRecipe} onDelete={mockOnDelete} />);
    
    // Act
    const heading = screen.getByRole('heading', { name: /Pasta Carbonara/i });
    
    // Assert
    expect(heading).toBeInTheDocument();
  });

  it('calls onDelete when delete button clicked', async () => {
    // Arrange
    const { user } = render(
      <RecipeCard recipe={mockRecipe} onDelete={mockOnDelete} />
    );
    
    // Act
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);
    
    // Assert
    expect(mockOnDelete).toHaveBeenCalledWith(mockRecipe.id);
  });
});
```

---

## 🚀 Development Workflow for Claude

### When implementing a feature:

1. **Read the issue** - Understand requirements & acceptance criteria
2. **Check CLAUDE.md** - This file! Follow all conventions
3. **Create files** - Add models, schemas, services, endpoints
4. **Type everything** - 100% type coverage (Pyright strict)
5. **Write tests** - 80%+ coverage minimum, every function tested
6. **Run checks** - Locally before pushing:
   ```bash
   # Backend
   cd backend
   pyright app                # Type check
   ruff check .              # Linting
   black --check .           # Formatting
   pytest --cov=app          # Tests + coverage
   
   # Frontend
   cd ../frontend
   npm run type-check        # TypeScript
   npm run lint              # ESLint
   npm test                  # Tests
   ```
7. **Create branch** - `git checkout -b feature/ISSUE-NNN`
8. **Commit** - Use conventional commits:
   ```
   feat(recipes): add recipe cost calculation
   fix(auth): fix token refresh endpoint
   test(recipes): add unit tests for costing
   docs(api): document recipe endpoints
   ```
9. **Create PR** - Link to issue, wait for CI/CD

---

## 📋 Important: Code Change Workflow

**Always follow this exact sequence for every change:**

### 1. Type Check (FIRST!)
```bash
cd backend && pyright app
cd ../frontend && npm run type-check
```

### 2. Lint & Format
```bash
cd backend
ruff check . --fix          # Auto-fix linting issues
black .                     # Auto-format code
isort .                     # Auto-sort imports

cd ../frontend
npm run lint -- --fix       # Auto-fix ESLint
npm run format              # Auto-format with Prettier
```

### 3. Test
```bash
cd backend
pytest --cov=app --cov-fail-under=80

cd ../frontend
npm test -- --coverage
```

### 4. Verify All Pass
```bash
# Backend
pyright app && ruff check . && black --check . && pytest

# Frontend
npm run type-check && npm run lint && npm test
```

### 5. Commit Only When All Green ✅

---

## 🔐 Security & Authentication

### JWT Tokens
- **Issuer**: RestoCost API
- **Secret Key**: From `config.SECRET_KEY`
- **Algorithm**: HS256
- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

### Password Security
```python
# ✅ CORRECT - Always hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(password)

# ✅ CORRECT - Always verify
is_valid = pwd_context.verify(password, hashed_password)

# ❌ WRONG - Never store plaintext
user.password = password
```

---

## 📚 Database Standards

### Models
```python
# ✅ CORRECT - All fields typed, relationships defined
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    yield_servings = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship("RecipeItem", back_populates="recipe")
```

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add recipe model"

# Review migration file in migrations/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## 🎨 API Endpoint Patterns

### Route Organization
```python
# ✅ CORRECT - Organized by feature
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

@router.post("", response_model=RecipeResponse)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeResponse:
    """Create a new recipe."""
    return await recipe_service.create(db, recipe_data)

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
) -> RecipeResponse:
    """Get recipe by ID."""
    recipe = await recipe_service.get(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
```

### Response Models
```python
# ✅ CORRECT - Pydantic schema
class RecipeCreate(BaseModel):
    name: str
    yield_servings: int

class RecipeResponse(BaseModel):
    id: int
    name: str
    yield_servings: int
    
    model_config = ConfigDict(from_attributes=True)
```

---

## 🛑 Before Pushing

**Checklist before every commit:**

- [ ] All type checks pass (`pyright`, `tsc`)
- [ ] All linting passes (`ruff`, `eslint`)
- [ ] All tests pass with 80%+ coverage
- [ ] No console.error or warnings
- [ ] No secrets in code (use .env)
- [ ] Docstrings on all public functions
- [ ] Tests for all new functions
- [ ] Conventional commit message
- [ ] Pre-commit hooks ran

**If ANY check fails:**
1. Fix the issue
2. Run full check suite again
3. Commit only when ALL pass ✅

---

## 🤔 Common Questions for Claude

**Q: Should I create async or sync endpoints?**  
A: Always async. Example: `async def get_recipe(...)`

**Q: How do I handle errors?**  
A: Raise specific exceptions and let FastAPI convert to HTTP errors.

**Q: Do I need to write docstrings?**  
A: Yes. Google-style format for all public functions.

**Q: What about database transactions?**  
A: Use AsyncSession context managers, always await `db.commit()`

**Q: How do I create migrations?**  
A: `alembic revision --autogenerate -m "Your message"`

**Q: Can I use raw SQL?**  
A: No. Use SQLAlchemy ORM/Core only.

**Q: What about frontend state management?**  
A: Use Zustand for global state, React hooks for local state.

---

## 📞 When Stuck

If implementation gets blocked:

1. **Check existing code** - Similar features may exist
2. **Read tests** - Tests show expected behavior
3. **Check type hints** - Function signatures show contracts
4. **Read docstrings** - Document the "why"
5. **Ask in issue** - Comment on GitHub issue for clarification

---

**Last Updated**: January 2025  
**For**: Claude Code Automation  
**Status**: 🟢 In Use
