# 11 — Caveats Register

Every trap the corpus warns about, in one place, indexed by the step where it bites. Each entry links
to the chapter with the full treatment.

Use this as a review checklist. Nothing here is invented — each item is something at least one source
paper explicitly warns against, and several are things the guidelines' own authors later retracted.

---

## A — Traps in the guidance itself

These matter most, because following the guidance uncritically reproduces them.

| # | Trap | Source position |
| - | ---- | --------------- |
| A1 | **The 2007 SLR guidelines are amended, not current.** Eleven changes, including removal of structured-question search-string construction and of the extractor/checker split | [01](./01-slr.md) |
| A2 | **The quality-checklist guidance was withdrawn** — "unhelpful… should be removed", with no replacement named | [07](./07-quality-assessment.md) |
| A3 | **No single guideline is complete.** 24 of 52 mapping studies used more than one, because they differ | [02](./02-sms.md) |
| A4 | **Petersen 2008's keywording was never properly defined**; 2015 concedes the process "is not clear" and re-specifies it as open coding | [02](./02-sms.md) |
| A5 | **Contribution type was over-promoted in 2008** and used by only 6 of 52 studies; the current recommendation is venue, research type, research method | [02](./02-sms.md) |
| A6 | **PRISMA 2020 forbids its own use as a quality instrument** | [10](./10-reporting-and-evaluation.md) |
| A7 | **SE dropped DARE's fifth criterion** — the mandatory synthesis one | [10](./10-reporting-and-evaluation.md) |
| A8 | **SEGRESS contradicts itself** on which items were reordered (prose says 13d/13f, table says 13e/13f) | [10](./10-reporting-and-evaluation.md) |
| A9 | **Ampatzoglou's figures duplicate two sub-threat labels**, and its prose miscounts ungrouped data-validity threats | [09](./09-threats-to-validity.md) |
| A10 | **Ribeiro warns its own intensity effect size is "of questionable value"** and the arithmetic "seems too simplistic" | [08](./08-extraction-and-synthesis.md) |

---

## B — Planning and protocol

| # | Trap | Chapter |
| - | ---- | ------- |
| B1 | **"Not using the intervention" is an inadequate control description** — it confounds the technique with its training | [01](./01-slr.md) |
| B2 | **Surrogate measures are endemic in SE** (defects in system test for quality; coupling for design quality) and weaken every conclusion resting on them | [01](./01-slr.md) |
| B3 | **Do not restrict the population early.** Medicine narrows to cut volume; SE has too few studies | [01](./01-slr.md) |
| B4 | **Expect to revise the questions during protocol development.** The protocol takes a long time and will change | [01](./01-slr.md) |
| B5 | **Piloting the protocol is essential** — it finds mistakes in collection and aggregation | [01](./01-slr.md) |
| B6 | **Every team member must help write the protocol**, or they will not understand the extraction they are about to do | [01](./01-slr.md) |
| B7 | **Write down the complementary questions you are *not* answering** — it sharpens selection and extraction. Absent from the guidelines | [01](./01-slr.md) |
| B8 | **Define the unit of analysis.** Also absent from the guidelines, and it decides what you are counting | [01](./01-slr.md), [08](./08-extraction-and-synthesis.md) |
| B9 | **If commissioning is skipped, the dissemination strategy must move into the protocol** or it is lost | [01](./01-slr.md) |
| B10 | **A Rapid Review protocol will change** — that is expected, but changes must be documented and justified | [03](./03-rapid-review.md) |
| B11 | **An RR may prove infeasible at problem definition** if no studies address the problem. The process must allow abandoning | [03](./03-rapid-review.md) |

---

## C — Search

| # | Trap | Chapter |
| - | ---- | ------- |
| C1 | **Database search alone is not adequate** — 45.9% recall against snowballing's 83%; 9 of 15 conclusions would have failed | [06](./06-search-and-selection.md) |
| C2 | **No single source is sufficient.** Google Scholar contributed **zero unique papers** in one study | [06](./06-search-and-selection.md) |
| C3 | **The snowballing start set is the single point of failure** — one study missed an entire category because the start set contained none of it | [06](./06-search-and-selection.md) |
| C4 | **Do not build the string mechanically from structured questions** (withdrawn); a simpler string may be just as effective | [01](./01-slr.md), [06](./06-search-and-selection.md) |
| C5 | **Adding a domain term silently drops cross-domain work** — removing `AND "software"` recovered two papers and quadrupled results | [04](./04-tertiary.md) |
| C6 | **Indexing lag defeats automated search.** Re-running a year later found all previously missed papers | [04](./04-tertiary.md) |
| C7 | **Sources not indexed by your libraries cannot serve as a gold standard** — the automated search could never have found them | [06](./06-search-and-selection.md) |
| C8 | **Split known papers into two disjoint sets** — one to build the string, one to evaluate it. Using one set for both measures memorisation | [06](./06-search-and-selection.md) |
| C9 | **SE keywords are not standardised**, which is the root cause of database non-overlap | [06](./06-search-and-selection.md) |
| C10 | **Terminology defeats tertiary searches** — authors say "literature survey", "assembly of studies", or just "review" | [04](./04-tertiary.md) |
| C11 | **An unassessed paper is not an excluded paper.** Time-budget stopping must record what was left unexamined | [02](./02-sms.md), [06](./06-search-and-selection.md) |
| C12 | **Grey-literature search is non-deterministic and personalised**; coverage cannot be established | [05](./05-grey-literature-mlr.md) |
| C13 | **Google Scholar's recall fails precisely on grey sources** — 96% overall, worst where grey lives | [05](./05-grey-literature-mlr.md) |
| C14 | **Search restrictions (date, language, geography, method) are threats and must be reported.** Narrowing to the practitioner's *context*, by contrast, is good practice | [03](./03-rapid-review.md) |

