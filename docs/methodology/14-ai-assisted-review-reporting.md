# 14 — Reporting AI Use Inside the Review Process

**Primary source**: Holst, Moenck, Koch, Schmedemann & Schüppstuhl 2025, *Transparent Reporting of AI
in Systematic Literature Reviews: Development of the **PRISMA-trAIce** Checklist*, JMIR AI
2025;4:e80247, doi:10.2196/80247. Open access, CC BY 4.0.

**Supersedes nothing.** No earlier chapter and no superseded repo document covers this ground.

Every other reporting standard in this corpus governs the *review*. This one governs the **tool used
to conduct the review** — and that makes it the chapter with the most direct claim on this codebase,
because the platform *is* the tool whose disclosure it specifies.

> ### ⚠ STATUS — READ BEFORE TREATING ANY ITEM AS NORMATIVE
>
> **PRISMA-trAIce is a proposal, not an endorsed standard.** Its authors say so twice, in Methods
> §Limitations and Discussion §Limitations: it is "the result of a systematic adaptation, not a
> formal, large-scale consensus-building exercise, such as a Delphi study", and its items "have not
> yet been empirically validated across diverse research contexts". Feasibility was judged on expert
> knowledge; **no user study has shown that a review team can actually answer all the items.**
>
> This is a deliberate trade, not an oversight. The authors argue a multi-year consensus process
> "would risk producing an obsolete guideline upon publication", and that the immediate risk of
> non-transparent AI use outweighs the risk of a preliminary guideline.
>
> **Consequences for this repository:**
> - SEGRESS and PRISMA 2020 ([10](./10-reporting-and-evaluation.md)) are consensus-endorsed
>   standards. This is not. Do not file them at equal authority.
> - It is a **living guideline by design**. The authors name a GitHub repository —
>   `github.com/cqh4046/PRISMA-trAIce` — as "the single source of truth", with annual revisions
>   envisioned and stewardship intended to pass to a steering committee that does not yet exist.
>   **The published table is a snapshot and is expected to go stale.** Check the repository before
>   implementing item-by-item.
> - Adopt it as **a design specification for what the platform must be able to record and emit**.
>   That use does not depend on its consensus status. Adopt it as a *conformance score* only with
>   the status caveat attached.

---

## Why this is a separate concern

The corpus already contains reporting standards. None of them reaches this problem, and the reason is
a clean distinction the paper makes in Discussion §Comparison With Prior Work:

| | **AI as the subject of research** | **AI as a tool in the research process** |
| --- | --- | --- |
| What is reported | The AI's performance and impact **as a study outcome** | **How the tool was used to produce the review** |
| Governed by | CONSORT-AI, SPIRIT-AI, TRIPOD-AI/+AI, TRIPOD-LLM, DECIDE-AI | **Nothing, before this paper** |
| Example | An SLR of ML-based defect predictors | An SLR **screened by** an LLM |

**PRISMA-AI does not fill the second column.** It was announced in 2022 and remains unpublished; per
its EQUATOR planning entry, its focus is reviews that *investigate* AI as a subject in clinical
medicine. **GAMER** does address generative-AI tool use, but is explicitly scoped to medicine.

PRISMA-trAIce's claim to a distinct niche therefore rests on two axes held together: **AI as tool,
not subject** × **discipline-agnostic and SLR-specific**. The discipline-agnosticism is inherited
from extending PRISMA 2020 — it is *structural*, not demonstrated by cross-disciplinary validation.

> **⚠ CAVEAT — the provenance is entirely medical.** All six parent guidelines (CONSORT-AI,
> SPIRIT-AI, TRIPOD-AI, TRIPOD-LLM, DECIDE-AI, GAMER) come from the EQUATOR Network and clinical
> research. Items were filtered for SLR relevance, not for software-engineering fit. Where an item
> reads oddly for SE, that is why.

---

## How the checklist was built

Three stages (Holst et al. 2025 §Methods — Formulation of the PRISMA-trAIce Checklist):

