# Troubleshooting & Advanced Features

Page wrapping, navigation, dynamic content, debugging, and common issues.

## Page Wrapping

React-PDF automatically creates new pages when content exceeds page limits.

### Enable/Disable Wrapping

**Page Level**:
```tsx
<Page wrap={false}>
  {/* Content won't wrap to new pages */}
</Page>
```

**Component Level**:
```tsx
<View wrap={false}>
  {/* This view won't break across pages */}
</View>
```

### Breakable vs Unbreakable

**Breakable** (default for View, Text, Link):
- Fills remaining space before new page
- Content splits across pages

**Unbreakable** (default for Image):
- Moves entirely to next page if insufficient space
- Never splits across pages

**Make Component Unbreakable**:
```tsx
<View wrap={false}>
  {/* This entire view moves to next page if needed */}
</View>
```

### Force Page Breaks

```tsx
<Text break>
  This text starts on a new page
</Text>

<View break>
  This entire view starts on a new page
</View>
```

### Fixed Elements

Render on all pages (headers/footers):

```tsx
<View fixed style={styles.header}>
  <Text>Document Header - Appears on every page</Text>
</View>

<View fixed style={styles.footer}>
  <Text render={({ pageNumber, totalPages }) =>
    `Page ${pageNumber} of ${totalPages}`
  } />
</View>
```

### Orphan & Widow Protection

Prevent single lines at page boundaries:

| Prop | Description | Default |
|------|-------------|---------|
| orphans | Min lines at bottom of page | 2 |
| widows | Min lines at top of page | 2 |
| minPresenceAhead | Min points before wrapping | 0 |

**Example**:
```tsx
<Text orphans={3} widows={3}>
  Long paragraph that should keep at least 3 lines together
  at page boundaries to avoid orphans and widows.
</Text>

<View minPresenceAhead={50}>
  {/* Won't wrap if less than 50pt space ahead */}
</View>
```

---

## Navigation

### Destinations (Internal Links)

Create clickable links to sections within the document:

```tsx
// Link to destination
<Link src="#section1" style={styles.link}>
  Go to Section 1
</Link>

// Destination target
<Text id="section1">
  Section 1 Content - You are here!
</Text>
```

**Any component** can be a destination using the `id` prop.

### Bookmarks (Table of Contents)

Add navigable outline for PDF readers:

**Simple Bookmark**:
```tsx
<Page bookmark="Chapter 1">
  Chapter 1 Content
</Page>
```

**Advanced Bookmark**:
```tsx
<Page bookmark={{
  title: "Chapter 1: Introduction",
  fit: true,              // Zoom to fit page
  expanded: true,         // Expand bookmark tree
  top: 0,                 // Scroll position (top)
  left: 0,                // Scroll position (left)
  zoom: 1.0,              // Zoom level
}}>
  Chapter Content
</Page>
```

**Nested Bookmarks**:
```tsx
<Page bookmark="Part 1">
  <View bookmark="Chapter 1">
    <Text bookmark="Section 1.1">
      Deeply nested content
    </Text>
  </View>
</Page>
```

**Bookmark Type**:
```tsx
type Bookmark = {
  title: string;      // Bookmark text
  fit?: boolean;      // Zoom to fit
  expanded?: boolean; // Expand children
  top?: number;       // Vertical scroll
  left?: number;      // Horizontal scroll
  zoom?: number;      // Zoom level
}
```

---

## Dynamic Content

Render content based on page context:

### Page Numbers

```tsx
<Text
  render={({ pageNumber, totalPages }) =>
    `Page ${pageNumber} of ${totalPages}`
  }
  fixed
/>
```

### Conditional Rendering

```tsx
<View
  render={({ pageNumber }) =>
    pageNumber % 2 === 0
      ? <Text>Even Page Header</Text>
      : <Text>Odd Page Header</Text>
  }
  fixed
/>

<Text
  render={({ pageNumber, totalPages }) =>
    pageNumber === totalPages
      ? "End of Document"
      : "Continued..."
  }
/>
```

