# Font Configuration

Typography system and font registration guide for React-PDF.

## Font Registration System

React-PDF provides a `Font` module for loading custom fonts, handling hyphenation, and embedding emoji glyphs.

### Built-in Fonts

Available without registration:

- `Courier`, `Courier-Bold`, `Courier-Oblique`, `Courier-BoldOblique`
- `Helvetica`, `Helvetica-Bold`, `Helvetica-Oblique`, `Helvetica-BoldOblique`
- `Times-Roman`, `Times-Bold`, `Times-Italic`, `Times-BoldItalic`

### Supported Font Formats

- **TTF** (TrueType Font)
- **WOFF** (Web Open Font Format)

**Note**: OTF and other formats are not currently supported.

---

## Font.register()

Register custom fonts for use in your PDF documents.

### Basic Registration

```tsx
import { Font } from '@react-pdf/renderer';

Font.register({
  family: 'FontFamilyName',
  src: 'https://fonts.gstatic.com/path/to/font.ttf',
});
```

### Full Registration Options

```tsx
Font.register({
  family: 'FontFamilyName',        // Required: Name to reference in styles
  src: 'url-or-path',              // Required: Font file source
  fontStyle: 'normal' | 'italic' | 'oblique',  // Optional: Default 'normal'
  fontWeight: 'normal' | number,   // Optional: Default 'normal' (400)
  fonts: [],                       // Optional: Register multiple variants
});
```

---

## Font Parameters

### family

Name to reference the font in style definitions. Can be any unique valid string.

**Example**:
```tsx
Font.register({ family: 'Lato', src: source });

// Reference in styles
const styles = StyleSheet.create({
  text: { fontFamily: 'Lato' }
});
```

### src

Specifies the font source. Can be:
- Valid URL (web fonts)
- Absolute path (Node.js only)

**Examples**:
```tsx
// Google Fonts
src: 'https://fonts.gstatic.com/s/lato/v23/S6uyw4BMUTPHjx4wXg.woff'

// Local file (Node only)
src: '/absolute/path/to/font.ttf'
```

### fontStyle

Specifies the font style variant.

| Value | Description |
|-------|-------------|
| normal | Normal font style (default) |
| italic | Italic variant (must be registered) |
| oblique | Oblique variant (must be registered) |

**Important**: React-PDF will fail if you reference an italic/oblique style that hasn't been registered.

### fontWeight

Specifies the font weight.

| Value | Numeric | Description |
|-------|---------|-------------|
| thin | 100 | Thinnest weight |
| ultralight | 200 | Extra light |
| light | 300 | Light weight |
| normal | 400 | Normal (default) |
| medium | 500 | Medium weight |
| semibold | 600 | Semi-bold |
| bold | 700 | Bold weight |
| ultrabold | 800 | Extra bold |
| heavy | 900 | Heaviest weight |
| _number_ | 0-1000 | Custom weight |

**Fallback Behavior**: When exact weight is unavailable, React-PDF uses the nearest registered weight (similar to browsers).

---

## Multi-Variant Registration

Register multiple font variants at once using the `fonts` array:

```tsx
Font.register({
  family: 'Roboto',
  fonts: [
    { src: source1 },                           // normal, 400
    { src: source2, fontStyle: 'italic' },      // italic, 400
    { src: source3, fontWeight: 700 },          // normal, 700
    { src: source4, fontStyle: 'italic', fontWeight: 700 }, // italic, 700
  ]
});
```

---

## Project Font Configuration

This project uses two font families registered in `src/pages/fonts-register.ts`:

### Lato (Primary)

```tsx
Font.register({ family: 'Lato', src: '...' });              // Regular
Font.register({ family: 'Lato Italic', src: '...' });       // Italic
Font.register({ family: 'Lato Light', src: '...' });        // Light
Font.register({ family: 'Lato semibold', src: '...' });     // Semibold
Font.register({ family: 'Lato Bold', src: '...' });         // Bold
```

**Usage**:
```tsx
fontFamily: 'Lato'           // Body text
fontFamily: 'Lato Bold'      // Headers, emphasis
fontFamily: 'Lato Italic'    // Italicized text
```

### Open Sans (Secondary)

```tsx
Font.register({ family: 'Open Sans', src: '...' });         // Regular
Font.register({ family: 'Open Sans Light', src: '...' });   // Light
Font.register({ family: 'Open Sans Bold', src: '...' });    // Bold
Font.register({ family: 'Open Sans Italic', src: '...' });  // Italic
```

