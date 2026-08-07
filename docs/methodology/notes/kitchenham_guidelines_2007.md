# Kitchenham & Charters (2007) — Guidelines for performing SLRs in SE, EBSE-2007-01 v2.3

**Role in corpus:** THE foundational SLR process document for SE. 65pp. Everything else extends,
critiques, or specialises it. Cite as the base process for SLR.

## Three phases, with iteration
Planning → Conducting → Reporting. Explicitly iterative: "Data synthesis methods defined in the
protocol may be amended once data has been collected." Search strategies are "usually iterative".

---
## PHASE 1 — PLANNING

### 1.1 Confirm the need for a review (§5.1)
Must first identify and evaluate any **existing** systematic reviews of the phenomenon.

**CRD checklist for evaluating an existing review** (9 items):
1. What are the review's objectives?
2. What sources were searched? Any restrictions?
3. What were the inclusion/exclusion criteria and how applied?
4. What criteria assessed primary-study quality?
5. How were quality criteria applied?
6. How were data extracted?
7. How were data synthesised?
8. How were differences between studies investigated? How combined? Was combining reasonable?
9. Do the conclusions flow from the evidence?

**DARE criteria (4 questions)** — simpler, used as a *scored* instrument (0–4, half points
allowed; Kitchenham scored 4, Jørgensen 3.5):
1. Are the review's inclusion and exclusion criteria described and appropriate?
2. Is the literature search likely to have covered all relevant studies?
3. Did the reviewers assess the quality/validity of the included studies?
4. Were the basic data/studies adequately described?

**Greenhalgh's 5 questions:** important question addressed? thorough search of appropriate
databases + other sources? methodological quality assessed and trials weighted accordingly? how
sensitive are results to how the review was done? numerical results interpreted with common
sense and regard to the broader problem?

> **IMPL:** DARE is a 4-item scored rubric → directly implementable as report validation (G10).
> Also usable as the "is a new review needed" gate.

### 1.2 Commissioning a review (§5.2) — optional
Commissioning document: Project Title · Background · Review Questions · Advisory/Steering Group
Membership (researchers, practitioners, lay members, policy makers) · Methods of the review ·
Project Timetable · Dissemination Strategy · Support Infrastructure · Budget · References.

**Caveat:** not required for a team's own review or a PhD. *If commissioning is skipped, the
dissemination strategy MUST be folded into the review protocol.*

### 1.3 Research questions (§5.3) — "the most important part of any systematic review"
Questions drive everything: search must find studies addressing them; extraction must extract
data needed to answer them; analysis must synthesise so they can be answered.

