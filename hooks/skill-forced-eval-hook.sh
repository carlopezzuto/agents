#!/bin/bash
# UserPromptSubmit hook that forces explicit skill AND agent activation

cat <<'EOF'
MANDATORY TOOL ACTIVATION SEQUENCE

HOW TO DETERMINE SKILL vs AGENT:

SKILLS (use Skill tool):
- Listed in Skill tool's "Available skills" section
- Inject context/guidance/patterns into conversation
- Examples: *-patterns, *-principles, *-templates, *-configuration
- Invoke: Skill("plugin:skill-name") or Skill("skill-name")

AGENTS (use Task tool):
- Built-in agents: Bash, Explore, Plan, claude-code-guide, debugger, general-purpose, etc.
- Plugin agents: Listed in Task tool description with "Tools: All tools"
- Spawn autonomous subagents that work independently
- Examples: *-pro, *-expert, *-engineer, *-architect, *-reviewer
- Invoke: Task(subagent_type="agent-name", prompt="...")

IF UNSURE: Check the plugin's marketplace.json or try Skill() first - if it fails with "Unknown skill", use Task() instead.

Step 1 - EVALUATE (state YES/NO with reason for relevant items):
Skills: [skill-name] - YES/NO - [reason]
Agents: [agent-name] - YES/NO - [reason]

**FORBIDDEN**: "Later", "After", "Maybe", "Defer" - ONLY YES or NO allowed!
If you need it during the task, it's YES. Activate upfront, not mid-task.

Step 2 - ACTIVATE YES ITEMS:
- For each YES skill → Skill("skill-name")
- For each YES agent → Task(subagent_type="agent-name", prompt="task description")
- If none YES → State "No skills/agents needed"

Step 3 - IMPLEMENT:
Only proceed with Read, Search, Glob, Grep AFTER Step 2 completes.

CRITICAL:
- Do NOT skip activation. Evaluation without activation is worthless.
- Do NOT defer agents to "after implementation" - activate ALL upfront.
- "Later" = violation. If you'll need it, activate NOW.

Example:
Skills:
- backend-development:python-testing-pattern: YES - need testing patterns

Agents:
- claude-code-guide: YES - need Claude Code docs
- backend-development:python-expert: YES - complex implementation

[Then IMMEDIATELY activate:]
> Skill("backend-development:python-testing-pattern")
> Task(subagent_type="claude-code-guide", prompt="research X")

[You MUST enable/activate/invoke the YES items for skills and agents for first, and THEN and ONLY THEN start implementation/read/think/grep/blob and/or any other tasks]
EOF
