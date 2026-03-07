# Security Guidelines

## Mandatory Security Checks

Before ANY commit:

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated with Pydantic
- [ ] SQL injection prevention (parameterized queries / ORM)
- [ ] XSS prevention (sanitized HTML with bleach)
- [ ] CSRF protection enabled
- [ ] Authentication/authorization verified
- [ ] Rate limiting on all endpoints (slowapi)
- [ ] Error messages don't leak sensitive data
- [ ] Path traversal prevention (validated file paths)

## Secret Management

```python
# NEVER: Hardcoded secrets
api_key = "sk-proj-xxxxx"
db_password = "password123"

# ALWAYS: Environment variables
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not configured")
```

### Using Pydantic Settings (Recommended)

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # Raises ValidationError if missing
```

## Input Validation

```python
from pydantic import BaseModel, EmailStr, field_validator


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    age: int

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Name must be 1-100 characters")
        return v.strip()

    @field_validator("age")
    @classmethod
    def age_must_be_valid(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError("Age must be 0-150")
        return v
```

## SQL Injection Prevention

```python
# NEVER: String concatenation
query = f"SELECT * FROM users WHERE email = '{user_email}'"

# ALWAYS: Parameterized queries
from sqlalchemy import select

stmt = select(User).where(User.email == user_email)
result = await session.execute(stmt)

# Or raw parameterized
await db.execute(
    "SELECT * FROM users WHERE email = :email",
    {"email": user_email}
)
```

## Path Traversal Prevention

```python
from pathlib import Path

UPLOAD_DIR = Path("/uploads").resolve()


def get_safe_file_path(filename: str) -> Path:
    """Validate and resolve file path safely."""
    file_path = (UPLOAD_DIR / filename).resolve()

    # Ensure path is within upload directory
    if not file_path.is_relative_to(UPLOAD_DIR):
        raise ValueError("Access denied: path traversal attempt")

    return file_path
```

## XSS Prevention

```python
import bleach


def sanitize_html(html: str) -> str:
    """Sanitize user-provided HTML."""
    return bleach.clean(
        html,
        tags=["b", "i", "em", "strong", "p", "br"],
        attributes={},
        strip=True,
    )
```

## Error Handling (No Data Leakage)

```python
import logging

logger = logging.getLogger(__name__)


# WRONG: Exposing internal details
@app.get("/api/data")
async def get_data():
    try:
        return await fetch_data()
    except Exception as e:
        raise HTTPException(500, detail=str(e))  # Leaks info!


# CORRECT: Generic error messages
@app.get("/api/data")
async def get_data():
    try:
        return await fetch_data()
    except Exception as e:
        logger.exception("Internal error fetching data")
        raise HTTPException(500, detail="An error occurred. Please try again.")
```

## Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/api/endpoint")
@limiter.limit("100/15minutes")
async def endpoint(request: Request):
    return {"status": "ok"}
```

## Security Response Protocol

If security issue found:

1. STOP immediately
2. Use **backend-security-coder** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review entire codebase for similar issues

## Python Security Libraries

| Library | Purpose |
|---------|---------|
| `pydantic` | Input validation |
| `bleach` | HTML sanitization |
| `python-jose` | JWT handling |
| `passlib` | Password hashing |
| `slowapi` | Rate limiting |
| `pip-audit` | Dependency vulnerability scanning |
| `safety` | Dependency vulnerability scanning |
| `bandit` | Static security analysis |
| `python-dotenv` | Environment variable management |
| `pydantic-settings` | Typed settings from env vars |

## Dependency Security

```bash
# Check for vulnerabilities
pip-audit

# Or with safety
safety check

# Static security analysis
bandit -r src/
```