1. **Targeted search** of EQUATOR for consensus-based AI reporting guidelines, on keywords
   "artificial intelligence", "machine learning", "reporting guideline". Six were selected.
2. **Item extraction and qualitative content analysis.** Every checklist item from all six was
   extracted and judged against one question — *is this reporting principle relevant and applicable
   to AI used as a methodological tool in an SLR?* — using **three criteria: relevance to
   reproducibility · feasibility for authors · adaptability to the SLR context**. Items about the
   patient safety of an AI intervention are the given example of what was dropped.
3. **Thematic synthesis** of what survived into recurring concepts ("AI tool identification",
   "human-AI interaction"), then **mapped onto PRISMA 2020's section structure** so that readers
   already fluent in PRISMA need learn no new organisation.

The three filter criteria are reusable: they are the acceptance test for any *additional* item this
platform might want to define.

> **⚠ CAVEAT.** The synthesis reports no coding frame, coder count, agreement statistic or saturation
> criterion. It cannot be cited as a worked example of thematic synthesis in the sense of
> [08](./08-extraction-and-synthesis.md) — and by the standard of caveat **G18** in
> [11](./11-caveats-register.md), its own methods account is thin.

---

## The checklist

**17 items** *(derived — tallied from Table 1)*, across the six sections of a review report. It is a
**checklist, not a scored instrument**: no anchors, no weights, no total.

> **⚠ The paper's own item count disagrees with its own table.** Results §The PRISMA-trAIce Checklist
> says the checklist "comprises **14** items". Table 1 contains **17**. The likeliest reconciliation
> is that 14 counts only the Methods, Results and Discussion items (10 + 2 + 2), excluding T1, A1 and
> I1 — but **the paper does not say this**, and it is not asserted here. Quote the count with care.

| Item | Requires, in paraphrase |
| ---- | ----------------------- |
| **T1** Title | Where AI played a substantial role — primary screening, data extraction — ***consider*** indicating AI assistance in the title or subtitle. **The only advisory item in the checklist** |
| **A1** Abstract | Which tools, at **which stages**, and their primary role |
| **I1** Introduction | The **rationale** for using AI for these specific tasks |
| **M1** Protocol | Whether AI use was **pre-specified in the protocol**, where the protocol lives, and **any deviation from it regarding AI use** |
| **M2** Identification and access | Per tool: name, **version**, developer/provider; how it can be **accessed**; for custom tools, core functionality plus code repository, dataset, or fine-tuning base model |
| **M3** Purpose and stage | Per tool: which SLR **stage(s)** — search, screening, extraction, risk-of-bias, synthesis, drafting — and the **precise task** at each |
| **M4** Input data | Training/fine-tuning/calibration data where the tool learns; **and what review data was fed in** — search results, abstracts, full texts |
| **M5** Output data | What came out, **its format** (structured JSON, labels with confidence scores), **and any automated post-processing applied before a human saw it** |
| **M6** Prompt engineering | **The full prompts** — or their structure, key instructions, supplied context and few-shot examples, plus where the full text can be accessed; **key parameters (temperature, max tokens, top-p)**; and any iterative refinement process |
| **M7** Operational settings | For non-LLM tools: algorithms/models, and settings that influence performance — **classification thresholds**, active-learning parameters |
| **M8** Human–AI interaction and oversight | How many reviewers validated AI output per task; whether they worked **independently**; their **qualifications or training**; **how outputs were presented**; **what proportion was manually verified**; how **AI-vs-human and human-vs-human** discrepancies were resolved; any calibration of reviewers or tool; the standard verification procedure |
| **M9** AI performance evaluation | *"If applicable and feasible"* — the **reference standard** (consensus human decisions), the **metrics** (accuracy, sensitivity, specificity, precision, recall, F1), analyses of **model bias or erroneous-output rate**, and any pilot/validation phase |
| **M10** Data governance and ethics | How input, output and intermediate data was managed and stored; privacy, security, and **compliance with copyright and terms of service, especially for third-party cloud tools** |
| **R1** Study selection | The flow diagram and text must **distinguish records included/excluded by AI decision from those by human decision, at every stage where AI was used**, and report how many records AI processed and with what outcome |
| **R2** AI performance metrics | The results of any M9 evaluation, including **measures of agreement between AI and human reviewers** |
| **D1** Limitations of AI use | Technical issues, identified biases, prompt-engineering difficulty, unexpected outputs — **and how each might have influenced the process or the findings** |
| **D2** Implications of AI use | The experience: benefits, challenges, usability, implications for future reviews |