**Question types** (adapted from Australian NHMRC's six healthcare types):
- Assessing the effect of a software engineering technology
- Assessing the frequency or rate of a project development factor (technology adoption, project
  success/failure rate)
- Identifying cost and risk factors associated with a technology
- Identifying the impact of technologies on reliability, performance and cost models
- Cost-benefit analysis of employing specific technologies/applications

(SE has no clear equivalent of "determining the performance of a diagnostic test".)

**What makes a *right* question:**
- Meaningful and important to practitioners as well as researchers
- Will lead either to changes in practice or to increased confidence in current practice
- Will identify discrepancies between commonly held beliefs and reality

Researcher-facing questions are legitimate (scoping future research; PhD positioning).

**Question structure — PICOC** (Petticrew & Roberts), extending medicine's PICO:
- **Population** — SE role (testers, managers), category of engineer (novice/experienced),
  application area, industry group.
  *Caveat:* medicine narrows population to reduce study count; SE has **too few** primary
  studies, so avoid restricting population until considering practical implications.
- **Intervention** — the methodology/tool/technology/procedure addressing the issue.
- **Comparison** — the control. **"Not using the intervention" is an inadequate description of a
  control.** SE techniques require training, so comparing users vs non-users confounds technique
  with training. Acute with student participants.
- **Outcome** — must relate to practitioner-relevant factors (reliability, cost, time to
  market). All relevant outcomes specified.
  *Caveat:* **widespread use of surrogate measures** in SE (defects in system test as surrogate
  for quality; coupling for design quality). Studies using surrogates may mislead.
- **Context** — academia vs industry; participants (practitioners/academics/consultants/
  students); task scale. Academic + student + small-scale is unlikely to be representative; some
  reviews exclude them, but in SE they may be all that exists.
- **Experimental designs** — medicine can restrict to RCTs; SE's paucity of primary studies means
  protocols more likely need to **aggregate across widely different study types**.

### 1.4 Develop the review protocol (§5.4)
Purpose: reduce researcher bias — "without a protocol, it is possible that the selection of
individual studies or the analysis may be driven by researcher expectations."

**Protocol components (10):**
1. Background / rationale
2. Research questions
3. Search strategy — terms + resources (digital libraries, journals, proceedings).
   *An initial mapping study can help determine an appropriate strategy.*
4. Study selection criteria — pilot on a subset
5. Study selection procedures — how many assessors per study, how disagreements resolved
6. Study quality assessment checklists and procedures
7. Data extraction strategy — if data require manipulation/assumptions/inferences, specify a
   validation process
8. Synthesis of extracted data — whether formal meta-analysis is intended, and which techniques
9. Dissemination strategy (if not in a commissioning document)
10. Project timetable

### 1.5 Evaluate the protocol (§5.5)
Independent expert group if funded; PhD students → supervisors. Reuse the §5.1 review questions.
Plus **internal consistency checks**:
- Search strings appropriately derived from the research questions
- Data to be extracted will properly address the research questions
- Data analysis procedure is appropriate to answer the research questions

> **IMPL:** these three are mechanically checkable; map onto `ProtocolReviewerAgent`.

### 1.6 Lessons learned for protocol construction (§5.6) — CAVEATS
- A **pre-review mapping study** may help scope research questions
- **Expect to revise questions during protocol development**
- **All team members must actively take part in developing the protocol**, so they understand how
  to perform data extraction
- **Piloting the protocol is essential** — finds mistakes in collection and aggregation; may
  force changes to extraction forms and synthesis methods
- Staples & Niazi: **limit scope by choosing clear and narrow research questions**

---
## PHASE 2 — CONDUCTING

### 2.1 Identification of research (§6.1)
Aim: find as many primary studies as possible with an **unbiased** strategy. Rigour of search is
what distinguishes an SLR from a traditional review.

**Search strategy development is iterative and benefits from:**
- Preliminary searches to identify existing SLRs and assess volume of relevant studies
- Trial searches using various combinations of terms derived from the question
- **Checking trial search strings against lists of already-known primary studies** ← seed-paper
  recall check / quasi-gold-standard
- Consultations with experts in the field

**General approach:** break the question into facets (population, intervention, comparison,
outcomes, context, study design) → list synonyms, abbreviations, alternative spellings → add
terms from subject headings used in journals/databases → combine with Boolean AND/OR.

**Digital libraries alone are NOT sufficient.** Must also search:
- Reference lists from relevant primary studies and review articles
- Journals (incl. company journals e.g. IBM Journal of R&D), **grey literature (technical
  reports, work in progress)**, conference proceedings
- Research registers
- The Internet
- Identify specific researchers to approach directly

**Cross-discipline:** where few SE studies exist, look to sociology (group working practices),
psychology (notation design / problem solving).

**Seven electronic sources (Brereton et al.):** IEEE Xplore · ACM DL · Google Scholar · CiteSeer
· Inspec · ScienceDirect · EI Compendex. Plus consider SpringerLink (EMSE) and SCOPUS.

#### Publication bias (§6.1.2)
Positive results more likely published. Worse for formal experiments (failure to reject H0 seen
as less interesting) and **worst when methods are sponsored by influential industry groups**
(US MoD and the CMM — few companies would publish negative results).
Countermeasures: scan grey literature; scan conference proceedings; contact experts/researchers
for unpublished results; **funnel plots** statistically (§6.5.7).

#### Documenting the search (§6.1.4) — transparent and replicable
- Documented in sufficient detail for readers to assess thoroughness
- **Documented as it occurs**, with changes noted and justified
- **Unfiltered search results saved and retained** for possible reanalysis

**Table 2 — search process documentation fields:**
| Source | Fields to record |
|---|---|
| Digital Library | Name of database; search strategy for that database; date of search; years covered |
| Journal hand searches | Name of journal; years searched; any issues not searched |
| Conference proceedings | Title of proceedings; name of conference (if different); title translation (if necessary); journal name (if published as part of a journal) |
| Efforts to identify unpublished studies | Research groups and researchers contacted (names + contact details); research web sites searched (date + URL) |
| Other sources | Date searched/contacted; URL; any specific conditions |

Must state a **rationale** for: which digital libraries; which journals/proceedings; and use of
electronic vs manual vs combined search.

#### Lessons learned for search (§6.1.5) — CAVEATS
- Alternative search strategies achieve different **completion criteria**; select and justify one
- **No single source finds all primary studies**
- **SE search engines are not designed to support SLRs**; unlike medicine, SE researchers must
  perform *resource-dependent* searches (per-engine adaptation) ← direct support for G2
- Kitchenham's very specific long search strings still produced many false positives; **"a
  simpler search string might have been just as effective"**

### 2.2 Study selection (§6.2)
Criteria decided during protocol definition (refinable during search); based on the research
question; **piloted** to ensure reliable interpretation and correct classification.

**Multistage process:**
1. Interpret criteria **liberally** at first — unless clearly excludable on title+abstract, get
   the full copy. *Caveat (Brereton): "The standard of IT and software engineering abstracts is
   too poor to rely on when selecting primary studies. You should also review the conclusions."*
2. Apply inclusion/exclusion on practical issues: language · journal · authors · setting ·
   participants/subjects · research design · sampling method · date of publication
3. Optional third stage on detailed quality criteria

**Staples & Niazi technique:** define the **complementary questions you are NOT investigating**
to sharpen exclusion criteria (worked CMM-based SPI example). "Directly improved and clarified
their primary study selection and data extraction process."

**Excluded-study logging — practical amendment:** textbooks say log all excluded studies.
Kitchenham recommends logging excluded papers **only after totally irrelevant papers are
removed** — record those excluded by the *detailed* criteria.

**Caveats:**
- Medicine avoids language-based exclusion; may matter less in SE
- Inclusion decisions could be biased by knowledge of authors/institutions/journals/year.
  **Experimental evidence suggests masking does not improve reviews**, and it costs time.

#### Reliability of inclusion decisions (§6.2.3)
- Two or more researchers → **Cohen's Kappa**; the *initial* Kappa value should be documented in
  the final report
- **Each disagreement must be discussed and resolved** — refer to the protocol or write to authors
- Uncertainty → **sensitivity analysis**
- **Single researcher:** discuss with advisor/expert panel; **or apply a test–retest approach —
  re-evaluate a random sample of the primary studies found after initial screening to check
  consistency of their own decisions** ← the intra-rater requirement (G4)

### 2.3 Study quality assessment (§6.3)
**Five purposes:** more detailed inclusion/exclusion criteria; investigate whether quality
differences explain result differences; weight studies in synthesis; guide interpretation and
strength of inference; guide recommendations for further research.

**No agreed definition of "quality".** CRD + Cochrane: quality = extent to which the study
minimises bias and maximises internal and external validity.

**Table 3 — quality concepts:**
| Term | Synonyms | Definition |
|---|---|---|
| Bias | Systematic error | Tendency to produce results departing systematically from the 'true' results. Unbiased results are internally valid. |
| Internal validity | Validity | Extent to which design and conduct prevent systematic error. **Prerequisite for external validity.** |
| External validity | Generalisability, Applicability | Extent to which observed effects apply outside the study. |

#### Hierarchy of evidence (§6.3.1) — and its critique
Traditional: SLRs and RCTs at top, quasi-experiments and expert opinion at bottom.
**Petticrew & Roberts: too simplistic.** Different designs suit different *question types* —
qualitative beats RCT for "do practitioners find this technology appropriate". Restrict to
designs **best suited to your specific question**, not a fixed hierarchy.

**Warning on observational studies:** large observational results have been overturned by RCTs
(vitamin C / heart disease — vitamin C use was a *surrogate* for lifestyle). Matters in SE
because much cost-estimation and success-factor research is correlational. Good observational
studies must consider confounders, measure them, adjust analyses, and include sensitivity
analysis for measured **and unmeasured** confounders.

#### Table 4 — Four types of bias (SE-adapted protection)
| Type | Synonyms | Definition | Protection mechanism |
|---|---|---|---|
| Selection bias | Allocation bias | Systematic difference between comparison groups w.r.t. treatment | Randomisation of a large number of subjects with concealment of the allocation method (allocation by computer program, not experimenter choice) |
| Performance bias | — | Systematic difference in conduct of comparison groups apart from the treatment | Replication using different experimenters; experimenters with no personal interest in either treatment |
| Measurement bias | Detection bias | Systematic difference between groups in how outcomes are ascertained | Blinding outcome assessors to treatments (sometimes possible) |
| Attrition bias | Exclusion bias | Systematic differences between groups in withdrawals/exclusions | Report reasons for all withdrawals; sensitivity analysis including all excluded participants |

*Medicine relies on blinding subjects and experimenters; usually impossible in SE.*

#### Building a quality instrument (§6.3.2)
Refine Table 4 with **generic items** (features of designs: survey, experimental, qualitative)
and **specific items** (review's subject area). Organise by **study stage: Design · Conduct ·
Analysis · Conclusions**.

**Table 5** = quantitative checklist; columns = {Quantitative empirical (no specific type),
Correlation (observational), Surveys, Experiments}; rows grouped by the four stages.
*Design:* aims clearly stated; study designed with these questions in mind; measures allow
questions to be answered; what population studied; who included/excluded; how sample obtained;
survey method likely to introduce bias; sample representative; treatments randomly allocated;
comparison/control group present; control participants similar on outcome-affecting variables;
sample size justified; technology clearly defined; could subject choice influence effect size;
could lack of blinding introduce bias; variables adequately measured (valid & reliable);
measures fully defined; measures most relevant for the questions; scope (size and length)
sufficient.
*Conduct:* untoward events; outcome assessment blind to treatment group; data collection methods
adequately described; groups treated similarly; drop-out proportion; how randomisation carried out.
*Analysis:* response rate; denominator reported; data types explained; participants/observational
units adequately described (SE experience, type — student/practitioner/consultant, nationality,
task experience); basic data adequately described; drop-outs introduced bias; reasons for
refusal; statistical methods described/justified/referenced to a tool; purpose of analysis clear;
scoring systems described; **confounders adequately controlled**; numbers add up across tables;
control for baseline differences (and was it successful); statistical significance assessed;
actual p value given; confidence limits on magnitude; evidence of multiple testing or many
post-hoc analyses; how could selection bias arise; side effects reported.
*Conclusions:* all study questions answered; what main findings mean; **negative findings
presented**; practical significance discussed; limitations from differing drop-outs; how null
findings interpreted (was small sample size considered); important effects overlooked; how
results compare with previous reports; how results add to the literature; implications for
practice; consequences of validity/reliability problems with measures.

**Table 6 — 18-item qualitative checklist:**
1 How credible are the findings? · 1.1 If credible, are they important? · 2 How has knowledge or
understanding been extended? · 3 How well does the evaluation address its original aims and
purpose? · 4 How well is the scope for drawing wider inference explained? · 5 How clear is the
basis of evaluative appraisal? · 6 How defensible is the research design? · 7 How well defined
are the sample design / target selection of cases/documents? · 8 How well is eventual sample
composition and coverage described? · 9 How well was data collection carried out? · 10 How well
has the approach to, and formulation of, analysis been conveyed? · 11 How well are contexts and
data sources retained and portrayed? · 12 How well has diversity of perspective and context been
explored? · 13 How well have detail, depth and complexity (richness) been conveyed? · 14 How
clear are the links between data, interpretation and conclusions? · 15 How clear and coherent is
the reporting? · 16 How clear are the assumptions / theoretical perspectives / values that
shaped the evaluation? · 17 What evidence of attention to ethical issues? · 18 How adequately
has the research process been documented?

**Do not use all questions** — select those appropriate to your questions (Fink). May need a
**measurement scale per item** since Yes/No can mislead. The instrument **must be assessed for
reliability and usability during protocol trials** before full application.

**Worked example of a scored instrument** (Kitchenham et al.) — 5 study-quality issues with
numeric anchors, e.g. within-company dataset size: <10 projects = 0 (poor); 10–20 = 0.33 (fair);
21–40 = 0.67 (good); >40 = 1 (excellent). Hold-out method: independent hold-out 0.5 / random
subsets 0.33 / leave-one-out 0.17 / no hold-out 0. Separately, **4 reporting-quality questions**.
> **"It is good practice not to include quality of study and quality of reporting scores in a
> single metric"** — they used a weighted measure giving *less* weight to reporting quality.

#### Using the quality instrument (§6.3.3) — two distinct uses, different data flows
1. **To assist primary study selection** → quality data become detailed inclusion/exclusion
   criteria and **must be collected prior to main data collection, using separate forms**.
2. **To assist data analysis/synthesis** → identify subsets and test whether quality differences
   associate with outcomes; **may be collected at the same time as main extraction, joint form**.
Both may coexist.
- **Weighting meta-analysis results by quality score is NOT recommended by any medical guideline.**
- Mixed study types require **an instrument per study type**; qualitative + quantitative reviews
  **essentially require different checklists**.

#### Limitations of quality assessment (§6.3.4) — CAVEATS
- Primary studies are often poorly reported → may be impossible to assess a criterion.
  **"It is tempting to assume that because something wasn't reported, it wasn't done. This
  assumption may be incorrect."** Try to obtain more information from the authors.
- Petticrew & Roberts: checklists must address **methodological quality, not reporting quality**.
- Limited evidence linking supposed validity factors to actual outcomes. Only inadequate
  concealment of allocation and lack of double-blinding are empirically shown to over-estimate
  treatment effects.
- You can identify bad statistics but cannot correct them without the original data — and SE data
  is often confidential or withheld.

### 2.4 Data extraction (§6.4)
Forms **defined and piloted when the protocol is defined**, to reduce bias.

**Form design (§6.4.1):** collect all information for the review questions AND quality criteria.
Separate forms if quality drives inclusion/exclusion; joint form if quality feeds analysis.
Numerical data are **a prerequisite for meta-analysis**. Pilot on a sample; if several
researchers will use the forms, **all take part in the pilot**. Pilots assess technical issues
(completeness) and usability (clarity of instructions, ordering of questions). Electronic forms
facilitate later analysis.

**Standard fields (§6.4.2):** Name of reviewer · Date of data extraction · Title, authors,
journal, publication details · Space for additional notes.

**Procedures (§6.4.3):**
- Whenever feasible, **two or more researchers extract independently**; compare; resolve by
  consensus or arbitration by an additional independent researcher; unresolved uncertainty →
  sensitivity analysis. **A separate form must be used to mark and correct errors or
  disagreements.**
- If resource constraints prevent double extraction, **have a random sample reviewed by all
  researchers** to assess inter-researcher consistency.
- Single researchers: supervisor extracts a random sample and cross-checks; **or test–retest — a
  second extraction from a random selection of primary studies**.
- **Extractor / checker split**: one completes the form, another confirms correctness. **They
  also ensured the data extractor was never a co-author of the primary study** — explicit COI
  control.
- Jørgensen (solo): **sent extracted data to an author of each primary study for confirmation**.

**Multiple publications of the same data (§6.4.4):** must not be included multiple times —
duplicates seriously bias results. Contact authors to confirm. **Use the most complete report**,
but it may be necessary to consult all versions to obtain all data.

**Unpublished/missing/manipulated data (§6.4.5):** include studies in progress if quality
information is obtainable **and written permission is available**. Contact authors for missing or
ambiguous data. If data must be recreated by manipulation, **report data first as published**,
and subject manipulated data to sensitivity analysis.

**Lessons (§6.4.6):** extractor/checker split helps at volume; **team members must understand the
protocol and the extraction process**.

### 2.5 Data synthesis (§6.5)
Specified in the protocol, but some issues can't be resolved until data are analysed (subset
analysis for heterogeneity is unnecessary if no heterogeneity is evident).

#### Descriptive / narrative synthesis (§6.5.1)
Tabulate intervention, population, context, sample sizes, outcomes, study quality consistent with
the review question. **Tables structured to highlight similarities and differences.** Identify
whether results are homogeneous or heterogeneous; tabulate to display potential sources of
heterogeneity (study type, quality, sample size).
*Techniques:* tabulate **by outcome** (three tables: no significant difference / within-company
better / no statistical tests) and flag complete replications offering no independent evidence.
Code studies **chronologically** to look for associations between study age and outcome.

#### Quantitative synthesis (§6.5.2)
Tabulate: sample size per intervention; estimated effect size per intervention with standard
errors; difference between means with CI; units of effect.

**Binary outcome effect measures:** Odds · Risk (proportion/probability/rate) · Odds ratio (OR) ·
Relative risk (RR) · Absolute risk reduction (ARR). (20/100 failures → odds 0.25, risk 0.20.)
*Trade-off:* odds/OR poorly understood by non-statisticians but mathematically desirable; risk
measures easier to understand; relative measures more statistically consistent, **but decision
makers need absolute values to assess real benefit.**

**Continuous outcome effect measures:** Mean difference · **Weighted mean difference (WMD)**
(same scale; weight = inverse of study variance) · **Standardised mean difference (SMD)**
(different scales; mean difference ÷ within-groups SD).
*Caveat:* **SMDs are only valid if differences in standard deviations reflect differences in
measurement scale, not real differences among trial populations.**

#### Presentation (§6.5.3)
**Forest plot** — line = standard error of the difference; box = mean difference, **box size
proportional to number of subjects**; may be annotated with n per group, mean difference and CI.
With formal meta-analysis the bottom entry is the summary estimate + CI.
Greatly differing effects → heterogeneity → single summary statistic is of little value;
investigate reasons.
**Anti-fishing rule: identify possible sources of heterogeneity when constructing the protocol**,
not post hoc. Often useful to synthesise different study types separately and check consistency.

#### Qualitative synthesis (§6.5.4) — Noblit & Hare's three approaches
- **Reciprocal translation** — studies about similar things, additive summary; "translate" each
  case into each of the other cases
- **Refutational synthesis** — studies implicitly/explicitly refute each other; translate both
  studies and refutations, analysing refutations in detail
- **Line of argument synthesis** — infer about the whole from studies each looking at a part;
  two-part: analyse individual studies, then the set as a whole (similar to descriptive
  synthesis: identify issues of importance, document and tabulate each study's approach)

#### Mixed qualitative + quantitative (§6.5.5)
1. Synthesise quantitative and qualitative **separately**
2. Integrate by investigating whether qualitative results **explain** the quantitative results
Model: Sutcliffe et al. did three syntheses — statistical meta-analysis, thematic qualitative
synthesis, and a **"cross-study synthesis"** using qualitative results to interpret the
meta-analysis.

#### Sensitivity analysis (§6.5.6)
Repeat analysis on subsets: high-quality studies only · particular study types · studies where
extraction presented no difficulties (excluding residual disagreement) · by experimental method.
Without formal meta-analysis: annotate forest plots to identify high-quality studies; order by
decreasing quality or study-type hierarchy; **colour-code reliability** (grey = less reliable,
black = reliable).
With descriptive synthesis it is more subjective, but still consider the impact of excluding
poor-quality studies or particular types.
*Example:* Turner et al. removed primary studies authored by the developer of the TAM model.

#### Publication bias (§6.5.7)
**Funnel plot** — treatment effect vs inverse of variance (or sample size). Symmetric funnel = no
evidence of publication bias (small samples vary more). **Asymmetry suggests publication bias →
results must be treated with caution.**

#### Lessons on synthesis (§6.5.8) — CAVEATS
- SE SLRs are **likely to be qualitative/descriptive** in nature
- Even with quantitative information, **meta-analysis is often impossible because reporting
  protocols vary so much between studies**
- Tabulation is useful aggregation, **but you must explain how the aggregated data actually
  answer the research questions**

---
## PHASE 3 — REPORTING

### 3.1 Dissemination strategy (§7.1)
Plan during commissioning or protocol preparation. Beyond journals/conferences: (1)
practitioner-oriented journals and magazines, (2) press releases to popular and specialist press,
(3) short summary leaflets, (4) posters, (5) web pages, (6) direct communication to affected
bodies. ← *precursor of Cartaxo's Evidence Briefings*

### 3.2 Report format (§7.2)
**Two formats:** a technical report / thesis chapter AND a journal or conference paper. Because
papers have size limits, **journal papers should reference a technical report or thesis
containing all the details**.

### 3.3 Table 8 — Structure and contents of an SLR report (CRD-derived)
| Section | Subsection | Scope / comments |
|---|---|---|
| Title\* | | Short but informative, based on the question; in journal papers **must indicate it is a systematic review** |
| Authorship\* | | Criteria for credit and author order **defined in advance**; non-author contributors in Acknowledgements |
| Executive summary / Structured abstract\* | Context; Objectives; Methods; Results; Conclusions | Methods = data sources, study selection, quality assessment, data extraction. Results = main findings incl. meta-analysis and sensitivity analyses. Conclusions = implications for practice and future research |
| Background | | Justification of the need for the review; summary of previous reviews; description of the technique and its importance |
| Review questions | | Each question specified; identify **primary and secondary** questions |
| Review methods | Data sources and search strategy; Study selection; Study quality assessment; Data extraction; Data synthesis | Based on the protocol. **Any changes to the original protocol must be reported** |
| Included and excluded studies | | Inclusion/exclusion criteria; list of excluded studies with rationale. **Best represented as a flow diagram** because studies are excluded at different stages for different reasons ← PRISMA-flow precursor |
| Results | Findings; Sensitivity analysis | Description of primary studies; quantitative summaries; meta-analysis details. Non-quantitative summaries in tabular form; quantitative in tables and graphs |
| Discussion | Principal findings; Strengths and weaknesses; Meaning of findings | Strengths/weaknesses of the evidence **and** bias in the systematic review itself; relation to other reviews incl. differences in quality and results. Direction and magnitude of effect; applicability/generalisability; extent to which results imply causality; all benefits, adverse effects and risks; variations in effects and their reasons |
| Conclusions | Recommendations | Practical implications for software development; unanswered questions and implications for future research |
| Acknowledgements\* | | Contributors not fulfilling authorship criteria |
| **Conflict of interest** | | **Any secondary interest (e.g. financial interest in the technology evaluated) must be declared** |
| References and Appendices | | Appendices list included/excluded studies, document search strategy details, list raw data |

(\* = not relevant for a PhD thesis.)

### 3.4 Evaluating review reports (§7.3)
Journal articles are peer reviewed; theses examined; **technical reports usually are not**. If
published on the Web, organise a peer review — ideally the **same expert panel that reviewed the
protocol**. Evaluation can use the §5.1 quality checklists (DARE/CRD).

### 3.5 Lessons on reporting (§7.4) — CAVEATS
- **Keep a detailed record of decisions made throughout the review process**
- **Report deviations from the protocol** (Staples & Niazi)
- SE needs publication mechanisms for longer papers / electronic appendices

---
## SECTION 8 — SYSTEMATIC MAPPING STUDIES (per this document)
Also known as **Scoping Studies**. Purpose: wide overview of a research area; establish if
research evidence exists; indicate the **quantity** of evidence. Results identify areas suitable
for SLRs and areas where a primary study is more appropriate. May be requested by an external
body **before** commissioning an SLR to target resources. Useful to PhD students.

**Five stated differences from an SLR:**
1. **Broader research questions**, often multiple
2. **Less focused search terms**, likely returning very many studies — **less of a problem than
   for an SLR because the aim is broad coverage rather than narrow focus**
3. **Extraction is much broader** — "more accurately termed a classification or categorisation
   stage"; classify with sufficient detail to answer broad questions and identify papers for
   later reviews **without being a time-consuming task**
4. **Analysis is summarising** — unlikely to include meta-analysis or narrative synthesis;
   **totals and summaries**; graphical representations of study distributions by classification
   type are effective
5. **Dissemination may be more limited** — commissioning bodies and academic publications, aimed
   at influencing future primary research

> **KEY FOR THIS PROJECT:** supports SMS protocol ≈ SLR protocol minus quality evaluation, with
> classification replacing extraction and descriptive totals replacing synthesis. NOTE: Kitchenham
> does NOT explicitly say quality assessment is omitted from an SMS — verify against Petersen
> 2008/2015 before encoding that as policy.

## §9 Final remarks — scope caveat
Derived from medical guidelines but SE "is not the same as medical research" — no RCTs, no
blinding — so this version incorporates social-science textbooks. Intended for PhD students as
well as large groups, **but many steps assume more than one researcher**.
