"""Utilities for checking self consistency of covariate claims."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, TYPE_CHECKING

from graphrag.index.operations.extract_covariates.typing import Covariate

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from graphrag.query.structured_search.local_search.search import LocalSearch
    from graphrag.data_model.covariate import Covariate as StoredCovariate
else:  # pragma: no cover - use generic types at runtime
    LocalSearch = Any  # type: ignore
    StoredCovariate = Any  # type: ignore


@dataclass
class SelfConsistencyResult:
    """Result of a self-consistency check."""

    is_consistent: bool
    """Whether the incoming claim is consistent with stored claims."""

    conflicts: List[StoredCovariate]
    """Conflicting stored covariates."""


def check_self_consistency(
    claim: Covariate, search_engine: LocalSearch
) -> SelfConsistencyResult:
    """Compare a claim with existing covariates for contradictions.

    The search engine's context builder is expected to expose a ``covariates``
    mapping of covariate type to lists of stored ``Covariate`` objects. This
    function looks up existing covariates for the same subject/object pair and
    claim type and marks contradictions when the claim status disagrees with
    stored statuses.
    """

    covariates_map: dict[str, Iterable[StoredCovariate]] = (
        getattr(search_engine.context_builder, "covariates", {}) or {}
    )
    existing: Iterable[StoredCovariate] = covariates_map.get(claim.type or "", [])

    conflicts: list[StoredCovariate] = []
    for stored in existing:
        obj_id = stored.attributes.get("object_id") if stored.attributes else None
        status = stored.attributes.get("status") if stored.attributes else None
        if (
            stored.subject_id == claim.subject_id
            and obj_id == claim.object_id
            and _status_conflict(status, claim.status)
        ):
            conflicts.append(stored)

    return SelfConsistencyResult(is_consistent=len(conflicts) == 0, conflicts=conflicts)


def _status_conflict(existing: str | None, incoming: str | None) -> bool:
    """Return True if statuses are a contradiction."""

    if existing is None or incoming is None:
        return False

    a = existing.strip().upper()
    b = incoming.strip().upper()
    return (a == "TRUE" and b == "FALSE") or (a == "FALSE" and b == "TRUE")
