# Testing Standards

## Core Testing Philosophy (Both Stacks)

- **TDD Workflow**: Red → Green → Refactor
- **Write tests FIRST** before implementation
- **ALL tests must pass** before committing
- **No feature without tests** - Every function/class needs tests
- **Coverage Targets**: Backend ≥80%, Frontend ≥70%, Critical paths 100%
- **Test Independence**: No shared state between tests
- **Deterministic**: Same input = same output, always

## Python Testing (pytest)

```python
# python-service/tests/test_technology_extractor.py

import pytest
from services.extractors.technology import TechnologyExtractor

# AIDEV-NOTE: Tests validate extraction accuracy against real job postings

@pytest.fixture
def tech_extractor():
    """Fixture provides TechnologyExtractor instance."""
    return TechnologyExtractor()

@pytest.fixture
def sample_tech_job():
    """Fixture provides real tech job posting sample."""
    return """
    Senior Frontend Developer
    5+ years React experience required.
    TypeScript, AWS, Docker preferred.
    Lead a team of 3-5 engineers.
    """

@pytest.mark.asyncio
async def test_extracts_required_technical_skills(tech_extractor, sample_tech_job):
    """Given tech job posting, when extracting requirements,
    then identifies React as required technical skill with high weight."""

    # When
    result = await tech_extractor.extract_requirements(sample_tech_job, use_llm=False)

    # Then
    technical_skills = result.extracted_requirements.technical_skills
    react_skill = next(s for s in technical_skills if s.skill == "React")

    assert react_skill.importance == "required"
    assert react_skill.weight >= 0.8

@pytest.mark.asyncio
async def test_extraction_completes_within_performance_target(tech_extractor, sample_tech_job):
    """Given job posting, when analyzing, then completes within 5s target."""

    # When
    result = await tech_extractor.extract_requirements(sample_tech_job)

    # Then
    assert result.processing_time_ms < 5000, "Extraction exceeded 5s performance target"
```

## TypeScript Testing (Vitest)

```typescript
// src/services/__tests__/job-analyzer.test.ts

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { JobAnalyzer } from '../job-analyzer';

// AIDEV-NOTE: Mock Python API calls, test TypeScript integration logic

describe('JobAnalyzer', () => {
  let analyzer: JobAnalyzer;

  beforeEach(() => {
    analyzer = new JobAnalyzer('http://localhost:8000');
  });

  it('should analyze job posting and return structured result', async () => {
    // Given
    const mockResponse = {
      detected_industry: 'technology',
      confidence: 0.94,
      extracted_requirements: {
        technical_skills: [{ skill: 'React', importance: 'required', weight: 0.9 }],
      },
      processing_time_ms: 2341,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const jobPosting = 'Senior React Developer...';

    // When
    const result = await analyzer.analyzeJob(jobPosting);

    // Then
    expect(result.detected_industry).toBe('technology');
    expect(result.confidence).toBeGreaterThanOrEqual(0.85);
    expect(result.extracted_requirements.technical_skills).toHaveLength(1);
  });

  it('should throw error when API call fails', async () => {
    // Given
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      statusText: 'Internal Server Error',
    });

    // When/Then
    await expect(analyzer.analyzeJob('Invalid posting')).rejects.toThrow(
      'Job analysis failed: Internal Server Error',
    );
  });
});
```

## Test Structure (Both Stacks)

### Given-When-Then Pattern

```python
# Given: Set up test conditions
user_profile = create_test_profile()
job_requirements = create_test_requirements()

# When: Execute behavior
matches = await matcher.match_competencies(user_profile, job_requirements)

# Then: Assert expected outcome
assert len(matches) > 0
assert matches[0].match_score >= 0.8
```

## Test Pyramid Balance

- **Unit Tests** (~70%): Individual functions, pure logic, fast (<100ms)
- **Integration Tests** (~20%): API endpoints, database, services (<1s)
- **E2E Tests** (~10%): Full workflow, Python → TypeScript → PDF (<10s)

## Anti-Patterns to Avoid

### ❌ Testing Implementation Details

```python
# Bad - Testing private methods
def test_private_validation():
    assert extractor._validate_pattern(text) == True

# Good - Testing public behavior
def test_extracts_valid_skills():
    result = await extractor.extract_requirements(job_posting)
    assert len(result.technical_skills) > 0
```

### ❌ Multiple Behaviors Per Test

```typescript
// Bad - Testing multiple behaviors
it('should handle all validation cases', () => {
  expect(validate(validData)).toBe(true);
  expect(validate(invalidData)).toBe(false);
  expect(validate(null)).toThrow();
});

// Good - Separate tests
it('should accept valid job posting', () => {
  expect(validate(validData)).toBe(true);
});

it('should reject invalid job posting', () => {
  expect(validate(invalidData)).toBe(false);
});
```

### ❌ Excessive Mocking

```python
# Bad - Mocking core business logic
def test_with_all_mocks():
    mock_classifier = Mock()
    mock_extractor = Mock()
    mock_matcher = Mock()
    # Not testing anything real

# Good - Mock only external dependencies (LLM, DB)
def test_with_minimal_mocks():
    real_extractor = TechnologyExtractor()
    mock_llm_client = Mock()  # External dependency
    result = await real_extractor.extract(posting, llm_client=mock_llm_client)
```

## Coverage Targets

- **Backend (Python)**: ≥80% overall
- **Frontend (TypeScript)**: ≥70% overall
- **Critical Paths**: 100% (job analysis pipeline, schema validation, PDF generation)

## Running Tests

### Python

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_technology_extractor.py

# Run with verbose output
pytest -v
```

### TypeScript

```bash
# Run all tests
bun test

# Run with coverage
bun test --coverage

# Run specific test file
bun test src/services/__tests__/job-analyzer.test.ts

# Run in watch mode
bun test --watch
```
