# Batch 8 — Threats-to-Validity Frameworks + Goal-Oriented Measurement (GQM)

Source texts: `scratchpad/txt/{ampatzoglou_guidelines_2020, petersen_worldviews_2013, basili_goal_1994}.txt`
plus `/home/isaacg/git/sms-reseacher/research/basili_software_1992.pdf` (scanned image; read via vision, **readable**).

---

## Ampatzoglou 2020 — Guidelines for Managing Threats to Validity of Secondary Studies in Software Engineering

Ampatzoglou, A., Bibi, S., Avgeriou, P., Chatzigeorgiou, A. Book chapter, based on Ampatzoglou et al.,
"Identifying, categorizing and mitigating threats to validity in software engineering secondary studies",
*Information and Software Technology* 106(2), pp. 201–230, Feb 2019.

**Type:** guideline (derived from a tertiary study — an SLR of secondary studies)

**Role in corpus:** This is the only paper in the corpus that supplies a *complete, closed catalogue* of
threats to validity specific to **secondary studies** (SLRs and SMSs), keyed to the *phase of the review*
rather than to classical experiment-validity categories, with an explicit mitigation action list per threat
and a usable yes/no checklist for authors, reviewers and readers.

### THE VALIDITY FRAMEWORK — reproduced IN FULL

#### The three-level classification schema

> "The classification schema consists of three levels: the first one depicting threat categories, the second,
> threats per se, whereas the third one, mitigation actions."

The **first level (categories)** is deliberately derived from the *planning phases of the secondary study*
— search process, study filtering, data extraction, data analysis — **not** from the aspect of validity that
is threatened:

> "To derive the threat categories (first level of the schema) and to facilitate the classification of any
> given threat, we use the planning phases of the secondary studies (i.e., search process, study filtering,
> data extraction and analysis—see Figure 2). These are easily identifiable steps in a secondary study, in
> contrast to using the aspects of validity that are threatened (e.g., internal / external / construct
> validity, etc.)."

The three categories, verbatim:

| Category | Definition (verbatim) | Phases covered |
|---|---|---|
| **Study Selection Validity** | "This category involves threats that can be identified in the first two phases of secondary studies (i.e., search process and study filtering phase). Issues classified in this category threaten the validity of searching and including primary studies in the examined set. This involves threats like the selection of digital libraries, search string construction, etc." | Search process; Study filtering |
| **Data Validity** | "This category includes threats that can be identified in the last two phases of secondary studies (i.e., data extraction and analysis) and threaten the validity of the extracted dataset and its analysis. Examples of threats in this category are small sample size, lack of statistical analysis, etc." | Data extraction; Data analysis |
| **Research Validity** | "Threats that can be identified in all phases and concern the overall research design are classified into this category. Examples of threats in this category are: generalizability, coverage of research questions, etc." | All phases (horizontal) |

Structural claim about orthogonality:

> "Using the proposed classification schema, we address the problem of classifying a single threat to two
> categories: every threat is classified within one category, based on the phase of the study design, in
> which it was identified and the set of artifacts, whose validity is threatened."

Counts stated by the paper: Study Selection Validity "involves 7 specific threats"; Data Validity "includes
9 specific threats … organized into three groups and five ungrouped threats"; Research Validity "includes 6
specific threats … forming two groups and include four ungrouped threats".
`[EXTRACTION NOTE: the Data Validity sentence says "five ungrouped", but Fig. 3b and the checklist list SIX
ungrouped data-validity threats — TV9, TV10, TV11, TV12, TV14, TV16 — against three groups (TV8, TV13,
TV15), which is what sums to the stated 9. Treat "five" as an error in the source.]`

**Total distinct threats reproduced below: 22 top-level threats (TV1–TV22), which expand to 34 distinct
named threats once the 18 named sub-threats under the six grouped threats (TV1, TV8, TV13, TV15, TV18,
TV22) are counted in place of their six parents. 60 distinct mitigation actions are enumerated in the
checklist (plus one further action, "Use tools for bibliography management", that appears only in Fig. 4).**

---

#### CATEGORY 1 — STUDY SELECTION VALIDITY (TV1–TV7)

Checklist top-level question is given verbatim; the "Definition" column reproduces the definition from
Section 3.1 verbatim where the paper gives one.

| Category | Threat | Definition (verbatim) | Review phase affected | Mitigation actions (verbatim, from the checklist §2.2) |
|---|---|---|---|---|
| Study Selection | **TV1 — Adequacy of relevant publication identification** (group). Checklist: "Has your search process adequately identified all relevant primary studies?" | Group threat; the paper states "Five threats to validity can be grouped in a more generic one, i.e., Adequacy of initial relevant publication identification (TV1)". | Search process | MA1: "Have you used snowballing?" · MA2: "Have you performed pilot searches to train your search string?" · MA3: "Have you selected the most-known digital libraries or have you made a selection of specific publication venues or used broad search engines or indices (based on the goal of your study)?" · MA4: "Have you compared your list of primary studies to a gold standard or to other secondary studies?" · MA5: "Have you used a broad search process in generic search engines or indices (e.g., Google Scholar) so that you ensure the identification of all relevant publication venues?" · MA6: "Have you used a strategy for systematic search string construction?" · MA7: "Has an independent expert reviewed the search process?" · MA8: "Have you used tools to facilitate the review process?" · MA9: "Have you evaluated search results and documented the outcomes?" — *plus, from Fig. 4 only:* "1.10 Use tools for bibliography management" |
| Study Selection | **TV1.1 — Construction of search string** | "Construction of the search string refers to problems that might occur when the researchers are building the search string. As a consequence, the search might return a large number of primary studies (including many irrelevant ones) or a very limited number (thus missing some relevant studies)." | Search process | Inherits TV1 MA1–MA9. Exemplar cited: Shanin et al. — "complemented automated searching in digital libraries with manual search on specific venues that are considered as important to the domain of the secondary study … used snowballing (both backward and forward) to decrease the chances of missing articles". Also "the careful construction of the search string [2], based on the PICO strategy proposed by Kitchenham et al. [33] that takes into account the population, intervention, comparison, and outcomes of the review." |
| Study Selection | **TV1.2 — Selection of digital libraries** | "Selection of Digital Libraries refers to problems that can arise from using very specific, too broad, or not credible search engines. The consequence of this threat can be either the return of a lot irrelevant or missing of relevant studies." | Search process | Inherits TV1 MA1–MA9. Exemplar: Garces et al. "opted to select the most adequate databases for their search. Based on the criteria discussed by Dieste and Padua [18], they opted for using six databases: namely ACM Digital Library, IEEE Xplore, ScienceDirect, Scopus, Springer, and Web of Science." |
| Study Selection | **TV1.3 — Selection of publication venues** | "Selection of publication venues refers to the problem that might occur, when the research team selects to explore specific venues rather than using broad search engines. The most common rationale for this decision is either the fact that a topic is too broad, or that the research aims at high quality studies only. The consequence of this threat is missing relevant studies." | Search process | Inherits TV1 MA1–MA9. Exemplars: select venues "based on their relevance to software engineering, their specificity (e.g., architecture, maintenance, etc.), and their average number of citations per month in Google Scholar"; "it is also crucial to pilot the searches and compare the obtained studies against a golden standard" — Jabangwe et al. "developed the golden standard set by creating an initial validation through Google Scholar, by identifying relevant papers to seminal works (i.e., mostly cited ones) of the secondary study domain." |
| Study Selection | **TV1.4 — Definition of starting year** `[EXTRACTION UNCLEAR: Fig. 3a labels this "TV1.3" a second time; the numbering in the figure is garbled. The order in the figure is: search string, digital libraries, publication venues, starting year, search engine inefficiencies.]` | "The selection of an arbitrary starting year as a starting point for performing the search process can lead to missing studies prior to that date. In order for this decision to not be considered as a threat, it should be clear why such a choice does not influence the results." | Search process | Inherits TV1 MA1–MA9. Also TV22-MA2 "Have you used a broad search process w/o an initial starting date?" Justification exemplar: Li et al. — a documented step-change in publication volume (post-2010 technical-debt literature after the MTD workshop began) legitimises a starting year. "If such a justification cannot be claimed researchers should consider shifting the starting year earlier." |
| Study Selection | **TV1.5 — Search Engines Inefficiencies** `[Figure labels it "TV1.4"; see note above.]` | "Problems of the search engines within digital libraries are characterized as Search engine inefficiencies (e.g., SpringerLink cannot perform a search based only on the abstract of manuscripts). This can lead to missing studies, or deriving a large corpus of papers for filtering." | Search process | "A tentative mitigation action for this threat is the use of bibliography management tools (e.g. JabRef, Zotero, etc.) for further filtering the large corpus of retrieved articles, based on the desired fields. This mitigation action, although it does not reduce the amount of effort required for data collection, it ensures the consistency of data collection." |
| Study Selection | **TV2 — Limited journals/conferences.** Checklist: "Were primary studies relevant to the topic of the review published in several different journals and conferences?" | "A limited number of publication venues in which primary studies can be published suggest a narrow scope of the secondary study. This will probably lead to obtaining a low number of primary studies. If the intended scope of the study is indeed narrow there might be no reason to mitigate this threat…" | Search process | MA1: "Have you used a broad search process in generic search engines or indices (e.g., Google Scholar) so that you ensure the identification of all relevant publication venues?" (Fig. 3a: "MA1: Use broad searches"). Also stated: "alternative strategies could be the inclusion of grey literature, or the execution of broader searches." |
| Study Selection | **TV3 — Missing non-English papers.** Checklist: "Have you identified primary studies in multiple languages?" | "Exploring studies written in a specific language (e.g., Missing non-English papers) can lead to the omission of important studies (or number of studies) written in other languages. This threat, exists in almost any secondary study that considers primary studies written in English, since most of them list it as an exclusion criterion. To our opinion this consist a threat only in cases that a very active community publishes high-quality papers in a domain, in languages other than English." | Search process / Study filtering | MA1: "Is their number expected to be high compared to the population?" (Fig. 3a: "MA1: Check if the no. of identified papers is a low fraction of population"). "A way to evaluate the risk that this threat poses is to assess the number of studies written in non-English languages compared to the population of the research corpus, regardless of the language." |
| Study Selection | **TV4 — Paper inaccessibility.** Checklist: "Were the full texts of all primary studies accessible from the researchers?" | "Papers whose full-text is not available cannot be processed (i.e., Papers inaccessibility). If this number is large, the set of retrieved studies might be limited / not representative." | Study filtering | MA1: "Is the number of studies with missing full texts expected to be high compared to the population?" Also: Magdaleno et al. "refer to asking access to the papers through email, directly from the authors"; "other sources (e.g., research social media, personal websites, etc.) can be used for retrieving a copy, as well as personal contact to the authors by email." |
| Study Selection | **TV5 — Handling of duplicate articles.** Checklist: "Have you managed duplicate articles?" | "Some early versions of a study may be published in a conference, and an extended one in a journal. Duplicate studies should be identified and handled, so that the study set, does not contain duplicate information." | Study filtering | MA1: "Have you developed a consistent strategy (e.g., keep the newer one or keep the journal version) for selecting which study should be retained in the list of primary studies?" · MA2: "Have you used summaries of candidate primary studies to guarantee the correct identification of all duplicate articles?" (Fig. 3a: "MA1: Use summaries of articles", "MA2: Develop strategy for handling duplicates"). Also: Ampatzoglou et al. "suggested the merging of multiple versions as one study … only the journal article can be added to the set of primary studies without the risk of missing relevant information." |
| Study Selection | **TV6 — Inclusion/exclusion of grey literature.** Checklist: "Have you included/excluded grey literature?" | "Based on the goal of the study, including or excluding grey literature can pose a threat. For example, grey literature should be considered in Multi-Vocal Literature Reviews (MLRs), in which practitioners' view should be examined. … On the other hand, if the authors are interested in focusing only on top quality venues …, then grey literature should be omitted form the searching space." | Search process / Study filtering | MA1: "Does the decision to include or exclude grey literature comply with the goals of the study and the availability of sources?" (Fig. 3a: "MA1: Check against study goals") |
| Study Selection | **TV7 — Study inclusion/exclusion.** Checklist: "Have you adequately performed study inclusion/exclusion?" | "Study inclusion/exclusion bias refers to problems that might occur in the study filtering phase, i.e., when applying the inclusion/exclusion criteria. Such threats are usually found in studies, in which there are conflicting inclusion/exclusion criteria, or very generic ones." | Study filtering | MA1: "Have you used systematic voting?" · MA2: "Have you performed random screening of articles among authors?" · MA3: "Have researchers discussed the inclusion or exclusion of selected articles in case of conflict?" · MA4: "Have the inclusion exclusion criteria been documented explicitly in the protocol?" · MA5: "Have the authors discussed the inclusion/exclusion criteria and revised them after pilots, or by experts' suggestions after review?" · MA6: "Have you prescribed a set of decision rules for study inclusion/exclusion?" · MA7: "Have you defined quality thresholds for inclusion/exclusion?" · MA8: "Have you performed sensitivity analysis?" · MA9: "Have you quantified experts' disagreement with the kappa statistic?" — Exemplar (Yang et al.): "(a) set a group of inclusion and exclusion criteria for study selection, which can be provided as a basis of an objective selection process; (b) considering the possible different interpretation and understanding of selection criteria by the researchers, a pilot selection has to be conducted before the formal selection to guarantee that the researchers reached a clear and consistent understanding of the selection criteria; and (c) two researchers need to conduct the study selection independently in at least in one round of selection, and discuss / resolve any conflicts between their results, to mitigate personal bias in study selection." |