---

## Hyphenation

React-PDF uses the Knuth-Plass algorithm for automatic hyphenation.

### registerHyphenationCallback()

Fine-grained control over word breaking:

```tsx
import { Font } from '@react-pdf/renderer';

Font.registerHyphenationCallback((word) => {
  // Return array of word parts
  return ["hy", "phen", "ation"];
});
```

### Disable Hyphenation

Return the word unchanged:

```tsx
Font.registerHyphenationCallback(word => [word]);
```

### Component-Level Hyphenation

Override at component level:

```tsx
<Text hyphenationCallback={(word) => customHyphenation(word)}>
  Content with custom hyphenation
</Text>
```

---

## Emoji Support

PDF documents don't support color emoji fonts. React-PDF embeds emojis as images.

### registerEmojiSource()

Configure emoji image CDN:

```tsx
import { Font } from '@react-pdf/renderer';

Font.registerEmojiSource({
  format: 'png',
  url: 'https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/',
});
```

**Note**: Requires internet connection at render time to download emoji images.

**Recommended CDN**: [Twemoji](https://github.com/twitter/twemoji) by Twitter

---

## Typography Best Practices

### Font Loading

1. **Register before rendering**: All fonts must be registered before document render
2. **Exact names**: Font family names in styles must match registration exactly
3. **Fallback fonts**: Always have built-in font fallbacks

```tsx
// Good - exact match
fontFamily: 'Lato Bold'

// Bad - will fail
fontFamily: 'Lato-Bold'
```

### Performance

1. **Minimize variants**: Only register fonts you actually use
2. **CDN sources**: Use reliable CDNs for web fonts
3. **Cache fonts**: React-PDF caches registered fonts

### Common Issues

**Font not rendering**:
- Check font family name matches registration
- Verify font file format (TTF/WOFF only)
- Ensure font source is accessible

**Italic/Bold not working**:
- Register the specific variant (italic, bold)
- Don't rely on synthetic styles

**Fallback to built-in**:
- Font registration failed silently
- Check network access for remote fonts
- Verify file path for local fonts

---

## Font Usage Patterns

### Section Headers

```tsx
const styles = StyleSheet.create({
  sectionTitle: {
    fontFamily: 'Lato Bold',
    fontSize: 12,
    textTransform: 'uppercase',
  }
});
```

### Body Text

```tsx
const styles = StyleSheet.create({
  bodyText: {
    fontFamily: 'Lato',
    fontSize: 9,
    lineHeight: 1.33,
  }
});
```

### Emphasis

```tsx
<Text style={styles.paragraph}>
  Regular text <Text style={{ fontFamily: 'Lato Bold' }}>bold text</Text> continues.
</Text>
```

### Mixed Weights

```tsx
<Text>
  <Text style={{ fontWeight: 300 }}>Light</Text>
  <Text style={{ fontWeight: 400 }}>Normal</Text>
  <Text style={{ fontWeight: 700 }}>Bold</Text>
</Text>
```

---

## Google Fonts Integration

Find TTF fonts from Google: [Available TTF Fonts](https://gist.github.com/sadikay/d5457c52e7fb2347077f5b0fe5ba9300)

**Example Integration**:
```tsx
Font.register({
  family: 'Roboto',
  fonts: [
    {
      src: 'https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff',
      fontWeight: 400,
    },
    {
      src: 'https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmWUlfBBc4.woff',
      fontWeight: 700,
    },
  ],
});
```

---

## Troubleshooting

### Font Not Loading

**Check**:
1. Font file format (TTF/WOFF only)
2. Source URL accessibility
3. Network connectivity (for remote fonts)
4. Exact family name match in styles

**Debug**:
```tsx
// Test with built-in font first
fontFamily: 'Helvetica'  // Should always work

// Then switch to custom
fontFamily: 'Lato'
```

### Style Not Applying

**Common Causes**:
- Unregistered font variant (italic, bold)
- Typo in family name
- Weight mismatch

**Solution**:
```tsx
// Register all variants needed
Font.register({
  family: 'MyFont',
  fonts: [
    { src: regular },
    { src: bold, fontWeight: 700 },
    { src: italic, fontStyle: 'italic' },
  ]
});
```

### Performance Issues

**Optimize**:
1. Use font CDNs (Google Fonts, Cloudflare)
2. Register only necessary variants
3. Prefer WOFF over TTF (smaller size)
4. Cache fonts between renders
