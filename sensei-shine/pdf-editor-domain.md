# Problem Domain: Haskell PDF Editor

**Version:** 0.1 | **Date:** 2025-03-29 | **Status:** Pre-Phase-1

---

## Goal

Personal-use PDF tool with feature parity to **Adobe Reader/Acrobat circa 2014**. No cloud sync. Incremental CLI-first approach.

---

## Core Operations (Priority Order)

### Must Have (Phase 1)
- [ ] Split (extract page range)
- [ ] Merge (combine PDFs)
- [ ] Compress (reduce file size)
- [ ] Rotate/reorder pages
- [ ] Extract text
- [ ] Extract images
- [ ] Convert to/from (docx, images via pandoc/imagemagick)

### Should Have (Phase 2–3)
- [ ] Render pages (preview/raster)
- [ ] Annotate (text, shapes, highlight)
- [ ] Search across PDFs
- [ ] Inspect document structure

### Nice to Have (Phase 4+)
- [ ] Text editing (requires font subsetting)
- [ ] Form filling (AcroForm)
- [ ] OCR integration
- [ ] Bookmark manipulation
- [ ] Watermark/stamp

---

## Non-Goals

- Cloud sync
- Real-time collab
- Mobile apps
- AI-powered stuff (summarization, extraction)
- Full PDF 2.0 spec compliance
- Encrypted PDF editing (read-only OK)

---

## Hard Constraints

| Constraint | Reason | Implication |
|-----------|--------|-------------|
| No year-long v1 | Pragmatism | Ship Phase 1 in 2 weeks, iterate |
| Haskell | Proof-of-work, learning | FFI only where subprocess insufficient |
| Personal-use scope | Maintainability | OK to call external binaries, skip edge cases for now |

---

## Known Friction Points

| Point | Severity | Mitigated By |
|-------|----------|-------------|
| PDF spec complexity | High | Delegate parsing to mupdf, only understand content streams |
| Font handling (text edit) | High | Defer to Phase 4, use fonttools subprocess first |
| Rendered output quality | Medium | Use mupdf's renderer, acceptable for preview |
| Form spec (AcroForm) | Medium | Phase 4+, start with annotation overlay |

---

## Delegation Strategy

```
Problem                   → Tool/Library
─────────────────────────────────────
PDF parsing               → mupdf (C library, FFI)
Compression               → ghostscript, qpdf (subprocess)
Rendering                 → mupdf (subprocess or Phase 2 FFI)
Format conversion         → pandoc, imagemagick (subprocess)
OCR                       → tesseract (subprocess, Phase 4)
Font subsetting           → fonttools (subprocess, Phase 4)
Text layout               → HaTeX or custom (Phase 4)
```

---

## Open Questions

1. **CLI interface design** — how much does `pdf-cli` abstract? One command or subcommands?
2. **Configuration** — config file, env vars, or just flags?
3. **Batch operations** — Phase 1 subprocess overhead OK, or move to FFI sooner?
4. **Testing strategy** — mock PDFs or use real ones from corpus?
5. **Error handling** — how granular? Fail fast or collect all errors?

---

## Success Criteria (per phase)

**Phase 1:** CLI tool that handles split/merge/compress without errors on 10 common PDF types.

**Phase 2:** Programmatic API; batch operations 2x faster than subprocess overhead.

**Phase 3:** Render pipeline; annotation algebra working (shapes, text, highlights).

**v1 (Phase 4):** Text editing functional, forms partially supported, OCR pipeline in place.