**Mutual exclusivity rule stated for this category:**

> "From the threats of this category, some are mutually exclusive, whereas others may coexist. For example,
> if selection of digital libraries is performed, the threat selection of publication venues (TV1.3) is
> excluded since, normally only one of the two search strategies (digital libraries or venues) is selected
> (except if a quasi-gold standard from specific venues is used for study selection validation; then both
> strategies are used). The construction of the search string threat (TV1.1) exists both when digital
> libraries or specific publication venues are selected."

---

#### CATEGORY 2 — DATA VALIDITY (TV8–TV16)

| Category | Threat | Definition (verbatim) | Review phase affected | Mitigation actions (verbatim) |
|---|---|---|---|---|
| Data | **TV8 — Small sample size** (group). Checklist: "Is your sample size large enough so that the obtained results can be considered valid?" | "A small sample threatens the validity of the dataset, since results may be: (a) prone to bias (data might come from a small community), (b) not statistically significant, and (c) not safe to generalize." Group described as "limitations of the dataset (TV8) that are due to the nature of the subject and not due to researchers' bias (i.e., small sample size and heterogeneous primary studies)." | Data extraction; Data analysis | MA1: "Have you tried to draw conclusions based on trends?" · MA2: "Have you used a broad search process in generic search engines or indices (e.g., Google Scholar) so that you ensure the identification of all relevant publication venues?" (Fig. 3b: "MA1: Draw conclusions based on trends", "MA2: Use broad searches"). Also: "The small sample size can be mitigated by broadening the searching space [3], but this decision must comply with the goals of the study and the research area of interest. Additionally, according to Barreiros et al. [11] the small sample size threat is mitigated if the quality of the obtained studies (although low in quantity) is high." |
| Data | **TV8.1 — Small sample size** (sub-threat) | See TV8. | Data extraction; Data analysis | As TV8. |
| Data | **TV8.2 — Primary study heterogeneity** | "Data from primary studies that are highly heterogeneous are not easy / safe to synthesize, since such a process is prone to involve a high degree of subjectivity." | Data extraction; Data analysis | "the careful construction of the search string [2], based on the PICO strategy proposed by Kitchenham et al. [33] that takes into account the population, intervention, comparison, and outcomes of the review. Such an approach aims at identifying only the most relevant publications, by limiting the chances for a heterogeneous dataset. Additionally, Nguyen-Duc et al. [43] suggested the development of a data extraction form based on the research questions to ensure that collected data will be as homogenous as possible." |
| Data | **TV9 — Choices of variables to be extracted.** Checklist: "Have you chosen the correct variables to extract?" | "The variables that have been chosen to be extracted might threaten the validity of the results, since they might not fit answering the research questions. Additionally, they are prone to researchers' bias." | Data extraction | MA1: "Has the choice of variables been discussed among authors to guarantee that the research questions can be answered?" (Fig. 3b: "MA1: Discuss among authors"). Also: "The best practice that can be used for mitigating this threat is the extraction of variables based on the set of research questions and their beforehand mapping." Exemplar (Galster et al.): "the authors list the extracted variables, and inside a parenthesis they denote the research question that can be answered by using them." |
| Data | **TV10 — Publication bias.** Checklist: "Are the studies in your dataset published in a limited set of venues?" | "Publication bias refers to cases where the majority of primary studies are identified in a specific publication venue. If the majority of primary studies stem from a single workshop, the likelihood of biasing the dataset (the values recorded for every study), and thereof the results, based on the beliefs of a certain community, is rather high." | Study selection → damages Data extraction/analysis (classified under Data Validity) | MA1: "Have you used snowballing?" · MA2: "Have you included grey literature (if this does not affect TV6)?" · MA3: "Have you manually scanned selected venues to check if they publish articles related to your secondary study?" (Fig. 3b: "MA1: Snowballing", "MA2: Include grey literature", "MA3: Investigate manually other venues"). Caveat: "both these mitigation actions should be treated with caution, since in specific types of studies, they pose more significant threats to validity. For example, the inclusion of grey literature might hurt the quality of primary studies." |
| Data | **TV11 — Lack of relationships.** Checklist: "Do you expect to identify relationships in your dataset?" | "Examining data that lack relations might hinder reaching a conclusion." | Data extraction; Data analysis | MA1: "Have you performed pilot data extraction to test the existence of relationships?" (Fig. 3b: "MA1: Pilot data extraction"). Also: "A tentative solution to this threat is the application of quality assessment as a criterion for study inclusion or exclusion" — Nguyen-Duc et al. "assessed the quality of the studies in terms of rigor, credibility, and relevance by using the checklist of Dyba and Dingsoyr [21]"; alternative schema by Ivarsson [26] — "rigor is evaluated based on the description of the context, the empirical design, and the validity discussion … relevance is assessed based on subjects, context, scale, and used research method". |
| Data | **TV12 — Validity of primary studies.** Checklist: "Does the quality of studies guarantee the validity of extracted data?" | "Another type of publication bias is the Validity of the primary studies, which suggests that the results of the secondary study might be biased from inaccurate results reported in the primary studies. A common reason for this is that studies with negative results are less probable to get accepted for publication." | Study selection → damages Data extraction/analysis (classified under Data Validity) | MA1: "Have you focused your search process on quality venues only?" · MA2: "Have you used article quality assessment as inclusion criterion?" · MA3: "Have you assessed the validity of primary studies and their impact using statistics?" (Fig. 3b: "MA1: Only quality venues", "MA2: Quality assessment", "MA3: Assess the validity using statistics"). Stated most-common pair: "(a) the use of quality thresholds as an exclusion criterion [1] (e.g., rigor and relevance checklist [21], [26]), and (b) the inclusion of high-quality venues, based on well-defined criteria [29]". |
| Data | **TV13 — Data extraction bias** (group). Checklist: "Is there data extraction bias in your study?" | "Data extraction bias refers to problems that can arise in the data extraction phase. Such problems might be caused from the use of open questions in the collected variables, whose handling is not explicitly discussed in the protocol. The specific threat to validity is one of the most common ones in software engineering." | Data extraction | MA1: "Have you involved more than one researcher?" · MA2: "Have you identified experts' disagreement with kappa statistic?" · MA3: "Have you performed pilot data extraction to test agreement between researchers? (Not applicable if MA1 is no)" · MA4: "Have you used experts or external reviewers' opinion in case of conflicts? (Not applicable if MA1 is no)" · MA5: "Have you performed paper screening to cross-check data extraction?" · MA6: "Have you used a keywording of abstracts? (Applicable only in mapping studies)" (Fig. 3b: "MA1: Involve more than one researchers", "MA2: Use kappa statistic", "MA3: Pilot data extraction", "MA4: Use expert's opinion", "MA5: Random paper screening", "MA6: Perform keywording of abstracts"). Most common named: "(a) the involvement of more than one researcher in the process and the continuous assessment of their level of agreement (e.g., using Fleis's kappa [43]), (b) the piloting through random sampling [28], and (c) the use of keywording from abstracts [45]." |
| Data | **TV13.1 — Data extraction bias** (sub-threat) | See TV13. | Data extraction | As TV13. |
| Data | **TV13.2 — Quality assessment subjectivity** | "A special type of data extraction bias is the Quality assessment subjectivity i.e., the process during which the quality of the primary studies is evaluated by the authors of the secondary study. This threat is relevant only for SLRs that report the evaluation of primary studies' quality." | Data extraction (or Study filtering — see grey-zone note) | As TV13 ("Since all the above threats fall in the generic data extraction bias threats, their mitigation can be achieved by applying the same mitigation actions."). |
| Data | **TV13.3 — Data extraction inaccuracies** | "Data extraction inaccuracies, refer to cases when data analysis might not be carefully performed, or might not follow strict guidelines. For example, the same concept might be inconsistently classified into two primary studies. This leads to inaccuracies in the dataset." | Data extraction | As TV13. |
| Data | **TV13.4 — Unverified data extraction** | "unverified data extraction refers to the situation in which data are not validated by external reviewers, or have not been subject to internal review." | Data extraction | As TV13. |
| Data | **TV13.5 — Misclassification of primary studies** | "Primary studies inconsistent classification is valid for secondary studies that aim at developing a classification schema (usually mapping studies)." Fig. 3b names it "Misclassification of studies"; §2.1 notes it is "mostly relevant for mapping studies". | Data extraction | As TV13; and see TV15 actions. |
| Data | **TV14 — Lack of statistical analysis.** Checklist: "Have you performed statistical analysis?" | "In some designs it is not possible to perform statistical analysis. For example, in cases that all extracted data items are categorical." | Data analysis | MA1: "Does your data extraction record quantitative data and if yes, does answering your research questions imply the use of statistics?" (Fig. 3b: "MA1: Check for quantitative data"). Also: "This threat can be mitigated during the selection of variables to be extracted, when the selection of numerical data can be opted … Nevertheless, as noted by Engström [22], qualitative data analysis methods are equally important to quantitative analysis. Therefore, using solid qualitative analysis methods mitigates the lack of statistical analysis." |
| Data | **TV15 — Bias of Classification Schema** (group). Checklist: "Have you selected a robust initial classification schema?" | Group of "threats that are relevant for mapping studies and have been posed by the use of inadequate classification schemas or attributes frameworks (TV15)." | Study selection (first appears) → impact in Data analysis | MA1: "Have you selected an existing initial classification schema?" · MA2: "Have you continuously updated the schema, until it becomes stable and classifies all primary studies in one or more classes?" (Fig. 3b: "MA1: Use existing schemas", "MA2: Continuous update") |
| Data | **TV15.1 — Robustness of initial classification** | "In case a classification schema is already in place, Robustness of initial classification is applicable to secondary studies that rely upon it. … The selection of this initial classification schema poses a threat to validity, since it might not be fitting for the domain, and its tailoring is not efficient." | Study selection → Data analysis | "(a) the piloting of data extraction to test the classification schema or the attribute framework—Cornelissen et al. [16] evaluated the usefulness of the attribute framework and measured the degree to which the attributes in each facet coincide; (b) the use of an existing and established classification schema—e.g., Hasselberger et al. [25] used the project manager competence development framework; (c) the use of experts' opinion—Kosar et al [35] have relied upon the opinion of a DSL expert for obtaining a coarse-grained classification that could offer a broader picture of the field." |
| Data | **TV15.2 — Construction of attribute framework** `[Fig. 3b mislabels this second sub-threat "TV15" rather than TV15.2.]` | "A similar threat is the Construction of attribute framework. While constructing this framework, the authors define a set of possible values for the attributes (i.e., variables) that are used to characterize each primary study. If the selected values are not discrete and comprehensive then the data extraction can result to an insufficient dataset." | Study selection → Data analysis | As TV15.1. |
| Data | **TV16 — Researcher bias.** Checklist: "Is your interpretation of the results subject to bias or is it as objective as possible?" | "Researcher bias refers to potential bias that authors of the secondary studies may have, while interpreting or synthesizing the extracted results. This can be a bias towards a certain topic, or because only one author worked on data synthesis." | Data analysis | MA1: "Have you performed pilot data analysis and interpretation?" · MA2: "Have you conducted reliability checks (e.g., post-SLR surveys with experts)?" · MA3: "Have you used a formal data synthesis method?" · MA4: "Have you performed sensitivity analysis?" · MA5: "Have you used the scientific quality of primary studies when drawing conclusions?" (Fig. 3b: "MA1: Pilot data analysis", "MA2: Conduct reliability checks", "MA3: Use formal data synthesis", "MA4: Perform sensitivity analysis", "MA5: Use scientific quality of primary studies when drawing conclusions"). Also: "vivid discussion among authors of the studies is encouraged … Nair et al. [42] advise the execution of reliability checks, the execution of pilot interpretations are proposed by Khurum et al. [30], whereas Penzenstadler et al. compare results with existing studies [44]." |

---

#### CATEGORY 3 — RESEARCH VALIDITY (TV17–TV22)

