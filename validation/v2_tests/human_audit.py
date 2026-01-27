"""Test 6: Human Expert Concordance Audit.

Generates a structured audit document with 30 sampled cases for human
review. Each case presents ACP's claim about a relationship or neighbor,
and a reviewer marks AGREE / DISAGREE / UNSURE.
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

from integration.acp_loader import ACPLoader, AXES


class HumanAuditTest:
    def __init__(self, acp: ACPLoader):
        self.acp = acp

    def _archetype_summary(self, arch_id: str) -> Dict:
        """Build a human-readable summary of an archetype."""
        arch = self.acp.archetypes.get(arch_id, {})
        coords = self.acp.get_coordinates(arch_id)
        insts = self.acp.get_instantiations(arch_id)
        return {
            "id": arch_id,
            "name": arch.get("name", arch_id),
            "system": arch.get("systemCode", arch.get("belongsToSystem", "unknown")),
            "description": arch.get("description", "")[:200],
            "coordinates": {
                AXES[i]: round(float(coords[i]), 4) for i in range(len(AXES))
            } if coords is not None else None,
            "primordials": [
                {"primordial": inst.get("primordial", ""), "weight": inst.get("weight", 0)}
                for inst in insts
            ],
            "domains": arch.get("domains", [])[:5],
        }

    def _pair_entry(self, source_id: str, target_id: str, category: str, claim: str, **extra) -> Dict:
        """Build a structured audit case for a pair."""
        c1 = self.acp.get_coordinates(source_id)
        c2 = self.acp.get_coordinates(target_id)
        dist = float(np.linalg.norm(c1 - c2)) if c1 is not None and c2 is not None else None
        per_axis = {}
        if c1 is not None and c2 is not None:
            per_axis = {
                AXES[i]: round(abs(float(c1[i] - c2[i])), 4)
                for i in range(len(AXES))
            }

        entry = {
            "category": category,
            "claim": claim,
            "source": self._archetype_summary(source_id),
            "target": self._archetype_summary(target_id),
            "distance_8d": round(dist, 4) if dist is not None else None,
            "per_axis_difference": per_axis,
            "reviewer_judgment": None,  # AGREE / DISAGREE / UNSURE
            "reviewer_notes": "",
        }
        entry.update(extra)
        return entry

    def run(self, seed: int = 42) -> Dict:
        rng = np.random.default_rng(seed)

        cases = []

        # --- 10 CULTURAL_ECHO pairs (stratified by fidelity) ---
        echoes = self.acp.get_all_relationships(type_filter="CULTURAL_ECHO")
        valid_echoes = [
            r for r in echoes
            if self.acp.get_coordinates(r["source"]) is not None
            and self.acp.get_coordinates(r.get("target", "")) is not None
            and r.get("fidelity") is not None
        ]

        high_fid = [r for r in valid_echoes if r.get("fidelity", 0) >= 0.85]
        med_fid = [r for r in valid_echoes if 0.5 <= r.get("fidelity", 0) < 0.85]
        low_fid = [r for r in valid_echoes if r.get("fidelity", 0) < 0.5]

        def sample_echoes(pool, n):
            if len(pool) <= n:
                return pool
            idx = rng.choice(len(pool), size=n, replace=False)
            return [pool[i] for i in idx]

        for r in sample_echoes(high_fid, 3):
            cases.append(self._pair_entry(
                r["source"], r["target"],
                category="CULTURAL_ECHO (high fidelity)",
                claim=f"These two archetypes are cultural echoes with fidelity {r['fidelity']}",
                fidelity=r["fidelity"],
                notes=r.get("notes", ""),
            ))

        for r in sample_echoes(med_fid, 4):
            cases.append(self._pair_entry(
                r["source"], r["target"],
                category="CULTURAL_ECHO (medium fidelity)",
                claim=f"These two archetypes are cultural echoes with fidelity {r['fidelity']}",
                fidelity=r["fidelity"],
                notes=r.get("notes", ""),
            ))

        for r in sample_echoes(low_fid, 3):
            cases.append(self._pair_entry(
                r["source"], r["target"],
                category="CULTURAL_ECHO (low fidelity)",
                claim=f"These two archetypes are cultural echoes with fidelity {r['fidelity']}",
                fidelity=r["fidelity"],
                notes=r.get("notes", ""),
            ))

        # --- 5 POLAR_OPPOSITE pairs (spanning different axes) ---
        polars = self.acp.get_all_relationships(type_filter="POLAR_OPPOSITE")
        valid_polars = [
            r for r in polars
            if self.acp.get_coordinates(r["source"]) is not None
            and self.acp.get_coordinates(r.get("target", "")) is not None
        ]

        # Try to pick from different axes
        axis_buckets = {}
        for r in valid_polars:
            axis = r.get("axis", "unknown")
            axis_buckets.setdefault(axis, []).append(r)

        polar_samples = []
        for axis, bucket in axis_buckets.items():
            if len(polar_samples) >= 5:
                break
            polar_samples.append(bucket[rng.integers(len(bucket))])
        # Fill remaining from any
        while len(polar_samples) < 5 and valid_polars:
            r = valid_polars[rng.integers(len(valid_polars))]
            if r not in polar_samples:
                polar_samples.append(r)

        for r in polar_samples[:5]:
            cases.append(self._pair_entry(
                r["source"], r["target"],
                category="POLAR_OPPOSITE",
                claim=f"These archetypes are polar opposites on axis: {r.get('axis', 'unspecified')}",
                declared_axis=r.get("axis", ""),
                strength=r.get("strength", None),
                notes=r.get("notes", ""),
            ))

        # --- 5 COMPLEMENT pairs ---
        complements = self.acp.get_all_relationships(type_filter="COMPLEMENT")
        valid_complements = [
            r for r in complements
            if self.acp.get_coordinates(r["source"]) is not None
            and self.acp.get_coordinates(r.get("target", "")) is not None
        ]
        comp_sample = sample_echoes(valid_complements, 5)
        for r in comp_sample:
            cases.append(self._pair_entry(
                r["source"], r["target"],
                category="COMPLEMENT",
                claim=f"These archetypes complement each other: {r.get('dynamic', '')}",
                strength=r.get("strength", None),
                notes=r.get("notes", ""),
            ))

        # --- 5 nearest-neighbor cases ---
        target_names = ["Zeus", "Odin", "Isis", "Quetzalcoatl", "Shiva"]
        for name in target_names:
            matches = self.acp.find_by_name(name)
            if not matches:
                continue
            arch_id = matches[0]["id"]
            neighbors = self.acp.get_nearby(arch_id, threshold=0.5)[:3]
            for neighbor_id, neighbor_dist in neighbors:
                cases.append(self._pair_entry(
                    arch_id, neighbor_id,
                    category="NEAREST_NEIGHBOR",
                    claim=f"ACP says {name}'s nearest neighbor is {self.acp.archetypes.get(neighbor_id, {}).get('name', neighbor_id)} (distance {neighbor_dist:.4f})",
                ))

        # --- 5 most-distant-same-primordial cases ---
        primordial_members = {}
        for arch_id in self.acp.archetypes:
            insts = self.acp.get_instantiations(arch_id)
            if not insts:
                continue
            dominant = max(insts, key=lambda x: x.get("weight", 0))
            pid = dominant.get("primordial", "")
            if self.acp.get_coordinates(arch_id) is not None:
                primordial_members.setdefault(pid, []).append(arch_id)

        distant_same = []
        for pid, members in primordial_members.items():
            if len(members) < 2:
                continue
            max_dist = 0
            max_pair = None
            for i in range(len(members)):
                c1 = self.acp.get_coordinates(members[i])
                for j in range(i + 1, len(members)):
                    c2 = self.acp.get_coordinates(members[j])
                    d = float(np.linalg.norm(c1 - c2))
                    if d > max_dist:
                        max_dist = d
                        max_pair = (members[i], members[j], pid, d)
            if max_pair:
                distant_same.append(max_pair)

        distant_same.sort(key=lambda x: x[3], reverse=True)
        for src, tgt, pid, d in distant_same[:5]:
            cases.append(self._pair_entry(
                src, tgt,
                category="DISTANT_SAME_PRIMORDIAL",
                claim=f"Both share dominant primordial '{pid}' but are distance {d:.4f} apart — should they?",
                primordial=pid,
            ))

        # Summary
        return {
            "n_cases": len(cases),
            "cases_by_category": {
                cat: sum(1 for c in cases if c["category"].startswith(cat))
                for cat in ["CULTURAL_ECHO", "POLAR_OPPOSITE", "COMPLEMENT", "NEAREST_NEIGHBOR", "DISTANT_SAME_PRIMORDIAL"]
            },
            "cases": cases,
            "scoring_instructions": {
                "AGREE": "The ACP's claim about this pair seems reasonable and well-supported",
                "DISAGREE": "The ACP's claim about this pair seems wrong or misleading",
                "UNSURE": "Cannot determine from available context",
            },
            "verdicts": {
                "concordance": {
                    "pass": None,  # Filled after human review
                    "criterion": ">=80% concordance (24/30 AGREE)",
                    "result": "Awaiting human review",
                },
                "overall_pass": None,
            },
        }

    def save_audit(self, results: Dict, output_dir: str) -> str:
        """Save audit cases to JSON for human review."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        path = out / "human_audit_cases.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        return str(path)

    def score_audit(self, results: Dict) -> Dict:
        """Score a completed audit (after human fills in reviewer_judgment)."""
        cases = results.get("cases", [])
        agree = sum(1 for c in cases if c.get("reviewer_judgment") == "AGREE")
        disagree = sum(1 for c in cases if c.get("reviewer_judgment") == "DISAGREE")
        unsure = sum(1 for c in cases if c.get("reviewer_judgment") == "UNSURE")
        total_judged = agree + disagree + unsure

        if total_judged == 0:
            return {"error": "No judgments recorded"}

        concordance = agree / total_judged

        return {
            "agree": agree,
            "disagree": disagree,
            "unsure": unsure,
            "total_judged": total_judged,
            "concordance": round(concordance, 4),
            "pass": concordance >= 0.80,
            "partial": 0.60 <= concordance < 0.80,
        }
