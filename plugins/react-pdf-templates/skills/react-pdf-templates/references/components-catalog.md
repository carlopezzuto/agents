# React-PDF Components Catalog

Complete component API reference for @react-pdf/renderer.

## Document

Root component representing the PDF document. Must be the top-level element.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| title | Document metadata title | String | undefined |
| author | Document metadata author | String | undefined |
| subject | Document metadata subject | String | undefined |
| keywords | Document metadata keywords | String | undefined |
| creator | Document metadata creator | String | "react-pdf" |
| producer | Document metadata producer | String | "react-pdf" |
| pdfVersion | PDF version | String | "1.3" |
| language | Default language | String | undefined |
| pageMode | Display mode when opened | PageMode | useNone |
| pageLayout | Page layout mode | PageLayout | singlePage |
| onRender | Callback after render (blob in web) | Function | undefined |

**PageMode Values**: useNone, useOutlines, useThumbs, fullScreen, useOC, useAttachments

**PageLayout Values**: singlePage, oneColumn, twoColumnLeft, twoColumnRight, twoPageLeft, twoPageRight

**Example**:
```tsx
<Document
  title="Professional Resume"
  author="John Doe"
  creator="Universal Job Tailor"
>
  <Page>{/* content */}</Page>
</Document>
```

---

## Page

Represents a single page in the PDF document.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| size | Page size (A4, Letter, [width, height], number) | String/Array/Number/Object | "A4" |
| orientation | Page orientation | "portrait" \| "landscape" | "portrait" |
| wrap | Enable page wrapping | Boolean | true |
| style | Page styles | Object/Array | undefined |
| debug | Debug mode (bounding box) | Boolean | false |
| dpi | Custom DPI | Number | 72 |
| id | Destination ID for internal links | String | undefined |
| bookmark | Attach bookmark | String/Bookmark | undefined |

**Example**:
```tsx
<Page size="A4" orientation="portrait" style={styles.page}>
  {/* content */}
</Page>
```

---

## View

Fundamental container component for building layouts. Supports flexbox.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| wrap | Enable page wrapping | Boolean | true |
| style | View styles | Object/Array | undefined |
| render | Dynamic content based on context | Function | undefined |
| debug | Debug mode | Boolean | false |
| fixed | Render in all wrapped pages | Boolean | false |
| id | Destination ID | String | undefined |
| bookmark | Attach bookmark | String/Bookmark | undefined |

**Two-Column Layout Example**:
```tsx
<View style={styles.container}>
  <View style={styles.leftColumn}>
    <Contact resume={data} />
  </View>
  <View style={styles.rightColumn}>
    <Experience resume={data} />
  </View>
</View>
```

---

## Text

Component for displaying text. Supports nesting for inline styles.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| wrap | Enable page wrapping | Boolean | true |
| render | Dynamic content | Function | undefined |
| style | Text styles | Object/Array | undefined |
| debug | Debug mode | Boolean | false |
| fixed | Render in all pages | Boolean | false |
| hyphenationCallback | Custom hyphenation | Function | undefined |
| id | Destination ID | String | undefined |
| bookmark | Attach bookmark | String/Bookmark | undefined |

**Dynamic Content Example**:
```tsx
<Text
  render={({ pageNumber, totalPages }) => `Page ${pageNumber} of ${totalPages}`}
  fixed
/>
```

**Inline Styling Example**:
```tsx
<Text style={styles.paragraph}>
  This is <Text style={styles.bold}>bold text</Text> inside a paragraph.
</Text>
```

---

## Image

Component for displaying JPG or PNG images (network, local, base64).

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| src | Image source | Source object | undefined |
| source | Alias of src | Source object | undefined |
| style | Image styles | Object/Array | undefined |
| debug | Debug mode | Boolean | false |
| fixed | Render in all pages | Boolean | false |
| cache | Enable caching | Boolean | true |
| bookmark | Attach bookmark | String/Bookmark | undefined |

**Source Object Types**:

| Type | Description | Example |
|------|-------------|---------|
| String | URL or filesystem path | `"www.example.com/image.jpg"` |
| URL object | URL with fetch parameters | `{ uri: "url", method: "GET", headers: {} }` |
| Buffer | Direct buffer | `Buffer` |
| Data buffer | Buffer with format | `{ data: Buffer, format: "png" \| "jpg" }` |
| Function | Returns any above type | `() => String \| Promise<String>` |

**Example**:
```tsx
<Image
  src="https://example.com/profile.jpg"
  style={{ width: 46, height: 46 }}
/>
```

---

## Link