| Category | Threat | Definition (verbatim) | Review phase affected | Mitigation actions (verbatim) |
|---|---|---|---|---|
| Research | **TV17 — Repeatability.** Checklist: "Is your process reliable/repeatable?" | "Repeatability refers to threats that deal with the replication of a secondary study. The most common reason for the existence of such threats is the lack of a detailed protocol, or the existence of researcher and data extraction bias." Classification rationale: "repeatability (TV17) has been classified in this category since although it is threatened by data unavailability; it is also threatened by any undocumented parts of the reviewing process. Therefore, it is considered more as a horizontal threat (that pertains to the whole research process), rather than a specific threat for the data extraction or analysis phase." | All phases (horizontal) | MA1: "Have more than one researcher been involved in the process?" · MA2: "Have you made all gathered data publicly available?" · MA3: "Have you documented in detail the review process in a protocol?" (Fig. 3c: "MA1: Involve more than one researchers", "MA2: Make data available", "MA3: Develop protocol"). Also: "The key practice for boosting the repeatability of a secondary study is the development and the public sharing of a review protocol … Other good practices are the involvement of more than one researcher in the process … and the adoption of well-known guidelines—most studies follow the guidelines of Kitchenham and Charters [31] or of Petersen et al. [45]." |
| Research | **TV18 — Research Method Bias** (group). Checklist: "Have you chosen the correct research method?" | "First, there is a possibility that the selected research method (i.e., mapping study vs. literature review) does not fit the goal of the study (TV18). Second, sometimes researchers deviate from the established review process." | Planning (protocol definition); All phases | MA1: "Have the authors discussed if the selected research method (SLR or SMS) fits the goals/research questions of the study, by advocating the purpose and scope of the methods?" · MA2: "Have you developed a protocol, monitored the process for deviations, and accurately reported any (if existed)?" (Fig. 3c: "MA1: Discuss among authors", "MA2: Develop protocol") |
| Research | **TV18.1 — Chosen research method** | "Chosen research method. Mapping studies and literature reviews are designed to serve different goals and scopes. The selection of a specific research method might not fit the goals, the scope, or the context of the performed secondary study." | Planning | As TV18. "A discussion on the proper way for selecting the research method for a secondary study is provided by Kitchenham et al. [32]. For example, broad topics should be approached through mapping studies, whereas more specialized ones through SLRs." |
| Research | **TV18.2 — Review process deviation** | "Review process deviations. In some cases researchers choose to deviate from the guidelines offered by the research method. Such deviations (e.g., not performing the keywording of abstracts step in a mapping study, despite the use of the guidelines of Petersen [45]) threaten validity, since some important aspects might be compromised. In such cases a strong argumentation should be set." | All phases | As TV18. Exemplar: "Galster et al. [23], deviated from the data extraction guidelines of Kitchenham and Charters [31] and adopted the strategy suggested by Brereton et al. [13]." |
| Research | **TV19 — Coverage of research questions.** Checklist: "Do the answers to your research questions guarantee the accomplishment of your study goal?" | "Coverage of Research Questions refers to the formulation of research questions that do not adequately fulfill the goal of the secondary study. Possible reasons are setting a very generic goal, or the improper decomposition of the goal into questions." | Planning (define the need / define the protocol) | MA1: "Have the authors discussed and brainstormed on if the research questions holistically cover the goal of the study?" · MA2: "Is your study and research questions well-motivated?" · MA3: "Have you consulted target audience for setting up your goals?" (Fig. 3c: "MA1: Brainstorming", "MA2: Motivate well research questions", "MA3: Consult target audience"). **Key cross-link to GQM:** "The most common best practice for resolving this threat is the use of the GQM approach that has been introduced by Basili et al. [12]. Also, brainstorming among authors [5] and the consultation of experts [4] are highly advisable." |
| Research | **TV20 — Lack of comparable studies.** Checklist: "Does your study have substantial related work, so that you can compare and discuss findings?" | "Some secondary studies lack comparable related work (i.e., other secondary studies or primary studies). In this case there is no possibility of comparing the results to existing literature." | Data analysis; Reporting | MA1: "Have the authors discussed and brainstormed to reach possible interpretations of the findings, due to the absence of related studies?" (Fig. 3c: "MA1: Brainstorming"). "Therefore, in our opinion, the only option is the intuitive validation and discussion of the obtained results. A best practice for this is the brainstorming between the authors and possible external experts." |
| Research | **TV21 — Unfamiliar with research field.** Checklist: "Were you familiar with the research field before performing the review?" | "In some cases secondary studies are performed by non-expert researchers that are unfamiliar with the research field. The lack of knowledge in the domain can lead to undesired consequences, such as: omission of well-known studies in the field, limited synthesis capacity, inability to reason about the findings, etc." | All phases (esp. Planning and Data analysis) | MA1: "Have the authors exhaustively searched related work so as to: (a) familiarize with the field, (b) identify comparable studies, and (c) identify relevant publication venues and influential papers?" (Fig. 3c: "MA1: Compare with related work"). "According to Mc Donnell [38] senior researchers should be included in the data analysis and interpretation of the results of secondary studies." |
| Research | **TV22 — Generalizability** (group). Checklist: "Are the results of your study generalizable?" | "Generalizability threats refer to the possibility of not being able to generalize the results of the secondary study (for example due to the identification of only a portion of existing primary studies)." | All phases | MA1: "Do your findings comply with those of existing studies?" · MA2: "Have you used a broad search process w/o an initial starting date?" (Fig. 3c: "MA1: Use a broad search", "MA2: Compare with existing studies") |
| Research | **TV22.1 — Generalizability** (sub-threat) | See TV22. | All phases | As TV22. |
| Research | **TV22.2 — Research not applicable to other domains/organizations** | "A special case of this threat that is quite frequently reported is Results not applicable to other organizations or domains." | All phases | "The mitigation actions that have been linked to generalizability threats are the use of broad searches [19], and the comparison to state-of-the art and related studies [53]." |

---

### Mapping of threats to review phases

Two explicit mappings are given.

**(a) Category → phase (Fig. 2 "Secondary Studies Phases and Corresponding Threats").** The pipeline is:

```
Search process → Study filtering → Data Extraction → Data Analysis
 (set of candidate  (set of included   (populated       (classification
  studies)           studies)           dataset)         schema)

|-- Threats to study selection validity --|-- Threats to data validity --|
|------------- Threats to research validity (spans all phases) ----------|
```

**(b) Mitigation action → activity of the secondary study process (Fig. 4).** The paper assigns every
mitigation action to a step of Kitchenham & Charters' process. Codes are `<threat id>.<mitigation id>`.
Reproduced in full:

**PLANNING PHASE**

| Step | Activity | Mitigation actions assigned |
|---|---|---|
| 1. Define the need | Motivate the study | 19.2 Motivate the need of the study/ RQs; 21.1 Search exhaustively related work |
| 2. Define the review protocol | Define the goal of the study | 19.3 Consult target audience to define questions; 19.2 Motivate the need of the study/ RQs |
| 2. Define the review protocol | Define the research method | 18.1 Select Research Method (SLR, MS); 21.1 Search exhaustively related work; 18.2 Define the process of handling/ reporting deviations |
| 3. Review the protocol | Review study goals | 19.1 Discuss/brainstorm if research questions cover holistically the goal of the study |
| 3. Review the protocol | Review protocol | 17.1 Involve more than one researchers in the review process; 17.3 Document in detail the review process in the protocol |

**CONDUCTING PHASE**

| Step | Activity | Mitigation actions assigned |
|---|---|---|
| 1. Identify Research | Generate Search strategy | 1.6 Use a specific strategy for systematic search string construction; 1.1 Perform Snowballing; 1.2 Perform pilot searches to train search string |
| 1. Identify Research | Develop the search | 1.5 / 22.2 Use broad search process in generic search engines w/o start date; 1.3 / 12.1 / 8.2 Search known DLs/ broad search engines/ specific high quality publication venues |
| 1. Identify Research | Document the process | 1.9 Evaluate results/ Document outcomes; 1.8 Use tools to support the review process; 1.10 Use tools for bibliography management |
| 1. Identify Research | Evaluate the search | 1.9 Evaluate results/ Document outcomes; 1.4 Compare to gold standard/ other secondary studies; 1.7 Independent experts review the search process |
| 2. Study selection | Define inclusion/exclusion criteria | 7.5 Do pilots and revise criteria or use independent expert's suggestions; 7.6 Prescribe a set of decision rules; 12.2 Perform quality assessment |
| 2. Study selection | Manage duplicate articles | 5.2 Use summaries of studies to identify duplicates; 5.1 Develop a strategy (keep newer or journal version) |
| 2. Study selection | Handle work in other languages or with missing text | 3.1 / 4.1 Decide based on their number compared to population |
| 2. Study selection | Handle disagreements | 7.1 Use systematic voting; 7.3 Discuss criteria among authors |
| 2. Study selection | Evaluate the final set of studies | 7.2 Perform random screening of papers; 12.3 Evaluate the quality of studies using statistics; 2.1 If the studies are published in limited journals/ conferences use a broad search |
| 2. Study selection | Document the process | 7.4 Document inclusion/ exclusion criteria in the protocol |
| 3. Study Quality Assurance | Handle Grey literature | 6.1 Decide based on the goal of the study and the availability of sources |
| 3. Study Quality Assurance | Assess the completeness of the final set (if the studies in the data set are published in a limited set of venues) | 10.1 Perform snowballing; 10.2 Include grey literature; 10.3 Scan manually selected venues |
| 3. Study Quality Assurance | Assess Quality | 7.9 Assess the validity of primary studies using statistics `[EXTRACTION UNCLEAR: coded 7.9 in Fig. 4 but the checklist has only TV7 MA1–MA9 with MA9 = kappa statistic; this action corresponds to TV12 MA3]`; 7.7 Define quality thresholds; 7.8 Perform Sensitivity analysis |
| 4. Data Extraction | Define the data to be extracted | 9.1 Discuss the choice of variables among authors; 11.1 Perform pilot data extraction to test the existence of relationships |
| 4. Data Extraction | Perform data extraction | 13.1 Involve more than one researchers; 13.6 Use keywording of abstracts; 13.5 Perform paper screening to cross check data extraction; 17.2 Make all collected data publicly available |
| 4. Data Extraction | Handle disagreements (only if multiple researchers are involved) | 13.3 Perform pilot data extract. to test researchers agreement; 13.2 Identify expert's disagreement level with the kappa statistic; 13.4 Use experts or external reviewers opinion to handle conflicts |
| 5. Data Synthesis | Perform data synthesis | 16.3 Use a formal data synthesis method; 14.1 Perform statistical analysis if you have quantitative data; 15.1 Select an existing classification schema; 15.2 Continuously update the classification schema to be able to classify all primary studies |
| 5. Data Synthesis | Interpret the results objectively | 16.1 Perform pilot data analysis and interpretation; 16.2 Conduct reliability checks (i.e. post-SLR surveys); 16.4 Perform sensitivity analysis; 16.5 Take into consideration the quality of primary studies; 8.1 If the sample size of results is small draw conclusions based on trends; 22.1 / 20.1 Compare with related work, in case of absence of related work brainstorm among authors |

Note on the reporting phase:

> "We note that the reporting phase of the secondary studies is omitted since no threats can arise at that
> stage. However, the step is of paramount importance, in the sense that it includes the reporting of the
> threats to validity per se."

### Mitigation catalogue