---

## D — Selection and screening

| # | Trap | Chapter |
| - | ---- | ------- |
| D1 | **SE abstracts are too poor to select on — read the conclusions too.** Repeated independently by several papers | [01](./01-slr.md), [06](./06-search-and-selection.md) |
| D2 | **Abstracts are also too poor for mapping-study classification**; allow reading depth to escalate per paper | [02](./02-sms.md) |
| D3 | **Title-only screening loses papers** — 5 of 11 in one snowballing study | [03](./03-rapid-review.md), [06](./06-search-and-selection.md) |
| D4 | **A binary include/exclude vote cannot express "uncertain"**, and the decision-rule table needs three values | [06](./06-search-and-selection.md) |
| D5 | **Selection is harder for mapping studies**, because criteria for broad topics are harder to define | [02](./02-sms.md) |
| D6 | **Exclusion can happen during extraction** — papers pass full-text screening then prove to have no aggregation | [04](./04-tertiary.md) |
| D7 | **Masking authors and institutions is not worth it** — no evidence it improves reviews, and it costs time | [01](./01-slr.md) |
| D8 | **Log exclusions only after the totally irrelevant papers are gone**, otherwise the log is noise | [01](./01-slr.md) |
| D9 | **A single reviewer must run test–retest** on a random sample of their own decisions | [01](./01-slr.md), [06](./06-search-and-selection.md) |
| D10 | **Requirements on evaluation should be avoided in a mapping study**, or recent unmatured work disappears | [02](./02-sms.md) |
| D11 | **Restricting to methodologically rigorous papers biases the map** — some sub-areas are simply easier to study empirically | [02](./02-sms.md) |

---

## E — Classification and extraction

| # | Trap | Chapter |
| - | ---- | ------- |
| E1 | **Authors mislabel their own papers** — 73% designated incorrectly in one study; "experiment" is used loosely | [02](./02-sms.md) |
| E2 | **Validation vs evaluation research is not about novelty** — it is lab versus real-world industrial context | [02](./02-sms.md) |
| E3 | **A new solution used in practice is still a solution proposal if empirical evaluation is missing** | [02](./02-sms.md) |
| E4 | **Context is the hardest thing to extract**; study aims often need analytical work to recover | [08](./08-extraction-and-synthesis.md) |
| E5 | **Do not skip immersion.** Stated in only half the SE thematic syntheses examined | [08](./08-extraction-and-synthesis.md) |
| E6 | **Line-by-line coding is impractical at SE scale** — code the extracted chunks | [08](./08-extraction-and-synthesis.md) |
| E7 | **A priori codes risk forcing data into a category** merely because the code exists | [08](./08-extraction-and-synthesis.md) |
| E8 | **Codes need explicit operational definitions**, or they become interchangeable and redundant | [08](./08-extraction-and-synthesis.md) |
| E9 | **Automated extraction without quality appraisal produces results "very quickly [that] will be wrong"** | [01](./01-slr.md) |
| E10 | **Never include the same data twice**; use the most complete report but consult all versions. Report how duplicates were handled | [01](./01-slr.md) |
| E11 | **Report manipulated data as published first**, then run sensitivity analysis on the reconstruction | [01](./01-slr.md) |
| E12 | **A paper is not a study.** One publication may report several; one study may span several papers | [08](./08-extraction-and-synthesis.md) |

---

## F — Quality assessment

