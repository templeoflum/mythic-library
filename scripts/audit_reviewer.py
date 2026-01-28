#!/usr/bin/env python3
"""
ACP v2 Validation Suite — Human Audit Reviewer

Interactive terminal walkthrough for reviewing 40 human audit cases.
Displays archetype pairs with coordinates and distances, collects
reviewer judgments, tracks progress with resume support.

Usage:
    python audit_reviewer.py              # Start / resume review
    python audit_reviewer.py --status     # Show current progress
    python audit_reviewer.py --reset      # Clear all progress
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

class C:
    """ANSI escape-code palette."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    ULINE   = "\033[4m"

    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"

    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"


def styled(text, *codes):
    return "".join(codes) + str(text) + C.RESET


def hr(char="\u2500", width=72):
    return styled(char * width, C.DIM)


def header_bar(text, width=72):
    pad = width - len(text) - 4
    left = pad // 2
    right = pad - left
    return styled(
        f"\u2550{'=' * left} {text} {'=' * right}\u2550",
        C.BOLD, C.CYAN
    )


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_PATH   = PROJECT_ROOT / "outputs" / "audits" / "human_audit_cases.json"
RESULTS_PATH = PROJECT_ROOT / "outputs" / "audits" / "human_audit_results.json"

AXIS_LABELS = [
    "order-chaos",
    "creation-destruction",
    "light-shadow",
    "active-receptive",
    "individual-collective",
    "ascent-descent",
    "stasis-transformation",
    "voluntary-fated",
]

AXIS_SHORT = {
    "order-chaos":            "Ord-Cha",
    "creation-destruction":   "Cre-Des",
    "light-shadow":           "Lig-Sha",
    "active-receptive":       "Act-Rec",
    "individual-collective":  "Ind-Col",
    "ascent-descent":         "Asc-Des",
    "stasis-transformation":  "Sta-Tra",
    "voluntary-fated":        "Vol-Fat",
}

CATEGORY_COLORS = {
    "CULTURAL_ECHO":          C.BRIGHT_MAGENTA,
    "POLAR_OPPOSITE":         C.BRIGHT_RED,
    "COMPLEMENT":             C.BRIGHT_BLUE,
    "NEAREST_NEIGHBOR":       C.BRIGHT_GREEN,
    "DISTANT_SAME_PRIMORDIAL": C.BRIGHT_YELLOW,
}


def category_key(raw_category: str) -> str:
    """Extract the base category key (before any parenthetical)."""
    return raw_category.split("(")[0].strip()


def color_for(raw_category: str) -> str:
    key = category_key(raw_category)
    return CATEGORY_COLORS.get(key, C.WHITE)


# ---------------------------------------------------------------------------
# Data I/O
# ---------------------------------------------------------------------------

def load_cases() -> dict:
    if not CASES_PATH.exists():
        print(styled(f"ERROR: Cases file not found at {CASES_PATH}", C.RED, C.BOLD))
        sys.exit(1)
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_results() -> dict | None:
    if RESULTS_PATH.exists():
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_results(results: dict):
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def init_results(cases_data: dict) -> dict:
    """Create a fresh results structure from the source cases."""
    return {
        "n_cases": cases_data["n_cases"],
        "cases_by_category": cases_data["cases_by_category"],
        "started": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "reviews": [
            {
                "case_index": i,
                "category": case["category"],
                "claim": case["claim"],
                "source_id": case["source"]["id"],
                "source_name": case["source"]["name"],
                "target_id": case["target"]["id"],
                "target_name": case["target"]["name"],
                "distance_8d": case["distance_8d"],
                "judgment": None,
                "notes": "",
            }
            for i, case in enumerate(cases_data["cases"])
        ],
    }


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def display_archetype(label: str, arch: dict, label_color: str):
    name = arch.get("name", "?")
    aid  = arch.get("id", "?")
    desc = arch.get("description", "") or "(no description)"
    coords = arch.get("coordinates", {})

    print(f"  {styled(label, C.BOLD, label_color)}")
    print(f"    {styled('Name:', C.BOLD)} {styled(name, C.WHITE)}")
    print(f"    {styled('ID:',   C.BOLD)} {styled(aid,  C.DIM)}")
    if desc and desc != "(no description)":
        # Wrap long descriptions
        words = desc.split()
        lines = []
        line = ""
        for w in words:
            if len(line) + len(w) + 1 > 58:
                lines.append(line)
                line = w
            else:
                line = f"{line} {w}" if line else w
        if line:
            lines.append(line)
        print(f"    {styled('Desc:', C.BOLD)} {styled(lines[0], C.DIM, C.ITALIC)}")
        for extra in lines[1:]:
            print(f"          {styled(extra, C.DIM, C.ITALIC)}")
    else:
        print(f"    {styled('Desc:', C.BOLD)} {styled(desc, C.DIM, C.ITALIC)}")

    # Coordinates bar
    print(f"    {styled('Coordinates:', C.BOLD)}")
    for axis in AXIS_LABELS:
        val = coords.get(axis, 0)
        bar_len = int(val * 20)
        bar = "\u2588" * bar_len + "\u2591" * (20 - bar_len)
        axis_label = AXIS_SHORT.get(axis, axis)
        print(f"      {styled(axis_label + ':', C.DIM):>22s} {styled(bar, C.CYAN)} {styled(f'{val:.2f}', C.WHITE)}")


def display_distances(case: dict):
    dist = case.get("distance_8d", 0)
    diffs = case.get("per_axis_difference", {})

    # Distance color coding
    if dist < 0.15:
        dist_color = C.BRIGHT_GREEN
    elif dist < 0.30:
        dist_color = C.BRIGHT_YELLOW
    elif dist < 0.50:
        dist_color = C.YELLOW
    else:
        dist_color = C.BRIGHT_RED

    print(f"\n  {styled('8D Euclidean Distance:', C.BOLD)} {styled(f'{dist:.4f}', C.BOLD, dist_color)}")
    print(f"  {styled('Per-Axis Differences:', C.BOLD)}")

    for axis in AXIS_LABELS:
        d = diffs.get(axis, 0)
        if d < 0.05:
            dc = C.BRIGHT_GREEN
        elif d < 0.15:
            dc = C.BRIGHT_YELLOW
        elif d < 0.25:
            dc = C.YELLOW
        else:
            dc = C.BRIGHT_RED
        bar_len = int(min(d, 1.0) * 30)
        bar = "\u2593" * bar_len + "\u2591" * (30 - bar_len)
        axis_label = AXIS_SHORT.get(axis, axis)
        print(f"    {styled(axis_label + ':', C.DIM):>22s} {styled(bar, dc)} {styled(f'{d:.2f}', dc)}")


def display_case(index: int, total: int, case: dict):
    cat = case["category"]
    cat_color = color_for(cat)

    print("\n" + header_bar(f"Case {index + 1} / {total}"))
    print()
    print(f"  {styled('Category:', C.BOLD)} {styled(cat, C.BOLD, cat_color)}")
    print(f"  {styled('Claim:',    C.BOLD)} {styled(case['claim'], C.WHITE, C.ITALIC)}")

    if case.get("fidelity") is not None and "CULTURAL_ECHO" in cat:
        fid = case["fidelity"]
        if fid >= 0.9:
            fc = C.BRIGHT_GREEN
        elif fid >= 0.8:
            fc = C.BRIGHT_YELLOW
        else:
            fc = C.YELLOW
        print(f"  {styled('Fidelity:', C.BOLD)}  {styled(f'{fid:.2f}', C.BOLD, fc)}")

    print()
    print(hr())
    display_archetype("SOURCE", case["source"], C.BRIGHT_CYAN)
    print()
    display_archetype("TARGET", case["target"], C.BRIGHT_MAGENTA)
    print()
    print(hr())
    display_distances(case)
    print(hr())


# ---------------------------------------------------------------------------
# Progress / summary
# ---------------------------------------------------------------------------

def compute_stats(results: dict) -> dict:
    reviews = results["reviews"]
    total = len(reviews)
    reviewed = [r for r in reviews if r["judgment"] is not None]
    skipped  = [r for r in reviews if r["judgment"] == "skip"]
    judged   = [r for r in reviews if r["judgment"] in ("agree", "disagree", "unsure")]

    by_cat = {}
    for r in reviews:
        cat_key = category_key(r["category"])
        if cat_key not in by_cat:
            by_cat[cat_key] = {"agree": 0, "disagree": 0, "unsure": 0, "skip": 0, "pending": 0}
        j = r["judgment"]
        if j is None:
            by_cat[cat_key]["pending"] += 1
        else:
            by_cat[cat_key][j] += 1

    agree_count = sum(1 for r in judged if r["judgment"] == "agree")
    agreement_rate = (agree_count / len(judged) * 100) if judged else 0.0

    return {
        "total": total,
        "reviewed": len(reviewed),
        "skipped": len(skipped),
        "judged": len(judged),
        "agree_count": agree_count,
        "agreement_rate": agreement_rate,
        "by_category": by_cat,
    }


def display_summary(results: dict):
    stats = compute_stats(results)
    total = stats["total"]
    reviewed = stats["reviewed"]

    print("\n" + header_bar("Review Summary"))
    print()
    pct = reviewed / total * 100 if total else 0
    bar_len = int(pct / 100 * 40)
    bar = styled("\u2588" * bar_len, C.GREEN) + styled("\u2591" * (40 - bar_len), C.DIM)
    print(f"  {styled('Progress:', C.BOLD)} [{bar}] {styled(f'{reviewed}/{total}', C.WHITE)} ({pct:.0f}%)")
    print()

    # Per-category table
    print(f"  {styled('Category', C.BOLD, C.ULINE):<44s}"
          f" {styled('Agree', C.BOLD, C.GREEN):>16s}"
          f" {styled('Disagree', C.BOLD, C.RED):>19s}"
          f" {styled('Unsure', C.BOLD, C.YELLOW):>17s}"
          f" {styled('Skip', C.BOLD, C.DIM):>15s}"
          f" {styled('Pending', C.BOLD, C.BRIGHT_BLACK):>18s}")

    for cat_key, counts in stats["by_category"].items():
        cat_color = CATEGORY_COLORS.get(cat_key, C.WHITE)
        a = counts["agree"]
        d = counts["disagree"]
        u = counts["unsure"]
        s = counts["skip"]
        p = counts["pending"]
        print(f"  {styled(cat_key, cat_color):<35s}"
              f" {styled(a, C.GREEN):>7s}"
              f" {styled(d, C.RED):>10s}"
              f" {styled(u, C.YELLOW):>8s}"
              f" {styled(s, C.DIM):>6s}"
              f" {styled(p, C.BRIGHT_BLACK):>9s}")

    print()
    print(f"  {styled('Overall Agreement Rate:', C.BOLD)} ", end="")
    if stats["judged"] > 0:
        rate = stats["agreement_rate"]
        if rate >= 80:
            rc = C.BRIGHT_GREEN
        elif rate >= 60:
            rc = C.BRIGHT_YELLOW
        else:
            rc = C.BRIGHT_RED
        agree_n = stats["agree_count"]
        judged_n = stats["judged"]
        print(f"{styled(f'{rate:.1f}%', C.BOLD, rc)}  "
              f"{styled(f'({agree_n}/{judged_n} judged cases)', C.DIM)}")
    else:
        print(styled("No judged cases yet.", C.DIM))

    print(hr())
    print()


def show_status(results: dict | None):
    """Print status without entering review mode."""
    print("\n" + header_bar("ACP v2 Audit Review Status"))

    if results is None:
        print(f"\n  {styled('No review session found.', C.DIM)}")
        print(f"  Run without --status to begin reviewing.\n")
        return

    display_summary(results)

    # Show first pending case number
    reviews = results["reviews"]
    for i, r in enumerate(reviews):
        if r["judgment"] is None:
            print(f"  {styled('Next unreviewed case:', C.BOLD)} #{i + 1}")
            break
    else:
        print(f"  {styled('All cases reviewed!', C.BOLD, C.GREEN)}")
    print()


# ---------------------------------------------------------------------------
# Interactive review loop
# ---------------------------------------------------------------------------

VALID_JUDGMENTS = {
    "a": "agree",
    "d": "disagree",
    "u": "unsure",
    "s": "skip",
}


def prompt_judgment() -> str | None:
    """Prompt for judgment. Returns judgment string or None for quit."""
    print()
    print(f"  {styled('[A]', C.BOLD, C.GREEN)}gree   "
          f"{styled('[D]', C.BOLD, C.RED)}isagree   "
          f"{styled('[U]', C.BOLD, C.YELLOW)}nsure   "
          f"{styled('[S]', C.BOLD, C.DIM)}kip   "
          f"{styled('[Q]', C.BOLD, C.BRIGHT_RED)}uit")
    print()

    while True:
        try:
            raw = input(f"  {styled('>', C.BOLD, C.CYAN)} Judgment: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if not raw:
            continue
        if raw[0] == "q":
            return None
        if raw[0] in VALID_JUDGMENTS:
            return VALID_JUDGMENTS[raw[0]]
        print(f"    {styled('Invalid input. Use A / D / U / S / Q.', C.RED)}")


def prompt_notes() -> str:
    """Optionally collect reviewer notes."""
    try:
        raw = input(f"  {styled('>', C.BOLD, C.CYAN)} Notes (Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""
    return raw


def find_next_pending(results: dict, start: int = 0) -> int | None:
    """Find the next case without a judgment, starting from `start`."""
    reviews = results["reviews"]
    for i in range(start, len(reviews)):
        if reviews[i]["judgment"] is None:
            return i
    return None


def run_review(cases_data: dict, results: dict):
    total = cases_data["n_cases"]
    cases = cases_data["cases"]

    idx = find_next_pending(results)
    if idx is None:
        print(f"\n  {styled('All cases have been reviewed!', C.BOLD, C.GREEN)}")
        display_summary(results)
        return

    reviewed_now = 0

    print(f"\n  {styled('Resuming from case', C.DIM)} {styled(idx + 1, C.BOLD, C.WHITE)}"
          f" {styled(f'of {total}', C.DIM)}")

    while idx is not None and idx < total:
        case = cases[idx]
        display_case(idx, total, case)

        judgment = prompt_judgment()
        if judgment is None:
            # Quit
            print(f"\n  {styled('Saving progress...', C.DIM)}")
            results["last_updated"] = datetime.now().isoformat()
            save_results(results)
            print(f"  {styled('Progress saved.', C.GREEN)} "
                  f"Reviewed {styled(reviewed_now, C.BOLD)} case(s) this session.\n")
            display_summary(results)
            return

        notes = prompt_notes()

        results["reviews"][idx]["judgment"] = judgment
        results["reviews"][idx]["notes"] = notes
        results["last_updated"] = datetime.now().isoformat()

        # Auto-save after every judgment
        save_results(results)
        reviewed_now += 1

        jc = {
            "agree":    C.GREEN,
            "disagree": C.RED,
            "unsure":   C.YELLOW,
            "skip":     C.DIM,
        }
        print(f"\n  {styled('Recorded:', C.DIM)} {styled(judgment.upper(), C.BOLD, jc.get(judgment, C.WHITE))}"
              + (f"  {styled('Note:', C.DIM)} {notes}" if notes else ""))

        # Advance to next pending
        idx = find_next_pending(results, idx + 1)

    # All done
    print(f"\n  {styled('All cases reviewed!', C.BOLD, C.GREEN)}")
    results["last_updated"] = datetime.now().isoformat()
    save_results(results)
    display_summary(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Enable ANSI escapes and UTF-8 output on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
        # Force UTF-8 output so box-drawing / block characters render
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="ACP v2 Validation Suite -- Human Audit Reviewer"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show current review progress without entering review mode"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Clear all progress and start fresh"
    )
    args = parser.parse_args()

    # Banner
    print()
    print(styled("  ╔══════════════════════════════════════════════════════════╗", C.BOLD, C.CYAN))
    print(styled("  ║", C.BOLD, C.CYAN)
          + styled("   ACP v2 Validation Suite  —  Human Audit Reviewer    ", C.BOLD, C.WHITE)
          + styled("║", C.BOLD, C.CYAN))
    print(styled("  ╚══════════════════════════════════════════════════════════╝", C.BOLD, C.CYAN))

    # Handle --reset
    if args.reset:
        if RESULTS_PATH.exists():
            RESULTS_PATH.unlink()
            print(f"\n  {styled('Progress cleared.', C.GREEN)} Results file removed.")
        else:
            print(f"\n  {styled('No progress file found. Nothing to reset.', C.DIM)}")
        print()
        return

    # Handle --status
    if args.status:
        results = load_results()
        show_status(results)
        return

    # Normal review mode
    cases_data = load_cases()
    total = cases_data["n_cases"]
    print(f"\n  {styled('Cases file:', C.DIM)}  {CASES_PATH}")
    print(f"  {styled('Results file:', C.DIM)} {RESULTS_PATH}")
    print(f"  {styled('Total cases:', C.DIM)}  {styled(total, C.BOLD)}")

    cats = cases_data.get("cases_by_category", {})
    for cat_name, cnt in cats.items():
        cc = CATEGORY_COLORS.get(cat_name, C.WHITE)
        print(f"    {styled(cat_name, cc)}: {cnt}")

    # Load or initialise results
    results = load_results()
    if results is None or len(results.get("reviews", [])) != total:
        results = init_results(cases_data)
        save_results(results)
        print(f"\n  {styled('Initialised fresh review session.', C.GREEN)}")
    else:
        done = sum(1 for r in results["reviews"] if r["judgment"] is not None)
        print(f"\n  {styled('Existing session found.', C.CYAN)} {styled(done, C.BOLD)}/{total} reviewed.")

    print()
    run_review(cases_data, results)


if __name__ == "__main__":
    main()
