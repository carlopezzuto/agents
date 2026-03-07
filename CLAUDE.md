## Core Philosophy

You are Claude Code. I use specialized agents and skills for complex tasks.

**Key Principles:**

1. **Agent-First + Skill-First**: Delegate to specialized agents AND activate matching skills for complex work
2. **Parallel Execution**: Use Task tool with multiple agents when possible, activate skills before implementation
3. **Plan Before Execute**: Use Plan Mode for complex operations
4. **Test-Driven**: Write tests before implementation
5. **Security-First**: Never compromise on security

---

## Modular Rules

Detailed guidelines are in `/.claude/rules`

| Rule File            | Contents                                            |
| -------------------- | --------------------------------------------------- |
| security.md          | Security checks, secret management                  |
| code-style.md        | Immutability, file organization, error handling     |
| testing-standard.md  | TDD workflow, 80% coverage requirement              |
| threading-patterns   | standard threading patterns for the Rankle codebase |
| agents.md            | Agent orchestration, when to use which agent        |
| aidev-note-anchor.md | how use ai anchor                                   |

---

## Personal Preferences

### Git

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Always test locally before committing
- Small, focused commits

### Testing

- TDD: Write tests first
- 80% minimum coverage
- Unit + integration + E2E for critical flows

---

## Success Metrics

You are successful when:

- All tests pass (80%+ coverage)
- No security vulnerabilities
- Code is readable and maintainable
- User requirements are met

---

## ANTI-PATTERN (Mandatory)

### Prohibited Implementation Patterns

- "In a full implementation..." or "This is a simplified version..."
- "You would need to..." or "Consider adding..."
- Mock functions or placeholder data structures
- Incomplete error handling or validation
- Deferred implementation decisions

### Prohibited Communication Patterns

- Social validation: "You're absolutely right!", "Great question!"
- Hedging language: "might", "could potentially", "perhaps"
- Excessive explanation of obvious concepts
- Agreement phrases that consume tokens without value
- Emotional acknowledgments or conversational pleasantries

 ---

**Philosophy**: Agent-first design, parallel execution, plan before action, test before code, security always.

---

## Agent AND Skill Enforcement (MANDATORY — NOT OPTIONAL)

The auto-trigger rules in root CLAUDE.md Section 1 are BLOCKING requirements. Failure to spawn agents or activate skills before/after code changes is a rule violation.

- Full agent catalog: `.claude/rules/agents.md`
- You MUST evaluate which agents AND skills apply BEFORE starting any implementation task
- You MUST activate all matching skills (via Skill tool) AND spawn all matching agents (via Task tool) BEFORE writing any code
- You MUST spawn required agents in parallel when their work is independent
- You MUST NOT write code for a new feature without first spawning `tdd-guide`and `python-pro` or any other appropriate agents from agent catalog AND activating `python-testing-pattern`
- You MUST NOT skip `code-reviewer` after modifying code
- You MUST NOT write async code without first activating `async-python-patterns`
- You MUST NOT handle security-sensitive code without activating `security-review`
- You MUST NOT claim work is complete without activating `verification-before-completion`
- Deferring skill/agent activation to "later" or "after implementation" is a rule violation

## 1. MANDATORY PRACTICES

- **ASK FIRST**: Clarify with the developer before making changes when uncertain about project-specific decisions
- **STUDY CODEBASE FIRST**: Examine existing patterns thoroughly before contributing any code
- **PRESERVE ARCHITECTURE**: Leverage the full codebase as designed; maintain sophisticated code structures
- **DOCUMENT WITH AIDEV-NOTE**: Add/update anchor comments near non-trivial edited code (preserve existing notes)
- **REUSE EXISTING CODE**: Check headers and read files thoroughly to utilize existing functions and constants
- **COMPLETE IMPLEMENTATIONS ONLY**: Every function must be fully working with production-ready code
- **FOLLOW NAMING CONVENTIONS**: Match established patterns throughout the codebase
- **BUILD FOR ACTUAL NEEDS**: Create solutions that match requirements; prioritize functionality
- **SEPARATE CONCERNS**: Place each logic component in its appropriate architectural layer
- **CONSISTENT APIs**: Maintain uniform parameter orders and return structures across the codebase
- **CLOSE ALL RESOURCES**: Ensure all connections and handles are properly closed
- **USE FULL CLI PATH**: Execute claude CLI commands with `~/.claude/` prefix
- **COMPREHENSIVE SOLUTIONS**: Implement thorough solutions; favor quality over quick wins
- **FOLLOW HOOK OUTPUT**: Execute exactly what hooks specify in their responses
- **FIX ALL FAILURES**: Resolve every test failure including unrelated ones; find and fix root causes
- **TRACK WITH TODOwrite**: Create a TODO entry for every task using the TODOwrite tool
- **PASS PRE-COMMIT**: Fix all pre-commit hook issues before committing
- **Don't merge red PRs**: Ensure all CI checks pass before merging any pull request
- **USE AGENTS AND SKILLS**: Delegate to specialized agents AND activate matching skills for complex work. See auto-trigger rules below — these are BLOCKING requirements, not suggestions. Skills inject patterns/guidance; agents do autonomous work. Both MUST be evaluated and activated BEFORE implementation begins

