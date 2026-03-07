# Anti-Patterns

Common TDD mistakes and how to avoid them.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |
| "Test hard = design unclear" | Listen to test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD faster than debugging. Pragmatic = test-first. |
| "Manual test faster" | Manual doesn't prove edge cases. You'll re-test every change. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |

---

## Testing Anti-Patterns

### ❌ Testing Implementation Details

**Problem**: Tests break when refactoring internal implementation.

**Bad Example**:

```python
class JobAnalyzer:
    def __init__(self):
        self._cache = {}

    def analyze(self, posting):
        if posting in self._cache:
            return self._cache[posting]
        # ... analysis logic

# ❌ Bad - Testing private implementation
def test_caches_results():
    analyzer = JobAnalyzer()
    analyzer.analyze("posting")
    assert "posting" in analyzer._cache  # Tests internal state
```

**Good Example**:

```python
# ✅ Good - Testing public behavior
def test_returns_consistent_results():
    analyzer = JobAnalyzer()
    result1 = analyzer.analyze("posting")
    result2 = analyzer.analyze("posting")
    assert result1 == result2  # Tests observable behavior
```

**Why**: Internal implementation can change (e.g., switching from dict to LRU cache) without changing behavior.

---

### ❌ Multiple Behaviors Per Test

**Problem**: Hard to identify which behavior failed, violates single responsibility.

**Bad Example**:

```python
# ❌ Bad - Multiple assertions for different behaviors
def test_job_analyzer():
    analyzer = JobAnalyzer()

    # Testing multiple unrelated behaviors
    result1 = analyzer.analyze("Software Engineer")
    assert result1["industry"] == "technology"

    result2 = analyzer.analyze("Nurse")
    assert result2["industry"] == "healthcare"

    result3 = analyzer.analyze("")
    assert result3 is None
```

**Good Example**:

```python
# ✅ Good - One behavior per test
def test_classifies_tech_posting():
    result = JobAnalyzer().analyze("Software Engineer")
    assert result["industry"] == "technology"

def test_classifies_healthcare_posting():
    result = JobAnalyzer().analyze("Nurse")
    assert result["industry"] == "healthcare"

def test_returns_none_for_empty_posting():
    result = JobAnalyzer().analyze("")
    assert result is None
```

---

### ❌ Excessive Mocking

**Problem**: Tests become coupled to implementation, don't test real behavior.

**Bad Example**:

```python
# ❌ Bad - Mocking core business logic
def test_with_all_mocks():
    mock_classifier = Mock()
    mock_extractor = Mock()
    mock_matcher = Mock()
    mock_scorer = Mock()

    # Not testing anything real
    analyzer = JobAnalyzer(
        classifier=mock_classifier,
        extractor=mock_extractor,
        matcher=mock_matcher,
        scorer=mock_scorer
    )
```

**Good Example**:

```python
# ✅ Good - Mock only external dependencies
def test_with_minimal_mocks():
    mock_llm_client = Mock()  # External API
    mock_llm_client.complete.return_value = {"industry": "tech"}

    # Real business logic
    analyzer = JobAnalyzer(llm_client=mock_llm_client)
    result = analyzer.analyze("Software Engineer...")

    assert result["industry"] == "technology"
```

**Rule**: Mock I/O boundaries (APIs, databases, file system), test real business logic.

---

### ❌ Testing Mock Behavior

**Problem**: Verifying mocks exist instead of testing real component behavior.

**Bad Example (TypeScript)**:

```typescript
// ❌ Bad - Testing that the mock exists
test('renders job analysis panel', () => {
  render(<JobAnalysisPage />);
  expect(screen.getByTestId('analyzer-mock')).toBeInTheDocument();
});
```

**Bad Example (Python)**:

```python
# ❌ Bad - Testing mock was called, not actual behavior
def test_analyzes_job_posting():
    mock_classifier = Mock()
    analyzer = JobAnalyzer(classifier=mock_classifier)

    analyzer.analyze("Software Engineer")

    # Testing mock behavior, not real functionality
    assert mock_classifier.classify.called
```

**Good Example (TypeScript)**:

```typescript
// ✅ Good - Test real component behavior
test('displays industry classification result', async () => {
  render(<JobAnalysisPage />);

  const input = screen.getByRole('textbox', { name: /job posting/i });
  await userEvent.type(input, 'Software Engineer position');
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }));

  expect(await screen.findByText(/technology/i)).toBeInTheDocument();
});
```

**Good Example (Python)**:

```python
# ✅ Good - Test actual output, not mock interactions
def test_analyzes_job_posting():
    mock_llm = Mock()  # Only mock external API
    mock_llm.complete.return_value = {"industry": "technology"}

    analyzer = JobAnalyzer(llm_client=mock_llm)
    result = analyzer.analyze("Software Engineer required...")

    # Test real behavior
    assert result["detected_industry"] == "technology"
    assert result["confidence"] > 0.85
```

