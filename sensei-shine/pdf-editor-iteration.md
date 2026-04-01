# Iteration Log: Design Decisions & Pivots

**Version:** 0.1 | **Date:** 2025-03-29 | **Project:** Haskell PDF Editor

---

## Format

Each entry follows this template:

```
### Decision: [Short Title]
**Date:** YYYY-MM-DD | **Phase:** [1/2/3/4] | **Status:** [Decided/Open/Deferred]
**Author:** Basit

**Context:**
[Why this came up. What problem forced the choice?]

**Options Considered:**
1. **Option A** — pros/cons, implementation cost
2. **Option B** — pros/cons, implementation cost
3. **Option C** — pros/cons, implementation cost

**Chosen:** Option X

**Rationale:**
[Why X over others. Proof-of-work, pragmatism, learning?]

**Implication:**
[What changes downstream. Cascading effects.]

**Blocker/Unknown:**
[What still needs testing. What could break this decision?]

---
```

---

## Decisions Log

### Decision: CLI Framework (optparse-applicative vs. Manual Parsing)
**Date:** 2025-03-29 | **Phase:** 1 | **Status:** Open

**Context:**
Phase 1 needs CLI parsing for `pdf-cli split`, `pdf-cli merge`, etc. Standard choice: optparse-applicative vs. hand-rolled parser combinator.

**Options Considered:**
1. **optparse-applicative** — mature, well-typed, generates help automatically
   - Pro: Industry standard, error messages are good
   - Con: Adds dependency, slight learning curve
   - Cost: 1–2 hours to learn + implement
   
2. **Hand-rolled** — use `System.Environment.getArgs` + pattern match
   - Pro: Zero dependencies, full control
   - Con: Error handling tedious, help text manual
   - Cost: 3–4 hours (error cases, help)
   
3. **Turtle** — unix-like shell scripting in Haskell
   - Pro: Piping, composition
   - Con: Overkill for static arg parsing, adds heavy dependency
   - Cost: Medium learning curve

**Chosen:** optparse-applicative

**Rationale:**
Standard choice. Error messages are actionable (beats hand-rolled). Help text automatic. Learning investment pays off in Phase 2 (config files, batch syntax). Pragmatism: don't reinvent parsing.

**Implication:**
- Add `optparse-applicative` to cabal dependencies
- Write small `CLI.hs` module to wrap it
- Phase 2+ can extend with config file parsing (same framework)

**Blocker/Unknown:**
- Is help text generation good enough, or do we customize?
- Test with `--help` on real usage patterns once Phase 1 is live.

---

### Decision: Error Handling (String vs. Typed Error Sum)
**Date:** 2025-03-29 | **Phase:** 1 | **Status:** Open

**Context:**
Subprocess calls will fail. How do we represent failures?

**Options Considered:**
1. **Typed Error Sum** — `data PDFError = FileNotFound | ParseError String | ProcessFailed Int String`
   - Pro: Pattern matching, no string parsing
   - Con: Requires exhaustive case analysis downstream
   - Cost: 2–3 hours (design + implementation)
   
2. **String Errors** — `IO (Either String a)`
   - Pro: Quick, flexible
   - Con: Hard to pattern match, error messages are unstructured
   - Cost: 1 hour (zero overhead)
   
3. **Exception + Catch** — use `Exception` typeclass, throw/catch
   - Pro: Traditional, forces error propagation
   - Con: Less type-safe, mixed control flow
   - Cost: 1–2 hours

**Chosen:** Typed Error Sum + Show instance

**Rationale:**
Proof-of-work: typed errors are the Haskell way. Phase 3+ annotation writing will need structured errors (PDF parse failures vs. IO). Invest early.

**Implication:**
- Write `PDF.Error` module with sum type
- All subprocess wrappers return `IO (Either PDFError a)`
- Error display: `show` for CLI, detailed context for logs

**Blocker/Unknown:**
- Do we add error context (file path, operation)? Yes, but defer to Phase 2.
- Test error handling with intentionally broken PDFs.

---

### Decision: Subprocess Piping (temp files vs. stdin/stdout)
**Date:** 2025-03-29 | **Phase:** 1 | **Status:** Open

**Context:**
`pdf-cli split` calls `mutool` or `qpdf`. Should we:
- Write temp files on disk
- Pipe via stdin/stdout
- Mixed (some ops use files, others pipes)

**Options Considered:**
1. **Temp Files** — input → temp1 → temp2 → output
   - Pro: Simple, debuggable, predictable
   - Con: Disk I/O, cleanup on error, slow for large files
   - Cost: 2 hours
   
2. **Pipes** — cat input | op | op | cat > output
   - Pro: Memory efficient, faster, no disk thrashing
   - Con: Error handling harder (stderr mixing, exit codes)
   - Cost: 3–4 hours
   
