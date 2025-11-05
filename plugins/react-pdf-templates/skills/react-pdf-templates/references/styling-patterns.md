# Styling Patterns

CSS properties, StyleSheet API, and layout techniques for React-PDF.

## StyleSheet API

React-PDF uses StyleSheet for performance-optimized styling.

### StyleSheet.create()

Create reusable style definitions:

```tsx
import { StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: { backgroundColor: 'white' },
  section: { margin: 10, padding: 10 },
  text: { fontSize: 12, fontFamily: 'Helvetica' }
});

// Usage
<Page style={styles.page}>
  <View style={styles.section}>
    <Text style={styles.text}>Content</Text>
  </View>
</Page>
```

### Inline Styling

Plain objects work without StyleSheet.create():

```tsx
<View style={{ margin: 10, padding: 10 }}>
  <Text style={{ fontSize: 12 }}>Content</Text>
</View>
```

**Note**: StyleSheet.create() is preferred for performance.

### Style Arrays

Combine multiple styles (later styles override earlier):

```tsx
const styles = StyleSheet.create({
  base: { fontSize: 12, color: 'black' },
  emphasis: { fontFamily: 'Lato Bold' }
});

<Text style={[styles.base, styles.emphasis]}>
  Bold text
</Text>

// Conditional styling
<Text style={[styles.base, isImportant && styles.emphasis]}>
  Content
</Text>
```

---

## Valid Units

| Unit | Description | Example |
|------|-------------|---------|
| pt | Points (default, 72 dpi) | `12pt` or `12` |
| in | Inches | `1in` |
| mm | Millimeters | `25.4mm` |
| cm | Centimeters | `2.54cm` |
| % | Percentage | `50%` |
| vw | Viewport width | `100vw` |
| vh | Viewport height | `100vh` |

**Default**: Numbers without units are treated as points (pt).

---

## Flexbox Layout

React-PDF uses Flexbox for layout (similar to CSS Flexbox).

### Flex Container Properties

```tsx
flexDirection: 'row' | 'row-reverse' | 'column' | 'column-reverse'
flexWrap: 'nowrap' | 'wrap' | 'wrap-reverse'
flexFlow: 'row wrap'  // Shorthand

justifyContent: 'flex-start' | 'flex-end' | 'center' | 'space-between' | 'space-around' | 'space-evenly'
alignItems: 'flex-start' | 'flex-end' | 'center' | 'stretch' | 'baseline'
alignContent: 'flex-start' | 'flex-end' | 'center' | 'stretch' | 'space-between' | 'space-around'

gap: 10            // Gap between items
rowGap: 10         // Gap between rows
columnGap: 10      // Gap between columns
```

### Flex Item Properties

```tsx
flex: 1                    // Grow and shrink
flexGrow: 1                // Grow factor
flexShrink: 1              // Shrink factor
flexBasis: 'auto' | 100    // Initial size
alignSelf: 'auto' | 'flex-start' | 'flex-end' | 'center' | 'baseline' | 'stretch'
```

### Common Layouts

**Two-Column Layout**:
```tsx
const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
  },
  leftColumn: {
    width: 180,          // Fixed width
    paddingRight: 18,
  },
  rightColumn: {
    flex: 1,             // Flexible width
    paddingLeft: 18,
  }
});
```

**Centered Content**:
```tsx
const styles = StyleSheet.create({
  container: {
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100%',
  }
});
```

**Space Between**:
```tsx
const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  }
});
```

---

## Dimension Properties

```tsx
width: 100 | '50%' | 'auto'
height: 100 | '50%' | 'auto'
minWidth: 100
maxWidth: 500
minHeight: 100
maxHeight: 500
```

---

## Position Properties

```tsx
position: 'relative' | 'absolute'
top: 10
right: 10
bottom: 10
left: 10
zIndex: 1
```

**Absolute Positioning Example**:
```tsx
const styles = StyleSheet.create({
  container: {
    position: 'relative',
    width: 200,
    height: 100,
  },
  overlay: {
    position: 'absolute',
    top: 10,
    right: 10,
  }
});
```