**Rule**: Test what the code does, not what the mocks do.

---

### ❌ Incomplete Mocks

**Problem**: Partial mocks hide structural assumptions and cause silent failures.

**Bad Example (Python)**:

```python
# ❌ Bad - Partial mock missing fields downstream code needs
def test_processes_job_analysis():
    mock_response = {
        "detected_industry": "technology",
        "confidence": 0.94
        # Missing: extracted_requirements that PDF generator uses
    }

    # Later: breaks when PDF generator accesses response["extracted_requirements"]
    pdf_generator.generate(mock_response)
```

**Bad Example (TypeScript)**:

```typescript
// ❌ Bad - Incomplete API response mock
const mockJobAnalysis = {
  industry: 'technology',
  confidence: 0.94
  // Missing: skills array, processing_time_ms
};

// Test passes but real API integration fails
```

**Good Example (Python)**:

```python
# ✅ Good - Complete mock matching real API structure
def test_processes_job_analysis():
    mock_response = {
        "detected_industry": "technology",
        "confidence": 0.94,
        "extracted_requirements": {
            "technical_skills": [
                {"skill": "React", "importance": "required", "weight": 0.9}
            ],
            "interpersonal_skills": [],
            "domain_knowledge": []
        },
        "processing_time_ms": 2341
    }

    # All fields downstream code expects
    pdf_generator.generate(mock_response)
```

**Good Example (TypeScript)**:

```typescript
// ✅ Good - Mirror complete API response structure
const mockJobAnalysis: JobAnalysisResponse = {
  detected_industry: 'technology',
  confidence: 0.94,
  extracted_requirements: {
    technical_skills: [
      { skill: 'React', importance: 'required', weight: 0.9 }
    ],
    interpersonal_skills: [],
    domain_knowledge: []
  },
  processing_time_ms: 2341
};
```

**Rule**: Mock complete data structures as they exist in reality, not just fields your immediate test uses.

**Checklist before creating mocks**:

- [ ] Examined actual API response documentation
- [ ] Included ALL fields system might consume downstream
- [ ] Verified mock matches Pydantic/Zod schema completely

---

### ❌ Test-Only Methods in Production

**Problem**: Production classes polluted with methods only used by tests.

**Bad Example (Python)**:

```python
# ❌ Bad - cleanup() only used in tests
class JobAnalysisSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.workspace_path = create_workspace(session_id)

    async def cleanup(self):  # Looks like production API!
        """Destroy workspace - ONLY CALLED BY TESTS"""
        await destroy_workspace(self.session_id)
        # ... cleanup logic
```

**Bad Example (TypeScript)**:

```typescript
// ❌ Bad - reset() only exists for tests
class AnalysisCache {
  private cache: Map<string, Analysis> = new Map();

  // Production API
  get(key: string): Analysis | undefined {
    return this.cache.get(key);
  }

  // ⚠️ Test-only method polluting production class
  reset(): void {
    this.cache.clear();
  }
}
```

**Good Example (Python)**:

```python
# ✅ Good - No cleanup() method in production class
class JobAnalysisSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.workspace_path = create_workspace(session_id)

# Test utilities handle cleanup
# In tests/utils/cleanup.py
async def cleanup_session(session: JobAnalysisSession):
    """Test utility for session cleanup"""
    await destroy_workspace(session.session_id)
```

**Good Example (TypeScript)**:

```typescript
// ✅ Good - Production class stays clean
class AnalysisCache {
  private cache: Map<string, Analysis> = new Map();

  get(key: string): Analysis | undefined {
    return this.cache.get(key);
  }
}

// Test utilities handle reset
// In tests/utils/cache-helpers.ts
export function resetCache(cache: AnalysisCache): void {
  // Access via reflection or create fresh instance
  cache = new AnalysisCache();
}
```

**Rule**: If a method is only called in tests, put it in test utilities, not production code.

**Gate checklist before adding any method**:

- [ ] Is this only used by tests? → Move to test utilities
- [ ] Does this class own this resource's lifecycle? → If no, wrong class
- [ ] Would this be dangerous if called in production? → Definitely test-only

---

### ❌ Brittle Tests

**Problem**: Tests fail for reasons unrelated to actual bugs.

**Bad Example**:

```python
# ❌ Bad - Hard-coded dates
def test_recent_posting():
    posting = {"date": "2024-01-15", "title": "Engineer"}
    result = analyzer.is_recent(posting)
    assert result == True  # Breaks when date changes
```

**Good Example**:

```python
# ✅ Good - Relative dates
from datetime import datetime, timedelta

def test_recent_posting():
    yesterday = datetime.now() - timedelta(days=1)
    posting = {"date": yesterday.isoformat(), "title": "Engineer"}
    result = analyzer.is_recent(posting)
    assert result == True
```

---

### ❌ Test Order Dependencies

**Problem**: Tests pass/fail based on execution order.

**Bad Example**:

```python
# ❌ Bad - Tests depend on order
shared_database = []

def test_first_adds_item():
    shared_database.append("item1")
    assert len(shared_database) == 1

def test_second_uses_item():
    # Fails if run alone, passes after test_first
    assert shared_database[0] == "item1"
```

**Good Example**:

```python
# ✅ Good - Independent tests with fixtures
@pytest.fixture
def database():
    return []

def test_first_adds_item(database):
    database.append("item1")
    assert len(database) == 1

def test_second_uses_item(database):
    database.append("item1")
    assert database[0] == "item1"
```

---

### ❌ Unclear Test Names

**Problem**: Can't understand what test validates without reading code.

**Bad Example**:

```python
# ❌ Bad - Unclear names
def test_1():
    pass

def test_analyzer():
    pass

def test_it_works():
    pass
```

**Good Example**:

```python
# ✅ Good - Descriptive names
def test_classifies_tech_posting_as_technology_industry():
    pass

def test_returns_none_when_posting_is_empty():
    pass

def test_extracts_required_skills_from_job_description():
    pass
```

---

### ❌ Testing Framework Code

**Problem**: Testing third-party library behavior, not your code.

**Bad Example**:

```python
# ❌ Bad - Testing pytest fixtures work
def test_fixture_returns_value(sample_data):
    assert sample_data is not None

# ❌ Bad - Testing dict behavior
def test_dict_assignment():
    d = {}
    d["key"] = "value"
    assert d["key"] == "value"
```

**Good Example**:

```python
# ✅ Good - Testing your code behavior
def test_analyzer_uses_sample_data_correctly(sample_data):
    result = analyzer.process(sample_data)
    assert result["status"] == "processed"
```

---

## TDD Anti-Patterns

### ❌ Writing Multiple Tests at Once

**Problem**: Violates TDD discipline, harder to debug failures.

**Bad Example**:

```python
# ❌ Bad - Writing 5 tests before implementing
def test_analyzes_tech_posting():
    pass

def test_analyzes_healthcare_posting():
    pass

def test_analyzes_finance_posting():
    pass

def test_handles_empty_posting():
    pass

def test_handles_invalid_posting():
    pass

# All failing, which to fix first?
```

**Good Example**:

```python
# ✅ Good - One test at a time
def test_analyzes_tech_posting():
    result = JobAnalyzer().analyze("Software Engineer")
    assert result["industry"] == "technology"

# Make this pass first, THEN add next test
```

---

### ❌ Over-Implementation

**Problem**: Implementing features not required by current failing test.

**Bad Example**:

```python
# Test only requires analyze() to return industry
def test_returns_industry():
    result = analyzer.analyze("Software Engineer")
    assert result["industry"] == "technology"

# ❌ Bad - Over-implemented
class JobAnalyzer:
    def analyze(self, posting):
        # Too much for current test
        return {
            "industry": self._classify_industry(posting),
            "confidence": self._calculate_confidence(posting),
            "skills": self._extract_skills(posting),
            "salary_range": self._estimate_salary(posting),
            "location": self._parse_location(posting)
        }
```

**Good Example**:

```python
# ✅ Good - Minimal implementation
class JobAnalyzer:
    def analyze(self, posting):
        return {"industry": "technology"}

# Add more features when tests require them
```

---

### ❌ Premature Abstraction

**Problem**: Creating abstractions before patterns emerge.

**Bad Example**:

```python
# ❌ Bad - Complex abstraction after first test
class BaseAnalyzer(ABC):
    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def analyze(self):
        pass

class JobAnalyzer(BaseAnalyzer):
    def preprocess(self):
        # Not needed yet
        pass
```

**Good Example**:

```python
# ✅ Good - Simple implementation
class JobAnalyzer:
    def analyze(self, posting):
        return {"industry": "technology"}

# Wait for 3+ similar patterns before abstracting
```

**Rule**: Wait until you have 3 similar cases before abstracting.

---

### ❌ Refactoring with Failing Tests

**Problem**: Can't distinguish between refactoring breaks and test failures.

**Bad Example**:

```bash
$ pytest
...FAILED...

# ❌ Bad - Refactoring anyway
class JobAnalyzer:
    def analyze(self, posting):
        # Extracting method while tests fail
        return self._process_posting(posting)
```

**Good Example**:

```bash
$ pytest
...FAILED...

# ✅ Good - Fix test first
class JobAnalyzer:
    def analyze(self, posting):
        # Fix the failure
        return {"industry": "technology"}

$ pytest
...PASSED...

# Now safe to refactor
class JobAnalyzer:
    def analyze(self, posting):
        return self._process_posting(posting)
```

---

### ❌ Not Running Tests

**Problem**: Writing code without feedback, defeats TDD purpose.

**Bad Example**:

```python
# Write test
def test_analyze():
    result = analyzer.analyze("posting")
    assert result["industry"] == "tech"

# Write implementation without running test
class JobAnalyzer:
    def analyze(self, posting):
        return {"industry": "tech"}

# Write more tests without running
def test_extract():
    pass
```

**Good Example**:

```python
# Write test
def test_analyze():
    result = analyzer.analyze("posting")
    assert result["industry"] == "tech"

# Run test - see it fail
$ pytest test_analyzer.py
FAILED

# Implement
class JobAnalyzer:
    def analyze(self, posting):
        return {"industry": "tech"}

# Run test - see it pass
$ pytest test_analyzer.py
PASSED
```

---

## General Testing Anti-Patterns

### ❌ Sleeping in Tests

**Problem**: Slow, flaky tests.

**Bad Example**:

```python
# ❌ Bad - Using sleep
import time

def test_async_operation():
    trigger_async_operation()
    time.sleep(5)  # Hope it completes
    assert operation_completed()
```

**Good Example**:

```python
# ✅ Good - Proper async handling
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_operation()
    assert result.completed
```

---

### ❌ Global State

**Problem**: Tests affect each other, unpredictable failures.

**Bad Example**:

```python
# ❌ Bad - Global state
global_config = {"mode": "test"}

def test_changes_config():
    global_config["mode"] = "production"
    assert global_config["mode"] == "production"

def test_uses_config():
    # Fails if previous test ran first
    assert global_config["mode"] == "test"
```

**Good Example**:

```python
# ✅ Good - Isolated state
def test_changes_config():
    config = {"mode": "test"}
    config["mode"] = "production"
    assert config["mode"] == "production"

def test_uses_config():
    config = {"mode": "test"}
    assert config["mode"] == "test"
```

---

### ❌ Testing Too Much in One Test

**Problem**: Hard to debug, violates single responsibility.

**Bad Example**:

```python
# ❌ Bad - Testing entire workflow
def test_complete_job_analysis_pipeline():
    # 50 lines of setup
    posting = load_posting()
    analyzer = JobAnalyzer()
    classifier = IndustryClassifier()
    extractor = SkillExtractor()
    matcher = CompetencyMatcher()

    # Multiple behaviors tested
    industry = classifier.classify(posting)
    assert industry == "technology"

    skills = extractor.extract(posting)
    assert len(skills) > 0

    analysis = analyzer.analyze(posting)
    assert analysis["confidence"] > 0.8

    matches = matcher.match(skills, user_profile)
    assert len(matches) > 0
```

**Good Example**:

```python
# ✅ Good - Focused unit tests
def test_classifies_tech_posting():
    industry = classifier.classify("Software Engineer")
    assert industry == "technology"

def test_extracts_skills_from_posting():
    skills = extractor.extract("React, Python required")
    assert "React" in skills

def test_analyzes_posting_with_confidence():
    analysis = analyzer.analyze("Developer role")
    assert analysis["confidence"] > 0.8
```

---

## How to Avoid Anti-Patterns

### Checklist

- [ ] Test behavior, not implementation
- [ ] One behavior per test
- [ ] Mock only I/O boundaries
- [ ] **Test real code, not mock behavior**
- [ ] **Mock complete data structures (match Pydantic/Zod schemas)**
- [ ] **No test-only methods in production classes**
- [ ] Independent tests (no shared state)
- [ ] Clear, descriptive test names
- [ ] Follow Red-Green-Refactor strictly
- [ ] Run tests frequently
- [ ] Keep tests fast (<100ms unit tests)

### Code Review Questions

1. **Does this test check behavior or implementation?**
2. **Would this test break if I refactored the code?**
3. **Can this test run in isolation?**
4. **Is the test name clear without reading the code?**
5. **Am I testing my code or the framework?**
6. **Did I add more than one test at a time?**
7. **Am I over-implementing for the current test?**
8. **Am I testing what the code does, or what the mocks do?**
9. **Does my mock match the complete API response structure?**
10. **Is this method only called by tests? (If yes, move to test utilities)**

### When in Doubt

- **Simplify**: Start with simplest possible test
- **One thing**: Test one behavior only
- **Real code**: Test your code, not libraries
- **Behavior focus**: Test what, not how
- **TDD discipline**: Red → Green → Refactor, strictly
