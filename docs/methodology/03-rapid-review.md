# 03 — Rapid Review

**Primary source**: Cartaxo, Pinto & Soares 2020, *Rapid Reviews in Software Engineering*.
**Supersedes**: `docs/rapid-reviews.md`.

> **⚠ CORRECTION to the project's framing.** `docs/all-together.md` describes Rapid Reviews as "the
> least rigorous of the three". That is not the defining property and it is a misleading basis for
> a workflow. **A Rapid Review is defined by being bound to a practitioner's actual problem and
> conducted with that practitioner**; the methodological relaxations follow from the time constraint
> that context imposes. Cartaxo is explicit that RRs "are neither ad-hoc literature reviews, nor an
> excuse for absence of scientific rigour", and that a review conducted **without practitioner
> collaboration and without a problem from practice is a *deviation* that the community should
> avoid**. Optimising the workflow for "less rigour" rather than "practitioner-bound" would
> reproduce exactly the deviation the source warns against.

---

## What defines a Rapid Review

Three phases mirroring an SLR — **planning, performing, reporting** — with the differences appearing
inside the steps. The distinction of purpose: an SLR adopts strategies aiming to reduce research
bias and guarantee evidence quality; an RR aims to **deliver scientific evidence in a timely manner
to support practitioners' decision-making**.

**Time frame: days or weeks**, against months or years for an SLR. The two worked examples in the
paper: **17 studies in 6 days**, and **35 studies in 8 days**.

> **⚠ CAVEAT — when *not* to do a Rapid Review.**
> - **No practitioner, no practical problem** → not an RR; avoid.
> - **No real time or cost constraint** → "the argument to conduct lightweight secondary studies
>   like RRs holds only in scenarios where time and costs are hard constraints."
> - **No studies on the problem** → an RR is simply not viable; find another problem. This can only
>   be discovered during problem definition, so the process must allow abandoning at that point.
> - **Not a replacement for an SLR** — complementary. SLRs curate in-depth knowledge; RRs transfer
>   established knowledge to practice quickly.

---

## Phase 1 — Planning

### 1.1 Demand for a Rapid Review

Three recognised origins:
1. **Practitioners ask for one** — a decision-maker contacts a researcher or institution wanting
   evidence for a decision.
2. **A researcher aligns their agenda to a practical problem** — approaches a company or open-source
   team facing problems in their research area, proposing an RR that both supplies needed evidence
   and grounds their research.
3. **A researcher prospects for an agenda** — approaches an organisation with *no predetermined
   focus*, uses interviews to find the problems practitioners face, and then chooses one. This is
   how the paper's own two RRs began.

### 1.2 Define the problem

Close collaboration with practitioners is crucial. The problem is often not well defined — the
practitioner may not be fully aware of the main problem they face. Use qualitative methods
(interviews, focus groups) to understand the context and the hidden problems. Calibrate the
interview to how clear the problem already is: exploratory, objective, or skipped entirely.

**This is an interactive process** and may fail: if no studies address the identified problem, the
RR is not viable and another problem must be found.

### 1.3 Define the research questions

Questions matter as much as in an SLR, but "useful" has a specific meaning: answers are useful when
they help practitioners **solve or attenuate their practical problem**, and questions are meaningful
only when they lead to such answers.

> **The rule**: research questions must be defined **in close collaboration with practitioners**.
> Questions aiming to identify research gaps or provide general insight to the research community
> **should be avoided and left to SLRs**. RR questions are bounded to their practical context — they
> are naturally narrower.

**The cornerstone form** is exploratory: *what strategies exist to deal with this problem, and how
effective are they?* Under time pressure, what practitioners most need is evidence-supported
strategies.

Worked pattern from the two cases:
- "What are the strategies to improve customer collaboration in software development practice?" +
  "What are their effectiveness?"
