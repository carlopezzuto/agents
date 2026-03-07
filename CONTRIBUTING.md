# Contributing to Claude Code Agents

Thank you for your interest in contributing! This guide explains how to get involved.

## How to Contribute

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/agents.git
   cd agents
   ```
3. **Create a branch** for your change:
   ```bash
   git checkout -b feat/your-feature-name
   ```
4. **Make your changes** following the guidelines below
5. **Commit** using conventional commit messages
6. **Push** to your fork and open a **Pull Request** against `main`

## Development Setup

- **Python 3.10+** is required for the hook system
- Optional but recommended tooling:
  - [ruff](https://docs.astral.sh/ruff/) — linting
  - [black](https://black.readthedocs.io/) — code formatting
  - [pyright](https://github.com/microsoft/pyright) — type checking

## Coding Standards

This project follows strict coding conventions defined in `.claude/rules/code-style.md`:

- **Style**: PEP 8 with 88-character line length
- **Type hints**: Required on all function signatures
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `SCREAMING_SNAKE_CASE` for constants
- **File size**: Max 600 lines per file; max 50 lines per function
- **Error handling**: Use specific exception types with meaningful messages
- **Security**: No hardcoded secrets, validate all inputs, parameterized queries

## Testing

We follow Test-Driven Development (TDD) with an 80% minimum coverage target:

1. Write the test first (it should fail)
2. Write the minimal implementation to make it pass
3. Refactor while keeping tests green

See `.claude/rules/testing-standard.md` for full details.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use for |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `docs:` | Documentation changes |
| `refactor:` | Code restructuring without behavior change |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance tasks |

Example: `feat: add rate-limiting skill for API endpoints`

## Adding Agents, Skills, or Commands

- **Agents** go in `.claude/agents/` — one Markdown file per agent
- **Skills** go in `.claude/skills/` — one Markdown file per skill
- **Commands** go in `.claude/commands/` — one Markdown file per command

Follow existing files as templates. Update the agent/skill/command table in `README.md` when adding new entries.

## Reporting Issues

Open an issue on GitHub with:

- A clear title describing the problem
- Steps to reproduce (if applicable)
- Expected vs actual behavior
- Your environment (OS, Python version, Claude Code version)

## Code of Conduct

Be respectful and constructive. We expect all contributors to maintain a professional, inclusive environment. Harassment, discrimination, and disruptive behavior are not tolerated.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
