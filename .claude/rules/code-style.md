# Code Style and Conventions - Rankle

## General Principles

- Follow PEP 8 style guide 'https://peps.python.org/pep-0008/'
- Use type hints for better code clarity
- Write self-documenting code with clear variable names
- Keep functions focused on a single responsibility
- Security-first development, comprehensive testing, error handling, performance optimization
- SOLID principles, clean architecture, dependency injection, separation of concerns
- Respect clean architecture, DI, repository, ports/adapters
- TDD approach, unit/integration/property-based testing, changed-lines coverage ≥90% and global coverage ≥85%, mutation testing for critical modules
- Validate and sanitize all inputs, secrets are always managed securely via environment variable or secret manager, development always aligns with OWASP best practices, database queries are always parameterized or ORM-based, secure coding practices, vulnerability prevention
- Specific exceptions, structured logging, clear failure messages, graceful degradation
- Profiling-based optimization, async for I/O, multiprocessing for CPU, efficient data structures, efficient algorithms, memory management, optimize hotspots

---

### Naming Conventions

- Variables: snake_case (ex:x, var, python_variable)
- Functions: snake_case with descriptive verbs (ex:function, python_function)
- Classes: camelCase (ex:Model, PythonClass)
- Constants: SCREAMING_SNAKE_CASE (ex:CONSTANT, PYTHON_CONSTANT, PYTHON_LONG_CONSTANT)
- Method: snake_case (ex:class_method, method)
- Module: snake_case (ex:module.py, python_module.py)
- Package: Use a short, lowercase word or words. Don’t separate words with underscores (ex:package, pythonpackage)

### Clean Code Guardrails

- Functions should be ≤50 lines and files ≤600 lines (justify if exceeded)
- Line Length: Max 88 characters
- Nesting depth ≤4 for readability
- Cyclomatic complexity ≤10 per function
- Replace magic numbers with named constants (0, 1, -1 allowed)
- Code must be self-documenting; comments explain intent (why), not mechanics (what)
- Apply DRY: eliminate duplication through abstraction and reuse

### Code Organization

- One class per file when it makes sense
- Group related functionality in modules
- Keep files under 600 lines
- Use `__init__.py` for clean imports

### Error Handling

- Always handle exceptions appropriately
- Use specific exception types
- Provide meaningful error messages
- Log errors for debugging
- Comprehensive exception hierarchies in each service

### Configuration Management

Uses centralized ConfigManager with environment-specific settings:

- Global, Service, Environment, Runtime, User scopes
- Supports JSON, YAML, TOML formats
- Dynamic configuration updates with validation

### Integration Patterns

Services communicate through:

- Abstract interfaces and dependency injection
- `EpicIntegrationOrchestrator` for cross-service coordination
- Internal Python APIs (no HTTP dependencies)
- Shared data models and DTOs

## Tools Configuration

### Black (Code Formatting)

- Line length: 88 characters
- Target Python versions: 3.10, 3.11, 3.12
- Compatible with isort

### Ruff (Linting)

- Extensive rule set including security (bandit), code quality (bugbear)
- Line length: 88 characters
- Target Python version: 3.10+

### Pyright (Type Checking)

- Standard type checking mode
- Full error reporting for missing imports, unused variables
- Virtual environment integration