### Reading the checklist structurally

Four groupings are more useful than the item order:

| Group | Items | What it is for |
| ----- | ----- | -------------- |
| **Reproducibility bundle** | M2 · M4 · M5 · M6 · M7 | Identity, inputs, outputs, prompts, settings. Together, near-sufficient to **re-run the tool** |
| **Human-accountability pair** | M8 · R1 | Who checked what, and which decisions were whose. **The two items a fully automated pipeline finds hardest to answer honestly** |
| **Evaluation pair** | M9 · R2 | Did the tool actually work, measured against a human reference standard |
| **Framing items** | T1 · A1 · I1 · D1 · D2 | Why AI was used, and what it cost |

> **⚠ CAVEAT — the escape hatch is in the evaluation pair.** M9 is hedged "if applicable and
> feasible" and R2 is scoped to "any performance evaluations" that were done. **Nothing else in the
> checklist is optional in this way.** A report can therefore conform fully while disclosing that an
> LLM screened every abstract *and* offering no evidence that it screened them correctly. That is the
> item a team under deadline will drop, and it is the one carrying the evidence that would justify
> trusting the review.

---

## The adapted flow diagram

PRISMA 2020's diagram already mentions "automation tools" in its de-duplication box
([10](./10-reporting-and-evaluation.md)). PRISMA-trAIce sharpens this in two ways:

1. **A distinction between rule-based administrative tools** — deduplication is the given example —
   **and evaluative AI systems.** Only the second kind makes judgements about a paper's relevance.
2. **Separate fields for records screened and excluded by AI systems versus by human reviewers**,
   with reasons for exclusion, at each stage where AI was used.

