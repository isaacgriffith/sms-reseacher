"""Tertiary Study extraction and seed-import service (feature 009).

Responsibilities:
- :class:`TertiaryExtractionService` — seed import: copies included
  ``CandidatePaper`` records from a source study into a Tertiary Study's
  candidate corpus, deduplicating by shared ``paper_id``.
- :meth:`TertiaryExtractionService.ensure_extraction_records` — bulk-creates
  pending ``TertiaryDataExtraction`` stubs for all accepted papers that do not
  yet have an extraction record.
"""

from __future__ import annotations

import structlog
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.tertiary import SecondaryStudySeedImport, TertiaryDataExtraction
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


class TertiaryExtractionService:
    """Service for Tertiary Study seed import and data extraction support.

    All methods are async-first and require a live :class:`AsyncSession` passed
    in by the caller.  The caller is responsible for committing the session.
    """

    async def import_seed_study(
        self,
        target_study_id: int,
        source_study_id: int,
        user_id: int | None,
        db: AsyncSession,
    ) -> SecondaryStudySeedImport:
        """Copy included papers from *source_study_id* into *target_study_id*.

        Deduplicates against the existing target corpus using the shared
        ``paper_id`` (the canonical Paper entity identifier).  If the same
        paper is already present in the target study, it is counted as skipped
        rather than imported.

        A synthetic :class:`~db.models.search_exec.SearchExecution` is created
        for the target study to satisfy the ``search_execution_id`` FK on
        ``CandidatePaper``; its ``phase_tag`` is set to ``"seed-import"`` so
        it is easily distinguishable from real search executions.

        Args:
            target_study_id: The Tertiary Study receiving the seed papers.
            source_study_id: The SMS / SLR / Rapid Review study being imported.
            user_id: ID of the user triggering the import, or ``None``.
            db: Active async database session.

        Returns:
            The persisted :class:`SecondaryStudySeedImport` audit record.

        Raises:
            ValueError: If the source study has no included (accepted) papers.

        """
        bound = logger.bind(
            target_study_id=target_study_id,
            source_study_id=source_study_id,
        )

        # 1. Fetch included (accepted) CandidatePapers from source study.
        src_result = await db.execute(
            select(CandidatePaper).where(
                CandidatePaper.study_id == source_study_id,
                CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
            )
        )
        source_papers = list(src_result.scalars().all())

        if not source_papers:
            raise ValueError(f"Source study {source_study_id} has no included (accepted) papers.")

        # 2. Fetch existing paper_ids already in the target study.
        existing_result = await db.execute(
            select(CandidatePaper.paper_id).where(CandidatePaper.study_id == target_study_id)
        )
        existing_paper_ids: set[int] = {row[0] for row in existing_result.all()}

        # 3. Create a sentinel import record first (we need its id for FK).
        import_record = SecondaryStudySeedImport(
            target_study_id=target_study_id,
            source_study_id=source_study_id,
            imported_by_user_id=user_id,
            records_added=0,
            records_skipped=0,
        )
        db.add(import_record)
        await db.flush()  # generates import_record.id

        # 4. Create a synthetic SearchString + SearchExecution for the target
        #    study so the new CandidatePaper rows satisfy the FK constraint.
        search_exec = await self._get_or_create_seed_search_execution(
            study_id=target_study_id,
            db=db,
        )

        # 5. Bulk-insert new CandidatePaper rows, skipping duplicates.
        added = 0
        skipped = 0
        for src_cp in source_papers:
            if src_cp.paper_id in existing_paper_ids:
                skipped += 1
                continue

            new_cp = CandidatePaper(
                study_id=target_study_id,
                paper_id=src_cp.paper_id,
                search_execution_id=search_exec.id,
                phase_tag="seed-import",
                current_status=CandidatePaperStatus.ACCEPTED,
                source_seed_import_id=import_record.id,
            )
            db.add(new_cp)
            existing_paper_ids.add(src_cp.paper_id)  # prevent within-batch dups
            added += 1

        import_record.records_added = added
        import_record.records_skipped = skipped

        await db.flush()

        bound.info(
            "import_seed_study: completed",
            records_added=added,
            records_skipped=skipped,
        )
        return import_record

    async def _get_or_create_seed_search_execution(
        self,
        study_id: int,
        db: AsyncSession,
    ) -> SearchExecution:
        """Return a sentinel SearchExecution for seed imports in *study_id*.

        If one already exists (``phase_tag == "seed-import"``), it is reused;
        otherwise a new ``SearchString`` and ``SearchExecution`` are created.

        Args:
            study_id: The Tertiary Study that owns the search execution.
            db: Active async database session.

        Returns:
            A :class:`~db.models.search_exec.SearchExecution` instance.

        """
        # Reuse an existing seed-import execution if one exists.
        existing = await db.execute(
            select(SearchExecution).where(
                SearchExecution.study_id == study_id,
                SearchExecution.phase_tag == "seed-import",
            )
        )
        exec_row = existing.scalar_one_or_none()
        if exec_row is not None:
            return exec_row

        # Create a sentinel SearchString (not a real search string).
        search_string = SearchString(
            study_id=study_id,
            version=1,
            string_text="(seed-import sentinel)",
            is_active=False,
        )
        db.add(search_string)
        await db.flush()

        # Create the sentinel SearchExecution.
        search_exec = SearchExecution(
            study_id=study_id,
            search_string_id=search_string.id,
            status=SearchExecutionStatus.COMPLETED,
            phase_tag="seed-import",
        )
        db.add(search_exec)
        await db.flush()

        return search_exec

    async def ensure_extraction_records(
        self,
        study_id: int,
        db: AsyncSession,
    ) -> int:
        """Bulk-create pending ``TertiaryDataExtraction`` stubs for all accepted papers.

        Idempotent — papers that already have an extraction record are skipped.
        Flushes but does **not** commit; the caller is responsible for committing.

        Args:
            study_id: The Tertiary Study to process.
            db: Active async database session.

        Returns:
            The number of new extraction records created.

        """
        # Find accepted candidate papers for this study.
        accepted_result = await db.execute(
            select(CandidatePaper.id).where(
                CandidatePaper.study_id == study_id,
                CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
            )
        )
        accepted_ids = [row[0] for row in accepted_result.all()]
        if not accepted_ids:
            return 0

        # Find which ones already have an extraction record.
        existing_result = await db.execute(
            select(TertiaryDataExtraction.candidate_paper_id).where(
                TertiaryDataExtraction.candidate_paper_id.in_(accepted_ids)
            )
        )
        existing_cp_ids: set[int] = {row[0] for row in existing_result.all()}

        created = 0
        for cp_id in accepted_ids:
            if cp_id in existing_cp_ids:
                continue
            db.add(TertiaryDataExtraction(candidate_paper_id=cp_id, extraction_status="pending"))
            created += 1

        if created:
            await db.flush()
            logger.info(
                "ensure_extraction_records: created stubs",
                study_id=study_id,
                created=created,
            )
        return created