3. **Mixed** — pipes where supported, fallback to files
   - Pro: Best of both
   - Con: Complexity, conditional logic per operation
   - Cost: 4–5 hours

**Chosen:** Temp Files (Phase 1), defer pipes to Phase 2 batch optimization

**Rationale:**
Pragmatism: Phase 1 is a week. Temp files are predictable, debuggable. Performance scaling (piping) is Phase 2 concern when batch operations matter. Ship early.

**Implication:**
- Use `System.IO.Temp.withSystemTempDirectory`
- Each operation: input → (temp1, temp2, ...) → output → cleanup
- Error handling: delete temps on exception

**Blocker/Unknown:**
- Test on low-disk systems (tight temp dir). Fallback?
- Revisit when batch processing begins (Phase 2).

---

### Decision: Rendering Library (mupdf vs. Building Own)
**Date:** 2025-03-29 | **Phase:** 2 | **Status:** Open

**Context:**
Phase 2–3 needs rendering. Fork mupdf or build custom?

**Options Considered:**
1. **mupdf subprocess** — `pdftoppm input.pdf output`
   - Pro: Zero FFI, works now
   - Con: Slow, lossy (raster quality), no per-annotation control
   - Cost: 0 (already have binary)
   
2. **mupdf FFI** — bind `fz_render_page` in Haskell
   - Pro: Fast, per-page control, memory efficient
   - Con: C FFI learning curve, lifetime management
   - Cost: 2–3 weeks
   
3. **Custom renderer** — write from scratch
   - Pro: Maximum learning, control
   - Con: Years of work, reinvent the wheel, forget it
   - Cost: Infinite

**Chosen:** mupdf FFI (Phase 2)

**Rationale:**
Proof-of-work: FFI is valuable skill. mupdf is battle-tested (no need to reinvent). Rendering is core to annotation (Phase 3), so investment needed.

**Implication:**
- Phase 2 FFI binding focuses on `fz_render_page` + pixmap API
- Minimal C shim for memory management
- Test on 20 real PDFs for output quality

**Blocker/Unknown:**
- DPI/quality settings — do we expose?
- Color space handling (RGB vs. CMYK)?
- Defer to first failure.

---

### Decision: Annotation Persistence (PDF content stream vs. Annotation objects)
**Date:** 2025-03-29 | **Phase:** 3 | **Status:** Open

**Context:**
Phase 3 annotations: should they be:
- Embedded in PDF content stream (immutable, permanent)
- Stored as PDF annotation objects (removable, editable)

**Options Considered:**
1. **Content Stream** — draw shapes/text into page's graphics stream
   - Pro: Permanent, looks like part of original document, works in all readers
   - Con: Can't edit/delete without reconstructing page
   - Cost: 2 weeks (learn PDF syntax, careful parsing)
   
2. **Annotation Objects** — use PDF's `/Annot` dictionary
   - Pro: Editable, standard, Adobe-compatible
   - Con: Not all readers respect, complex state management
   - Cost: 3 weeks (AcroForm spec, widget handling)
   
3. **Both** — content stream for stamps, annotations for interactive markup
   - Pro: Flexibility
   - Con: Complexity, two code paths
   - Cost: 4–5 weeks

**Chosen:** Content Stream (Phase 3), defer Annotation Objects to Phase 4

**Rationale:**
Pragmatism: content stream is simpler (no widget state), works everywhere. Phase 3 goal is "mark up for review", not "fill forms". Phase 4 can do proper AcroForm.

**Implication:**
- Write simple PDF content stream builder (shapes, text)
- Append to page's `/Contents` stream
- Can't edit/remove after save (document this)

**Blocker/Unknown:**
- Font rendering in content stream — use device fonts or embedded? Device fonts first.
- Test on 10 real PDFs, verify readability in Adobe + Preview.

---

## Deferred Decisions

### (Placeholder for decisions that need data first)

**Decision: Font Subsetting Strategy** — wait until Phase 4a when text editing is live. Subprocess call (`fonttools`) vs. FFI binding.

**Decision: Config File Format** — wait until Phase 2 when batch operations matter. TOML vs. custom DSL.

**Decision: Streaming Large PDFs** — wait until we hit a bottleneck. Process.withCreateProcess + lazy I/O vs. strict buffering.

---

## Lessons Learned (Cumulative)

*Filled in as project progresses.*

---

## References

- [PDF 1.7 Spec](https://www.adobe.io/content/dam/udp/assets/open/pdf/spec/PDF32000_2008.pdf) (sections 5.3, 8.6, 12.6 relevant)
- [mupdf C API](https://mupdf.com/docs/) (API reference)
- [Haskell FFI Guide](https://wiki.haskell.org/FFI) (best practices)
- [optparse-applicative docs](https://hackage.haskell.org/package/optparse-applicative) (CLI parsing)

