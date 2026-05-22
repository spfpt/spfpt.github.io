#!/usr/bin/env bash
# Rebuild post HTML from a markdown source file.
#
# Requires Node (uses npx to pull markdown-it + markdown-it-anchor on first run,
# then caches them under /tmp/cc-build/node_modules). No npm install at the
# site root.
set -euo pipefail

SITE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SRC_MD="${1:-${SRC_MD:-}}"
POST_HTML="$SITE_DIR/claude-code-101/index.html"
BUILD_DIR="/tmp/cc-build"

if [ -z "$SRC_MD" ]; then
  echo "usage: ./build.sh /path/to/source.md" >&2
  echo "   or: SRC_MD=/path/to/source.md ./build.sh" >&2
  exit 1
fi

if [ ! -f "$SRC_MD" ]; then
  echo "error: source markdown not found at $SRC_MD" >&2
  exit 1
fi

# install converter deps once
if [ ! -d "$BUILD_DIR/node_modules/markdown-it" ]; then
  mkdir -p "$BUILD_DIR"
  cd "$BUILD_DIR"
  npm init -y >/dev/null 2>&1
  npm install --silent markdown-it markdown-it-anchor 2>&1 | tail -3
  cd - >/dev/null
fi

# converter script
cat > "$BUILD_DIR/convert.js" <<'JS'
const MarkdownIt = require('markdown-it');
const anchor = require('markdown-it-anchor');
const fs = require('fs');

const md = new MarkdownIt({ html: true, linkify: false, typographer: false });
md.use(anchor, {
  slugify: s => s.toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
});

const input = fs.readFileSync(process.argv[2], 'utf8');
process.stdout.write(md.render(input));
JS

node "$BUILD_DIR/convert.js" "$SRC_MD" > "$BUILD_DIR/body.html"

# inject body into the existing shell (preserves all the CSS/JS/markup around it)
python3 <<PY
import re
shell_path = "$POST_HTML"
body_path  = "$BUILD_DIR/body.html"

body = open(body_path).read()
# strip the inline Contents TOC (the sidebar replaces it)
body = re.sub(
    r'<hr>\s*<h2 id="contents"[^>]*>.*?</h2>\s*<ol>.*?</ol>\s*<hr>\s*',
    '\n',
    body, count=1, flags=re.DOTALL
)
# h1 doesn't need an id
body = re.sub(r'<h1 id="[^"]*"[^>]*>', '<h1>', body, count=1)

shell = open(shell_path).read()

# find the <main class="article">…</main> block and replace its inner content
new_shell = re.sub(
    r'(<main id="main" class="article">)(.*?)(</main>)',
    lambda m: m.group(1) + '\n' + body.rstrip() + '\n  ' + m.group(3),
    shell, count=1, flags=re.DOTALL
)
open(shell_path, 'w').write(new_shell)
print(f"  built {shell_path} ({len(new_shell)} bytes)")
PY

echo "  done."
