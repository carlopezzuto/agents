# TDD Workflow

The Red-Green-Refactor cycle, violations, and incremental development principles.

## The TDD Cycle

### 1. Red Phase: Write ONE Failing Test

**Goal**: Describe desired behavior through a failing test.

**Rules**:
- Write only ONE test at a time
- Test must fail for the RIGHT reason (not syntax/import errors)
- Test describes what the code should do, not how

**Example**:
```python
def test_analyzes_job_posting():
    """Given job posting text, when analyzing, then returns industry classification."""
    analyzer = JobAnalyzer()
    result = analyzer.analyze("Software Engineer position...")

    assert result["industry"] == "technology"
```

**Initial Run**: Test fails with `NameError: name 'JobAnalyzer' is not defined` ✅

**Exception**: Adding a single test to a test file is ALWAYS allowed, even if prior test output shows unrelated work. Starting TDD for a new feature is always valid.

---

### 2. Green Phase: Write MINIMAL Code

**Goal**: Make the failing test pass with the simplest possible implementation.

**Rules**:
- Implement only what's needed for the current failing test
- No anticipatory coding or extra features
- Address the specific failure message
- No "nice to have" additions

**Incremental Steps**:

**Step 1** - Test fails: `NameError: name 'JobAnalyzer' is not defined`
```python
# Create empty class only
class JobAnalyzer:
    pass
```

**Step 2** - Test fails: `AttributeError: 'JobAnalyzer' object has no attribute 'analyze'`
```python
# Add method stub only
class JobAnalyzer:
    def analyze(self, posting: str):
        pass
```

**Step 3** - Test fails: `AssertionError: None != {'industry': 'technology'}`
```python
# Implement minimal logic only
class JobAnalyzer:
    def analyze(self, posting: str):
        return {"industry": "technology"}
```

**Test passes** ✅

**Over-Implementation Example (❌ WRONG)**:
```python
# DON'T DO THIS - too much at once
class JobAnalyzer:
    def __init__(self, config=None):
        self.config = config or {}

    def analyze(self, posting: str):
        # Multiple features not required by test
        industry = self._classify_industry(posting)
        confidence = self._calculate_confidence(posting)
        skills = self._extract_skills(posting)

        return {
            "industry": industry,
            "confidence": confidence,
            "skills": skills
        }

    def _classify_industry(self, posting: str):
        # Complex logic not needed yet
        pass
```

---

### 3. Refactor Phase: Improve Structure

**Goal**: Improve code quality while keeping all tests green.

**Rules**:
- Only allowed when relevant tests are passing
- Requires proof that tests have been run and are green
- Applies to BOTH implementation and test code
- No new functionality - only structural improvements

**Allowed Refactorings**:
- Extract methods/functions for clarity
- Rename variables for better naming
- Add types/interfaces/constants
- Remove duplication
- Improve code organization
- Replace magic values with named constants

**Not Allowed**:
- Adding new features
- Adding untested error handling
- Implementing methods not required by tests
- Changing behavior without tests

**Example Refactoring**:

**Before** (tests passing):
```python
class JobAnalyzer:
    def analyze(self, posting: str):
        return {"industry": "technology"}
```

**After** (refactored, tests still passing):
```python
# Added constant for clarity
DEFAULT_INDUSTRY = "technology"

class JobAnalyzer:
    def analyze(self, posting: str) -> dict[str, str]:
        """Analyze job posting and return classification."""
        return {"industry": self._classify_industry(posting)}

    def _classify_industry(self, posting: str) -> str:
        """Extract industry from posting text."""
        return DEFAULT_INDUSTRY
```

**Prohibited Refactoring with Failing Tests**:
```bash
$ pytest
...FAILED...

# ❌ STOP - Do not refactor with failing tests
# Fix the test failure first, then refactor
```

---

## Why Order Matters

### "I'll write tests after to verify it works"

Tests written after code pass immediately. **Passing immediately proves nothing**:

- Might test wrong thing
- Might test implementation, not behavior
- Might miss edge cases you forgot
- You never saw it catch the bug

**Test-first forces you to see the test fail**, proving it actually tests something.

---

### "I already manually tested all the edge cases"

Manual testing is ad-hoc. You think you tested everything but:

- No record of what you tested
- Can't re-run when code changes
- Easy to forget cases under pressure
- "It worked when I tried it" ≠ comprehensive

**Automated tests are systematic**. They run the same way every time.

