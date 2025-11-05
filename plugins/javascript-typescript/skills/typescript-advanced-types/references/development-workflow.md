# Development Workflow

## Python Service Development

### Standard Workflow

1. **Write test first (TDD)**
   ```bash
   # Create test file
   touch python-service/tests/test_new_feature.py

   # Write failing test
   # Run tests - should fail
   pytest tests/test_new_feature.py
   ```

2. **Implement feature with type hints**
   ```bash
   # Create implementation file
   touch python-service/services/new_feature.py

   # Implement with full type hints
   # See: references/python-style.md
   ```

3. **Run pytest - all must pass**
   ```bash
   # Run all tests
   pytest

   # Run specific test
   pytest tests/test_new_feature.py -v

   # Run with coverage
   pytest --cov=. --cov-report=term-missing
   ```

4. **Run ruff check - fix linting issues**
   ```bash
   # Check for issues
   ruff check .

   # Auto-fix where possible
   ruff check . --fix

   # Check specific file
   ruff check services/new_feature.py
   ```

5. **Run pyright - resolve type errors**
   ```bash
   # Type check entire project
   pyright

   # Type check specific file
   pyright services/new_feature.py
   ```

6. **Run black - format code**
   ```bash
   # Check formatting
   black . --check

   # Format code
   black .

   # Format specific file
   black services/new_feature.py
   ```

### Python Development Commands

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest                                    # All tests
pytest -v                                 # Verbose
pytest -k "test_extraction"               # Filter by name
pytest --cov=. --cov-report=html          # Coverage with HTML report

# Code quality
ruff check .                              # Lint
ruff check . --fix                        # Lint and auto-fix
black .                                   # Format
pyright                                   # Type check

# Complete validation
pytest && ruff check . && pyright && black . --check
```

## TypeScript Frontend Development

### Standard Workflow

1. **Write test first (Vitest)**
   ```bash
   # Create test file
   touch src/services/__tests__/new-feature.test.ts

   # Write failing test
   # Run tests - should fail
   bun test src/services/__tests__/new-feature.test.ts
   ```

2. **Implement feature with strict types**
   ```bash
   # Create implementation file
   touch src/services/new-feature.ts

   # Implement with strict TypeScript
   # See: references/typescript-style.md
   ```

3. **Run bun test - all must pass**
   ```bash
   # Run all tests
   bun test

   # Run specific test
   bun test src/services/__tests__/new-feature.test.ts

   # Run with coverage
   bun test --coverage
   ```

4. **Run bun run lint - fix ESLint issues**
   ```bash
   # Check for issues
   bun run lint

   # Auto-fix where possible
   bun run lint:fix

   # Check specific file
   bun run lint src/services/new-feature.ts
   ```

5. **Run bun run tsc - resolve type errors**
   ```bash
   # Type check entire project
   bun run tsc

   # Watch mode
   bun run tsc --watch
   ```

6. **Run bun run format - Prettier formatting**
   ```bash
   # Check formatting
   bun run format:check

   # Format code
   bun run format

   # Format specific file
   bun run format src/services/new-feature.ts
   ```

### TypeScript Development Commands

```bash
# Install dependencies
bun install

# Development server with hot reload
bun run dev

# Generate PDF to disk
bun run save-to-pdf -C company-name

# Generate TypeScript data from YAML
bun run generate-data -C company-name

# Run all (generate data + start server)
bun run start

# Testing
bun test                                  # Run tests
bun test --watch                          # Watch mode
bun test --coverage                       # With coverage

# Code quality
bun run lint                              # ESLint
bun run lint:fix                          # ESLint auto-fix
bun run tsc                               # Type check
bun run format                            # Prettier format
bun run format:check                      # Check formatting

