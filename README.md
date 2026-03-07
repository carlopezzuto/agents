# Claude Code Agents

A production-grade configuration system for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) featuring 42 specialized agents, 33 domain skills, 28 slash commands, and an intelligent hook system that enforces development best practices automatically.

## Features

- **42 Specialized Agents** — role-based AI specialists covering backend, frontend, security, DevOps, ML, architecture, and more
- **33 Domain Skills** — reusable knowledge patterns activated automatically based on context (TDD, async, security, API design, etc.)
- **28 Slash Commands** — workflow automation for common operations (`/tdd-cycle`, `/feature-development`, `/smart-debug`, etc.)
- **Intelligent Hook System** — Python-based pre/post tool hooks that validate, normalize, and enforce quality standards in real time
- **Auto-Trigger Rules** — agents and skills activate automatically based on what you're doing (writing tests, fixing bugs, handling security)
- **Project Rules** — enforced guidelines for security, code style, testing (80% coverage minimum), and threading patterns

## Project Structure

```
.
├── CLAUDE.md                  # Core philosophy and principles
├── hooks/                     # Hook system (Python)
│   ├── pre_tool_use.py        # Pre-execution validation
│   ├── post_tool_use.py       # Post-execution quality checks
│   ├── session_start.py       # Session initialization
│   ├── session_end.py         # Session finalization
│   ├── stop.py                # Final verification
│   ├── subagent_stop.py       # Subagent lifecycle
│   └── shared/                # Shared utilities
│       ├── hook_response.py   # Spec-compliant JSON responses
│       ├── advanced_features.py
│       ├── logger.py          # Structured event logging
│       ├── quality_toolchain.py
│       └── ...
└── .claude/
    ├── agents/                # 42 agent definitions
    ├── skills/                # 33 skill patterns
    ├── commands/              # 28 slash commands
    ├── rules/                 # Project rules
    │   ├── agents.md          # Agent orchestration & auto-triggers
    │   ├── security.md        # Security guidelines
    │   ├── code-style.md      # Code style (PEP 8, naming, organization)
    │   ├── testing-standard.md # TDD workflow, 80% coverage
    │   ├── threading-patterns.md # ConditionalLock, concurrency
    │   ├── hooks.md           # Hook system documentation
    │   ├── memory-mcp.md      # MCP Memory Service integration
    │   └── aidev-note-anchor.md # AIDEV anchor comment guidelines
    ├── output-styles/         # Response formatting (concise, technical, verbose)
    └── settings.local.json    # Hook config and permissions
```

## Agents

| Agent | Purpose |
|-------|---------|
| ai-engineer | LLM applications, RAG systems, intelligent agents |
| api-documenter | API documentation with OpenAPI 3.1, SDK generation |
| architect-review | Architecture patterns, clean architecture, DDD |
| backend-architect | Scalable API design, microservices, distributed systems |
| backend-security-coder | Secure coding, input validation, authentication |
| bash-pro | Defensive Bash scripting, CI/CD pipelines |
| brainstorm-PRD | Requirements discovery, stakeholder analysis |
| business-analyst | Requirements gathering, process improvement |
| cloud-architect | AWS/Azure/GCP multi-cloud, IaC, FinOps |
| code-archaeologist | Codebase exploration and documentation |
| code-reviewer | Code analysis, security vulnerabilities, performance |
| competitive-analyst | Competitor intelligence, SWOT analysis |
| data-scientist | Analytics, ML, statistical modeling |
| database-optimizer | Query optimization, indexing, caching |
| debugger | Error diagnosis, test failures |
| deployment-engineer | CI/CD pipelines, GitOps, deployment automation |
| devops-troubleshooter | Incident response, debugging, observability |
| django-pro | Django development, ORM, async views |
| docs-architect | Technical documentation, architecture guides |
| e2e-runner | E2E testing with Playwright |
| fastapi-pro | FastAPI, SQLAlchemy 2.0, async APIs |
| graphql-architect | GraphQL federation, performance, security |
| kubernetes-architect | K8s, GitOps (ArgoCD/Flux), service mesh |
| market-researcher | Market analysis, consumer insights |
| mermaid-expert | Mermaid diagrams, flowcharts, ERDs |
| ml-engineer | Production ML with PyTorch, TensorFlow |
| mlops-engineer | ML pipelines, MLflow, Kubeflow |
| network-engineer | Cloud networking, service mesh, zero-trust |
| observability-engineer | Monitoring, logging, tracing systems |
| performance-engineer | Performance optimization, OpenTelemetry |
| posix-shell-pro | POSIX sh scripting, maximum portability |
| product-manager | Product strategy, roadmap planning |
| project-manager | Project planning, execution, delivery |
| prompt-engineer | Prompting techniques, LLM optimization |
| python-expert | Production Python, SOLID principles |
| refactor-cleaner | Dead code cleanup, consolidation |
| reference-builder | Technical references, API documentation |
| socratic-mentor | Educational guidance, Socratic method |
| tdd-guide | Test-driven development, tests-first |
| terraform-specialist | Terraform/OpenTofu, IaC automation |
| test-automator | Test automation, self-healing tests |
| tutorial-engineer | Step-by-step tutorials, educational content |

## Skills

