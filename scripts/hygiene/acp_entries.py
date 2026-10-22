"""Shared entry extraction for the ACP hygiene scripts.

Yields every entry dict in a parsed JSON-LD file: top-level entries[] or
@graph[], a single-object file, and the nested shapes integration/acp_loader.py
reads (tarot minor arcana suits[].cards[], hero's journey acts[].stages[]).
Yields the live objects, not copies; the fixers edit them in place.
"""


def extract_entries(data):
    if isinstance(data, dict):
        if "entries" in data and isinstance(data["entries"], list):
            for entry in data["entries"]:
                if isinstance(entry, dict):
                    yield entry
        elif "@graph" in data and isinstance(data["@graph"], list):
            for entry in data["@graph"]:
                if isinstance(entry, dict):
                    yield entry
        elif "@id" in data:
            yield data
        # Nested entries, as integration/acp_loader.py reads them:
        # tarot minor arcana suits[].cards[], hero's journey acts[].stages[]
        for outer, inner in (("suits", "cards"), ("acts", "stages")):
            for group in data.get(outer, []) or []:
                if not isinstance(group, dict):
                    continue
                if "@id" in group:
                    yield group
                for item in group.get(inner, []) or []:
                    if isinstance(item, dict) and "@id" in item:
                        yield item
    elif isinstance(data, list):
        for item in data:
            yield from extract_entries(item)
