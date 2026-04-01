# Open Questions & Unknowns

**Version:** 0.1 | **Date:** 2025-03-29 | **Project:** Haskell PDF Editor

Use this as a checklist for collaborative design iteration. Each question maps to a decision point or blocker.

---

## Phase 1: CLI Wrapper

- [ ] **CLI Interface Design**
  - One monolithic `pdf-cli` subcommand, or separate binaries?
  - Example: `pdf-cli split` vs. `pdf-split`
  - Implication: Distribution, discoverability, user mental model

- [ ] **Configuration**
  - Config file (TOML, YAML, JSON)?
  - Environment variables (PDF_TEMP_DIR, PDF_COMPRESS_LEVEL)?
  - Or just CLI flags only?
  - Implication: Batch operations, presets, scripting

- [ ] **Output Default**
  - If no `--output` specified, replace input or write to `output.pdf`?
  - Implication: Destructive operations, safety

- [ ] **Batch Operations Syntax**
  - How do users chain operations? Shell pipes or dedicated `--batch` file?
  - Example: `pdf-cli split ... | pdf-cli compress ...` vs. `pdf-cli batch rules.txt`
  - Implication: Phase 2 complexity, subprocess overhead

- [ ] **Help Text Verbosity**
  - Full examples in `--help`, or terse + separate `--manual`?
  - Implication: Onboarding, discoverability

- [ ] **Error Message Style**
  - Terse (exit code 1 + one line), or verbose (full context)?
  - Implication: Debuggability, user frustration

---

## Phase 1–2: Testing & Validation

- [ ] **Test PDF Corpus**
  - Where to source 50–100 varied PDFs? (pdfminer tests, PDF Samples repo, real documents)
  - How to organize (by feature, by failure mode)?
  - Implication: Testing coverage, regression safety

- [ ] **Benchmarking Baseline**
  - Against what tool? (Adobe, qpdf, pdftk)
  - Which operations matter most? (compress, split, merge)
  - Implication: Phase 2 performance targets, ROI on FFI

- [ ] **Compatibility Matrix**
  - Test on macOS, Linux, Windows (WSL)? All three or Linux only?
  - Implication: Distribution burden, platform-specific issues

---

## Phase 2: FFI Design

- [ ] **Memory Management Strategy**
  - Use `bracket` for all resources, or custom allocators?
  - How to handle partial failures (e.g., render succeeds, save fails)?
  - Implication: Safety, complexity, error recovery

- [ ] **Lazy vs. Strict Loading**
  - Load entire PDF upfront, or page-on-demand?
  - Implication: Memory scaling for 1000+ page documents

- [ ] **Error Context in FFI**
  - Do we log/store error codes from mupdf, or just boolean success?
  - Implication: Debuggability, error messages to user

- [ ] **C Shim Scope**
  - Minimal bridging only, or wrap more of mupdf?
  - Where's the boundary between Haskell and C?
  - Implication: Maintenance, FFI learning curve

- [ ] **Dependency Management**
  - System mupdf via `pkgconfig-depends`, or vendor it?
  - Implication: Distribution, build complexity

---

## Phase 3: Annotation & Rendering

- [ ] **Rendering Quality**
  - DPI/resolution settings? (72, 150, 300 dpi)?
  - Default, or configurable?
  - Implication: Preview quality, file size

- [ ] **Color Space Handling**
  - Support CMYK, Grayscale, Lab, or RGB only?
  - Implication: Print vs. screen use, color fidelity

- [ ] **Annotation Persistence**
  - Content stream (permanent, non-interactive) vs. PDF annotations (editable)?
  - Implication: User expectations, Phase 4 complexity

- [ ] **Font Handling in Annotations**
  - Use device fonts (Helvetica, Times), or embed?
  - Implication: Portability, visual fidelity across readers

- [ ] **Search Implementation**
  - Full-text index on load, or linear scan?
  - Case-sensitive by default?
  - Implication: Speed, memory, user expectations

