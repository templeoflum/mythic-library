#!/usr/bin/env python3
"""Check prerequisites for ACP + Library integration."""
import io
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def main():
    print("=== ACP + Library Integration Setup ===\n")
    ok = True

    # Check database
    db_path = PROJECT_ROOT / "data" / "mythic_patterns.db"
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"  [OK] Database: {db_path} ({size_mb:.1f} MB)")
    else:
        print(f"  [!!] Database not found: {db_path}")
        print("       Run: python scripts/database/create_db.py --reset")
        ok = False

    # Check ACP schema
    acp_path = PROJECT_ROOT / "ACP"
    primordials = acp_path / "schema" / "primordials.jsonld"
    if primordials.exists():
        print(f"  [OK] ACP primordials: {primordials}")
    else:
        print(f"  [!!] ACP schema not found: {primordials}")
        ok = False

    # Count ACP files
    jsonld_files = list(acp_path.rglob("*.jsonld")) if acp_path.exists() else []
    print(f"  [OK] ACP JSON-LD files: {len(jsonld_files)}")

    # Check dependencies
    print("\nDependencies:")
    for mod in ["numpy", "scipy", "sqlite3", "json"]:
        try:
            __import__(mod)
            print(f"  [OK] {mod}")
        except ImportError:
            print(f"  [!!] {mod} not installed")
            ok = False

    # Create output directories
    print("\nOutput directories:")
    for subdir in ["mappings", "metrics", "visualizations"]:
        out_dir = PROJECT_ROOT / "outputs" / subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] {out_dir}")

    # Quick ACP load test
    if ok:
        print("\nQuick load test:")
        sys.path.insert(0, str(PROJECT_ROOT))
        from integration.acp_loader import ACPLoader
        acp = ACPLoader(str(acp_path))
        summary = acp.summary()
        print(f"  Archetypes loaded:  {summary['archetypes']}")
        print(f"  Primordials loaded: {summary['primordials']}")
        print(f"  Systems loaded:     {summary['systems']}")
        print(f"  Alias entries:      {summary['alias_entries']}")
        print(f"  With coordinates:   {summary['with_coordinates']}")

        from integration.library_loader import LibraryLoader
        lib = LibraryLoader(str(db_path))
        lib_summary = lib.summary()
        print(f"\n  Library entities:   {lib_summary['entities']}")
        print(f"  Entity mentions:    {lib_summary['entity_mentions']}")
        print(f"  Segments:           {lib_summary['segments']}")
        print(f"  Motif tags:         {lib_summary['motif_tags']}")
        lib.close()

    print(f"\n{'='*40}")
    if ok:
        print("Setup OK. Run: python scripts/integration/run_validation.py")
    else:
        print("Setup INCOMPLETE. Fix issues above first.")

    return ok


if __name__ == "__main__":
    main()
