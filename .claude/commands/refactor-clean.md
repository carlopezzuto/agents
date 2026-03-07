# Refactor Clean

Safely identify and remove dead code with test verification:

1. Run dead code analysis tools:
   - vulture: Find unused functions, variables, classes, imports
   - ruff (F401, F841): Find unused imports and variables
   - pylint (W0611, W0612): Find unused imports and variables
   - pip-extra-reqs: Find unused dependencies

2. Generate comprehensive report in .reports/dead-code-analysis.md

3. Categorize findings by severity:
   - SAFE: Test files, unused utilities, private functions (\_prefixed)
   - CAUTION: API routes, CLI entry points, pytest fixtures
   - DANGER: Config files, main entry points, `__all__` exports, pyproject.toml entry points

4. Propose safe deletions only

5. Before each deletion:
   - Run full test suite: `pytest`
   - Verify tests pass
   - Apply change
   - Re-run tests: `pytest`
   - Check types: `pyright`
   - Check lint: `ruff check .`
   - Rollback if any check fails

6. Show summary of cleaned items

7. Update docs/DELETION_LOG.md with changes

## Commands Reference

```bash
# Dead code detection
vulture src/ tests/ --min-confidence 80
ruff check . --select=F401,F841,F811
pylint src/ --disable=all --enable=W0611,W0612,W0613

# Preview autoflake changes (dry-run)
autoflake --remove-all-unused-imports --remove-unused-variables -r --check src/

# Apply autoflake changes
autoflake --remove-all-unused-imports --remove-unused-variables -r --in-place src/

# Find duplicate code
pylint src/ --disable=all --enable=R0801 --min-similarity-lines=10

# Check for unused dependencies
pip-extra-reqs requirements.txt
```

## Dynamic Import Detection (CAREFUL)

Before removing, grep for dynamic imports:

- `getattr(module, "name")`
- `importlib.import_module("name")`
- `globals()["name"]`
- `__import__("name")`

Never delete code without running tests first!