---

### "Deleting X hours of work is wasteful"

**Sunk cost fallacy**. The time is already gone. Your choice now:

1. Delete and rewrite with TDD (X more hours, **high confidence**)
2. Keep it and add tests after (30 min, **low confidence, likely bugs**)

**The "waste" is keeping code you can't trust**. Working code without real tests is technical debt.

---

### "TDD is dogmatic, being pragmatic means adapting"

**TDD IS pragmatic**:

- Finds bugs before commit (faster than debugging after)
- Prevents regressions (tests catch breaks immediately)
- Documents behavior (tests show how to use code)
- Enables refactoring (change freely, tests catch breaks)

**"Pragmatic" shortcuts = debugging in production = slower.**

---

### "Tests after achieve the same goals - it's spirit not ritual"

**No.** Tests-after answer "What does this do?" Tests-first answer "What should this do?"

- **Tests-after** are biased by your implementation. You test what you built, not what's required.
- **Tests-first** force edge case discovery before implementing.

30 minutes of tests after ≠ TDD. You get coverage, lose proof tests work.

---

## Verification Checklist

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

**Can't check all boxes? You skipped TDD. Start over.**

---

## Red Flags - STOP and Start Over

- Code before test
- Test after implementation
- Test passes immediately
- Can't explain why test failed
- Tests added "later"
- Rationalizing "just this once"
- "I already manually tested it"
- "Tests after achieve the same purpose"
- "It's about spirit not ritual"
- "Keep as reference" or "adapt existing code"
- "Already spent X hours, deleting is wasteful"
- "TDD is dogmatic, I'm being pragmatic"
- "This is different because..."

**All of these mean: Delete code. Start over with TDD.**

---

## Core Violations

### Violation 1: Multiple Test Addition

**❌ WRONG**:
```python
# Adding 3 tests at once
def test_analyzes_tech_posting():
    pass

def test_analyzes_healthcare_posting():
    pass

def test_analyzes_finance_posting():
    pass
```

**✅ CORRECT**:
```python
# Add ONE test
def test_analyzes_tech_posting():
    analyzer = JobAnalyzer()
    result = analyzer.analyze("Software Engineer...")
    assert result["industry"] == "technology"

# Run test, make it pass
# THEN add next test
```

**Exception**: Initial test file setup or extracting shared test utilities is allowed.

---

### Violation 2: Over-Implementation

**❌ WRONG**:
```python
# Test only requires analyze() method
def test_analyzes_posting():
    result = analyzer.analyze(posting)
    assert result["industry"] == "technology"

# But code implements multiple untested features
class JobAnalyzer:
    def analyze(self, posting: str):
        # ❌ Over-implementation
        return {
            "industry": self._classify(),
            "confidence": self._score(),  # Not tested
            "skills": self._extract(),    # Not tested
        }
```

**✅ CORRECT**:
```python
# Implement only what test requires
class JobAnalyzer:
    def analyze(self, posting: str):
        return {"industry": "technology"}
```

---

### Violation 3: Premature Implementation

**❌ WRONG**:
```python
# No test written yet
class JobAnalyzer:
    def analyze(self, posting: str):
        # Implementing before test exists
        return {"industry": "technology"}
```

**✅ CORRECT**:
```python
# 1. Write test first
def test_analyzes_posting():
    result = JobAnalyzer().analyze("...")
    assert result["industry"] == "technology"

# 2. Run test - see it fail
# 3. Then implement
```

---

## Incremental Development Principle

Each step should address ONE specific issue:

### Step-by-Step Example

**Test Code**:
```python
def test_extracts_required_skills():
    extractor = SkillExtractor()
    skills = extractor.extract("React, Python required")

    assert "React" in skills
    assert "Python" in skills
```

**Incremental Implementation**:

**Iteration 1** - Test fails: `NameError: name 'SkillExtractor' is not defined`
```python
# Create empty class only
class SkillExtractor:
    pass
```

**Iteration 2** - Test fails: `AttributeError: no attribute 'extract'`
```python
# Add method stub only
class SkillExtractor:
    def extract(self, text: str):
        pass
```

**Iteration 3** - Test fails: `TypeError: argument of type 'NoneType' is not iterable`
```python
# Return empty list only
class SkillExtractor:
    def extract(self, text: str):
        return []
```