| # | Trap | Chapter |
| - | ---- | ------- |
| F1 | **Unreported does not mean not done** | [07](./07-quality-assessment.md) |
| F2 | **Assess methodological quality, not reporting quality**; never sum them into one number | [07](./07-quality-assessment.md) |
| F3 | **Do not weight meta-analysis by quality score** — no medical guideline recommends it | [07](./07-quality-assessment.md) |
| F4 | **Scores compare only within the same study type and size** | [07](./07-quality-assessment.md) |
| F5 | **A checklist cannot catch what it does not ask** — e.g. an invalid accuracy metric | [07](./07-quality-assessment.md) |
| F6 | **Expert inter-rater agreement on quality is poor** — 0.54 correlation on average score | [07](./07-quality-assessment.md) |
| F7 | **Extracting quality data and not using it scores worse than not collecting it** (DARE Q3 = N) | [04](./04-tertiary.md) |
| F8 | **Mapping studies score lower on DARE structurally**, not because they are worse | [04](./04-tertiary.md) |
| F9 | **The evidence hierarchy is too simplistic** — match design to question type | [07](./07-quality-assessment.md) |
| F10 | **90% of reviews using grey literature perform no grey-specific quality assessment** | [05](./05-grey-literature-mlr.md) |

---

## G — Synthesis

| # | Trap | Chapter |
| - | ---- | ------- |
| G1 | **49% of SE "systematic reviews" are really scoping studies**; only 20.4% cite any synthesis method | [08](./08-extraction-and-synthesis.md) |
| G2 | **4 of 10 synthesis-method citations pointed at references that do not define the method** | [08](./08-extraction-and-synthesis.md) |
| G3 | **Classification alone is not synthesis.** Nor is tabulation alone | [08](./08-extraction-and-synthesis.md) |
| G4 | **Vote counting is a fallback, not a method with standing** | [08](./08-extraction-and-synthesis.md) |
| G5 | **Meta-analysis is usually impossible in SE** because reporting varies too much | [01](./01-slr.md), [08](./08-extraction-and-synthesis.md) |
| G6 | **SMD is only valid if SD differences reflect measurement scale**, not real population differences | [08](./08-extraction-and-synthesis.md) |
| G7 | **Identify heterogeneity sources in the protocol, not post hoc** — the anti-fishing rule | [01](./01-slr.md) |
| G8 | **Thematic analysis has limited interpretive power outside a theoretical framework** | [08](./08-extraction-and-synthesis.md) |
| G9 | **Content analysis counts what is easy to classify, not what matters** | [08](./08-extraction-and-synthesis.md) |
| G10 | **Explain how tabulated data answers the questions** — otherwise no synthesis occurred | [01](./01-slr.md) |
| G11 | **Translating codes to themes is not a single pass**; the stopping rule is saturation | [08](./08-extraction-and-synthesis.md) |

---

## H — Reporting

| # | Trap | Chapter |
| - | ---- | ------- |
| H1 | **Report deviations from the protocol.** The failure is not deviating but concealing it | [01](./01-slr.md), [10](./10-reporting-and-evaluation.md) |
| H2 | **Keep a detailed record of decisions throughout** | [01](./01-slr.md) |
| H3 | **Search dates go unreported** — the specific omission that motivated a SEGRESS change | [10](./10-reporting-and-evaluation.md) |
| H4 | **Do not duplicate the limitations discussion** across sections | [10](./10-reporting-and-evaluation.md) |
| H5 | **Full checklist compliance inflates report length**; use the protocol and supplementary material | [10](./10-reporting-and-evaluation.md) |
| H6 | **A threats section without mitigations or acknowledgements is decoration** | [09](./09-threats-to-validity.md) |
| H7 | **ENTREQ omits publication bias and confidence in the evidence body** | [10](./10-reporting-and-evaluation.md) |
| H8 | **An RR report with findings but no recommendations fails the method** | [03](./03-rapid-review.md) |
| H9 | **Grey-literature URLs rot** — 23.7% dead, 24.8% never recorded. Stamp the access date at retrieval | [05](./05-grey-literature-mlr.md) |

---

## I — Scope and expectations

| # | Trap | Chapter |
| - | ---- | ------- |
| I1 | **Do not build an SLR directly on a mapping study** without additional focused searches | [02](./02-sms.md) |
| I2 | **Mapping studies cannot be guaranteed complete and date quickly** | [02](./02-sms.md) |
| I3 | **A Rapid Review is not a substitute for an SLR**, and not an excuse for absent rigour | [03](./03-rapid-review.md) |
| I4 | **An RR without a practitioner and a practical problem is a deviation to be avoided** | [03](./03-rapid-review.md) |
| I5 | **Repeatability depends on reviewer experience** — expert pairs converged; research associates did not | [01](./01-slr.md) |
| I6 | **8–9 months is normal for a PhD-level SLR; 2–3 months is insufficient** | [01](./01-slr.md) |
| I7 | **Two independent reviews of the same topic shared only 33 of 44 papers** | [06](./06-search-and-selection.md) |
| I8 | **A mitigation for one threat can create another** — snowballing and grey literature mitigate publication bias but introduce their own risks | [09](./09-threats-to-validity.md) |
| I9 | **Non-expert reviewers omit well-known studies and cannot reason about findings** (TV21) — automation that hides the process conceals this rather than fixing it | [09](./09-threats-to-validity.md) |
