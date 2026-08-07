# 09 — Threats to Validity

**Primary sources**: Ampatzoglou et al. 2020, *Guidelines for managing threats to validity of
secondary studies in software engineering* — the operational framework. Petersen & Gencel 2013,
*Worldviews, research methods, and their relationship to validity in empirical SE research* — the
classification and its justification.

Two frameworks, doing different jobs. **Use Ampatzoglou to find and mitigate threats. Use Petersen &
Gencel to name the validity categories you report under.** They are complementary, not competing.

---

## Framework A — Ampatzoglou: threats organised by review phase

### Why it is organised this way

The categories derive from **the phases of the secondary study** — search, filtering, extraction,
analysis — rather than from the aspect of validity threatened (internal, external, construct…). The
stated reason is practical: phases are easily identifiable steps, whereas validity aspects are not,
and a phase-based scheme **stops one threat being classifiable under two categories**. Every threat
belongs to exactly one category, determined by the phase where it arises and the artefact whose
validity it damages.

**Three levels**: threat categories → threats → mitigation actions.

| Category | What it threatens | Phases |
| -------- | ----------------- | ------ |
| **Study Selection Validity** | The validity of searching for and including primary studies | Search process; study filtering |
| **Data Validity** | The validity of the extracted dataset and its analysis | Data extraction; data analysis |
| **Research Validity** | The overall research design | **All phases — horizontal** |

```
Search process  →  Study filtering  →  Data Extraction  →  Data Analysis
(candidate set)    (included set)      (populated data)    (classification)

|--- Study selection validity ---|------ Data validity ------|
|-------------- Research validity: spans all phases ---------|
```

**Scale**: 22 top-level threats (TV1–TV22), expanding to **34 distinct named threats** once the 18
sub-threats under the six grouped threats are counted, with **60 mitigation actions**.

> **⚠ Two defects in the source, not corrected here.** Figure 3a duplicates the label "TV1.3" for two
> distinct sub-threats and Figure 3b duplicates "TV15"; and the Data Validity prose says "five
> ungrouped" threats where the figure and checklist both give six. The numbering below follows the
> checklist, which is internally consistent.

> **Note: the reporting phase has no threats of its own.** Ampatzoglou omits it deliberately —
> reporting is where the threats are *disclosed*, not where they arise.

### Category 1 — Study Selection Validity (TV1–TV7)

| ID | Threat | What goes wrong |
| -- | ------ | --------------- |
| **TV1** | Adequacy of relevant publication identification *(group)* | The umbrella for five search-process failures below |
| TV1.1 | Construction of search string | Returns far too many irrelevant studies, or too few, missing relevant ones |
| TV1.2 | Selection of digital libraries | Libraries too specific, too broad, or not credible |
| TV1.3 | Selection of publication venues | Choosing specific venues over broad engines — usually because the topic is broad or only high-quality work is wanted — and missing relevant studies |
| TV1.4 | Definition of starting year | An arbitrary start date drops earlier work. **Only acceptable if you can say why it does not affect results** |
| TV1.5 | Search engine inefficiencies | Engine limitations (e.g. cannot search abstract-only) cause misses or an unmanageably large corpus |
| **TV2** | Limited journals/conferences | Primary studies confined to few venues implies a narrow scope and a low yield |
| **TV3** | Missing non-English papers | Only a real threat where an active community publishes high-quality work in another language |
| **TV4** | Paper inaccessibility | Full texts unobtainable; if many, the retrieved set is unrepresentative |
| **TV5** | Handling of duplicate articles | Conference and extended journal versions double-counted |
| **TV6** | Inclusion/exclusion of grey literature | Either choice can be a threat — it depends on the study's goal |
| **TV7** | Study inclusion/exclusion | Conflicting or over-generic criteria applied during filtering |

