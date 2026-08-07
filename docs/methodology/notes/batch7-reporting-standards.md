# Batch 7 — Reporting Guidelines, Checklists, and Report Evaluation Procedures

Source extractions: `scratchpad/txt/`. All six papers read in full. Verbatim quotation used
throughout for checklist items. Where the PDF extraction split an item across lines or columns
it has been reassembled faithfully; nothing has been reconstructed from memory.

---

## kitchenham_segress_2023 — SEGRESS: Software Engineering Guidelines for REporting Secondary Studies

(Kitchenham, Madeyski & Budgen, *IEEE Transactions on Software Engineering*, vol. 49, no. 3,
March 2023, pp. 1273–1298. DOI 10.1109/TSE.2022.3174092)

**Type:** reporting standard (SE-specific), derived from PRISMA 2020.

**Role in corpus:** This is the only reporting standard that covers *all four* secondary-study
types this project builds workflows for — quantitative SR, mapping study, qualitative review,
mixed-methods review, plus tertiary studies as a special case — in a single 27-item checklist
that says, item by item, whether the item is *required*, *optional*, or *not required* for each
type.

### THE CHECKLIST — reproduce IN FULL

#### SEGRESS (Table 9): "The PRISMA 2020-Inspired Structured Checklist for Reporting SE Secondary Studies"

The table interleaves unnumbered *section-level guidance rows* (which carry real instructions,
not just headings) with the 27 numbered PRISMA items and their sub-items. Both are reproduced.

| Item # | Section | Checklist item (verbatim) | Notes/guidance |
|---|---|---|---|
| — | Full Report | "Use of SEGRESS may result in long documents. For publication purposes, authors should consider referencing material in the protocol, publishing some material in supplementary material, and reporting any large-scale model building exercise separately from the basic SR report." | Unnumbered guidance row; opens the table. |
| — | Title (section) | "Identify both the report topic and type of secondary study, so potential readers can find the report." | Section-level purpose statement. |
| 1 | Title | "Identify the report as a systematic review, systematic mapping study, tertiary study, qualitative review, or mixed-methods review and specify the topic being reviewed, see explanation and examples in [8, Section 2.1]. **Required for all review types.**" | Widened from PRISMA's "Identify the report as a systematic review." |
| — | Abstract (section) | "Provide a summary of the entire report, so potential readers can easily assess its relevance." | Section-level purpose statement. |
| 2 | Structured abstract | "Provide a structured summary incl.: Background (emphasizing the importance of this research), Objective, Methods, Results, Limitations (optional), Conclusion. Guidelines for constructing an abstract can be found in [15, Table 2] and [20, Box 2] and are discussed in the SEGRESS Supplementary Material [8, Section 2.2]. **Required for all review types.**" | [15, Table 2] = the PRISMA 2020 for Abstracts checklist; [20, Box 2] = PRISMA-S. SEGRESS does not restate the 12 abstract items — it points at PRISMA 2020 Table 2 (reproduced below under PRISMA). |
| — | Introduction (section) | "Set context for the work." | Section-level purpose statement. |
| — | Opening | "Introduce the larger problem the paper is targeting, lay out a broad context for the work, and highlight the importance of the work to a large audience. In subsequent steps define the research area, establish a niche within the area (knowledge gap), and then focus on the niche." | Unnumbered item — **SEGRESS addition with no PRISMA counterpart.** |
| 3 | Rationale | "Describe information the reader needs to understand the work the authors did, why it is important, i.e., the rationale for the study (e.g., update, new topic area, new empirical results, mature topic having no previous systematic review) and how it contributes to the larger problem, see explanation and example in [8, Section 2.3]. **Required for all review types.**" | |
| 4 | Objectives | "Specify the research questions, explaining how they contribute to the larger problem, see [8, Section 2.4]. **Required for all review types.**" | PRISMA's "objective(s) or question(s)" is narrowed to *research questions* — the SE norm. |
| — | Methods (section) | "Outline procedures you followed and resources you used to conduct your work." | Section-level purpose statement. |
| 5 | Eligibility criteria | "Use the study characteristics to define eligibility criteria based on the intervention or topic of interest [8, Section 3.1]. Criteria used to restrict the search must be specified and justified (e.g., search start and end dates, language limitations, journal restrictions, publication restrictions). Specify how any existing systematic reviews and/or qualitative reviews on the topic of interest, found by the search process, will be used. **Required for all review types.** Tertiary mapping studies investigating research trends must justify search restrictions, such as limiting inclusion to papers in high quality journals, in terms of the study RQs." | Carries the date-restriction requirement Budgen et al. asked for. Explicit tertiary-study clause. |
| 6 | Information sources | "Describe all information sources, databases, primary study references, and others (e.g., researchers) with search end dates. The Supplementary Material [8, Section 3.4] includes a checklist for reporting the search process based on the PRISMA-S guide [20], while [106] guides on how should software engineering secondary studies include grey material. **Required for all review types.**" | [106] = Kitchenham, Madeyski & Budgen, "How should software engineering secondary studies include grey material?" |
| 7 | Search Strategy | "Present full search strategy, including, as appropriate, electronic search strings, snowballing, manual search, finding unpublished materials, and any method(s) used to assess achieved completeness. If previous reviews exist, explain how they have contributed to the current search process. The Supplementary Material [8, Section 3.5] includes a checklist for reporting the search process based on the PRISMA-S guide [20]. **Required for all review types.** Qualitative reviews should explain any search processes aimed at finding deviant cases and exceptions and any exploratory scoping of the literature." | Adds snowballing, manual search and completeness assessment — all SE-specific additions absent from PRISMA item 7. |
| 8 | Selection Process | "State the process for selecting studies, including the specific phases of the selection process, the number of assessors per study, methods of handling disagreements, any tools used, and any methods of assessing agreement rates [8, Section 3.6]. **Required for all review types.** Qualitative studies should explain exclusions that relate to synthesis issues rather than eligibility criteria." | Adds *agreement rates* (κ) explicitly. |
| 9 | Data Collection Process | "Specify the method used to collect data from reports, including how many reviewers collected data from each report, whether they worked independently, any processes for obtaining or confirming data from study investigators, and, if applicable, details of automation tools used in the process [8, Section 3.7]. **Required for all review types.** For qualitative reviews, indicate which areas of each primary study were analysed." | |
| 10a | Data items | "List, define and justify all outcomes for which data was sought, explaining their relationship to the research questions [8, Section 3.8]. **Required for all review types except Mapping studies, because they do not analyse primary study outcomes.**" | |
| 10b | Data items | "List and define all non-outcome variables for which data was sought (e.g., participant and intervention characteristics, funding source). Describe any assumptions made about any missing or unclear information [8, Section 3.9]. **Required for all review types.** For mapping studies define any classification systems used to categorize the data items and confirm how the data item relates to the research questions." | The classification-scheme clause is *the* mapping-study hook. |
| 11 | Study Risk Of Bias Assessment | "Specify the methods used to assess risk of bias in the included studies, including details of the tool(s) used, how many reviewers assessed each study and whether they worked independently, and, if applicable, details of automation tools used in the process [8, Section 3.10]. **This is optional for mapping studies, but required for all other review types.**" | |
| 12 | Effect Measures | "Specify for each outcome the effect measure(s) (e.g., risk ratio, mean difference) used in the synthesis or presentation of results [8, Section 3.11]. **This is required for quantitative reviews and meta-analyses. It is sometimes reported by mapping studies, depending on the research questions** (e.g., if the research question involves identifying the definitions of outcome metrics used in empirical studies). **It is not required for qualitative reviews.**" | |
| 13 | Analysis and Synthesis | "Quantitative SRs and qualitative reviews should report the methods used for synthesis of primary study outcomes [8, Section 3.12]. Mapping studies should report the methods used to analyse primary study characteristics." | Parent row for 13a–13f. Note the section is renamed from PRISMA's "Synthesis methods" to **"Analysis and Synthesis"**. |
| 13a | methods | "Describe the process used to decide which studies were eligible for each synthesis [8, Section 3.13]." | PRISMA's worked example parenthetical is dropped. |
| 13b | methods | "Describe any methods required to prepare the data for presentation or synthesis, such as handling missing summary statistics, or data conversions [8, Section 3.14]. **Not required for mapping studies.** Qualitative studies should describe the coding processes adopted and specify whether it was inductive (i.e., based on deriving the code from the raw textual data, which is typical for grounded theory analyses), or deductive (i.e., based on pre-existing themes or theories)." | |
| 13c | methods | "Describe any methods used to tabulate or visually display results of individual studies and synthesis [8, Section 3.15]. **Required for all review types.** For mapping studies describe the methods used to prepare tables, graphs and maps of study characteristics." | |
| 13d | methods | "Describe any methods used to synthesize results and provide a rationale for the choice(s) [8, Section 3.16]. **Required for all types of review except mapping studies.** If meta-analysis was performed, describe the model(s), method(s) to identify the presence and extent of heterogeneity, and the software packages(s) used. Qualitative studies should, where necessary, identify constructs analyzed, explain how findings from different studies were compared, and specify how synthesized findings were validated." | |
| 13e | methods | "Describe any sensitivity analysis conducted to assess robustness of the synthesized results [8, Section 3.17]. Formal procedures are available for quantitative synthesis and mixed-methods analysis, such as removing high influence data points. For qualitative methods, this involves discussing the impact of any deviant cases and exceptions on the synthesized findings. **Not required for mapping studies.**" | **ORDER DELIBERATELY SWAPPED vs PRISMA** — PRISMA 13e is heterogeneity, 13f is sensitivity. See "Differences" table. |
| 13f | methods | "Describe any methods used to explore possible causes of heterogeneity among study results [8, Section 3.18]. **Required for all types of review except mapping studies.**" | **ORDER DELIBERATELY SWAPPED vs PRISMA.** |
| 14 | Reporting Bias Assessment | "Describe any methods used to assess risk of bias due to publication bias [8, Section 3.19]. **Not required for mapping studies, or secondary studies investigating SE research practices rather than SE development and maintenance methods.**" | Reworded: PRISMA says "risk of bias due to missing results in a synthesis (arising from reporting biases)". |
| 15 | Certainty Assessment | "Describe methods used to assess certainty (or confidence) in the body of evidence for an outcome (e.g., GRADE) [8, Section 3.20]. **Not required for mapping studies or secondary studies investigating SE research practices, but essential for all other review types.** See Sections 3.3.3 and 5.1.3." | Names GRADE explicitly (PRISMA item 15 does not). |
| — | Results (section) | "Communicate complex, quantitative and qualitative information in an easy to read manner." | Section-level purpose statement. |
| 16a | Study selection | "Describe the results of the search and selection process, from the number of records identified in the search to the number of studies included in the review, ideally using a flow diagram [8, Section 4.1]. Report agreement statistics, if collected. **Required for all review types.** Qualitative studies should describe any iteration between selection and synthesis." | Adds agreement statistics. |
| 16b | Study selection | "Cite studies that met many but not all inclusion criteria ('near-misses') and explain why they were excluded [8, Section 4.2]. **Optional for mapping studies, required for all other review types.** Qualitative reviews should identify any eligible studies that were excluded from synthesis and justify the exclusions." | Reworded from PRISMA's "studies that might appear to meet the inclusion criteria" to the "near-misses" formulation. |
| [17-22] | (Reporting Style note) | "Reporting Style: If reporting syntheses (i.e., meta-analysis results or answers to research questions) obtained from different subgroups of primary studies or different research questions consider using an iterative reporting approach, keeping items 17 to 22 together for primary studies subgroups or specific research questions. Note that, even if using an iterative style for reporting, it may be appropriate to report information that was obtained from every primary study in integrated tables. The issue is that risk of bias among contributing primary studies will be different for different syntheses if they depend on different subsets of studies." | **SEGRESS addition with no PRISMA counterpart.** Addresses the "iteration" problem of §3.5.1. |
| 17 | Study characteristics | "Describe the characteristics of each included study, and provide citations [8, Section 4.3]. **Required for all review types.**" | |
| 18 | Risk of Bias in Studies | "Present data on the risk assessment for each study [8, Section 4.4]. Report agreement statistics. **Optional for mapping studies but required for all other review types.**" | |
| 19 | Results of individual studies | "For quantitative reviews, for all outcomes, present for each study [8, Section 4.5]: a) summary statistics for each group (where appropriate) and (b) an effect estimate and its precision (e.g., confidence/credible interval), ideally using structure tables or plots. For qualitative reviews, present the major findings from each study included in the synthesis. **Not usually required for mapping studies.**" | ("structure tables" is as printed; PRISMA reads "structured tables".) |
| 20 | Results of Analyses and Syntheses | "Quantitative SRs and Qualitative reviews should describe the results of their syntheses [8, Section 4.6]. Mapping studies should report their analyses of primary study characteristics." | Parent row for 20a–20d. Section renamed from PRISMA's "Results of syntheses". |
| 20a | Results of Analyses and Syntheses | "Report each synthesis, briefly summarising the characteristics and risk of bias among contributing studies [8, Section 4.7]. **Required for all review types.** For qualitative studies, define any derived themes, and focus on theory building and testing. Provide appropriate quotations specifying the primary study from which the quotation was obtained, and whether it was produced by the study authors or individual study participants. For mapping studies, discuss the maps and tables produced to address each research question." | |
| 20b | Results of Analyses and Syntheses | "Present results of all statistical syntheses conducted [8, Section 4.8]. If meta-analysis was performed, present for each analysis, the summary estimate and its precision (e.g., confidence/credible interval) and measures of statistical heterogeneity. If comparing groups, describe the direction of the effect. **Only required for quantitative reviews.**" | |
| 20c | Results of Analyses and Syntheses | "Present results of all sensitivity analysis conducted to assess the robustness of the synthesized results [8, Section 4.9]. Qualitative studies should discuss deviant cases and exceptions [95] and should report any additional validation of qualitative models." | **ORDER DELIBERATELY SWAPPED vs PRISMA** (PRISMA 20c = heterogeneity, 20d = sensitivity). |
| 20d | Results of Analyses and Syntheses | "Present results of all investigations of possible causes of heterogeneity among study results [8, Section 4.10]. **Not required for mapping studies.** Other review types should attempt to identify qualitative factors that might explain different primary study outcomes." | **ORDER DELIBERATELY SWAPPED vs PRISMA.** |
| 21 | Reporting Biases | "Report results of assessing publication bias for each synthesis [8, Section 4.11]. For meta-analysis, report the heterogeneity among studies and provide funnel plots. **Not usually required for mapping studies or qualitative studies.**" | Adds funnel plots explicitly. |
| 22 | Certainty of Evidence | "Present assessment of certainty (or confidence) in the body of evidence for each reported finding [8, Section 4.12]. **Not required for mapping studies. Required for all other review types.**" | PRISMA says "for each outcome assessed"; SEGRESS says "for each reported finding". |
| — | Discussion (section) | "Turn data into knowledge (i.e., advice or recommendations for practitioners, academics, and educators), point out how your results provide novel understanding, challenge previous knowledge, or resolve persisting controversy answering questions raised in the Introduction." | Section-level purpose statement — **SEGRESS addition.** |
| 23a | Discussion | "Provide a general interpretation of the results in the context of other evidence [8, Section 5.2]. Where applicable compare review findings with other reviews on the same topic. **Required for all review types.**" | |
| 23b | Discussion | "Discuss any limitations of the evidence included in the review [8, Section 5.3]. **Required for quantitative and qualitative reviews. Not required for mapping studies.**" | |
| 23c | Discussion | "Discuss any limitations of the review process used [8, Section 5.4]. **Required for all reviews, but include only those issues that were not previously addressed as part of the specification of the specified review process or when discussing the synthesis results.**" | This is SEGRESS's **theoretical rationale for the Threats to Validity section** — non-duplication. |
| 23d | Discussion | "Discuss implications of the results for practice, policy and future research [8, Section 5.5]. **Required for all review types. For mapping studies, only discussion of future research is relevant.**" | |
| 24a | Registration and Protocol | "Provide registration information for the review, including register name and registration number, or state that the review was not registered [8, Section 6.2]. Guidelines for constructing an SR protocol can be found in the PRISMA-P statement [18]. **Optional for all review types.**" | Downgraded from PRISMA (where all of item 24 is expected). |
| 24b | Registration and Protocol | "Indicate where the review protocol can be accessed or state why no protocol is available [8, Section 6.3]. **Optional for mapping studies, required for all other review types.**" | PRISMA says "or state that a protocol was not prepared"; SEGRESS demands a *reason*. |
| 24c | Registration and Protocol | "Describe and explain any amendments to information provided at registration or in the protocol [8, Section 6.4]. **Required for quantitative and qualitative review types, optional for mapping studies.**" | |
| 25 | Support | "Describe sources of financial and non-financial support for the review and the role of the funders or sponsors of the review [8, Section 6.5]. **Required for all review types.**" | |
| 26 | Competing Interests | "Declare competing interests of the review authors [8, Section 6.6]. **Required for all review types.**" | |
| 27 | Availability Of Data, Code and Other Materials | "Report which of the following are publicly available and where they can be found (e.g., Zenodo, Figshare, Dryad): template data collection forms; data extracted from included studies; data used for all analyses; analytic code; any other materials used in the review or to produce the review (e.g., Rnw file if using R scripts or code chunks as analytic code) [8, Section 6.7] [107]. **Optional but recommended for all review types.**" | Adds named repositories and the reproducible-research (Rnw) clause. |

