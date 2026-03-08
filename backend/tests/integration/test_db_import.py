"""Integration test: verify db package imports correctly from backend context."""

import importlib


class TestDbImport:
    """Verify db package is importable from the backend workspace member."""

    def test_study_model_importable(self) -> None:
        """Study model imports without ImportError."""
        from db.models import Study  # noqa: F401

    def test_paper_model_importable(self) -> None:
        """Paper model imports without ImportError."""
        from db.models import Paper  # noqa: F401

    def test_study_paper_model_importable(self) -> None:
        """StudyPaper model imports without ImportError."""
        from db.models import StudyPaper  # noqa: F401

    def test_engine_factory_importable(self) -> None:
        """engine_factory imports without ImportError."""
        from db.base import engine_factory  # noqa: F401

    def test_all_models_in_single_import(self) -> None:
        """All three models importable in a single statement."""
        from db.models import Paper, Study, StudyPaper  # noqa: F401
        assert Study is not None
        assert Paper is not None
        assert StudyPaper is not None
