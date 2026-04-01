# Phase Roadmap & Milestones

**Version:** 0.1 | **Date:** 2025-03-29 | **Owner:** Basit

---

## Overview

```
Phase 1 (2 wk)     Phase 2 (2–3 mo)   Phase 3 (3–6 mo)   Phase 4 (6–12 mo)   v1.0
├─ CLI wrapper     ├─ FFI to mupdf    ├─ Render          ├─ Text edit        [Ship]
├─ Split/merge     ├─ Batch ops       ├─ Annotate        ├─ Forms             
├─ Compress        ├─ Introspect      ├─ Search          ├─ OCR               
└─ Extract         └─ State persist   └─ Preview         └─ Font subsetting   
```

---

## Phase 1: CLI Wrapper (Weeks 1–2)

**Goal:** Usable command-line tool for common operations. No FFI. Subprocess-first.

**Acceptance Criteria:**
- [ ] `pdf-cli split input.pdf [1,3,5] output.pdf` works
- [ ] `pdf-cli merge in1.pdf in2.pdf output.pdf` works
- [ ] `pdf-cli compress input.pdf output.pdf` works (reduces size measurably)
- [ ] `pdf-cli extract-text input.pdf output.txt` works
- [ ] `pdf-cli extract-images input.pdf output/` works
- [ ] `pdf-cli rotate input.pdf 90 output.pdf` works
- [ ] `pdf-cli convert input.pdf output.docx` works (via pandoc)
- [ ] Help text (`--help`) is clear
- [ ] Error messages are actionable (not "error 127")
- [ ] All 10 test PDFs pass without crashing

**Deliverables:**
- `cabal build` produces `pdf-cli` binary
- `--help` output
- Test suite with 10 real PDFs
- README with usage examples

**Gating Condition for Phase 2:**
- Phase 1 is stable (no crashes on test corpus).
- You've identified the next bottleneck (subprocess overhead, batch ops, introspection).

**Effort:** 2 weeks (80 hours).

---

## Phase 2: FFI to MuPDF (Months 2–3)

**Goal:** Programmatic API; fast batch operations; introspection without subprocess overhead.

**Gating Condition for Entry:**
- Phase 1 stable.
- You've run Phase 1 on 50+ PDFs, found patterns in failures or slowness.
- Identified: "I need faster X" or "I need to know Y without subprocess".

**Acceptance Criteria:**
- [ ] `withDocument "in.pdf" $ \doc -> pageCount doc` works
- [ ] Batch split/merge 10x faster than subprocess (benchmarked)
- [ ] No segfaults under stress test (100 rapid open/close)
- [ ] `renderPage doc 0 >>= savePNG "page.png"` produces viewable image
- [ ] Memory profile shows no leaks (valgrind clean)
- [ ] Can introspect page resources (fonts, images) without subprocess

**Deliverables:**
- `PDF.MuPDF.Safe` module (public API)
- `cbits/mupdf_bridge.c` (minimal shim)
- Benchmark comparison (Phase 1 vs Phase 2)
- 3–5 integration tests with real PDFs

**Key Milestones:**
1. **Week 1:** Raw FFI declarations + simple test (open/close document).
2. **Week 2:** Safe API wrapper with bracket.
3. **Week 3:** Rendering pipeline (to pixmap, save PNG).
4. **Week 4:** Batch operations (verify speedup).

**Effort:** 2–3 months (160–200 hours, much reading C FFI docs).

---

## Phase 3: Rendering & Annotation (Months 3–6)

**Goal:** Visual preview; annotation overlays (highlights, stamps, shapes).

**Gating Condition for Entry:**
- Phase 2 FFI stable.
- You've used Phase 1–2 on real projects, want to annotate PDFs visually.

**Acceptance Criteria:**
- [ ] Render page to PNG: `renderPage doc 0 >>= savePNG "page0.png"`
- [ ] Render with annotations: `renderPage doc 0 annotList >>= savePNG "annot.png"`
- [ ] Annotation algebra works: TextStamp, HighlightBox, Circle, Ink
- [ ] Write annotations back to PDF (manual content stream syntax)
- [ ] Search text across pages: `searchText doc "foo"` returns [(page, x, y)]

**Deliverables:**
- `PDF.Render` module (page → pixmap)
- `PDF.Annotate` module (annotation algebra + serialization)
- Example: Load PDF, annotate page 2, save as new PDF
- Integration test: render + annotate + re-read, verify