The full per-threat mitigation lists are reproduced inside the three tables above (60 checklist actions,
TV1×9, TV2×1, TV3×1, TV4×1, TV5×2, TV6×1, TV7×9, TV8×2, TV9×1, TV10×3, TV11×1, TV12×3, TV13×6, TV14×1,
TV15×2, TV16×5, TV17×3, TV18×2, TV19×3, TV20×1, TV21×1, TV22×2; plus Fig. 4's "1.10 Use tools for
bibliography management"). Distinct *techniques* named across the catalogue, for quick reference:

snowballing (backward and forward) · pilot searches to train the search string · selection of well-known
digital libraries / venues / broad indices · comparison against a gold standard or other secondary studies ·
broad search in generic engines (Google Scholar, Scopus) · systematic search string construction (PICO) ·
independent expert review of the search process · review-support tools · bibliography-management tools
(JabRef, Zotero) · evaluation and documentation of search results · assessing non-English / inaccessible
paper counts against the population · emailing authors for inaccessible full texts · a consistent
duplicate-handling strategy (keep journal version / merge versions) · using article summaries to detect
duplicates · aligning the grey-literature decision with study goals · systematic voting · random paper
screening · discussion among authors on conflicts · explicit documentation of inclusion/exclusion criteria
in the protocol · revising criteria after pilots or expert review · prescribed decision rules · quality
thresholds for inclusion/exclusion · sensitivity analysis · Cohen's/Fleiss's kappa for reviewer
disagreement · drawing conclusions based on trends when the sample is small · mapping extracted variables
to research questions · a data extraction form derived from the research questions · manual scanning of
venues · quality assessment as an inclusion criterion (Dybå & Dingsøyr; Ivarsson & Gorschek rigor–relevance)
· assessing primary-study validity statistically · involving more than one researcher · pilot data
extraction · external reviewer/expert adjudication · keywording of abstracts (mapping studies) · checking
whether quantitative data exists before claiming statistical analysis · qualitative analysis methods as a
substitute for statistics · reusing an existing classification schema · continuous update of the schema
until stable · pilot data analysis and interpretation · reliability checks (post-SLR expert surveys) ·
formal data synthesis methods · weighting conclusions by primary-study scientific quality · public data
availability · a documented review protocol · adopting Kitchenham & Charters or Petersen et al. guidelines ·
explicit argumentation for method choice (SMS for broad topics, SLR for specialised) · documented and
reported process deviations · GQM for deriving research questions from the goal · brainstorming ·
consulting the target audience · exhaustive related-work search · comparison of findings with existing
studies · broad search without a starting date.

### Process steps or stages defined

**Author-side procedure for managing threats (§3, verbatim):**

> "First, the authors should create a dedicated section for threats to validity in both the study protocol
> and the study report (final manuscript). Second, this section should be organized according to categories
> of threats (e.g., by following the proposed classification schema or another established one). Third, all
> threats should be checked whether they pertain to the study. Finally, for all identified threats, either
> appropriate mitigation action should be explicitly reported or an acknowledgement should be made that the
> threat is not (fully) mitigated."

**Checklist structure (§2.2, verbatim):**

> "The structure of the checklist is quite simple: First each top-level question is asked to understand if a
> specific threat exists (TVn), and then a series of sub-questions are asked to check if a proper mitigation
> action MAm has been performed. The numbering of mitigation actions is restarted for every threat to
> validity."

**Reviewer/reader appraisal procedure (§4, verbatim):**

> "the evaluation of validity of a secondary study based on the classification schema and the checklist can
> be performed using two parts of the manuscript: (a) the threats to validity section, and (b) the study
> design section. We first examine if the threats are classified / organized into sensible categories in the
> threats to validity section. Subsequently we check if all threats to validity are discussed in the threats
> to validity section, or if some of them (or some mitigation actions) are only discussed while reporting
> the study design."

And the four reviewer actions (verbatim):

> "(a) to check whether more threats to validity pertain to their studies, preferably pointing out specific
> threats that the reviewers have identified; (b) suggest additional mitigation actions for the reported
> threats that seem more relevant to the study; (c) ensure that all identified threats are mitigated with at
> least one action; and (d) encourage them to report all the threats identified in the study design, also
> within the threats to validity section."

**Stakeholder usage scenarios (Fig. 1 / §1):** readers and reviewers perform "a critical appraisal of
secondary studies … by consulting the checklist to identify possible threats in the study design, and
confirm that they have been properly mitigated"; authors "can be guided on how to setup their study design,
so as to avoid or mitigate validity threats, while planning, conducting and reporting secondary studies."

### Caveats, traps and pitfalls

- **The core motivating pitfall — multi-label misclassification.** "Despite the fact that the percentage of
  secondary studies reporting threats to validity has been continuously increasing, considerable confusion
  still exists in terms of terminology, mitigation strategies, and classification [8] often leading to
  erroneous classification of threats. For instance, in many secondary studies any bias that might be
  introduced during study selection, is wrongly classified (by the authors of secondary studies) under
  internal validity almost as often as under reliability, pointing to inconsistencies in the classification
  of threats [8]. … While one can argue about the correctness of both classifications, multi-label
  classification can be confusing and does not allow for a uniform comparison of the threats."
- **Grey-zone threats persist.** "Although we believe that the current classification schema improves the
  orthogonality among threat categories, there are still some 'grey-zone' threats." Five named cases:
  - *Quality Assessment Subjectivity* — "the quality of a primary study can either be used as an inclusion
    criterion or as a variable that is collected during data extraction … Thus, Quality Assessment
    Subjectivity can be classified under both Study Selection Validity and Data Validity, based on the role
    of the quality assessment. To ease the readability of this section, Quality Assessment Subjectivity is
    presented only as part of Data Validity."
  - *Publication Bias* and *Validity of Primary Studies* — "Although Publication Bias and Validity of
    Primary Studies stem from the study selection phase, they threaten the validity of the extracted data,
    their analysis, and the subsequent interpretation. … Thus, we have classified both threats in the Data
    Validity category."
  - *Robustness of Initial Classification* and *Construction of Attribute Framework* — "These two threats
    are highly related to data validity in the sense that if a 'wrong' classification schema is selected the
    complete data collection will be misguided due to the use of inaccurate classification classes and
    terminology. Thus, the correctness of the final dataset is threatened. Although these threats first
    appear in the study selection phase their impact is mainly observed in the Data analysis phase."
- **Not all threats apply to all studies.** The checklist "can aid both in the identification of threats
  (since not all threats apply in all studies) and the suggestion of mitigation actions". A blank cell in
  Table 2 "implies that either the threat is not identified, or it does not apply to the specific secondary
  study."
- **Some threats are mutually exclusive** — see the digital-libraries vs. publication-venues rule quoted
  above; picking one search strategy excludes the other's threat, "except if a quasi-gold standard from
  specific venues is used for study selection validation; then both strategies are used."
- **Mitigations can themselves introduce threats.** On publication bias: "both these mitigation actions
  should be treated with caution, since in specific types of studies, they pose more significant threats to
  validity. For example, the inclusion of grey literature might hurt the quality of primary studies."
- **A starting year needs an argument, not a convention.** "In order for this decision to not be considered
  as a threat, it should be clear why such a choice does not influence the results. … If such a
  justification cannot be claimed researchers should consider shifting the starting year earlier."
- **Deviating from guidelines requires argumentation.** "In some cases researchers choose to deviate from
  the guidelines offered by the research method. Such deviations … threaten validity, since some important
  aspects might be compromised. In such cases a strong argumentation should be set."
- **Narrow scope may be legitimate.** "If the intended scope of the study is indeed narrow there might be no
  reason to mitigate this threat" (TV2); similarly for non-English papers, a threat "only in cases that a
  very active community publishes high-quality papers in a domain, in languages other than English."
- **THE headline misreporting trap — threats mitigated in the design but never reported as threats.**
  "80.7% of the mitigation actions of studies are only discussed as part of the study design and not the
  threats to validity section. Although the level of validity for the studies is high, the reporting of the
  threats is somehow limited. This hinders the evaluation of how threats to validity are considered and
  mitigated and undermines the overall validity of the studies."
- **Inconsistent classification even within one author group.** "even for studies that come from the same
  group of authors (or at least overlapping ones), the classification of the threats is not uniform, or it
  is sometimes completely omitted."
- **A custom schema is acceptable; an undefined one is not.** "Not all authors need to use an existing
  schema, but it is crucial that they thoroughly define the types of threats."
- **No threats arise at reporting, but reporting is where threats are declared** — see the Fig. 4 note above.

### Empirical findings worth citing

- **Reporting location:** "80.7% of the mitigation actions of studies are only discussed as part of the
  study design and not the threats to validity section."
- **Mitigation density:** "In very few cases a threat has been identified without applying any mitigation
  action, while often more than one action is applied to mitigate a given threat, which implies relatively
  good management of threats."
- **Sample sizes across existing secondary studies** (from the underlying tertiary study): "existing
  secondary studies parse from less than 10 papers to more than 500 primary studies. The mean value is 90
  primary studies, whereas 2.5% of our sample includes studies with less than 10 papers and 9.5% of the
  studies have considered more than 200 papers."
- **Most common threat named:** data extraction bias — "The specific threat to validity is one of the most
  common ones in software engineering. Therefore, a variety of mitigation actions have been linked to it."
- **Most frequently reported generalizability special case:** "Results not applicable to other organizations
  or domains" — "A special case of this threat that is quite frequently reported".
- **Classification practice in the 5 self-audited exemplars (Table 1, reproduced in full):**

| Study ID | Dedicated Section | Classification of Threats to Validity |
|---|---|---|
| [S1] Ampatzoglou & Stamelos 2010 | YES | No categorization |
| [S2] Ampatzoglou et al. 2013 | YES | Construct Validity (threats during study design); Internal Validity (threats occurring during data collection); External Validity (threats when generalizing to population); Conclusion Validity (possibly incorrect conclusions, e.g., missing relations, or wrongly extracted relations) |
| [S3] Galster et al. 2014 | NO | No categorization |
| [S4] Ampatzoglou et al. 2015 | YES | Threats to identification of primary studies; Threats to data extraction; Threats to generalization of results; Threats to conclusions |
| [S5] Arvanitou et al. 2017 | YES | No categorization |

- **Which threats those five studies actually addressed (Table 2, reproduced in full; cell = mitigation
  action code applied; ID = identified but not mitigated; blank = not identified or not applicable):**

| Checklist Question | [S1] | [S2] | [S3] | [S4] | [S5] |
|---|---|---|---|---|---|
| TV1: Has your search process adequately identified all relevant primary studies? | MA3, MA5 | MA3 | MA2, MA3, MA5, MA6, MA9 | MA2, MA3, MA4, MA6 | MA2, MA3, MA4, MA6 |
| TV2: Were primary studies relevant to the topic of the review published in several different journals and conferences? | MA1 | | MA1 | | |
| TV3: Have you identified primary studies in multiple languages? | | | | | |
| TV4: Were the full texts of all identified primary studies accessible from the researchers | | | | | |
| TV5: Have you managed duplicate articles? | MA1 | MA1 | MA1 | MA1 | MA1 |
| TV6: Have you included/excluded grey literature? | | | MA1 | | MA1 |
| TV7: Have you adequately performed study inclusion / exclusion? | MA3, MA4 | MA3, MA4 | MA2, MA3, MA4, MA5 | MA3, MA4 | MA3, MA4 |
| TV8: Is your sample size large enough so that the obtained results can be considered valid? | MA1, MA2 | MA1 | MA1, MA2 | MA1 | MA1 |
| TV9: Have you chosen the correct variables to extract? | | MA1 | MA1 | | |
| TV10: Are the primary studies in your dataset published in a limited set of venues? | | | | | ID |
| TV11: Do you expect to identify relationships in your dataset? | | | | | |
| TV12: Does the quality of primary studies guarantee the validity of extracted data? | | MA1 | MA1 | | MA1 |
| TV13: Is there data extraction bias in your study? | | MA1, MA2 | MA1, MA5 | MA1 | MA1 |
| TV14: Have you performed statistical analysis? | | | MA1 | | MA1 |
| TV15: Have you selected a robust classification schema? | MA1 | MA1 | | MA1 | |
| TV16: Is your interpretation of the results subject to bias or is it as objective as possible? | | ID | MA1 | MA1 | MA1 |
| TV17: Is your process reliable/repeatable? | MA1, MA2, MA3 | MA1, MA3 | MA1, MA3 | MA1, MA3 | MA1, MA2, MA3 |
| TV18: Have you chosen the correct research method? | | MA1 | MA2 | | |
| TV19: Do the answers to your research questions guarantee the accomplishment of your study goal? | MA2 | MA2 | MA2 | MA2 | MA2 |
| TV20: Does your study have substantial related work, so that you can compare and discuss findings? | | | | | |
| TV21: Were you familiar with the research field before performing the review? | MA1 | MA1 | MA1 | MA1 | MA1 |
| TV22: Are the results of your study generalizable? | MA2 | ID | MA2 | ID | |

Reading: TV3, TV4, TV11 and TV20 were addressed by none of the five; TV5, TV17, TV19 and TV21 by all five.

### Recommended further reading (as given, §5)

Three groups: (1) general empirical-SE threat categorisation — Cook & Campbell [15] as "a fitting starting
point", plus Wohlin et al. [57], Runeson et al. [48], Shull et al. [52]; (2) threat identification and
reporting in medical science — [10] Avellar et al. external validity, [20] Downs & Black, [40] PRISMA-P,
[51] AMSTAR, [55] the Delphi list — "since medical research is considered a more mature field in secondary
study design and execution and has already inspired the guidelines for conducting secondary studies in
software engineering"; (3) SE secondary-study guidelines — Budgen et al. [14], Cruzes & Dybå [17],
Kitchenham & Charters [31], Petersen et al. [45].

---

## Petersen & Gencel 2013 — Worldviews, Research Methods, and their Relationship to Validity in Empirical Software Engineering Research

Kai Petersen (BTH) & Cigdem Gencel (Free University of Bolzano/Bozen). IWSM–Mensura 2013, Ankara.

**Type:** framework (conceptual/position paper with a derived checklist)

**Role in corpus:** Only this paper explains *why* the classical Wohlin/Cook–Campbell four categories are
the wrong vocabulary for much SE research — by tying each validity classification to a philosophical
worldview — and proposes Maxwell's qualitative-research classification as the generic replacement that
covers mixed-method (pragmatist) SE work.

### THE VALIDITY FRAMEWORK — reproduced IN FULL

#### Step 1 — the four worldviews and what they imply

> "Philosophical worldviews (also referred to as philosophical worldviews or paradigms) refer to 'a basic
> set of beliefs that guide action' [1]. Four worldviews are distinguished, namely positivist (or
> post-positivist), constructivist (or interpretivist), advocacy/participatory, and pragmatist."

- **Positivist/post-positivist:** "seek an objective reality that exists 'out there' in the world. They hold
  a deterministic philosophy; that is, based on careful observations and measurements, they try to make
  inferences to a general truth." Post-positivists "have taken a worldview that evidence established in
  research is always imperfect and fallible. Therefore, they state that they do not prove a hypothesis, but
  indicate a failure to reject a hypothesis."
