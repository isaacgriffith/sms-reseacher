# 08 — Data Extraction and Synthesis

**Primary sources**: Cruzes & Dybå 2011a, *Recommended steps for thematic synthesis in SE* (the
method). Cruzes & Dybå 2011b, *Research synthesis in SE: a tertiary study* (the method catalogue and
the audit). Ribeiro et al. 2014 (qualitative metasummary). Kitchenham & Charters 2007 (extraction
forms, quantitative synthesis).

---

## The finding that frames this chapter

Cruzes & Dybå's tertiary study over SE systematic reviews found:

- **49.0%** of studies calling themselves systematic reviews were really **scoping studies**
- only **20.4%** cited any synthesis method at all
- and **4 of those 10 citations pointed at references that do not define the method claimed**
- only **25%** had a table comparing the findings of the primary studies
- genuine meta-ethnography: **1 of 49** SE reviews, against almost half of healthcare reviews

> **⚙ IMPLEMENTATION.** "Synthesis was claimed but not performed" is the single most common quality
> failure in SE secondary studies. It is also mechanically detectable: a synthesis that produces no
> codes, no themes, and no cross-study comparison is tabulation. Gap **G8** records that the
> platform's thematic strategy is a single LLM call producing a theme→index map — that is thematic
> *clustering*, and by this corpus's own standard it would be reclassified as not-synthesis.

---

## Part 1 — Data extraction

### The form

Defined and piloted **when the protocol is defined**. It must capture everything needed for the
research questions and the quality criteria. Numerical data are a **prerequisite for meta-analysis**.

**Standard administrative fields**: reviewer name · extraction date · title, authors, journal,
publication details · space for notes.

