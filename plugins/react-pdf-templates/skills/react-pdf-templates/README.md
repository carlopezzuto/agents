# React-PDF Templates Skill

Code style and development patterns skill for professional PDF document generation using @react-pdf/renderer.

## Purpose

This skill provides comprehensive guidance for creating and modifying PDF templates in the Universal Job Tailor resume generator project. It consolidates React-PDF component documentation, font configuration, styling patterns, and troubleshooting techniques into a modular, token-efficient structure.

## Activation

**Automatic**: Claude loads this skill when:
- Creating new PDF components
- Modifying existing resume/cover letter templates
- Working with React-PDF styling
- Debugging layout or rendering issues
- Configuring fonts or typography
- Troubleshooting PDF generation

**Manual**: Reference specific guidance via:
```
See: references/components-catalog.md
See: references/font-configuration.md
See: references/styling-patterns.md
See: references/troubleshooting.md
```

## Structure

```
react-pdf-templates/
├── SKILL.md                          # Main skill entry point (quick reference)
├── README.md                         # This file (skill documentation)
└── references/                       # Detailed reference documentation
    ├── components-catalog.md         # React-PDF component API reference
    ├── font-configuration.md         # Font registration and typography
    ├── styling-patterns.md           # CSS properties and StyleSheet API
    └── troubleshooting.md            # Page wrapping, navigation, debugging
```

## Quick Reference

### Core Technologies

- **Runtime**: Bun (JavaScript runtime and bundler)
- **PDF Engine**: @react-pdf/renderer
- **Type Safety**: TypeScript with strict mode
- **Design System**: Centralized design tokens (`design-tokens.ts`)
- **Fonts**: Lato (primary), Open Sans (secondary)

### Essential Components

- **Document**: Root component, PDF document wrapper
- **Page**: Single page (size: "A4", orientation: "portrait")
- **View**: Container for layout (flexbox)
- **Text**: Text content (supports inline styling)
- **Image**: JPG/PNG images (network, local, base64)
- **Link**: External or internal navigation
- **Canvas**: Free-form drawing with painter API

### Design Tokens

**Colors** (Tailwind-based palette):
- `colors.primary` - Main text (zinc-900)
- `colors.accent` - Highlights/links (rose-600)
- `colors.darkGray` - Content text (zinc-800)
- `colors.mediumGray` - Secondary text (zinc-600)
- `colors.separatorGray` - Separator lines (zinc-400)

**Typography**:
- `typography.text` - Body: 9px, Lato, lineHeight 1.33
- `typography.title` - Main: 22px, Lato Bold, uppercase
- `typography.subtitle` - Section: 14px, Lato Bold, capitalize

**Spacing**:
- `spacing.columnWidth` - Left column: 180
- `spacing.documentPadding` - Document padding: 42
- `spacing.pagePadding` - Section padding: 18
- `spacing.profileImageSize` - Profile image: 46

### Critical Requirements

1. **Design Token Usage**: Always use centralized design system instead of hardcoded values
2. **Type Safety**: All components receive typed data through `ResumeSchema` interface
3. **StyleSheet Performance**: Use `StyleSheet.create()` instead of inline styles
4. **Font Registration**: Fonts must be registered before document render

## Token Efficiency

**Before (rpdf/ directory)**:
- 5 markdown files
- ~60,000 tokens
- Always loaded when referenced

**After (react-pdf-templates skill)**:
- SKILL.md: ~1-2K tokens (always via metadata)
- References: ~3-5K tokens (loaded when needed)
- **Savings**: ~92% token reduction (60K → 5K)

## Migration from rpdf/ Directory

This skill replaces the `/rpdf` documentation directory with a modular, token-efficient structure:

**Migrated Content**:
- `rpdf/CLAUDE.md` → Integrated into SKILL.md + all references
- `rpdf/components.md` → `references/components-catalog.md`
- `rpdf/fonts.md` → `references/font-configuration.md`
- `rpdf/styling.md` → `references/styling-patterns.md`
- `rpdf/troubleshooting.md` → `references/troubleshooting.md`

**Original Directory**:
- Keep for reference during transition
- Archive to `docs/archive/rpdf/` after validation
- Update project documentation to reference skill instead

## Usage Examples

### Creating New Component

Claude automatically loads `references/components-catalog.md` when:
- Creating new PDF component files
- Understanding component props and API
- Working with Document, Page, View, Text, Image, Link

### Font Configuration

Claude loads `references/font-configuration.md` when:
- Registering new fonts
- Debugging font loading issues
- Working with typography and text rendering
- Configuring emoji support

### Styling Components