- **Interpretivist:** "seek for subjective reality, constructed by how human beings see and interpret the
  world in their respective context. So, truth is not absolute but relative in interpretism."
- **Advocacy/participatory:** "holds that research inquiry needs to be intertwined with politics and
  political agenda and contains an action agenda through intervention for reform that may change the lives
  of the participants."
- **Pragmatist:** "emphasise the research problem and using all approaches available to understand the
  problem, instead of focusing on the methods. … The pragmatists seek a truth that is 'what is practically
  useful and whatever works at the time'. Therefore, they are not committed to any philosophical view or
  reality, and therefore use mixed methods in their inquiries."

Choice of worldview is partly dictated by the object of study: "if a study is about people in an
organization, the interpretivist world view might dominate, while if the objects of the study is a software
product and some hypotheses are to be tested, a positivist world view is likely to dominate."

**Table I — Research Methods and Nature of Data in Different Worldviews (reproduced in full):**

| World views | Truth | Research method | Data collection |
|---|---|---|---|
| Positivist/Postpositivist | Objective (independent from participants) | Controlled experiment, case study, and survey | Quantitative (Random sampling) |
| Constructivist/Interpretivist | Subjective (constructed by participants) | Case study, survey, interview | Quantitative and Qualitative (Random and purposeful) |
| Advocacy/Participatory | Subjective (constructed by participants and the observer) | Action research (intervention driven) | Quantitative and Qualitative (Random and purposeful) |
| Pragmatist | Depends on what works at the time | Multi method research | Quantitative and Qualitative (Random and purposeful) |

#### Step 2 — THE CENTRAL TABLE: their classification vs. the classical categories

**Table II — Categorization of Threats Mapping With Respect to World Views (reproduced in full):**

| Category | Positivist (Cook [8], Wohlin et al. [7]) | Interpretivist (Lincoln and Guba [18]) | Advocacy/Participatory (Greenwood and Levin [19]) | Pragmatist (Runeson and Höst [9]) | Maxwell [17] |
|---|---|---|---|---|---|
| **C1** | Internal Validity | – | Uncontrollability | Internal Validity | Theoretical Validity |
| **C2** | External Validity | Transferability | Transcontextual | External Validity | External Generalizability |
| **C3** | Construct Validity | – | Contingency | Construct Validity | Theoretical Validity |
| **C4** | Conclusion Validity | – | – | – | Internal Generalizability |
| **C5** | – | Credibility | – | – | Descriptive Validity |
| **C6** | – | Confirmability | Subjectivity | Reliability | Interpretive Validity |

> "Threats in one row are similar in their meaning even though different terminologies are used in different
> world views."

**Table III — Validity Threat Definitions in Different Worldviews With Respect to Categories (reproduced in
full, verbatim):**

| Category | Term | Definition (verbatim) |
|---|---|---|
| C1 | Internal validity | "When the researcher is investigating whether one factor affects an investigated factor there is a risk that the investigated factor is also affected by a third factor. If the researcher is not aware of the third factor and/or does not know to what extent it affects the investigated factor, there is a threat to the internal validity. [7], [9]" |
| C1 | Uncontrollability | "The researcher does not usually have full control over that environment [20]" |
| C1 | Theoretical validity | "Refers to an accounts function as an explanation (as well as a description or interpretation, of the phenomena); that is, as a theory of some phenomenon. Any theory has two components: the concepts or categories that the theory employs, and the relationships that are thought to exist among these concepts [17]" |
| C2 | External validity | "This aspect of validity is concerned with to what extent it is possible to generalize the findings, and to what extent the findings are of interest to other people outside the investigated case. During analysis of external validity, the researcher tries to analyze to what extent the findings are of relevance for other cases. [7], [9]" |
| C2 | Transferability | "Transferability refers to the degree to which the results of qualitative research can be generalized or transferred to other contexts or settings. From a qualitative perspective transferability is primarily the responsibility of the one doing the generalizing. [18]" |
| C2 | Transcontextual | "Research outcome is intersection of environmental conditions, a group of people, and a variety of historical events, including the actions of participants [19]" |
| C2 | External Generalizability | "Refers to the extent to which one can extend the account of a particular situation or population to other other communities, groups, or institutions. [17]" |
| C3 | Construct Validity | "Refers to what extent the operational measures that are studied really represent what the researcher have in mind and what is investigated according to the research questions. [9]" |
| C3 | Contingency | "Inherent obstacles to isolation of evidence related to particular effects and constructs from the contextual 'glue' in which they are naturally found, given a vast amount of shallow information. [20]" |
| C3 | Theoretical validity | "Refers to an accounts function as an explanation (as well as a description or interpretation, of the phenomena); that is, as a theory of some phenomenon. [17]" |
| C4 | Conclusion validity | "Focus on how sure we can be that the treatment we used in an experiment really is related to the actual outcome we observed; that is whether the results are statistically significant [7]" |
| C4 | Internal Generalizability | "Generalizing within the community, group, or institution studied to persons, events, and settings that were not directly observed or interviewed [17]" |
| C5 | Credibility | "The credibility criteria involves establishing that the results of qualitative research are credible or believable from the perspective of the participant in the research. Since from this perspective, the purpose of qualitative research is to describe or understand the phenomena of interest from the participant's eyes, the participants are the only ones who can legitimately judge the credibility of the results. [18]" |
| C5 | Descriptive Validity | "Factual accuracy of the account that is, researchers are not making up or distorting the things they observed (interpretivist cognition – see, hear, smell etc where positivists measure using measurement instruments). [17]" |
| C6 | Confirmability | "Confirmability refers to the degree to which the results could be confirmed or corroborated by others. [18]" |
| C6 | Subjectivity | "The deep involvement of researchers with client organizations in Action Research studies may hinder good research by introducing personal biases in the conclusions. [20]" |
| C6 | Reliability | "Concerns to what extent the data and the analysis are dependent on the specific researchers. Hypothetically, if another researcher later on conducted the same study, the result should be the same. [9]" |

#### Step 3 — the per-category argument (why each category is or is not paradigm-specific)

- **C1 (internal / theoretical):** "deal with factors that might affect cause and effect relationships, but
  is unknown to the researcher. … In the case of the positivist worldview … the cause-effect refers to a
  statistically established relationship. However, in the cases of the interpretivist and critical theory
  worldview non-statistical inferences about data qualitative data are made, hence the threat still applies
  to them. … Thus, it is not justified to exclude the threat category in research planning with the argument
  that no statistical cause-effect relationships are to be established."
- **C2 (generalizability):** "Positivist studies … are based on random sampling and clear definition of
  populations. Hence, positivists are after being able to generalize from a sample to a population. … In
  interpretivist and action research studies generalizability has to be viewed differently. As Yin [10]
  points out, one should not talk about a sample of cases, given that one would not aim to generalize to a
  population. Instead, one would like to generalize to similar contexts, and find supporting cases and
  conflicting cases for theories, and by doing that being able to conduct cross-case comparison. … Hence,
  reporting context is very important to know which cases to compare … case studies should not be rejected
  due to that they represent only a single case, each case is an important contribution to learning."
- **C3 (construct / theoretical):** "concerned with whether we measured (e.g. quantitative measurement
  instrument) or captured (e.g. qualitatively in an interview), what we intend to in relation to our
  hypothesis or theory to test. This threat is equally relevant in all world views."
- **C4 (conclusion / internal generalizability):** "deal with the degree to which conclusions/inferences we
  draw … are reasonable. … This threat is not highlighted by all views, however, we believe that one should
  always consider threats in relation to whether the conclusions drawn are reasonable with respect to the
  collected data."
- **C5 (credibility / descriptive validity):** "refers to validity threats related to factual accuracy of
  the account; that is, the researchers are not making up or distorting the things they observed and it is
  expected to produce descriptively same accounts/data for the same event or situation. One important
  comment of Maxwell [17] is that this validity concerns also issues of omission (no account can include
  everything, and we include/exclude/omit depending on the implicit theory we have.)."
- **C6 (confirmability / reliability / interpretive validity):** "concerns with whether the
  inferences/conclusions follow from the account (data), not biased by the researchers during analysis.
  Maxwell [17] claims that this category is not so much relevant to quantitative studies, but to qualitative
  studies as the methods used are more apt to this types of threat when the researchers make interpretations
  about the data."

#### Step 4 — the demotion of reliability/repeatability

> "There are also other validity threats categories defined in the literature such as Reliability [10] (in
> positivist case studies) or Dependability [18] in qualitative research. These actually concern with
> repeatability or reproducability in research (i.e., whether we would obtain the same results if we could
> observe the same thing twice). For these threats, we agree with Maxwell's point of view [17] that they do
> not refer to an aspect of validity or separate issue of validity, but a particular type of validity that
> arise in relation a number of validity threat categories defined above."

Repeatability is therefore drawn in Fig. 1 as *following from* the other four, justified by three examples:

> "• If we do not have a means to draw conclusions from the data (interpretative validity), we will very
> likely draw different conclusions assuming we could repeat the research. • If we are not aware of
> generalizability, we can not repeat the study in different contexts and compare (e.g. due to not knowing
> about the context) • If we do not have means to collect correct data, we are likely to get different
> results when measuring the same attribute."

#### Step 5 — the recommended classification (Fig. 1, "Pragmatic Software Engineering View")

Four top-level categories under the **PRAGMATIST VIEW**, each with its guiding question verbatim:

| Category | Guiding question (verbatim from Fig. 1) |
|---|---|
| **DESCRIPTIVE VALIDITY (FACTUAL ACCURACY)** | "Could we describe the objective/subjective truth accurately?" |
| **THEORETICAL VALIDITY** | "What are confounding factors (uncontrollability)? Do we capture what we intend to capture?" |
| **GENERALIZABILITY** | "To what degree can we generalize results?" — split into **INTERNAL** ("Within groups/communities/a company") and **EXTERNAL** ("Across groups/communities/companies") |
| **INTERPRETIVE VALIDITY (OBJECTIVE RESEARCHER)** | "Are the conclusions/inferences drawn reasonable given the data representing an objective/subjective truth?" |
| *(derived)* **REPEATABILITY (REPRODUCIBILITY/DEPENDABILITY)** | "Data and analysis methods/instruments should be defined and enable repeatability" — labelled "Follows from the above" |

**Why Maxwell, stated verbatim:**

> "Maxwell's classification has been chosen for two reasons: 1) The threat categories are defined generic
> enough to capture the different philosophical worldviews, i.e. they can apply to more quantitative, as
> well as qualitative research. … and 2) The terminology of the threat categories is more intuitive, with
> terms such as theoretical validity, interpretative validity, and descriptive validity, and
> generalisability."

And: "all four validity threats raised by Wohlin et al. [7] for experiments and by Greenwood and Levn [19]
for action research are covered by Maxwell [17]. As for the categories by [9], only reliability is not
included due to the reasons we just stated. Similarly, dependability [18] is not included. In addition,
Maxwell added two more categories: descriptive validity and interpretive validity in his categories."

### Mapping of threats to review phases

Petersen & Gencel use **two research phases**, not the four secondary-study phases:

> "We distinguish two main phases in research to identify relevant validity threats (1) data collection, and
> (2) data analysis. Design of data collection and analysis procedures are considered under each phase to
> avoid confusion. That is, generalizability, theoretical validity, and descriptive validity are relevant
> and have to be considered both in the design of the data collection procedures as well as during the
> collection of the data. Then, when the data is collected, interpretative validity and generalisability
> comes into play in the analysis of the results."

**Figure 2 — World Views × Research Process × Validity Threats (reproduced in full).**
Phase 1 = **Data Collection** ("record, store, review, and revise"); Phase 2 = **Data Analysis**
("interpret, report, review, and revise"). The Pragmatist column reads, for both phases, "Combinations of
the views, depending on how research stances are combined (multi-method)".

**Data Collection phase**

| Category | Positivist | Interpretivist | Participatory (Critical Theory) |
|---|---|---|---|
| Theoretical Validity | Reliability of measures; Reliability of treatment implementation; Heterogeneity of subjects; Constructs (e.g. theory) not well defined, unclear; Mono-method bias (use single measure); Evaluation apprehension; Selection of subjects; Ambiguity about direction of causal influence; History affects results; Maturation (behavior change over time); Poor instrumentation for data collection; Compensatory rivalry between subjects with different treatments; Researcher expectations | Constructs (e.g. theory, object of study) not well defined, unclear; Mono-method bias; Evaluation apprehension; Selection of subjects; Ambiguity about direction of inferences derived from data; History affects results; Maturation (behavior change over time); Poor instrumentation for data collection | Constructs (e.g. theory, object of study) not well defined, unclear; Mono-method bias; Descriptive accuracy; Selection of subjects; Ambiguity about direction of inferences derived from data; History affects results; Maturation (behavior change over time); Learning effects; Poor instrumentation for data collection; political and social threats; Resistance of change; few iterations |
| Generalizability | Interaction of selection and treatment; Interaction of setting and treatment; Interaction of history and treatment | Saturation, i.e. non-purposeful selection study context/questions | Saturation, i.e. non-purposeful selection study context/questions |
| Descriptive Validity | — | poor recording of data; too many steps of interpretation | poor recording of data; too many steps of interpretation |