**The three kinds of data to extract** (Cruzes & Dybå's core extraction recommendation):

| Kind | Contents |
| ---- | -------- |
| **Publication details** | Authors, year, title, source, abstract, aims |
| **Context descriptions** | Subjects, technologies, industry, settings, instruments, study type |
| **Findings** | Results, behaviours, actions, phenomena, events, quotes — **each carrying its origin and strength of evidence** |

**The structure is one-to-many, twice over**: one publication has **at least one context** (more if
the paper reports several studies), and each context has **at least one finding**, probably many. A
worked instantiation used `Publication → Study → Quote`.

> **⚙ IMPLEMENTATION — this is gap G6 in a different guise.** The extraction model is not
> paper-keyed; it is *publication → study → finding*. The platform's `DataExtraction` is keyed to
> `candidate_paper_id`, which collapses the middle level. Cruzes' template is the authority for
> introducing it, and Petersen 2008's screening rule agrees: "where several studies were reported in
> the same paper, each relevant study was treated separately."

### Where findings live, and how to recognise one

Most likely in results, analysis-of-results, discussion and conclusions. **Tables and figures are
also sources of findings** — a relationship expressed only visually can be extracted and translated
into text.

**Heuristics for deciding whether a statement is a finding.** Does it: state the results of
measurements? summarise raw data? highlight a characteristic of the raw data? provide additional
insight about a table or figure? summarise the results of analyses? help answer the research
questions? reflect the main results of the study?

### Immersion — the step that gets skipped

**Read the whole set at least once before extracting.** The source is emphatic that this is tempting
to skip and that the thematic-analysis literature advises strongly against skipping it: immersion is
what makes you familiar with the depth and breadth of the evidence, and initial ideas and candidate
patterns form during that first reading.

**It was explicitly stated in only half of the eight SE thematic syntheses examined.**

After the initial reading, reviewers may **update the protocol** — extraction strategy and synthesis
strategy both.

> **⚙ IMPLEMENTATION.** Immersion has no obvious analogue in an automated pipeline, and pretending
> otherwise would be dishonest. What the platform *can* do is preserve the affordance: make the full
> corpus readable before extraction begins, and record whether a human did so. Do not let "the agent
> read every paper" stand in for it — the purpose is the reviewer's familiarity, which is also the
> mitigation for threat TV21.

### Rigour controls

Two or more researchers extract independently where feasible; compare; resolve by consensus or
independent arbitration. **Where SE papers lack detail — a recurring problem — extract in consensus
meetings instead.** Unresolvable uncertainty is pushed into sensitivity analysis or the
trustworthiness evaluation **rather than silently resolved**.

> **⚠ CAVEAT — the hardest field is context.** Publication details extract straightforwardly, but
> **study aims are often unclear and need analytical work to recover**, and **context is hardest of
> the three**: papers frequently omit design detail, do not address bias and validity, and describe
> data collection, analysis, samples and settings poorly. In such cases extraction is hindered
> outright — which is a finding about the corpus, not a failure of the extractor.

See [01-slr.md §2.4](./01-slr.md) for duplicate handling, missing data, and the warning against
extraction decoupled from quality appraisal.

---

## Part 2 — Thematic synthesis (Cruzes & Dybå)

The method SE reviews most often claim and least often perform. Five steps, with a characteristic
funnel:

| Stage | Artefact | Expected volume |
| ----- | -------- | --------------- |
| Initial reading | immersion | many pages |
| Identify segments | candidate units | many segments |
| Label segments | **codes** | **30–40** |
| Reduce overlap, translate | **themes** | **15–20** |
| Model higher-order themes | **model** | **5–7** |

Levels of interpretation: **Text → Codes → Themes → Model**, abstraction and generalisability rising
at each level.

### Step 1 — Extract data
As Part 1 above. Output: a populated extraction form, possibly an updated protocol.

### Step 2 — Code data

**Output**: a list of initial codes **with definitions and frequencies**, validated by a second
researcher; roughly 30–40 codes.

Coding is more than applying a label — it requires a clear sense of the context in which the finding
was made, and involves identifying passages exemplifying the same descriptive or theoretical idea.
Codes are "the beginning of themes". **Nobody gets coding right first time**; codes refine as work
proceeds.

**Three ways to create codes:**

| Approach | Origin | Mechanics | Risk |
| -------- | ------ | --------- | ---- |
| **Deductive / a priori** | A provisional start list from theory, research questions, hypotheses, key variables | Structure defined *before* coding; a start list runs from a dozen up to 30–40 codes — a number holdable in short-term memory given clear structure | **Forcing data into a category merely because a code exists for it** |
| **Inductive / grounded** | Purely from the data | Line-by-line review; a code assigned as each concept appears; specifications refined as more data is seen. Test a code by comparing the segment against segments already given that code — **constant comparison** | Slow; impractical at scale |
| **Integrated** | Both | Inductive development of codes *inside* a deductive framework of code **types** — a general accounting scheme that is not content-specific but points to domains within which codes emerge | — |

**Cruzes & Dybå recommend the integrated approach for systematic reviews**, because reviews are
driven by theoretical interests embedded in the review questions: the reviewer arrives with specific
questions to code against, while also having to relate to the concepts the primary authors used.

**Whether pre-specified or emergent, clear operational definitions are indispensable**, so codes can
be applied consistently by one researcher over time or by several concurrently.

**Four code types useful in SE**: conceptual codes (key concepts and their dimensions) · relationship
codes (links between conceptual codes) · subject codes (subjects' perceptions) · context
characteristic codes.

> **⚠ SE-specific adaptation.** Line-by-line coding is **unlikely to be practical for large numbers
> of studies**. In SE reviews, work with the **chunks** of data extracted in Step 1. Thematic analysis
> specifies no particular length of text per code — unlike grounded theory, which some authors
> distinguish precisely by coding incident by incident or line by line.

**Rigour controls**: at least two researchers validating codes; codes must have **explicit boundaries
so they are neither interchangeable nor redundant**, and must be limited in scope — otherwise you end
up coding every sentence. Give equal attention to all papers.

> **Do not confuse thematic analysis with content analysis.** Content analysis also compares and
> sorts, but its aim is to **quantify** content against predetermined categories, establishing
> significance largely by frequency. **Thematic analysis does not.**

### Step 3 — Translate codes into themes

**Input** ~30–40 codes. **Output** ~15–20 themes plus a **thematic map**.

A theme, per three offered definitions: an *outcome* of coding, categorisation and analytic
reflection — not itself something that is coded (Saldaña); something that at minimum describes and
organises observations and at maximum interprets the phenomenon, identifiable at the **manifest**
level (directly observable) or the **latent** level (underlying) (Boyatzis); an abstract entity
bringing meaning and identity to a recurrent experience and unifying it into a meaningful whole
(DeSantis & Ugarriza).

**Explicitly not a single pass.** First-cycle codes may be subsumed, relabelled, or dropped; coded
data is rearranged and reclassified into different and even new codes. **The stopping rule is
saturation** of the themes emerging from the data.

Named techniques: pattern coding, elaborative coding, longitudinal coding; and the
grounded-theory-flavoured focused coding, axial coding, theoretical/selective coding.

**Representation**: thematic networks, tables, tree-maps, mind-maps — codes clustering into themes,
themes into higher-order themes, arranged around a central topic.

> **⚠ In the SE thematic syntheses examined, this step was usually not described** — which is the gap
> between claiming thematic synthesis and doing it.

### Step 4 — Create a model of higher-order themes

**Output** 5–7 higher-order themes forming a model. Three sources of heterogeneity must be handled
during model building.

### Step 5 — Assess the trustworthiness of the synthesis

Four criteria: **credibility · confirmability · dependability · transferability.**

> **⚙ IMPLEMENTATION.** Step 5 is what makes the difference between a synthesis and an assertion, and
> it is the step gap **G8** identifies as entirely absent. A 21-item checklist maps onto the five
> steps and is the natural basis for a synthesis completeness gate.

---

## Part 3 — Qualitative metasummary (Ribeiro et al.)

A **quantitatively oriented aggregation of qualitative findings**. The goal is to discern the
frequency of each finding, and to treat higher-frequency findings as the evidence of replication that
grounds a claim to have discovered a pattern.

**Four steps**: extract → group → abstract → compute effect sizes.

**The two effect sizes** — both recovered from the source and cross-checked arithmetically against
its own worked table:

- **Frequency effect size** = (number of studies containing a finding, *discounting reports from a
  common parent study that repeat the same data*) ÷ (total number of studies)
- **Intensity effect size** = (number of findings in a study) ÷ (total findings across all studies)

> **⚠ CAVEAT from the source itself.** Ribeiro et al. warn that **the intensity index is of
> questionable value** and that the arithmetic "seems too simplistic". Implement it if you like, but
> do not present it as a settled measure — the authors do not.

> **⚠ Three internal inconsistencies** in the paper's prose (a "10-factor model" against nine groups;
> "four out of five studies"; "six concepts investigated more than once") were flagged during
> extraction and **not reconciled**. Verify against the PDF before quoting its worked numbers.

---

## Part 4 — The synthesis method catalogue

Thirteen methods for synthesising qualitative and mixed-methods evidence.

| Method | What it does | When it applies |
| ------ | ------------ | --------------- |
| **Narrative synthesis** | Narrative rather than statistical summary; ordered descriptions of primary evidence with commentary and interpretation, plus tools that increase transparency | Quantitative and/or qualitative reviews; **the general-purpose fallback when statistical pooling is impossible** |
| **Meta-ethnography** | Translates studies into one another, then synthesises the translations into concepts going beyond individual accounts. Treats primary interpretations as data | Small, conceptually comparable sets where a genuinely new interpretation is the aim |
| **Grounded theory** | Simultaneous collection and analysis, constant comparison, theoretical sampling, new theory | When new theory is the target and the corpus supports inductive analysis |
| **Cross-case analysis** | Tabular displays, graphs, meta-matrices to partition and cluster data through intensive coding; summarise within themes across studies | Multi-case evidence where displays carry the comparison |
| **Thematic analysis / synthesis** | Identify, analyse and report patterns; organises and describes richly, frequently interprets | Broad applicability — **but has limited interpretative power beyond description if not used within an existing theoretical framework** |
| **Content analysis** | Systematic categorising and coding under fixed thematic headings; occurrences counted and tabulated | When reproducible frequency counts are wanted — with the risk that counting **fails to reflect the structure or importance of the phenomenon, and counts what is easy to classify rather than what matters** |
| **Case survey** | Structured closed-ended questions extract data from many case studies so answers aggregate; qualitative evidence converted to quantitative | Large numbers of case studies; reliability over depth |
| **Qualitative comparative analysis (QCA)** | Boolean logic over a **truth table** to find necessary and sufficient conditions for an outcome | Configurational causal questions — which *combinations* produce the outcome |
| **Aggregated synthesis** | Elements of grounded theory and meta-ethnography; preserves original context while building mid-range theories | Theory development aiming to explain and predict |
| **Realist synthesis** | Theory-driven; explains **how interventions work and why they fail in particular contexts** | When the intervention cannot be implemented identically and context is the explanation. Flagged as **"a particularly relevant method for future research synthesis in SE"** |
| **Qualitative metasummary** | Quantitatively oriented aggregation; frequency of findings as evidence of replication | See Part 3 |
| **Qualitative metasynthesis** | Interpretive integration of findings that are themselves interpretive. **Validity resides in interpretation, not replication logic** | The interpretive counterpart of metasummary |
| **Meta-study** | Analyses the theories, methods *and* findings of a literature, then synthesises those insights | When methodological and theoretical drift across a literature is itself the object |

**How to choose.** Nominally: the research question, the anticipated number of primary studies, and
the review team's expertise. The source's stronger recommendation: rather than letting
epistemological foundations decide, take a pragmatic approach and let **the review's research
questions and the primary studies' designs, data collection and analysis methods drive the choice**.

### What does *not* count as synthesis

- **Classification alone.** Nine reviews described their work as "classification analysis"; six were
  reclassified as scoping studies. Classification was treated as *not* synthesis.
- **Tabulation alone.** Tables appeared in almost all reviews that synthesised, and they help — but
  the demand is to go beyond large per-study tables and build a **tabular synthesis combining key
  findings accessibly**. Only 25% had a table comparing findings across studies.
- **Vote counting.** Claimed by three reviews, all reclassified. Documented as **a fallback reviewers
  reach for, not a method with standing in the catalogue**. One used it explicitly because effect-size
  meta-analysis was impossible in its sample.

---

## Part 4b — Method slurring: claiming a method you did not use

**Source**: Stol, Ralph & Fitzgerald 2016, *Grounded Theory in Software Engineering Research: A
Critical Review and Guidelines*. The term is taken from Baker, Wuest & Stern 1992.

Stol et al. studied grounded theory specifically, but **the diagnosis and the remedy generalise to
every method named in this chapter** — and they give the pathology behind the numbers this chapter
opens with. Where Cruzes & Dybå found synthesis methods cited but not performed, Stol et al. supply
the name for it, the reasons it happens, and a test.

### The definition

**Method slurring** is claiming to use a research method without actually following its guidelines.

### The test — the most reusable thing in the paper

For grounded theory, stated as a disqualifier:

> If a study does not involve **simultaneous data collection and analysis, constant comparison,
> coding, memoing and theory development**, it is **not** a grounded theory study.

And behaviours that disqualify outright:

> If researchers **collect most or all of their data before beginning analysis**, **collect or
> categorise data according to existing theory**, or **base analysis on seed categories or
> preconceived analytical frameworks**, they are not using grounded theory.

**The generalised form**, which is what makes this belong in a chapter about synthesis: *for any
named method, list the practices that constitute it, and check whether the study performed them.* If
it did not, the study used something else, and should say so.

Applied to the methods in [Part 4](#part-4--the-synthesis-method-catalogue):

| Claimed method | Constitutive practices to check for |
| -------------- | ----------------------------------- |
| **Thematic synthesis** | Immersion · codes with operational definitions · translation of codes into themes · a higher-order model · a trustworthiness assessment ([Part 2](#part-2--thematic-synthesis-cruzes--dybå)) |
| **Meta-ethnography** | Translation of studies into one another, *then* synthesis of the translations into concepts beyond the individual accounts |
| **Qualitative metasummary** | Extract → group → abstract → **compute the two effect sizes** ([Part 3](#part-3--qualitative-metasummary-ribeiro-et-al)) |
| **Meta-analysis** | Pooled effect sizes with a stated model, heterogeneity assessment, sensitivity analysis |
| **Grounded theory** | The five practices above |
| **Content analysis** | Predetermined categories, systematic rule application, frequency counts |

> **⚠ The corpus already shows this test failing at scale.** Cruzes & Dybå reclassified nine reviews
> claiming "classification analysis" — six became scoping studies. Three claiming vote counting were
> all reclassified. Only **1 of 49** claimed meta-ethnographies survived scrutiny. Stol et al. found
> **only 16 of 98** articles gave a comprehensive account of their procedures at all.

### Why researchers do it

Five reasons, and they are worth knowing because they are mostly not dishonesty:

1. **To confer legitimacy.** The method is more structured, and therefore perceived as more
   scientific, than an unnamed approach. Charmaz's complaint: researchers "have invoked grounded
   theory as a methodological rationale" to justify doing qualitative research rather than adopting
   its guidelines.
2. **To avoid a detailed literature review.** The grounded-theory maxim about avoiding
   over-familiarity with the literature becomes an excuse to skip necessary background work.
3. **For simplicity.** It is easier to write "we used grounded theory" than to explain how a large
   volume of unstructured text became a cohesive theory.
4. **Because they do not understand the method.** Suddaby is quoted: a cursory citation to Glaser and
   Strauss while describing little of the method; invited to elaborate, it becomes clear the term was
   taken to mean "anything goes".
5. **On a referee's suggestion.** Reviewers tell authors their method "looks like grounded theory",
   and authors recast the work post hoc to satisfy them.

### What it costs

- **It undermines the method.** Using the term for any theory-building or qualitative analysis erodes
  a method that prescribes a highly structured approach, and **engenders undue suspicion of genuine
  studies, possibly hindering their publication.**
- **It undermines other methods.** Recasting interpretive interview studies, positivist case studies
  and ethnographies as grounded theory **implicitly disparages and devalues** them. "There is nothing
  wrong with conducting an ethnography and researchers should not hesitate to label it as such."
- **It misrepresents the research**, violating the principle that readers must be able to evaluate
  quality from an accurate account of how data was collected and analysed.
- **It defeats appraisal**, because readers cannot tell whether a study used the method or merely
  referenced it.

### The four recommendations

1. **Study the method before starting.** It suffers from "apparent simplicity" — superficially it
   looks like reading and categorising text. Read several books **before even deciding whether it is
   the right method**. The decisive sentence, and the one with the sharpest implication for tooling:
   > **"Research cannot be reconstructed as [grounded theory] at write-up."**

   The method dictates the *order* of collection and analysis, so it cannot be applied retrospectively.
2. **Describe your implementation, not the method in principle.** Several sampled studies gave
   reasonable summaries of grounded theory and never explained their own practices. Describe how each
   key practice was used, **and explicitly describe deviations**.
3. **Avoid "borrowing" rhetoric.** If you used techniques from the literature, say you used those
   techniques **without invoking the method**. Coding, memoing and constant comparison are part of any
   qualitative analyst's toolbox and exist independently of any particular method. **"Bringing in GT
   clouds the issue."**
4. **Do not claim a method you did not use.** Name the method you did use. If you invented one,
   explain it. **If you proceeded ad hoc, explain the "pragmatic, agile approach" rather than dressing
   it up.**

### Reporting questions worth reusing

Stol et al. supply a reporting checklist and are explicit that it is **not** a compliance list — "no
single article can or should include all of these items"; they are "questions to ask oneself". The
ones that generalise beyond grounded theory:

- **What variant of the method did you adopt, and what published guidance did you follow?**
- **How and why did you adapt, or deviate from, that guidance?**
- What was your initial research question, and what question emerged during the study — **preferably
  state both**
- What is your epistemological and ontological position?
- Who collected and analysed the data — an individual or a team? If a team, who did what, and how was
  it coordinated?
- **Describe your coding, memoing and sorting with examples**
- **Confirm that you employed constant comparison**
- When did you stop collecting data, and how did saturation become apparent?
- **Did you conduct a reliability check** — was your analysis reviewed by someone else? Who, how, what
  did they find, what changed, and what was their expertise?
- **How might your own biases, preconceptions, background and beliefs affect your analysis?**

### Specific defects that are mechanically checkable

These are the ones a tool could actually catch:

| Defect | Why it is checkable |
| ------ | ------------------- |
| **Mixing variants inconsistently** — claiming classic grounded theory while doing axial coding, or Straussian while using Glaser's coding families | The variant and the technique are both stated |
| **Citing conflicting seminal works without acknowledging the conflict** | Signals the authors have not read them |
| **Declaring an interpretivist epistemology while citing objectivist sources** | Found in **4 of the 5** papers that stated any epistemology at all |
| **"The method consists of three coding phases"** | A wrong summary — incomplete, and falsely implies three sequential phases |
| **Theoretical sampling described as purposive sampling** | Selecting cases a priori for topical relevance is *not* theoretical sampling, which responds to gaps in the emerging theory and is indeterministic |
| **Starting from a classification taken from the literature** | Highly suspect even under the more liberal variants |

### The numbers

From 98 articles across nine SE journals:

- **52 (53%) explicitly claim grounded theory; 46 (47%) merely borrow its techniques**
- **Only 16 of 98 (16%) provide a comprehensive account of their research procedures.** Of the 52
  claimants: 30 give significant methodological detail, **18 give none beyond the bare claim**, and 4
  deviate so sharply that the method was not used
- **39 of the 52 claimants (75%) do not acknowledge that the method has variants.** Of the 13 who do,
  5 claim classic and 8 Straussian; **none claim constructivist, and no article in the entire sample
  cited Charmaz**
- **Only 5 of 98 state an epistemological position** — all interpretivism, and **4 of those 5 cite
  sources aligned with positivism**
- Among the 30 detailed articles, practice reporting falls off sharply: data sources 29, coding 29,
  theoretical saturation 15, simultaneous collection and analysis 13, constant comparison 13,
  theoretical sampling 12, memoing 12, **memo sorting 4**
- **8 articles produced cohesive theories; 10 produced mere description**

> **⚙ IMPLEMENTATION.** Three things follow directly.
>
> **1. The method name must be earned by recorded steps.** The platform names a synthesis strategy in
> its output. Stol et al.'s test says the name is only valid if the constitutive practices were
> performed — so record *which steps ran* (codes created, themes derived, model built, trustworthiness
> assessed) and derive the claim from that, rather than letting the user assert it. This is the same
> conclusion the closing note of this chapter reaches from Cruzes & Dybå's side.
>
> **2. Some methods cannot be selected retrospectively.** "Research cannot be reconstructed as
> grounded theory at write-up" because the method dictates the order of collection and analysis. A UI
> that offers synthesis-strategy selection *after* extraction has completed is offering an invalid
> choice for those methods. This is the same ordering constraint open science imposes on the analysis
> plan — see [13](./13-open-science.md).
>
> **3. Deviations are reportable, not shameful.** Recommendation 2 asks for deviations to be described
> explicitly, and SEGRESS asks for the same thing about the protocol. A platform that records
> deviations makes the honest path the easy one — which is the whole argument for encoding process.

---

## Part 5 — Quantitative synthesis

From Kitchenham & Charters. Applicable when studies are homogeneous enough to pool.

**Binary outcome effect measures**: odds · risk (proportion/probability/rate) · odds ratio · relative
risk · absolute risk reduction.
*Trade-off*: odds ratios are mathematically convenient but poorly understood by non-statisticians;
risk measures are easier to grasp; relative measures are statistically more consistent, **but decision
makers need absolute values to judge real benefit**.

**Continuous outcome effect measures**: mean difference · **weighted mean difference** (same scale,
weight = inverse of study variance) · **standardised mean difference** (different scales; mean
difference ÷ within-group SD).

> **⚠ SMD is only valid if differences in standard deviations reflect differences in measurement
> scale, not real differences among study populations.**

**Presentation**: **forest plot** — line = standard error, box = mean difference with **box size
proportional to sample size**; the bottom entry is the pooled estimate when a formal meta-analysis is
performed. **Funnel plot** — effect against inverse variance or sample size; **asymmetry suggests
publication bias**.

**Homogeneity**: assess heterogeneity with the **Q test** or **likelihood ratio test**; homogeneous
studies use a **fixed-effects** model, heterogeneous studies a **random-effects** model.

**Anti-fishing rule**: identify possible sources of heterogeneity **in the protocol**, not post hoc.

**Sensitivity analysis is required regardless of approach** — repeat over subsets: high-quality
studies only, particular study types, studies where extraction was unproblematic, by experimental
method. With a descriptive synthesis it is more subjective but still owed.

> **⚠ Meta-analysis is often impossible in SE** because reporting varies too much between studies. It
> requires studies of the same type, with the same hypothesis, the same measures of treatment and
> effect, and the same explanatory factors reported.

---

## Mixed qualitative and quantitative evidence

1. Synthesise the quantitative and qualitative studies **separately**
2. Then integrate by asking whether the qualitative results **explain** the quantitative ones

The model example ran three syntheses: a statistical meta-analysis, a thematic qualitative synthesis,
and a **cross-study synthesis** using the qualitative results to interpret the meta-analysis.

---

## Per study type

| Study type | Expected synthesis |
| ---------- | ------------------ |
| **SLR** | A named method from the catalogue, applied and reported. Meta-analysis where studies permit; thematic synthesis or narrative synthesis otherwise |
| **SMS** | **Frequencies per category** — counts and percentages, with bubble plots or heatmaps for facet combinations. Not synthesis in the above sense, and should not claim to be |
| **Rapid Review** | **Narrative synthesis**, deliberately lightweight — plus mandatory conclusions and recommendations |
| **Tertiary** | Descriptive aggregation over secondary studies; regression where the sample supports it |

> **A closing note on honesty of labelling.** The tertiary study reclassified nearly half the reviews
> it examined. The lesson for a platform that *names* the method in its output: the name must be
> earned by the steps actually executed. Recording which synthesis steps ran — codes created, themes
> derived, model built, trustworthiness assessed — makes the claim checkable rather than declarative.