**Mitigations for TV1** (nine, and this is the richest set): snowballing · pilot searches to train
the string · choosing well-known digital libraries, or specific venues, or broad indices *according
to the study's goal* · **comparing the primary-study list against a gold standard or other secondary
studies** · a broad search in a generic engine to ensure all relevant venues are found · a systematic
strategy for string construction · **independent expert review of the search process** · review tools
· evaluating and documenting search outcomes. A tenth appears only in a figure: bibliography
management tools.

**Mitigations for TV7** (nine): systematic voting · random screening of articles among authors ·
discussion of conflicts · explicit documentation of criteria in the protocol · **revising criteria
after pilots or expert review** · **a prescribed set of decision rules** · quality thresholds for
inclusion/exclusion · sensitivity analysis · **quantifying disagreement with the kappa statistic**.

Worked good practice for TV7: define criteria as an objective basis; run a **pilot selection before
formal selection** so reviewers reach a consistent understanding; have **two researchers select
independently for at least one round** and resolve conflicts by discussion.

> **A mutual-exclusivity rule worth encoding.** If digital-library selection is used, TV1.3 (venue
> selection) does not apply — normally only one of the two strategies is chosen. The exception is a
> quasi-gold standard drawn from specific venues, where both apply. TV1.1 (string construction)
> applies in **both** cases.

> **⚙ IMPLEMENTATION.** This exclusivity logic is why threats should be *derived from the protocol
> configuration* rather than presented as a flat checklist. The platform already auto-creates threats
> from Rapid Review QA mode; this generalises that to all study types and gives the full rule set.

### Category 2 — Data Validity (TV8–TV16)

| ID | Threat | What goes wrong |
| -- | ------ | --------------- |
| **TV8** | Small sample size *(group)* | Results prone to bias, not statistically significant, unsafe to generalise |
| TV8.1 | Small sample size | As above |
| TV8.2 | Primary study heterogeneity | Highly heterogeneous data cannot be synthesised without heavy subjectivity |
| **TV9** | Choice of variables to extract | Variables that do not answer the research questions; prone to researcher bias |
| **TV10** | Publication bias | Most primary studies from one venue → the dataset reflects one community's beliefs |
| **TV11** | Lack of relationships | Data with no relations in it cannot yield a conclusion |
| **TV12** | Validity of primary studies | Inaccurate primary results bias the review. Negative results are less likely published |
| **TV13** | Data extraction bias *(group)* | **"One of the most common" threats in SE** |
| TV13.1 | Data extraction bias | Open questions in collected variables, handling not specified in the protocol |
| TV13.2 | Quality assessment subjectivity | Only relevant where primary-study quality is evaluated |
| TV13.3 | Data extraction inaccuracies | The same concept classified inconsistently across studies |
| TV13.4 | Unverified data extraction | Not validated by external or internal review |
| TV13.5 | Misclassification of primary studies | Mostly a mapping-study threat |
| **TV14** | Lack of statistical analysis | Sometimes unavoidable — e.g. all data items categorical |
| **TV15** | Bias of classification schema *(group)* | Mapping studies using an inadequate schema or attribute framework |
| TV15.1 | Robustness of initial classification | A pre-existing schema that does not fit the domain and resists tailoring |
| TV15.2 | Construction of attribute framework | Attribute values not discrete and comprehensive → insufficient dataset |
| **TV16** | Researcher bias | Bias in interpreting or synthesising — including **only one author doing the synthesis** |

**Mitigations for TV13** (six): involve more than one researcher · quantify disagreement with kappa ·
pilot data extraction to test agreement · use experts or external reviewers for conflicts · **random
paper screening to cross-check extraction** · keywording of abstracts (mapping studies only).

**Mitigations for TV16** (five): pilot data analysis and interpretation · **reliability checks such
as post-review surveys with experts** · use a formal data synthesis method · sensitivity analysis ·
**weight conclusions by the scientific quality of primary studies**.

> **⚠ CAVEAT on TV10's mitigations.** Snowballing and including grey literature mitigate publication
> bias — but "should be treated with caution, since in specific types of studies, they pose more
> significant threats to validity", e.g. grey literature may hurt primary-study quality. **A
> mitigation for one threat can create another.**

