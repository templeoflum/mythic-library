#!/usr/bin/env python3
"""
fix_polar_coordinates.py

Identifies POLAR_OPPOSITE pairs where the axis diff < 0.55 and applies
minimal symmetric coordinate adjustments to bring the diff to >= 0.55.

Constraints:
  - Max shift per dimension per archetype: 0.15
  - Coordinates must stay in [0.0, 1.0]
  - Adjustments are symmetric (push both archetypes away from each other)
  - Pairs that cannot be fixed within constraints are skipped and reported

Usage (from project root):
    python validation/fix_polar_coordinates.py
    python validation/fix_polar_coordinates.py --dry-run
"""

import json
import os
import sys
import copy
import argparse
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The 8 spectral axes as they appear in the .jsonld files (hyphenated keys)
AXES = [
    "order-chaos",
    "creation-destruction",
    "light-shadow",
    "active-receptive",
    "individual-collective",
    "ascent-descent",
    "stasis-transformation",
    "voluntary-fated",
]

# Mapping from "axis:some-name" reference strings to the coordinate key
# In relationship objects, the axis is sometimes stored as "axis:order-chaos"
# and sometimes as just "order-chaos". We normalise both.
def normalise_axis(axis_str):
    """Strip 'axis:' prefix if present."""
    if axis_str and axis_str.startswith("axis:"):
        return axis_str[len("axis:"):]
    return axis_str


# Threshold and target
THRESHOLD = 0.55        # pairs must have diff >= this
MAX_SHIFT = 0.15        # max coordinate shift per archetype per dimension
COORD_MIN = 0.0
COORD_MAX = 1.0


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def find_project_root():
    """Return the project root (directory containing ACP/)."""
    # Try the script's parent's parent first
    script_dir = Path(__file__).resolve().parent          # validation/
    candidate = script_dir.parent                          # project root
    if (candidate / "ACP").is_dir():
        return candidate
    # Fallback: current working directory
    cwd = Path.cwd()
    if (cwd / "ACP").is_dir():
        return cwd
    raise FileNotFoundError(
        "Cannot find project root (directory containing ACP/). "
        "Run this script from the project root or from validation/."
    )


