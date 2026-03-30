# Quickstart: 008-Rapid-Review-Workflow

**Generated**: 2026-03-21

This guide validates the Rapid Review feature end-to-end using the dev stack.

---

## Prerequisites

```bash
# Start the dev stack
cp .env.example .env   # ensure DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY set
docker compose up -d

# Apply migrations (includes 0016_rapid_review_workflow)
uv run alembic upgrade head
```

---

## 1. Create a Rapid Review Study

```bash
# Log in (obtain JWT)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"username":"admin@example.com","password":"changeme"}' \
  -H "Content-Type: application/json"
# → save access_token as TOKEN

# Create study with type=Rapid
curl -X POST http://localhost:8000/api/v1/studies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Onboarding Time Reduction","study_type":"Rapid"}'
# → save study id as STUDY_ID
```

---

## 2. Add a Practitioner Stakeholder

```bash
curl -X POST http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/stakeholders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "role_title": "Engineering Manager",
    "organisation": "Acme Corp",
    "involvement_type": "PROBLEM_DEFINER"
  }'
```

---

## 3. Configure and Validate the Protocol

```bash
# Set protocol fields
curl -X PUT http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/protocol \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "practical_problem": "How to reduce onboarding time in SMEs?",
    "research_questions": ["What strategies exist to reduce onboarding time?"],
    "time_budget_days": 14,
    "effort_budget_hours": 40,
    "inclusion_criteria": ["Published 2015-2025"],
    "exclusion_criteria": ["Grey literature"],
    "quality_appraisal_mode": "SKIPPED"
  }'

# Validate — expect 200 and status=VALIDATED
curl -X POST http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/protocol/validate \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: Protocol status transitions to `VALIDATED`. Phase 2 (search) unlocks.
Verify:
```bash
curl http://localhost:8000/api/v1/studies/$STUDY_ID/phases \
  -H "Authorization: Bearer $TOKEN"
# → {"unlocked_phases": [1, 2]}
```

---

## 4. Verify Threat-to-Validity Auto-Creation

```bash
# QA was SKIPPED → expect a QA_SKIPPED threat entry
curl http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/threats \
  -H "Authorization: Bearer $TOKEN"
# → should include {"threat_type": "QA_SKIPPED", ...}
```

---

## 5. Run a Search (Single Source)

Use the existing search UI or API (from 006-database-search-and-retrieval).
Confirm that configuring a single database source does **not** produce a quality error
(only a threat-to-validity entry).

```bash
# After search runs, check phases — Phase 3 should unlock
curl http://localhost:8000/api/v1/studies/$STUDY_ID/phases \
  -H "Authorization: Bearer $TOKEN"
# → {"unlocked_phases": [1, 2, 3]}
```

---

## 6. Test Protocol Re-validation (Invalidation Flow)

```bash
# Attempt to edit a validated protocol without acknowledging invalidation
curl -X PUT http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/protocol \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"practical_problem": "Updated problem statement"}'
# → expect 409 Conflict with papers_at_risk count

# Re-send with acknowledgment
curl -X PUT "http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/protocol?acknowledge_invalidation=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"practical_problem": "Updated problem statement"}'
# → expect 200, status=DRAFT, papers marked PROTOCOL_INVALIDATED
```

---

## 7. Complete Narrative Synthesis

```bash
# List synthesis sections (created when protocol was validated)
curl http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/synthesis \
  -H "Authorization: Bearer $TOKEN"
# → save first section id as SECTION_ID

# Request AI draft
curl -X POST http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/synthesis/$SECTION_ID/ai-draft \
  -H "Authorization: Bearer $TOKEN"
# → returns job_id; poll BackgroundJob until complete

# Update section with final text and mark complete
curl -X PUT http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/synthesis/$SECTION_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"narrative_text": "Three strategies were identified...", "is_complete": true}'

# Mark synthesis complete
curl -X POST http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/synthesis/complete \
  -H "Authorization: Bearer $TOKEN"
# → {"synthesis_complete": true}
```

---

## 8. Generate and Publish Evidence Briefing

```bash
# Trigger generation
curl -X POST http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/briefings \
  -H "Authorization: Bearer $TOKEN"
# → returns job_id; poll until complete; then list versions

curl http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/briefings \
  -H "Authorization: Bearer $TOKEN"
# → save briefing id as BRIEFING_ID

# Publish the version
curl -X POST http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/briefings/$BRIEFING_ID/publish \
  -H "Authorization: Bearer $TOKEN"
# → status=PUBLISHED
```

---

## 9. Generate Share Token and Verify Public Access

```bash
# Create share token
curl -X POST http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/briefings/$BRIEFING_ID/share-token \
  -H "Authorization: Bearer $TOKEN"
# → save token as SHARE_TOKEN

# Access WITHOUT authentication
curl http://localhost:8000/api/v1/public/briefings/$SHARE_TOKEN
# → full briefing JSON, no auth header needed

# Download PDF without auth
curl "http://localhost:8000/api/v1/public/briefings/$SHARE_TOKEN/export?format=pdf" \
  --output /tmp/briefing.pdf
# → PDF file, exactly one page

# Revoke token
curl -X DELETE http://localhost:8000/api/v1/rapid/studies/$STUDY_ID/briefings/share-token/$SHARE_TOKEN \
  -H "Authorization: Bearer $TOKEN"

# Verify revoked token returns 404
curl http://localhost:8000/api/v1/public/briefings/$SHARE_TOKEN
# → 404
```

---

## 10. Export Full Study Data

```bash
# Export in existing formats (JSON, CSV)
curl "http://localhost:8000/api/v1/studies/$STUDY_ID/export?format=json" \
  -H "Authorization: Bearer $TOKEN" \
  --output /tmp/rr-export.json
```

---

## E2E Playwright Smoke Test

```bash
cd frontend
PLAYWRIGHT_BASE_URL=http://localhost:5173 npx playwright test e2e/rapid-review/
```

Tests cover: creating a Rapid Review study → protocol editor → stakeholder form →
protocol validation → single-reviewer warning → synthesis editor → AI draft →
briefing generation → publish → share link → public briefing page.