### Available Context

| Property | Description |
|----------|-------------|
| pageNumber | Current page number (1-indexed) |
| totalPages | Total number of pages |
| subPageNumber | Sub-page number (wrapped pages) |
| subPageTotalPages | Total sub-pages |

**Example - Chapter Markers**:
```tsx
<Text
  render={({ pageNumber }) => {
    if (pageNumber === 1) return "Introduction";
    if (pageNumber <= 5) return "Chapter 1";
    if (pageNumber <= 10) return "Chapter 2";
    return "Appendix";
  }}
  fixed
  style={styles.chapterMarker}
/>
```

---

## Debugging

### Debug Mode

Enable visual debugging with red bounding boxes:

```tsx
<Page debug={true}>
  <View debug={true}>
    <Text debug={true}>
      Content with visible boundaries
    </Text>
  </View>
</Page>
```

**What to Check**:
1. **Layout boundaries**: See exact component dimensions
2. **Overlap detection**: Identify overlapping elements
3. **Flex layout**: Verify flex container behavior
4. **Positioning**: Check absolute/relative positioning

### Common Layout Issues

**Components Not Rendering**:
```tsx
// Check data availability
console.log('Resume data:', resume);

// Verify component structure
<View style={styles.container} debug={true}>
  <Text>Test content</Text>
</View>

// Check data iteration
{resume.skills && resume.skills.map((skill, index) =>
  <Text key={index}>{skill}</Text>
)}
```

**Overlapping Elements**:
```tsx
// Enable debug mode to see boundaries
<View debug={true}>
  <Image debug={true} />
  <Text debug={true} />
</View>

// Check z-index and positioning
position: 'absolute'
zIndex: 1
```

**Text Overflow**:
```tsx
// Use ellipsis for long text
textOverflow: 'ellipsis'
maxLines: 2
width: '100%'

// Or enable wrapping
wrap: true
```

---

## On-the-Fly Rendering (Web Only)

### PDFDownloadLink

Generate and download PDFs without displaying:

```tsx
import { PDFDownloadLink } from '@react-pdf/renderer';

<PDFDownloadLink
  document={<MyDocument />}
  fileName="resume.pdf"
>
  {({ blob, url, loading, error }) =>
    loading ? 'Loading document...' : 'Download PDF'
  }
</PDFDownloadLink>
```

### BlobProvider

Access blob data without download:

```tsx
import { BlobProvider } from '@react-pdf/renderer';

<BlobProvider document={<MyDocument />}>
  {({ blob, url, loading, error }) => {
    if (loading) return 'Generating PDF...';
    if (error) return `Error: ${error.message}`;

    // Use blob or url
    return <a href={url} download="file.pdf">Download</a>;
  }}
</BlobProvider>
```

### Imperative API

```tsx
import { pdf } from '@react-pdf/renderer';

// Get blob
const blob = await pdf(<MyDocument />).toBlob();

// Get buffer (Node.js)
const buffer = await pdf(<MyDocument />).toBuffer();

// Get stream (Node.js)
const stream = await pdf(<MyDocument />).toStream();
```

### usePDF Hook

```tsx
import { usePDF } from '@react-pdf/renderer';

function MyComponent() {
  const [instance, updateInstance] = usePDF({
    document: <MyDocument />
  });

  // instance.url - PDF URL
  // instance.blob - PDF Blob
  // instance.loading - Loading state
  // instance.error - Error state

  // Update document
  updateInstance(<UpdatedDocument />);
}
```

---

## Performance Optimization

### StyleSheet Performance

```tsx
// ✅ Good - Use StyleSheet.create()
const styles = StyleSheet.create({
  container: { margin: 10 }
});

// ❌ Bad - Inline styles (slower)
<View style={{ margin: 10 }} />
```

### Component Memoization

```tsx
import React from 'react';

const MemoizedComponent = React.memo(({ data }) => (
  <View>
    {/* Expensive render */}
  </View>
));
```

### Image Optimization