> **⚙ IMPLEMENTATION.** TV14's mitigation is a check the platform can perform automatically: *does
> the extracted data actually contain quantitative variables, and do the research questions require
> statistics?* Claiming statistical analysis over categorical-only data is mechanically detectable.
> Note also the source's counterweight — qualitative analysis methods are "equally important", so
> the absence of statistics is only a threat if statistics were warranted.

### Category 3 — Research Validity (TV17–TV22)

| ID | Threat | What goes wrong |
| -- | ------ | --------------- |
| **TV17** | Repeatability | Cannot replicate the study — usually from a missing detailed protocol |
| **TV18** | Research method bias *(group)* | Wrong method chosen, or deviation from the established process |
| TV18.1 | Chosen research method | SMS and SLR serve different goals; the wrong one was picked |
| TV18.2 | Review process deviation | Departing from the guidelines — **requires strong argumentation** |
| **TV19** | Coverage of research questions | Questions do not fulfil the study goal — too generic a goal, or poor decomposition |
| **TV20** | Lack of comparable studies | No related work to compare findings against |
| **TV21** | Unfamiliarity with the research field | Non-expert reviewers omit well-known studies, synthesise poorly, cannot reason about findings |
| **TV22** | Generalizability *(group)* | Results not generalisable — e.g. only part of the literature was found |
| TV22.2 | Not applicable to other domains/organisations | The frequently reported special case |

**Mitigations for TV17**: more than one researcher · **make all gathered data publicly available** ·
**document the review process in detail in a protocol**. The key practice is developing and
*publicly sharing* the protocol.

**Mitigations for TV19**: brainstorm whether the questions holistically cover the goal · motivate the
questions well · **consult the target audience**. The named best practice is **GQM** — see below.

> **⚠ TV21 is the threat this platform most directly addresses, and most directly risks.** Reviews
> performed by researchers unfamiliar with the field omit well-known studies and cannot reason about
> findings. Encoded guidance helps; but the recommended mitigation is *exhaustive related-work search
> to familiarise yourself*, and the recommendation that **senior researchers be included in data
> analysis and interpretation**. Automation that removes the need to become familiar does not mitigate
> this threat — it conceals it.

### The author-side procedure

Ampatzoglou prescribes how to *manage* threats, in four steps:
1. Create a **dedicated threats-to-validity section in both the protocol and the final report**
2. Organise it **by threat category**, following this schema or another established one
3. **Check every threat** for whether it pertains to the study
4. For each identified threat, either **report an appropriate mitigation action** or **acknowledge
   that the threat is not (fully) mitigated**

> **⚙ IMPLEMENTATION.** Step 4 is the one to enforce: an identified threat with neither a mitigation
> nor an explicit acknowledgement is an incomplete study. That is a mechanical completeness check
> over a threat record — exactly the shape of check the platform's phase gates already perform.

---

## Framework B — Petersen & Gencel: which validity categories to report under

Ampatzoglou tells you *what can go wrong*. Petersen & Gencel tell you *what to call it*, and why the
classical categories are the wrong choice for software engineering.

### The argument

Validity classifications are **paradigm-specific**. The classical set — internal, external, construct
and conclusion validity (Cook & Campbell, carried into SE by Wohlin et al.) — belongs to a
**positivist, quantitative** worldview. Software engineering is in practice **pragmatist and
multi-method**, mixing qualitative and quantitative work. Petersen & Gencel therefore recommend
**Maxwell's classification**, which fits mixed-method research, and map it against the alternatives.

**The recommended set** — and the one already used, without attribution, in the repo's SMS document:

| Category | Meaning | Classical analogue |
| -------- | ------- | ------------------ |
| **Descriptive validity** | Are observations described accurately and objectively? | — (no clean analogue; closest to measurement reliability) |
| **Theoretical validity** | Does the study capture what it intended to capture? | Construct validity |
| **Generalizability** | Do findings hold beyond the studied cases? Split into **internal** (within a group/community) and **external** (across groups or organisations) | External validity |
| **Interpretive validity** | Are the conclusions reasonable given the data? | Conclusion validity |
| **Repeatability** | Can the study be repeated? | Reliability |

