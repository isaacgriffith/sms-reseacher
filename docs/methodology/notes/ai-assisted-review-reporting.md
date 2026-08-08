# Extraction notes — reporting AI use inside the review process

Covers `holst_transparent_2025.pdf`. Composed by the orchestrating agent rather than a subagent, so
it follows the schema in [`README.md`](./README.md) but quotes a little more heavily where the
paper's own hedging is load-bearing.

Fed chapter [14 — AI-assisted review reporting](../14-ai-assisted-review-reporting.md), with
secondary entries in [10](../10-reporting-and-evaluation.md), [11](../11-caveats-register.md) and
[12](../12-platform-implications.md).

---

## holst_transparent_2025 — Transparent Reporting of AI in Systematic Literature Reviews: Development of the PRISMA-trAIce Checklist

Holst D, Moenck K, Koch J, Schmedemann O, Schüppstuhl T. *JMIR AI* 2025;4:e80247.
doi:10.2196/80247. Institute of Aircraft Production Technology, Hamburg University of Technology.
Open access, CC BY 4.0. Submitted 2025-07-07, accepted 2025-10-12, published 2025-12-10. 8 pages.
First four authors marked as contributing equally.

**Type:** proposed reporting guideline — a methodological proposal, **explicitly not a
consensus-derived standard**. The authors state this twice, in Methods §Limitations and again in
Discussion §Limitations.

**Role in corpus:** the only source addressing **AI used as a tool *within* the review process**
rather than AI as the *subject* of a review. Every other reporting standard in the corpus (SEGRESS,
PRISMA 2020) is silent on this; every AI reporting standard it draws on (CONSORT-AI, TRIPOD-AI,
TRIPOD-LLM, DECIDE-AI, SPIRIT-AI) governs AI as the object of study. It supplies a checklist mapped
onto PRISMA 2020's section structure, plus an adapted flow diagram.

**Relevance to this repository is unusually direct**: the platform *is* the AI tool this checklist
demands disclosure of. Most of the corpus tells the platform how a review should be conducted; this
paper tells it what it must be able to *emit about itself*.

---

### Process steps or stages defined

#### A. The three-stage method that produced the checklist (Methods §Formulation)

1. **Targeted literature search** for established, consensus-based AI reporting guidelines, sourced
   primarily from the **EQUATOR Network** (Enhancing the Quality and Transparency of Health
   Research), described as "a recognized authority on such standards". Search keywords included
   "artificial intelligence", "machine learning", and "reporting guideline".

   Six guidelines were selected for adaptation:

   | Guideline | Full name | Governs |
   | --------- | --------- | ------- |
   | **CONSORT-AI** | Consolidated Standards of Reporting Trials–AI | Clinical trial reports for AI interventions |
   | **SPIRIT-AI** | Standard Protocol Items: Recommendations for Interventional Trials–AI | Clinical trial *protocols* for AI interventions |
   | **TRIPOD-AI** (cited as TRIPOD+AI) | Transparent Reporting of a Multivariable Prediction Model of Individual Prognosis or Diagnosis–AI | Clinical prediction models using regression or ML |
   | **TRIPOD-LLM** | …–Large Language Model | Studies using LLMs |
   | **DECIDE-AI** | Developmental and Exploratory Clinical Investigations of Decision Support Systems Driven by AI | Early-stage clinical evaluation of AI decision support |
   | **GAMER** | Generative Artificial Intelligence Tools in MEdical Research | Generative-AI tool use in medical research |

   Selection rationale given: CONSORT-AI and TRIPOD-AI "represent the most widely adopted,
   cross-domain standards for research involving AI", so they supply the most consensus-driven
   foundation available.

2. **Item extraction and qualitative content analysis.** Every individual checklist item from the six
   selected guidelines was extracted. The stated guiding question for the analysis was whether a
   given reporting principle is relevant and applicable to the use of AI as a *methodological tool*
   in an SLR.

   Each item was evaluated against **three criteria**:
   - relevance to **reproducibility**
   - **feasibility** for authors
   - **adaptability** to the SLR context

   Items judged irrelevant were dropped — the worked example given is items concerning the patient
   safety of an AI intervention. The analysis is said to have concentrated on principles covering
   disclosure of AI models, data origins, and explicit description of human–AI interaction and
   oversight.

