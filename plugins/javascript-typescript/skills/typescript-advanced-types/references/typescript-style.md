# TypeScript Frontend Style Guide

## Overview

Style guide for TypeScript frontend (React + PDF) implementing UI and PDF generation.

## Style Guide

- Follow Airbnb TypeScript Style Guide
- Strict TypeScript mode enabled
- ESLint + Prettier for formatting
- Functional components with hooks

## Naming Conventions

- **Variables**: `camelCase` (e.g., `jobPosting`, `matchedSkills`)
- **Functions**: `camelCase` (e.g., `analyzeJob`, `generatePDF`)
- **Components**: `PascalCase` (e.g., `ResumeTemplate`, `SkillsSection`)
- **Interfaces/Types**: `PascalCase` with descriptive names (e.g., `JobAnalysisResponse`, `CompetencyProfile`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `API_BASE_URL`, `MAX_FILE_SIZE`)
- **Files**: `kebab-case` for modules (e.g., `job-analyzer.ts`), `PascalCase` for components (e.g., `ResumeTemplate.tsx`)

## Clean Code Guardrails

- **Functions**: ≤50 lines (extract helpers if needed)
- **Files**: ≤600 lines (split into modules)
- **Line Length**: Max 100 characters
- **Nesting Depth**: ≤3 levels (early returns preferred)
- **Component Complexity**: ≤10 props per component
- **Magic Values**: Use design tokens or constants

## TypeScript File Structure

```typescript
// src/services/job-analyzer.ts

// AIDEV-NOTE: Interfaces with Python backend for job analysis
import { z } from 'zod';
import { JobAnalysisRequestSchema, JobAnalysisResponseSchema } from '../zod/schemas';

export class JobAnalyzer {
  private readonly apiBaseUrl: string;

  constructor(apiBaseUrl: string = import.meta.env.VITE_API_URL) {
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * Analyze job posting via Python backend.
   *
   * @param jobPosting - Raw job description text
   * @param enableLLM - Enable LLM enhancement (default: true)
   * @returns Structured job analysis with industry classification
   * @throws {Error} If API call fails or validation fails
   */
  async analyzeJob(jobPosting: string, enableLLM: boolean = true): Promise<JobAnalysisResponse> {
    const request = JobAnalysisRequestSchema.parse({
      job_posting: jobPosting,
      user_preferences: { enable_llm_enhancement: enableLLM },
    });

    const response = await fetch(`${this.apiBaseUrl}/api/analyze-job`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Job analysis failed: ${response.statusText}`);
    }

    const data = await response.json();
    return JobAnalysisResponseSchema.parse(data);
  }
}
```

## React Component Patterns

```typescript
// src/templates/resume/SkillsSection.tsx

import { Text, View } from '@react-pdf/renderer';
import { styles } from '../design-tokens';
import type { Competency } from '../../types';

interface SkillsSectionProps {
  skills: Competency[];
  emphasizedSkills?: string[]; // From job matching
}

/**
 * Skills section with dynamic emphasis based on job requirements.
 *
 * AIDEV-NOTE: Emphasized skills rendered first with visual distinction
 */
export function SkillsSection({ skills, emphasizedSkills = [] }: SkillsSectionProps) {
  const emphasized = skills.filter(s => emphasizedSkills.includes(s.skill));
  const regular = skills.filter(s => !emphasizedSkills.includes(s.skill));

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Technical Skills</Text>

      {/* Emphasized skills first */}
      {emphasized.map(skill => (
        <Text key={skill.skill} style={styles.skillEmphasized}>
          {skill.skill} - {skill.proficiency}
        </Text>
      ))}

      {/* Regular skills */}
      {regular.map(skill => (
        <Text key={skill.skill} style={styles.skill}>
          {skill.skill} - {skill.proficiency}
        </Text>
      ))}
    </View>
  );
}
```

## Zod Schema Validation

```typescript
// src/zod/schemas.ts

import { z } from 'zod';

// AIDEV-NOTE: Schemas must align with Python Pydantic models

export const CompetencySchema = z.object({
  technical: z.array(z.string()),
  interpersonal: z.array(z.string()),
  domain_specific: z.array(z.string()),
});

export const JobAnalysisRequestSchema = z.object({
  job_posting: z.string().min(50, 'Job posting too short'),
  user_preferences: z.object({
    enable_llm_enhancement: z.boolean().default(true),
    target_industry: z.string().nullable().optional(),
  }),
});

export const JobAnalysisResponseSchema = z.object({
  detected_industry: z.string(),
  confidence: z.number().min(0).max(1),
  extracted_requirements: z.object({
    technical_skills: z.array(
      z.object({
        skill: z.string(),
        importance: z.enum(['required', 'preferred', 'nice-to-have']),
        weight: z.number().min(0).max(1),
      }),
    ),
    // ... more fields
  }),
  processing_time_ms: z.number(),
});

// Type inference
export type JobAnalysisRequest = z.infer<typeof JobAnalysisRequestSchema>;
export type JobAnalysisResponse = z.infer<typeof JobAnalysisResponseSchema>;
```

## Tools Configuration

### ESLint

- Airbnb base config
- TypeScript plugin
- React hooks plugin
- Config in `.eslintrc.json`

### Prettier

- Print width: 100
- Single quotes
- Trailing commas: es5
- Config in `.prettierrc`

### TypeScript

- Strict mode: `true`
- No implicit any
- Config in `tsconfig.json`

## Common Pitfalls

- Not validating API responses with Zod
- Forgetting error boundaries in React
- Blocking PDF render with heavy computation
- Not handling API timeout gracefully
