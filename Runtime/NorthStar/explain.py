"""Trace-only Explain Runtime; it never creates or changes evidence."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from .context import RuntimeContext


class ExplainRuntimeError(RuntimeError):
    """Raised when an Explain Chain input is invalid."""


class ExplainRuntime:
    """Build Decision -> Evidence -> Pattern -> Experience -> Repository."""

    engine_id = "explain_runtime"
    LAYERS = (
        ("decision", "decision_ref"),
        ("evidence", "evidence_refs"),
        ("pattern", "pattern_refs"),
        ("experience", "experience_refs"),
        ("repository", "repository_refs"),
    )

    def run(self, context: RuntimeContext) -> Mapping[str, Any]:
        payload = context.mutable_payload()
        groups: list[tuple[str, list[str]]] = []
        missing_layers: list[str] = []

        for layer, field in self.LAYERS:
            raw = payload.get(field)
            references = [raw] if isinstance(raw, str) else raw
            if not isinstance(references, list) or not all(
                isinstance(item, str) and item.strip() for item in references
            ):
                raise ExplainRuntimeError(
                    f"Explain Runtime field {field} must contain references"
                )
            if not references:
                missing_layers.append(layer)
            groups.append((layer, references))

        nodes: list[dict[str, Any]] = []
        missing_refs: list[str] = []
        for layer, references in groups:
            for reference in references:
                available = reference in context.snapshots
                if not available and layer != "decision":
                    missing_refs.append(reference)
                nodes.append(
                    {
                        "node_id": f"{layer}:{reference}",
                        "layer": layer,
                        "reference": reference,
                        "available": available or layer == "decision",
                    }
                )

        edges: list[dict[str, str]] = []
        populated_groups = [
            (layer, refs) for layer, refs in groups if refs
        ]
        for (_, sources), (_, targets) in zip(
            populated_groups, populated_groups[1:]
        ):
            for source in sources:
                for target in targets:
                    edges.append(
                        {
                            "source": source,
                            "target": target,
                            "relation": "EXPLAINS_WITH",
                        }
                    )

        return {
            "contract_version": "1.0",
            "request_id": context.request_id,
            "engine_id": self.engine_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_state": "candidate",
            "payload": {
                "chain_id": f"EXPLAIN-{context.request_id}",
                "decision_ref": groups[0][1][0],
                "layer_order": [layer for layer, _ in self.LAYERS],
                "nodes": nodes,
                "edges": edges,
                "missing_layers": missing_layers,
                "missing_refs": sorted(set(missing_refs)),
            },
            "source_refs": list(context.source_refs),
            "warnings": (
                ["Explain Chain contains missing references."]
                if missing_refs
                else []
            ),
            "errors": [],
            "model_impact": "shadow_candidate_not_production",
        }