3. **Thematic synthesis** of the retained items into recurring core concepts — the two named
   examples are "AI tool identification" and "human-AI interaction". The resulting thematic clusters
   were then **mapped onto the existing PRISMA 2020 section structure**, the stated purpose being
   seamless integration and user-friendliness for readers already fluent in PRISMA 2020.

> The method is therefore **adaptation of prior consensus, not new consensus**. The authors are
> explicit that this was a deliberate trade: "a multiyear, de novo consensus process would risk
> producing an obsolete guideline upon publication" (Methods §Formulation). See *Caveats* below.

#### B. The proposed governance model — a "living guideline" (Discussion §Rationale)

Not a review process, but a process for the *standard itself*, and the part most likely to date the
paper. Two tiers:

1. **A central, stable anchor on GitHub** — `https://github.com/cqh4046/PRISMA-trAIce` — declared
   "the single source of truth for the checklist", enabling transparent, version-controlled
   development. The Data Availability statement says this repository "contains the latest version of
   the PRISMA-trAIce guideline and documents all version changes".
2. **A dynamic community hub on Discord**, for "rapid and low-friction collaboration".

A schedule of **annual reviews** is envisioned to fold in community feedback. The stated long-term
intent is to constitute a **formal steering committee** from the expert community and transfer
stewardship of the standard to it. The authors describe this as applying open-source development
principles to scientific standard setting.

**Consequence for anyone citing this paper:** the paper is a *snapshot*, and by its authors' own
design is expected to diverge from the canonical checklist over time.

---

### Clarifications and refinements to earlier guidance

| Prior guidance | What this paper changes |
| -------------- | ----------------------- |
| **PRISMA 2020 flow diagram** already contains an "automation tools" concept in its de-duplication box | Sharpened into a distinction between **rule-based administrative tools** (deduplication is the given example) and **evaluative AI systems**. The adapted diagram adds separate fields for the number of records screened and excluded **by AI systems versus by human reviewers**, with reasons for exclusion |
| **PRISMA-AI**, announced 2022 | Still unpublished as of this paper. More importantly, per its planning document on the EQUATOR site, its conceptual focus is reporting SLRs that **investigate AI as a subject of research in clinical medicine** — a different problem. trAIce claims the vacant slot |
| **CONSORT-AI, TRIPOD, TRIPOD-LLM** | Described as "indispensable" where AI is the *subject* of research — a diagnostic intervention or a clinical prediction model. They guide reporting of the AI's performance and impact *as a study outcome*. trAIce addresses the case where AI is "part of the research process itself" |
| **GAMER** | Acknowledged as offering valuable recommendations on reporting AI tool use, but "explicitly tailored to the field of medicine". trAIce's claim to distinction is being **discipline-agnostic and SLR-specific** by virtue of extending PRISMA 2020 |

The claimed niche, stated in Discussion §Comparison With Prior Work, rests on two axes taken
together: **AI as tool (not subject)** × **discipline-agnostic and SLR-specific**.

---

### Checklists, rubrics, scoring schemes, evaluation criteria

#### The PRISMA-trAIce checklist (Table 1)

