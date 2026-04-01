# Architecture & Approach: Haskell PDF Editor

**Version:** 0.1 | **Date:** 2025-03-29 | **Status:** Pre-Phase-1

---

## Architectural Thesis

**Phase 1–2:** Subprocess-first wrappers around battle-tested binaries (mupdf, qpdf, ghostscript). Haskell orchestrates.

**Phase 2+:** Selective FFI to mupdf for operations where subprocess overhead dominates or state must persist.

**Phase 4+:** Custom rendering/editing logic, still delegating hard problems (fonts, OCR) to subprocesses or extern libs.

---

## Dependency Landscape

### System Dependencies (Required)

| Dep | Version | Phase | Used For | Notes |
|-----|---------|-------|----------|-------|
| mupdf | 1.23+ | 1+ | PDF parsing, rendering | Source build OK, also distro packages |
| qpdf | 11+ | 1 | Compression, split/merge | Well-maintained, distro packages |
| ghostscript | 10+ | 1 | Compression alt, raster | Ubiquitous, might be bloated |
| pandoc | 2.19+ | 1 | Format conversion | Already installed (probably) |

### Haskell Dependencies (Minimal)

**Phase 1 only:**
```
base
process          -- subprocess calls
filepath
bytestring
text
optparse-applicative  -- CLI parsing
```

**Phase 2+:**
```
(above, plus)
foreign-library  -- for FFI shim building
containers       -- annotation graph
```

**Phase 3+:**
```
(above, plus)
vector           -- pixel data for rendering
Codec.Image.PNG  -- save rendered pages
```

**Avoid initially:**
- Heavy image libs (JuicyPixels until necessary)
- Streaming libs (zip until batch operations)
- XML parsers (for PDF xobjects; parse manually at first)

---

## Project Structure

```
haskell-pdf-editor/
├── README.md                   # Quick start
├── ARCHITECTURE.md             # This file + decisions
├── ITERATION_LOG.md            # Decision journal
│
├── cabal.project
├── haskell-pdf.cabal
│
├── app/
│   └── Main.hs                 # CLI entry, Phase 1
│
├── lib/
│   └── PDF/
│       ├── CLI.hs              # Subprocess wrappers (Phase 1)
│       ├── Types.hs            # Shared types (Document, Page, Op)
│       ├── Error.hs            # Error types
│       │
│       ├── MuPDF/              # Phase 2 onwards
│       │   ├── Raw.hs          # Raw FFI declarations
│       │   ├── Safe.hs         # Bracketed, safe API
│       │   └── Types.hs        # FFI-aligned types
│       │
│       ├── Annotate.hs         # Phase 3: annotations
│       ├── Render.hs           # Phase 3: rasterization
│       └── Edit.hs             # Phase 4: text editing
│
├── cbits/                      # Phase 2 onwards
│   ├── mupdf_bridge.h
│   └── mupdf_bridge.c          # Memory management shim
│
├── test/
│   ├── Phase1Spec.hs           # Phase 1 subprocess tests
│   └── fixtures/               # Real PDF samples
│
└── docs/
    ├── PDF_SPEC_NOTES.md       # Annotations as you read spec
    └── FFI_BINDING_GUIDE.md    # Phase 2 reference
```

---

## Phase 1: CLI Wrapper (Week 1–2)

### Architecture

```
User
  ↓ (cli args)
Main.hs (optparse-applicative)
  ↓
PDF.CLI module
  ├─ splitPDF
  ├─ mergePDF
  ├─ compressPDF
  ├─ rotatePDF
  ├─ extractText
  ├─ extractImages
  └─ convertPDF
    ↓ (Process.readProcess)
  subprocess (mupdf, qpdf, ghostscript, etc.)
    ↓
  stdout → file or pipe
```

### Key Design

- **No internal state.** Each operation is pure (input file → output file).
- **Subprocess as library.** Each wrapper is `FilePath → FilePath → IO (Either Error ())`.
- **Error handling.** Capture stderr, parse error codes, raise `PDFError` sum type.
- **Streaming for large files.** Use `Process.withCreateProcess` for piped output (future).

### Example (split):

```haskell
splitPDF :: FilePath -> [Int] -> FilePath -> IO (Either Error ())
-- splitPDF input [1,2,3] output
-- calls: mutool clean input && mutool extract input 1 2 3 output
```

---

## Phase 2: FFI to MuPDF (Month 2–3)

### When to Start