| Skill | Domain |
|-------|--------|
| api-design-principles | REST and GraphQL API design |
| architecture-patterns | Clean Architecture, Hexagonal, DDD |
| async-python-patterns | asyncio, concurrent programming |
| auth-implementation-patterns | JWT, OAuth2, session management, RBAC |
| bash-defensive-patterns | Production-grade shell scripting |
| bats-testing-patterns | Shell script testing with Bats |
| code-review-excellence | Code review practices and standards |
| condition-based-waiting | Race condition elimination in tests |
| debugging-strategies | Systematic debugging and profiling |
| defense-in-depth | Multi-layer input validation |
| distributed-tracing | Jaeger, Tempo, request tracking |
| e2e-testing-patterns | Playwright and Cypress E2E testing |
| error-handling-patterns | Exceptions, Result types, graceful degradation |
| fastapi-templates | Production-ready FastAPI project setup |
| grafana-dashboards | Real-time metric visualization |
| langchain-architecture | LangChain agents, memory, tool integration |
| llm-evaluation | LLM testing, benchmarking, evaluation |
| microservices-patterns | Service boundaries, event-driven communication |
| ml-pipeline-workflow | End-to-end MLOps pipelines |
| monorepo-management | Turborepo, Nx, pnpm workspaces |
| prometheus-configuration | Metric collection and alerting |
| prompt-engineering-patterns | Advanced prompting techniques |
| python-packaging | PyPI packaging, pyproject.toml |
| python-performance-optimization | Profiling and optimization |
| python-testing-pattern | pytest, fixtures, mocking, TDD |
| rag-implementation | RAG systems with vector databases |
| root-cause-tracing | Bug tracing through call stacks |
| security-review | Security checklist and patterns |
| shellcheck-configuration | ShellCheck static analysis |
| slo-implementation | SLIs, SLOs, error budgets |
| tdd-workflow | Red-green-refactor discipline |
| testing-anti-patterns | Common testing mistakes to avoid |
| verification-before-completion | Pre-completion verification checks |

## Commands

| Command | Description |
|---------|-------------|
| `/ai-assistant` | AI assistant development |
| `/brainstorm` | Interactive design refinement (Socratic method) |
| `/code-explain` | Code explanation and analysis |
| `/context-restore` | Restore previous session context |
| `/context-save` | Save current session context |
| `/deps-audit` | Dependency audit and security analysis |
| `/doc-generate` | Automated documentation generation |
| `/e2e` | Generate and run E2E tests with Playwright |
| `/feature-development` | End-to-end feature development workflow |
| `/langchain-agent` | LangChain/LangGraph agent development |
| `/memory-context` | Add current session to memory |
| `/memory-health` | Check memory service health |
| `/memory-ingest` | Ingest a document into memory |
| `/memory-ingest-dir` | Ingest a directory into memory |
| `/memory-recall` | Recall memories by time and context |
| `/memory-search` | Search memories by tags and content |
| `/memory-store` | Store information in memory |
| `/ml-pipeline` | ML pipeline orchestration |
| `/monitor-setup` | Monitoring and observability setup |
| `/performance-optimization` | End-to-end performance optimization |
| `/prompt-optimize` | Prompt optimization |
| `/python-scaffold` | Python project scaffolding |
| `/refactor-clean` | Dead code cleanup and refactoring |
| `/slo-implement` | SLO implementation guide |
| `/smart-debug` | AI-assisted debugging |
| `/tdd-cycle` | Test-driven development cycle |
| `/tech-debt` | Technical debt analysis and remediation |
| `/workflow-automate` | Workflow automation |

## Hook System

The hook system runs Python scripts at key points in the Claude Code lifecycle:

| Hook | File | Purpose |
|------|------|---------|
| Pre-Tool-Use | `hooks/pre_tool_use.py` | Validates parameters, normalizes paths, blocks destructive operations |
| Post-Tool-Use | `hooks/post_tool_use.py` | Checks output quality, runs linters, provides feedback |
| Session Start | `hooks/session_start.py` | Initializes session with project context |
| Session End | `hooks/session_end.py` | Finalizes session |
| Stop | `hooks/stop.py` | Final verification before session close |

Shared utilities in `hooks/shared/` provide structured logging, quality toolchain integration (ruff, black, pyright), async validation, and response formatting.

## Auto-Trigger Rules

Agents and skills activate automatically based on context:

| Trigger | What Activates |
|---------|---------------|
| Complex feature request | architect-review + backend-architect agents |
| Code written or modified | code-reviewer agent |
| Bug fix or new feature | tdd-guide agent |
| Security concerns | backend-security-coder agent |
| Writing tests | python-testing-pattern skill |
| Async/IO-bound work | async-python-patterns skill |
| Security-sensitive code | security-review skill |
| About to mark work done | verification-before-completion skill |

## Getting Started

1. **Clone** this repository into your project or home directory:
   ```bash
   git clone https://github.com/carlopezzuto/agents.git
   ```

2. **Configure Claude Code** to use the hooks by updating your `~/.claude/settings.json` to point to the hook scripts, or copy `.claude/settings.local.json` as a reference.

3. **Use Claude Code** as normal — agents, skills, and hooks activate automatically based on your workflow.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.10+ (for the hook system)
- Optional: ruff, black, pyright (for code quality hooks)

## Conventions

- **Git**: Conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`)
- **Testing**: TDD with 80% minimum coverage
- **Security**: Input validation, parameterized queries, no hardcoded secrets
- **Code Style**: PEP 8, type hints, max 88 char lines, max 600 line files

## License

See [LICENSE](LICENSE) for details.
