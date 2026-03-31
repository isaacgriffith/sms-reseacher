"""research_protocol_definition

Revision ID: 0018
Revises: 0017
Create Date: 2026-03-30 00:00:00.000000

Feature 010 schema additions:

1. New PostgreSQL enum types:
   - ``protocol_task_type_enum`` — all valid task types across all study types.
   - ``quality_gate_type_enum`` — gate evaluation strategy.
   - ``edge_condition_operator_enum`` — numeric comparison operators.
   - ``task_node_status_enum`` — runtime execution state per node.
   - ``node_assignee_type_enum`` — human role vs AI agent assignee.
   - ``node_data_type_enum`` — typed input/output slot types.

2. New tables (in dependency order):
   - ``research_protocol`` — header record for a named protocol graph.
   - ``protocol_node`` — task vertices in a protocol graph.
   - ``protocol_node_input`` — named typed input slots on a node.
   - ``protocol_node_output`` — named typed output slots on a node.
   - ``quality_gate`` — quality gate conditions attached to nodes.
   - ``node_assignee`` — assignees on protocol nodes.
   - ``protocol_edge`` — directed information-flow edges between nodes.
   - ``study_protocol_assignment`` — one-to-one study → protocol mapping.
   - ``task_execution_state`` — runtime state per (study, node) pair.

3. Data seeding:
   - Default protocol templates for all 4 study types (SMS 10, SLR 12,
     Rapid 10, Tertiary 9 nodes) with edges and quality gates.
   - ``study_protocol_assignment`` rows for all existing studies (pointing
     to the default template matching their study_type).
   - ``task_execution_state`` rows for all existing studies (status=pending,
     with the first topological node set to active for active studies).

Downgrade reverses all steps in reverse order.
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision: str = "0018"
down_revision: str = "0017"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

# ---------------------------------------------------------------------------
# New enum type definitions (create_type=False — created/dropped explicitly)
# ---------------------------------------------------------------------------

_protocol_task_type_enum = postgresql.ENUM(
    "DefinePICO",
    "DefineProtocol",
    "DefineScope",
    "BuildSearchString",
    "ExecuteSearch",
    "GreyLiteratureSearch",
    "SearchSecondaryStudies",
    "ScreenPapers",
    "FullTextReview",
    "SnowballSearch",
    "AssessQuality",
    "AppraiseQuality",
    "CheckInterRaterReliability",
    "ImportSeedStudies",
    "ExtractData",
    "AppraiseQualityItems",
    "IdentifyThreatsToValidity",
    "NarrativeSynthesis",
    "SynthesizeData",
    "ProduceBriefing",
    "ValidateResults",
    "GenerateReport",
    "StakeholderEngagement",
    name="protocol_task_type_enum",
    create_type=False,
)

_quality_gate_type_enum = postgresql.ENUM(
    "metric_threshold",
    "completion_check",
    "human_sign_off",
    name="quality_gate_type_enum",
    create_type=False,
)

_edge_condition_operator_enum = postgresql.ENUM(
    "gt",
    "gte",
    "lt",
    "lte",
    "eq",
    "neq",
    name="edge_condition_operator_enum",
    create_type=False,
)

_task_node_status_enum = postgresql.ENUM(
    "pending",
    "active",
    "complete",
    "skipped",
    "gate_failed",
    name="task_node_status_enum",
    create_type=False,
)

_node_assignee_type_enum = postgresql.ENUM(
    "human_role",
    "ai_agent",
    name="node_assignee_type_enum",
    create_type=False,
)

_node_data_type_enum = postgresql.ENUM(
    "text",
    "pico_struct",
    "search_string",
    "candidate_paper_list",
    "full_text_content",
    "extraction_record_list",
    "synthesis_result",
    "quality_score",
    "paper_count",
    "boolean",
    "report",
    name="node_data_type_enum",
    create_type=False,
)

# Existing enum type (referenced, not created)
_study_type_enum = postgresql.ENUM(
    "SMS",
    "SLR",
    "Tertiary",
    "Rapid",
    name="study_type_enum",
    create_type=False,
)


# ---------------------------------------------------------------------------
# Seed data helpers
# ---------------------------------------------------------------------------


def _seed_sms_protocol(conn: sa.engine.Connection) -> int:
    """Insert default SMS protocol and return its id.

    Args:
        conn: Active database connection.

    Returns:
        The ``id`` of the inserted ``research_protocol`` row.
    """
    result = conn.execute(
        sa.text(
            "INSERT INTO research_protocol"
            " (name, description, study_type, is_default_template, owner_user_id, version_id,"
            "  created_at, updated_at)"
            " VALUES"
            " (:name, :desc, :stype, :is_default, NULL, 1, now(), now())"
            " RETURNING id"
        ),
        {
            "name": "Default SMS Protocol",
            "desc": "Default systematic mapping study protocol with 10 standard task nodes.",
            "stype": "SMS",
            "is_default": True,
        },
    )
    protocol_id: int = result.scalar_one()

    # ---- nodes (10) --------------------------------------------------------
    nodes = [
        ("define_pico", "DefinePICO", "Define PICO", "Define Population, Intervention, Comparison, Outcome components.", True, 100.0, 100.0),
        ("build_search_string", "BuildSearchString", "Build Search String", "Construct boolean search string from PICO components.", True, 300.0, 100.0),
        ("execute_search", "ExecuteSearch", "Execute Search", "Run search across selected literature databases.", True, 500.0, 100.0),
        ("screen_papers", "ScreenPapers", "Screen Papers", "Title and abstract screening against inclusion/exclusion criteria.", True, 700.0, 100.0),
        ("full_text_review", "FullTextReview", "Full Text Review", "Full-text review of papers that passed screening.", False, 900.0, 100.0),
        ("snowball_search", "SnowballSearch", "Snowball Search", "Forward/backward citation snowballing from included papers.", False, 900.0, 300.0),
        ("extract_data", "ExtractData", "Extract Data", "Extract structured data from included papers.", True, 1100.0, 100.0),
        ("synthesize_data", "SynthesizeData", "Synthesize Data", "Synthesize extracted data across included papers.", True, 1300.0, 100.0),
        ("validate_results", "ValidateResults", "Validate Results", "Validate synthesis results for consistency and completeness.", False, 1500.0, 100.0),
        ("generate_report", "GenerateReport", "Generate Report", "Generate the final systematic mapping study report.", True, 1700.0, 100.0),
    ]
    node_ids: dict[str, int] = {}
    for task_id, task_type, label, desc, is_req, px, py in nodes:
        r = conn.execute(
            sa.text(
                "INSERT INTO protocol_node"
                " (protocol_id, task_id, task_type, label, description, is_required,"
                "  position_x, position_y, created_at, updated_at)"
                " VALUES (:pid, :tid, :ttype, :label, :desc, :is_req, :px, :py, now(), now())"
                " RETURNING id"
            ),
            {
                "pid": protocol_id,
                "tid": task_id,
                "ttype": task_type,
                "label": label,
                "desc": desc,
                "is_req": is_req,
                "px": px,
                "py": py,
            },
        )
        node_ids[task_id] = r.scalar_one()

    # ---- inputs / outputs --------------------------------------------------
    _insert_node_io(conn, node_ids["define_pico"],
                    inputs=[("research_questions", "text", True)],
                    outputs=[("pico_components", "pico_struct")])
    _insert_node_io(conn, node_ids["build_search_string"],
                    inputs=[("pico_components", "pico_struct", True)],
                    outputs=[("search_string", "search_string")])
    _insert_node_io(conn, node_ids["execute_search"],
                    inputs=[("search_string", "search_string", True)],
                    outputs=[("candidate_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["screen_papers"],
                    inputs=[("candidate_papers", "candidate_paper_list", True)],
                    outputs=[("screened_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["full_text_review"],
                    inputs=[("screened_papers", "candidate_paper_list", True)],
                    outputs=[("reviewed_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["snowball_search"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("additional_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["extract_data"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("extraction_records", "extraction_record_list")])
    _insert_node_io(conn, node_ids["synthesize_data"],
                    inputs=[("extraction_records", "extraction_record_list", True)],
                    outputs=[("synthesis_result", "synthesis_result")])
    _insert_node_io(conn, node_ids["validate_results"],
                    inputs=[("synthesis_result", "synthesis_result", True)],
                    outputs=[("validated_synthesis", "synthesis_result")])
    _insert_node_io(conn, node_ids["generate_report"],
                    inputs=[("synthesis_result", "synthesis_result", True)],
                    outputs=[("report", "report")])

    # ---- quality gates (FR-022 mapping) ------------------------------------
    _insert_gate(conn, node_ids["define_pico"], "completion_check",
                 {"description": "PICO document is complete and saved."})
    _insert_gate(conn, node_ids["execute_search"], "completion_check",
                 {"description": "At least one search has been executed."})
    _insert_gate(conn, node_ids["extract_data"], "completion_check",
                 {"description": "Data extraction has been started."})

    # ---- assignees ---------------------------------------------------------
    _insert_assignee(conn, node_ids["define_pico"], "human_role", "study_admin")
    _insert_assignee(conn, node_ids["screen_papers"], "human_role", "reviewer")
    _insert_assignee(conn, node_ids["extract_data"], "human_role", "reviewer")

    # ---- edges -------------------------------------------------------------
    edges = [
        ("e_pico_search", "define_pico", "pico_components", "build_search_string", "pico_components"),
        ("e_search_exec", "build_search_string", "search_string", "execute_search", "search_string"),
        ("e_exec_screen", "execute_search", "candidate_papers", "screen_papers", "candidate_papers"),
        ("e_screen_ft", "screen_papers", "screened_papers", "full_text_review", "screened_papers"),
        ("e_ft_extract", "full_text_review", "reviewed_papers", "extract_data", "reviewed_papers"),
        ("e_ft_snowball", "full_text_review", "reviewed_papers", "snowball_search", "reviewed_papers"),
        ("e_snowball_extract", "snowball_search", "additional_papers", "extract_data", "reviewed_papers"),
        ("e_extract_synth", "extract_data", "extraction_records", "synthesize_data", "extraction_records"),
        ("e_synth_validate", "synthesize_data", "synthesis_result", "validate_results", "synthesis_result"),
        ("e_synth_report", "synthesize_data", "synthesis_result", "generate_report", "synthesis_result"),
        ("e_validate_report", "validate_results", "validated_synthesis", "generate_report", "synthesis_result"),
    ]
    for edge_id, src, src_out, tgt, tgt_in in edges:
        _insert_edge(conn, protocol_id, edge_id,
                     node_ids[src], src_out, node_ids[tgt], tgt_in)

    return protocol_id


def _seed_slr_protocol(conn: sa.engine.Connection) -> int:
    """Insert default SLR protocol and return its id."""
    result = conn.execute(
        sa.text(
            "INSERT INTO research_protocol"
            " (name, description, study_type, is_default_template, owner_user_id, version_id,"
            "  created_at, updated_at)"
            " VALUES (:name, :desc, :stype, :is_default, NULL, 1, now(), now())"
            " RETURNING id"
        ),
        {
            "name": "Default SLR Protocol",
            "desc": "Default systematic literature review protocol with 12 standard task nodes.",
            "stype": "SLR",
            "is_default": True,
        },
    )
    protocol_id: int = result.scalar_one()

    nodes = [
        ("define_protocol", "DefineProtocol", "Define Protocol", "Define the SLR protocol including PICO/S, search strategy, and quality criteria.", True, 100.0, 100.0),
        ("build_search_string", "BuildSearchString", "Build Search String", "Construct boolean search string from protocol components.", True, 300.0, 100.0),
        ("execute_search", "ExecuteSearch", "Execute Search", "Run search across selected literature databases.", True, 500.0, 100.0),
        ("grey_literature", "GreyLiteratureSearch", "Grey Literature Search", "Search grey literature sources.", False, 500.0, 300.0),
        ("screen_papers", "ScreenPapers", "Screen Papers", "Title and abstract screening.", True, 700.0, 100.0),
        ("full_text_review", "FullTextReview", "Full Text Review", "Full-text review of screened papers.", False, 900.0, 100.0),
        ("snowball_search", "SnowballSearch", "Snowball Search", "Citation snowballing from included papers.", False, 900.0, 300.0),
        ("assess_quality", "AssessQuality", "Assess Quality", "Quality assessment of included studies.", True, 1100.0, 100.0),
        ("check_irr", "CheckInterRaterReliability", "Check Inter-Rater Reliability", "Compute Cohen's κ and resolve disagreements.", False, 1100.0, 300.0),
        ("extract_data", "ExtractData", "Extract Data", "Extract structured data from included papers.", True, 1300.0, 100.0),
        ("synthesize_data", "SynthesizeData", "Synthesize Data", "Synthesize extracted data.", True, 1500.0, 100.0),
        ("generate_report", "GenerateReport", "Generate Report", "Generate the final SLR report.", True, 1700.0, 100.0),
    ]
    node_ids: dict[str, int] = {}
    for task_id, task_type, label, desc, is_req, px, py in nodes:
        r = conn.execute(
            sa.text(
                "INSERT INTO protocol_node"
                " (protocol_id, task_id, task_type, label, description, is_required,"
                "  position_x, position_y, created_at, updated_at)"
                " VALUES (:pid, :tid, :ttype, :label, :desc, :is_req, :px, :py, now(), now())"
                " RETURNING id"
            ),
            {"pid": protocol_id, "tid": task_id, "ttype": task_type,
             "label": label, "desc": desc, "is_req": is_req, "px": px, "py": py},
        )
        node_ids[task_id] = r.scalar_one()

    _insert_node_io(conn, node_ids["define_protocol"],
                    inputs=[("research_questions", "text", True)],
                    outputs=[("protocol_doc", "text")])
    _insert_node_io(conn, node_ids["build_search_string"],
                    inputs=[("protocol_doc", "text", True)],
                    outputs=[("search_string", "search_string")])
    _insert_node_io(conn, node_ids["execute_search"],
                    inputs=[("search_string", "search_string", True)],
                    outputs=[("candidate_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["grey_literature"],
                    inputs=[("search_string", "search_string", True)],
                    outputs=[("grey_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["screen_papers"],
                    inputs=[("candidate_papers", "candidate_paper_list", True)],
                    outputs=[("screened_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["full_text_review"],
                    inputs=[("screened_papers", "candidate_paper_list", True)],
                    outputs=[("reviewed_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["snowball_search"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("additional_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["assess_quality"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("quality_scores", "quality_score")])
    _insert_node_io(conn, node_ids["check_irr"],
                    inputs=[("quality_scores", "quality_score", True)],
                    outputs=[("kappa_score", "quality_score")])
    _insert_node_io(conn, node_ids["extract_data"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("extraction_records", "extraction_record_list")])
    _insert_node_io(conn, node_ids["synthesize_data"],
                    inputs=[("extraction_records", "extraction_record_list", True)],
                    outputs=[("synthesis_result", "synthesis_result")])
    _insert_node_io(conn, node_ids["generate_report"],
                    inputs=[("synthesis_result", "synthesis_result", True)],
                    outputs=[("report", "report")])

    _insert_gate(conn, node_ids["assess_quality"], "completion_check",
                 {"description": "All included papers have quality scores."})
    _insert_gate(conn, node_ids["check_irr"], "metric_threshold",
                 {"metric_name": "kappa_coefficient", "operator": "gte", "threshold": 0.6})

    _insert_assignee(conn, node_ids["assess_quality"], "human_role", "reviewer")
    _insert_assignee(conn, node_ids["extract_data"], "human_role", "reviewer")

    edges = [
        ("e_proto_search", "define_protocol", "protocol_doc", "build_search_string", "protocol_doc"),
        ("e_search_exec", "build_search_string", "search_string", "execute_search", "search_string"),
        ("e_search_grey", "build_search_string", "search_string", "grey_literature", "search_string"),
        ("e_exec_screen", "execute_search", "candidate_papers", "screen_papers", "candidate_papers"),
        ("e_screen_ft", "screen_papers", "screened_papers", "full_text_review", "screened_papers"),
        ("e_ft_snowball", "full_text_review", "reviewed_papers", "snowball_search", "reviewed_papers"),
        ("e_ft_assess", "full_text_review", "reviewed_papers", "assess_quality", "reviewed_papers"),
        ("e_ft_extract", "full_text_review", "reviewed_papers", "extract_data", "reviewed_papers"),
        ("e_assess_irr", "assess_quality", "quality_scores", "check_irr", "quality_scores"),
        ("e_extract_synth", "extract_data", "extraction_records", "synthesize_data", "extraction_records"),
        ("e_synth_report", "synthesize_data", "synthesis_result", "generate_report", "synthesis_result"),
    ]
    for edge_id, src, src_out, tgt, tgt_in in edges:
        _insert_edge(conn, protocol_id, edge_id,
                     node_ids[src], src_out, node_ids[tgt], tgt_in)

    return protocol_id


def _seed_rapid_protocol(conn: sa.engine.Connection) -> int:
    """Insert default Rapid Review protocol and return its id."""
    result = conn.execute(
        sa.text(
            "INSERT INTO research_protocol"
            " (name, description, study_type, is_default_template, owner_user_id, version_id,"
            "  created_at, updated_at)"
            " VALUES (:name, :desc, :stype, :is_default, NULL, 1, now(), now())"
            " RETURNING id"
        ),
        {
            "name": "Default Rapid Review Protocol",
            "desc": "Default rapid review protocol with 10 standard task nodes.",
            "stype": "Rapid",
            "is_default": True,
        },
    )
    protocol_id: int = result.scalar_one()

    nodes = [
        ("define_pico", "DefinePICO", "Define PICO", "Define scope and research questions.", True, 100.0, 100.0),
        ("build_search_string", "BuildSearchString", "Build Search String", "Construct search string from scope definition.", True, 300.0, 100.0),
        ("execute_search", "ExecuteSearch", "Execute Search", "Run search across selected databases.", True, 500.0, 100.0),
        ("screen_papers", "ScreenPapers", "Screen Papers", "Title and abstract screening.", True, 700.0, 100.0),
        ("full_text_review", "FullTextReview", "Full Text Review", "Full-text review of screened papers.", False, 900.0, 100.0),
        ("appraise_quality", "AppraiseQuality", "Appraise Quality", "Quality appraisal of included papers.", True, 1100.0, 100.0),
        ("appraise_items", "AppraiseQualityItems", "Appraise Quality Items", "Detailed quality item appraisal.", False, 1100.0, 300.0),
        ("identify_threats", "IdentifyThreatsToValidity", "Identify Threats to Validity", "Document threats to validity.", False, 1300.0, 300.0),
        ("narrative_synth", "NarrativeSynthesis", "Narrative Synthesis", "Synthesize findings narratively.", True, 1300.0, 100.0),
        ("produce_briefing", "ProduceBriefing", "Produce Evidence Briefing", "Generate practitioner-facing evidence briefing.", True, 1500.0, 100.0),
    ]
    node_ids: dict[str, int] = {}
    for task_id, task_type, label, desc, is_req, px, py in nodes:
        r = conn.execute(
            sa.text(
                "INSERT INTO protocol_node"
                " (protocol_id, task_id, task_type, label, description, is_required,"
                "  position_x, position_y, created_at, updated_at)"
                " VALUES (:pid, :tid, :ttype, :label, :desc, :is_req, :px, :py, now(), now())"
                " RETURNING id"
            ),
            {"pid": protocol_id, "tid": task_id, "ttype": task_type,
             "label": label, "desc": desc, "is_req": is_req, "px": px, "py": py},
        )
        node_ids[task_id] = r.scalar_one()

    _insert_node_io(conn, node_ids["define_pico"],
                    inputs=[("research_questions", "text", True)],
                    outputs=[("scope_definition", "pico_struct")])
    _insert_node_io(conn, node_ids["build_search_string"],
                    inputs=[("scope_definition", "pico_struct", True)],
                    outputs=[("search_string", "search_string")])
    _insert_node_io(conn, node_ids["execute_search"],
                    inputs=[("search_string", "search_string", True)],
                    outputs=[("candidate_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["screen_papers"],
                    inputs=[("candidate_papers", "candidate_paper_list", True)],
                    outputs=[("screened_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["full_text_review"],
                    inputs=[("screened_papers", "candidate_paper_list", True)],
                    outputs=[("reviewed_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["appraise_quality"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("quality_appraisal", "quality_score")])
    _insert_node_io(conn, node_ids["appraise_items"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("item_appraisals", "quality_score")])
    _insert_node_io(conn, node_ids["identify_threats"],
                    inputs=[("quality_appraisal", "quality_score", True)],
                    outputs=[("threats_identified", "boolean")])
    _insert_node_io(conn, node_ids["narrative_synth"],
                    inputs=[("reviewed_papers", "candidate_paper_list", True)],
                    outputs=[("narrative_sections", "synthesis_result")])
    _insert_node_io(conn, node_ids["produce_briefing"],
                    inputs=[("narrative_sections", "synthesis_result", True)],
                    outputs=[("evidence_briefing", "report")])

    _insert_gate(conn, node_ids["appraise_quality"], "completion_check",
                 {"description": "Quality appraisal is complete for all included papers."})
    _insert_gate(conn, node_ids["narrative_synth"], "completion_check",
                 {"description": "Narrative synthesis sections are complete."})

    _insert_assignee(conn, node_ids["define_pico"], "human_role", "study_admin")
    _insert_assignee(conn, node_ids["appraise_quality"], "human_role", "reviewer")

    edges = [
        ("e_pico_search", "define_pico", "scope_definition", "build_search_string", "scope_definition"),
        ("e_search_exec", "build_search_string", "search_string", "execute_search", "search_string"),
        ("e_exec_screen", "execute_search", "candidate_papers", "screen_papers", "candidate_papers"),
        ("e_screen_ft", "screen_papers", "screened_papers", "full_text_review", "screened_papers"),
        ("e_ft_appraise", "full_text_review", "reviewed_papers", "appraise_quality", "reviewed_papers"),
        ("e_ft_items", "full_text_review", "reviewed_papers", "appraise_items", "reviewed_papers"),
        ("e_appraise_threats", "appraise_quality", "quality_appraisal", "identify_threats", "quality_appraisal"),
        ("e_ft_synth", "full_text_review", "reviewed_papers", "narrative_synth", "reviewed_papers"),
        ("e_synth_briefing", "narrative_synth", "narrative_sections", "produce_briefing", "narrative_sections"),
    ]
    for edge_id, src, src_out, tgt, tgt_in in edges:
        _insert_edge(conn, protocol_id, edge_id,
                     node_ids[src], src_out, node_ids[tgt], tgt_in)

    return protocol_id


def _seed_tertiary_protocol(conn: sa.engine.Connection) -> int:
    """Insert default Tertiary Study protocol and return its id."""
    result = conn.execute(
        sa.text(
            "INSERT INTO research_protocol"
            " (name, description, study_type, is_default_template, owner_user_id, version_id,"
            "  created_at, updated_at)"
            " VALUES (:name, :desc, :stype, :is_default, NULL, 1, now(), now())"
            " RETURNING id"
        ),
        {
            "name": "Default Tertiary Study Protocol",
            "desc": "Default tertiary study protocol with 9 standard task nodes.",
            "stype": "Tertiary",
            "is_default": True,
        },
    )
    protocol_id: int = result.scalar_one()

    nodes = [
        ("define_scope", "DefineScope", "Define Scope", "Define the scope and research questions for the tertiary study.", True, 100.0, 100.0),
        ("build_search_string", "BuildSearchString", "Build Search String", "Construct search string targeting secondary study databases.", True, 300.0, 100.0),
        ("execute_search", "ExecuteSearch", "Execute Search", "Run search to identify candidate secondary studies.", True, 500.0, 100.0),
        ("search_secondary", "SearchSecondaryStudies", "Search Secondary Studies", "Search platform and external sources for secondary studies.", True, 500.0, 300.0),
        ("screen_papers", "ScreenPapers", "Screen Papers", "Screen candidate secondary studies by title and abstract.", True, 700.0, 100.0),
        ("assess_quality", "AssessQuality", "Assess Quality", "Quality assessment of included secondary studies.", True, 900.0, 100.0),
        ("import_seeds", "ImportSeedStudies", "Import Seed Studies", "Import included papers from platform secondary studies.", False, 900.0, 300.0),
        ("extract_data", "ExtractData", "Extract Data", "Extract structured data from each secondary study.", True, 1100.0, 100.0),
        ("generate_report", "GenerateReport", "Generate Report", "Generate the tertiary study landscape report.", True, 1300.0, 100.0),
    ]
    node_ids: dict[str, int] = {}
    for task_id, task_type, label, desc, is_req, px, py in nodes:
        r = conn.execute(
            sa.text(
                "INSERT INTO protocol_node"
                " (protocol_id, task_id, task_type, label, description, is_required,"
                "  position_x, position_y, created_at, updated_at)"
                " VALUES (:pid, :tid, :ttype, :label, :desc, :is_req, :px, :py, now(), now())"
                " RETURNING id"
            ),
            {"pid": protocol_id, "tid": task_id, "ttype": task_type,
             "label": label, "desc": desc, "is_req": is_req, "px": px, "py": py},
        )
        node_ids[task_id] = r.scalar_one()

    _insert_node_io(conn, node_ids["define_scope"],
                    inputs=[("research_questions", "text", True)],
                    outputs=[("scope_doc", "text")])
    _insert_node_io(conn, node_ids["build_search_string"],
                    inputs=[("scope_doc", "text", True)],
                    outputs=[("search_string", "search_string")])
    _insert_node_io(conn, node_ids["execute_search"],
                    inputs=[("search_string", "search_string", True)],
                    outputs=[("candidate_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["search_secondary"],
                    inputs=[("scope_doc", "text", True)],
                    outputs=[("secondary_candidates", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["screen_papers"],
                    inputs=[("candidate_papers", "candidate_paper_list", True)],
                    outputs=[("screened_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["assess_quality"],
                    inputs=[("screened_papers", "candidate_paper_list", True)],
                    outputs=[("quality_scores", "quality_score")])
    _insert_node_io(conn, node_ids["import_seeds"],
                    inputs=[("screened_papers", "candidate_paper_list", True)],
                    outputs=[("imported_papers", "candidate_paper_list")])
    _insert_node_io(conn, node_ids["extract_data"],
                    inputs=[("screened_papers", "candidate_paper_list", True)],
                    outputs=[("extraction_records", "extraction_record_list")])
    _insert_node_io(conn, node_ids["generate_report"],
                    inputs=[("extraction_records", "extraction_record_list", True)],
                    outputs=[("report", "report")])

    _insert_gate(conn, node_ids["extract_data"], "completion_check",
                 {"description": "Data extraction is complete for all included secondary studies."})
    _insert_gate(conn, node_ids["assess_quality"], "completion_check",
                 {"description": "Quality assessment is complete for all screened studies."})

    _insert_assignee(conn, node_ids["define_scope"], "human_role", "study_admin")
    _insert_assignee(conn, node_ids["extract_data"], "human_role", "reviewer")

    edges = [
        ("e_scope_search", "define_scope", "scope_doc", "build_search_string", "scope_doc"),
        ("e_scope_secondary", "define_scope", "scope_doc", "search_secondary", "scope_doc"),
        ("e_search_exec", "build_search_string", "search_string", "execute_search", "search_string"),
        ("e_exec_screen", "execute_search", "candidate_papers", "screen_papers", "candidate_papers"),
        ("e_screen_assess", "screen_papers", "screened_papers", "assess_quality", "screened_papers"),
        ("e_screen_import", "screen_papers", "screened_papers", "import_seeds", "screened_papers"),
        ("e_screen_extract", "screen_papers", "screened_papers", "extract_data", "screened_papers"),
        ("e_extract_report", "extract_data", "extraction_records", "generate_report", "extraction_records"),
    ]
    for edge_id, src, src_out, tgt, tgt_in in edges:
        _insert_edge(conn, protocol_id, edge_id,
                     node_ids[src], src_out, node_ids[tgt], tgt_in)

    return protocol_id


def _insert_node_io(
    conn: sa.engine.Connection,
    node_id: int,
    inputs: list[tuple[str, str, bool]],
    outputs: list[tuple[str, str]],
) -> None:
    """Insert input and output slot rows for a protocol node.

    Args:
        conn: Active database connection.
        node_id: The ``protocol_node.id`` this IO belongs to.
        inputs: List of ``(name, data_type, is_required)`` tuples.
        outputs: List of ``(name, data_type)`` tuples.
    """
    for name, dtype, is_req in inputs:
        conn.execute(
            sa.text(
                "INSERT INTO protocol_node_input (node_id, name, data_type, is_required)"
                " VALUES (:nid, :name, :dtype, :is_req)"
            ),
            {"nid": node_id, "name": name, "dtype": dtype, "is_req": is_req},
        )
    for name, dtype in outputs:
        conn.execute(
            sa.text(
                "INSERT INTO protocol_node_output (node_id, name, data_type)"
                " VALUES (:nid, :name, :dtype)"
            ),
            {"nid": node_id, "name": name, "dtype": dtype},
        )


def _insert_gate(
    conn: sa.engine.Connection,
    node_id: int,
    gate_type: str,
    config: dict,
) -> None:
    """Insert a quality gate row for a protocol node.

    Args:
        conn: Active database connection.
        node_id: The ``protocol_node.id`` this gate belongs to.
        gate_type: One of ``metric_threshold``, ``completion_check``, ``human_sign_off``.
        config: Type-specific configuration dict.
    """
    conn.execute(
        sa.text(
            "INSERT INTO quality_gate (node_id, gate_type, config, created_at)"
            " VALUES (:nid, :gtype, :config, now())"
        ),
        {"nid": node_id, "gtype": gate_type, "config": json.dumps(config)},
    )


def _insert_assignee(
    conn: sa.engine.Connection,
    node_id: int,
    assignee_type: str,
    role: str,
) -> None:
    """Insert a human-role assignee row for a protocol node.

    Args:
        conn: Active database connection.
        node_id: The ``protocol_node.id`` this assignee belongs to.
        assignee_type: ``human_role`` or ``ai_agent``.
        role: The role string (e.g. ``study_admin``, ``reviewer``).
    """
    conn.execute(
        sa.text(
            "INSERT INTO node_assignee (node_id, assignee_type, role)"
            " VALUES (:nid, :atype, :role)"
        ),
        {"nid": node_id, "atype": assignee_type, "role": role},
    )


def _insert_edge(
    conn: sa.engine.Connection,
    protocol_id: int,
    edge_id: str,
    source_node_id: int,
    source_output_name: str,
    target_node_id: int,
    target_input_name: str,
) -> None:
    """Insert an unconditional directed edge row.

    Args:
        conn: Active database connection.
        protocol_id: Parent protocol id.
        edge_id: Researcher-defined edge key (unique within protocol).
        source_node_id: Source ``protocol_node.id``.
        source_output_name: Name of the source node's output slot.
        target_node_id: Target ``protocol_node.id``.
        target_input_name: Name of the target node's input slot.
    """
    conn.execute(
        sa.text(
            "INSERT INTO protocol_edge"
            " (protocol_id, edge_id, source_node_id, source_output_name,"
            "  target_node_id, target_input_name, created_at)"
            " VALUES (:pid, :eid, :src, :src_out, :tgt, :tgt_in, now())"
        ),
        {
            "pid": protocol_id,
            "eid": edge_id,
            "src": source_node_id,
            "src_out": source_output_name,
            "tgt": target_node_id,
            "tgt_in": target_input_name,
        },
    )


def upgrade() -> None:
    """Apply feature 010 Research Protocol Definition schema additions.

    Creates 6 new enum types, 9 new tables in dependency order, seeds default
    protocol templates for all 4 study types, and back-fills existing studies
    with protocol assignments and initial execution states.
    """
    bind = op.get_bind()

    # 1. Create new enum types.
    _protocol_task_type_enum.create(bind, checkfirst=True)
    _quality_gate_type_enum.create(bind, checkfirst=True)
    _edge_condition_operator_enum.create(bind, checkfirst=True)
    _task_node_status_enum.create(bind, checkfirst=True)
    _node_assignee_type_enum.create(bind, checkfirst=True)
    _node_data_type_enum.create(bind, checkfirst=True)

    # 2. research_protocol
    op.create_table(
        "research_protocol",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("study_type", _study_type_enum, nullable=False),
        sa.Column("is_default_template", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("version_id", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["owner_user_id"], ["user.id"], ondelete="SET NULL",
                                name="fk_research_protocol_owner"),
        sa.UniqueConstraint("name", "owner_user_id", name="uq_research_protocol_name_owner"),
    )
    op.create_index("ix_research_protocol_owner_study_type",
                    "research_protocol", ["owner_user_id", "study_type"])
    op.create_index("ix_research_protocol_default_study_type",
                    "research_protocol", ["is_default_template", "study_type"])

    # 3. protocol_node
    op.create_table(
        "protocol_node",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("protocol_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.String(100), nullable=False),
        sa.Column("task_type", _protocol_task_type_enum, nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("position_x", sa.Float(), nullable=True),
        sa.Column("position_y", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["protocol_id"], ["research_protocol.id"], ondelete="CASCADE",
                                name="fk_protocol_node_protocol"),
        sa.UniqueConstraint("protocol_id", "task_id", name="uq_protocol_node_task_id"),
    )
    op.create_index("ix_protocol_node_protocol_id", "protocol_node", ["protocol_id"])

    # 4. protocol_node_input
    op.create_table(
        "protocol_node_input",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("data_type", _node_data_type_enum, nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["node_id"], ["protocol_node.id"], ondelete="CASCADE",
                                name="fk_protocol_node_input_node"),
        sa.UniqueConstraint("node_id", "name", name="uq_protocol_node_input_name"),
    )
    op.create_index("ix_protocol_node_input_node_id", "protocol_node_input", ["node_id"])

    # 5. protocol_node_output
    op.create_table(
        "protocol_node_output",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("data_type", _node_data_type_enum, nullable=False),
        sa.ForeignKeyConstraint(["node_id"], ["protocol_node.id"], ondelete="CASCADE",
                                name="fk_protocol_node_output_node"),
        sa.UniqueConstraint("node_id", "name", name="uq_protocol_node_output_name"),
    )
    op.create_index("ix_protocol_node_output_node_id", "protocol_node_output", ["node_id"])

    # 6. quality_gate
    op.create_table(
        "quality_gate",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("gate_type", _quality_gate_type_enum, nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["node_id"], ["protocol_node.id"], ondelete="CASCADE",
                                name="fk_quality_gate_node"),
    )
    op.create_index("ix_quality_gate_node_id", "quality_gate", ["node_id"])

    # 7. node_assignee
    op.create_table(
        "node_assignee",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("assignee_type", _node_assignee_type_enum, nullable=False),
        sa.Column("role", sa.String(100), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(["node_id"], ["protocol_node.id"], ondelete="CASCADE",
                                name="fk_node_assignee_node"),
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"], ondelete="SET NULL",
                                name="fk_node_assignee_agent"),
    )
    op.create_index("ix_node_assignee_node_id", "node_assignee", ["node_id"])

    # 8. protocol_edge
    op.create_table(
        "protocol_edge",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("protocol_id", sa.Integer(), nullable=False),
        sa.Column("edge_id", sa.String(100), nullable=False),
        sa.Column("source_node_id", sa.Integer(), nullable=False),
        sa.Column("source_output_name", sa.String(100), nullable=False),
        sa.Column("target_node_id", sa.Integer(), nullable=False),
        sa.Column("target_input_name", sa.String(100), nullable=False),
        sa.Column("condition_output_name", sa.String(100), nullable=True),
        sa.Column("condition_operator", _edge_condition_operator_enum, nullable=True),
        sa.Column("condition_value", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["protocol_id"], ["research_protocol.id"], ondelete="CASCADE",
                                name="fk_protocol_edge_protocol"),
        sa.ForeignKeyConstraint(["source_node_id"], ["protocol_node.id"], ondelete="CASCADE",
                                name="fk_protocol_edge_source_node"),
        sa.ForeignKeyConstraint(["target_node_id"], ["protocol_node.id"], ondelete="CASCADE",
                                name="fk_protocol_edge_target_node"),
        sa.UniqueConstraint("protocol_id", "edge_id", name="uq_protocol_edge_edge_id"),
    )
    op.create_index("ix_protocol_edge_protocol_id", "protocol_edge", ["protocol_id"])

    # 9. study_protocol_assignment
    op.create_table(
        "study_protocol_assignment",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("protocol_id", sa.Integer(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("assigned_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE",
                                name="fk_study_protocol_assignment_study"),
        sa.ForeignKeyConstraint(["protocol_id"], ["research_protocol.id"],
                                ondelete="RESTRICT",
                                name="fk_study_protocol_assignment_protocol"),
        sa.ForeignKeyConstraint(["assigned_by_user_id"], ["user.id"], ondelete="SET NULL",
                                name="fk_study_protocol_assignment_user"),
        sa.UniqueConstraint("study_id", name="uq_study_protocol_assignment_study"),
    )

    # 10. task_execution_state
    op.create_table(
        "task_execution_state",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("node_id", sa.Integer(), nullable=False),
        sa.Column("status", _task_node_status_enum, nullable=False, server_default="pending"),
        sa.Column("gate_failure_detail", sa.JSON(), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE",
                                name="fk_task_execution_state_study"),
        sa.ForeignKeyConstraint(["node_id"], ["protocol_node.id"], ondelete="CASCADE",
                                name="fk_task_execution_state_node"),
        sa.UniqueConstraint("study_id", "node_id",
                            name="uq_task_execution_state_study_node"),
    )
    op.create_index("ix_task_execution_state_study_id", "task_execution_state", ["study_id"])

    # 11. Seed default protocol templates for all 4 study types.
    conn = op.get_bind()
    sms_protocol_id = _seed_sms_protocol(conn)
    slr_protocol_id = _seed_slr_protocol(conn)
    rapid_protocol_id = _seed_rapid_protocol(conn)
    tertiary_protocol_id = _seed_tertiary_protocol(conn)

    # 12. Back-fill study_protocol_assignment for all existing studies.
    #     Maps each study_type to the newly inserted default protocol id.
    protocol_by_type = {
        "SMS": sms_protocol_id,
        "SLR": slr_protocol_id,
        "Rapid": rapid_protocol_id,
        "Tertiary": tertiary_protocol_id,
    }
    for study_type, protocol_id in protocol_by_type.items():
        conn.execute(
            sa.text(
                "INSERT INTO study_protocol_assignment"
                " (study_id, protocol_id, assigned_at)"
                " SELECT id, :pid, now()"
                " FROM study WHERE study_type = :stype"
                " ON CONFLICT (study_id) DO NOTHING"
            ),
            {"pid": protocol_id, "stype": study_type},
        )

    # 13. Back-fill task_execution_state for all existing studies.
    #     All nodes start as 'pending'; no active node is set here so the
    #     existing phase gate system remains authoritative for existing studies
    #     (see research.md Decision 8 — additive approach).
    conn.execute(
        sa.text(
            "INSERT INTO task_execution_state"
            " (study_id, node_id, status, created_at, updated_at)"
            " SELECT spa.study_id, pn.id, 'pending', now(), now()"
            " FROM study_protocol_assignment spa"
            " JOIN protocol_node pn ON pn.protocol_id = spa.protocol_id"
            " ON CONFLICT (study_id, node_id) DO NOTHING"
        )
    )


def downgrade() -> None:
    """Reverse feature 010 Research Protocol Definition schema additions.

    Drops tables in reverse dependency order, then drops the 6 new enum types.
    """
    # Drop tables in reverse dependency order.
    op.drop_index("ix_task_execution_state_study_id", table_name="task_execution_state")
    op.drop_table("task_execution_state")

    op.drop_table("study_protocol_assignment")

    op.drop_index("ix_protocol_edge_protocol_id", table_name="protocol_edge")
    op.drop_table("protocol_edge")

    op.drop_index("ix_node_assignee_node_id", table_name="node_assignee")
    op.drop_table("node_assignee")

    op.drop_index("ix_quality_gate_node_id", table_name="quality_gate")
    op.drop_table("quality_gate")

    op.drop_index("ix_protocol_node_output_node_id", table_name="protocol_node_output")
    op.drop_table("protocol_node_output")

    op.drop_index("ix_protocol_node_input_node_id", table_name="protocol_node_input")
    op.drop_table("protocol_node_input")

    op.drop_index("ix_protocol_node_protocol_id", table_name="protocol_node")
    op.drop_table("protocol_node")

    op.drop_index("ix_research_protocol_default_study_type", table_name="research_protocol")
    op.drop_index("ix_research_protocol_owner_study_type", table_name="research_protocol")
    op.drop_table("research_protocol")

    # Drop new enum types.
    bind = op.get_bind()
    _node_data_type_enum.drop(bind, checkfirst=True)
    _node_assignee_type_enum.drop(bind, checkfirst=True)
    _task_node_status_enum.drop(bind, checkfirst=True)
    _edge_condition_operator_enum.drop(bind, checkfirst=True)
    _quality_gate_type_enum.drop(bind, checkfirst=True)
    _protocol_task_type_enum.drop(bind, checkfirst=True)
