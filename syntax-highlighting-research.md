# Syntax Highlighting Libraries Research for Flask File Viewer (2024)

## Executive Summary

Based on comprehensive research of current syntax highlighting libraries, **Prism.js** emerges as the optimal choice for a lightweight Flask file viewer that serves HTML directly. It offers the best balance of performance, bundle size, CDN availability, and ease of integration.

## Detailed Comparison

### 1. Prism.js ⭐ **RECOMMENDED**

**Pros:**
- **Ultra-lightweight**: Core is only 2KB minified & gzipped
- **Modular**: Languages add only 0.3-0.5KB each, themes ~1KB
- **Excellent CDN support**: Available on cdnjs, jsDelivr, and UNPKG
- **297 language support**: Most comprehensive language coverage
- **Easy integration**: Simple HTML markup with `<pre><code class="language-*">` 
- **Autoloader plugin**: Dynamic language loading for optimal performance
- **Modern architecture**: Built with modern web standards
- **Extensive plugin ecosystem**: Line numbers, copy-to-clipboard, etc.

**Cons:**
- No automatic language detection (requires manual class specification)
- Slightly more complex setup for dynamic language loading

**Bundle Size:**
- Core: 2KB gzipped
- Per language: 0.3-0.5KB
- Themes: ~1KB each

### 2. Highlight.js

**Pros:**
- **Automatic language detection**: No need to specify language classes
- **192 language support**: Extensive language coverage
- **Zero dependencies**: Standalone operation
- **Good CDN support**: Available on major CDNs
- **Popular**: 12.9M weekly npm downloads

**Cons:**
- **Large bundle size**: ~2.5MB for full language support, ~539KB for common bundle
- **Performance impact**: Can be 40-60% of total bundle size
- **Less granular control**: Harder to optimize for specific languages

**Bundle Size:**
- Common languages (CDN): ~188KB gzipped (~539KB parsed)
- Full language support: ~2.5MB
- Custom build required for optimization

### 3. CodeMirror

**Pros:**
- **Lightweight**: 55.7KB (v5) to 124KB (v6) minified + gzipped
- **High performance**: Excellent mobile performance
- **Modular architecture**: Include only needed features
- **Advanced editing features**: Beyond just highlighting

**Cons:**
- **Overkill for file viewing**: Designed for editing, not just display
- **More complex integration**: Requires JavaScript initialization
- **Limited themes**: Fewer visual options than dedicated highlighters

**Bundle Size:**
- CodeMirror 5: 55.7KB gzipped
- CodeMirror 6: 124KB gzipped

### 4. Monaco Editor

**Pros:**
- **VS Code experience**: Full IDE-like features
- **Advanced functionality**: IntelliSense, code navigation
- **Professional appearance**: Rich editing experience

**Cons:**
- **Massive bundle size**: >2MB minimum, up to 5MB
- **Performance impact**: 40% of total bundle size
- **Overkill for display**: Too feature-rich for file viewing
- **Complex setup**: Requires special bundler configuration

**Bundle Size:**
- Minimum: >2MB gzipped
- Typical: 2.4-5MB

## Language Support Comparison

| Library | Total Languages | JS/Python/HTML/CSS/JSON/MD | Auto-Detection |
|---------|----------------|----------------------------|-----------------|
| Prism.js | 297 | ✅ All supported | ❌ (Manual class) |
| Highlight.js | 192 | ✅ All supported | ✅ Automatic |
| CodeMirror | 100+ | ✅ All supported | ⚠️ Manual mode |
| Monaco | 50+ | ✅ All supported | ⚠️ Manual mode |

## File Extension to Language Mapping

**Challenge**: Most libraries require manual language specification rather than automatic file extension detection.

**Solutions:**
1. **Create mapping function** in Flask backend
2. **Use automatic detection** (Highlight.js only)
3. **Implement detection logic** with file extensions

