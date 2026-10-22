#!/usr/bin/env bash
# Run the repo's checks locally, in the order from docs/TOOL_SURVEY.md:
#
#   0. build data/mythic_patterns.db if it is missing (create_db.py)
#   1. pytest
#   2. hygiene audit          (scripts/hygiene/audit_hygiene.py)
#   3. ACP validator          (ACP/tools/validate.js)
#   4. v2 validation suite    (python -m validation.v2_run --quick, or --full)
#   5. human audit            (scripts/conduct_audit.py, reads step 4's cases)
#
# Logs and a summary go to a results folder: by default
# outputs/checks/<UTC timestamp>/ (outputs/ is gitignored), or the path given
# with --out. The folder must be outside the repo or gitignored.
#
# Tools that rewrite ACP files (derive_coordinates.js --all,
# add_archetypes.py, add_shadow_evolution.py, the enrich_* and hygiene fix_*
# scripts without --dry-run) are never run here. If any tracked file changes
# during the run, the script says so and exits non-zero.
#
# Usage: scripts/run_checks.sh [--out DIR] [--full]
#   PYTHON=/path/to/python scripts/run_checks.sh   to choose the interpreter
#
# Exit status: 0 if every step exited 0, 1 otherwise. A step's own verdict
# (validate.js exits 1 when it finds errors) counts as non-zero; see the
# summary for which step it was.

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 2
PYTHON="${PYTHON:-python3}"
V2_MODE="--quick"
OUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="${2:-}"; shift 2 ;;
    --full) V2_MODE="--full"; shift ;;
    -h|--help) sed -n '2,27p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1 (see --help)" >&2; exit 2 ;;
  esac
done

if [ -z "$OUT" ]; then
  OUT="$ROOT/outputs/checks/$(date -u +%Y%m%dT%H%M%SZ)"
fi
mkdir -p "$OUT" || exit 2
OUT="$(cd "$OUT" && pwd)"

# Refuse a results folder that git would track.
case "$OUT/" in
  "$ROOT"/*)
    if ! git check-ignore -q "$OUT/.probe"; then
      echo "results folder $OUT is inside the repo and not gitignored; pass --out with an ignored or outside path" >&2
      rmdir "$OUT" 2>/dev/null
      exit 2
    fi ;;
esac

SUMMARY="$OUT/summary.txt"
TRACKED_BEFORE="$(git status --porcelain --untracked-files=no)"
FAILED=0
: > "$SUMMARY"
{
  echo "run_checks.sh  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "commit  $(git rev-parse --short HEAD)"
  echo "python  $("$PYTHON" --version 2>&1)   node  $(node --version 2>/dev/null || echo missing)"
  echo
} >> "$SUMMARY"

step() {
  # step <name> <command...>
  local name="$1"; shift
  local log="$OUT/$name.log"
  local t0 t1 rc
  t0=$(date +%s)
  "$@" < /dev/null > "$log" 2>&1
  rc=$?
  t1=$(date +%s)
  printf '%-16s rc=%-3s %4ss  %s\n' "$name" "$rc" "$((t1 - t0))" "$*" | tee -a "$SUMMARY"
  [ "$rc" -eq 0 ] || FAILED=1
  return "$rc"
}

if [ ! -f data/mythic_patterns.db ]; then
  step 0-create_db "$PYTHON" scripts/database/create_db.py
fi
step 1-pytest "$PYTHON" -m pytest -q -p no:cacheprovider
step 2-hygiene "$PYTHON" scripts/hygiene/audit_hygiene.py
(cd ACP && step 3-validate_js node tools/validate.js)
[ $? -eq 0 ] || FAILED=1
if step 4-v2_run "$PYTHON" -m validation.v2_run "$V2_MODE"; then
  step 5-conduct_audit "$PYTHON" scripts/conduct_audit.py
else
  echo "5-conduct_audit skipped: needs step 4" | tee -a "$SUMMARY"
  FAILED=1
fi

# Copy the files the steps wrote under outputs/ next to the logs.
for f in outputs/hygiene_audit.json \
         outputs/metrics/v2_validation_results.json \
         outputs/reports/v2_validation_report.md \
         outputs/audits/human_audit_results.json; do
  [ -f "$f" ] && cp "$f" "$OUT/"
done

TRACKED_AFTER="$(git status --porcelain --untracked-files=no)"
if [ "$TRACKED_BEFORE" != "$TRACKED_AFTER" ]; then
  {
    echo
    echo "WARNING: tracked files changed during the run:"
    diff <(echo "$TRACKED_BEFORE") <(echo "$TRACKED_AFTER") | sed -n 's/^> /  /p'
  } | tee -a "$SUMMARY"
  FAILED=1
fi

echo
echo "results: $OUT"
exit "$FAILED"