**Data Analysis phase**

| Category | Positivist | Interpretivist | Participatory (Critical Theory) |
|---|---|---|---|
| Interpretative Validity | Low stat. power; Invalid assumptions of stat. tests | Researcher bias in drawing conclusions | Researcher bias in drawing conclusions; Researcher suffers from organizational/contextual blindness |
| Generalizability | — | Lack of context definition and awareness in interpretation | Lack of context definition and awareness in interpretation |

Per-worldview commentary (verbatim highlights):

- *Positivist:* "The threats of the positivist view are all related to quantitative measures used in
  hypotheses testing. Therefore, reliability of measures and reliability of treatment implementation are of
  particular relevance. … Generalizability here is focused on generalizing the sample to the defined
  population, while in the other world views sampling has to be purposeful … Furthermore, interpretative
  validity is different due to that the conclusions follow from the results of the statistical analysis,
  hence statistical power and assumptions of statistical tests are emphasized over researcher bias, or the
  researchers' contextual blindness."
- *Interpretivist:* "Given the vast amount of qualitative information gathered, the threat [descriptive
  validity] is more significant, and it is more challenging to capture all relevant information (e.g. in
  observations or interviews without recording). Also, the interpretation of field data in interpretivist
  studies might be influenced by researcher bias. Even though the interpretivist worldview highlights
  subjective truth, this only refers to the truth of the subjects being studied. The researcher should
  provide an objective interpretation of that subjective truth."
- *Critical theory:* "This raises some unique threats, such as political and social threats due to the very
  close engagement of the researcher in the research setting [19], and the number of iterations (also
  referred to as action research cycles) being of importance." Validity criterion quoted: "research outcomes
  are well-grounded if the focus of the inquiry, both in its parts and as a whole, is taken through as many
  cycles as possible, by as many group members as possible, with as many individual diversity as possible,
  and collective unity of approach as possible".
- *Pragmatism:* "this worldview considers truth what works at the time. This sentence could be interpreted
  as an alibi for conducting poor and invalid research, which of course must not be the case. … Given that
  … software engineering research is following the pragmatism worldview, all threats are potentially
  relevant in our research field."

### Mitigation catalogue

The paper deliberately does **not** supply one. Verbatim:

> "Besides identifying and improving the reporting, we also should identify countermeasures in future work.
> That is, when a relevant threat has been identified, research design decisions should be related to
> different threats, so that software engineering researchers have support in increasing the validity of
> their research."

The only mitigation-shaped prescriptions are procedural: report the worldview; separate design-of-collection
from design-of-analysis threats; and classify each threat as open / reduced / mitigated (below).

### Process steps or stages defined

**The four-question checklist (verbatim):**

> "1. Which of the world views you had when doing this research? a) Positivist b) Interpretivist c)
> Advocacy/Partcipatory d) Pragmatist
> 2. What type of research you are conducting (based on research questions) (see Table IV)?
> 3. Choose which research method(s) you used in your study (see Table V)? Note that the answer to this
> question should be consistent with choices on question 1. and 2.
> 4. Check which of the validity threat categories apply to your study for each phase. Figure 2 aids in
> identifying relevant threats with regard to world views."

**Table IV — Research Type (reproduced in full; √ = applicable):**

| Method | Descriptive | Exploratory | Explanatory | Improving |
|---|---|---|---|---|
| Case Study | √ | √ | √ | |
| Survey | √ | √ | | |
| Interview | √ | √ | | |
| Experiment | | | √ | |
| Action research | | | | √ |

`[EXTRACTION UNCLEAR: the √ marks in Table IV are misaligned in the plain-text extraction — the header row
carries four √ symbols before the method rows begin. The reading above is the most plausible reconstruction;
verify against the PDF before quoting cell-by-cell.]`

**Table V — Choice of Research Method (reproduced in full; √ = applicable):**

| Method | Positivist | Interpretivist | Critical Theory | Pragmatist |
|---|---|---|---|---|
| Case Study | √ | √ | | √ |
| Survey | √ | √ | | √ |
| Interview | | √ | | √ |
| Experiment | √ | | | √ |
| Action research | | | √ | √ |

`[EXTRACTION UNCLEAR: Table V's √ marks are also displaced by one row in the plain-text extraction; the
reconstruction above follows Table I's method–worldview assignments, which are unambiguous. Verify against
the PDF before quoting cell-by-cell.]`

**The three-way reporting taxonomy (verbatim) — the paper's most transferable prescription:**

> "Furthermore, all threats potentially relevant should be documented. If a threat is not reported, it can
> mean two things: Either the threat was addressed and hence not reported, or it was overlooked.
> Consequently, it would be useful to report:
> • **Open** threats that were not reduced or mitigated in the research design.
> • **Reduced** threats that are still of relevance, but countermeasures have been taken to address them.
> • **Mitigated** threats not of any relevance for the study, as they are completely mitigated by the design
> of the study, or the worldview taken."

And on structure: "Validity threats for design and conduct of data collection and analysis should be
reported separately, so that the countermeasures could be identified accordingly where they are needed in
the research process."

Overall recommended sequence (Conclusion, verbatim): "(1) choosing a world view for the research, (2)
choosing the type of research, and (3) choosing the method. These choices then guide which threats to
consider in the research in step (4)."

### Caveats, traps and pitfalls

- **The paradigm-mismatch rejection trap (the paper's central warning).** "a study should not be scored low
  (systematic review) or be rejected (peer review) for threats that are not of relevance for the worldview.
  A good example is the case study research method, which in some cases is rejected due to that only a
  single case is investigated, given that the objectivist view of sampling is applied. Though, as discussed
  earlier, this should be avoided given that case studies should be purposeful, rather than representative
  of a large population. A reason to reject a case might, for instance, be saturation (i.e. no new insights
  are gained). A pre-requisite for fair evaluations is hence an awareness of the different worldviews with
  respect to validity threats."
- **This has direct consequences for secondary studies:** "The presence of validity threats not addressed in
  research designs are often reasons to provide low quality scores to studies when aggregating evidence
  (e.g. in systematic reviews [23]), or to reject them in the peer review process." — i.e. quality-appraisal
  instruments used in SLRs can systematically penalise interpretivist primary studies.
- **Cross-worldview rejection:** "a researcher primarily following the positivist worldview might reject
  conclusions of a research conducted within a research community having different worldview, as the
  worldview determines how we evaluate concrete studies."
- **Existing categorisations are incomplete and inconsistent:** "we also identified that the established
  categories and definitions of validity threats is incomplete and there are some inconsistencies among
  them." And: "in software engineering so far the validity threats have been defined independently of the
  worldviews."
- **Silence is ambiguous.** "If a threat is not reported, it can mean two things: Either the threat was
  addressed and hence not reported, or it was overlooked." (This is the reason for the open/reduced/mitigated
  taxonomy.)
- **Pragmatism is not a licence.** "This sentence could be interpreted as an alibi for conducting poor and
  invalid research, which of course must not be the case. In particular, what works well at the time, and in
  which context, has to be based on high quality research."
- **Do not exclude C1 because you are not doing statistics.** "it is not justified to exclude the threat
  category in research planning with the argument that no statistical cause-effect relationships are to be
  established."
- **Descriptive validity includes omission**, not only distortion — "no account can include everything, and
  we include/exclude/omit depending on the implicit theory we have."
- **Self-declared incompleteness:** "It should be highlighted that we do not aim at providing a complete
  list of threats, but rather document the threats to make the difference between the worldviews explicit."
  Also: "In future work, the list can be completed by reviewing literature on specific research
  methodologies to identify threats unique to them."

### Empirical findings worth citing

None — this is a conceptual/position paper. The paper explicitly proposes such studies as future work: "we
propose to conduct systematic literature studies on validity threat reporting in different research areas,
and for different study types"; "It would also be of interest to review literature investigating which
worldview is dominant in different sub-disciplines of software engineering. Systematically investigating the
worldviews represented by studies would also empirically substantiate our argument that software
engineering represents the pragmatist worldview."

The one claim asserted (not measured): "Software engineering is dominated by the pragmatist worldviews, and
therefore use multiple methods in research."

---

## Basili, Caldiera & Rombach 1994 — The Goal Question Metric Approach

Victor R. Basili, Gianluigi Caldiera (U. Maryland), H. Dieter Rombach (U. Kaiserslautern).
Encyclopedia of Software Engineering article.

**Type:** guideline / paradigm definition

**Role in corpus:** Supplies the top-down goal→question→metric derivation mechanism that Ampatzoglou names
as the mitigation for TV19 (coverage of research questions) — i.e. the principled way to derive *what to
extract* in a secondary study from the study's stated goal, rather than choosing data items bottom-up.

### GQM (Basili) — the paradigm

**Founding assumption (verbatim):**

> "The Goal Question Metric (GQM) approach is based upon the assumption that for an organization to measure
> in a purposeful way it must first specify the goals for itself and its projects, then it must trace those
> goals to the data that are intended to define those goals operationally, and finally provide a framework
> for interpreting the data with respect to the stated goals."

**Why top-down (verbatim):**

> "This means that measurement must be defined in a top-down fashion. It must be focused, based on goals and
> models. A bottom-up approach will not work because there are many observable characteristics in software
> (e.g., time, number of defects, complexity, lines of code, severity of failures, effort, productivity,
> defect density), but which metrics one uses and how one interprets them it is not clear without the
> appropriate models and goals to define the context."

**Preconditions on effective measurement (verbatim, numbered):**

> "1. Focused on specific goals; 2. Applied to all life-cycle products, processes and resources;
> 3. Interpreted based on characterization and understanding of the organizational context, environment and
> goals."

#### The three levels of the measurement model (verbatim)

> "**1. Conceptual level (GOAL):** A goal is defined for an object, for a variety of reasons, with respect
> to various models of quality, from various points of view, relative to a particular environment. Objects
> of measurement are
> • **Products:** Artifacts, deliverables and documents that are produced during the system life cycle;
>   E.g., specifications, designs, programs, test suites.
> • **Processes:** Software related activities normally associated with time; E.g., specifying, designing,
>   testing, interviewing.
> • **Resources:** Items used by processes in order to produce their outputs; E.g., personnel, hardware,
>   software, office space.
>
> **2. Operational level (QUESTION):** A set of questions is used to characterize the way the
> assessment/achievement of a specific goal is going to be performed based on some characterizing model.
> Questions try to characterize the object of measurement (product, process, resource) with respect to a
> selected quality issue and to determine its quality from the selected viewpoint.
>
> **3. Quantitative level (METRIC):** A set of data is associated with every question in order to answer it
> in a quantitative way. The data can be
> • **Objective:** If they depend only on the object that is being measured and not on the viewpoint from
>   which they are taken; E.g., number of versions of a document, staff hours spent on a task, size of a
>   program.
> • **Subjective:** If they depend on both the object that is being measured and the viewpoint from which
>   they are taken; E.g., readability of a text, level of user satisfaction."

**Structure (verbatim):** "A GQM model is a hierarchical structure (Figure 1) starting with a goal
(specifying purpose of measurement, object to be measured, issue to be measured, and viewpoint from which
the measure is taken). The goal is refined into several questions … Each question is then refined into
metrics, some of them objective …, some of them subjective. The same metric can be used in order to answer
different questions under the same goal. Several GQM models can also have questions and metrics in common,
making sure that, when the measure is actually taken, the different viewpoints are taken into account
correctly (i.e., the metric might have different values when taken from different viewpoints)."

#### THE GOAL TEMPLATE — 1994 form (verbatim)

> "a goal has three coordinates:
>  1. Issue                   Timeliness
>  2. Object (process)        Change request processing
>  3. Viewpoint               Project manager
> and a purpose:
>  • Purpose                  Improve"

Instantiated (Figure 2/4, verbatim):

```
Goal    Purpose            Improve
        Issue              the timeliness of
        Object (process)   change request processing
        Viewpoint          from the project manager's viewpoint
```

**Three sources of information for filling the template (verbatim):**

> "The first source is the policy and the strategy of the organization that applies the GQM approach. From
> this source we derive both the issue and the purpose of the Goal by analyzing corporate policy statements,
> strategic plans and, more important, interviewing relevant subjects in the organization.
> The second source of information is the description of the process and products of the organization … From
> this source we derive the object coordinate of the Goal by specifying process and product models, at the
> best possible level of formality.
> The third source of information is the model of the organization, which provides us with the viewpoint
> coordinate of the Goal. Obviously, not all issues and processes are relevant for all viewpoints in an
> organization, therefore we must perform a **relevancy analysis** step before completing our list of goals,
> in order to make sure that the goals that we have defined have the necessary relevancy."

#### How QUESTIONS are derived — the three question groups (verbatim)