Claude loads `references/styling-patterns.md` when:
- Creating StyleSheet definitions
- Working with flexbox layouts
- Applying colors, spacing, borders
- Using design tokens

### Debugging Issues

Claude loads `references/troubleshooting.md` when:
- Debugging layout problems
- Working with page wrapping
- Creating navigation (links, bookmarks)
- Optimizing performance

## Common Workflows

### Component Creation Pattern

1. Create file in `src/pages/resume/ComponentName.tsx`
2. Import React-PDF components and design tokens
3. Define TypeScript interface with `ResumeSchema`
4. Create StyleSheet with design token usage
5. Implement component with proper data access
6. Add to main document in appropriate column
7. Test with `bun run dev` and debug mode

### Debugging Workflow

1. Enable debug mode on components
2. Check flexbox properties and alignment
3. Verify width constraints and column behavior
4. Test with minimal content to isolate issues
5. Reference `references/troubleshooting.md` for advanced debugging

## Development Commands

```bash
# Development with hot reload
bun run dev

# Generate PDF file (outputs to tmp/resume.pdf)
bun run save-to-pdf

# Data conversion (runs automatically in other commands)
bun run generate-data
```

## Architecture Integration

### Directory Structure

```
src/pages/
├── design-tokens.ts          # Centralized design system
├── fonts-register.ts          # Font registration
├── index.tsx                  # Component export barrel
└── resume/                    # Resume-specific components
    ├── index.tsx              # Main resume document
    ├── Header.tsx             # Name, title, summary, profile image
    ├── Contact.tsx            # Contact information with links
    ├── Skills.tsx             # Technical expertise and soft skills
    ├── Experience.tsx         # Professional experience and projects
    ├── Education.tsx          # Education section
    ├── Languages.tsx          # Language proficiency
    ├── List.tsx               # Generic list utility component
    └── Title.tsx              # Generic title utility component
```

### Data Flow

```
data/resume.yaml → generate-data.ts → src/data/resume.ts → React components → PDF output
```

### Component Hierarchy

```tsx
<Document>
  <Page style={styles.page}>
    <Header resume={data} />
    <View style={styles.container}>
      <View style={styles.leftColumn}>
        <Contact resume={data} />
        <Skills resume={data} />
        <Languages resume={data} />
      </View>
      <View style={styles.rightColumn}>
        <Experience resume={data} />
        <Education resume={data} />
      </View>
    </View>
  </Page>
</Document>
```

## Best Practices

### Design System Integration

```tsx
// ✅ Good - uses design tokens
import { colors, spacing, typography } from '../design-tokens';

marginBottom: spacing.pagePadding / 2,
color: colors.primary,
fontFamily: 'Lato Bold',

// ❌ Bad - hardcoded values
marginBottom: 9,
color: '#18181b',
fontFamily: 'Arial',
```

### StyleSheet Performance

```tsx
// ✅ Good - StyleSheet.create()
const styles = StyleSheet.create({
  container: { marginBottom: spacing.pagePadding / 2 }
});

// ❌ Bad - Inline styles (slower)
<View style={{ marginBottom: 9 }} />
```

### Type Safety

```tsx
// ✅ Good - Typed props
const ComponentName = ({ resume }: { resume: ResumeSchema }) => {
  const { contact, professional_experience } = resume;
  return <View>{/* Use with type safety */}</View>;
};

// ❌ Bad - Untyped props
const ComponentName = ({ resume }: { resume: any }) => { ... }
```

## Anti-Patterns to Avoid

- **Hardcoded Values**: Always use design tokens
- **Inline Styles**: Use StyleSheet.create() for performance
- **Wrong Font Names**: Must match registration exactly
- **Unsupported CSS**: Check valid properties in references
- **No Type Safety**: Always use ResumeSchema interface
- **Deep Nesting**: Keep component hierarchies flat (≤3 levels)

## Maintenance

### Adding New Guidance

1. Identify appropriate reference file
2. Add content following existing structure
3. Update SKILL.md quick reference if needed
4. Test skill activation

### Updating References

1. Modify content in `references/` directory
2. Ensure consistency with existing patterns
3. Test with actual component creation
4. Verify token efficiency maintained

### Version Control

Track skill evolution in git:
```bash
git log -- .claude/skills/react-pdf-templates/
```

## Related Documentation

- **Project CLAUDE.md**: Links to this skill for PDF development
- **Design Tokens**: `src/pages/design-tokens.ts` (source of truth)
- **Original Reference**: `rpdf/` directory (to be archived)

## Support

For issues or improvements to this skill:
1. Test changes in isolated environment
2. Verify skill activation works correctly
3. Ensure token efficiency maintained (92% savings target)
4. Update documentation as needed