**Iteration 4** - Test fails: `AssertionError: assert 'React' in []`
```python
# Implement minimal logic to pass
class SkillExtractor:
    def extract(self, text: str):
        return ["React", "Python"]
```

**Test passes** ✅

**Iteration 5** - Refactor (tests still green)
```python
# Extract logic, add constants
SKILL_PATTERNS = ["React", "Python"]

class SkillExtractor:
    def extract(self, text: str) -> list[str]:
        """Extract skills from text."""
        return [skill for skill in SKILL_PATTERNS if skill in text]
```

---

## Special Cases

### Debug Logging

**Allowed without tests**:
```python
import logging

logger = logging.getLogger(__name__)

class JobAnalyzer:
    def analyze(self, posting: str):
        logger.debug(f"Analyzing posting: {posting[:50]}...")
        # ... implementation
```

Debug logs, console statements, and error logging **do not require tests**.

---

### Test Infrastructure

**Allowed without tests** when test fails due to imports:

```python
# Test fails: ModuleNotFoundError: No module named 'models'

# ✅ Create simple stub to fix import
class JobAnalysisResult:
    """Stub for test infrastructure."""
    pass
```

---

### Refactoring Test Code

**Allowed during refactor phase**:

```python
# Extract shared fixture
@pytest.fixture
def sample_tech_posting():
    return """
    Senior Software Engineer
    5+ years React experience
    """

def test_analyzes_tech_posting(sample_tech_posting):
    result = analyzer.analyze(sample_tech_posting)
    assert result["industry"] == "technology"

def test_extracts_tech_skills(sample_tech_posting):
    skills = extractor.extract(sample_tech_posting)
    assert "React" in skills
```

---

## TDD Workflow Checklist

### Before Starting

- [ ] Understand the feature/bug requirement
- [ ] Identify the smallest testable behavior
- [ ] Ensure existing tests are passing

### Red Phase

- [ ] Write ONE failing test
- [ ] Test describes desired behavior
- [ ] Run test - verify it fails correctly
- [ ] Failure message is meaningful

### Green Phase

- [ ] Write minimal code to pass
- [ ] No extra features or methods
- [ ] Run test - verify it passes
- [ ] All other tests still pass

### Refactor Phase

- [ ] All tests are passing
- [ ] Improve code structure
- [ ] Extract constants, methods
- [ ] Run tests after each refactoring step
- [ ] No new functionality added

---

## Common Mistakes

### Mistake 1: Skipping Red Phase

**❌ WRONG**:
```python
# Write implementation first
class Analyzer:
    def analyze(self):
        return "result"

# Then write test
def test_analyze():
    assert Analyzer().analyze() == "result"
```

**✅ CORRECT**: Write test first, see it fail, then implement.

---

### Mistake 2: Not Running Tests

**❌ WRONG**: Making changes without running tests

**✅ CORRECT**:
```bash
# After writing test
$ pytest test_file.py
FAILED - NameError

# After adding stub
$ pytest test_file.py
FAILED - AttributeError

# After implementation
$ pytest test_file.py
PASSED
```

---

### Mistake 3: Refactoring with Failing Tests

**❌ WRONG**:
```bash
$ pytest
...FAILED...

# But still refactoring code
class Analyzer:
    def analyze(self):
        return self._process()  # Extracting method
```

**✅ CORRECT**: Fix failing tests first, THEN refactor.

---

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write wished-for API. Write assertion first. Ask your human partner. |
| Test too complicated | Design too complicated. Simplify interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify design. |

---

## Debugging Integration

Bug found? **Write failing test reproducing it.** Follow TDD cycle.

Test proves fix and prevents regression.

**Never fix bugs without a test.**

---

## Final Rule

**Production code** → test exists and failed first

Otherwise → **not TDD**

No exceptions without your human partner's permission.

---

## General Guidelines

### When Test Output Shows No Tests Run

Sometimes tests fail during import due to missing classes or constructors. In such cases:

1. Create simple stubs to fix imports
2. No need to block on "no tests run" message
3. Focus on making test infrastructure work
4. Then proceed with normal TDD cycle

### Helpful Directions When Stuck

If blocked:
- Check if a simple stub is missing
- Verify imports are correct
- Ensure test can at least run (even if failing)
- Break problem into smaller steps

### New Logic Requires Tests

It is never allowed to introduce new logic without evidence of relevant failing tests.

**Exceptions**:
- Stubs for test infrastructure
- Debug logging
- Type annotations
- Constants replacing magic values