> "From the specification of each goal we can derive meaningful questions that characterize that goal in a
> quantifiable way. In general, we will ask at least three groups of questions:
>
> **Group 1.** How can we characterize the object (product, process, or resource) with respect to the
> overall goal of the specific GQM model?
> *Example:* "What is the current change request processing speed?"; "Is the (documented) change request
> process actually performed?"
>
> **Group 2.** How can we characterize the attributes of the object that are relevant with respect to the
> issue of the specific GQM model?
> *Example:* "What is the deviation of the actual change request processing time from the estimated one?";
> "Is the performance of the process improving?"
>
> **Group 3.** How do we evaluate the characteristics of the object that are relevant with respect to the
> issue of the specific GQM model?
> *Example:* "Is the current performance satisfactory from the viewpoint of the project manager?"; "Is the
> performance visibly improving?""

#### How METRICS are derived — the three selection factors (verbatim)

> "Once the questions have been developed, we proceed to associating the question with appropriate metrics.
> The factors we consider in doing this are many; among them:
> • **Amount and quality of the existing data:** we will try to maximize the use of existing data sources if
>   they are available and reliable;
> • **Maturity of the objects of measurement:** we will apply objective measures to more mature measurement
>   objects, and we will use more subjective evaluations when we deal with informal or unstable objects
> • **Learning process:** GQM models need always refinement and adaptation, therefore the measures we define
>   must help us in evaluating not only the object of measurement but also the reliability of the model used
>   to evaluate it."

#### The worked model (Figure 4, reproduced in full)

| Level | ID | Content |
|---|---|---|
| Goal | Purpose | Improve |
| | Issue | the timeliness of |
| | Object (process) | change request processing |
| | Viewpoint | from the project manager's viewpoint |
| Question | Q1 | What is the current change request processing speed? |
| Metrics | M1 | Average cycle time |
| | M2 | Standard deviation |
| | M3 | % cases outside of the upper limit |
| Question | Q2 | Is the (documented) change request process actually performed? |
| Metrics | M4 | Subjective rating by the project manager |
| | M5 | % of exceptions identified during reviews |
| Question | Q3 | What is the deviation of the actual change request processing time from the estimated one? |
| Metrics | M6 | (Current average cycle time − Estimated average cycle time) / Current average cycle time × 100 |
| | M7 | Subjective evaluation by the project manager |
| Question | Q4 | Is the performance of the process improving? |
| Metrics | M8 | Current average cycle time / Baseline average cycle time × 100 |
| Question | Q5 | Is the current performance satisfactory from the viewpoint of the project manager? |
| Metrics | M7 | Subjective evaluation by the project manager |
| Question | Q6 | Is the performance visibly improving? |
| Metrics | M8 | Current average cycle time / Baseline average cycle time × 100 |

### Process steps or stages defined

The GQM process, verbatim (§3):

> "A GQM model is developed by identifying a set of quality and/or productivity goals, at corporate,
> division or project level; e.g., customer satisfaction, on-time delivery, improved performance. From those
> goals and based upon models of the object of measurement, we derive questions that define those goals as
> completely as possible. … The next step consists in specifying the measures that need to be collected in
> order to answer those questions, and to track the conformance of products and processes to the goals.
> After the measures have been specified, we need to develop the data collection mechanisms, including
> validation and analysis mechanisms."

And: "Once a GQM model has been developed, we will select the appropriate data collection techniques, tools
and procedures. The data that will be collected will [b]e mapped into the model and interpreted according to
schemes previously defined by the organization."

Organisational embedding: "the development of GQM models is a task performed by the experience factory which
will use as inputs to the process the business driven goals provided by the corporate management and the
environment characteristics provided by the project team." Roles/flows in Fig. 5: Corporate Management
(Business-Driven Goals ↔ Quantifiable Targets) → GQM Definition Team (Core Competencies; produces Metrics &
Procedures) → Project Team (supplies Environment Characteristics, Data) → GQM Analysis Team → Experience
Base; with Corporate Feedback and Project Feedback loops. GQM Definition Team + Experience Base + GQM
Analysis Team constitute the **Experience Factory**; Project Team is the **Project Organization**.

### Caveats, traps and pitfalls

- "A bottom-up approach will not work" (quoted in full above) — the central trap.
- Metrics are meaningless without models: "which metrics one uses and how one interprets them it is not
  clear without the appropriate models and goals to define the context."
- Viewpoint changes values: "the metric might have different values when taken from different viewpoints."
- Relevancy analysis is mandatory: "not all issues and processes are relevant for all viewpoints in an
  organization, therefore we must perform a relevancy analysis step before completing our list of goals."
- Models must be chosen to match the issue: "if it is to characterize a software system … with respect to a
  certain set of quality issues (e.g., portability across architectures), then a quality model of the
  product must be chosen that deals with those issues."
- "GQM models need always refinement and adaptation."

### Empirical findings worth citing

No quantitative results. Deployment claim only: "it has been applied in several organizations, e.g., NASA,
Hewlett Packard [12], Motorola, Coopers & Lybrand." Origin: "The approach was originally defined for
evaluating defects for a set of projects in the NASA Goddard Space Flight Center environment."

---

## Basili 1992 — Software Modeling and Measurement: The Goal/Question/Metric Paradigm

Victor R. Basili, Institute for Advanced Computer Studies, University of Maryland. NASA/GSFC contract
NSG-5123 and AFOSR contract 90-0031. 24 pages.

**READABILITY: the PDF is a scanned image with no text layer (`basili_software_1992.txt` is a 24-byte
stub, and pdftotext yields nothing), but the pages were read successfully with the Read tool's vision on
the PDF directly, in two requests (pages 1–12 and 13–24). All 24 pages are legible. Content below is
transcribed from the page images.**

**Type:** guideline / paradigm definition (the long-form technical-report version of GQM; the 1994
encyclopedia article is the condensed form)

**Role in corpus:** This is the paper that carries the **full GQM goal-definition template with all five
purpose values and the environment coordinate** — which the 1994 article omits — plus the *guidelines for
generating questions* (product-related and process-related question sets) that turn a goal into a concrete
extraction form. It is the operational source for "how do I derive what to extract".

**Abstract (verbatim):** "This paper discusses the use of the Goal/Question/Metric paradigm as a mechanism
for defining and interpreting software measurement. Templates are provided for defining goals and generating
questions. Different types of metrics are discussed. Examples of both process and product goals are
defined."

### GQM (Basili) — the paradigm

**The three requirements (verbatim):** "For an organization to measure in a purposeful way requires that it
(1) specifies the goals for itself and its projects, (2) traces those goals to the data that are intended to
define these goals operationally, and (3) provides a framework for interpreting the data understand the
goals."

**Definition (verbatim):** "The Goal/Question/Metric paradigm is a mechanism for defining and evaluating a
set of operational goals, using measurement. It represents a systematic approach for tailoring and
integrating goals with models of the software processes, products and quality perspectives of interest,
based upon the specific needs of the project and the organization." And: "The goals are defined in an
operational, tractable way by refining them into a set of quantifiable questions that are used to extract
the appropriate information from the models. The questions and models, in turn, define a specific set of
metrics and data for collection and provide a framework for interpretation."

Same top-down insistence as 1994: "Measurement must be defined in a top down fashion, bottom-up approach
won't work."

#### THE GOAL DEFINITION TEMPLATE — reproduced verbatim (this is the canonical five-slot template)

> "Goals may be defined for any object, for a variety of reasons, with respect to various models of quality,
> from various points of view, relative to a particular environment. The goal is defined by filling in a set
> of values for the various parameters in the template. Template parameters include purpose (what object and
> why), perspective (what aspect and who) and the environmental characteristics (where).
>
> ***Purpose:***
> Analyze some
>   (objects: processes, products, other experience models)
> for the purpose of
>   (why: **characterization, evaluation, prediction, motivation, improvement**)
>
> ***Perspective:***
> with respect to
>   (focus: cost, correctness, defect removal, changes, reliability, user friendliness,...)
> from the point of view of
>   (who: user, customer, manager, developer, corporation,...)
>
> ***Environment:***
> in the following context
>   (problem factors, people factors, resource factors, process factors,...)
>
> **Example:** Analyze the (system testing method) for the purpose of (evaluation) with respect to a model of
> (defect removal effectiveness) from the point of view of the (developer) in the following context: the
> standard NASA/GSFC environment, i.e., process model (SEL version of the waterfall model,...), application
> (ground support software for satellites), machine (running on a DEC 780 under VMS), etc."

**Explanation of each slot (verbatim):**

- *Purpose:* "The purpose is meant to define the object or objects of study, what we are going to do and why
  we are doing it. There may be several objects and we may be doing it for several purposes. It is clear
  that the author must avoid complex objectives. In some cases it may be wise to break a complex goal into
  several simpler goals."
- *Perspective:* "The perspective is meant to define a particular angle or set of angles for evaluation. The
  author may choose more than one model, e.g. defects and changes, and more than one point of view, e.g.,
  the corporation and the project manager. The author should define the model and put himself/herself in the
  mind set of the person who wants to know the information so that all aspects of the evaluation are
  performed from that point of view."
- *Environment:* "The purpose of the environment is to define the context of the study by defining all
  aspects of the project so it can be categorized correctly and the appropriate set of similar projects
  found as a basis of comparison. Types of factors include: process factors, people factors, problem
  factors, methods, tools, constraints, etc. … In general, the environment should include all those factors
  that may be common among all projects and become part of the data base for future comparisons. Thus the
  environmental factors, rather than the values associated with these factors, should be consistent across
  several goals within the project and the organization."

**Ordering rule for defining a goal (verbatim):**

> "There is an order to defining a goal. For example, first one decides upon the object of study. It is
> assumed that there exists an appropriate model of that object. Then one determines why that object is
> being studied. For example, if it is to characterize the object, then all that is required is a set of
> models of the characteristics of interest. If the reason is to evaluate the object with respect to a
> certain set of qualities, then an evaluative model must be chosen along with an evaluation algorithm. In a
> sense, the why limits the set of focus models available. The focus model is chosen in the context of the
> who, i.e. the focus may change if the who is the project manager, requiring immediate feedback, versus, if
> the who is the corporation and a long range evaluation might be acceptable."

#### GUIDELINES FOR GENERATING QUESTIONS — the two question-generation schemes

> "Different sets of guidelines exist for each of the different objects of study, i.e., there are
> product-related and process-related questions based upon product and process models."

**PRODUCT-related questions (verbatim):**

> "For each product under study there are three major areas that need to be addressed: (1) definition of the
> product (purpose), (2) definition of the quality perspectives of interest (perspective), and (3) feedback
> related to the quality perspectives of interest.
>
> **(1) Definition of the product** defines a model of all those aspects that characterize the particular
> product under study. It includes questions related to:
> - *logical/physical attributes* (a quantitative characterization of the product in terms of the logical
>   attributes such as function, application domain, etc. and physical attributes such as size, complexity,
>   etc.),
> - *cost* (a quantitative characterization of the resources expended related to this product in terms of
>   effort, computer time, etc.),
> - *changes and defects* (a quantitative characterization of the errors, faults, failures, adaptations, and
>   enhancements related to this product), and
> - *context* (a quantitative characterization of the customer community using this product and their
>   operational profiles).
>
> **(2) The quality perspectives of interest** are based upon the focuses of interest for the product. The
> perspective should be based upon some model of the product that provides a framework for measurement. The
> models used here may be mathematically tractable models or qualitative models. Quality perspectives of
> interest (e.g., reliability, user friendliness), include questions related to
> - the *major model(s) used* (a quantitative specification of the quality perspective of interest),
> - the *validity of the model* for the particular environment (an analysis of the appropriateness of the
>   model for the particular project environment),
> - the *validity of the data* collected (an analysis of the quality of data), and optionally,
> - a *substantiation of the model* (an alternative model to help evaluate whether the results of the
>   primary model are reasonable).
> This last option is taken when there is some concern about the validity of the primary model or the data.
>
> **(3) Feedback** includes questions related to improving the product relative to the quality perspective of
> interest (a quantitative characterization of the product quality, major problems regarding the quality
> perspective of interest, and suggestions for improvement during the ongoing project as well as during
> future projects). It should also include things learned with regard to process, application and other
> products based upon what we have learned here."

Plus the completeness check: "Feedback very often requires reference to other factors not explicitly
mentioned in the definition of the product or perspective. In these cases it should be checked that these
factors exist either in the environment section … or in the definition of the product section."

**PROCESS-related questions (verbatim):**

> "For each process under study, there are three major areas that need to be addressed: (1) definition of
> the process, (2) definition of the quality perspectives of interest, and (3) feedback from using this
> process relative to the quality perspective of interest.
>
> **(1) Definition of the process** includes questions related to
> - *process conformance* (a quantitative characterization of the process and an assessment of how well it
>   is performed), and
> - *domain conformance* (a quantitative characterization of the object to which the process is applied and
>   an analysis of the process performer's knowledge concerning this object and its domain by the process
>   performers).
>
> **(2) Quality perspectives of interest** follows a pattern similar to the corresponding product-oriented
> subgoal including, for each quality perspective of interest (e.g., reduction of defects, cost
> effectiveness), questions related to the major model(s) used, the validity of the model for the particular
> environment, the validity of the data collected, the model effectiveness and the substantiation of the
> model.
>
> **(3) Feedback** follows a pattern similar to the corresponding product-oriented subgoal."