---

## Margin & Padding

```tsx
// All sides
margin: 10
padding: 10

// Directional
marginTop: 10
marginRight: 10
marginBottom: 10
marginLeft: 10
paddingTop: 10
paddingRight: 10
paddingBottom: 10
paddingLeft: 10

// Horizontal/Vertical
marginHorizontal: 10   // Left + Right
marginVertical: 10     // Top + Bottom
paddingHorizontal: 10
paddingVertical: 10
```

---

## Color Properties

```tsx
color: '#000000'             // Text color
backgroundColor: '#FFFFFF'   // Background color
opacity: 0.5                 // Transparency (0-1)
```

**Color Formats**:
- Hex: `#FF0000`, `#F00`
- RGB: `rgb(255, 0, 0)`
- RGBA: `rgba(255, 0, 0, 0.5)`
- Named: `red`, `blue`, `transparent`

---

## Text Properties

```tsx
// Font
fontSize: 12
fontFamily: 'Helvetica'
fontStyle: 'normal' | 'italic' | 'oblique'
fontWeight: 'normal' | 'bold' | 100-900

// Spacing
letterSpacing: 1
lineHeight: 1.5

// Alignment
textAlign: 'left' | 'right' | 'center' | 'justify'
textIndent: 10

// Decoration
textDecoration: 'none' | 'underline' | 'line-through' | 'underline line-through'
textDecorationColor: '#000000'
textDecorationStyle: 'solid' | 'double' | 'dotted' | 'dashed'

// Transform
textTransform: 'none' | 'capitalize' | 'uppercase' | 'lowercase'

// Overflow
textOverflow: 'clip' | 'ellipsis'
maxLines: 3
```

---

## Border Properties

```tsx
// All sides
border: '1px solid #000000'
borderWidth: 1
borderStyle: 'solid' | 'dashed' | 'dotted'
borderColor: '#000000'

// Per-side
borderTop: '1px solid #000000'
borderTopWidth: 1
borderTopStyle: 'solid'
borderTopColor: '#000000'
// (same for Right, Bottom, Left)

// Radius
borderTopLeftRadius: 5
borderTopRightRadius: 5
borderBottomRightRadius: 5
borderBottomLeftRadius: 5
```

**Common Border Patterns**:
```tsx
// Separator line
borderBottom: `1px solid ${colors.separatorGray}`

// Card border
border: '1px solid #E5E7EB'
borderRadius: 8

// Bottom border only
borderBottomWidth: 1
borderBottomColor: colors.mediumGray
borderBottomStyle: 'solid'
```

---

## Transform Properties

```tsx
transform: 'rotate(45deg)'
transform: 'scale(1.5)'
transform: 'scaleX(2) scaleY(0.5)'
transform: 'translate(10, 20)'
transform: 'translateX(10)'
transform: 'translateY(20)'
transform: 'skew(10deg, 5deg)'
transform: 'skewX(10deg)'
transform: 'skewY(10deg)'
transform: 'matrix(1, 0, 0, 1, 0, 0)'

transformOrigin: 'center' | 'top left' | '50% 50%'
```

---

## Image Sizing/Positioning

```tsx
objectFit: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
objectPosition: 'center' | 'top' | '50% 50%'
```

**Examples**:
```tsx
// Cover image
objectFit: 'cover'
objectPosition: 'center'

// Contain with aspect ratio
objectFit: 'contain'
```

---

## Other Properties

```tsx
display: 'flex' | 'none'
overflow: 'visible' | 'hidden'
```

---

## Media Queries

Apply styles based on page dimensions or orientation:

```tsx
const styles = StyleSheet.create({
  section: {
    width: 200,
    '@media max-width: 400': {
      width: 300,
    },
    '@media min-width: 600': {
      width: 400,
    },
    '@media orientation: landscape': {
      width: 500,
    },
  }
});
```