- Two further questions were added in one case only — on the *benefits* of collaboration and the
  *problems caused by its absence* — because the team needed the findings to persuade their
  customers. In the other case they were unnecessary, because the stakeholders already agreed the
  problem mattered and only wanted to know what to do.

> **⚙ IMPLEMENTATION.** The optional-extra-questions pattern is worth modelling: the question set is
> shaped by *what the practitioner needs to do with the answer* (decide vs. persuade), not only by
> the topic.

### 1.4 Define the stakeholder roles

An RR is a joint initiative and **active participation of both sides is mandatory**. Researchers
guarantee methodological consistency and transparency; practitioners ensure the work stays bound to
a real problem so the evidence is useful.

**Either extreme is acceptable**, and everything between is encouraged:
- Researchers perform every activity — provided practitioners are involved throughout, validating
  each decision.
- Practitioners perform every activity — provided researchers are involved, validating each
  methodological decision.

Effort split is decided by the time and resource constraints of the specific situation.

### 1.5 Create the protocol

Same goal as an SLR protocol: specify all methodological steps. **The protocol is what makes an RR
systematic rather than ad-hoc, so it is required, well-documented.** Components are the same as
Kitchenham & Charters: research questions, search strategy, inclusion/exclusion criteria, selection
procedure, extraction procedure, synthesis procedure, reporting.

> **The one structural difference**: an RR protocol is **naturally inclined to change during the
> review**, because the process is deliberately flexible. Changes after protocol definition **must
> be documented and justified transparently**.

> **⚙ IMPLEMENTATION.** This makes protocol *versioning with justification* a first-class
> requirement for RR, not an optional audit feature. An RR protocol that cannot record "we changed
> this, here is why" fails the method's central rule.

---

## Phase 2 — Performing

**The governing rule, and the one to enforce in software:**

> **Transparency is the golden standard in Rapid Reviews.** Whatever strategies are employed to
> reduce cost or time, **limitations and threats to validity must be reported in the protocol**.
> Practitioners are willing to consume evidence from less rigorous methods, *as long as they are
> aware of the limitations*.

**Strategies are a menu, not a package.** You do not adopt all of them — analyse the context and
decide which trade-offs to accept. The paper's own illustration: one RR may use multiple search
sources if coverage is critical but skip quality appraisal; another may use a single source but
appraise rigorously, if reliability of evidence is critical.

### 2.1 Search strategy

May focus on **a single search source** — most likely Scopus or Google Scholar, since these cover a
wide spectrum and index the major digital libraries. Complementing with snowballing is a viable
option. Both worked examples used **Scopus only**.

Four further effort-reducing restrictions:
1. Limit by date
2. Restrict language
3. Focus on a geographical area
4. Limit by research method (e.g. controlled experiments only)

> **⚠ CAVEAT.** These may exclude relevant studies and reduce coverage. **If adopted, the threat must
> be reported transparently.**

### 2.2 Selection procedure

Restrictive criteria serve two goals: reduce the volume to screen, **and** produce evidence that
better fits the practitioner's needs.

Worked exclusions from the Team Motivation RR — run in a small private company with collocated
teams — excluded studies about large companies, distributed teams, crowdsourced development, and
open-source development.

> **This is the important nuance.** Narrowing inclusion criteria to match the practitioner's context
> **is not a threat to validity — it is good practice.** Highly contextualised studies are long
> considered one of the best ways to have impact in practice. Contrast with search restrictions
> (2.1), which *are* threats. The platform should not treat all narrowing identically.

**Staffing**: may be conducted by **a single reviewer**, or with a second reviewer covering only a
reduced sample. This introduces selection bias and must be reported.

**Three-substep screening** — an RR-specific procedural change:

| Substep | Basis | Effect |
| ------- | ----- | ------ |
| 1 | **Title only** | Accelerates exclusion of clearly out-of-scope papers without reading abstracts |
| 2 | Abstract | |
| 3 | Full content | |