**Key Milestones:**
1. **Week 1–2:** Rendering pipeline (mupdf → pixmap → PNG).
2. **Week 3:** Annotation algebra + overlay on pixmap.
3. **Week 4:** Manual content stream writing (read PDF spec section 5.3).
4. **Week 5–6:** Search implementation, edge cases.

**Effort:** 3–6 months (160–240 hours, heavy on PDF spec reading).

---

## Phase 4: Text Editing, Forms, OCR (Months 6–12)

**Goal:** Feature parity with Adobe 2014. Text editing, form filling, OCR pipeline.

**Gating Condition for Entry:**
- Phase 3 stable.
- You've deployed Phase 1–3 and want deeper editing.

**Sub-phases:**

### 4a: Text Editing (Months 6–9)

**Acceptance Criteria:**
- [ ] Load PDF, find text, replace it, save
- [ ] Round-trip: load → edit → save → reload, verify text changed
- [ ] Font subsetting works (via fonttools subprocess)
- [ ] Text reflow on edit (via HaTeX or custom layout)

**Strategy:** 
- Use existing fonts (no embedding new ones yet).
- Call `fonttools` for subsetting.
- Rebuild content stream with new glyphs.

**Effort:** 2–3 months.

### 4b: Form Filling (Months 8–10)

**Acceptance Criteria:**
- [ ] Detect AcroForm fields: `formFields doc`
- [ ] Fill field: `fillField doc fieldName value`
- [ ] Save filled form
- [ ] Round-trip test with real PDF forms

**Strategy:**
- Parse AcroForm dict (manual PDF walk).
- Write values to field widgets.
- Flatten form if needed (merge annotations into content).

**Effort:** 1–2 months.

### 4c: OCR Integration (Months 10–12)

**Acceptance Criteria:**
- [ ] Run tesseract on rasterized page: `ocrPage doc 0`
- [ ] Embed text layer (searchable but invisible)
- [ ] Confidence scores per word
- [ ] Save OCR'd PDF

**Strategy:**
- Render page to PNG (Phase 3).
- Call tesseract subprocess.
- Parse hOCR output, embed as invisible text layer.

**Effort:** 1–2 months.

---

## v1.0: Ship (Month 12+)

**Acceptance Criteria:**
- [ ] All Phase 4 features stable
- [ ] 50+ test PDFs pass without crash
- [ ] Benchmark: edit a 100-page PDF in <5 seconds
- [ ] Documentation complete (user guide + API docs)
- [ ] GitHub release with tagged binary

**Deliverable:** `haskell-pdf v1.0` on GitHub, Hackage upload optional.

**Effort:** 1 month (polish, testing, docs).

---

## Parallel Work (All Phases)

- **Documentation.** Keep PDF_SPEC_NOTES.md updated as you learn.
- **Testing.** Add 1 test per phase per week.
- **Benchmarking.** Monthly comparison of performance vs. Adobe/qpdf.
- **Blog.** Optional: publish Phase 1 writeup as proof-of-work.

---

## Off-Ramp Decisions

**If Phase 2 takes >4 months:**
- Reconsider FFI complexity. Subprocess-based tool is still useful.
- Defer Phase 2, ship Phase 1 on GitHub, call it "v0.5".

**If Phase 3 annotation writing fails:**
- Stick to overlay rendering (pixmap annotation, no PDF mutation).
- Useful for review/markup workflows.

**If Phase 4 text editing is infeasible:**
- Stop at Phase 3: "annotator + preview tool".
- Hire out text editing to separate tool (stay focused).

---

## Checkpoints (Monthly Check-ins)

### End of Week 2 (Phase 1 wrap)
- [ ] All Phase 1 criteria met?
- [ ] Subprocess overhead acceptable?
- [ ] Ready for Phase 2 FFI?

### End of Month 3 (Phase 2 wrap)
- [ ] FFI stable, no segfaults?
- [ ] Speedup measured and acceptable?
- [ ] Ready for Phase 3 rendering?

### End of Month 6 (Phase 3 wrap)
- [ ] Annotations work end-to-end?
- [ ] Search functional?
- [ ] Ready for Phase 4 text editing?

### End of Month 12 (v1 candidate)
- [ ] All features working?
- [ ] Performance acceptable?
- [ ] Ship or iterate?

---

## Resource Constraints

- **Time:** Assume 10–20 hrs/week (evenings/weekends).
- **RAM:** Rendering large PDFs = memory spike. Keep in mind.
- **Disk:** Store test corpus locally (~500 MB).

**Timeline adjustment:** If <10 hrs/week, add 50% to all estimates.

