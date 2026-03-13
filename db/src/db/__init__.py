"""SMS Researcher database package: SQLAlchemy models and engine factory."""

from db.base import Base, engine_factory
from db.models import InclusionStatus, Paper, Study, StudyPaper, StudyStatus, StudyType
from db.models.users import GroupMembership, ResearchGroup, User
from db.models.study import Reviewer, StudyMember
from db.models.pico import PICOComponent
from db.models.seeds import SeedAuthor, SeedPaper
from db.models.criteria import ExclusionCriterion, InclusionCriterion
from db.models.search import SearchString, SearchStringIteration
from db.models.search_exec import SearchExecution, SearchMetrics
from db.models.candidate import CandidatePaper, CandidatePaperStatus, PaperDecision, PaperDecisionType
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.audit import AuditAction, AuditRecord
from db.models.extraction import DataExtraction, ExtractionFieldAudit, ExtractionStatus, ResearchType
from db.models.results import ChartType, ClassificationScheme, DomainModel, QualityReport

__all__ = [
    "Base",
    "engine_factory",
    "Paper",
    "Study",
    "StudyPaper",
    "StudyStatus",
    "StudyType",
    "InclusionStatus",
    "ResearchGroup",
    "User",
    "GroupMembership",
    "StudyMember",
    "Reviewer",
    "PICOComponent",
    "SeedPaper",
    "SeedAuthor",
    "InclusionCriterion",
    "ExclusionCriterion",
    "SearchString",
    "SearchStringIteration",
    "SearchExecution",
    "SearchMetrics",
    "CandidatePaper",
    "CandidatePaperStatus",
    "PaperDecision",
    "PaperDecisionType",
    "BackgroundJob",
    "JobStatus",
    "JobType",
    "AuditRecord",
    "AuditAction",
    "DataExtraction",
    "ExtractionFieldAudit",
    "ExtractionStatus",
    "ResearchType",
    "DomainModel",
    "ClassificationScheme",
    "ChartType",
    "QualityReport",
]