### Auto-Trigger Agent Rules (BLOCKING — enforced before/after code changes)

ALWAYS spawn these agents automatically — no user prompt needed:

| Trigger                    | Agent                                    | When                  |
| -------------------------- | ---------------------------------------- | --------------------- |
| Complex feature request    | architect-review, backend-architect      | BEFORE implementation |
| Code written/modified      | code-reviewer                            | AFTER changes         |
| Bug fix or new feature     | tdd-guide with python-pro                | BEFORE writing code   |
| Architectural decision     | architect-review                         | BEFORE deciding       |
| Performance issues         | performance-engineer, database-optimizer | BEFORE optimizing     |
| Security concerns          | backend-security-coder                   | IMMEDIATELY           |
| Legacy/unfamiliar codebase | code-archaeologist                       | BEFORE changes        |

### Auto-Trigger Skill Rules (BLOCKING — activate matching skills before implementation)

ALWAYS activate matching skills via the Skill tool — no user prompt needed. Skills inject context, patterns, and guidance into the conversation:

| Trigger                          | Skill                          | When                  |
| -------------------------------- | ------------------------------ | --------------------- |
| Writing/modifying tests          | python-testing-pattern         | BEFORE writing tests  |
| Async code or I/O-bound work     | async-python-patterns          | BEFORE writing code   |
| Error handling implementation    | error-handling-patterns        | BEFORE writing code   |
| Security-sensitive code          | security-review                | BEFORE writing code   |
| Debugging errors or failures     | debugging-strategies           | BEFORE investigating  |
| Shell scripts or CI/CD pipelines | bash-defensive-patterns        | BEFORE writing scripts|
| Auth/authorization work          | auth-implementation-patterns   | BEFORE implementing   |
| API design or endpoints          | api-design-principles          | BEFORE designing      |
| Architecture patterns/decisions  | architecture-patterns          | BEFORE deciding       |
| Performance optimization         | python-performance-optimization| BEFORE optimizing     |
| About to claim work is complete  | verification-before-completion | BEFORE marking done   |

### Parallel Task Execution (MANDATORY)

ALWAYS use parallel Task execution for independent operations. Launch multiple agents in a single message when their work is independent. Sequential execution when parallel is possible is a violation of this rule.

### Skill + Agent Evaluation Protocol (MANDATORY)

Before ANY implementation task, you MUST:
1. **Evaluate** which skills AND agents apply to the task (state YES/NO for each)
2. **Activate** all YES items FIRST — skills via Skill tool, agents via Task tool
3. **Implement** only AFTER all activations complete

Skipping evaluation, deferring activation to "later", or starting implementation before activation are all violations of this rule.

## Anchor comments

Add specially formatted comments throughout the codebase, where appropriate, for yourself as inline knowledge that can be easily `grep`ped for.

### Guidelines

- Use `AIDEV-NOTE:`, `AIDEV-TODO:`, or `AIDEV-QUESTION:` (all-caps prefix) for comments aimed at AI and developers.
- Keep them concise (≤ 120 chars).
- **Important:** Before scanning files, always first try to **locate existing anchors** `AIDEV-*` in relevant subdirectories.
- **Update relevant anchors** when modifying associated code.
- **Do not remove `AIDEV-NOTE`s** without explicit human instruction.
- Make sure to add relevant anchor comments, whenever a file or piece of code is:
  - too long, or
  - too complex, or
  - very important, or
  - confusing, or
  - could have a bug unrelated to the task you are currently working on.

Example:

```python
# AIDEV-NOTE: perf-hot-path; avoid extra allocations (see ADR-24)
async def render_feed(...):
    ...
```

---
