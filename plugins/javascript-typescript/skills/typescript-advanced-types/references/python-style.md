# Python Backend Style Guide

## Overview

Style guide for Python backend (FastAPI service) implementing NLP/ML processing for job analysis.

## Style Guide

- Follow PEP 8: <https://peps.python.org/pep-0008/>
- Use type hints for all function signatures
- Async-first approach for I/O operations
- Pydantic models for validation

## Naming Conventions

- **Variables**: `snake_case` (e.g., `job_posting`, `extracted_skills`)
- **Functions**: `snake_case` with descriptive verbs (e.g., `extract_requirements`, `classify_industry`)
- **Classes**: `PascalCase` (e.g., `JobAnalyzer`, `IndustryClassifier`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Methods**: `snake_case` (e.g., `analyze_posting`, `match_competencies`)
- **Modules**: `snake_case` (e.g., `classifier.py`, `llm_enhancer.py`)
- **Packages**: Short, lowercase (e.g., `services`, `extractors`)

## Clean Code Guardrails

- **Functions**: ≤50 lines (justify if exceeded)
- **Files**: ≤600 lines (extract modules if larger)
- **Line Length**: Max 88 characters (Black formatter)
- **Nesting Depth**: ≤4 levels for readability
- **Cyclomatic Complexity**: ≤10 per function
- **Magic Numbers**: Use named constants (0, 1, -1 allowed)
- **Comments**: Explain intent (why), not mechanics (what)
- **DRY**: Eliminate duplication through abstraction

## Python File Structure

```python
# python-service/services/extractors/technology.py

# AIDEV-NOTE: Tech industry extractor using hybrid rules + LLM enhancement
from typing import List, Dict
from pydantic import BaseModel

from ..base_extractor import BaseExtractor
from ...models.schemas import Requirement, JobAnalysisResult

class TechnologyExtractor(BaseExtractor):
    """Extract requirements from technology job postings.

    Implements hybrid approach:
    1. Rule-based extraction for explicit skills (React, Python, AWS)
    2. LLM enhancement for implicit requirements and context
    """

    TECHNICAL_SKILL_PATTERNS = [
        r"\b(React|Vue|Angular|Python|Java|AWS|Docker)\b",
        # ... more patterns
    ]

    async def extract_requirements(
        self,
        job_posting: str,
        use_llm: bool = True
    ) -> JobAnalysisResult:
        """Extract requirements using hybrid approach.

        Args:
            job_posting: Raw job description text
            use_llm: Enable LLM enhancement for nuance

        Returns:
            JobAnalysisResult with structured requirements
        """
        # Implementation
        pass
```

## Repository Pattern

All data access through abstract interfaces:

```python
# python-service/repositories/job_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.schemas import JobAnalysisResult

class JobRepository(ABC):
    """Abstract interface for job analysis persistence."""

    @abstractmethod
    async def save_analysis(self, analysis: JobAnalysisResult) -> str:
        """Save job analysis result, return analysis_id."""
        pass

    @abstractmethod
    async def get_analysis(self, analysis_id: str) -> Optional[JobAnalysisResult]:
        """Retrieve saved analysis by ID."""
        pass

# python-service/repositories/sqlite_job_repository.py

class SqliteJobRepository(JobRepository):
    """SQLite implementation of JobRepository."""

    async def save_analysis(self, analysis: JobAnalysisResult) -> str:
        # Implementation
        pass
```

## Async Patterns

I/O operations are async due to LLM calls and database access:

```python
async def analyze_job_posting(
    posting: str,
    classifier: IndustryClassifier,
    extractor_factory: ExtractorFactory
) -> JobAnalysisResult:
    """Analyze job posting using ML classifier and industry extractor.

    AIDEV-NOTE: Performance target <5s, uses async for LLM calls
    """
    # Classify industry (ML model - fast)
    industry = await classifier.predict(posting)

    # Get industry-specific extractor
    extractor = extractor_factory.get_extractor(industry)

    # Extract requirements (rules + LLM)
    requirements = await extractor.extract_requirements(posting)

    return JobAnalysisResult(
        industry=industry,
        requirements=requirements,
        processing_time_ms=...
    )
```

## Error Handling

```python
# python-service/exceptions.py

class JobTailorException(Exception):
    """Base exception for Universal Job Tailor."""
    pass

class IndustryClassificationError(JobTailorException):
    """Failed to classify job posting industry."""
    pass

class ExtractionError(JobTailorException):
    """Failed to extract requirements from posting."""
    pass

class LLMEnhancementError(JobTailorException):
    """LLM API call failed during enhancement."""
    pass

# Usage
async def extract_with_llm(posting: str) -> Dict:
    try:
        response = await openai_client.complete(prompt)
        return parse_llm_response(response)
    except OpenAIError as e:
        logger.error(f"LLM enhancement failed: {e}")
        raise LLMEnhancementError(f"OpenAI API error: {e}") from e
```

## Configuration Management

```python
# python-service/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ML Model Configuration
    classifier_model_path: str = "ml/classifier_model.pkl"
    classification_confidence_threshold: float = 0.85

    # LLM Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    llm_timeout_seconds: int = 30

    # Performance Targets
    max_analysis_time_seconds: int = 5

    class Config:
        env_file = ".env"
        env_prefix = "JOB_TAILOR_"

settings = Settings()
```

## Tools Configuration

### Black (Formatting)

- Line length: 88 characters
- Target Python: 3.11+
- Config in `pyproject.toml`

### Ruff (Linting)

- Security rules (bandit)
- Code quality (bugbear, pylint)
- Import sorting (isort compatible)
- Config in `pyproject.toml`

### Pyright (Type Checking)

- Strict mode enabled
- Virtual environment integration
- Config in `.pyrightconfig.json`

## Common Pitfalls

- Forgetting `await` on async functions
- Not validating Pydantic models (use `.parse()` not `.dict()`)
- Hardcoding LLM prompts (use templates)
- Ignoring ML model confidence thresholds