def discover_jsonld_files(root):
    """Return a list of all .jsonld files under ACP/."""
    acp_dir = root / "ACP"
    return sorted(acp_dir.rglob("*.jsonld"))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_jsonld(path):
    """Load a .jsonld file and return its parsed JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_entries(data):
    """
    Yield (entry, parent_data) for every entry-like object in a .jsonld file.
    Handles files with a top-level 'entries' array as well as files that are
    themselves a single entry.
    """
    if isinstance(data, dict):
        if "entries" in data and isinstance(data["entries"], list):
            for entry in data["entries"]:
                yield entry
        elif "@id" in data and "spectralCoordinates" in data:
            yield data
    elif isinstance(data, list):
        for item in data:
            yield from extract_entries(item)


# ---------------------------------------------------------------------------
# Build index of all archetypes (by @id)
# ---------------------------------------------------------------------------

def build_archetype_index(root):
    """
    Scan all .jsonld files.  Return:
      archetype_index : dict  @id -> { 'entry': dict, 'file': Path }
      file_data       : dict  Path -> parsed JSON (for later write-back)
    """
    archetype_index = {}
    file_data = {}

    for path in discover_jsonld_files(root):
        try:
            data = load_jsonld(path)
        except Exception as e:
            print(f"  [WARN] Could not parse {path}: {e}")
            continue
        file_data[path] = data

        for entry in extract_entries(data):
            eid = entry.get("@id")
            if eid and "spectralCoordinates" in entry:
                archetype_index[eid] = {
                    "entry": entry,
                    "file": path,
                }

    return archetype_index, file_data


# ---------------------------------------------------------------------------
# Find all POLAR_OPPOSITE relationships
# ---------------------------------------------------------------------------

def find_polar_pairs(archetype_index):
    """
    Yield unique (source_id, target_id, axis_key) tuples for every
    POLAR_OPPOSITE relationship declared in the dataset.
    We de-duplicate by keeping the pair with the smaller source_id first.
    """
    seen = set()
    for eid, rec in archetype_index.items():
        entry = rec["entry"]
        rels = entry.get("relationships", [])
        for rel in rels:
            if rel.get("type") != "POLAR_OPPOSITE":
                continue
            target = rel.get("target")
            axis_raw = rel.get("axis")
            if not target or not axis_raw:
                continue
            axis = normalise_axis(axis_raw)
            if axis not in AXES:
                print(f"  [WARN] Unknown axis '{axis}' in relationship "
                      f"{eid} -> {target}. Skipping.")
                continue

            pair_key = tuple(sorted([eid, target])) + (axis,)
            if pair_key in seen:
                continue
            seen.add(pair_key)
            yield eid, target, axis


# ---------------------------------------------------------------------------
# Compute and apply adjustment
# ---------------------------------------------------------------------------

def compute_adjustment(val_a, val_b, axis, threshold=THRESHOLD, max_shift=MAX_SHIFT):
    """
    Given two coordinate values on the same axis for a POLAR_OPPOSITE pair,
    compute the symmetric shifts needed to make |val_a - val_b| >= threshold.

    For polar opposites, one archetype should be near 0 and the other near 1,
    so we push them apart symmetrically.

    Returns:
        (shift_a, shift_b, achievable) where shift_a/shift_b are the signed
        shifts to apply, and achievable is True if the target diff is reached.
    """
    current_diff = abs(val_a - val_b)
    if current_diff >= threshold:
        return 0.0, 0.0, True

    needed = threshold - current_diff  # total extra separation needed

    # Determine which direction to push each archetype.
    # Push them apart: lower value goes lower, higher value goes higher.
    if val_a <= val_b:
        low_val, high_val = val_a, val_b
        a_is_low = True
    else:
        low_val, high_val = val_b, val_a
        a_is_low = False

    # Ideal: split needed/2 to each side
    half_needed = needed / 2.0

    # How much room each side has
    room_low = low_val - COORD_MIN         # can go down by this much
    room_high = COORD_MAX - high_val       # can go up by this much

    # Effective shift per side (clamped by max_shift and room)
    shift_low = min(half_needed, max_shift, room_low)
    shift_high = min(half_needed, max_shift, room_high)

    # If one side is limited, try to compensate with the other
    remaining_after_low = half_needed - shift_low
    remaining_after_high = half_needed - shift_high

    if remaining_after_low > 0:
        # Low side couldn't shift enough, give extra to high side
        extra = min(remaining_after_low, max_shift - shift_high, room_high - shift_high)
        shift_high += max(0, extra)

    if remaining_after_high > 0:
        # High side couldn't shift enough, give extra to low side
        extra = min(remaining_after_high, max_shift - shift_low, room_low - shift_low)
        shift_low += max(0, extra)

    total_shift = shift_low + shift_high
    achievable = (current_diff + total_shift) >= threshold

    # Build signed shifts for a and b
    if a_is_low:
        sa = -shift_low
        sb = +shift_high
    else:
        sa = +shift_high
        sb = -shift_low

    return sa, sb, achievable


def apply_shift(entry, axis, shift):
    """Apply a signed shift to one axis of an entry's spectralCoordinates."""
    coords = entry["spectralCoordinates"]
    old_val = coords[axis]
    new_val = round(max(COORD_MIN, min(COORD_MAX, old_val + shift)), 4)
    # Clean up floating-point: round to 2 decimal places (matching data style)
    new_val = round(new_val, 2)
    coords[axis] = new_val
    return old_val, new_val


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fix POLAR_OPPOSITE pairs with insufficient axis separation."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing files.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=THRESHOLD,
        help=f"Minimum axis diff required (default {THRESHOLD}).",
    )
    parser.add_argument(
        "--max-shift",
        type=float,
        default=MAX_SHIFT,
        help=f"Max coordinate shift per archetype per dimension (default {MAX_SHIFT}).",
    )
    args = parser.parse_args()
    threshold = args.threshold
    max_shift = args.max_shift

    print("=" * 70)
    print("  POLAR OPPOSITE COORDINATE RECALIBRATION")
    print("=" * 70)

    # --- Locate project root ---
    root = find_project_root()
    print(f"\nProject root : {root}")

    # --- Build index ---
    print("\nScanning .jsonld files ...")
    arch_index, file_data = build_archetype_index(root)
    print(f"  Found {len(arch_index)} archetypes with spectral coordinates")
    print(f"  Across {len(file_data)} .jsonld files")

    # --- Find POLAR_OPPOSITE pairs ---
    print(f"\nFinding POLAR_OPPOSITE pairs with diff < {threshold} ...")
    pairs = list(find_polar_pairs(arch_index))
    print(f"  Total POLAR_OPPOSITE pairs found: {len(pairs)}")

    # Classify pairs
    failing = []
    passing = []
    missing_target = []

    for src_id, tgt_id, axis in pairs:
        if src_id not in arch_index:
            missing_target.append((src_id, tgt_id, axis, "source not found"))
            continue
        if tgt_id not in arch_index:
            missing_target.append((src_id, tgt_id, axis, "target not found"))
            continue

        src_coords = arch_index[src_id]["entry"]["spectralCoordinates"]
        tgt_coords = arch_index[tgt_id]["entry"]["spectralCoordinates"]

        if axis not in src_coords or axis not in tgt_coords:
            missing_target.append((src_id, tgt_id, axis, "axis key missing in coordinates"))
            continue

        diff = abs(src_coords[axis] - tgt_coords[axis])
        if diff < threshold:
            failing.append((src_id, tgt_id, axis, diff))
        else:
            passing.append((src_id, tgt_id, axis, diff))

    if missing_target:
        print(f"\n  [WARN] {len(missing_target)} pairs skipped (missing data):")
        for s, t, a, reason in missing_target:
            print(f"    {s} <-> {t} on {a}: {reason}")

    print(f"\n  Passing (diff >= {threshold}): {len(passing)}")
    print(f"  Failing (diff <  {threshold}): {len(failing)}")

    if not failing:
        print("\n  All POLAR_OPPOSITE pairs pass! Nothing to fix.")
        return

    # --- Sort failing by diff (ascending = worst first) ---
    failing.sort(key=lambda x: x[3])

    print(f"\n{'='*70}")
    print("  FAILING PAIRS (sorted by diff, worst first)")
    print(f"{'='*70}")
    for src_id, tgt_id, axis, diff in failing:
        src_name = arch_index[src_id]["entry"].get("name", src_id)
        tgt_name = arch_index[tgt_id]["entry"].get("name", tgt_id)
        needed = threshold - diff
        print(f"  {src_name:30s} <-> {tgt_name:30s}  axis={axis:25s}  "
              f"diff={diff:.3f}  need={needed:.3f}")

    # --- Compute and apply adjustments ---
    log_entries = []
    fixed_pairs = []
    skipped_pairs = []
    modified_files = set()

    print(f"\n{'='*70}")
    print("  COMPUTING ADJUSTMENTS")
    print(f"{'='*70}")

    for src_id, tgt_id, axis, diff in failing:
        src_entry = arch_index[src_id]["entry"]
        tgt_entry = arch_index[tgt_id]["entry"]
        src_name = src_entry.get("name", src_id)
        tgt_name = tgt_entry.get("name", tgt_id)

        val_a = src_entry["spectralCoordinates"][axis]
        val_b = tgt_entry["spectralCoordinates"][axis]

        shift_a, shift_b, achievable = compute_adjustment(
            val_a, val_b, axis, threshold=threshold, max_shift=max_shift
        )

        new_diff = abs((val_a + shift_a) - (val_b + shift_b))

        log_entry = {
            "pair": [src_id, tgt_id],
            "names": [src_name, tgt_name],
            "axis": axis,
            "original_values": [val_a, val_b],
            "original_diff": round(diff, 4),
            "needed_increase": round(threshold - diff, 4),
            "shifts": [round(shift_a, 4), round(shift_b, 4)],
            "new_values": [
                round(max(COORD_MIN, min(COORD_MAX, val_a + shift_a)), 2),
                round(max(COORD_MIN, min(COORD_MAX, val_b + shift_b)), 2),
            ],
            "new_diff": round(new_diff, 4),
            "achievable": achievable,
            "applied": False,
        }

        if not achievable:
            max_possible = abs(shift_a) + abs(shift_b)
            print(f"\n  SKIP  {src_name} <-> {tgt_name}")
            print(f"         axis={axis}  diff={diff:.3f}  "
                  f"need={threshold - diff:.3f}  "
                  f"max_achievable={max_possible:.3f}")
            print(f"         Cannot reach threshold within constraints.")
            skipped_pairs.append(log_entry)
            log_entries.append(log_entry)
            continue

        # Apply shifts
        if not args.dry_run:
            old_a, new_a = apply_shift(src_entry, axis, shift_a)
            old_b, new_b = apply_shift(tgt_entry, axis, shift_b)
            log_entry["applied"] = True

            modified_files.add(arch_index[src_id]["file"])
            modified_files.add(arch_index[tgt_id]["file"])

            print(f"\n  FIXED {src_name} <-> {tgt_name}")
            print(f"         axis={axis}")
            print(f"         {src_name}: {old_a:.2f} -> {new_a:.2f}  "
                  f"(shift {shift_a:+.3f})")
            print(f"         {tgt_name}: {old_b:.2f} -> {new_b:.2f}  "
                  f"(shift {shift_b:+.3f})")
            print(f"         diff: {diff:.3f} -> {abs(new_a - new_b):.3f}")
        else:
            print(f"\n  WOULD FIX  {src_name} <-> {tgt_name}")
            print(f"              axis={axis}")
            print(f"              {src_name}: {val_a:.2f} -> "
                  f"{log_entry['new_values'][0]:.2f}  "
                  f"(shift {shift_a:+.3f})")
            print(f"              {tgt_name}: {val_b:.2f} -> "
                  f"{log_entry['new_values'][1]:.2f}  "
                  f"(shift {shift_b:+.3f})")
            print(f"              diff: {diff:.3f} -> {new_diff:.3f}")

        fixed_pairs.append(log_entry)
        log_entries.append(log_entry)

    # --- Write modified .jsonld files ---
    if not args.dry_run and modified_files:
        print(f"\n{'='*70}")
        print(f"  WRITING {len(modified_files)} MODIFIED FILES")
        print(f"{'='*70}")
        for fpath in sorted(modified_files):
            data = file_data[fpath]
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  Written: {fpath.relative_to(root)}")

    # --- Write recalibration log ---
    log_dir = root / "outputs" / "metrics"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "polar_recalibration_log.json"

    log_output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "threshold": threshold,
        "max_shift_per_dimension": max_shift,
        "dry_run": args.dry_run,
        "summary": {
            "total_polar_pairs": len(pairs),
            "passing_before": len(passing),
            "failing_before": len(failing),
            "fixed": len(fixed_pairs),
            "skipped_unfixable": len(skipped_pairs),
            "files_modified": len(modified_files),
        },
        "fixed_pairs": fixed_pairs,
        "skipped_pairs": skipped_pairs,
    }

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\n  Log written to: {log_path.relative_to(root)}")

    # --- Final summary ---
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total POLAR_OPPOSITE pairs examined : {len(pairs)}")
    print(f"  Already passing (>= {threshold})     : {len(passing)}")
    print(f"  Failing (< {threshold})              : {len(failing)}")
    print(f"  Successfully fixed                   : {len(fixed_pairs)}")
    print(f"  Skipped (exceed max shift)           : {len(skipped_pairs)}")
    print(f"  Files modified                       : {len(modified_files)}")
    if args.dry_run:
        print(f"\n  ** DRY RUN -- no files were modified **")
    print()


if __name__ == "__main__":
    main()
