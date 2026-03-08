"""Placeholder unit tests for SMS Researcher ORM models."""

import pytest

from db.models import (
    InclusionStatus,
    Paper,
    Study,
    StudyPaper,
    StudyStatus,
    StudyType,
)


class TestStudyModel:
    """Tests for the Study model."""

    def test_study_instantiates(self) -> None:
        """Study can be created with required fields."""
        study = Study(
            name="Test Study",
            study_type=StudyType.SMS,
            status=StudyStatus.DRAFT,
        )
        assert study.name == "Test Study"
        assert study.study_type == StudyType.SMS
        assert study.status == StudyStatus.DRAFT

    def test_study_repr(self) -> None:
        """Study __repr__ contains expected fields."""
        study = Study(name="My Study", study_type=StudyType.SLR)
        assert "My Study" in repr(study)
        assert "SLR" in repr(study)

    @pytest.mark.parametrize("study_type", list(StudyType))
    def test_study_type_enum_values(self, study_type: StudyType) -> None:
        """All StudyType enum values are valid."""
        study = Study(name="s", study_type=study_type)
        assert study.study_type == study_type

    @pytest.mark.parametrize("status", list(StudyStatus))
    def test_study_status_enum_values(self, status: StudyStatus) -> None:
        """All StudyStatus enum values are valid."""
        study = Study(name="s", study_type=StudyType.SMS, status=status)
        assert study.status == status


class TestPaperModel:
    """Tests for the Paper model."""

    def test_paper_instantiates_minimal(self) -> None:
        """Paper can be created with only required fields."""
        paper = Paper(title="A Great Paper")
        assert paper.title == "A Great Paper"
        assert paper.abstract is None
        assert paper.doi is None
        assert paper.metadata_ is None

    def test_paper_instantiates_full(self) -> None:
        """Paper can be created with all fields."""
        paper = Paper(
            title="Full Paper",
            abstract="This paper explores...",
            doi="10.1234/test",
            metadata_={"venue": "ICSE", "year": 2026},
        )
        assert paper.doi == "10.1234/test"
        assert paper.metadata_ == {"venue": "ICSE", "year": 2026}

    def test_paper_repr(self) -> None:
        """Paper __repr__ contains expected fields."""
        paper = Paper(title="Repr Test", doi="10.0/x")
        assert "10.0/x" in repr(paper)


class TestStudyPaperModel:
    """Tests for the StudyPaper join model."""

    def test_study_paper_instantiates(self) -> None:
        """StudyPaper can be created with required fields."""
        sp = StudyPaper(study_id=1, paper_id=2, inclusion_status=InclusionStatus.PENDING)
        assert sp.study_id == 1
        assert sp.paper_id == 2
        assert sp.inclusion_status == InclusionStatus.PENDING

    def test_study_paper_repr(self) -> None:
        """StudyPaper __repr__ contains expected fields."""
        sp = StudyPaper(study_id=3, paper_id=7, inclusion_status=InclusionStatus.INCLUDED)
        r = repr(sp)
        assert "3" in r
        assert "7" in r

    @pytest.mark.parametrize("status", list(InclusionStatus))
    def test_inclusion_status_enum_values(self, status: InclusionStatus) -> None:
        """All InclusionStatus enum values are valid."""
        sp = StudyPaper(study_id=1, paper_id=1, inclusion_status=status)
        assert sp.inclusion_status == status