#### VIEWS OF METRICS (verbatim)

> "Metrics can be objective and subjective. An objective metric is an absolute measure taken on the product
> or process. Examples include: time for development, number of lines of code, work productivity, number of
> errors or changes. Objective metrics are usually based upon an interval or ratio scale. Subjective metrics
> represent an estimate of extent or degree in the application of some technique or a classification or
> qualification of problem or experience. They are used in situations where there is no exact measurement,
> usually on a relative scale. Examples include: the degree of use of a method or technique or the
> experience of the programmers in the application. Subjective metrics are usually based upon a nominal or
> ordinal scale."

> "Measures may be taken of the product and the process. Product measurement is on a developed product or
> document, i.e., source code, object code, requirements document. … Process measurement is taken on the
> activities used in developing the product."

> "We can measure cost and quality. Cost includes the measure of any resource expenditure used in a project,
> e.g., staff months, computer time, hardware cost, purchased software, calendar time. Quality is a measure
> of some form of value of the product or process, e.g., reliability, functionality, ease of change,
> correctness, reusable components developed."

> "The choice of metrics is determined by the quantifiable questions which are based upon the models used.
> The guidelines for questions acknowledge the need for generally more than one metric, for both objective
> and subjective metrics, and for associating interpretations with metrics. … As goals, questions and
> metrics provide for tractability of the (top-down) definitional quantification process, they also provide
> for the interpretation context (bottom-up). This integration of definition with interpretation allows for
> the interpretation process to be tailored to the specific needs of an environment."

#### GENERATING A PARTICULAR OPERATIONAL MODEL (verbatim, the worked technique)

> "Often we must build simple models of various products and processes. … This definition is then converted
> into an operational model by providing a set of interval values associated with the various steps of the
> process. In this case, since the model is clear, each of the steps represents a further passage along the
> interval scale."

The resulting reusable ordinal instrument — a template worth copying for extraction forms:

```
Characterize the process experience of the team.
(subjective rating per person)
  0 - none
  1 - have read the manuals
  2 - have had a training course
  3 - have had experience in a laboratory environment
  4 - have used on a project before
  5 - have used on several projects before
  x - no response
```

> "The data from the question can then be interpreted in a variety of ways. For example, if there are ten
> members of the team, we might require that a minimum requirement is that all team members have at least a
> three and the team leader has a five, etc. This evaluation process will become more effective over time."

And the validity note: "Even though we call this a subjective rating, it should be clear that if the
education and training process is valid, then our model and the metrics associated with it are valid."

#### The GQM process (verbatim, five numbered steps)

> "Applying the GQM involves (1) developing a set of corporate, division and project goals for productivity
> and quality, e.g., customer satisfaction, on-time delivery, improved quality, (2) generating questions
> (based upon models) that define those goals as completely as possible in a quantifiable way, (3)
> specifying the measures needed to be collected to answer those questions and to track process and product
> conformance to the goals, (4) developing mechanisms for data collection, and (5) collecting, validating
> and analyzing the data in real time to provide feedback to projects for corrective action and analyzing
> the data in a post mortem fashion to assess conformance to the goals and make recommendations for future
> improvements."

#### The Quality Improvement Paradigm (QIP), verbatim — the enclosing cycle

> "**Planning:** an iterative process involving characterizing the current project and its environment,
> setting the quantifiable goals for successful project performance and improvement, and choosing the
> appropriate process model and supporting methods and tools for this project.
> **Execution:** a closed-loop project cycle which involves executing the processes, constructing the
> products, collecting and validating the prescribed data, and analyzing it in real-time to provide feedback
> for corrective action on the current project.
> **Analysis and Packaging:** a post mortem analysis of the data and information gathered to evaluate the
> current practices, determine problems, record findings, and make recommendations for future project
> improvements, and a packaging of the experience gained in the form of updated and refined models and other
> forms of structured knowledge gained from this and prior projects and the storing of the packages in an
> experience base so it is available for future projects."

**Experience Factory (verbatim):** "a logical and/or physical organization that supports project
developments by analyzing and synthesizing all kinds of experience, acting as a repository for such
experience, and supplying that experience to various projects on demand. It packages experience by building
informal, formal or schematized, and productized models and measures of various software processes,
products, and other forms of knowledge via people, documents, and automated support."

#### The GQM graph structure (verbatim)

> "The flow from the goals to the metrics in the GQM paradigm can be viewed as a directed graph (the flow is
> from the goal nodes to the question nodes to the metric nodes) … Here there are n goals shown and each
> goal generates a set of quantifiable questions that attempt to define and quantify the specific goal which
> represents an entry node in the directed graph. These questions are based upon a particular set of
> process, product, and quality models that are not explicitly represented in the graph. Each directed
> sub-graph reachable from a goal node represents a particular GQM model."

> "The goal is only as well-defined as the questions it generates and the models on which those questions
> are based. Since models are often hard to define, they may exist only implicitly in the questions. The
> more formal, explicit, and complete the models, the more effective the questions and the definition of the
> goals. Each question generates a set of metrics (mi) or distributions (di). Again, the question can only be
> answered relative to and as completely as the available metrics and distributions allow. As is shown in the
> above diagram, the same questions can be used to define multiple goals …, and metrics and distributions can
> be used to answer more than one question. Thus questions and metrics are used in several contexts."

### Techniques for data extraction and analysis (worked examples reproduced)

**Process goal example (verbatim):** "GQM Goal: Analyze the *system test process* for the purpose of
*evaluation* with respect to *defect slippage* from the point of view of the *corporation*."

Defect Slippage Model, verbatim:

```
Es = #faults per KLOC found in system test in this project
Ea = #faults per KLOC found in acceptance test in this project
Eo = #faults per KLOC found in operation in this project
Let {Pi} be the set of projects used as a basis for comparison.
PEs = average #faults per KLOC found in system test in {Pi}
PEa = average #faults per KLOC found in acceptance test in {Pi}
PEo = average #faults per KLOC found in operation in {Pi}
Fc = the ratio of faults per KLOC found in system test to the faults found after system test on this
     project.  [Fc = Es/(Es+Ea+Eo)]
Fs = the ratio of faults per KLOC found in system test to the faults found after system test in the set of
     projects used as a basis for comparison.  [Fs = PEs/(PEs+PEa+PEo)]
QF = Fc/Fs = the relationship of system test on this project to faults as compared to the average the
     appropriate basis set.
```

*Simple Interpretation Algorithm for Defect Slippage Model* (verbatim) — a model of how to attach an
interpretation rule to a metric:

```
if QF
 > 1 then
        method better than history
        check process conformance
        if process conformance poor
              improve process or process conformance
        check domain conformance
        if domain conformance poor
              improve object or domain training
 = 1 then
        method equivalent to history
        if cost lower than normal
              method cost effective
              check process conformance
        ...
 < 1 then
        check process conformance
        if process conformance good
              check domain conformance
              if domain conformance good
                    method poor for this class of project
```

**Product goal example (verbatim):** "GQM Goal: Analyze the *system* for the purpose of *evaluation* with
respect to *reliability* from the point of view of the *user community* and with respect to *user
satisfaction* from the point of view of the *customer*." — "Product Models: Logical/Physical Attributes,
Cost, Changes, Operational Profile". This demonstrates two focuses and two viewpoints on one object.

Also reproduced in the paper and directly transferable to extraction-form design: **DATA SOURCES** as
explicit tables filled at defined lifecycle points ("System test table 1: Nature of requirements (Filled out
after baselining of requirements)"; "System test table 2: Nature of tests (Filled out after test plan)";
"System test table 3: Results of the tests (Filled out after tests run)"), and **DATA PRESENTATIONS**
prescribed per question group (histograms, graphs vs. calendar time, and matrices —
Requirements × Customer, Component × Requirements, Component × Customer, Test × Component,
Test × Requirements).

### Caveats, traps and pitfalls

- "Measurement must be defined in a top down fashion, bottom-up approach won't work."
- **Record unmeasurable items anyway (verbatim):** "If a measure cannot be taken but is part of the
  definition of the question, it is important that it be included in the GQM paradigm. This is so that the
  other metrics that answer the question can be viewed in the proper context and the question interpreted
  with the appropriate limitations. The same is clearly true for questions being asked that may not be
  answerable with the data available."
- **The goal is only as good as its questions and models (verbatim):** "The goal is only as well-defined as
  the questions it generates and the models on which those questions are based. Since models are often hard
  to define, they may exist only implicitly in the questions. The more formal, explicit, and complete the
  models, the more effective the questions and the definition of the goals."
- **Answers are bounded by the instrument (verbatim):** "the question can only be answered relative to and
  as completely as the available metrics and distributions allow."
- **Avoid complex objectives (verbatim):** "It is clear that the author must avoid complex objectives. In
  some cases it may be wise to break a complex goal into several simpler goals."
- **Environmental factors must be stable across goals (verbatim):** "the environmental factors, rather than
  the values associated with these factors, should be consistent across several goals within the project and
  the organization."
- **Metric count does not scale with goal count (verbatim):** "Although there may be many goals and even
  many questions, the metrics do not grow at the same rate as the goals and questions. Thus a set of metrics
  could be collected for characterizing the software process and product that will allow us to answer many
  questions generated by different goals."
- **Goal setting is hard and needs experience (verbatim):** "The process of setting goals and refining them
  into quantifiable questions is complex and requires experience."
- **The templates are provisional (verbatim):** "The current set of templates and guidelines represent our
  current thinking and well may change over time as our experience grows."
- **Substantiation is a validity hedge:** the optional "substantiation of the model" question ("an
  alternative model to help evaluate whether the results of the primary model are reasonable") is "taken
  when there is some concern about the validity of the primary model or the data." Note the paper builds
  *validity of the model* and *validity of the data collected* in as standing question types in both the
  product and process question guidelines.

### Empirical findings worth citing

None (no study data). Origin/deployment claims only: "The GQM paradigm was originally developed for
evaluating defects for a set of projects in the NASA/GSFC environment. The application involved a set of
case study experiments [BaWe84]. It was then expanded to include various types of experimental approaches,
including controlled experiments [BaSe84]."

### Appendix — Comparison of Quality Measurement Approaches (reproduced in full)

| Criteria | QFD Approach | SQM Approach | GQM Approach |
|---|---|---|---|
| **Scope** — Object of study | products | final product | any process, product, model |
| **Scope** — Purpose | plan, engineer, control | assess | characterize, evaluate, predict, motivate, ... |
| **Scope** — Viewpoint | customer, user | customer, user | customer, user, developer, manager, corporation... |
| **Structure** — Paradigm | Trace user characteristics of final product into related product/process characteristics at various stages of development | Refine factors into criteria and metrics | Refine goals into questions and metrics |
| **Structure** — Options | select/tailor | select | select/tailor |
| **Usage** | Quality Management | Quality Management | Quality and Project Management |

> "The SQM approach was developed to allow the customer to assess the product being developed by a
> contractor. … It can be thought of as representing a specific example of a GQM with the models and metrics
> already supplied."
> "The QFD approach was originally developed for manufacturing in order to better understand customer
> requirements and map them into the design documents for the product. … As with the SQM, the models and
> metrics are built into the system and supplied to the user although there is some opportunity to tailor.
> Again, this can be considered as a special example of the GQM."

---

## Cross-paper synthesis for `docs/methodology/`

1. **Ampatzoglou is the operative framework for secondary studies**; Petersen & Gencel is the operative
   framework for *primary* studies and for the *appraisal* of them inside a review. The two do not compete —
   Ampatzoglou explicitly rejects Cook–Campbell categories *for secondary studies* on usability grounds
   ("These are easily identifiable steps in a secondary study, in contrast to using the aspects of validity
   that are threatened"), while Petersen & Gencel rejects them *for primary studies* on paradigm grounds
   (they encode a positivist worldview and unfairly penalise interpretivist work).
2. **Petersen & Gencel's open/reduced/mitigated reporting taxonomy is directly graftable onto Ampatzoglou's
   TV/MA checklist** — it supplies the missing status field that Ampatzoglou's "either appropriate mitigation
   action should be explicitly reported or an acknowledgement should be made that the threat is not (fully)
   mitigated" only gestures at.
3. **GQM is the named mitigation for Ampatzoglou's TV19** ("The most common best practice for resolving this
   threat is the use of the GQM approach that has been introduced by Basili et al."), so the goal template
   (Basili 1992's five-slot form: object / purpose / focus / viewpoint / environment) is the mechanism for
   deriving a review's research questions from its goal — and by extension, via the product- and
   process-question guidelines, the mechanism for deriving the data extraction form. This also mitigates
   Ampatzoglou's TV9 ("Have you chosen the correct variables to extract?"), whose stated best practice is
   "the extraction of variables based on the set of research questions and their beforehand mapping".
4. **Basili's "record the measure even if it cannot be taken"** rule is the extraction-form analogue of
   Ampatzoglou's reporting complaint that 80.7% of mitigations are buried in study design rather than
   declared: in both cases the failure mode is silent omission rather than acknowledged limitation.
