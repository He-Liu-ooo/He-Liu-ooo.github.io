# Repository Purpose

This repository publishes Liu He's English academic homepage through GitHub Pages at https://he-liu-ooo.github.io. It focuses on his biography, research, publications, university education, and professional links.

## Architecture

- `index.html` contains the public content and semantic structure.
- `styles.css` provides the responsive Pure Monochrome presentation.
- `files/profile/` contains the public profile image.
- `files/cv/`, `files/papers/`, and `files/slides/` contain public downloads.

Keep the site static. Do not add JavaScript, a framework, a package manager, analytics, external fonts, or build tooling unless the owner changes the requirements.

## Privacy

The root `CV.pdf` is a private source containing a phone number and full address. It is ignored and must never be staged, committed, or published. Enable the public CV link only after placing a sanitized copy under `files/cv/`. Do not publish unapproved sensitive information. Everything under `files/` becomes public.

Binary public downloads, especially CV PDFs, require manual content and privacy inspection before staging because simple text inspection may not reveal their contents.

## Content Maintenance

- Replace `Research interests statement forthcoming.` only with text approved by the owner.
- Put the approved profile photo under `files/profile/`, update its `src`, and preserve useful `alt` text plus explicit dimensions.
- Add publication links only after verifying them.
- Put distributable papers in `files/papers/` and slides in `files/slides/`.
- Link to a DOI or publisher page when a paper cannot be redistributed.
- Keep the page timeless: do not add news, year-of-study labels, or last-updated text.
- Keep `LINKS.md` synchronized with the links in `index.html`.

## Verification

Preview the site locally:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

The server runs in the foreground; use a browser for the preview. The loopback binding keeps the repository, including any ignored root `CV.pdf`, off the lab network. Inspect desktop and mobile layouts, verify all local links and assets, and confirm there is no horizontal overflow.

Before committing, inspect the staged file names:

```bash
git diff --cached --name-only
```

The output must not include `CV.pdf`, `.worktrees/`, `.superpowers/`, or `docs/superpowers/`.