Component for external links or internal navigation.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| src | URL or destination ID (prefix with #) | String | undefined |
| wrap | Enable page wrapping | Boolean | true |
| style | Link styles | Object/Array | undefined |
| debug | Debug mode | Boolean | false |
| fixed | Render in all pages | Boolean | false |
| bookmark | Attach bookmark | String/Bookmark | undefined |

**External Link Example**:
```tsx
<Link src="https://linkedin.com/in/profile" style={styles.link}>
  LinkedIn Profile
</Link>
```

**Email Link Example**:
```tsx
<Link src="mailto:email@example.com" style={styles.email}>
  email@example.com
</Link>
```

**Internal Navigation Example**:
```tsx
<Link src="#section1" style={styles.internalLink}>
  Go to Section 1
</Link>

<Text id="section1">Section 1 Content</Text>
```

---

## Canvas

Component for free-form drawing using painter API.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| style | Canvas styles (width/height required) | Object/Array | undefined |
| paint | Painter function | Function | undefined |
| debug | Debug mode | Boolean | false |
| fixed | Render in all pages | Boolean | false |
| bookmark | Attach bookmark | String/Bookmark | undefined |

**Painter Function Signature**:
```tsx
(
  painter: PainterObject,
  availableWidth: number,
  availableHeight: number
) => void
```

**Painter Methods**: dash, clip, save, path, fill, font, text, rect, scale, moveTo, lineTo, stroke, rotate, circle, lineCap, opacity, ellipse, polygon, restore, lineJoin, fontSize, fillColor, lineWidth, translate, miterLimit, strokeColor, fillOpacity, roundedRect, strokeOpacity, bezierCurveTo, quadraticCurveTo, linearGradient, radialGradient

**Example**:
```tsx
<Canvas
  style={{ width: 200, height: 100 }}
  paint={(painter, width, height) => {
    painter
      .rect(0, 0, width, height)
      .fillColor('blue')
      .fill();
  }}
/>
```

---

## Note

Component for displaying annotation notes in the document.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| style | Note styles | Object/Array | undefined |
| children | Note content | String | undefined |
| fixed | Render in all pages | Boolean | false |

---

## Web-Only Components

### PDFViewer

Iframe PDF viewer for client-side generated documents.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| style | Iframe styles | Object/Array | undefined |
| className | Iframe class | String | undefined |
| children | Document implementation | Document | undefined |
| width | Iframe width | String/Number | undefined |
| height | Iframe height | String/Number | undefined |
| showToolbar | Show toolbar (Chrome/Edge/Safari) | Boolean | true |

**Example**:
```tsx
<PDFViewer width="100%" height="600px">
  <Document>
    <Page>{/* content */}</Page>
  </Document>
</PDFViewer>
```

### PDFDownloadLink

Anchor tag for on-the-fly PDF download.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| document | Document implementation | Document | undefined |
| fileName | Download filename | String | undefined |
| style | Anchor styles | Object/Array | undefined |
| className | Anchor class | String | undefined |
| children | Anchor content | DOM node/Function | undefined |

**Example**:
```tsx
<PDFDownloadLink document={<MyDoc />} fileName="resume.pdf">
  {({ loading }) => loading ? 'Loading...' : 'Download PDF'}
</PDFDownloadLink>
```

### BlobProvider

Declarative way to get document blob without displaying.

**Valid Props**:

| Prop | Description | Type | Default |
|------|-------------|------|---------|
| document | Document implementation | Document | undefined |
| children | Render prop | Function | undefined |

**Example**:
```tsx
<BlobProvider document={<MyDoc />}>
  {({ blob, url, loading, error }) => {
    // Use blob, url, handle loading/error
  }}
</BlobProvider>
```

---

## Common Patterns

### Header with Profile Image

```tsx
<View style={styles.headerContainer}>
  <View style={styles.profileArea}>
    <Image src={profileUrl} style={styles.profileImage} />
  </View>
  <View style={styles.contentArea}>
    <Text style={styles.name}>{name}</Text>
    <Text style={styles.title}>{title}</Text>
  </View>
</View>
```

### List with Bullets

```tsx
{items.map((item, index) => (
  <View key={index} style={styles.listItem}>
    <Text style={styles.bullet}>•</Text>
    <Text style={styles.itemText}>{item}</Text>
  </View>
))}
```

### Fixed Header/Footer

```tsx
<View style={styles.header} fixed>
  <Text>Document Header</Text>
</View>

<View style={styles.footer} fixed>
  <Text render={({ pageNumber }) => `Page ${pageNumber}`} />
</View>
```

### Conditional Rendering

```tsx
{company_description && (
  <Text style={styles.description}>
    {company_description}
  </Text>
)}
```
