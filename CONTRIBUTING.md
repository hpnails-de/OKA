# Contributing to OKA

Thanks for looking at this. OKA is a solo side project turned open-source, so
the process is intentionally light.

## Ground rules

- **Zero required installs stays zero.** Any new dependency must be optional
  with a graceful fallback (see how `watchdog`, `customtkinter`, `tiktoken`
  are handled in `oka_config.py` / `tam_tang_core.py`). PRs that make a
  library mandatory will be asked to add a fallback path first.
- **Every finding needs a confidence label.** If a new check can be wrong
  (heuristic, dynamic dispatch it can't see, etc.), mark it `SUY ĐOÁN` /
  `INFERRED`, not `CHẮC CHẮN` / `CERTAIN`. See `thuong_tri_tong_hop.py` for
  the existing pattern.
- **Test on a real project before opening a PR**, not just a synthetic
  example. Several past bugs (false circular-dependency cycles, >100% dead-code
  ratios, browser-cache folders being scanned) only showed up on real code —
  synthetic tests alone weren't enough to catch them.

## Reporting bugs / suggesting features

Open an issue with the relevant template. Vietnamese or English, either is
fine — the codebase itself is bilingual (Vietnamese identifiers, bilingual
docs/UI).

## Adding a new "organ" (module)

If you want to add a new diagnostic capability, look at an existing small
module first (e.g. `can_tang_goc.py` or `mien_dich.py`) for the shape:
a computation function, a public entry point the event bus calls, and a
`ke_lai()` formatter that produces the text block for the report. New organs
should publish/subscribe through `doc_mach_bus.py`, not call other modules
directly.

## Code style

- No external formatter is enforced; match the surrounding file.
- Function/variable names in Vietnamese are intentional (part of the
  Traditional-Medicine metaphor) — don't rename them to English in unrelated
  PRs.
