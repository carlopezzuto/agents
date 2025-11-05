# Validation Scripts

## Schema Alignment Validation

**Use the project's existing comprehensive validator**:

```bash
# From project root
python scripts/validate_schemas.py
```

**Features**:
- ✅ Validates all Pydantic ↔ Zod schemas
- ✅ Checks enums: `IndustryType`, `SkillImportance`, `ExperienceLevel`
- ✅ Validates 12+ model schemas
- ✅ Granular exit codes for different error types
- ✅ Colorized terminal output
- ✅ Report-only mode: `--report-only`

**Exit Codes**:
- `0` - All schemas aligned successfully
- `1` - General validation failure
- `2` - Missing dependencies (Pydantic not installed)
- `3` - Enum value mismatch
- `4` - Field type mismatch
- `5` - Constraint mismatch (min/max/length)
- `6` - Required/optional field mismatch
- `7` - TypeScript schema file not found

**Validated Models**:
- Job Analysis: `JobAnalysisRequest`, `JobAnalysisResult`, `ExtractedRequirements`
- Skills: `TechnicalSkill`, `InterpersonalSkill`, `DomainKnowledge`
- Competencies: `Competency`, `CompetencyProfile`
- Matching: `CompetencyMatch`, `ResumeMatchRequest`, `ResumeMatchResult`
- Configuration: `UserPreferences`, `MatchingSuggestions`

## Usage in Skill

When the skill guides you to validate schema alignment, use:

```bash
python scripts/validate_schemas.py
```

**Pre-commit Hook** (recommended):
```bash
# Add to .git/hooks/pre-commit
python scripts/validate_schemas.py || exit 1
```

**CI/CD Integration**:
```yaml
- name: Validate Schema Alignment
  run: python scripts/validate_schemas.py
```

## Reference

For schema alignment guidance, see: `../references/schema-alignment.md`

The actual validation script is located at: `/home/armisael/jobtailor/scripts/validate_schemas.py`
