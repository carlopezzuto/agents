# Performance Targets and Optimization

## Performance Guidelines

### Python Backend

- **Target**: <5s total analysis time (p95)
- **ML Inference**: <500ms for industry classification
- **Rule Extraction**: <1s per industry extractor
- **LLM Enhancement**: <3s with timeout/fallback
- **Async I/O**: All network calls (LLM, DB) must be async
- **Caching**: Redis for repeated job postings (Phase 3)

### TypeScript Frontend

- **Target**: <3s PDF generation
- **API Calls**: 5s timeout with retry logic
- **PDF Rendering**: Virtualization for large resumes
- **Bundle Size**: <500KB initial load

## Optimization Strategies

### Backend Optimization

#### Async I/O

All network calls must be async to prevent blocking:

```python
# GOOD - Async operations
async def analyze_job(posting: str) -> JobAnalysisResult:
    # Parallel execution of independent operations
    industry_task = classifier.predict(posting)
    skills_task = extract_basic_skills(posting)

    industry, skills = await asyncio.gather(industry_task, skills_task)

    # Sequential when dependent
    extractor = get_extractor(industry)
    requirements = await extractor.extract(posting)

    return JobAnalysisResult(...)

# BAD - Blocking operations
def analyze_job_blocking(posting: str) -> JobAnalysisResult:
    industry = classifier.predict(posting)  # Blocks
    skills = extract_basic_skills(posting)  # Blocks
    # Wastes time on sequential I/O
```

#### Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_industry_classifier():
    """Cache classifier model loading."""
    return load_model("ml/classifier_model.pkl")

async def analyze_with_cache(posting: str) -> JobAnalysisResult:
    """Cache analysis results for identical postings."""
    cache_key = hashlib.sha256(posting.encode()).hexdigest()

    # Check Redis cache (Phase 3)
    cached_result = await redis_client.get(cache_key)
    if cached_result:
        return JobAnalysisResult.parse_raw(cached_result)

    # Analyze and cache
    result = await analyze_job(posting)
    await redis_client.setex(cache_key, 3600, result.json())

    return result
```

#### Profiling

Use profiling to identify bottlenecks:

```python
import cProfile
import pstats

def profile_analysis():
    """Profile job analysis performance."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Run analysis
    asyncio.run(analyze_job(sample_posting))

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 slowest functions
```

### Frontend Optimization

#### API Timeout and Retry

```typescript
async function analyzeJobWithRetry(
  posting: string,
  maxRetries: number = 3,
  timeout: number = 5000
): Promise<JobAnalysisResponse> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch('/api/analyze-job', {
        method: 'POST',
        signal: controller.signal,
        body: JSON.stringify({ job_posting: posting }),
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (attempt === maxRetries) throw error;

      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }

  throw new Error('Max retries exceeded');
}
```

#### PDF Rendering Optimization

```typescript
import { Document, Page, View, Text } from '@react-pdf/renderer';
import { useMemo } from 'react';

export function OptimizedResume({ data }: ResumeProps) {
  // Memoize expensive computations
  const sortedExperience = useMemo(
    () => data.experience.sort((a, b) => b.year - a.year),
    [data.experience]
  );

  const emphasizedSkills = useMemo(
    () => data.skills.filter(s => s.weight > 0.8),
    [data.skills]
  );

  return (
    <Document>
      <Page size="A4">
        {/* Render only visible content first */}
        <ExperienceSection experience={sortedExperience.slice(0, 3)} />
        <SkillsSection skills={emphasizedSkills} />
      </Page>
    </Document>
  );
}
```

## Performance Monitoring

### Backend Metrics

Track performance metrics in production:

```python
import time
from prometheus_client import Histogram

# Prometheus metrics
ANALYSIS_DURATION = Histogram(
    'job_analysis_duration_seconds',
    'Time spent analyzing job posting',
    ['industry']
)

async def analyze_with_metrics(posting: str) -> JobAnalysisResult:
    start_time = time.time()

    try:
        result = await analyze_job(posting)

        # Record metrics
        duration = time.time() - start_time
        ANALYSIS_DURATION.labels(industry=result.industry).observe(duration)

        # Log if exceeds target
        if duration > 5.0:
            logger.warning(
                f"Analysis exceeded 5s target: {duration:.2f}s for {result.industry}"
            )

        return result
    except Exception as e:
        logger.error(f"Analysis failed after {time.time() - start_time:.2f}s: {e}")
        raise
```

### Frontend Metrics

Track PDF generation performance:

```typescript
export function generatePDFWithMetrics(data: ResumeData): Promise<Blob> {
  const startTime = performance.now();

  return pdf(<ResumeDocument data={data} />)
    .toBlob()
    .then(blob => {
      const duration = performance.now() - startTime;

      // Log to analytics
      analytics.track('pdf_generated', {
        duration_ms: duration,
        size_kb: blob.size / 1024,
        exceeded_target: duration > 3000,
      });

      if (duration > 3000) {
        console.warn(`PDF generation exceeded 3s target: ${duration.toFixed(0)}ms`);
      }

      return blob;
    });
}
```

## Performance Checklist

### Before Committing

- [ ] Run profiler on Python backend
- [ ] Verify analysis completes <5s (p95)
- [ ] Check all I/O operations are async
- [ ] Validate PDF generation <3s
- [ ] Review bundle size <500KB
- [ ] Test timeout and retry logic

### Before Deployment

- [ ] Load test backend with realistic job postings
- [ ] Validate caching effectiveness
- [ ] Verify no performance regressions
- [ ] Check monitoring dashboards
- [ ] Review error rates and timeouts

## Common Performance Issues

### Python Backend

- **Blocking I/O**: Not using async/await for network calls
- **Missing Caching**: Re-analyzing identical job postings
- **Unoptimized Models**: Loading ML models on every request
- **N+1 Queries**: Database queries in loops
- **Heavy Computations**: CPU-intensive work blocking event loop

### TypeScript Frontend

- **Blocking API Calls**: Not implementing timeouts
- **Missing Retries**: Single-attempt failures
- **Unoptimized Renders**: Re-rendering entire PDF on small changes
- **Large Bundles**: Including unnecessary dependencies
- **Memory Leaks**: Not cleaning up event listeners

## Optimization Resources

- **Python Async**: <https://docs.python.org/3/library/asyncio.html>
- **React Performance**: <https://react.dev/learn/render-and-commit>
- **React-PDF Optimization**: <https://react-pdf.org/advanced>
- **Profiling Tools**: cProfile (Python), Chrome DevTools (TypeScript)