**Supported Queries**:
- `@media max-width: 400`
- `@media min-width: 600`
- `@media max-height: 800`
- `@media min-height: 400`
- `@media orientation: portrait`
- `@media orientation: landscape`

---

## Design Token Integration

This project uses centralized design tokens in `src/pages/design-tokens.ts`:

### Colors

```tsx
import { colors } from '../design-tokens';

color: colors.primary           // zinc-900
color: colors.accent            // rose-600
color: colors.darkGray          // zinc-800
color: colors.mediumGray        // zinc-600
borderColor: colors.separatorGray  // zinc-400
```

### Typography

```tsx
import { typography } from '../design-tokens';

// Body text
fontSize: typography.text.size
fontFamily: typography.text.fontFamily
lineHeight: typography.text.lineHeight

// Titles
fontSize: typography.title.fontSize
fontFamily: typography.title.fontFamily
textTransform: typography.title.textTransform

// Subtitles
fontSize: typography.subtitle.fontSize
fontFamily: typography.subtitle.fontFamily
```

### Spacing

```tsx
import { spacing } from '../design-tokens';

width: spacing.columnWidth           // 180
padding: spacing.documentPadding     // 42
marginBottom: spacing.pagePadding    // 18
marginBottom: spacing.pagePadding / 2   // 9 (derived)
```

---

## Common Styling Patterns

### Section Title

```tsx
const styles = StyleSheet.create({
  sectionTitle: {
    fontFamily: 'Lato Bold',
    fontSize: 12,
    color: colors.primary,
    textTransform: 'uppercase',
    marginBottom: spacing.pagePadding / 3,
  }
});
```

### Body Text

```tsx
const styles = StyleSheet.create({
  bodyText: {
    fontSize: typography.text.size,
    fontFamily: typography.text.fontFamily,
    lineHeight: typography.text.lineHeight,
    color: colors.darkGray,
  }
});
```

### List Item

```tsx
const styles = StyleSheet.create({
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.listItemSpacing,
  },
  bullet: {
    width: 10,
    marginRight: 5,
    color: colors.mediumGray,
  },
  itemText: {
    flex: 1,
    fontSize: typography.text.size,
  }
});
```

### Card/Container

```tsx
const styles = StyleSheet.create({
  card: {
    padding: spacing.pagePadding,
    marginBottom: spacing.pagePadding / 2,
    border: '1px solid #E5E7EB',
    borderRadius: 4,
  }
});
```

---

## Best Practices

### Performance

1. **Use StyleSheet.create()**: Better performance than inline styles
2. **Avoid deep nesting**: Flatten component hierarchies
3. **Minimize style recalculation**: Use static styles when possible

### Maintainability

1. **Design tokens**: Always use centralized design system
2. **Naming conventions**: Descriptive style names (sectionTitle, bodyText)
3. **Grouping**: Group related styles together
4. **Comments**: Document complex layouts

### Layout

1. **Flexbox**: Preferred for all layouts
2. **Absolute positioning**: Use sparingly (overlays, badges)
3. **Fixed widths**: Left column only; flex for right column
4. **Responsive**: Use media queries for different page sizes

---

## Troubleshooting

### Styles Not Applying

**Check**:
1. Property name spelling
2. Value format (string vs number)
3. Supported properties (not all CSS works)
4. Style precedence in arrays

### Layout Issues

**Debug**:
1. Enable debug mode: `debug={true}`
2. Check flexbox properties
3. Verify width/height constraints
4. Inspect parent container

### Text Overflow

**Solutions**:
```tsx
textOverflow: 'ellipsis'
maxLines: 2
width: '100%'
```

### Border Not Showing

**Common Issues**:
```tsx
// Missing color
border: '1px solid'  // ❌ No color
border: '1px solid #000000'  // ✅ With color

// Wrong syntax
borderWidth: 1
borderStyle: 'solid'
borderColor: '#000000'
// Better: border: '1px solid #000000'
```