**It is a checklist, not a scored instrument** — there are no anchors, weights, or totals. Items are
paraphrased below; the source Table 1 carries the official wording and
[Multimedia Appendix 1](#extraction-limits-and-source-defects) carries per-item rationale and
examples.

| Item ID | Label | What it requires, paraphrased |
| ------- | ----- | ----------------------------- |
| **T1** | Title | Where AI played a **substantial** role (primary screening, data extraction are the given examples), *consider* indicating AI assistance in the title or subtitle. **The only item phrased as a suggestion rather than a requirement** |
| **A1** | Abstract | Briefly summarise which AI tools were used, at which SLR stages, and their primary role |
| **I1** | Introduction | State the rationale for using AI for specific tasks — the examples offered are managing literature volume, efficiency, and exploring novel methods |
| **M1** | Protocol and Registration | If AI tools or AI-assisted methods were **pre-specified in the protocol**, say so and give the protocol's location. **Report any deviations from the protocol regarding AI use** |
| **M2** | Identification and Access | Per tool: (a) name, version number where applicable, developer/provider; (b) how the tool can be accessed — URL, repository, commercial availability, local instance; (c) for custom tools or scripts, core functionality and how to access or replicate it, including code repository, dataset, or base model of a fine-tuning process |
| **M3** | Purpose and Stage of Application | Per tool: (a) which SLR stage(s) it was applied at — search, screening, data extraction, risk-of-bias assessment, synthesis, drafting; (b) the precise task(s) intended at each stage |
| **M4** | Input Data | (a) For tools that learn or are fine-tuned: origin, nature and preparation of any training, fine-tuning or calibration data specific to this review; (b) for tools applied to review data: what was fed in — search results, abstracts, full texts, specific datasets |
| **M5** | Output Data | What each tool produced, **including the output format** (structured JSON, plain text, classification labels with confidence scores are the given examples) **and any automated post-processing applied to the raw output before human review** |
| **M6** | Prompt Engineering (if any) | Per LLM/GenAI tool: (a) **the full prompts** for each task — or, if extensive, a detailed description of structure, key instructions, context supplied (inclusion/exclusion criteria, PICO elements) and any few-shot examples, plus where the full prompts can be accessed; (b) key output-influencing parameters — temperature, max tokens, top-p; (c) any iterative prompt-refinement process based on initial outputs or pilot testing |
| **M7** | Operational Details and Settings | For non-LLM AI tools, or in addition to prompts: (a) key algorithms or models employed, where known and relevant; (b) settings, parameters and configurations that could influence performance — classification thresholds in screening tools, active-learning parameters |
| **M8** | Human-AI Interaction and Oversight | The largest item. Per stage: how many reviewers interacted with or validated AI outputs per task; whether reviewers worked **independently** when validating; reviewer **qualifications or training** for AI-assisted tasks; **how AI outputs were presented** to reviewers; **what proportion of AI outputs were manually verified**; how discrepancies were resolved — AI-vs-human and human-vs-human; any calibration process for reviewers or the tool; the standard procedure for human verification. **Sub-item labelling is defective — see below** |
| **M9** | AI Performance Evaluation (Methods) | Hedged with "if applicable and feasible". May include: (a) the **reference standard** used — consensus human decisions is the given example; (b) metrics — accuracy, sensitivity, specificity, precision, recall, F1; (c) analyses conducted to assess **model bias or rate of erroneous outputs**; (d) any pilot testing or validation prior to full implementation |
| **M10** | Data Governance and Ethics | How data handled by AI tools — input, output, intermediate — was managed and stored, and measures taken for privacy, security, and **compliance with copyright or terms of service, especially for third-party cloud-based tools** |
| **R1** | Study selection (AI-assisted) | The flow diagram and text must **distinguish records excluded or included by AI decision from those by human reviewer decision, at each screening stage where AI was used**. Report the number of records processed by AI and the outcomes |
| **R2** | AI Performance Metrics (Results) | Report the results of any M9 evaluation, including quantitative results and **measures of agreement between AI and human reviewers** where assessed |
| **D1** | Limitations of AI Use | Limitations encountered — technical issues, biases identified, prompt-engineering difficulties, unexpected outputs, task-specific performance limits — **and how they might have influenced the review process or findings** |
| **D2** | Implications of AI Use | The experience of using the tools: perceived benefits (efficiency, ability to handle larger datasets), challenges, usability, and implications for future reviews |

**Structural observations** (mine, not the paper's):

- The checklist is **modular by SLR section**, not by AI stage. A tool used at three stages is
  reported once under M2/M3 and again per stage under M8.
- **M2, M4, M5, M6, M7 are jointly a reproducibility bundle**: identity, inputs, outputs, prompts,
  settings. Together they are close to sufficient to re-run the tool.
- **M8 and R1 are the human-accountability pair**, and they are the two items a fully automated
  pipeline would find hardest to answer honestly.
- **M9/R2 are the only conditional pair** — "if applicable and feasible" appears at M9 and R2 is
  scoped to "any performance evaluations". Nothing else in the checklist is optional in this way.

#### Evaluation criteria the paper applies to *itself*

Not a rubric, but the three criteria used to filter candidate items are reusable as an acceptance
test for any future item: **relevance to reproducibility · feasibility for authors · adaptability to
the SLR context** (Methods, stage 2).

---

### Threats to validity framework

**None offered.** The paper defines no validity categories and does not use a threats-to-validity
frame; its Limitations sections are prose. It should not be cited as a source for validity
classification.

It does, however, imply an **evaluation axis absent from the rest of the corpus**: the performance of
the review *instrument* against a human reference standard (M9/R2). Every quality instrument in the
corpus — DARE, Petersen's rubrics, Dybå & Dingsøyr's checklist, Garousi's grey-literature
instrument — scores *the studies* or *the review*. None scores *the tool used to conduct the review*.

---

### Data extraction and analysis techniques

**The paper's own technique**: qualitative content analysis over extracted checklist items, followed
by thematic synthesis into clusters, then mapping to a target structure. No coding frame, coder
count, agreement statistic, or saturation criterion is reported — so it cannot be cited as a worked
example of thematic synthesis in the sense of `cruzes_recommended_2011`.

**What the checklist demands of extraction**, which is the part that bears on this platform:

- **M4b** — the data fed to the tool must be named at the granularity of search results / abstracts /
  full-text articles.
- **M5** — output **format** and **automated post-processing before human review** must be reported.
  This is the item that catches a pipeline which silently normalises, thresholds or filters model
  output before a human ever sees it.
- **M8e** — the **proportion of AI outputs manually verified** must be reported. A number, not a
  policy statement.
- **M8f** — the discrepancy-resolution procedure must cover **AI-versus-human** disagreement, not
  only human-versus-human. This is a genuine extension: the rest of the corpus specifies
  disagreement resolution only between human reviewers.
- **M9a** — where AI performance is evaluated, the **reference standard** must be stated; consensus
  human decisions is the suggested one.

---

### Empirical findings worth citing

> **⚠ This paper reports no empirical findings of its own.** It is a proposal. Every number in it is
> cited from another source, and must be attributed to that source rather than to Holst et al. The
> playbook's principle 5 applies with unusual force here.

Numbers appearing in the paper, with their true origin:

| Figure | Claim | Actually from |
| ------ | ----- | ------------- |
| **50%–75%** | Reduction in manual workload achievable with AI in evidence synthesis | Abogunrin, Muir, Zerbini & Sarri 2025, *Front Pharmacol* 16:1454245 — a pragmatic review quantifying workload efficiencies and cost savings. **Cited, not measured here** |
| **6** | Guidelines selected for adaptation | This paper *(derived — the count is not stated numerically in the text; it is the length of the list in Methods)* |
| **14** | Stated number of checklist items | This paper — **and it disagrees with its own Table 1. See below** |
| **17** | Actual number of rows in Table 1 | *(derived — tallied from Table 1)* |

Uncited-but-attributed context claims the paper makes in its Introduction, all sourced elsewhere:
LLM hallucination and training-data bias as obstacles to SLR principles; AI tools now assisting in
"almost all phases" of the SLR process; SLR cost as a barrier to research outside well-funded groups.

**Authors' own AI-use disclosure** (Acknowledgments) is worth noting as a *worked example of the
practice the paper advocates*, and it is more specific than most: Gemini 2.5 Pro (Google DeepMind),
via its web interface, June–July 2025, used for conceptual brainstorming and elaboration of ideas,
supplementary web research and fact-checking, writing for readability and linguistic precision, and
initial consistency checks of arguments and terminology; interaction consisted of prompts, manuscript
drafts and source documents; all outputs critically reviewed, verified and edited by the authors.
They report observing **rare instances of erroneous outputs ("hallucinations")** and conclude that
this "reinforces that rigorous human quality control is mandatory".

Note that this disclosure would **not** fully satisfy the paper's own M6 — no prompts, parameters, or
access location are given. That is not hypocrisy (M6 scopes to AI use *in the review process*, not in
manuscript preparation), but it is an instructive boundary case.

---

### Caveats, traps and pitfalls

Attached to the process step each bites.

| # | Caveat | Bites at |
| - | ------ | -------- |
| 1 | **This is not a consensus standard.** It is a systematic adaptation, not "a formal, broad-based Delphi study or consensus meeting". Its items "have not yet been empirically validated across diverse research contexts" | Any decision to treat it as normative |
| 2 | **Feasibility was assessed on expert knowledge only** — no formal user study. Nobody has demonstrated that a review team can actually answer all 17 items | Adoption; effort estimation |
| 3 | **It is a living guideline by design**, with GitHub named as the single source of truth and annual revisions envisioned. The published table is a snapshot that is *expected* to go stale | Citing the paper rather than the repository |
| 4 | **The two-tier governance depends on infrastructure that may not persist** — a Discord server and a personal-account GitHub repository. The steering committee is stated as intent, not fact. This is the same link-rot exposure the corpus documents for grey literature, applied to a standard | Long-term reliance |
| 5 | **Provenance is entirely clinical/medical.** All six parent guidelines come from EQUATOR and medical research. The claim of discipline-agnosticism follows from extending PRISMA 2020, not from any cross-disciplinary validation | Applying it to SE without checking item fit |
| 6 | **"Black box" LLM behaviour, hallucinations, and training-data bias stand in direct contradiction to SLR principles** — the paper's own framing of the risk it addresses. The checklist makes AI use *visible*; it does not make it *valid* | Mistaking disclosure for rigour |
| 7 | **T1 is advisory where the rest is mandatory** — "consider indicating" AI assistance in the title. A checker treating T1 as required would over-report | Building an automated conformance checker |
| 8 | **M9 and R2 are conditional** ("if applicable and feasible"). This is the escape hatch a team under time pressure will take, and it removes exactly the evidence that would justify trusting the AI's decisions | Conformance checking; interpreting a conforming report |
| 9 | **Item count contradicts the table** — text says 14, Table 1 lists 17. See source defects | Quoting the item count |
| 10 | **M8's sub-item labels are malformed** and two of its sub-items overlap | Implementing M8 item-by-item |

---

### Extraction limits and source defects

Recorded per the playbook's principle 2 — defects in sources are noted, never silently corrected.

#### Extraction limits

| Limit | Detail |
| ----- | ------ |
| **Figure 1 — the adapted flow diagram** | An **image**. `pdftotext -layout` recovered the caption only; no box labels, no field names, no counts. The caption states the modification is "the addition of separate fields to distinguish between exclusions made by human reviewers and those made by artificial intelligence (AI) systems". **The diagram's actual fields are therefore not recoverable from the text layer and must be read from the PDF page image or the GitHub repository before being implemented** |
| **Multimedia Appendix 1** | "The PRISMA-trAIce statement—elaboration, explanation, and examples", a 29 KB DOCX. **Not present in `research/`.** It is the file carrying per-item rationale, sources, and application examples — i.e. exactly what an implementer needs. Every item paraphrase above rests on Table 1 alone |
| **`pdfinfo` stream warning** | `Syntax Error (255884): Can't revert non decrypt streams`. Text extraction nonetheless produced 5,146 words and the body appears complete; the warning is noted only so a later reader does not mistake it for truncation |

#### Defects in the source itself

| Defect | Detail |
| ------ | ------ |
| **Item count: 14 vs 17** | Results §The PRISMA-trAIce Checklist states the checklist "comprises 14 items". Table 1 contains **17** *(derived — tallied: T1, A1, I1, M1–M10, R1, R2, D1, D2)*. A plausible reconciliation is that 14 counts only the Methods, Results and Discussion items (10 + 2 + 2), excluding T1/A1/I1 — but **the paper does not say this**, and it is not asserted here as fact |
| **M8 sub-item labels are malformed** | The sub-items run `a. b. c. d. e. f. g.` and then a **second `f.`** — "f. Describe the standard procedure for human verification of AI-generated outputs". So M8 carries **eight** sub-items under seven distinct labels |
| **M8 has semantically overlapping sub-items** | The duplicate-labelled final item ("standard procedure for human verification") substantially restates `e.` ("what proportion of AI outputs were manually reviewed/verified") and `g.` ("processes for calibrating human reviewers or the AI tool"). Whether it is a third distinct requirement or an editing artefact cannot be settled from Table 1 |
| **Typographical errors in M9** | "Analyzes conducted to access model bias" — reads as *analyses … to assess*; and "erroneous ouputs". Sub-item `c.` also lacks its terminating period. Minor, but they indicate Table 1 did not receive a final copy-edit, which weakens any argument that its exact wording is authoritative |
| **References 22 and 23 are the same paper** | Both are Gallifant J, Afshar M, Ameen S, et al., "The TRIPOD-LLM reporting guideline for studies using large language models", *Nat Med* 2025;31(1):60-69. Entry 23 adds a Medline ID; entry 22 does not. TRIPOD-LLM is cited in text as `[20,23]` and again as `[23]` |
| **TRIPOD-AI naming** | Reference 20 is Collins et al., **TRIPOD+AI** (BMJ 2024;385:e078378). The paper's abbreviation list and body call it **TRIPOD-AI**. The `+` form is the official name of that 2024 statement |

None of the above is fatal to the checklist's substance. Together they are consistent with the
paper's own self-description: a fast, deliberately preliminary proposal published ahead of consensus.

---

### One-line summary

A 17-item (self-described 14-item) extension to PRISMA 2020 for disclosing AI used **as a tool** in
conducting a systematic review — the first such standard, discipline-agnostic by construction,
adapted from six medical AI reporting guidelines, and **explicitly pre-consensus**.