**Count:** 27 top-level items → **44 numbered checklist rows** when sub-items are expanded, plus
**9 unnumbered guidance rows** (Full Report; Title section; Abstract section; Introduction
section; Opening; Methods section; Results section; the [17-22] Reporting Style note; Discussion
section) = **53 rows total**.

#### SEGRESS's own reproduction of PRISMA 2020 (its Table 4)

SEGRESS Table 4 restates PRISMA 2020 as its baseline. Its wording differs in places from the
authoritative Page et al. text (see the PRISMA section below for the authoritative version).
Divergences worth knowing, because SEGRESS readers see the Table 4 version:

| Item | SEGRESS Table 4 wording | Page et al. 2021 (authoritative) |
|---|---|---|
| 5 | "…and how studies were grouped for synthesis." | "…and how studies were grouped for the syntheses." |
| 6 | "Specify all databases, registers, web sites, organizations, reference lists and other sources, **to be searched or consulted**. Specify the date when each source was last searched or consulted." | "…and other sources **searched or consulted to identify studies**." (SEGRESS's future tense reads like a protocol.) |
| 10a | "…compatible with **each outcome** in each study…" | "…compatible with **each outcome domain** in each study…" |
| 13a | "Describe the process used to decide which studies were eligible for each synthesis." | "Describe the **processes** used… (e.g. tabulating the study intervention characteristics and comparing against the planned groups for each synthesis (item #5))." |
| 13d | "…the presence and extent of heterogeneity…" | "…the presence and extent of **statistical** heterogeneity…" |
| 16b | "Cite studies that met many but not all inclusion criteria ('near-misses') and explain why they were excluded." | "Cite studies that might appear to meet the inclusion criteria, but which were excluded, and explain why they were excluded." |
| 20d | "Present results of all sensitivity analysis conducted to assess the robustness of synthesized results" | "…all sensitivity analyses conducted…" |
| 22 | "Present assessment of certainty (or confidence) in the body of evidence for each **item** assessed." | "…for each **outcome** assessed." |
| 23b | "Discuss any limitations of the evidence included in the review" | identical |
| 24a | "…incl. register name & registration number…" | "…including register name and registration number…" |
| 26 | "Declare **and** competing interests of the review authors." | "Declare **any** competing interests of review authors." (`and` is an extraction/typo artefact in the SEGRESS table.) |

### The PRISMA flow diagram

SEGRESS does not redraw the flow diagram; item 16a says "ideally using a flow diagram" and
defers to PRISMA. The exact structure is documented under `page_prisma_2021` below.

### Differences between SEGRESS and PRISMA 2020

| Aspect | PRISMA 2020 | SEGRESS | Why |
|---|---|---|---|
| Scope | "systematic reviews of studies that evaluate the effects of health interventions"; explicitly *not* for qualitative synthesis | systematic reviews, systematic mapping studies, tertiary studies, qualitative reviews, mixed-methods reviews | "secondary studies in SE are often mapping studies … or qualitative reviews"; PRISMA alone "will be of very limited value to SE researchers". |
| Per-item applicability | none — every item applies | **every item is labelled required / optional / not required per review type** | This is SEGRESS's single largest structural addition. |
| Item 1 (Title) | "Identify the report as a systematic review." | must name the *type* (SR / mapping / tertiary / qualitative / mixed-methods) **and** the topic | so readers/searchers can find it. |
| "Opening" (Introduction) | absent | new unnumbered item: broad problem → research area → niche → focus | SE writing convention. |
| Section-level purpose rows | absent | Title/Abstract/Introduction/Methods/Results/Discussion each carry a one-line statement of purpose | Budgen et al. asked for "a well-defined structure for a secondary study report". |
| "Full Report" length advice | absent | new opening row: reference the protocol, use supplementary material, publish large model-building separately | mitigates the report-length cost of full compliance. |
| Item 5 | inclusion/exclusion + grouping for synthesis | adds: **search restrictions must be specified and justified** (dates, language, journal, publication type); adds: state how existing SRs/qualitative reviews found by the search will be used; adds a tertiary-mapping-study clause | Budgen et al.'s finding that search dates go unreported. PRISMA "assumes that there is no lower bound on the search". |
| Item 7 (Search Strategy) | "full search strategies for all databases, registers and websites, including any filters and limits" | adds **snowballing, manual search, finding unpublished materials, methods used to assess achieved completeness**, and how previous reviews fed the search | SE search practice is not database-only. |
| Item 8 / 16a / 18 | no mention of agreement statistics | explicitly requires **methods of assessing agreement rates** (8) and **reporting agreement statistics** (16a, 18) | SE reviews use κ; PRISMA leaves it implicit. |
| Item 10b | "other variables… assumptions about missing information" | adds "**For mapping studies define any classification systems used to categorize the data items**" | the defining activity of a mapping study. |
| Item 13 heading | "Synthesis methods" | "**Analysis and Synthesis**" | mapping studies *analyse characteristics*; they do not *synthesise outcomes*. Same reason PRISMA-ScR's "Synthesis of Results" is rejected in favour of "Analysis of Study Characteristics". |
| Item 13b | data preparation only | adds qualitative coding: **inductive vs deductive** must be stated | ENTREQ item 17/19 folded in. |
| 13e ↔ 13f | 13e = explore heterogeneity, 13f = sensitivity analysis | **swapped**: 13e = sensitivity analysis, 13f = explore heterogeneity | "we thought that it made more sense to perform any sensitivity analysis which could lead to a revision of the SR analysis or synthesis before initiating any investigation of possible reasons for the heterogeneity of the results." |
| 20c ↔ 20d | 20c = heterogeneity results, 20d = sensitivity results | **swapped**: 20c = sensitivity results, 20d = heterogeneity results | same rationale. (Note: the paper's own prose says "we have therefore changed the order of items 13d and 13f, items 20c and 20d in SEGRESS" — the *table* shows the swap at 13e/13f and 20c/20d. Treat the table as authoritative; the prose reference to "13d" appears to be a slip.) |
| Item 14 | "risk of bias due to missing results in a synthesis (arising from reporting biases)" | "risk of bias due to **publication bias**" | plainer term for SE readers. |
| Item 15 / 22 | "certainty (or confidence) in the body of evidence" | same, but **names GRADE** and cross-references GRADE-CERQual for qualitative reviews | PRISMA leaves the instrument open. |
| Item 21 | assessments of reporting bias per synthesis | adds "**For meta-analysis, report the heterogeneity among studies and provide funnel plots**" | concrete SE-usable instruction. |
| Item 23c | "Discuss any limitations of the review processes used." | adds "**include only those issues that were not previously addressed** as part of the specification of the specified review process or when discussing the synthesis results" | the anti-duplication rule; a direct answer to the Ampatzoglou checklist problem. |
| Item 24a/24b/24c | all expected | 24a **optional for all**; 24b optional for mapping, required otherwise; 24c optional for mapping | SE has no review registry culture. |
| Item 27 | list of artefacts | adds named repositories (Zenodo, Figshare, Dryad) and reproducible-research artefacts ("Rnw file if using R scripts or code chunks as analytic code"); **"Optional but recommended"** | |
| [17-22] iterative reporting | absent | new note permitting/encouraging iterating items 17–22 per subgroup or per RQ | PRISMA's linear order breaks when different findings rest on different subsets of studies. |
| Length | not addressed | addressed twice (Full Report row; §6.3) | compliance inflates reports. |
| Removed | nothing is removed outright — items are marked *not required* per type instead | | "rather than develop separate standards for mapping studies it would be preferable to extend the definitions and scope of PRISMA 2020 items". |

### Guidance per study type

SEGRESS's per-type applicability, collected from Table 9 into one view:

| Item | Quantitative SR | Mapping study | Qualitative review | Mixed-methods | Tertiary study |
|---|---|---|---|---|---|
| 1–9 | required | required | required (7, 8, 9 carry extra qualitative clauses) | required | required |
| 10a | required | **not required** ("they do not analyse primary study outcomes") | required | required | per type |
| 10b | required | required + **define classification systems** | required | required | required |
| 11 Study RoB | required | **optional** | required | required | see note below |
| 12 Effect measures | required | **sometimes**, depending on RQs | **not required** | required | per type |
| 13b | required | **not required** | required + coding inductive/deductive | required | per type |
| 13c | required | required (tables, graphs, maps) | required | required | required |
| 13d | required | **not required** | required + constructs/comparison/validation | required | per type |
| 13e (sensitivity) | required | **not required** | required (deviant cases/exceptions) | required | per type |
| 13f (heterogeneity) | required | **not required** | required | required | per type |
| 14 Reporting bias | required | **not required** | required | required | **not required** if investigating SE research practices rather than development/maintenance methods |
| 15 Certainty | essential | **not required** | essential | essential | **not required** if investigating SE research practices |
| 16b near-misses | required | **optional** | required + justify synthesis exclusions | required | per type |
| 18 RoB results | required | **optional** | required | required | per type |
| 19 Individual results | required | **not usually required** | required (major findings per study) | required | per type |
| 20b statistical syntheses | required | — | **only quantitative** | required | per type |
| 20d heterogeneity results | required | **not required** | required | required | per type |
| 21 Reporting biases | required | **not usually** | **not usually** | required | per type |
| 22 Certainty of evidence | required | **not required** | required | required | per type |
| 23b limitations of evidence | required | **not required** | required | required | per type |
| 23d implications | required | **only future research is relevant** | required | required | required |
| 24b protocol location | required | **optional** | required | required | per type |
| 24c amendments | required | **optional** | required | required | per type |

Explicit routing advice for tertiary studies (§6.1):
> "Readers performing tertiary studies related to assessing research methods should read the
> comments related to mapping studies. Researchers performing other types of tertiary study
> should consult the comments related to quantitative and qualitative reviews, as appropriate."

Also on tertiary studies (§4.3.2):
> "Unlike most SE mapping studies, when conducting tertiary mapping studies that investigate SR
> methodology, assessment of the quality of the primary studies is often required to address
> mapping study research questions. Thus, in terms of PRISMA-ScR, identifying quality assessment
> criteria and extracting quality assessments would be regarded as a data charting process."

And on QA instruments (from Yang et al., §2.3):
> "The QA instruments for tertiary studies and secondary studies are different. Since the primary
> studies in a tertiary study are secondary studies, tertiary studies can all use the DARE
> criteria as quality assessment criteria."

Mapping study reporting, additional (§4.3):
- Search: "In most respects, the search for evidence is the same for mapping studies as it is for
  systematic reviews. However, there is less emphasis on completeness and more emphasis on
  defining the search process used, and specifying any search limitations … together with a
  rationale for any such limitations."
- QA: "The main simplification for mapping studies compared with quantitative SRs is that the
  PRISMA standard for scoping reviews (PRISMA-ScR) accepts that there will be no formal
  aggregation of the outcomes of primary studies. This implies that risk of bias due to synthesis
  is irrelevant, as is certainty assessment."
- Limitations: "if there have been no deviations from the secondary review standards or the review
  protocol and no critical appraisal of primary studies, discussion of limitations is not
  necessary for mapping studies."
- Terminology: "The term *Data Charting* is misleading and the PRISMA 2020 term *Data Collection
  Process* is more appropriate." / "The term *Synthesis of Results* in PRISMA-ScR should be
  replaced by *Analysis of Study Characteristics* in any standards used for SE mapping studies."

Qualitative review reporting: SEGRESS maps ENTREQ (21 items) and RAMESES (19 items) onto PRISMA
2020 (Tables 7 and 8, reproduced under "Data extraction/analysis" support below). Key structural
findings:
- ENTREQ items sit at a *lower* level of detail: ENTREQ items 10, 11, 12 all map to PRISMA item 11.
- "ENTREQ omits some standard items such as title, abstract, protocol registration, data
  availability, and financial support."
- "Of most significance is that ENTREQ omits any discussion of publication bias or confidence in
  the body of evidence."
- RAMESES collapses selection and appraisal into one element, and "does not explicitly mention
  critical appraisal of documents as an issue that is separate from document selection."

### Report evaluation procedures

**1. The DARE criteria (Database of Attributes of Reviews of Effects)** — the instrument Budgen et
al. used to evaluate 178 SE SRs, and the instrument SEGRESS says tertiary studies can use as
their QA instrument. Verbatim, all five:
1. "Are the review's inclusion and exclusion criteria described and appropriate?"
2. "Is the literature search likely to have covered all relevant studies?"
3. "Did the reviewers assess the quality/validity of the included studies?"
4. "Were basic data/studies adequately described?"
5. "Were the included studies synthesised?"

**2. Budgen et al.'s nine "essential information" items (SEGRESS Table 2)** — the requirements
SEGRESS was built to satisfy, each mapped to the PRISMA item that carries it:

| Review aspect | Information Required (verbatim) | PRISMA item |
|---|---|---|
| Inclusion/Exclusion | "The rules for both inclusion and exclusion should be clearly stated." | 5 |
| Inclusion/Exclusion | "How the rules were applied, and any difference between reviewers were resolved should be described." | 8 |
| Inclusion/Exclusion | "The number of papers remaining at each stage of selection should be reported." | 16a |
| Searching | "All of the search mechanisms used should be clearly reported." | 6, 7 |
| Searching | "The period covered by the search should be explicitly stated, and the dates when any searches were performed should be reported." | 5, 6 |
| Quality Assessment | "When performed, the intended use as well as the checklist items should be reported." | 13e, 13f, 15 |
| Quality Assessment | "How quality assessment was undertaken, and how any differences between reviewers were resolved needs to be explained." | 11, 15 |
| Synthesis | "Where performed, the form of the synthesis adopted for specific research questions should be described, and the reasons for its use should be given." | 13a |
| Outcomes | "Key findings should be clearly reported, together with any information related to the 'strength of evidence' that applies to them." | 22, 23b, 23d |

**3. GRADE — grading certainty in a body of evidence.** Four levels: **high, moderate, low, very
low**. Five domains, "each of which must be assessed against each of the four levels":
1. **Risk of bias of individual studies** — "In SE, small-scale, student-based laboratory
   experiments should initially be regarded as having a high risk of bias, and thus provide very
   low certainty for evidence. In contrast, large experiments with industry practitioners … could
   be assessed as having relatively low risk of bias … Furthermore, field studies, whether
   qualitative or quantitative, should initially be regarded as high quality evidence but could be
   re-assessed to a higher risk of bias if their methodology was particularly weak."
2. **Publication bias** — funnel plots where meta-analysis is possible; otherwise "the risk of
   publication bias can usually only be addressed by the stringency of the search process, but can
   also consider factors such as whether the primary studies are dominated by small positive
   studies."
3. **Imprecision** — "related to the confidence intervals associated with overall effect size
   estimates. Confidence intervals that do not exclude the null hypothesis would usually lead to a
   reduction in the certainty associated with the body of evidence."
4. **Inconsistency** — "whether the direction of the effect size is consistent across the
   individual studies… The body of evidence is downgraded if studies give inconsistent results. In
   qualitative studies, strong disagreements between the findings of studies with similar contexts
   would be an indication of inconsistency."
5. **Indirectness** — "whether the studies directly test the concept of interest or are inferred
   from indirect comparison." Three SE causes: unrepresentative participants; the reported
   intervention differs from the intervention of interest; outcome measures differ from those of
   primary interest.

Process: "The process of evaluating findings against the GRADE domains is subjective. It should
usually be done by several reviewers independently. Each reviewer should provide an explanation
for their assessment of each domain for each separate review finding. Differences among reviewer
assessments should be discussed and, if necessary, mediated until agreement is reached."

**4. GRADE-CERQual — certainty for qualitative syntheses.** Four components, each a paper in the
Implementation Science series:
- **Methodological limitations** (Munthe-Kaas et al.) — "Assessments should emphasize
  methodological strengths and weaknesses rather than the quality of reporting."
- **Coherence** (Colvin et al.) — "an assessment of how clear and cogent is the fit between the
  data from the primary studies and a review finding that synthesizes that data".
- **Adequacy of data** (Glenton et al.) — "somewhat analogous to sample size and number of
  experiments in quantitative studies. It requires an assessment of whether the number of
  participants and the richness of the data obtained from the participants are sufficient to
  understand and explain a phenomenon."
- **Relevance** (Noyes et al.) — "the extent to which the body of data from the primary studies
  supporting a review finding is applicable to the context specified in the research question".
Output: an overall CERQual assessment of confidence plus a **Summary of Qualitative Findings
table** (Lewin et al., paper 2).

**5. Cochrane risk-of-bias domains for non-randomised designs** (Cochrane Handbook chs 22–25) —
the four SE-relevant RoB domains:
1. **Confounding** — "occurs when a factor other than the intervention of interest could have
   caused the effect." SE example: a manager restricting design inspections to complex components.
2. **Selection bias** — "occurs when some eligible participants, or some outcome events, are
   excluded in a way that leads to systematic bias in the outcomes." SE example: restricting
   eligibility to the most capable students.
3. **Information bias** — "may be introduced if intervention status is wrongly classified, or if
   outcomes are wrongly classified or measured with error." SE example: process conformance —
   engineers reverting to their old method.
4. **Non-reporting bias** — "for example, experimenters reporting only outcomes that have
   significant results."
Plus non-domain poor practice: "small sample size, over-simplistic tasks, lack of effect sizes and
confidence intervals, and multiple statistical tests".

**6. Yang et al.'s four QA criteria areas found in SE SRs** (the abstract alternative to Cochrane's
concrete domains): **Rationality** (study rationale, context, RQs); **Rigour** (choice of research
methodology and how it was applied); **Credibility** (clarity and validity of reported results,
extent supported by evidence, relationship between experimenters and participants);
**Contribution** (value of the findings for industry and academia). SEGRESS's verdict: "The items
identified in the Cochrane Handbook are related to the issues identified by Yang et al., but they
are less abstract, which means they may be easier for reviewers to understand and use in a RoB
assessment."

**7. SEGRESS's own validation procedure** (§6.2) — the model for validating a reporting standard:
per-item detailed explanation + list of issues each item must address + an excerpt from a
published SR illustrating each item, *plus* a running example (revising an existing SR) to show
how related items interact. "The PRISMA 2020 authors did not provide any empirical validation of
their checklist."

### Caveats, traps and pitfalls

Verbatim:

- **On terminology substitution** — "once it is appreciated that the term *risk of bias* is a
  replacement for the term *quality assessment*, and that *limitations* is a replacement for
  *threats to validity*, PRISMA 2020 recommends reporting all aspects of the SR process and the
  results of applying that process."
- **PRISMA is not self-explanatory** — "our discussions confirmed that PRISMA 2020 is not simple to
  understand and needs additional explanations and examples from software engineering to be
  suitable for software engineering researchers."
- **RoB ≠ quality** — "the important difference between RoB and quality assessment for individual
  studies is that RoB is about identifying potential methodological flaws that can bias the outcome
  of primary studies, whereas quality is about whether the research was performed as well as
  possible. … although SE researchers may perform other aspects of their experiments to the highest
  possible standard (i.e. the quality may be high), lack of blinding remains a significant RoB."
- **Certainty is per-finding, not per-review** — "it is possible for different findings from the
  same study to be assessed as having different quality of evidence. … If only the primary studies
  assessed as having high risk of bias are the ones that report task duration outcomes, any
  assessment of the quality of evidence associated with findings associated with duration will be
  lower than the quality of evidence associated with development effort findings."
- **The checklist-in-a-Threats-section trap** — "The practical problem of adopting Ampatzoglou et
  al.'s recommendations is that a checklist is supposed to represent a complete set of items that
  must all be addressed. However, attempts to apply the complete checklist in an isolated Threats
  to Validity section can lead to duplicate reporting of issues that may have already been covered
  in the Methods and Results sections."
- **What belongs in a threats section** — "it should include only issues that have not been fully
  explained in other parts of the paper." And: "An approach to reporting validity threats for
  systematic reviews and mapping studies that properly reflects their differences and similarities.
  For example, since mapping studies do not synthesize the outcomes of primary studies, there can
  be no threats to validity associated with statistical meta-analysis such as primary study
  heterogeneity, publication bias, or generalizability."
- **Classic social-science threat taxonomies don't fit SRs** — "Ampatzoglou et al. make a very good
  point that classic threats to validity, as described in the social sciences … are not generally
  applicable to systematic reviews."
- **What-is-reported ≠ what-should-be-reported** — "The information the researchers extracted
  answered the question 'What threats to validity are reported', it does not answer the question
  'What threats to validity should be reported'."
- **The guidelines themselves are mitigations** — "systematic review guidelines were explicitly
  designed to mitigate many threats to validity in secondary studies, for example, requiring
  extensive searches to avoid publication bias, and having multiple reviewers independently address
  tasks such as searching, selection, data collection and quality assessment to avoid researcher
  bias. … Thus, Ampatzoglou et al. may have under-estimated the extent to which SE researchers have
  actually avoided many threats to validity."
- **Mapping-study threats and SR threats are different threats** — "There was no explicit
  consideration of the difference between a systematic review and a mapping study, although many
  threats to validity may be different. For example, among Data Validity threats, Ampatzoglou et
  al. include *The selection of classification system is biased* which is a mapping study issue, and
  among Research Validity threats they include *Lack of comparable studies*, that is a quantitative
  systematic review issue that is irrelevant for mapping studies which do not investigate the
  outcomes of empirical studies."
- **Deviations must be justified and their impact discussed** — Page et al. on item 23c, quoted in
  full by SEGRESS: "Discussing limitations, avoidable or unavoidable, in the review process should
  help readers understand the trustworthiness of the review findings. For example, authors might
  acknowledge the decision to restrict eligibility to studies in English only, search only a small
  number of databases, have only one reviewer screen records or collect data, or not contact study
  authors to clarify unclear information. They might also acknowledge that they were unable to
  access all potentially eligible study reports or to carry out some of the planned analyses because
  of insufficient data. While some limitations may affect the validity of the review findings,
  others may not." SEGRESS's gloss: "researchers need to discuss the implications of any deviations
  from the standard SR guidelines in terms of their likely impact on the review findings."
- **Item 23b explained** (Page et al., quoted in full): "Discussing the completeness, applicability,
  and uncertainties in the evidence included in the review should help readers interpret the
  findings appropriately. For example, authors might acknowledge that they identified few eligible
  studies or studies with a small number of participants, leading to imprecise estimates; have
  concerns about risk of bias in studies or missing results; or identified studies that only
  partially or indirectly address the review question, leading to concerns about their relevance and
  applicability to particular patients, settings, or other target audiences."
- **Ad hoc amendment is worse than a standard** — "ad hoc and uncoordinated changes in reporting
  practices aiming to change individual aspects of SR reporting may cause confusion about what is to
  be reported in other related sections, and might also cause SE systematic review terminology to
  deviate from existing standards."
- **PRISMA's linear order breaks (iteration)** — "One reporting problem with PRISMA 2020 is that
  items 18 and 19 appear to assume a linear order for reporting all primary study RoB data and
  outcome data. In contrast, all item 20 sub-items and item 21 require reporting results for each
  finding. Thus, there is some iteration among items, but it is not clearly defined."
- **PRISMA's linear order breaks (repetition)** — "items 19 and 20a seem to have considerable
  overlap and it is difficult to understand what to report in item 23 given what has been reported
  in items 20, 21, and 22 without introducing excessive repetition."
- **Length** — "A practical concern is that conforming to SEGRESS (or indeed PRISMA 2020) may
  increase the length of reports of SRs. This may be acceptable if the outcome of the SR is a simple
  meta-analysis, but if the outcomes are more complex (such as a qualitative model that needs
  definition and explanation), it may cause serious length issues." Mitigation: the 1-3-25 method
  (a one-page "take-home" summary for end-users; a three-page executive summary for
  sponsors/policy-makers; a 25-page detailed report on design and conduct for reviewers) — "such
  initiatives have not yet been adopted in SE."
- **The hardest part of SEGRESS** — "the issue of coordinating the assessments of risk of primary
  study bias and risk of missing data in order to produce a GRADE style assessment of the certainty
  in the body of evidence is the most difficult part of using the SEGRESS checklist. … The most
  difficult problem is assessing the risk of missing data/projects because the SR authors need to
  assess the rigour of their own methods."
- **Qualitative reviews are the riskiest adoption** — "Adoption of SEGRESS presents a greater risk
  for qualitative reviews than quantitative reviews and mapping studies."
- **The underlying qualitative checklists are provisional** — "A limitation of SEGRESS is that the
  authors of ENTREQ and RAMESES both acknowledge that their checklists are preliminary checklists.
  This means that SE researchers must remain alert for any changes in the ENTREQ and RAMESES
  checklists that could require them to provide additional information when they report qualitative
  reviews."
- **PRISMA-ScR will change** — "McGowan et al. point out that ongoing revisions to the PRISMA
  statement make it likely that authors of PRISMA-related checklists such as PRISMA-ScR will
  consider revising those checklists to conform with PRISMA 2020. Thus, SE researchers need to be
  aware that new scoping study checklists are likely to be published in the near future."
- **SEGRESS deviates from PRISMA by design, and reasonable people may object** — "We have adapted
  the explanation of some items of PRISMA 2020 that seem more relevant to medical SRs rather than to
  software engineering SRs, based on our view of best SE practice. Some researchers might dispute
  our view of good practice in SE and prefer to conform strictly to the PRISMA 2020 guidelines."
- **Sub-item order is the author's call** — "In general, the order in which sub-items are discussed
  that is adopted in a specific SR should be decided by the authors in order to support report
  clarity."
- **No guidelines exist for *conducting* qualitative reviews** — "It is much more difficult to
  provide standards for reporting qualitative reviews than for mapping studies, not least because
  there is no definitive standard for conducting qualitative systematic reviews." And: "The more
  recent guidelines in [Kitchenham, Budgen & Brereton 2016] acknowledge the need for guidelines for
  qualitative reviews, but treat such reviews as being deviations from the quantitative SR
  guidelines, and do not provide detailed advice."
- **Philosophical positioning is a barrier for engineers** — "For engineers, such as software
  engineers and computer scientists, a specific problem with using any qualitative method is the
  need for individual researchers to consider their personal 'philosophical positioning' and its
  relationship to their choice of qualitative methodology." SEGRESS's own stance: "we have taken a
  pragmatic, realist approach."
- **Omitting publication bias in qualitative reviews is fine, omitting search rigour is not** —
  "Omitting any discussion of publication bias is sensible in the context of qualitative reviews
  since the selection process does not usually require completeness (for example, it may be based
  on theoretical saturation). However, it is important to ensure that there has been a thorough
  search of the literature to avoid missing relevant disconfirming cases."
- **On whether to do QA at all** (Yang et al.) — "It is important to consider whether or not to
  conduct quality assessment."

### Empirical findings worth citing

- Budgen et al.: **178 SE systematic reviews** published 2010–2015, assessed against DARE; yielded
  **12 "lessons learned"** and **9 essential-information items**.
- Zhou et al.: **316 secondary studies** 2004–mid-2015 — **178 SRs, 132 systematic mapping studies,
  6 meta-analyses**. "while most SRs reported internal validity and reliability issues, few reported
  construct validity and external validity issues. Additionally, they reported that methods for
  addressing threats to validity were seldom reported."
- Ampatzoglou et al.: **449 secondary studies** 2007–2016; only **165 papers reported threats to
  validity**; produced a checklist of **22 threats** in **3 categories** (Study Selection, Data
  Validity, Research Validity), each with mitigation actions rated for effectiveness by an expert
  panel.
- Yang et al.: **241 SRs** published 2004–2018 that used a QA instrument; **46 primary studies did
  not explain why they had collected quality assessment data**; **2022 reasons** for using QA were
  classified as:
  - **Selection** (more extensive inclusion/exclusion criteria) — **54%** of reasons (most frequent)
  - **Interpretation** (guide interpretation, determine strength of inference) — **16%**
  - **Investigation** (understand current state of research) — **14%**
  - **Validation** (ensure only good-quality studies included) — **10%**
  - **Weighting** (weight individual studies during synthesis) — **5%**
  Yang et al. conclude "the aims of quality assessment are more concise, the instruments used are
  more diverse and rigorous and the criteria more thoughtful" than in their 2004–2013 study.
- PRISMA 2020 development: Page et al. mapping study identified **60 sources containing 221 unique
  items**, reduced to **175 items** as an item bank; **220 methodologists/editors invited, 110
  replied**; **21-person** consensus group; final feedback from a **convenience sample of 15**.
- PRISMA-ScR construction: Tricco et al. found **five PRISMA items not applicable** to scoping
  reviews (effect sizes, synthesis, risk of bias across studies, additional analysis) and **two
  optional** (risk of bias for primary studies). "In our experience, the same restrictions apply to
  mapping study reports."
- Evidence of experimenter bias in SE meta-analyses: Ciolkowski (inspections) and Shepperd, Bowes &
  Hall (fault prediction) "both reported that the outcomes of their meta-analyses revealed evidence
  of experimenter bias."
- Menzies & Shepperd identified **12 "bad smells"** as indicators of potential problems in software
  analytics papers.

---

## kitchenham_segress_2022 — SEGRESS: The PRISMA 2020-Inspired Structured Checklist for Reporting SE Secondary Studies

(Kitchenham, Madeyski & Budgen, 4-page standalone note, `madeyski.e-informatyka.pl/download/shortly-about-segress-guidelines.pdf`)

**Type:** reporting standard (condensed distribution copy).

**Role in corpus:** The freely-downloadable "just the checklist" artefact — it reproduces SEGRESS
Table 9 in full with no surrounding argument, and states the two terminology substitutions
up-front. It is the version to hand to a tool implementer.

### THE CHECKLIST — reproduce IN FULL

**The checklist in this paper is byte-for-byte the same as SEGRESS 2023 Table 9**, reproduced above
in full. Verified item by item across all 44 numbered rows and all 9 unnumbered guidance rows. The
only differences are reference-numbering (this paper's `[4]` = the Supplementary Material, `[7]` =
Page et al. PRISMA 2020, `[6]` = the PRISMA 2020 explanation-and-elaboration paper, `[8]` =
PRISMA-S, `[9]` = PRISMA-P, `[2]` = the grey-material paper, `[1]` = Booth et al. on disconfirming
cases, `[5]` = Madeyski & Kitchenham on reproducible research) and one internal cross-reference
phrasing ("See Section 3.3.3 and Section 5.1.3" at item 15). It is not re-tabulated here to avoid
duplication.

### Differences between SEGRESS and PRISMA 2020

Stated explicitly and compactly in this paper's framing text:

> "Please note that, following PRISMA 2020, we have adopted the terms 'Risk of Bias' (RoB) as a
> replacement for the term 'Quality Assessment', and 'Limitations' as a replacement for 'Threats to
> Validity'. Both of these are considered to be more appropriate descriptions to use in the context
> of a secondary study."

> "The most important part of the SEGRESS paper is Table 9, which is reproduced below, and presents
> the structured checklist for reporting software engineering secondary studies."

> "Also, all references in the table are to the Supplementary Material [4], which provides
> explanations of the sections with the aid of examples."

### Caveats, traps and pitfalls

- The per-item explanations and worked examples live **only** in the Supplementary Material
  (`SEGRESS22supplement.pdf`), which is *not* in this corpus. Every `[4, Sec. n.n]` reference in the
  checklist points there. Anyone implementing SEGRESS from the table alone is working without the
  elaboration layer — the same complaint SEGRESS levels at bare PRISMA ("PRISMA 2020 is not simple
  to understand and needs additional explanations and examples").

---

## page_prisma_2021 — The PRISMA 2020 statement: an updated guideline for reporting systematic reviews

(Page, McKenzie, Bossuyt, Boutron, Hoffmann, Mulrow, Shamseer, Tetzlaff, Akl, Brennan, Chou,
Glanville, Grimshaw, Hróbjartsson, Lalu, Li, Loder, Mayo-Wilson, McDonald, McGuinness, Stewart,
Thomas, Tricco, Welch, Whiting & Moher. *BMJ* 2021;372:n71. DOI 10.1136/bmj.n71)

**Type:** reporting standard (the medical/health baseline).

**Role in corpus:** The authoritative source text for the 27 items and 12 abstract items that
SEGRESS renumbers and re-scopes, plus the only source in this batch for the **flow diagram
template** — which SEGRESS defers to and never redraws.

### THE CHECKLIST — reproduce IN FULL

#### Table 1 — the PRISMA 2020 item checklist (27 items, 7 sections)

The published table has a third column, "Location where item is reported", left blank for authors
to complete. That column is part of the instrument and is noted here.

| Item # | Section | Checklist item (verbatim) | Notes/guidance |
|---|---|---|---|
| 1 | Title | "Identify the report as a systematic review." | |
| 2 | Abstract | "See the PRISMA 2020 for Abstracts checklist (table 2)." | The abstract checklist is *inside* PRISMA 2020 — new in 2020. |
| 3 | Introduction — Rationale | "Describe the rationale for the review in the context of existing knowledge." | |
| 4 | Introduction — Objectives | "Provide an explicit statement of the objective(s) or question(s) the review addresses." | |
| 5 | Methods — Eligibility criteria | "Specify the inclusion and exclusion criteria for the review and how studies were grouped for the syntheses." | The grouping clause feeds item 13a. |
| 6 | Methods — Information sources | "Specify all databases, registers, websites, organisations, reference lists and other sources searched or consulted to identify studies. Specify the date when each source was last searched or consulted." | PRISMA-S referenced here in the E&E paper. |
| 7 | Methods — Search strategy | "Present the full search strategies for all databases, registers and websites, including any filters and limits used." | **Changed in 2020**: "all databases … not just at least one database". |
| 8 | Methods — Selection process | "Specify the methods used to decide whether a study met the inclusion criteria of the review, including how many reviewers screened each record and each report retrieved, whether they worked independently, and if applicable, details of automation tools used in the process." | **Changed in 2020** to emphasise reviewer counts/independence/automation. |
| 9 | Methods — Data collection process | "Specify the methods used to collect data from reports, including how many reviewers collected data from each report, whether they worked independently, any processes for obtaining or confirming data from study investigators, and if applicable, details of automation tools used in the process." | |
| 10a | Methods — Data items | "List and define all outcomes for which data were sought. Specify whether all results that were compatible with each outcome domain in each study were sought (e.g. for all measures, time points, analyses), and if not, the methods used to decide which results to collect." | **New sub-item in 2020.** |
| 10b | Methods — Data items | "List and define all other variables for which data were sought (e.g. participant and intervention characteristics, funding sources). Describe any assumptions made about any missing or unclear information." | |
| 11 | Methods — Study risk of bias assessment | "Specify the methods used to assess risk of bias in the included studies, including details of the tool(s) used, how many reviewers assessed each study and whether they worked independently, and if applicable, details of automation tools used in the process." | |
| 12 | Methods — Effect measures | "Specify for each outcome the effect measure(s) (e.g. risk ratio, mean difference) used in the synthesis or presentation of results." | |
| 13a | Methods — Synthesis methods | "Describe the processes used to decide which studies were eligible for each synthesis (e.g. tabulating the study intervention characteristics and comparing against the planned groups for each synthesis (item #5))." | **13a–13f are a 2020 split** of the old single 'Synthesis of results' item. |
| 13b | Methods — Synthesis methods | "Describe any methods required to prepare the data for presentation or synthesis, such as handling of missing summary statistics, or data conversions." | |
| 13c | Methods — Synthesis methods | "Describe any methods used to tabulate or visually display results of individual studies and syntheses." | |
| 13d | Methods — Synthesis methods | "Describe any methods used to synthesise results and provide a rationale for the choice(s). If meta-analysis was performed, describe the model(s), method(s) to identify the presence and extent of statistical heterogeneity, and software package(s) used." | SWiM reporting guideline referenced here in the E&E paper. |
| 13e | Methods — Synthesis methods | "Describe any methods used to explore possible causes of heterogeneity among study results (e.g. subgroup analysis, meta-regression)." | **SEGRESS swaps this with 13f.** |
| 13f | Methods — Synthesis methods | "Describe any sensitivity analyses conducted to assess robustness of the synthesised results." | **SEGRESS swaps this with 13e.** |
| 14 | Methods — Reporting bias assessment | "Describe any methods used to assess risk of bias due to missing results in a synthesis (arising from reporting biases)." | |
| 15 | Methods — Certainty assessment | "Describe any methods used to assess certainty (or confidence) in the body of evidence for an outcome." | **New item in 2020** (paired with item 22). |
| 16a | Results — Study selection | "Describe the results of the search and selection process, from the number of records identified in the search to the number of studies included in the review, ideally using a flow diagram (see fig 1)." | |
| 16b | Results — Study selection | "Cite studies that might appear to meet the inclusion criteria, but which were excluded, and explain why they were excluded." | **New sub-item in 2020.** |
| 17 | Results — Study characteristics | "Cite each included study and present its characteristics." | |
| 18 | Results — Risk of bias in studies | "Present assessments of risk of bias for each included study." | |
| 19 | Results — Results of individual studies | "For all outcomes, present, for each study: (a) summary statistics for each group (where appropriate) and (b) an effect estimate and its precision (e.g. confidence/credible interval), ideally using structured tables or plots." | |
| 20a | Results — Results of syntheses | "For each synthesis, briefly summarise the characteristics and risk of bias among contributing studies." | **20a–20d are a 2020 split.** |
| 20b | Results — Results of syntheses | "Present results of all statistical syntheses conducted. If meta-analysis was done, present for each the summary estimate and its precision (e.g. confidence/credible interval) and measures of statistical heterogeneity. If comparing groups, describe the direction of the effect." | |
| 20c | Results — Results of syntheses | "Present results of all investigations of possible causes of heterogeneity among study results." | **SEGRESS swaps this with 20d.** |
| 20d | Results — Results of syntheses | "Present results of all sensitivity analyses conducted to assess the robustness of the synthesised results." | **SEGRESS swaps this with 20c.** |
| 21 | Results — Reporting biases | "Present assessments of risk of bias due to missing results (arising from reporting biases) for each synthesis assessed." | |
| 22 | Results — Certainty of evidence | "Present assessments of certainty (or confidence) in the body of evidence for each outcome assessed." | **New item in 2020** (paired with item 15). |
| 23a | Discussion | "Provide a general interpretation of the results in the context of other evidence." | |
| 23b | Discussion | "Discuss any limitations of the evidence included in the review." | |
| 23c | Discussion | "Discuss any limitations of the review processes used." | This is the *threats to validity* slot. |
| 23d | Discussion | "Discuss implications of the results for practice, policy, and future research." | |
| 24a | Other information — Registration and protocol | "Provide registration information for the review, including register name and registration number, or state that the review was not registered." | **Moved in 2020** from the start of Methods into a new 'Other information' section. |
| 24b | Other information — Registration and protocol | "Indicate where the review protocol can be accessed, or state that a protocol was not prepared." | |
| 24c | Other information — Registration and protocol | "Describe and explain any amendments to information provided at registration or in the protocol." | **New sub-item in 2020.** |
| 25 | Other information — Support | "Describe sources of financial or non-financial support for the review, and the role of the funders or sponsors in the review." | |
| 26 | Other information — Competing interests | "Declare any competing interests of review authors." | **New item in 2020.** |
| 27 | Other information — Availability of data, code, and other materials | "Report which of the following are publicly available and where they can be found: template data collection forms; data extracted from included studies; data used for all analyses; analytic code; any other materials used in the review." | **New item in 2020.** |

**Count:** 27 items → **42 numbered rows** when sub-items are expanded (10a–b, 13a–f, 16a–b,
20a–d, 23a–d, 24a–c).

#### Table 2 — the PRISMA 2020 for Abstracts checklist (12 items)

Footnote as printed: "*This abstract checklist retains the same items as those included in the
PRISMA for Abstracts statement published in 2013, but has been revised to make the wording
consistent with the PRISMA 2020 statement and includes a new item recommending authors specify the
methods used to present and synthesise results (item #6)."

| Item # | Section | Checklist item (verbatim) | Notes/guidance |
|---|---|---|---|
| 1 | Title | "Identify the report as a systematic review." | |
| 2 | Background — Objectives | "Provide an explicit statement of the main objective(s) or question(s) the review addresses." | |
| 3 | Methods — Eligibility criteria | "Specify the inclusion and exclusion criteria for the review." | |
| 4 | Methods — Information sources | "Specify the information sources (e.g. databases, registers) used to identify studies and the date when each was last searched." | |
| 5 | Methods — Risk of bias | "Specify the methods used to assess risk of bias in the included studies." | |
| 6 | Methods — Synthesis of results | "Specify the methods used to present and synthesise results." | **New item vs the 2013 abstracts statement.** |
| 7 | Results — Included studies | "Give the total number of included studies and participants and summarise relevant characteristics of studies." | |
| 8 | Results — Synthesis of results | "Present results for main outcomes, preferably indicating the number of included studies and participants for each. If meta-analysis was done, report the summary estimate and confidence/credible interval. If comparing groups, indicate the direction of the effect (i.e. which group is favoured)." | |
| 9 | Discussion — Limitations of evidence | "Provide a brief summary of the limitations of the evidence included in the review (e.g. study risk of bias, inconsistency and imprecision)." | |
| 10 | Discussion — Interpretation | "Provide a general interpretation of the results and important implications." | |
| 11 | Other — Funding | "Specify the primary source of funding for the review." | |
| 12 | Other — Registration | "Provide the register name and registration number." | |

**Count: 12 abstract items.** SEGRESS item 2 points at this table rather than restating it, but
prescribes its own abstract *sections*: "Background (emphasizing the importance of this research),
Objective, Methods, Results, Limitations (optional), Conclusion."

#### Box 2 — "Noteworthy changes to the PRISMA 2009 statement" (verbatim, all 12 bullets)

- "Inclusion of the abstract reporting checklist within PRISMA 2020 (see item #2 and table 2)."
- "Movement of the 'Protocol and registration' item from the start of the Methods section of the
  checklist to a new Other section, with addition of a sub-item recommending authors describe
  amendments to information provided at registration or in the protocol (see item #24a-24c)."
- "Modification of the 'Search' item to recommend authors present full search strategies for all
  databases, registers and websites searched, not just at least one database (see item #7)."
- "Modification of the 'Study selection' item in the Methods section to emphasise the reporting of
  how many reviewers screened each record and each report retrieved, whether they worked
  independently, and if applicable, details of automation tools used in the process (see item #8)."
- "Addition of a sub-item to the 'Data items' item recommending authors report how outcomes were
  defined, which results were sought, and methods for selecting a subset of results from included
  studies (see item #10a)."
- "Splitting of the 'Synthesis of results' item in the Methods section into six sub-items
  recommending authors describe: the processes used to decide which studies were eligible for each
  synthesis; any methods required to prepare the data for synthesis; any methods used to tabulate or
  visually display results of individual studies and syntheses; any methods used to synthesise
  results; any methods used to explore possible causes of heterogeneity among study results (such as
  subgroup analysis, meta-regression); and any sensitivity analyses used to assess robustness of the
  synthesised results (see item #13a-13f)."
- "Addition of a sub-item to the 'Study selection' item in the Results section recommending authors
  cite studies that might appear to meet the inclusion criteria, but which were excluded, and
  explain why they were excluded (see item #16b)."
- "Splitting of the 'Synthesis of results' item in the Results section into four sub-items
  recommending authors: briefly summarise the characteristics and risk of bias among studies
  contributing to the synthesis; present results of all statistical syntheses conducted; present
  results of any investigations of possible causes of heterogeneity among study results; and present
  results of any sensitivity analyses (see item #20a-20d)."
- "Addition of new items recommending authors report methods for and results of an assessment of
  certainty (or confidence) in the body of evidence for an outcome (see items #15 and #22)."
- "Addition of a new item recommending authors declare any competing interests (see item #26)."
- "Addition of a new item recommending authors indicate whether data, analytic code and other
  materials used in the review are publicly available and if so, where they can be found (see item
  #27)."

#### Box 1 — Glossary of terms (verbatim, all 8 definitions)

These definitions govern how the flow-diagram counts must be interpreted, so they are load-bearing.

- **Systematic review** — "A review that uses explicit, systematic methods to collate and synthesise
  findings of studies that address a clearly formulated question"
- **Statistical synthesis** — "The combination of quantitative results of two or more studies. This
  encompasses meta-analysis of effect estimates (described below) and other methods, such as
  combining P values, calculating the range and distribution of observed effects, and vote counting
  based on the direction of effect"
- **Meta-analysis of effect estimates** — "A statistical technique used to synthesise results when
  study effect estimates and their variances are available, yielding a quantitative summary of
  results"
- **Outcome** — "An event or measurement collected for participants in a study (such as quality of
  life, mortality)"
- **Result** — "The combination of a point estimate (such as a mean difference, risk ratio, or
  proportion) and a measure of its precision (such as a confidence/credible interval) for a
  particular outcome"
- **Report** — "A document (paper or electronic) supplying information about a particular study. It
  could be a journal article, preprint, conference abstract, study register entry, clinical study
  report, dissertation, unpublished manuscript, government report, or any other document providing
  relevant information"
- **Record** — "The title or abstract (or both) of a report indexed in a database or website (such
  as a title or abstract for an article indexed in Medline). Records that refer to the same report
  (such as the same journal article) are 'duplicates'; however, records that refer to reports that
  are merely similar (such as a similar abstract submitted to two different conferences) should be
  considered unique."
- **Study** — "An investigation, such as a clinical trial, that includes a defined group of
  participants and one or more interventions and outcomes. A 'study' might have multiple reports.
  For example, reports could include the protocol, statistical analysis plan, baseline
  characteristics, results for the primary outcome, results for harms, results for secondary
  outcomes, and results for additional mediator and moderator analyses"

### The PRISMA flow diagram

Figure 1: "PRISMA 2020 flow diagram template for systematic reviews. The new design is adapted from
flow diagrams proposed by Boers, Mayo-Wilson et al. and Stovold et al. **The boxes in grey should
only be completed if applicable; otherwise they should be removed from the flow diagram.** Note
that a 'report' could be a journal article, preprint, conference abstract, study register entry,
clinical study report, dissertation, unpublished manuscript, government report or any other
document providing relevant information."

The single template is **three parallel columns** that converge on one final pair of boxes. It
serves both the original-review case and the updated-review case: for an original review the
left-hand column is deleted; for an updated review it is retained.

**Column A — "Previous studies"** (grey; only for updated/living reviews)
- Box A1: `Studies included in previous version of review (n= )`
- Box A2: `Reports of studies included in previous version of review (n= )`
- Arrow: A2 → the bottom "Total studies included in review" box. No screening stages.

**Column B — "Identification of new studies via databases and registers"** (the classical column)

| Stage | Box | Counts required | Side-arrow (exclusions) |
|---|---|---|---|
| Identification | `Records identified from*:` | `Databases (n= )`, `Registers (n= )` — reported **separately**, not as one total | → `Records removed before screening:` with **three separate counts**: `Duplicate records removed (n= )`, `Records marked as ineligible by automation tools (n= )`, `Records removed for other reasons (n= )` |
| Screening | `Records screened (n= )` | one count | → `Records excluded† (n= )` |
| Retrieval | `Reports sought for retrieval (n= )` | one count | → `Reports not retrieved (n= )` |
| Eligibility | `Reports assessed for eligibility (n= )` | one count | → `Reports excluded:` broken out **by reason**: `Reason 1 (n= )`, `Reason 2 (n= )`, `Reason 3 (n= ) etc` |
| Included | `New studies included in review (n= )` **and** `Reports of new included studies (n= )` | **two counts** — studies and reports are distinct | — |

Arrows run top-to-bottom through the five stages; each exclusion box hangs off to the right of its
stage box.

**Column C — "Identification of new studies via other methods"** (websites, organisations, citation
searching)

| Stage | Box | Counts required | Side-arrow (exclusions) |
|---|---|---|---|
| Identification | `Records identified from:` | `Websites (n= )`, `Organisations (n= )`, `Citation searching (n= ) etc` — **broken out by source type** | — **no "records removed before screening" box** |
| Retrieval | `Reports sought for retrieval (n= )` | one count | → `Reports not retrieved (n= )` |
| Eligibility | `Reports assessed for eligibility (n= )` | one count | → `Reports excluded:` by reason: `Reason 1 (n= )`, `Reason 2 (n= )`, `Reason 3 (n= ) etc` |

**Difference between the "databases and registers" version and the "other methods" version — this
is the key structural asymmetry:**

| Feature | Databases and registers (col. B) | Other methods (col. C) |
|---|---|---|
| Source breakdown | Databases / Registers | Websites / Organisations / Citation searching / etc |
| "Records removed before screening" box (duplicates, automation-ineligible, other) | **present** | **absent** |
| "Records screened → Records excluded" stage | **present** | **absent** — there is no record-screening stage, because items found by citation-chasing or site-browsing arrive as reports, not as indexed records |
| "Reports sought for retrieval → Reports not retrieved" | present | present |
| "Reports assessed for eligibility → Reports excluded by reason" | present | present |
| Own "included" box | `New studies included in review` + `Reports of new included studies` | none — column C feeds directly into the shared included box |

**Convergence.** All three columns converge on the final pair:
- `Total studies included in review (n= )`
- `Reports of total included studies (n= )`

**Footnotes (both are instructions, not decoration):**
- `*` — "Consider, if feasible to do so, reporting the number of records identified from each
  database or register searched (rather than the total number across all databases/registers)"
- `†` — "If automation tools were used, indicate how many records were excluded by a human and how
  many were excluded by automation tools"

**Numbers that must be reported, exhaustively** (an original review with no other-methods searching
reports the minimum set; a full updated review with both search routes reports all of them):
1. Studies included in previous version of review
2. Reports of studies included in previous version of review
3. Records identified from databases
4. Records identified from registers
5. Duplicate records removed
6. Records marked as ineligible by automation tools
7. Records removed for other reasons
8. Records screened
9. Records excluded (split human vs automation where automation was used)
10. Reports sought for retrieval
11. Reports not retrieved
12. Reports assessed for eligibility
13. Reports excluded, **one count per exclusion reason**
14. New studies included in review
15. Reports of new included studies
16. Records identified from websites
17. Records identified from organisations
18. Records identified from citation searching (and any further "other method")
19. Reports sought for retrieval (other methods)
20. Reports not retrieved (other methods)
21. Reports assessed for eligibility (other methods)
22. Reports excluded (other methods), **one count per reason**
23. Total studies included in review
24. Reports of total included studies

Note the **studies-vs-reports** distinction runs through the whole diagram: counts above the
retrieval stage are *records*, counts from retrieval onward are *reports*, and the terminal boxes
report *studies* and *reports* separately (see Box 1 glossary).

### Differences between SEGRESS and PRISMA 2020

See the table under `kitchenham_segress_2023`. From PRISMA's own side, three statements bound what
SEGRESS was obliged to fix:

> "The PRISMA 2020 statement has been designed primarily for systematic reviews of studies that
> evaluate the effects of health interventions, irrespective of the design of the included studies.
> However, the checklist items are applicable to reports of systematic reviews evaluating other
> interventions (such as social or educational interventions), and many items are applicable to
> systematic reviews with objectives other than evaluating interventions (such as evaluating
> aetiology, prevalence, or prognosis)."

> "The PRISMA 2020 items are relevant for mixed-methods systematic reviews (which include
> quantitative and qualitative studies), but reporting guidelines addressing the presentation and
> synthesis of qualitative data should also be consulted."

> "PRISMA 2020 can be used for original systematic reviews, updated systematic reviews, or
> continually updated ('living') systematic reviews. However, for updated and living systematic
> reviews, there may be some additional considerations that need to be addressed."

### Guidance per study type

- Scoping reviews are handled by an **extension** (PRISMA-ScR), not by PRISMA 2020 itself: "for
  these types of reviews we recommend authors report their review in accordance with the
  recommendations in PRISMA 2020 along with the guidance specific to the extension." The named
  extensions are: network meta-analyses, meta-analyses of individual participant data, systematic
  reviews of harms, systematic reviews of diagnostic test accuracy studies, and scoping reviews.
- Protocols are out of scope: "PRISMA 2020 is not intended to inform the reporting of systematic
  review protocols, for which a separate statement is available (PRISMA for Protocols (PRISMA-P)
  2015 statement)."
- Cross-referenced sub-guidelines: **PRISMA-Search** in items 6 and 7; **SWiM (Synthesis without
  meta-analysis)** in item 13d.
- Reviews with no synthesis are in scope: "PRISMA 2020 is intended for use in systematic reviews
  that include synthesis (such as pairwise meta-analysis or other statistical synthesis methods) or
  do not include synthesis (for example, because only one eligible study is identified)."

### Report evaluation procedures

**PRISMA 2020 explicitly forbids its own use as a quality-assessment instrument:**

> "PRISMA 2020 is not intended to guide systematic review conduct, for which comprehensive
> resources are available. However, familiarity with PRISMA 2020 is useful when planning and
> conducting systematic reviews to ensure that all recommended information is captured. **PRISMA
> 2020 should not be used to assess the conduct or methodological quality of systematic reviews;
> other tools exist for this purpose.**"

Supporting instruments and mechanisms that *are* offered:
- **Fillable checklist templates** on `http://www.prisma-statement.org/`, downloadable and
  completable, plus editable flow-diagram templates.
- **A web application** for completing the checklist "via a user-friendly interface" (adapted from
  the Transparency Checklist app), at `https://prisma.shinyapps.io/checklist/`; "The completed
  checklist can be exported to Word or PDF."
- **The "Location where item is reported" column** in Table 1 — the mechanism by which a journal
  makes an author point at where each item is satisfied.
- **The expanded checklist** — "an abridged version of the elements presented in the explanation and
  elaboration paper"; the E&E paper (BMJ 2021;372:n160) "explain[s] why reporting of each item is
  recommended and present[s] bullet points that detail the reporting recommendations (which we refer
  to as elements). The bullet-point structure is new to PRISMA 2020 and has been adopted to
  facilitate implementation of the guidance."
- Roles named for enforcement: "journals requiring authors to indicate where in their manuscript
  they have adhered to each reporting item"; "peer reviewers evaluating adherence to reporting
  guidelines"; "authors using online writing tools that prompt complete reporting at the writing
  stage"; "educators introducing reporting guidelines into graduate curricula".

### Caveats, traps and pitfalls

Verbatim:

- **PRISMA 2009 must not be used any more** — "The PRISMA 2020 statement (including the checklists,
  explanation and elaboration, and flow diagram) replaces the PRISMA 2009 statement, which should no
  longer be used."
- **Consult it before writing, not after** — "We recommend authors refer to PRISMA 2020 early in the
  writing process, because prospective consideration of the items may help to ensure that all the
  items are addressed."
- **Location is not prescriptive** — "although PRISMA 2020 provides a template for where information
  might be located, the suggested location should not be seen as prescriptive; the guiding principle
  is to ensure the information is reported."
- **Length management** — "Journals and publishers might impose word and section limits, and limits
  on the number of tables and figures allowed in the main report. In such cases, if the relevant
  information for some items already appears in a publicly accessible review protocol, referring to
  the protocol may suffice. Alternatively, placing detailed descriptions of the methods used or
  additional results (such as for less critical outcomes) in supplementary files is recommended.
  Ideally, supplementary files should be deposited to a general-purpose or institutional open-access
  repository that provides free and permanent access to the material (such as Open Science
  Framework, Dryad, figshare). A reference or link to the additional information should be included
  in the main report."
- **We do not know what makes checklists stick** — "of 31 interventions proposed to increase
  adherence to reporting guidelines, the effects of only 11 have been evaluated, mostly in
  observational studies at high risk of bias due to confounding. It is therefore unclear which
  strategies should be used."
- **Multi-pronged enforcement may be needed** — "Multi-pronged interventions, where more than one of
  these strategies are combined, may be more effective (such as completion of checklists coupled
  with editorial checks)."
- **The items may be read inconsistently** — "it would also be valuable to conduct think-aloud
  studies to understand how systematic reviewers interpret the items, and reliability studies to
  identify items where there is varied interpretation of the items."
- **Records that look like duplicates may not be** — "records that refer to reports that are merely
  similar (such as a similar abstract submitted to two different conferences) should be considered
  unique." (A deduplication trap directly relevant to tooling.)
- **A study is not a report** — "A 'study' might have multiple reports." (Counting reports as
  studies inflates the flow diagram.)

### Empirical findings worth citing

- PRISMA 2009 "citation in over **60 000 reports** (Scopus, August 2020), endorsement from almost
  **200 journals** and systematic review organisations, and adoption in various disciplines."
- "Evidence from observational studies suggests that use of the PRISMA 2009 statement is associated
  with more complete reporting of systematic reviews, although **more could be done to improve
  adherence to the guideline**."
- PRISMA 2020 development inputs: **60 documents** providing reporting guidance reviewed; survey of
  systematic review methodologists and journal editors — **110 of 220 invited responded**; a
  **21-member, two-day, in-person** development meeting (September 2018, Edinburgh); **an initial
  draft and five revisions** circulated across 2019–2020; **22** reviewers invited for layout/
  terminology feedback, **15** responded.
- Adherence interventions: **31 proposed**, **only 11 evaluated**, "mostly in observational studies
  at high risk of bias due to confounding".
- Motivating changes since 2009 cited as evidence of methodological drift: natural language
  processing and machine learning for identifying evidence; methods for synthesis when meta-analysis
  is not possible or appropriate; new risk-of-bias tools; new tools to appraise the conduct of
  systematic reviews; "the shift from assessing 'quality' to assessing 'certainty' in the body of
  evidence".

---

## williams_towards_2017 — Toward the use of blog articles as a source of evidence for software engineering research

(Ashley Williams & Austen Rainer, *EASE'17*, Karlskrona, Sweden. DOI 10.1145/3084226.3084268)

**Type:** empirical study (pilot exploratory study + pilot systematic mapping study).

**Role in corpus:** The origin point of the Williams/Rainer credibility-criteria line — it derives,
from a pilot SMS of the credibility literature, the **11 candidate criteria for blog-article
content credibility** and then argues down to the four that are both valued by researchers and
automatable. It is the only paper in this batch that treats *criteria for evaluating a source* as
something to be discovered empirically rather than prescribed.

### THE CHECKLIST — reproduce IN FULL

This paper contains no reporting checklist. It contains three evaluation instruments, reproduced
in full.

#### Wohlin's five criteria for good research evidence (verbatim, as quoted by Williams & Rainer)

| # | Criterion (verbatim) |
|---|---|
| 1 | "Quality of evidence (how reliable is the evidence?)" |
| 2 | "Relevance of evidence" |
| 3 | "Aging of evidence (evidence that has aged too much may no longer be relevant)" |
| 4 | "Vested interest (is the evidence unbiased?)" |
| 5 | "Strength of evidence" |

#### Fenton, Pfleeger and Glass's five questions about any claim in SE research (verbatim)

| # | Question (verbatim) |
|---|---|
| 1 | "Is the claim based on empirical evaluation and data?" |
| 2 | "Was the empirical study designed correctly?" |
| 3 | "Is the claim based on a toy or real situation?" |
| 4 | "Were the measurements used appropriate to the goals of the empirical study?" |
| 5 | "Was the empirical study run for a long enough time?" |

> "Together, these two sources provide an indication of researchers' requirements of evidence and
> the inferences from evidence."

#### Table 4 — the 11 most popular blog-content credibility criteria found by the pilot SMS (n=7 positive results)

| # | Criterion | Definition (verbatim) |
|---|---|---|
| 1 | Authentic | "Article is of undisputed origin." |
| 2 | Informative | "Article provides useful or interesting information." |
| 3 | Trusted | "Content is unbiased, fair and consistent." |
| 4 | Evidence based | "Content is supported by evidence." |
| 5 | Focused | "Article pays attention to a particular topic." |
| 6 | Accurate | "Content is correct." |
| 7 | Timely | "Article was published recently or is relevant to the reader." |
| 8 | Popular | "Article is liked by others (e.g. comments, likes, page reads)." |
| 9 | Intrinsic Quality | "Article is relevant to the core topics of the overall blog." |
| 10 | Comprehensive | "Article has all necessary parts required to give a full picture of the topic it addresses." |
| 11 | Quality of writing | "Article is well written, grammatically correct etc." |

#### Table 5 — the four chosen criteria and their operationalisation

| Criterion | Measurement (verbatim) |
|---|---|
| Rigour | "Argumentation mining can be used as this allows us to evaluate the arguments and reasoning being presented by the author and thus, the strength of the message." |
| Relevance | "Some form of topic detection needs to take place. This allows us to ensure that the article being analysed is relevant to the researchers needs." |
| Evidence based | "Where researchers use empirical evidence to support their views, practitioners tend to form opinions based on personal experience. Experience mining allows us to evaluate the references to professional experience, and how those references relate to reasoning." |
| Quality of writing | "An automatic assessment of writing quality (e.g. punctuation, spelling, grammar) needs to be carried out. This will serve to aid researchers in extracting the high quality articles from the vast quantity available." |

Conclusion drawn: "we decide that blog articles need to be **rigorous, relevant, well written and
experience based** for them to be considered credible to researchers."

#### Table 3 — the search criteria used for the pilot SMS (a reusable protocol fragment)

| Search Criteria (Google Scholar) — verbatim |
|---|
| "Timely (Published between 2007 and 2017. This is to ensure that we are looking at criteria that is currently used)" |
| "Content includes one of the following sources; blog, blogger, news, twitter, web, website, content, media, social media" |
| "Title includes one of the following verbs; assessing, measuring, evaluating, assess, measure, evaluate" |
| "Title includes one of the following keywords; credibility, credible, truthfulness, truthful, truth, believability, believable, belief" |
| "Has been published in a peer reviewed journal, conference, book or thesis" |

### Report evaluation procedures

The four-criteria instrument above **is** the evaluation procedure — it is an instrument for
appraising a *source* (a grey-literature item) rather than a *report of a review*. It sits
alongside SEGRESS's risk-of-bias layer: SEGRESS item 11 asks for "details of the tool(s) used";
this is a candidate tool for reviews that admit blog articles.

Rejection rationale for the seven discarded criteria, verbatim:
> "In developing an automated method for assessing the criteria of blog content, some of the
> criteria presented in Table 4 become difficult to use. Assessing the authenticity, informativeness,
> trustworthiness, accuracy and comprehensiveness becomes difficult without prior knowledge of what
> should be included in each article. Excluding these leaves us with four main criteria; rigour
> (strength of message), relevance (focused, timely, intrinsic quality), experience based and
> quality of writing."

And for popularity specifically:
> "Although popularity can be a good indicator in certain contexts, we omit it from our research as
> unpopular/unread articles may still provide valuable evidence to researcher and popular articles
> may be found to hold no value."

### Caveats, traps and pitfalls

Verbatim:

- **Credibility is context-dependent and audience-dependent** — "Kang notes that credibility is
  subjective and credibility measurements change given different context. For example, credibility
  measures for gaming blogs will be different to political blogs. This is also true of the different
  user groups reading the blog article."
- **Researchers are not the population these criteria were derived from** — "The profile of the blog
  users that participated in Kangs focus group may have different requirements to that of a
  researcher, the focus of our research. Therefore, the same study performed on a group of
  researchers may yield different measurements being identified."
- **Preferred-source bias** — "Carter and Greenberg found that people judge their preferred news
  source as the most credible. Hence, a group of regular blog users, such as those used in Kang's
  study, would be expected to find blogs a credible source."
- **The literature's criteria miss what researchers actually need** — "these criteria may not
  necessarily be the correct criteria for assessing credibility of blog article content in research
  (i.e what researchers care about when looking for evidence). For example, missing from this list
  that is of great value to researchers is the rigour of the message."
- **Influence ≠ credibility** — "The features used in these influential blogger studies indicate that
  there is a difference between an influential blogger and a blogger who reports competent and
  credible (rigorous and evidence based) views."
- **The bootstrapping problem** — "there is a boot-strapping problem with automating the process:
  building an automated process requires that we have some sense of what the 'right content' is in a
  relatively large dataset of candidate articles."
- **Search-engine relevance is not reproducible** — "reproducability of result generation becomes
  difficult when search engine ranks are affected by features such as previous search history and
  search engine optimasation (SEO)."
- **Search-engine relevance is not the researcher's relevance** — "the topic rank is then being
  determined by the search engine, which may not necessarily align with the requirements of
  researchers."
- **Simplistic ranking** (self-criticism of phase one) — "Our methods of ranking were simplistic and
  the weightings used for each criteria are subjective. Also, the methods used for extracting the
  criteria were not robust enough and effected subsequent results. For example, although named
  entities give some indication of topic, using them as the sole indication method meant that some
  articles would rank consistently high based on the frequency of named entities alone."
- **Topic models need a static corpus and a per-topic ontology** — "This current method requires a
  static dataset, whereas real world blog analysis is ever changing as new articles are published.
  Also, this method requires an ontology of seed words for every topic that researchers may want to
  use."
- **Grey-literature data is messy** — "the difficulty that can arise from messy, unstructured data
  such as blogs (i.e. repeated articles, informal language, parsing poor grammar and punctuation,
  ambiguity etc)."
- **Transparency of the selection process is itself a requirement** — "any analysis of blog articles
  for researchers needs to be able to present the results and process to the reader. This provides
  transparency to the researcher for the purpose of reproducibility and testing."

### Empirical findings worth citing

- Pilot SMS: **833 potential papers** found; **763** after de-duplication; **143** after a first pass
  on titles/abstracts to eliminate papers not discussing credibility of online data sources; **38**
  analysed at the time of writing, of which **7 positive results** yielded the 11 criteria.
- Pilot argument-detection: **62 indicators** (1st pass) → precision **89.6%**, recall **31.3%**,
  F1 **46.4%**; **85 indicators** (2nd pass) → precision **91.1%**, recall **38.7%**, F1 **54.3%**.
- Inter-rater agreement on argument classification in blog articles: Cohen's κ = **0.397**, "fair"
  (Landis and Koch). Suggested cause: "arguments are difficult to classify when they have been
  stripped of the context of their surrounding sentences."
- Pagano and Maalej: project-specific blog articles "typically contain **fourteen times** the word
  count of version control commit comments."
- Corpus scale: pilot analysis scaled to "approximately **36,000 articles**" from a single
  practitioner's blog.
- Searches for literature on influential bloggers (Table 1): `<influential bloggers>` since 2012 =
  **12,100**; `<"influential bloggers">` since 2012 = **784**; with "software engineering research"
  = **173**; in title only = **12**; all six `allintitle:` variants = **0**. "we can find no study
  that analyses influential software engineering bloggers".

---

## williams_using_2018 — Using reasoning markers to select the more rigorous software practitioners' online content when searching for grey literature

(Ashley Williams, *EASE'18*, Christchurch, New Zealand. DOI 10.1145/3210459.3210464)

**Type:** empirical study (instrument construction + evaluation + partial validation + two
demonstrations).

**Role in corpus:** Supplies the **86-item reasoning-marker instrument** in full — the only
operational, reusable artefact in this batch for *executing* a rigour filter over grey literature,
and the only paper here that shows markers being folded into an actual search string.

### THE CHECKLIST — reproduce IN FULL

#### Table 13 — the final set of 86 reasoning markers (verbatim, all 86)

The paper prints them in six columns of 15/15/15/15/15/11. Read column by column they are in
alphabetical order. Reproduced here in that order, all 86.

**The authoritative flat sequence, as printed column by column:**

1. `a consequence, accordingly, admit that, although, another point, as a result, as can be seen, as indicated by, as opposed to, assume, assumed, assuming, assumption, because, belief that` (15)
2. `believe that, but, can derive, conclude, conclusion, consequently, contrary, deduce, deduced, deduces, demonstrate, demonstrates, due to, entails that, ergo` (15)
3. `first of all, firstly, follow, follows, for example, for instance, given that, has shown, hence, however, i would contend that, implied, implies, Imply, in actual fact` (15)
4. `in fact, in my opinion, indicate, indicates, infer, inference, inferences, inferencing, inferred, infers, it is always said that, it is believed that, it is clear, it is proven, may be derived` (15)
5. `on the grounds, on these grounds, on those grounds, otherwise, prove, proved, proves, reason, reasons, secondly, showed that, since, suppose, supposed, supposedly` (15)
6. `supposition, that is exactly why, that show, the fact is, the fact that, therefore, think that, though, thus, yet, you could argue` (11)

Total: 15 + 15 + 15 + 15 + 15 + 11 = **86 markers**. Note "first of all" and "firstly" open
column 3 (both are in the set; "first of all" is one of the ten markers used in the live search
string below). `Imply` is capitalised as printed.

#### Table 1 — Cartaino's six guidelines for high-quality Stack Overflow submissions, mapped to criteria

| # | Guideline (verbatim) | Criteria |
|---|---|---|
| 1 | "Great subjective questions invite explanations." | Rigor |
| 2 | "Great subjective questions invite the sharing of actual experiences." | Experience |
| 3 | "Great subjective questions have a constructive, fair and impartial tone to encourage learning." | Quality of writing |
| 4 | "Great subjective questions invite the sharing of experience over opinion, what you've done rather than what you think." | Experience |
| 5 | "Great subjective questions insist on supporting material e.g. references and facts." | Rigor |
| 6 | "Great subjective questions are about something other than 'social fun'." | Relevnace *(as printed — "Relevance")* |

#### Table 6 — the reasoning and experience markers used in the live Google search

| Reasoning markers (10) | Experience markers (9) |
|---|---|
| but | i |
| because | me |
| for example | we |
| due to | us |
| first of all | my |
| however | experience |
| as a result | experiences |
| since | experienced |
| reason | our |
| therefore | |

> "The reasoning markers have been chosen due to them having the highest precision when ran over
> the persuasive essays corpus. The chosen experience markers are arbitrary, and have been included
> to help in the evaluation of the reasoning markers. The development of a evaluated list of
> experience markers is left for future research."

#### Table 7 — the three query strings (reusable verbatim)

| # | Logic | Query string (verbatim) |
|---|---|---|
| 1 | T+R+E | `"software" AND "testing" AND ("but" OR "because" OR "for example" OR "due to" OR "first of all" OR "however" OR "as a result" OR "since" OR "reason" OR "therefore") AND ("i" OR "me" OR "we" OR "us" OR "my" OR "experience" OR "experiences" OR "experienced" OR "our")` |
| 2 | (T+R)+!E | `"software" AND "testing" AND ("but" OR "because" OR "for example" OR "due to" OR "first of all" OR "however" OR "as a result" OR "since" OR "reason" OR "therefore")) -"i" -"me" -"we" -"us" -"my" -"experience" -"experiences" -"experienced" -"our"` |
| 3 | T+!(R+E) | `"software" AND "testing" -"but" -"because" -"for example" -"due to" -"first of all" -"however" -"as a result" -"since" -"reason" -"therefore" -"i" -"me" -"we" -"us" -"my" -"experience" -"experiences" -"experienced" -"our"` |

#### Table 3 — provenance of the initial candidate marker list (333 markers)

| Source | # Indicators |
|---|---|
| Taboada, M | 32 |
| Knott, A, and Dale, R | 222 |
| Govier, T | 31 |
| Fisher, A | 34 |
| Eemeren et. al. | 17 |
| Harrell, M | 8 |
| Gupta, S | 26 |
| Halpern, D | 34 |
| Other (grey literature) | 83 |

Inclusion criteria for a source, verbatim: "To be included in the candidate list, the paper needed
to have been published, and include a discussion on argument identification in discourse. It also
needed to include a set of markers that was greater than five."

#### Table 9 — the URL classification scheme (a reusable coding frame for grey-literature triage)

| Category | Explanation (verbatim) |
|---|---|
| Online articles (news, blogs etc) | "Page contains an opinion article about a given topic. (Although this papers focus is on blog articles, we use a generic 'online articles' category as it is not always clear whether a site is a blog, or a news site)." |
| E-commerce, service providers, tools & software | "Page promotes the buying of, or downloading of a tool or service. This may include some whitepapers, download pages of free software, and certain articles that have been written by a company to promote their own product/services." |
| Education, academic or online courses/certifications | "Any page that comes from an academic institute (e.g. '.edu' or '.ac.uk' domains) or promotes/provides information on a online course/industry certification." |
| Research | "Research that has been published in a peer reviewed conference/journal." |
| Event advertisements | "Pages which advertise an event (e.g. developer meetups, academic conferences etc)." |
| Government sites | "Any site with a .gov or .mil (United States Department of Defense and its affiliations) domain." |
| Seed pages (i.e. link to many articles) | "A page within a site that contains no content itself, but links to multiple other pages (e.g. the home page of a blog, a directory of businesses etc.)." |
| Discussion/Q&A sites | "Pages where a user provides a topic or question, and then the main bulk of the content is a series of comments around that topic/question" |
| Wiki articles | "Page provides facts and definitions about a given topic. Unlike 'online articles,' wiki articles do not convey the opinions of the author." |
| Job advertisements | "Pages where the main content is to publish one or many jobs" |
| Broken links | "Pages that provide no content to the browser (e.g. 500/404 response)" |
| Other/un-catergorised | "Anything that does not fall into any other category in the list" |
| Review sites | "Pages that contain a review of a product, technology or service; and come from a site that is dedicated to reviews (e.g. trip advisor)." |
| Code, repositories, documentation & bug reports | "Pages that contain only code, documentation about a specific piece of softtware, or bug reports for a specific piece of software." |

### Report evaluation procedures

- The instrument is a **rigour proxy**: "We analyse rigour using the presence of reasoning sentences
  i.e. sentences that contain one or more reasoning marker."
- **Two applications demonstrated**: (a) markers embedded in a search-engine query string, so that
  the retrieval step itself filters for rigour; (b) markers counted across an already-collected
  corpus and normalised by word count, so articles can be **ranked** by `# indicators / word count`.
- **Adams et al.'s three reasons to include grey literature**, rephrased by Williams for SE
  (verbatim):
  1. "Including grey literature can reduce publication bias, as studies with null findings are less
     likely to be published in peer-reviewed software engineering journals and conferences."
  2. "Grey literature can provide useful contextual information on how, why, and for whom software
     engineering practices and technologies are effective."
  3. "Syntheses of grey literature can help software engineering researchers and practitioners
     understand what solutions exist for a particular software engineering problem, the full range of
     evaluations (if any) that have been conducted, and where further development and evaluation is
     needed."

### Caveats, traps and pitfalls

Verbatim:

- **Classification-by-example is not a criterion** — "Neither of these classifications are based on
  definitions as criteria, but are instead based on example only. For example, both papers classify
  emails as having the lowest credibility rating but this may not be true for all emails."
- **We believe these classifications by example are not helpful** — "In the previous section, we have
  demonstrated that even within a single practitioners blog, articles contain varying levels of
  quality and credibility. Our research instead presents a novel approach that looks towards
  classifying grey literature by criteria that are meaningful to researchers."
- **Markers alone are naive** — "Using these markers on their own for identifying reasoning sentences
  within a body of text is a naive approach and not robust enough."
- **Non-systematic instrument construction** — "collating the results from the literature was not
  done systematically, and some sources came from grey literature and not peer reviewed work.
  Therefore, we can not be confident that we have generated an exhaustive initial list. Also, the
  majority of markers in the initial list (222 markers) came from one of the sources. Therefore, the
  validity of our initial list hangs on the validity of that one source."
- **Single-corpus evaluation** — "the list was only evaluated using one dataset of persuasive essays.
  This dataset contains multiple authors but the essays are all of similar structure and topic.
  Therefore, the final list of indicators may perform differently against a different dataset and in
  a different context."
- **Overfitting risk** — "the analysis of false-negatives that was carried out to adjust the list of
  markers and report the results of the 2nd pass may introduce some overfitting. To ensure that this
  is not the case, the list of results need to be validated over a different corpus."
- **Context-stripping kills agreement** — "it is difficult to classify a sentence when it has been
  stripped of its context. This can be countered by validating at a higher level of abstraction such
  as the paragraph, or article level."
- **Boilerplate contaminates counts** — "Every page on Joel's website contains a side bar that
  contains information about him and the companies that he is involved in. This sidebar contains 324
  words and two reasoning markers ('since' and 'as a result'). This explains why the majority of
  results in our bottom 1% still have two indicators."
- **Seed pages pollute rankings** — "there are three pages in Table 11 that are seed pages containing
  multiple articles… When combined, these articles rank higher then their individual parts… These
  pages should be excluded from the analysis as they do not contain a single article."
- **Search engines do not parse PDFs** — "Search sets 2 and 3 contain a lot more PDF files than
  search set 1, some of which contain markers that our query attempts to negate. This could be
  because Google does not parse the content of PDF files when generating its' topic model, relying
  only on meta-data."
- **Foreign-language pages leak through** — "The page may contain both reasoning and experience, but
  Google can only parse based on the English key words in the meta data."
- **API word limits constrain the instrument** — "In using Google however, we are limited by the
  total number of words that we can use in each search string (maximum 32 words). We therefore limit
  our search strings to 10 reasoning markers and 9 experience markers."
- **Zipf's law** — "From our final set of markers, 'but' and 'because' both appear in the list of 100
  most common English words. This is not necessarily a limitation of the study as commonality does
  not prevent a word from being a good reasoning marker."
- **No annotated corpus exists for this task** — "as far as we are aware, there is currently no
  corpus available that provides annotated reasoning and evidence together. There is also no
  annotated corpus of reasoning or experience given in blogs in a software engineering context. This
  makes verifying and extending our work difficult."
- **Rigour ≠ influence** — "Relevant and rigourous blog articles are not the same as influential blog
  articles. A widely read (influential) blog article is not necessarily a rigourous article."
- **Reasoning alone is insufficient** — "Reasoning alone does not determine whether the article is of
  high quality to researchers."
- **Stemming would break search-engine use** — "Normal NLP practice would be to stem these markers,
  but we want our list to be able to be used in search engines which do not recognise stemmed words."

### Empirical findings worth citing

- Marker construction: **333 unique candidate markers** from 9 sources → **62 explicit markers**
  after review → **86** after false-negative analysis (100 false negatives inspected → 85 new
  candidates → 24 added).
- Evaluation corpus: Stab & Gurevych's 90 persuasive essays — **1294 reasoning sentences, 235
  non-reasoning sentences** (unbalanced).

| | 1st Pass | 2nd Pass |
|---|---|---|
| Predicted reasoning sentences | 452 | 550 |
| Predicted Non-reasoning sentences | 1077 | 979 |
| True Positives | 405 | 501 |
| True Negatives | 188 | 186 |
| False Positives | 47 | 49 |
| False Negatives | 889 | 793 |
| **Precision** | **0.896** | **0.911** |
| **Recall** | **0.313** | **0.387** |
| True Negative Rate | 0.388 | 0.449 |
| **F1 Score** | **0.464** | **0.543** |

- Reference point: Stab & Gurevych report "a macro F1 score of **0.726** using supervised
  classification to detect argument sentences" — but "our results cannot be compared like for like…
  because we analyse the whole dataset whereas they split the data into training and testing sets."
- Stab & Gurevych's own example markers alone: precision **0.884**, recall **0.539** — better recall
  than Williams's set, "Although these markers yield more favourable results in terms of recall than
  our set of markers, they include words that do not explicitly indicate the presence of reasoning."
- Post-validation agreement (Table 5): Author vs Supervisor κ = **0.397** ("fair"); Author vs
  Predictions κ = **0.433** ("moderate"); Supervisor vs Predictions κ = **0.166** ("poor").
- Search demonstration: 3 queries × 100 queries/day × 10 results × 28 days. Totals and unique URLs:

| Search set | Total number of URLs | Unique URLs |
|---|---|---|
| 1 (T+R+E) | 27,990 | 282 |
| 2 ((T+R)+!E) | 28,000 | 207 |
| 3 (T+!(R+E)) | 28,000 | 154 |

- Categorised unique URLs (columns = search sets 1 / 2 / 3): Online articles **136 / 24 / 5**;
  E-commerce & tools 57 / 30 / 23; Education & academic **30 / 47 / 60**; Research 16 / 14 / 12;
  Event ads 12 / 6 / 7; Government 8 / 22 / 8; Seed pages 6 / 1 / 12; Discussion/Q&A 6 / 0 / 1;
  Wiki 4 / 11 / 9; Job ads 2 / 0 / 1; Broken links 2 / 4 / 6; Other 2 / 14 / 9; Review sites
  1 / 0 / 0; Code & documentation **0 / 35 / 1**. PDF counts: 15 (set 1), 60 (set 2), 23 (set 3).
- Interpretation: "This indicates that mentions of experience are perhaps more influential than
  reasoning markers when trying to identify blog articles."
- Single-blog demonstration (Joel Spolsky's blog): **1556 pages crawled**, **1515 extracted**, **41
  failed** ("none of the actual published articles failed to extract"), **201 duplicates removed**,
  **1314 articles analysed**. Top 1% by markers/word count ranged 0.0188 → 0.0160; bottom 1% ranged
  0.0032 → 0.
- Missing control: "There is also a search set missing from the comparison that would have been
  useful. That search set is just topic on its own (T). This hasn't been included due to time
  constraints."

---

## williams_how_2019 — How do empirical software engineering researchers assess the credibility of practitioner–generated blog posts?

(Ashley Williams & Austen Rainer, *EASE '19*, Copenhagen. DOI 10.1145/3319008.3319013)

**Type:** empirical study (online survey, n=43 software engineering researchers).

**Role in corpus:** The only paper in this batch that **empirically ranks** evaluation criteria by
asking the community rather than deriving them from literature — "the first empirical benchmark of
the credibility of blog posts in SE research". It converts the Williams 2017 criteria into a
validated, weighted instrument.

### THE CHECKLIST — reproduce IN FULL

#### The nine credibility criteria put to respondents

Derived from 88 candidate criteria distilled to six (`relevance, strength of argument,
evidence–backed, quality of writing, prior beliefs of the reader, prior beliefs of others who may
influence the reader`), with `evidence–backed` then split into five specific criteria.

| Acronym | Criterion (verbatim) | Derivation |
|---|---|---|
| CoW | Clarity of writing | from `quality of writing` |
| RED | Reports empirical data ("Reporting empirical data") | split from `evidence–backed` |
| RM | Reports data collection ("Reporting the method of data collection") | split from `evidence–backed` |
| PExp | Professional Experience ("Reporting professional experience") | split from `evidence–backed`; "previous research has found that practitioners form opinions based on their personal experience" |
| URL-P | Link to practitioner source ("Citing practitioner sources") | split from `evidence–backed` |
| URL-R | Link to research source ("Citing research sources") | split from `evidence–backed` |
| Reason | Reasoning | from `strength of argument` |
| Beliefs | Prior beliefs (of the reader) | unchanged |
| IofO | Influence of others ("Prior beliefs of others who influence the reader") | unchanged |

Rating scale: 7-point Likert, **"0 Not at all important"** to **"6 Extremely important"**, plus a
**"DK / Don't know"** option.

#### Table 8 — additional criteria proposed by respondents (verbatim)

| Criterion | Explanation (verbatim) |
|---|---|
| Author | "A complex criterion covering a range of author attributes, including expertise; background and experience; conflicts of interest; affiliation; prior beliefs (of the author); motivation and intention; reputation and prestige; presence of declared limitations and self–reflection in the blog post." |
| Context | "The context of the publication process (e.g. peer–review), separate to the context of the author's experience, and to the context in which the reader reads the blog post." |
| Medium | "For example, contrasting Stack Overflow with a blog post with a YouTube video." |
| Blog | "Other properties of the blog, for example the frequency and relevance of blog posts." |

#### Table 10 — concerns raised about the use of blog posts in research (verbatim, all 8)

| Issue | Source |
|---|---|
| "Blogs are anecdotal" | Survey |
| "Blogs contain a lack of contextual information" | Survey |
| "Blogs contain subjective/bias opinions only" | Survey |
| "Blogs are based on experience, which is limited" | Survey |
| "Blogs are not scientifically validated" | Survey |
| "Blogs contain no real evidence" | Survey |
| "Credibility is subjective to the reader, therefore is not truth" | Other |
| "Blogs cannot be trusted as there is no formal review process" | Other |

#### The set of pre-existing checklists the paper positions itself against (verbatim)

> "These include: Kitchenham and Charters' guidelines for conducting systematic reviews; Petersen et
> al.'s guidelines for systematic mapping studies; Garousi et al.'s guidelines for MLRs; Runeson and
> Höst's guidelines and checklists for case study research; Kitchenham and Pfleeger's guidelines for
> survey research; and Kitchenham et al.'s general guidelines on empirical research."

> "Whilst all of these guidelines assert, or prescribe, how to evaluate information, none of these
> guidelines are particular to blog posts."

### Report evaluation procedures

**The validated ranking instrument (Table 5, n=43)** — the deliverable. Criteria ranked by
percentage of respondents rating them "6 Extremely important":

| Criterion | Mean | Mode | Median | SD | %(6) | Rank by Median | Rank by Mean | Rank by %(6) |
|---|---|---|---|---|---|---|---|---|
| Reason (Reasoning) | 5.1 | 6 | 5 | 1.0 | 39.5 | 1 | 1 | 1 |
| RED (Reports empirical data) | 4.9 | 6 | 5 | 1.0 | 32.6 | 1 | 2 | 2 |
| CoW (Clarity of writing) | 4.6 | 5 | 5 | 1.2 | 30.2 | 1 | 3 | 3 |
| RM (Reports data collection) | 4.6 | 4 | 5 | 1.3 | 27.9 | 1 | 3 | 4 |
| PExp (Professional experience) | 4.5 | 5 | 5 | 1.2 | 20.9 | 1 | 4 | 5 |
| URL-R (Link to research source) | 4.3 | 5 | 5 | 1.5 | 14 | 1 | 5 | 6 |
| URL-P (Link to practitioner source) | 4.0 | 5 | 4 | 1.4 | 9.3 | 2 | 6 | 7 |
| Beliefs (Prior beliefs) | 3.1 | 3 | 3 | 1.9 | 7 | 3 | 7 | 8 |
| IofO (Influence of others) | 3.0 | 2 | 3 | 1.8 | 7 | 3 | 8 | 8 |

**Full response distribution (Table 4, n=43)** — frequency and percentage per Likert point:

| Criterion | 0 | 1 | 2 | 3 | 4 | 5 | 6 | DK |
|---|---|---|---|---|---|---|---|---|
| Reason (f / %) | 0 / 0.0 | 0 / 0.0 | 1 / 2.3 | 3 / 7.0 | 5 / 11.6 | 15 / 34.9 | 17 / 39.5 | 2 / 4.7 |
| RED (f / %) | 0 / 0.0 | 0 / 0.0 | 1 / 2.3 | 3 / 7.0 | 11 / 25.6 | 14 / 32.6 | 14 / 32.6 | 0 / 0.0 |
| CoW (f / %) | 0 / 0.0 | 0 / 0.0 | 2 / 4.7 | 8 / 18.6 | 7 / 16.3 | 13 / 30.2 | 13 / 30.2 | 0 / 0.0 |
| RM (f / %) | 0 / 0.0 | 1 / 2.3 | 2 / 4.7 | 4 / 9.3 | 13 / 30.2 | 11 / 25.6 | 12 / 27.9 | 0 / 0.0 |
| PExp (f / %) | 0 / 0.0 | 1 / 2.3 | 2 / 4.7 | 6 / 14.0 | 9 / 20.9 | 16 / 37.2 | 9 / 20.9 | 0 / 0.0 |
| URL-R (f / %) | 1 / 2.3 | 2 / 4.7 | 4 / 9.3 | 1 / 2.3 | 10 / 23.3 | 19 / 44.2 | 6 / 14.0 | 0 / 0.0 |
| URL-P (f / %) | 1 / 2.3 | 2 / 4.7 | 4 / 9.3 | 5 / 11.6 | 12 / 27.9 | 14 / 32.6 | 4 / 9.3 | 1 / 2.3 |
| Beliefs (f / %) | 6 / 14.0 | 3 / 7.0 | 3 / 7.0 | 9 / 20.9 | 7 / 16.3 | 7 / 16.3 | 3 / 7.0 | 5 / 11.6 |
| IofO (f / %) | 5 / 11.6 | 5 / 11.6 | 9 / 20.9 | 5 / 11.6 | 9 / 20.9 | 7 / 16.3 | 3 / 7.0 | 0 / 0.0 |

**Sub-sample analysis (Table 6)** — respondents split by their own view of blog credibility: Low
(scores 0–1), Medium (2–3), High (4–5). `%(6)` = percentage rating the criterion Extremely
important.

| Criterion | %(6) L | %(6) M | %(6) H | Mean L / M / H | Min L / M / H |
|---|---|---|---|---|---|
| CoW | 43 | 28 | 29 | 4.6 / 4.6 / 4.7 | 3 / 2 / 3 |
| RED | 43 | 35 | 14 | 5.4 / 4.9 / 4.1 | **5** / 3 / 2 |
| RM | 44 | 31 | **0** | 5.0 / 4.7 / 3.7 | 2 / 2 / 1 |
| PExp | 29 | 17 | 29 | 4.7 / 4.3 / 4.9 | 2 / 1 / 3 |
| URL-P | 14 | 10 | **0** | 4.3 / 3.9 / 3.9 | 2 / 0 / 2 |
| URL-R | 14 | 17 | **0** | 4.9 / 4.3 / 3.4 | 4 / 0 / 1 |
| Reason | 43 | 31 | **71** | 5.1 / 4.9 / 5.6 | 4 / 2 / 4 |
| Beliefs | 0 | 7 | 14 | 3.2 / 2.8 / 3.9 | 2 / 0 / 2 |
| IofO | 0 | 10 | 0 | 3.4 / 2.7 / 3.6 | 2 / 0 / 2 |

**Generalisation of the instrument (Table 7):**

| Question | Yes | No | It depends | Total |
|---|---|---|---|---|
| "Does the model generalise to practitioner–generated online content?" | 26 (60.5%) | 6 (14.0%) | 11 (25.6%) | 43 |
| "Does the model generalise to researcher–generated content?" | 25 (58.1%) | 10 (23.3%) | 8 (18.6%) | 43 |

**Spearman's rank-order correlations (Table 3)** — used to demonstrate the criteria are independent
constructs. Notable: `RED × RM = 0.74`, `Beliefs × IofO = 0.78`, `URL-P × URL-R = 0.55`; all other
pairs weak. "In most cases, the criteria do not correlate with each other, which suggests we have
independent constructs."

### Caveats, traps and pitfalls

Verbatim:

- **The dominant answer is "it depends"** — "The majority of researchers provide a qualified response
  to the credibility of blog posts: essentially, it depends." Ten of the 37 respondents who
  commented "indicated that 'it depends' e.g., it depends on the topic, subject matter, author."
- **A one-score answer to a complex question is a measurement problem** — "We are conscious that
  respondents are being asked to evaluate a complex situation (i.e., a very large volume of blog
  posts that vary in content and quality) with a one–score response… Given the complexity of the
  situation, a score of 3 might constitute the 'safest' response, or the most conservative response,
  for many respondents."
- **The result is surprisingly weak on empirical data** — "it is surprising how low (some of) the
  percentages are e.g. 'only' 32% of researchers consider the Reporting of empirical data to be
  extremely important. This is surprising for an empirical discipline."
- **Reasoning is valued but ungoverned** — "Given these responses, it is curious that the quality of
  reasoning receives relatively little explicit consideration in software engineering research e.g.
  there are few guidelines in the field on argumentation or reasoning."
- **Two of the valued criteria have no checklist support** — "Two of the valued criteria — Reasoning
  and Clarity of writing — are not usually explicitly discussed by researchers e.g. there is a lack
  of guidelines on reasoning, in contrast to many guidelines and checklists for study design, data
  collection, analysis etc."
- **Researchers and practitioners value opposite things** — "Devanbu et al. and Rainer et al. found
  that software engineering practitioners valued their own personal experience, and that of their
  colleagues, over independent, third–party empirical evidence. By contrast, researchers assign a
  low importance to Prior beliefs and Influence of others."
- **Contradictory subgroups explain the controversy** — "the High–credibility respondents place a
  high value on Reasoning and a low value on Reporting empirical data for blog posts, in contrast to
  the Low–credibility respondents who place a relatively high value on Reporting empirical data.
  … This may (partially) explain why blog posts are contentious for some members of the research
  community."
- **Self-report ≠ behaviour** — "in conducting a survey we ask respondents how they think they assess
  credibility rather then measuring the reality of what those respondents actually do. Similarly, we
  ask respondents for their general ratings in contrast to, for example, providing a concrete example
  of a blog post and asking respondents to evaluate that post."
- **A removed outlier materially changes the result** — "we removed the responses from one respondent
  as they were 'internally contradictory'. Removing the 'datapoint' affects the results, albeit in a
  'positive' way… The anomalies apparent for that respondent's responses may recur, but in a subtler
  way, for other respondents." The outlier scored 0 on general credibility yet 1 across every
  criterion, while writing "…it is simply impossible to evaluate the value [of blog posts] since no
  real evidence is provided…".
- **Statistics fishing** — "We are conscious that with sufficient quantities of statistics (as in
  Table 6) one is more likely to find interesting values by chance."
- **Why frequencies of qualitative codes were deliberately not reported** — "Quantifying the
  qualitative data dilutes that richness and simply provides another set of quantitative results.
  Second, a respondent can provide qualitative comments for each and all of the criteria, with the
  effect that there could be a kind of 'double counting' of frequencies of codes… Third, the quantity
  of comments declined as the respondents progressed through the survey, with reduced variation and
  frequency of codes identified for later criteria. This results in a kind of imbalanced dataset."
- **Representativeness** — "There is always the question as to whether survey respondents are
  representative of the wider population."
- **The uncontrolled invitation chain** — "Four of these invitee's asked us whether they could forward
  the survey to their colleagues. We approved these requests but were not able to track increase in
  numbers of invited participants. Consequently, we are unable to accurately report the number of
  people who actually received the invitation."
- **The instrument is unvalidated for the intended targets** — "The study would benefit from
  independent replication and evaluation."
- Respondent quotes that qualify generalisation, verbatim (selection):
  - "Unlike academic articles, which can be judged on the basis of the method and data collected, the
    quality of a blog articles also depends on the reputation and experience of the author: everyone
    can have an opinion (which is what most blog articles express I think), but opinions of reputable
    authors carry more weight."
  - "Unfortunately, research publications do not provide means to assess the article's authors' past
    experience."
  - "The key difference… between research publications and practitioner produced material should have
    been subject to scrutiny through peer-review. The same cannot always be said of blog material.
    Whether the peer review of academic publishing is more rigorous and hence intrinsically of better
    'quality' in terms of is, however, questionable."
  - "I think we should assess the type of information according to its intention. It is unfair to
    assess a blog post as we would do to a scientific paper, and vice–versa. They have different
    target audience… Both can be assessed regarding a their reasoning and the use of practical
    experiences, though."
  - "Clarity and method descriptions are in general more important when assessing research
    contributions while CV and reputation is less important"

### Empirical findings worth citing

- **n=43** completed responses used (44 completed, 1 removed as an outlier); **138 researchers
  invited** (EASE and ESEM Programme Committees); **57 started**, **44 completed** → response rate
  **32%**. Pilot: 8 responses from SI^NZ.
- Respondent experience: **2 to 35 years**, mean **16.2 years**.
- Survey window: **13 February 2018 – 26 March 2018**. Completion time: 2.4 minutes to 22 hours;
  ignoring the five >1 hour responses, 2.4 to 47.1 minutes, average **11.7 minutes**.
- General credibility of practitioner blog posts (0–5 scale): **Mode = 3, Median = 3, Mean = 2.7**.
  Subgroups: **n=7** consider blog posts generally credible; **n=7** generally not credible; **n=29
  (67%)** intermediate.
- **60.5%** think the criteria generalise to other practitioner-generated content; **58.1%** to
  researcher-generated content.
- Criterion construction: **833 candidate articles** identified via Google Scholar → de-duplication,
  filtering, selection/rejection criteria → **13 papers** shortlisted → **88 candidate criteria** →
  distilled to **6** → expanded to **9** survey criteria.
- Prior use of blog posts in SE research (Table 1) — a useful scale reference: Pagano 2011 = **50,000
  blog posts**; Inui 2008 = **50M posts**; Kurashima 2009 = **29M blog posts**; Kurashima 2006 =
  **62,396**; Park 2010 = **6000**; Swanson 2014 = **5000**; Williams 2018 = **2852**; Parnin 2011 =
  **376**; Parnin 2013 = **300**; Soldani 2018 = **20/51 blog posts (40% of dataset)**;
  Raulamo–Jurvanen 2017 = **60 GL sources**; Garousi 2016 = **46 internet articles & white papers**;
  Rainer 2017 = **one blog post**.
- How quality is currently handled per study category, verbatim: "For secondary studies, each
  secondary study develops its own quality checklist for assessing the quality of grey literature,
  with Garousi et al. proposing a more generic checklist as part of their guidelines for MLRs. For
  data mining research, the quality of the dataset of blog posts… is often evaluated with measures of
  annotator agreement. The remaining category, primary studies of software practice, **appears to
  generally accept the quality of blog posts without evaluation**."

---

## Cross-batch: mapping tables SEGRESS uses to build its per-type guidance

These are the crosswalks a tool would need to support non-SR review types. Reproduced in full
because they are the evidentiary basis for SEGRESS's per-type applicability labels.

### SEGRESS Table 5 — Mapping PRISMA-ScR (scoping review) items to PRISMA 2020 items

| Id | Review aspect | Information Required (verbatim) | PRISMA item |
|---|---|---|---|
| 1 | Title | "Identify the report as a scoping review" | 1 |
| 2 | Abstract | "Provide a structured summary that includes (as applicable) background, objectives, eligibility criteria, sources of evidence, charting methods, results, and conclusions that relate to the review questions and objectives." | 2 |
| 3 | Rationale | "Describe the rationale for the review in the context of what is already known. Explain why the review questions/objectives lend themselves to a scoping review approach." | 3 |
| 4 | Objectives | "Provide an explicit statement of the questions and objectives being addressed with reference to their key elements (e.g., population or participants, concepts, and context) or other relevant key elements used to conceptualize the review questions and/or objectives." | 4 |
| 5 | Protocol & Registration | "Indicate whether a review protocol exists; state if and where it can be accessed (e.g., a Web address); and if available, provide registration information, including the registration number." | 24a, 24b |
| 6 | Eligibility criteria | "Specify characteristics of the sources of evidence used as eligibility criteria (e.g., years considered, language, and publication status), and provide a rationale." | 5 |
| 7 | Information Sources | "Describe all information sources in the search (e.g., databases with dates of coverage and contact with authors to identify additional sources), as well as the date the most recent search was executed." | 6 |
| 8 | Search | "Present the full electronic search strategy for at least 1 database, including any limits used, such that it could be repeated." | 7 |
| 9 | Selection of sources of evidence | "State the process for selecting sources of evidence (i.e., screening and eligibility) included in the scoping review." | 8 |
| 10 | Data charting process | "Describe the methods of charting data from the included sources of evidence (e.g., calibrated forms or forms that have been tested by the team before their use, and whether data charting was done independently or in duplicate) and any processes for obtaining and confirming data from investigators." | 9, 13b |
| 11 | Data items | "List and define all variables for which data were sought and any assumptions and simplifications made." | 10b |
| 12 | Critical Appraisal of individual sources of evidence | "If done, provide a rationale for conducting a critical appraisal of included sources of evidence; describe the methods used and how this information was used in any data synthesis (if appropriate)." | 11 |
| 13 | Synthesis of results | "Describe the methods of handling and summarizing the data that were charted." | 9, 13c |
| 14 | Selection of sources of evidence | "Give numbers of sources of evidence screened, assessed for eligibility, and included in the review, with reasons for exclusions at each stage, ideally using a flow diagram." | 16a, 16b |
| 15 | Characteristics of sources of evidence | "For each source of evidence, present characteristics for which data were charted and provide the citations." | 17 |
| 16 | Critical Appraisal of sources of evidence | "If done, present data on critical appraisal of included sources of evidence (see item 12)." | 18 |
| 17 | Results of individual sources of evidence | "For each included source of evidence, present the relevant data that were charted that relate to the review questions and objectives." | 19, 20a |
| 18 | Synthesis of results | "Summarize and/or present the charting results as they relate to the review questions and objectives." | 20b |
| 19 | Summary of evidence | "Summarize the main results (including an overview of concepts, themes, and types of evidence available), link to the review questions and objectives, and consider the relevance to key groups." | 23a |
| 20 | Limitations | "Discuss the limitations of the scoping review process." | 23c |
| 21 | Conclusions | "Provide a general interpretation of the results with respect to the review questions and objectives, as well as potential implications and/or next steps." | 23d |
| 22 | Funding | "Describe sources of funding for the included sources of evidence, as well as sources of funding for the scoping review. Describe the role of the funders of the scoping review." | 25, 26 |

Three terminology traps SEGRESS flags in PRISMA-ScR:
1. "PRISMA-ScR talks about 'sources of evidence'. By this we understand the authors to mean an
   individual primary study, since it is possible that one article or report might contain more than
   one primary study."
2. "PRISMA-ScR talks about the 'data charting process'… this meant the process of extracting all the
   variables and the textual information that were used to address the research questions from each
   primary study in 'calibrated forms' (i.e., agreed data extraction forms). In the context of SE
   mapping studies we often need to classify primary studies. The specification of the classification
   system(s) used would be part of the data definitions item, whereas the process of extracting the
   classification data would be part of the data charting process item."
3. "PRISMA-ScR uses the term Synthesis of Results to remain consistent with PRISMA… However, there is
   a substantial difference between investigating the characteristics of scientific articles and
   empirical studies and synthesising the outcomes of empirical studies. … We would prefer to use the
   term *Analysis of Study Characteristics* rather than *Synthesis of Results* for SE mapping
   studies."

Scoping review vs mapping study: "the main difference appears to be that a mapping study addresses a
broad topic area, while a scoping review aims at assessing whether there is sufficient evidence to
undertake a systematic review. Thus, findings from a mapping study might be more extensive and
varied than those from a scoping review. Nonetheless, our basic assumption is that reporting
guidelines for mapping studies address the same basic items as the guidelines for scoping reviews."

### SEGRESS Table 7 — Mapping ENTREQ qualitative synthesis items to PRISMA 2020 items

| Id | Domain | Review aspect | Information Required (verbatim) | PRISMA item |
|---|---|---|---|---|
| 1 | 1 Introduction | Aim | "State the research questions the synthesis addresses." | 4 |
| 2 | 2 Method | Synthesis Methodology | "Identify the synthesis methodology or the theoretical framework which underpins the synthesis and describe the rationale for choice of methodology." | 13d |
| 3 | 3 Literature search and selection | Approach to Searching | "Indicate whether the search was pre-planned or iterative." | 7 |
| 4 | 3 | Inclusion criteria | "Specify the inclusion criteria." | 5 |
| 5 | 3 | Data sources | "Describe the information sources used (e.g., digital libraries), when the search was conducted and the rationale for the using the data source." | 6 |
| 6 | 3 | Electronic search strategy | "Define search strings used." | 7 |
| 7 | 3 | Study screening methods | "Describe the methods used to screen the studies." | 8 |
| 8 | 3 | Study characteristics | "Present the characteristics of the included studies." | 10a, 17 |
| 9 | 3 | Study selection results | "Identify the number of studies screened and provide reasons for study inclusion." | 16 |
| 10 | 4 Quality Appraisal | Rationale for appraisal | "Describe the rationale and approach used to appraise the selected studies or study findings." | 11 |
| 11 | 4 | Appraisal items | "State the tools, frameworks and criteria used to appraise the studies or selected findings." | 11 |
| 12 | 4 | Appraisal process | "Indicate whether appraisal was conducted independently by more than one reviewer and if consensus was required." | 11 |
| 13 | 4 | Appraisal results | "Present results of quality assessment and indicate which articles, if any, were weighted/excluded and give the rationale." | 18 |
| 14 | 5 Synthesis of findings | Data Extraction | "Indicate which sections of the primary studies were analysed and how the data were extracted from the primary studies." | 9 |
| 15 | 5 | Software | "State the computer software used, if any." | 9 |
| 16 | 5 | Number of reviewers | "Identify who was involved in the coding and analysis." | 9 |
| 17 | 5 | Coding | "Describe the process for coding." | 13b |
| 18 | 5 | Study comparison | "Describe how comparisons were made within and across studies." | 13c, 13e |
| 19 | 5 | Derivation of themes | "Explain whether the process of deriving themes or constructs was inductive or deductive." | 13d |
| 20 | 5 | Quotations | "Provide quotations from the primary studies to illustrate themes/constructs and identify whether the quotations were participant quotations or the authors interpretations." | 20a, 20c |
| 21 | 5 | Synthesis output | "Present rich, compelling and useful results that go beyond a summary of the primary studies." | 20a, 20c, 23a, 23d |

### SEGRESS Table 8 — Mapping RAMESES qualitative synthesis items to PRISMA 2020 items

| Id | Review aspect | Information Required (verbatim) | PRISMA item |
|---|---|---|---|
| 1 | Title | "Identify the document as a realist synthesis or review." | 1 |
| 2 | Abstract | "Brief details of the background, review questions or objectives, search strategy, method of selection, appraisal, analysis and synthesis, main results, and implications for practice." | 2 |
| 3 | Rationale for review | "Explain why the review is needed and what it is likely to contribute to existing understanding of the topic area." | 3 |
| 4 | Objectives and focus of review | "State the objectives of the review and/or the review question(s). Define and provide a rationale for the focus of the review." | 4 |
| 5 | Changes in the review process | "Any changes made to the review process that was originally planned should be briefly described and justified." | 24c |
| 6 | Rationale for using realist synthesis | "Explain why realist synthesis was considered the most appropriate method to use." | 13d |
| 7 | Scoping the literature | "Describe and justify the initial process of exploratory scoping of the literature." | 7 |
| 8 | Searching process | "State and provide a rationale for how the iterative searching was done. Provide details of all the sources accessed for information in the review. For electronic databases report, for example, name of database, search terms, dates of coverage and date last searched. If researchers with topic knowledge were contacted, indicate how they were identified and selected." | 7, 8 |
| 9 | Selection and appraisal of documents | "Explain how judgments were made about including and excluding data from documents, and justify these." | 5, 8 |
| 10 | Data Extraction | "Describe and explain which data or information were extracted from the included documents and justify this selection." | 10a |
| 11 | Analysis and synthesis processes | "Describe the analysis and synthesis processes in detail. This section should include information on the constructs analyzed and describe the analytic process." | 13 |
| 12 | Document flow diagram | "Provide details on the number of documents assessed for eligibility and included in the review with reasons for exclusion at each stage as well as an indication of their source of origin (for example, from searching databases, reference lists and so on)." | 16 |
| 13 | Document characteristics | "Provide information on the characteristics of the documents included in the review." | 17 |
| 14 | Main findings | "Present the key findings with a specific focus on theory building and testing." | 20a |
| 15 | Summary of findings | "Summarize the main findings, taking into account the review's objective(s), research question(s), focus and intended audience(s)." | 23a |
| 16 | Strengths, limitations and future research directions | "Discuss both the strengths of the review and its limitations. These should include (but need not be restricted to) (a) consideration of all the steps in the review process, and (b) comment on the overall strength of evidence supporting the explanatory insights which emerged. The limitations identified may point to areas where further work is needed." | 23b, 23c |
| 17 | Comparison with existing literature | "Where applicable, compare and contrast the review's findings with the existing literature (for example, other reviews) on the same topic." | 23a |
| 18 | Conclusion and recommendations | "List the main implications of the findings and place them in the context of other relevant literature. If appropriate, offer recommendations for policy and practice." | 23d |
| 19 | Funding | "Provide details of funding source (if any) for the review, the role played by the funder (if any) and any conflicts of interest of the reviewers." | 25, 26 |

### Standards inventory (SEGRESS Tables 3 and 6)

| ID | Name | Scope | Derivation |
|---|---|---|---|
| PRISMA | Preferred Reporting Items for Systematic Reviews | "Reporting quantitative systematic reviews and meta-analysis" | — |
| PRISMA-ScR | PRISMA Extension for Scoping Reviews | "Reporting scoping reviews" | "Based on PRISMA after removing items related to synthesis and risk of bias" |
| PRISMA-P | Preferred reporting items for systematic review and meta-analysis protocols | "Developing protocols for systematic reviews and meta-analyses that will be reported using PRISMA" | "Based on specifying all the items in a PRISMA–compliant SR" |
| PRISMA-A | PRISMA for Abstracts | "Specifying abstracts for PRISMA-based systematic reviews in journals and conferences" | "Based on PRISMA. Updated in PRISMA 2020" |
| PRISMA-S | An extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews | "Supports three items in PRISMA: Information sources, Search Strategies and Study Selection Results (items 7, 8 and 14 in PRISMA and items 6, 7, and 16 in PRISMA 2020)" | "Based on PRISMA and an extensive expert-opinion based development process, including consultation with developers of PRISMA 2020." |
| GRADE | Grading of Recommendations Assessment, Development, and Evaluation | "Assessing the strength of recommendations made in systematic reviews, health technology assessments and clinical practice guidelines. Supports PRISMA 2020 item 22 Certainty of Evidence." | "The original ideas were presented in [21] and have been revised and refined in a series of articles produced by a technical working group" |
| PRISMA 2020 | The PRISMA 2020 statement | "Reporting quantitative systematic reviews, evaluation studies, meta-analysis, and mixed methods. Includes an update to PRISMA-A" | "Based on PRISMA after substantial research" |
| RAMESES | Realist And MEta-narrative Evidence Synthesis | "Reporting the outcomes of complex interventions and adopting policy friendly approaches to evidence synthesis" | "Guidelines for reporting guidelines, excluding Delphi exercise" |
| ENTREQ | ENhancing Transparency in REporting the synthesis of Quality research | "A framework for reporting the synthesis of qualitative health research" | "Protocol for guidelines construction" |
| GRADE-CERQual | Confidence in the Evidence from Reviews of Qualitative Research | "To support the use of findings from systematic reviews of qualitative evidence" | Development discussed in a series of Implementation Science papers |

---

## Item counts reproduced

| Standard | Count |
|---|---|
| **SEGRESS** (Kitchenham et al. 2023 Table 9 = 2022 Table 1) | **27 top-level items → 44 numbered checklist rows** with sub-items expanded, **plus 9 unnumbered guidance rows** (Full Report; Title section; Abstract section; Introduction section; Opening; Methods section; Results section; the [17-22] Reporting Style note; Discussion section) = **53 rows total** |
| **PRISMA 2020** (Page et al. 2021) | **27 main items → 42 numbered rows** with sub-items expanded, **plus 12 abstract-checklist items** = **54 items total** |
| PRISMA-ScR (as tabulated by SEGRESS Table 5) | 22 items |
| ENTREQ (as tabulated by SEGRESS Table 7) | 21 items in 5 domains |
| RAMESES (as tabulated by SEGRESS Table 8) | 19 items |
| DARE criteria | 5 |
| Budgen et al. essential-information items | 9 |
| GRADE domains / levels | 5 domains × 4 levels |
| GRADE-CERQual components | 4 |
| Williams 2017 blog-content credibility criteria (Table 4) | 11 candidates → 4 chosen |
| Williams 2018 reasoning markers (Table 13) | 86 |
| Williams 2019 credibility criteria | 9 (from 88 candidates → 6 → 9) |