An SLR normally uses two substeps (title+abstract, then full text). The title-only first pass is the
speed gain, and its acknowledged cost is **false negatives**.

> **⚠ CAVEAT, with a counterweight.** Title-only screening loses papers with badly written titles —
> Wohlin found strict title screening would have dropped 5 of 11 papers snowballing found. But an RR
> practitioner in Cartaxo's study judged the trade-off acceptable in context: the RR still surfaced
> more possibilities than their usual practice of consulting a single source. **Record the trade-off;
> do not pretend it is free, and do not treat it as disqualifying.**

### 2.3 Quality appraisal

Three escalating options:
1. **Skip it entirely** — threats must be reported. Both worked examples did this.
2. **Venue proxy** — include only studies from conferences/journals with a rigorous review process.
   Low effort, and you know the studies passed *some* sieve. Lossy: a relevant study may appear at a
   less prestigious venue or on arXiv.
3. **Reduced-staffing appraisal** — single reviewer, or pairs appraising only a sample. For when
   evidence quality is critical.

### 2.4 Extraction procedure

May be conducted by **a single reviewer**, with the bias reported. Both worked examples did this.

**On missing data — an explicit divergence from SLR practice.** An SLR recommends contacting authors.
RRs in medicine very infrequently do. The RR strategy: **exclude studies with missing data and report
the exclusion.** Consumers can reach those studies later if they wish.

### 2.5 Synthesis procedure

Use **lightweight methods — Narrative Synthesis** — rather than meta-analysis, grounded theory, or
similar. Narrative summaries are the most common approach in practice. The limitation must be
reported so practitioners can make an informed decision.

**Conclusions and recommendations are mandatory, not optional.** They are particularly important in
an RR because they guide adoption. Researchers should dedicate time to conclusions and
recommendations for practitioners and **avoid presenting a report with findings only**. A
practitioner in the study said what was missing was "a conclusion, the researcher's comments".

Conclusions must be **strongly bounded to the RR's context** — unlike SLR conclusions, which aim at a
wider audience.

> **⚙ IMPLEMENTATION.** "Findings without recommendations" should be a completion gate failure for an
> RR, not an acceptable end state. This is the opposite of the SLR default, where over-claiming is
> the greater risk.

---

## Phase 3 — Reporting

An SLR is written for an academic audience in scientific paper format. An RR **targets practitioners**,
so not everything crucial to researchers is relevant to them — research method, background, related
work. RRs must be reported in a **more straightforward way, focused on results and recommendations**.

### Evidence Briefings

**One-page documents** reporting the main findings. The template derives from best practices in
medicine plus Information Design and Gestalt Theory principles. Six parts:

| # | Part | Rule |
| - | ---- | ---- |
| 1 | **Title** | As concise as possible — one or two lines. Longer titles steal space from findings |
| 2 | **Summary** | Suggested structure: *"This briefing reports scientific evidence on \<RESEARCH GOAL\>"*. A few lines only |
| 3 | **Findings** | The most important section. **One finding per paragraph.** Bullets, charts, figures and tables are welcome. Short sentences, straight to the point. **Must not contain information about the research method** — interested readers follow the complementary material |
| 4 | **Right-side box** | Target audience; what is included; **what is *not* included** |
| 5 | **Complementary material** | At the bottom: a link to at least the RR protocol and the list of primary study references |
| 6 | **Logos** | Institutions involved, at the very top — publicises the producers and invites practitioners to seek more RRs |

Empirical warrant: both researchers and practitioners were positive about Evidence Briefings as a
medium for transferring knowledge to practice.

> **⚠ CAVEAT observed empirically.** Practitioners found **some findings unclear in the printed
> briefing**, though they became clear after discussion with researchers at a workshop. A briefing is
> not self-evidently sufficient; the format has a legibility ceiling worth testing against real
> readers.

### Dissemination

Post the briefing on the institution's or company's website; share via social networks or
ResearchGate. Not all RRs can be disseminated beyond the practitioner, because of sensitive company
information — so **confidentiality is a first-class property of an RR report**.

