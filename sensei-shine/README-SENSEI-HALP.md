# Haskell PDF Editor: Design & Iteration Kit

**Version:** 0.1 | **Status:** Pre-Phase-1 | **Date:** 2025-03-29

This is a **problem domain + approach kit** for iterating on a personal-use PDF editor in Haskell. Use with `sensei-halp` (or manual co-exploration) to refine design before writing code.

---

## Files Overview

| File | Purpose | When to Use |
|------|---------|------------|
| **pdf-editor-domain.md** | Problem definition, constraints, non-goals | Start here. Read first, questions emerge. |
| **pdf-editor-approach.md** | Architecture, dependency story, FFI strategy | Understand *how* you'll build it. |
| **pdf-editor-roadmap.md** | Phases, milestones, timelines, gating conditions | Plan the work. Decide when to move forward. |
| **pdf-editor-questions.md** | Open questions, unknowns, spike work | Identify what needs research/discussion. |
| **pdf-editor-iteration.md** | Decision log (template + examples) | Log decisions as you make them. Audit trail. |
| **haskell-pdf.cabal** | Skeleton project file | Start cabal build from here. |

---

## How to Iterate with sensei-halp

### Round 1: Problem Domain Review (30 min)

1. Read **pdf-editor-domain.md** (5 min)
2. Raise questions or pushback:
   - "Why Phase 1 in 2 weeks? Too aggressive?"
   - "Missing any critical operations?"
   - "Non-goals seem right?"
3. Update domain doc with refined constraints.
4. **Checkpoint:** Domain is locked in. Non-goals are clear.

### Round 2: Approach & Architecture (60 min)

1. Read **pdf-editor-approach.md** (10 min)
2. Sanity-check the architecture:
   - "Will subprocess wrappers handle X operation?"
   - "FFI complexity realistic for month 2–3?"
   - "Missing dependencies?"
3. Iterate on decision checkpoints in **pdf-editor-questions.md**
4. **Checkpoint:** Architecture is approved. Decisions recorded in iteration.md.

### Round 3: Roadmap & Gating (45 min)

1. Read **pdf-editor-roadmap.md** (10 min)
2. Pressure-test timeline:
   - "Can you really do Phase 1 in 2 weeks?"
   - "What if X blocks FFI? Then what?"
   - "Off-ramps reasonable?"
3. Adjust effort estimates based on feedback.
4. **Checkpoint:** Roadmap is realistic. Off-ramps are clear.

### Round 4: Questions & Spikes (60 min)

1. Review **pdf-editor-questions.md** (10 min)
2. Prioritize unknowns:
   - "Which spike should I do first?"
   - "Which questions kill the project if wrong?"
3. Plan spike work (small experiments):
   - FFI toy binding (2 hours)
   - PDF content stream manual construction (2 hours)
   - CLI framework proof-of-concept (1 hour)
4. **Checkpoint:** High-risk unknowns are spiked. Confidence goes up.

### Round 5: Iteration Log (30 min)

1. As decisions are made (or deferred), add to **pdf-editor-iteration.md**
2. Use the template. Date every decision.
3. Link decisions to domain/roadmap implications.
4. **Checkpoint:** All Phase 1 decisions are logged.

---

## Workflow: Pre-Code Phase

**Timeline:** 1–2 weeks before writing code.

```
Day 1: Read all docs (1 hour). List questions.
       ↓
       Iteration 1: Domain refinement (sensei-halp, 30 min)
       ↓
Day 2: Read refined docs. List unknowns.
       ↓
       Iteration 2: Architecture Q&A (sensei-halp, 60 min)
       ↓
Day 3: Spike 1: FFI toy binding (2 hours)
       ↓
       Iteration 3: Spike results + roadmap (sensei-halp, 45 min)
       ↓
Day 4: Spike 2: PDF content stream (2 hours)
       ↓
       Iteration 4: Questions deep-dive (sensei-halp, 60 min)
       ↓
Day 5: All decisions logged in iteration.md
       ↓
       READY FOR CODE
```

---

## How sensei-halp Interacts

**Bring:** The specific doc + question.

**Example:**

> **You:** "Reading pdf-editor-approach.md. FFI strategy assumes mupdf is available on the system. But what if someone on Windows doesn't have mupdf? What's the fallback?"