> **⚠ EXTRACTION UNCLEAR: the PRISMA-trAIce flow diagram's field labels.** Figure 1 is an **image**.
> Text extraction recovered the caption only — no box labels, no field names, no counts. The
> distinction above is taken from the caption and the surrounding prose, both of which are
> unambiguous about *what* was added; **the exact fields and their placement are not recoverable from
> the text layer.** Read the PDF page image or the project's GitHub repository before implementing
> the diagram. Recorded in the [README reliability table](./README.md#reliability-of-this-document).

> **⚙ IMPLEMENTATION — this compounds G14.** [10](./10-reporting-and-evaluation.md) already
> establishes that the PRISMA 2020 diagram needs **24 counts** across two structurally different
> column variants. PRISMA-trAIce **multiplies the screening counts by decision authority**: for each
> screening stage, records processed by AI, excluded by AI, excluded by human, with per-reason
> breakdowns. A `PaperDecision` log that cannot attribute each decision to an AI or a human reviewer
> cannot render this. **This platform can** — see [12](./12-platform-implications.md) and gap
> **G44** — which makes it one of the few requirements here that is close to already satisfied.

---

## Where this meets the rest of the corpus

### It supplies a missing evaluation axis

Every quality instrument in this corpus scores either **the primary studies** (Dybå & Dingsøyr's
checklist, Garousi's grey-literature instrument) or **the review** (DARE, the Petersen 2015 rubrics,
SEGRESS). **None scores the tool used to conduct the review.** M9/R2 is that axis, and it is the only
one in the corpus.

| Instrument | Measures | Consensus-endorsed? |
| ---------- | -------- | ------------------- |
| SEGRESS | Reporting completeness of the review, per review type | Yes |
| PRISMA 2020 | Reporting completeness of the review | Yes — and **must not** be used for quality |
| DARE | Review quality | Yes, by adoption |
| Petersen 2015 rubrics | Process actions taken | Yes, by adoption |
| **PRISMA-trAIce** | **Reporting completeness of AI *tool* use** | **No — proposal stage** |

Note the last row measures **reporting completeness**, exactly like SEGRESS and PRISMA. So caveat
**A6** in [11](./11-caveats-register.md) transfers directly: *a trAIce conformance score is not a
measure of whether the AI was used well.* It measures whether you said what you did.

### It extends disagreement resolution to a new pair

The whole corpus specifies disagreement resolution **between human reviewers** — Kitchenham's
consensus protocol, the tertiary study's minority report, Cohen's κ, the Petersen 2015 decision-rule
table. **M8f is the first requirement in the corpus to demand a procedure for AI-versus-human
disagreement**, which is a structurally different problem: one party cannot participate in a
consensus meeting.

### It asks who is supervising the automation

**M8c requires the qualifications or training of reviewers performing AI-assisted tasks.** Set beside
threat **TV21** and caveat **I9** in [11](./11-caveats-register.md) — non-expert reviewers omit
well-known studies and cannot reason about findings, and automation that hides the process conceals
this rather than fixing it — M8c is the corpus's only item that makes reviewer expertise a *reported
quantity* in an automated setting. It is the natural ally of the closing argument in
[12](./12-platform-implications.md).

### But it has no per-review-type applicability

> **⚠ CAVEAT — and this is the gap that matters most for this platform.** SEGRESS is the primary
> standard here for exactly one reason: it marks every item required / optional / not-required **per
> review type** ([10](./10-reporting-and-evaluation.md)). **PRISMA-trAIce has no such table.** It is
> written for the SLR and says nothing about mapping studies, rapid reviews or tertiary studies.
>
> Three consequences, none resolved by the source:
> - A **mapping study** using AI classification still needs R1, but SEGRESS marks several
>   results-section items optional or not-required for mapping studies. Whether R1 survives that is
>   undefined.
> - A **Rapid Review** reports through a six-part **Evidence Briefing**
>   ([03](./03-rapid-review.md)), which has no Title/Abstract/Methods/Results/Discussion structure for
>   trAIce items to attach to. The mapping simply does not exist.
> - A **tertiary study** is routed by SEGRESS to the mapping-study profile *except* for quality
>   assessment. trAIce offers no routing at all.
>
> **Do not silently generalise the checklist across the four study types.** Where this platform needs
> per-type applicability, it is defining it, not applying it.

### A tension the sources do not resolve

> ### ◐ DISPUTED — may an LLM extract data, and on what evidence?
>
> **The SE position.** Kitchenham et al. distrust automated extraction "unless our ability to
> evaluate the quality of different studies improves"; extraction from a study without checking
> whether it used an invalid metric yields results "very quickly [that] will be wrong". Recorded as
> caveat **E9** in [11](./11-caveats-register.md) and as the first of the three cautions in
> [12](./12-platform-implications.md) — the sharpest methodological warning in the corpus for a
> platform like this one.
>
> **The trAIce position.** AI tools "can assist in almost all phases of the SLR process", data
> extraction explicitly among them (Holst et al. §Introduction). The checklist's response to the risk
> is **disclosure plus human oversight** — M3 names extraction as a reportable stage without
> qualification, M8 governs verification, and M9 evaluation is **conditional**.
>
> **Why this is a genuine disagreement and not a difference of topic.** Both are addressing what
> makes an AI-assisted result trustworthy. The SE position holds that AI extraction is *invalid*
> until appraisal capability improves — a claim about the result. The trAIce position holds that AI
> extraction is *acceptable when disclosed and overseen* — a claim about the process. Because M9 is
> optional, **a fully trAIce-conforming review can do precisely what Kitchenham et al. say produces
> confidently wrong answers, and disclose it in conforming prose.**
>
> Neither source engages the other; Holst et al. cite no SE methodological literature beyond a
> ResearchGate link to Kitchenham's procedures document. **Presented unresolved.**
>
> **The defensible reading for this platform** — stated as a design choice, not as a resolution: treat
> **M9/R2 as required rather than conditional** wherever AI touches extraction or screening. That
> satisfies trAIce, and it is the only configuration that answers Kitchenham's objection with
> evidence instead of process.

---

## What this means for the platform

> **⚙ IMPLEMENTATION — tracked as gap G44.** The full current-state analysis is in
> [`docs/feature-gaps.md`](../feature-gaps.md). In summary:
>
> **Already substantially satisfied.** `Reviewer.reviewer_type` distinguishes human from AI, and
> `PaperDecision.reviewer_id` points at it — so **R1's AI-versus-human split is derivable today**,
> which is the single hardest item for most tools to retrofit. `PaperDecision.is_override` and
> `overrides_decision_id` record human overrides of AI decisions as a chain, which is a partial
> **M8f**. `Agent.model_id` and `provider_id` give **M2a**.
>
> **The load-bearing absence is M6.** `Agent.system_message_template` is mutable with only a
> single-level undo buffer, so the prompt that produced a decision is unrecoverable once the template
> has been edited twice — and sampling parameters are function-signature defaults in the LLM client
> rather than persisted state. A review conducted over months cannot answer M6 at all.
>
> **The reframing that matters.** M8e asks what *proportion* of AI outputs were manually verified.
> An override log cannot answer that: a human who reviewed an AI decision **and agreed with it**
> leaves no row. Verification and disagreement are different events, and only one of them is
> currently recorded.

---

## Caveats

Consolidated into [11 — Caveats register](./11-caveats-register.md) as **J1–J7**.

> **⚠ Disclosure is not validity.** The paper's own framing of the risk is that LLM opacity,
> hallucination and training-data bias "stand in direct contradiction to the core principles of
> SLRs". The checklist makes AI use **visible**. It does not make it **sound**. A perfectly
> conforming report may describe an unsound review in complete detail.

> **⚠ The standard's own infrastructure is grey literature.** The authoritative version lives in a
> personal-account GitHub repository, coordination happens on Discord, and the steering committee is
> an intention. This is the link-rot exposure documented for grey sources in
> [05](./05-grey-literature-mlr.md) — 23.7% of grey URLs dead, 24.8% never recorded — applied to a
> reporting standard. **If this platform encodes the checklist, it should stamp the version and
> access date it encoded, exactly as caveat H9 requires for grey sources.**

> **⚠ T1 is advisory; the rest are not.** "Consider indicating the use of AI assistance in the title"
> is the only item phrased as a suggestion. A conformance checker treating all items uniformly will
> over-report non-compliance.

> **⚠ The paper reports no empirical findings of its own.** The much-quotable "50% to 75% reduction
> in manual workload" is **cited from Abogunrin et al. 2025**, not measured here. Attribute it there.
> Playbook principle 5 — distinguish a paper's own contribution from what it cites — applies with
> unusual force to this source.

> **⚠ Table 1 shows signs of not having been copy-edited**, which weakens any argument that its exact
> wording is authoritative: M8's sub-items run `a.`–`g.` and then a **second `f.`** (eight sub-items
> under seven labels), the duplicate overlaps semantically with `e.` and `g.`, and M9 contains
> "Analyzes conducted to access model bias" and "erroneous ouputs". References 22 and 23 are the same
> Gallifant et al. TRIPOD-LLM paper listed twice. **For any item to be implemented verbatim, consult
> the source and the project repository.**

> **⚠ Multimedia Appendix 1 is not in this corpus.** The per-item elaboration, rationale, sources and
> application examples ship as a separate 29 KB DOCX. Every paraphrase in this chapter rests on
> Table 1 alone. **Anyone implementing item-by-item needs that appendix.** Recorded in the
> [README reliability table](./README.md#reliability-of-this-document).

---

## Sources

| Source | Role |
| ------ | ---- |
| `holst_transparent_2025` | The whole chapter |
| Extraction notes | [`notes/ai-assisted-review-reporting.md`](./notes/ai-assisted-review-reporting.md) — denser, with the full item table and every source defect |
