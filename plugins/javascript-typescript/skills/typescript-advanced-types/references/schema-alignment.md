# Schema Alignment - Pydantic ↔ Zod

## Critical Requirement

Zod (TypeScript) and Pydantic (Python) schemas MUST stay synchronized to ensure API contract integrity.

## Synchronization Process

### 1. Python Schema (Source of Truth)

Define schema in Python (Pydantic) first:

```python
# python-service/models/schemas.py

from pydantic import BaseModel
from typing import List

class TechnicalSkill(BaseModel):
    skill: str
    importance: str  # 'required' | 'preferred' | 'nice-to-have'
    weight: float

class JobAnalysisResult(BaseModel):
    detected_industry: str
    confidence: float
    extracted_requirements: ExtractedRequirements
    processing_time_ms: int
```

### 2. TypeScript Schema (Mirror)

Mirror in TypeScript (Zod) with exact field names and types:

```typescript
// src/zod/schemas.ts

export const TechnicalSkillSchema = z.object({
  skill: z.string(),
  importance: z.enum(['required', 'preferred', 'nice-to-have']),
  weight: z.number(),
});

export const JobAnalysisResultSchema = z.object({
  detected_industry: z.string(),
  confidence: z.number(),
  extracted_requirements: ExtractedRequirementsSchema,
  processing_time_ms: z.number(),
});
```

### 3. Validation Steps

1. **Define schema in Python (Pydantic)** first (source of truth)
2. **Mirror in TypeScript (Zod)** with exact field names and types
3. **Test alignment** with contract tests
4. **Update both** when schema changes

## Type Mapping Reference

| Python (Pydantic) | TypeScript (Zod) | Notes |
|-------------------|------------------|-------|
| `str` | `z.string()` | |
| `int` | `z.number()` | Validate with `.int()` if needed |
| `float` | `z.number()` | |
| `bool` | `z.boolean()` | |
| `List[str]` | `z.array(z.string())` | |
| `Optional[str]` | `z.string().optional()` or `.nullable()` | |
| `Literal['a', 'b']` | `z.enum(['a', 'b'])` | |
| `datetime` | `z.string().datetime()` | Serialize as ISO 8601 |
| `Dict[str, Any]` | `z.record(z.any())` | Use sparingly |

## Contract Testing

Create tests that validate both schemas accept/reject the same data:

### Python Contract Test

```python
# python-service/tests/test_schema_alignment.py

import pytest
from models.schemas import JobAnalysisResult

def test_job_analysis_result_accepts_valid_data():
    """Verify Pydantic schema accepts valid data."""
    valid_data = {
        "detected_industry": "technology",
        "confidence": 0.94,
        "extracted_requirements": {...},
        "processing_time_ms": 2341
    }

    result = JobAnalysisResult(**valid_data)
    assert result.detected_industry == "technology"

def test_job_analysis_result_rejects_invalid_confidence():
    """Verify Pydantic schema rejects invalid confidence."""
    invalid_data = {
        "detected_industry": "technology",
        "confidence": 1.5,  # Invalid: > 1.0
        "extracted_requirements": {...},
        "processing_time_ms": 2341
    }

    with pytest.raises(ValidationError):
        JobAnalysisResult(**invalid_data)
```

### TypeScript Contract Test

```typescript
// src/zod/__tests__/schema-alignment.test.ts

import { describe, it, expect } from 'vitest';
import { JobAnalysisResultSchema } from '../schemas';

describe('Schema Alignment', () => {
  it('should accept valid job analysis result', () => {
    const validData = {
      detected_industry: 'technology',
      confidence: 0.94,
      extracted_requirements: {...},
      processing_time_ms: 2341,
    };

    const result = JobAnalysisResultSchema.parse(validData);
    expect(result.detected_industry).toBe('technology');
  });

  it('should reject invalid confidence', () => {
    const invalidData = {
      detected_industry: 'technology',
      confidence: 1.5, // Invalid: > 1.0
      extracted_requirements: {...},
      processing_time_ms: 2341,
    };

    expect(() => JobAnalysisResultSchema.parse(invalidData)).toThrow();
  });
});
```

## Validation Script

Run before committing schema changes:

```bash
python scripts/check_schema_alignment.py
```

This script should:

1. Load Pydantic schemas
2. Load Zod schemas (via TypeScript parser)
3. Compare field names, types, and constraints
4. Report any mismatches
5. Exit with error code if misalignment detected

## Common Misalignments

### Field Name Mismatch

```python
# Python (WRONG)
class Example(BaseModel):
    user_id: int

# TypeScript (WRONG)
const ExampleSchema = z.object({
  userId: z.number()  // camelCase doesn't match snake_case
});
```

**Fix**: Use snake_case in both (Zod allows it):

```typescript
const ExampleSchema = z.object({
  user_id: z.number()  // Matches Python
});
```

### Type Incompatibility

```python
# Python
class Example(BaseModel):
    confidence: float  # 0.0 to 1.0

# TypeScript (WRONG)
const ExampleSchema = z.object({
  confidence: z.number()  // Missing range validation
});
```

**Fix**: Add validation constraints:

```typescript
const ExampleSchema = z.object({
  confidence: z.number().min(0).max(1)  // Matches Python constraint
});
```

### Optional vs Nullable

```python
# Python
class Example(BaseModel):
    optional_field: Optional[str] = None

# TypeScript (AMBIGUOUS)
const ExampleSchema = z.object({
  optional_field: z.string().optional()  // undefined allowed
  // or
  optional_field: z.string().nullable()  // null allowed
});
```

**Fix**: Clarify intent and match Python behavior:

```typescript
// If Python allows both None and missing:
optional_field: z.string().nullable().optional()
```

## Maintenance Workflow

### When Adding New Schema

1. Define Pydantic model in `python-service/models/schemas.py`
2. Add Zod schema in `src/zod/schemas.ts`
3. Add contract tests in both Python and TypeScript
4. Run `scripts/check_schema_alignment.py`
5. Verify tests pass on both sides

### When Modifying Existing Schema

1. Update Pydantic model first
2. Update corresponding Zod schema
3. Update contract tests
4. Run alignment validation
5. Update API documentation
6. Deploy both backend and frontend together

## Best Practices

- **Always update both schemas together** - Never deploy mismatched schemas
- **Use snake_case consistently** - Matches Python conventions and avoids serialization issues
- **Add validation constraints** - Match Pydantic validators in Zod
- **Test edge cases** - Validate both schemas handle boundary conditions identically
- **Version schemas** - Consider schema versioning for breaking changes
- **Document changes** - Note schema modifications in commit messages
