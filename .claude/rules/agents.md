# Agent Orchestration

## Available Agents (REQUIRED: Delegate to matching agent)

| Agent                  | Purpose                                                 | When to Use                                        |
| ---------------------- | ------------------------------------------------------- | -------------------------------------------------- |
| ai-engineer            | LLM applications, RAG systems, intelligent agents       | LLM features, chatbots, AI agents, AI-powered apps |
| api-documenter         | API documentation with OpenAPI 3.1, SDK generation      | API documentation, developer portals               |
| architect-review       | Architecture patterns, clean architecture, DDD          | Architectural decisions, system design reviews     |
| backend-architect      | Scalable API design, microservices, distributed systems | New backend services, APIs, service boundaries     |
| backend-security-coder | Secure coding, input validation, authentication         | Backend security implementations, security reviews |
| bash-pro               | Defensive Bash scripting, CI/CD pipelines               | Production automation, system utilities            |
| brainstorm-PRD         | Requirements discovery, stakeholder analysis            | Ambiguous project ideas, PRD creation              |
| business-analyst       | Requirements gathering, process improvement             | Business value analysis, stakeholder management    |
| cloud-architect        | AWS/Azure/GCP multi-cloud, IaC, FinOps                  | Cloud architecture, cost optimization, migrations  |
| code-archaeologist     | Codebase exploration and documentation                  | Legacy code, refactors, onboarding, audits         |
| code-reviewer          | Code analysis, security vulnerabilities, performance    | After writing code, code quality assurance         |
| competitive-analyst    | Competitor intelligence, SWOT analysis                  | Market positioning, strategic analysis             |
| data-scientist         | Analytics, ML, statistical modeling                     | Data analysis, predictive modeling, BI             |
| database-optimizer     | Query optimization, indexing, caching                   | Database performance, scalability issues           |
| debugger               | Error diagnosis, test failures                          | Errors, unexpected behavior, debugging             |
| deployment-engineer    | CI/CD pipelines, GitOps, deployment automation          | CI/CD design, zero-downtime deployments            |
| devops-troubleshooter  | Incident response, debugging, observability             | Production outages, system troubleshooting         |
| django-pro             | Django development, ORM, async views                    | Django applications, ORM optimization              |
| docs-architect         | Technical documentation, architecture guides            | System documentation, technical manuals            |
| e2e-runner             | E2E testing with Playwright                             | Critical user flows, E2E test generation           |
| fastapi-pro            | FastAPI, SQLAlchemy 2.0, async APIs                     | FastAPI development, async optimization            |
| graphql-architect      | GraphQL federation, performance, security               | GraphQL architecture, schema design                |
| kubernetes-architect   | K8s, GitOps (ArgoCD/Flux), service mesh                 | K8s architecture, cloud-native platforms           |
| market-researcher      | Market analysis, consumer insights                      | Market sizing, trend analysis, opportunities       |
| mermaid-expert         | Mermaid diagrams, flowcharts, ERDs                      | Visual documentation, system diagrams              |
| ml-engineer            | Production ML with PyTorch, TensorFlow                  | ML deployment, inference optimization              |
| mlops-engineer         | ML pipelines, MLflow, Kubeflow                          | ML infrastructure, experiment management           |
| network-engineer       | Cloud networking, service mesh, zero-trust              | Network design, connectivity, performance          |
| observability-engineer | Monitoring, logging, tracing systems                    | Observability, SLI/SLO, incident response          |
| performance-engineer   | Performance optimization, OpenTelemetry                 | Performance issues, scalability challenges         |
| posix-shell-pro        | POSIX sh scripting, maximum portability                 | Portable shell scripts across Unix systems         |
| product-manager        | Product strategy, roadmap planning                      | Feature prioritization, product decisions          |
| project-manager        | Project planning, execution, delivery                   | Resource management, risk mitigation               |
| prompt-engineer        | Prompting techniques, LLM optimization                  | AI features, agent performance, system prompts     |
| python-expert          | Production Python, SOLID principles                     | Python development, best practices                 |
| refactor-cleaner       | Dead code cleanup, consolidation                        | Removing unused code, refactoring                  |
| reference-builder      | Technical references, API documentation                 | API docs, configuration references                 |
| socratic-mentor        | Educational guidance, Socratic method                   | Programming knowledge, discovery learning          |
| tdd-guide              | Test-driven development, tests-first                    | New features, bug fixes, refactoring               |
| terraform-specialist   | Terraform/OpenTofu, IaC automation                      | Infrastructure automation, state management        |
| test-automator         | Test automation, self-healing tests                     | Testing automation, quality assurance              |
| tutorial-engineer      | Step-by-step tutorials, educational content             | Onboarding guides, feature tutorials               |

## Auto-Trigger Rules (MANDATORY)

ALWAYS spawn these agents automatically - no user prompt needed:

| Trigger                    | Agent                                    | When                  |
| -------------------------- | ---------------------------------------- | --------------------- |
| Complex feature request    | architect-review, backend-architect      | BEFORE implementation |
| Code written/modified      | code-reviewer                            | AFTER changes         |
| Bug fix or new feature     | tdd-guide                                | BEFORE writing code   |
| Architectural decision     | architect-review                         | BEFORE deciding       |
| Performance issues         | performance-engineer, database-optimizer | BEFORE optimizing     |
| Security concerns          | backend-security-coder                   | IMMEDIATELY           |
| Legacy/unfamiliar codebase | code-archaeologist                       | BEFORE changes        |

## Parallel Task Execution (Mandatory)

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution

Launch 3 agents in parallel:

1. Agent 1: Security analysis of auth.ts
2. Agent 2: Performance review of cache system
3. Agent 3: Type checking of utils.ts

# BAD: Sequential when unnecessary

First agent 1, then agent 2, then agent 3
```

## Multi-Perspective Analysis

For complex problems, use split role sub-agents:

- Factual reviewer
- Senior engineer
- Security expert
- Consistency reviewer
- Redundancy checker