> **sensei-halp:** "Good catch. Options:
> 1. Vendor mupdf (adds build complexity)
> 2. Provide prebuilt binaries on GitHub (maintenance burden)
> 3. Fall back to subprocess-only (slower, but works)
> 4. Windows-only: recommend WSL2 + Linux build
> 
> Which fits your personal-use scope?"

> **You:** "I'm on Linux. Users are me + maybe 1–2 friends. Fall back to subprocess is fine."

> **sensei-halp:** "Add that decision to pdf-editor-iteration.md (Decision: Windows FFI Support). Mark as deferred."

---

## Before Phase 1 Code

**Checklist:**

- [ ] Domain doc locked in. No scope creep.
- [ ] Approach reviewed. Architecture makes sense.
- [ ] Roadmap accepted. Timelines realistic.
- [ ] High-risk spikes done (FFI, PDF syntax). Confidence up.
- [ ] Phase 1 decisions all in iteration.md.
- [ ] cabal file is ready to build.

**Only then:** Start coding Phase 1.

---

## During Phase 1 (and beyond)

**Weekly checkpoint:**
- Update pdf-editor-iteration.md with new decisions.
- Link decisions to domain/roadmap changes (if any).
- Adjust timeline if needed (spikes took longer, or shorter).
- Note what went faster/slower than expected.

**Monthly review:**
- Reread relevant roadmap section.
- Check: still on track? Off-ramps triggered? Risk changed?
- Update all docs with learnings.

---

## Collaboration Pattern (with sensei-halp)

**Pattern: "Pressure test → Refine → Log"**

1. **Pressure Test:** Ask the hard question. Force yourself to justify.
2. **Refine:** Update the doc. Test again.
3. **Log:** Record the decision in iteration.md. Why this way?

Example:

```
You: "In pdf-editor-approach.md, Phase 2 FFI. Is 2–3 months realistic for FFI?"

sensei-halp: "Assuming you spend 20 hrs/week. Walk through:
- Week 1: Learn Haskell FFI (10 hrs, docs + toy example)
- Week 2: Bind 3 mupdf functions, test (10 hrs, tight)
- Week 3–4: Safe wrapper + bracket (20 hrs, careful)

Total: ~40 hours so far. Still 2 months out. ✓

But unknown: How long to debug segfaults? Assume 1 week buffer."

You: "OK, realistically 8–12 weeks. Update roadmap to 3 months."

→ Log in iteration.md: "Decision: FFI timeline = 3 months (40–50 hours)."
```

---

## File Diff Pattern (Git)

As you iterate:

```bash
# After each sensei-halp session:
git add pdf-editor-*.md haskell-pdf.cabal
git commit -m "Round 1: Domain refinement — added constraint on window size, updated non-goals"
```

This creates an audit trail of design evolution. Useful for:
- Understanding *why* decisions were made.
- Explaining the project to others.
- Identifying when scope changed.

---

## What "sensei-halp" Means

A **collaborative problem-solving partner** (could be Claude, could be a human, could be this system). The partner's job:

- Ask hard questions.
- Point out contradictions.
- Suggest alternatives you missed.
- Push back on timeline claims.
- Pressure-test assumptions.

The system's job:
- Provide clear, actionable docs.
- Record decisions.
- Integrate feedback into refined docs.
- Know when you're ready for code.

---

## Expected Outcome

After 1–2 weeks of iteration:

✅ You understand the problem domain (constraints, non-goals, friction points).
✅ You have an architecture you trust (subprocess + FFI strategy clear).
✅ You have a realistic roadmap (phases, timelines, off-ramps).
✅ You've spiked the high-risk unknowns (FFI, PDF syntax).
✅ All decisions are logged and justified.
✅ You're ready to `cabal init` and write Phase 1.

---

## Quick Start

1. Copy all files to a project directory.
2. Read **pdf-editor-domain.md** (skip intro, jump to constraints).
3. List your immediate questions (3–5).
4. Bring them to sensei-halp (or iterate solo).
5. After each round, update the docs and commit to git.

---

## References in Docs

- PDF 1.7 Spec: https://www.adobe.io/content/dam/udp/assets/open/pdf/spec/PDF32000_2008.pdf
- mupdf API: https://mupdf.com/docs/
- Haskell FFI: https://wiki.haskell.org/FFI
- optparse-applicative: https://hackage.haskell.org/package/optparse-applicative

---

**Version Control:** Update version field in each doc as you iterate. Dates track evolution.

**Questions?** Add to pdf-editor-questions.md under "Open Questions". Revisit each week.

