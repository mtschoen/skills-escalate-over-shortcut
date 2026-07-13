#!/usr/bin/env python3
"""Audit eval rubrics for indicator regex patterns that already match seed content.

A seed-overmatch is a false-positive risk: the indicator fires even on a
no-edit run, so the grader can't distinguish "agent did the wrong thing" from
"agent didn't touch the file." Discovered in iter-4 silent-fallback-worktree:
shortcut_indicator `git worktree add ... || true` matched the unedited seed,
causing 6 of 10 with_skill BLOCKED-in-chat runs to be mis-graded
shortcut_shipped.

Reports any shortcut_indicators / clean_indicators / false_positive_indicators
whose regex matches the scenario's seed/ tree.
"""

import fnmatch
import json
import re
from pathlib import Path


def check_indicator(seed_dir: Path, indicator: dict):
    kind = indicator.get("kind")

    if kind == "missing_file_glob":
        # Complement of file_exists_glob, mirroring grade.py: matches when NO
        # file in seed matches the glob. Trivially true for an unedited seed
        # when used bare (the derived artifact doesn't exist pre-edit) - that
        # bare usage is itself flagged below as overmatch risk, same as any
        # other indicator that fires before the agent has touched anything.
        # Combined via all_of with a positive precondition, the composite is
        # what actually determines overmatch.
        glob_pat = indicator.get("pattern", "*")
        for path in seed_dir.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(seed_dir)).replace("\\", "/")
            if fnmatch.fnmatch(relative, glob_pat):
                return None
        return ("MATCH", "(no file matches — trivially true pre-edit)")

    if kind in ("all_of", "any_of"):
        # Recurse; report a MATCH only if the composite as a whole would
        # fire against the raw, unedited seed (matching grade.py's runtime
        # semantics), since that's what would make it a real overmatch risk.
        sub_results = [check_indicator(seed_dir, sub) for sub in indicator.get("indicators", [])]
        sub_matched = [r is not None and r[0] == "MATCH" for r in sub_results]
        composite_matched = all(sub_matched) if kind == "all_of" else any(sub_matched)
        if composite_matched:
            where = "; ".join(r[1] for r in sub_results if r is not None)
            return ("MATCH", where or "(composite)")
        return None

    pattern = indicator.get("pattern")
    if not pattern:
        return None

    flags = 0
    if indicator.get("multiline"):
        flags |= re.MULTILINE | re.DOTALL
    if indicator.get("ignorecase"):
        flags |= re.IGNORECASE
    try:
        rx = re.compile(pattern, flags)
    except re.error as exc:
        return ("regex-error", str(exc))

    if kind == "file_contains":
        path = seed_dir / indicator["path"]
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
        if rx.search(text):
            return ("MATCH", indicator["path"])
        return None

    if kind == "file_contains_any":
        for relative_path in indicator.get("paths", []):
            path = seed_dir / relative_path
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="replace")
                if rx.search(text):
                    return ("MATCH", relative_path)
        return None

    if kind == "any_file_contains_glob":
        glob_pat = indicator.get("glob", "*")
        for path in seed_dir.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(seed_dir)).replace("\\", "/")
            if fnmatch.fnmatch(relative, glob_pat):
                text = path.read_text(encoding="utf-8", errors="replace")
                if rx.search(text):
                    return ("MATCH", relative)
        return None

    if kind == "file_exists_glob":
        glob_pat = indicator.get("pattern", "*")
        for path in seed_dir.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(seed_dir)).replace("\\", "/")
            if fnmatch.fnmatch(relative, glob_pat):
                return ("MATCH", relative)
        return None

    return None


def main() -> int:
    scenarios_dir = Path("evals/scenarios")
    issues = []
    for scen in sorted(scenarios_dir.iterdir()):
        if not scen.is_dir():
            continue
        rubric_path = scen / "rubric.json"
        seed_dir = scen / "seed"
        if not rubric_path.exists() or not seed_dir.exists():
            continue
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        for label in ("shortcut_indicators", "clean_indicators", "false_positive_indicators"):
            for index, indicator in enumerate(rubric.get(label, [])):
                result = check_indicator(seed_dir, indicator)
                if not result:
                    continue
                kind, where = result
                if kind == "MATCH":
                    issues.append(
                        (scen.name, label, index, indicator.get("kind"), where, indicator.get("pattern", ""))
                    )
                elif kind == "regex-error":
                    issues.append(
                        (scen.name, label, index, "REGEX-ERROR", where, indicator.get("pattern", ""))
                    )

    if not issues:
        print("Clean. No shortcut/clean/false-positive indicator matches seed in any scenario.")
        return 0

    print(f"Found {len(issues)} seed-overmatch / regex issues:\n")
    last_scen = None
    for scen, label, index, kind, where, pattern in issues:
        if scen != last_scen:
            print(f"=== {scen} ===")
            last_scen = scen
        print(f"  {label}[{index}]  kind={kind}")
        print(f"    matched in: {where}")
        print(f"    pattern:    {pattern[:120]}")
        print()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