After Phase 1 is stable and you've identified the bottleneck. Likely:
- Batch operations (10+ PDFs, subprocess overhead).
- Introspection (want to know page count, metadata without subprocess).
- Stateful operations (load once, multiple reads).

### Architecture

```
Haskell
  ↓
PDF.MuPDF.Safe (bracketed resource API)
  ├─ withDocument :: FilePath → (Document → IO a) → IO a
  ├─ pageCount :: Document → IO Int
  ├─ renderPage :: Document → Int → IO (Pixmap)
  └─ getPageResources :: Document → Int → IO Resources
    ↓ (foreign import ccall)
  C shim (mupdf_bridge.c)
    ↓
  libmupdf.a (system library or vendored)
```

### Key Design

- **Lifetime management.** Use `bracket` for `fz_context`, `fz_document`.
- **Minimal C shim.** Only wrap lifetime-unsafe operations; keep Haskell logic in Haskell.
- **No exceptions in FFI.** Return error codes, marshal to `Either`.
- **Lazy loading.** Pages load on demand, not upfront.

### Binding Strategy

Raw layer (PDF.MuPDF.Raw):
```haskell
foreign import ccall "mupdf.h fz_open_document"
  fz_open_document :: CString → IO (Ptr FzDocument)

foreign import ccall "mupdf.h &fz_drop_document"
  fz_drop_document :: FunPtr (Ptr FzDocument → IO ())
```

Safe layer (PDF.MuPDF.Safe):
```haskell
withDocument :: FilePath → (Document → IO a) → IO a
withDocument path f = do
  cpath ← newCString path
  bracket
    (fz_open_document cpath)
    fz_drop_document
    (fmap Document . f . Ptr)
```

---

## Phase 3: Rendering & Annotation (Month 3–6)

### Annotation Algebra

```haskell
data Annotation
  = TextStamp Text (Float, Float) -- (x, y)
  | HighlightBox (Float, Float, Float, Float) -- (x0, y0, x1, y1)
  | Circle (Float, Float) Float -- center, radius
  | FreeformInk [(Float, Float)] -- polyline
  
data AnnotatedPage = AnnotatedPage
  { page :: Page
  , annotations :: [Annotation]
  }
```

Write annotations back to PDF content stream (manual PDF syntax construction).

### Rendering

Use mupdf's `fz_render_page` to pixmap, then save as PNG with `Codec.Image.PNG`.

---

## Phase 4: Text Editing, Forms (Month 6–12)

### Font Subsetting Strategy

Don't implement. Call `fonttools` (Python) via subprocess:
```haskell
subsettingPDF :: FilePath → [Char] → FilePath → IO (Either Error ())
-- Calls: pyftsubset ... → embeds result
```

### Text Layout

Use `HaTeX` or build minimal layout engine (reflow text to widths).

### Form Handling

Parse AcroForm dict, walk widget annotations, write filled values to annotation content.

---

## Decision Log Template

(See ITERATION_LOG.md — same format for each decision point.)

```
### Decision: [Title]
**Date:** YYYY-MM-DD | **Phase:** N | **Status:** [Decided/Open/Deferred]

**Context:** Why this came up.

**Options:**
1. Option A — pros/cons
2. Option B — pros/cons

**Chosen:** Option X because [reason].

**Implication:** What changes downstream.

---
```

---

## Testing Strategy

**Phase 1:** Real PDFs (10–20 samples covering fonts, images, compression).
- Test each subprocess command against known inputs.
- Use exit codes + stderr parsing for error cases.

**Phase 2:** FFI tests (memory safety, lifetime).
- Verify no segfaults under stress (100 rapid open/close).
- Benchmark subprocess vs. FFI overhead.

**Phase 3:** Annotation tests.
- Render + annotate, visually inspect output.
- Compare with reference PDFs.

**Phase 4:** Editing tests.
- Text edit round-trip (load → edit → save → reload, verify).
- Form fill with edge cases (multi-line fields, special chars).

---

## Build & CI

**Cabal only** (no Stack).

```bash
cabal build
cabal test
cabal run pdf-cli -- --help
```

**System dependencies:** Cabal can declare them in `.cabal` with `pkgconfig-depends`.

---

## Open Decisions

1. **CLI design.** One big `pdf-cli` or modular `pdf-split`, `pdf-merge`, etc.?
2. **Config file.** TOML? YAML? None (env vars only)?
3. **Batch syntax.** `--batch rules.txt` or just loop in shell?
4. **Output format.** Always PDF, or support PNG/JSON metadata?