---

## Phase 4: Text Editing & Forms

- [ ] **Text Editing Scope**
  - Can only edit existing text, or add new text?
  - Implication: Complexity, feature set

- [ ] **Font Subsetting**
  - Call fonttools (Python subprocess), or Haskell FFI binding?
  - Implication: Dependency chain, maintenance burden

- [ ] **Form Field Types**
  - Text fields only, or also checkboxes, dropdowns, buttons?
  - Implication: Feature completeness, AcroForm complexity

- [ ] **Form Flattening**
  - Support flattening (merge form into content), or read-only?
  - Implication: User expectation, PDF mutation complexity

- [ ] **OCR Output Quality**
  - Store raw tesseract output, or post-process (spell check, layout)?
  - Implication: Accuracy, complexity, dependencies

---

## Long-term (Post-v1.0)

- [ ] **UI Layer**
  - Command-line only, or GUI (GTK, Qt, etc.)?
  - Implication: User experience, maintenance, scope creep

- [ ] **Performance Targets**
  - Edit 100-page PDF in <5 seconds? <1 second?
  - Implication: Optimization scope, worth the cost?

- [ ] **Platform Support**
  - Linux only, or Windows/macOS first-class?
  - Implication: Distribution, testing burden

- [ ] **Extensibility**
  - Plugin architecture for custom operations?
  - Implication: Architecture complexity, third-party ecosystem

- [ ] **Licensing & Distribution**
  - Publish to Hackage, GitHub, binaries?
  - GPL (mupdf dependent) vs. MIT?
  - Implication: User adoption, legal concerns

---

## Unknowns Requiring Spike Work

| Unknown | Spike Task | Effort | Phase | Owner |
|---------|-----------|--------|-------|-------|
| mupdf C FFI learning | Bind 3 simple functions, test on 5 PDFs | 4–6 hours | 2-pre | Basit |
| PDF content stream syntax | Manually construct one annotation, verify in Adobe | 3–4 hours | 3-pre | Basit |
| Tesseract hOCR output | Run tesseract, parse hOCR, understand format | 2–3 hours | 4a-pre | Basit |
| Font subsetting workflow | Run fonttools on sample, understand output | 1–2 hours | 4b-pre | Basit |

---

## Decision Checkpoints

**Before Phase 1 Start:**
- [ ] CLI framework chosen (optparse-applicative yes/no)
- [ ] Error handling strategy chosen (typed sum vs. string)
- [ ] Temp file management decided

**Before Phase 2 Start:**
- [ ] Test corpus sourced and categorized
- [ ] Baseline benchmarks established
- [ ] FFI memory strategy decided

**Before Phase 3 Start:**
- [ ] Annotation persistence model chosen
- [ ] Rendering quality parameters set
- [ ] Font strategy for annotations decided

**Before Phase 4 Start:**
- [ ] Text editing scope scoped (read-only? mutate?)
- [ ] Form field types enumerated
- [ ] Subsetting strategy chosen (subprocess vs. FFI)

---

## How to Use This File

1. **Before phase start:** Answer all open questions in the "Checkpoints" section.
2. **During phase:** Mark unknowns as "RESOLVED" with brief note.
3. **Blockers:** If stuck, spike the "Unknowns Requiring Spike Work" table item.
4. **Iteration:** Link to `pdf-editor-iteration.md` when decisions are locked in.

---

## References & Research

- **PDF Spec:** https://www.adobe.io/content/dam/udp/assets/open/pdf/spec/PDF32000_2008.pdf
- **mupdf API:** https://mupdf.com/docs/
- **Haskell FFI:** https://wiki.haskell.org/FFI
- **optparse-applicative:** https://hackage.haskell.org/package/optparse-applicative
- **Tesseract hOCR:** https://github.com/UB-Mannheim/tesseract/wiki
- **fonttools:** https://fonttools.readthedocs.io/

