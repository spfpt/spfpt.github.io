# spfpt.github.io

Personal writing site, served by GitHub Pages from `main`.

## Structure

```
spfpt.github.io/
├── .nojekyll                                    # serve raw HTML, no Jekyll pipeline
├── index.html                                   # hub / landing
├── build.sh                                     # rebuild post HTML from markdown source
├── claude-code-from-zero-to-agentic/
│   ├── index.html                               # the post
│   └── assets/                                  # screenshots used in the post
```

Each post is a self-contained directory under the root, modelled on Thariq Shihipar's [`html-effectiveness`](https://github.com/ThariqS/html-effectiveness) gallery — no build step, no framework, just a hand-crafted HTML file per piece.

## Adding or updating a post

The source-of-truth for each post lives in a sibling repo (`fai-writeups` for now). To rebuild this site's HTML from the latest markdown:

```bash
./build.sh
```

`build.sh` converts the markdown body with `markdown-it` + `markdown-it-anchor`, then injects it into the post's shell template (preserves the inline CSS / JS / dark-mode / scrollspy / copy-buttons).

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

## License

Words © spfpt. Code in the templates (CSS, JS) is CC0 — copy freely.