### Recommended Extension Mapping for Flask:
```python
EXTENSION_MAP = {
    '.js': 'javascript',
    '.jsx': 'jsx', 
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.py': 'python',
    '.html': 'markup',
    '.htm': 'markup',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.json': 'json',
    '.md': 'markdown',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.xml': 'xml',
    '.sql': 'sql',
    '.sh': 'bash',
    '.dockerfile': 'docker',
    '.go': 'go',
    '.rust': 'rust',
    '.php': 'php',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp'
}
```

## Implementation Examples

### Prism.js - Lightweight Flask Integration

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flask File Viewer</title>
    
    <!-- Prism.js Theme CSS -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />
    
    <!-- Optional: Line numbers plugin -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css" rel="stylesheet" />
</head>
<body>
    <h1>{{ filename }}</h1>
    
    <!-- File content with language class from Flask -->
    <pre class="line-numbers"><code class="language-{{ language }}">{{ file_content | escape }}</code></pre>
    
    <!-- Prism.js Core -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    
    <!-- Autoloader for dynamic language loading -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    
    <!-- Optional plugins -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js"></script>
</body>
</html>
```

### Flask Backend with Language Detection

```python
from flask import Flask, render_template, request
import os

app = Flask(__name__)

EXTENSION_MAP = {
    '.js': 'javascript',
    '.py': 'python', 
    '.html': 'markup',
    '.css': 'css',
    '.json': 'json',
    '.md': 'markdown',
    # Add more mappings as needed
}

def get_language_from_extension(filename):
    """Get Prism.js language identifier from file extension"""
    ext = os.path.splitext(filename)[1].lower()
    return EXTENSION_MAP.get(ext, 'text')

@app.route('/view/<path:filepath>')
def view_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        language = get_language_from_extension(filepath)
        filename = os.path.basename(filepath)
        
        return render_template('file_viewer.html', 
                             filename=filename,
                             file_content=content,
                             language=language)
    except Exception as e:
        return f"Error reading file: {e}", 404

if __name__ == '__main__':
    app.run(debug=True)
```

### Alternative: Highlight.js with Auto-Detection

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flask File Viewer</title>
    
    <!-- Highlight.js Theme CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
</head>
<body>
    <h1>{{ filename }}</h1>
    
    <!-- Auto-detection - no language class needed -->
    <pre><code>{{ file_content | escape }}</code></pre>
    
    <!-- Highlight.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
</body>
</html>
```

## Performance Recommendations

### For Maximum Performance (Prism.js):
1. **Use Autoloader plugin** for dynamic language loading
2. **Load only core initially** (2KB)
3. **Languages load on-demand** (0.3-0.5KB each)
4. **Choose lightweight themes** (~1KB)

### Bundle Size Optimization:
- **Prism.js with Autoloader**: 2KB + languages as needed
- **Highlight.js Common**: 188KB gzipped upfront
- **Custom Highlight.js build**: Variable, requires build process

## Theme Options

### Prism.js Popular Themes:
- `prism.min.css` - Default light theme
- `prism-okaidia.min.css` - Dark theme
- `prism-tomorrow-night.min.css` - Popular dark theme
- `prism-coy.min.css` - Minimal light theme

### Highlight.js Popular Themes:
- `default.min.css` - Clean light theme
- `github.min.css` - GitHub-style
- `atom-one-dark.min.css` - Popular dark theme
- `vs2015.min.css` - Visual Studio dark

## Final Recommendation

**Use Prism.js** for your Flask file viewer because:

1. **Optimal Performance**: 2KB core + 0.3-0.5KB per language
2. **Best CDN Support**: Reliable global distribution
3. **Comprehensive Language Support**: 297 languages available
4. **Easy Flask Integration**: Simple template implementation
5. **Extensible**: Rich plugin ecosystem when needed
6. **Modern**: Built with current web standards

The slight overhead of manual language mapping is easily handled in Flask and results in significantly better performance than auto-detection alternatives.

For automatic language detection needs, Highlight.js is the fallback choice, but comes with a 90x larger initial bundle size (188KB vs 2KB).

## CDN Links (Current - 2024)

### Prism.js (Recommended):
```html
<!-- CSS -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />

<!-- Core JS -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>

<!-- Autoloader -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
```

### Highlight.js (Alternative):
```html
<!-- CSS -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">

<!-- JS -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
```