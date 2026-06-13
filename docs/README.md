# 1. LinguAI documentation index

This directory holds detailed documentation that does not belong in the
top-level [`README.md`](../README.md). Read the project README first for
setup, architecture overview, and dev workflow; the documents below dig
into specific design decisions and historical context.

## 1.1. Why the folder is called `superpowers`

The documents under `superpowers/` were produced through the
[`superpowers`](https://github.com/anthropics/superpowers) workflow for
Claude Code — a brainstorming → spec → plan → execution discipline.
The folder name is preserved so the documents remain interpretable in
their original tooling context.

## 1.2. Specifications

Design specifications. These describe *intended* behaviour, including
the rationale behind architectural choices.

- [Frontend MVVM overhaul — design spec](superpowers/specs/2026-05-30-frontend-mvvm-overhaul-design.md)
  — The full design for replacing Streamlit with NiceGUI + VMx, with
  the MVVM contract, page-VM layout, and DI rules. **Status:** implemented
  in commit `67fa99c` on 2026-05-31. Where the spec's pseudo-code
  contradicts VMx's real API, [the VMx API quickref](superpowers/notes/vmx-api-quickref.md)
  is authoritative.

## 1.3. Plans

Step-by-step implementation plans associated with the specs above.

- [Frontend MVVM overhaul — plan](superpowers/plans/2026-05-30-frontend-mvvm-overhaul.md)
  — Phase-by-phase work breakdown that drove the migration. **Status:**
  completed (merged into `develop` via commit `67fa99c`). Hard-coded
  worktree paths in this document refer to the original implementation
  worktree; substitute your checkout root.

## 1.4. Notes

Reference material that doesn't fit "spec" or "plan" — quick-reference
guides, audits, and known-issue trackers.

- [VMx API quickref](superpowers/notes/vmx-api-quickref.md) — Concise
  cheat sheet for the consumer-facing VMx API as it actually behaves in
  the version vendored under `external/vmx/`. **This is the authoritative
  API reference** for VMx as used by LinguAI; prefer it over the design
  spec when the two disagree.
- [VMx upstream-improvement backlog](superpowers/notes/vmx-issues-report.md)
  — Known VMx pain points worth fixing upstream. Consumer-side workarounds
  applied in LinguAI are described inline in the frontend code.
- [Streamlit-vs-NiceGUI parity audit (2026-05-31)](superpowers/notes/old-vs-new-audit-2026-05-31.md)
  — Feature-by-feature comparison taken at cutover time, used to verify
  no Streamlit feature was silently dropped. References to local screenshots
  (`/tmp/audit-screenshots/`) are not committed.

## 1.5. Per-service documentation

- [`backend/README.md`](../backend/README.md) — Routes, services, sessions,
  and the SQLAlchemy/SQLModel migration caveats.
- [`frontend/README.md`](../frontend/README.md) — MVVM layering rules,
  page-VM lifecycle, and import-linter contracts.

## 1.6. Architecture diagram

The rendered architecture diagram lives at
[`images/linguai_system_architecture.jpg`](../images/linguai_system_architecture.jpg).
Its source is [`architecture.py`](../architecture.py) at the repository root.
Regeneration is a manual step (`pip install diagrams` + Graphviz, then
`python architecture.py`); see the docstring at the top of `architecture.py`.
