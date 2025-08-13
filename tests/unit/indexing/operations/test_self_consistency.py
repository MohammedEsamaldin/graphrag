from dataclasses import dataclass

from graphrag.index.operations.extract_covariates.typing import Covariate
from graphrag.index.operations.self_consistency import check_self_consistency


@dataclass
class StoredCovariate:
    id: str
    subject_id: str
    attributes: dict | None = None


class DummySearchEngine:
    def __init__(self, covariates):
        class Context:
            def __init__(self, cov):
                self.covariates = cov

        self.context_builder = Context(covariates)


def test_conflict_detected():
    existing = StoredCovariate(
        id="1",
        subject_id="A",
        attributes={"object_id": "B", "status": "TRUE"},
    )
    search = DummySearchEngine({"claim": [existing]})
    incoming = Covariate(subject_id="A", object_id="B", type="claim", status="FALSE")

    result = check_self_consistency(incoming, search)
    assert not result.is_consistent
    assert result.conflicts[0].id == "1"


def test_no_conflict():
    existing = StoredCovariate(
        id="1",
        subject_id="A",
        attributes={"object_id": "B", "status": "TRUE"},
    )
    search = DummySearchEngine({"claim": [existing]})
    incoming = Covariate(subject_id="A", object_id="B", type="claim", status="TRUE")

    result = check_self_consistency(incoming, search)
    assert result.is_consistent


if __name__ == "__main__":
    test_conflict_detected()
    test_no_conflict()
    print("tests passed")