> **⚙ IMPLEMENTATION.** The platform's share-token model for briefings matches this: some briefings
> are public artefacts, others must stay private to the commissioning organisation.

**RRs can and should also be published in academic peer-reviewed venues.** The objection that an RR
is too small a contribution misses that RRs usually sit inside broader knowledge-transfer
initiatives, which are welcomed in scientific venues. Such a paper can report the protocol, the
results, **and the practitioners' perceptions of the initiative**. Note that briefings themselves are
usually internally reviewed but **not peer reviewed**.

---

## RR versus SLR — the comparison

| Characteristic | Rapid Review | Systematic Review |
| -------------- | ------------ | ----------------- |
| **Problem** | Bounded to a practical problem, in a practical context | May emerge from academic or practical contexts; practice-driven SRs are the exception |
| **Research questions** | Lead to answers that help solve the practitioner's problem; exploratory strategy-and-effectiveness questions are a gold standard | Admits practitioner-supporting questions but also purely researcher-facing ones |
| **Protocol** | Required, documented | Required, documented |
| **Stakeholder roles** | Close collaboration with practitioners, who may execute steps themselves | Practitioner participation possible, but researchers usually conduct everything |
| **Time frame** | **Days or weeks** | **Months or years** |
| **Search strategy** | May use one source; may limit by year, language, study design | Multiple sources recommended; may limit similarly but comprehensiveness is preferred |
| **Selection** | May be single-person; criteria may be **more restrictive** to match the RR's context | Must be in pairs to avoid selection bias; usually less context-restrictive |
| **Quality appraisal** | Single person, or not at all | In pairs |
| **Extraction** | Usually single person | In pairs to avoid extraction bias |
| **Synthesis** | Narrative summaries most common | More systematic methods should be applied — though often are not |
| **Report** | Alternative media fitting practitioner needs, e.g. Evidence Briefings | Traditional research paper |

---

## Threats to validity in an RR — a disclosure regime, not a taxonomy

Cartaxo defines no named threat taxonomy. Instead: **every methodological concession is itself a
threat that must be recorded.** All concessions go in the protocol; the report carries a disclaimer
about methodological limitations, with detail deferred to the protocol so the report stays concise.

Concession-specific threats named in the text:

| Concession | Threat |
| ---------- | ------ |
| Search restriction (date, language, geography, method) | Reduced coverage |
| Title-only first screening pass | False negatives |
| Single-reviewer selection | Selection bias |
| Single-reviewer extraction | Extraction bias |
| Skipped quality appraisal | Low-quality primary studies |
| Narrative synthesis | Limited synthesis rigour |
| Excluding studies with missing data | Missing-data exclusions |
| **Narrowing criteria to the practitioner's context** | **Explicitly NOT a threat — good practice** |

> **⚙ IMPLEMENTATION.** This is directly encodable: the platform already models RR concessions as
> configuration (single-reviewer mode, QA appraisal mode). Each concession selected should
> **automatically create the corresponding threat record**, pre-populated — which is what the
> existing `RRThreatToValidity` auto-creation does. This chapter supplies the full mapping, and the
> exception that must *not* generate a threat.

---

## On grey literature in an RR

> **◐ DISPUTED.** Cartaxo recommends **excluding grey literature from RRs**: an RR already carries
> several limitations, and adding grey literature "could weaken the quality of the review produced,
> at least in the eyes of an unconvinced researcher". He flags this as an untested hypothesis.
>
> This sits in direct tension with Garousi's MLR work and with Kitchenham 2023, which argue grey
> literature is often exactly what practitioner-facing questions need. The platform should not
> hard-code either position — but it should surface the tension, because an RR is the study type
> where practitioner relevance and grey-literature scepticism collide most sharply. See
> [05-grey-literature-mlr.md](./05-grey-literature-mlr.md).