> **⚠ Reliability is demoted.** Petersen & Gencel treat reliability/repeatability as a **derived
> property** rather than a first-class validity category — it follows from descriptive validity and
> documentation, rather than standing alone. Worth knowing before treating it as a peer of the others.

> **⚠ EXTRACTION CAVEAT.** The cross-terminology mapping (Cook & Campbell / Wohlin / Lincoln & Guba /
> Greenwood & Levin / Runeson & Höst / Maxwell) is reproduced in the working notes, but the check
> marks in the source's Tables IV and V were **displaced by one row in text extraction**. The
> category set and definitions above are sound; **the cell-by-cell cross-mapping must be verified
> against the PDF before being quoted**.

### How the two frameworks combine

They are not alternatives:

- **Ampatzoglou** = the checklist. Which specific things can go wrong at which phase, and what to do.
- **Petersen & Gencel** = the reporting taxonomy. Which heading each acknowledged threat is filed
  under in the protocol and report.

A worked pairing: TV1.2 (selection of digital libraries) is an Ampatzoglou *study-selection* threat;
in the report it is discussed under **theoretical validity**, because it concerns whether the study
captured what it intended to. TV13 (extraction bias) is filed under **descriptive validity**. TV22
(generalizability) maps to **generalizability** directly.

---

## Framework C — GQM, for deriving what to measure

**Goal Question Metric** (Basili, Caldiera & Rombach) is named by Ampatzoglou as the best practice for
mitigating **TV19 — coverage of research questions**. Three levels:

| Level | Content |
| ----- | ------- |
| **Conceptual — Goal** | An object (product, process, resource) studied for a purpose, with respect to a quality focus, from a viewpoint, in an environment |
| **Operational — Question** | Questions characterising the object with respect to the goal, in three groups: how the object is characterised; how its relevant attributes are characterised; how those attributes are evaluated |
| **Quantitative — Metric** | Data answering each question, chosen by three factors: the amount and quality of existing data, the maturity of the objects, and the intended learning |

The 1992 goal template has five slots: **purpose · perspective · environment**, with purpose values
drawn from a fixed set (characterise, evaluate, predict, motivate, control).

> **⚙ IMPLEMENTATION.** GQM is the missing traceability link the platform needs anyway: goal →
> question → what gets extracted. Kitchenham's protocol evaluation asks whether "the data to be
> extracted will properly address the research question"; GQM is the structure that makes that
> checkable rather than a matter of opinion. It also gives the platform a principled answer to *which
> extraction fields belong on the form* — those, and only those, that answer a question derived from
> the goal.

---

## Practical guidance

**Every study type needs a threats section.** Mapping studies included — Petersen 2015 makes validity
discussion a quality criterion for a mapping study, and it is one of the five scoring rubrics.

**Where each framework fits:**

| Study type | Threat catalogue | Reporting categories | Notes |
| ---------- | ---------------- | -------------------- | ----- |
| SLR | Ampatzoglou, all three categories | Petersen & Gencel | The framework's home case |
| SMS | Ampatzoglou; TV13.5 and TV15.x are mapping-specific | Petersen & Gencel | Already partly encoded in the repo |
| Tertiary | Ampatzoglou | Petersen & Gencel | Plus the tertiary-specific caveats in [04](./04-tertiary.md) |
| Rapid Review | **Cartaxo's disclosure regime instead** — every methodological concession is itself a threat | Petersen & Gencel | See [03](./03-rapid-review.md) for the concession→threat map |

**A closing caution the corpus supports repeatedly.** A threats section that lists threats without
mitigations or acknowledgements is decoration. Ampatzoglou's step 4 exists precisely because that is
the common failure — and the Petersen 2015 rubric scores study validity **1 if threats and limitations
are described, 0 if not**, which is a low bar that a platform can raise.