```tsx
// Enable caching
<Image src="url" cache={true} />

// Optimize size
<Image
  src="url"
  style={{ width: 100, height: 100 }}
/>
```

### Minimize Nesting

```tsx
// ✅ Good - Flat structure
<View>
  <Text>Content</Text>
</View>

// ❌ Bad - Deep nesting
<View>
  <View>
    <View>
      <Text>Content</Text>
    </View>
  </View>
</View>
```

---

## Common Issues & Solutions

### Font Loading Issues

**Problem**: Custom fonts not appearing

**Solutions**:
```tsx
// 1. Verify font registration
Font.register({
  family: 'Lato',
  src: 'valid-url',
});

// 2. Check exact name match
fontFamily: 'Lato'  // Must match registration

// 3. Test with built-in font first
fontFamily: 'Helvetica'  // Fallback
```

### Image Not Displaying

**Problem**: Image component empty

**Solutions**:
```tsx
// 1. Check source format
src: 'https://example.com/image.jpg'  // Valid URL
src: { uri: 'url' }  // URL object

// 2. Verify dimensions
style={{ width: 100, height: 100 }}

// 3. Check network access
// Ensure URL is accessible

// 4. Try base64
src: 'data:image/png;base64,...'
```

### Page Not Breaking

**Problem**: Content overflows without new page

**Solutions**:
```tsx
// 1. Enable wrapping
<Page wrap={true}>

// 2. Check component wrap prop
<View wrap={true}>

// 3. Force break
<Text break>New page content</Text>
```

### Styling Not Applied

**Problem**: Styles don't render

**Solutions**:
```tsx
// 1. Check property name
fontSize: 12  // ✅
font-size: 12  // ❌ Wrong format

// 2. Verify value format
padding: 10  // ✅ Number
padding: '10px'  // ❌ String with 'px'

// 3. Use StyleSheet
const styles = StyleSheet.create({
  text: { fontSize: 12 }
});

// 4. Check supported properties
// Some CSS properties aren't supported
// See styling-patterns.md for valid list
```

### Layout Breaks on Wrap

**Problem**: Layout corrupts across pages

**Solutions**:
```tsx
// 1. Disable wrapping for layout containers
<View wrap={false}>
  {/* Two-column layout */}
</View>

// 2. Use minPresenceAhead
<View minPresenceAhead={100}>
  {/* Needs 100pt space */}
</View>

// 3. Adjust orphan/widow protection
<Text orphans={3} widows={3}>
  {/* Paragraph text */}
</Text>
```

---

## Development vs Production

### Development (PDFViewer)

```tsx
// web_layout.tsx
import { PDFViewer } from '@react-pdf/renderer';

<PDFViewer width="100%" height="600px">
  <Document>
    <Page>{/* content */}</Page>
  </Document>
</PDFViewer>
```

**Advantages**:
- Hot reload
- Fast iteration
- Browser DevTools
- Real-time preview

### Production (File Generation)

```tsx
// generate-pdf.ts
import { pdf } from '@react-pdf/renderer';
import fs from 'fs';

const doc = <Document><Page>...</Page></Document>;
const buffer = await pdf(doc).toBuffer();
fs.writeFileSync('output.pdf', buffer);
```

**Command**: `bun run save-to-pdf`

**Advantages**:
- Actual file output
- Production accuracy
- File system integration

---

## Best Practices

### Testing Workflow

1. **Start with PDFViewer**: Rapid development with hot reload
2. **Enable debug mode**: Visual layout verification
3. **Test with real data**: Avoid synthetic examples
4. **Generate actual PDF**: Final validation
5. **Test on multiple readers**: Adobe, Preview, Chrome

### Error Prevention

1. **Type safety**: Use TypeScript interfaces
2. **Data validation**: Check data before mapping
3. **Graceful degradation**: Handle missing data
4. **Debug incrementally**: Build in small steps

### Performance

1. **Profile renders**: Identify slow components
2. **Optimize images**: Compress and resize
3. **Use memoization**: Cache expensive operations
4. **Minimize complexity**: Keep component trees simple