# Complete validation
bun test && bun run lint && bun run tsc && bun run format:check
```

## Integration Testing

### Full Stack Workflow

1. **Start Python backend**
   ```bash
   cd python-service
   source .venv/bin/activate
   uvicorn main:app --reload
   # Backend running on http://localhost:8000
   ```

2. **Start TypeScript frontend**
   ```bash
   # In separate terminal
   bun run dev
   # Frontend running on http://localhost:3000
   ```

3. **Test E2E workflow**
   ```
   Job posting → Python API analysis → TypeScript PDF generation
   ```

4. **Validate performance**
   - Backend analysis: <5s
   - Frontend PDF: <3s
   - Total time: <8s

5. **Check schema alignment**
   ```bash
   python scripts/check_schema_alignment.py
   ```

### Integration Test Example

```python
# python-service/tests/integration/test_full_workflow.py

import pytest
import httpx
from fastapi.testclient import TestClient
from main import app

@pytest.mark.integration
async def test_job_analysis_to_pdf_workflow():
    """Test complete workflow: job posting → analysis → PDF generation."""
    client = TestClient(app)

    # Step 1: Analyze job posting
    job_posting = """
    Senior Frontend Developer
    5+ years React experience required.
    """

    response = client.post(
        "/api/analyze-job",
        json={"job_posting": job_posting}
    )

    assert response.status_code == 200
    analysis = response.json()

    # Step 2: Verify analysis structure
    assert analysis["detected_industry"] == "technology"
    assert analysis["confidence"] >= 0.85
    assert len(analysis["extracted_requirements"]["technical_skills"]) > 0

    # Step 3: Verify processing time
    assert analysis["processing_time_ms"] < 5000
```

## Common Development Workflows

### Adding New Industry Extractor

1. Create extractor class in `python-service/services/extractors/`
2. Write tests in `python-service/tests/test_extractors/`
3. Register in extractor factory
4. Add industry patterns
5. Test against real job postings
6. Verify <1s extraction time
7. See: `references/python-style.md`

### Modifying API Schema

1. Update Pydantic model in `python-service/models/schemas.py`
2. Update Zod schema in `src/zod/schemas.ts`
3. Run `scripts/check_schema_alignment.py`
4. Update contract tests
5. Update API documentation
6. Test both Python and TypeScript sides
7. See: `references/schema-alignment.md`

### Adding New PDF Component

1. Create component in `src/templates/`
2. Write tests in `src/templates/__tests__/`
3. Follow React-PDF patterns
4. Use design tokens from `design-tokens.ts`
5. Test PDF generation
6. Verify <3s generation time
7. See: `references/typescript-style.md`

## Pre-Commit Checklist

- [ ] All tests pass (Python + TypeScript)
- [ ] Code formatted (Black + Prettier)
- [ ] No linting errors (Ruff + ESLint)
- [ ] No type errors (Pyright + TypeScript)
- [ ] Coverage maintained (≥80% Python, ≥70% TypeScript)
- [ ] Schema alignment validated
- [ ] Performance targets met (<5s backend, <3s frontend)
- [ ] No console errors/warnings
- [ ] Git commit message follows conventions

## CI/CD Integration

### GitHub Actions Workflow Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=. --cov-report=xml
      - run: ruff check .
      - run: pyright
      - run: black . --check

  typescript-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun test --coverage
      - run: bun run lint
      - run: bun run tsc
      - run: bun run format:check

  schema-alignment:
    runs-on: ubuntu-latest
    needs: [python-tests, typescript-tests]
    steps:
      - uses: actions/checkout@v3
      - run: python scripts/check_schema_alignment.py
```

## Troubleshooting

### Common Issues

**Python virtual environment not activated:**
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

**pytest/ward syntax confusion:**
Ward uses `@test()` decorator, not pytest fixtures/classes.

**Wrong CWD or PYTHONPATH:**
Ensure you're in the correct directory and PYTHONPATH is set properly.

**TypeScript type errors:**
Run `bun run tsc` to see all type errors, fix from top to bottom.

**Schema drift:**
Run `python scripts/check_schema_alignment.py` regularly.
