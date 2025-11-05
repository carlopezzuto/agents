---
name: react-pdf-templates
description: React-PDF component library, font configuration, and styling patterns for professional PDF document generation. Use when creating or modifying PDF templates, debugging layout issues, or working with resume/cover letter components.
---

# React-PDF Templates

Comprehensive guide for creating professional PDF documents using @react-pdf/renderer in this resume generator project.

## Quick Reference

### Core Components

- **Document**: Root component, required wrapper for all PDFs
- **Page**: Single page (size: "A4", orientation: "portrait"|"landscape")
- **View**: Container component (supports flexbox layout)
- **Text**: Text content (supports nesting for inline styles)
- **Image**: JPG/PNG images (network, local, base64)
- **Link**: External links or internal navigation (`src="#id"`)
- **Canvas**: Free-form drawing with painter API

### Font System

**Available Fonts**:
- `Lato` family: Regular, Italic, Light, Semibold, Bold (primary)
- `Open Sans` family: Regular, Light, Bold, Italic
- Built-in: Helvetica, Courier, Times-Roman

**Registration Pattern**:
```tsx
Font.register({
  family: 'Lato Bold',
  src: 'https://fonts.gstatic.com/...',
});
```

### Design Tokens

**Colors** (Tailwind-based):
- `colors.primary` - Main text (zinc-900)
- `colors.accent` - Highlights/links (rose-600)
- `colors.darkGray` - Content text (zinc-800)
- `colors.mediumGray` - Secondary text (zinc-600)

**Typography**:
- `typography.text` - Body: 9px, Lato, lineHeight 1.33
- `typography.title` - Main: 22px, Lato Bold, uppercase
- `typography.subtitle` - Section: 14px, Lato Bold

**Spacing**:
- `spacing.columnWidth` - Left column: 180
- `spacing.documentPadding` - Document: 42
- `spacing.pagePadding` - Section: 18

### StyleSheet Patterns

```tsx
import { StyleSheet } from '@react-pdf/renderer';
import { colors, spacing, typography } from '../design-tokens';

const styles = StyleSheet.create({
  section: {
    marginBottom: spacing.pagePadding / 2,
  },
  sectionTitle: {
    fontFamily: 'Lato Bold',
    fontSize: 12,
    color: colors.primary,
    marginBottom: spacing.pagePadding / 3,
  },
  bodyText: {
    fontSize: typography.text.size,
    fontFamily: typography.text.fontFamily,
    lineHeight: typography.text.lineHeight,
    color: colors.darkGray,
  },
});
```

## Critical Requirements

### 1. Design System Integration

**Always use design tokens** instead of hardcoded values:

```tsx
// ✅ Good - uses design tokens
marginBottom: spacing.pagePadding / 2,
color: colors.primary,
fontFamily: 'Lato Bold',

// ❌ Bad - hardcoded values
marginBottom: 9,
color: '#18181b',
fontFamily: 'Arial',
```

### 2. Component Structure

**Standard Pattern**:
```tsx
import React from 'react';
import { Text, View, StyleSheet } from '@react-pdf/renderer';
import { colors, spacing, typography } from '../design-tokens';
import type { ResumeSchema } from '../../types';

const styles = StyleSheet.create({
  container: { marginBottom: spacing.pagePadding / 2 },
});

const ComponentName = ({ resume }: { resume: ResumeSchema }) => (
  <View style={styles.container}>
    <Text style={styles.sectionTitle}>Section Title</Text>
  </View>
);

export default ComponentName;
```

### 3. Type Safety

All components receive typed data through `ResumeSchema`:

```tsx
const ComponentName = ({ resume }: { resume: ResumeSchema }) => {
  const { contact, professional_experience, skills } = resume;
  return <View>{/* Use data with type safety */}</View>;
};
```

### 4. Performance

- **StyleSheet.create()** instead of inline styles (performance)
- **Memo** for repeated components
- **Optimize** image sizes and formats

## Common Workflows

### Creating New Component

1. Create file in `src/pages/resume/ComponentName.tsx`
2. Import React-PDF components and design tokens
3. Define TypeScript interface with `ResumeSchema`
4. Create StyleSheet with design token usage
5. Implement component with proper data access
6. Add to main document in appropriate column
7. Test with `bun run dev` and debug mode

### Modifying Existing Components

1. Use design tokens for any new styling
2. Follow existing patterns in the component
3. Test with debug mode: `<View debug={true}>`
4. Verify two-column layout doesn't break
5. Check both PDFViewer and file output

### Debugging Layout Issues

1. Enable debug mode: `debug={true}` on components
2. Check flexbox properties and alignment
3. Verify width constraints (leftColumn: 180, rightColumn: flex 1)
4. Reference: `references/troubleshooting.md`

## Development Commands

```bash
# Development with hot reload
bun run dev

# Generate PDF file
bun run save-to-pdf

# Data conversion
bun run generate-data
```

## When to Reference

Load specific reference files based on task:

| Task | Reference File |
|------|---------------|
| Component API details | `references/components-catalog.md` |
| Font registration | `references/font-configuration.md` |
| Styling and CSS | `references/styling-patterns.md` |
| Page breaks, navigation | `references/troubleshooting.md` |

## Quick Wins

### Component Best Practices

- **Functions**: Keep components focused, ≤50 lines
- **Files**: ≤600 lines (extract modules if larger)
- **Nesting**: ≤3 levels (use early returns)
- **Props**: ≤10 props per component
- **Magic Values**: Use design tokens or constants

### Layout Patterns

**Two-Column**:
```tsx
flexDirection: 'row',
leftColumn: {
  width: spacing.columnWidth,
  paddingRight: spacing.pagePadding,
},
rightColumn: {
  flex: 1,
  paddingLeft: spacing.pagePadding,
},
```

**List Items**:
```tsx
flexDirection: 'row',
alignItems: 'flex-start',
marginBottom: spacing.listItemSpacing,
```

## Anti-Patterns to Avoid

**❌ Hardcoded Values**: Always use design tokens
**❌ Inline Styles**: Use StyleSheet.create() for performance
**❌ Wrong Font Names**: Must match registration exactly
**❌ Unsupported CSS**: Check valid properties in `references/styling-patterns.md`
**❌ No Type Safety**: Always use ResumeSchema interface

## Architecture

### Directory Structure

```
src/pages/
├── design-tokens.ts          # Centralized design system
├── fonts-register.ts          # Font registration
└── resume/                    # Resume components
    ├── index.tsx              # Main document
    ├── Header.tsx             # Name, title, summary
    ├── Contact.tsx            # Contact info with links
    ├── Skills.tsx             # Technical/soft skills
    ├── Experience.tsx         # Professional experience
    ├── Education.tsx          # Education section
    └── Languages.tsx          # Language proficiency
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

## Tools Configuration

- **Bun**: Fast JavaScript runtime and bundler
- **TypeScript**: Strict mode enabled
- **@react-pdf/renderer**: PDF generation engine
- **Design Tokens**: Centralized styling system

## Getting Help

For detailed guidance on specific topics, read the appropriate reference file:

- **Component API and props** → `references/components-catalog.md`
- **Font registration and typography** → `references/font-configuration.md`
- **CSS properties and styling** → `references/styling-patterns.md`
- **Page wrapping, navigation, debugging** → `references/troubleshooting.md`
