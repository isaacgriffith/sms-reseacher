# Batch 5 — Multivocal Literature Reviews and Grey Literature

Source extractions: `/tmp/claude-1000/-home-isaacg-git-sms-reseacher/a0f345f5-a480-4ec5-b6b4-ca1581ec6c5c/scratchpad/txt/`

Papers covered: `garousi_guidelines_2019`, `garousi_need_2016`, `garousi_benefitting_2020`, `adams_shades_2017`, `neto_multivocal_2019`, `lopez_multivocal_2026`.

Convention: quoted text is verbatim from the extraction. `[EXTRACTION UNCLEAR: …]` marks content that lives in a figure/table that did not survive PDF-to-text conversion.

---

## garousi_guidelines_2019 — Guidelines for including grey literature and conducting multivocal literature reviews in software engineering
**(V. Garousi, M. Felderer, M.V. Mäntylä, Information and Software Technology 106 (2019) 101–121)**

**Type:** guideline (methodological guidelines paper)

**Role in corpus:** This is *the* MLR process paper for software engineering — it is the only source in the corpus that gives a complete, phase-by-phase MLR process (planning / conducting / reporting) with 14 numbered guidelines, a 7-question decision aid for whether to include grey literature, three named stopping criteria for grey-literature search, and a 20-item grey-literature quality-assessment checklist with worked scoring.

### Definition and tiers of grey literature

**The Luxembourg definition** (described as "The most widely used and accepted definition"):

> "<grey literature> is produced on all levels of government, academics, business and industry in print and electronic formats, but which is not controlled by commercial publishers, i.e., where publishing is not the primary activity of the producing body" [23]

**Cochrane handbook definition** [24]: GL is "literature that is not formally published in sources such as books or journal articles".

**The multivocal-literature definition** (from Ogawa & Malen [12], quoted by Garousi et al.):

> "Multivocal literatures are comprised of all accessible writings on a common, often contemporary topic. The writings embody the views or voices of diverse sets of authors (academics, practitioners, journalists, policy centers, state offices of education, local school districts, independent research and development firms, and others). The writings appear in a variety of forms. They reflect different purposes, perspectives, and information bases. They address different aspects of the topic and incorporate different research or non-research logics".

**Table 1 — Spectrum of the 'white', 'grey' and 'black' literature (from [25] = Giustini):**

| 'White' literature | 'Grey' literature | 'Black' literature |
|---|---|---|
| Published journal papers | Preprints | Ideas |
| Conference proceedings | e-Prints | Concepts |
| Books | Technical reports | Thoughts |
| | Lectures | |
| | Data sets | |
| | Audio-Video (AV) media | |
| | Blogs | |

**Fig. 1 "Shades of grey literatures" (adopted from Adams et al. [17], with SE-specific revisions).** The figure image itself is not in the text extraction, but its two axes and the three tiers are defined verbatim in the prose and reproduced fully in Table 7 (below):

> "The model shown in Fig. 1 has two dimensions: expertise and outlet control. Both dimensions run between extremes "unknown" and "known". Expertise is the extent to which the authority and knowledge of the producer of the content can be determined. Outlet control is the extent to which content is produced, moderated or edited in conformance with explicit and transparent knowledge creation criteria. Rather than having discrete bands, the gradation in both dimensions is on a continuous range between known and unknown, producing the shades of GL."

Garousi's own change to Adams' model: "The changes that we made to the model in [17] to make it more applicable to SE was a revision of the outlets on the right-hand side under the three "tier" categories, e.g., we added the Q/A websites (such as StackOverflow)."

**The three tiers, verbatim (from Table 7, "Outlet type" criterion):**

- "1st tier GL (measure = 1): High outlet control/ High credibility: Books, magazines, theses, government reports, white papers"
- "2nd tier GL (measure = 0.5): Moderate outlet control/ Moderate credibility: Annual reports, news articles, presentations, videos, Q/A sites (such as StackOverflow), Wiki articles"
- "3rd tier GL (measure = 0): Low outlet control/ Low credibility: Blogs, emails, tweets"

> Note a genuine internal inconsistency in the paper: in Table 7 "presentations" appear in the **2nd** tier, while in the Table 9 worked example the same list places "Blog posts, presentations, emails, tweets" in the **3rd** tier. Both are reproduced above/below as printed.

**Mapping of the white/grey/black spectrum onto the tiers:**

> "The 'white' literature is visible in both Fig. 1 and Table 1 and the means the source where both expertise and outlet control are fully known. 'Grey' literature according to Table 1 corresponds mainly to the 2nd tier in Fig. 1 with moderate outlet control and credibility. For SE, we add Q/A sites like StackOverflow to the 2nd tier. 'Black' literature finally corresponds to ideas, concepts and thoughts. As blogs, but also emails and tweets mainly refer to ideas, concepts or thoughts they are in the 3rd tier. However, there are even "shades" of grey in the classification and depending on the concrete content a specific type of grey literature can be in a different tier than shown in Fig. 1. For instance, if a presentation (or a video, which is often linked to a presentation) is about new ideas, then it would fall into the 3rd tier."

**GL producers** (seven categories, from [25]): "(1) Government departments and agencies (i.e., in municipal, provincial, or national levels); (2) Non-profit economic and trade organizations; (3) Academic and research institutions; (4) Societies and political parties; (5) Libraries, museums, and archives; (6) Businesses and corporations; and (7) Freelance individuals, i.e., bloggers, consultants, and web 2.0 enthusiasts." Garousi adds: "For SE, it might in addition also be relevant to distinguish different types of companies, e.g. startups versus established organizations, or different governmental organizations, e.g. military versus municipalities, producing GL."

### Six types of secondary study (the MLR/SLR/GLR taxonomy — Fig. 2, Fig. 3)

Garousi's own contribution. "we categorize secondary studies in SE into six types, i.e., Systematic Literature Mappings (SLM), Systematic Literature Review (SLR), Grey Literature Mapping (GLM), Grey Literature Review (GLR), Multivocal Literature Mapping (MLM), and Multivocal Literature Review (MLR)".

Differentiation factors: "types of analysis, and types of sources under study."

| Study type | Sources | Analysis |
|---|---|---|
| SLM / SM (Systematic Literature Mapping) | Papers in formal literature | Mapping (classification) |
| SLR (Systematic Literature Review) | Papers in formal literature | Synthesis of evidence |
| GLM (Grey Literature Mapping) | Sources in grey literature | Mapping |
| GLR (Grey Literature Review) | Sources in grey literature | Synthesis of evidence |
| MLM (Multivocal Literature Mapping) | Both formal and grey | Mapping |
| MLR (Multivocal Literature Review) | Both formal and grey | Synthesis of evidence |

Core MLR-vs-SLR difference, stated twice verbatim:

> "the difference between an MLR and an SLR is the fact that, while SLRs use as input only academic peer-reviewed articles, MLRs in addition also use sources from the GL, e.g., blogs, white papers, videos and web-pages [18]."

Venn relationship (Fig. 3): "an MLR in a given subject field is a union of the sources that would be studied in an SLR and in a GLR of that field. As a result, an MLR, in principle, is expected to provide a more complete picture of the evidence as well as the state-of-the-art and -practice in a given field than an SLR or a GLR".

MLM→MLR extension: "Similar to the relationship of SLM and SLR studies [22], a MLM can be extended by follow-up studies to a Multivocal Literature Review (MLR) where an additional in-depth analysis or qualitative coding of the issues and evidence in a given subject is performed".

### Decision criteria: when to include grey literature / when to do an MLR

**Table 4 — Questions to decide whether to include the GL in software engineering reviews.** (Items 1–5 adopted from Benzies et al. [81] and Adams et al. [17]; items 6 and 7 are Garousi's own addition. Third column shows the a-posteriori application to the running example MLR-AutoTest.)

| # | Question | Possible answers | MLR-AutoTest |
|---|---|---|---|
| 1 | Is the subject "complex" and not solvable by considering only the formal literature? | Yes/No | Yes |
| 2 | Is there a lack of volume or quality of evidence, or a lack of consensus of outcome measurement in the formal literature? | Yes/No | Yes |
| 3 | Is the contextual information important to the subject under study? | Yes/No | Yes |
| 4 | Is it the goal to validate or corroborate scientific outcomes with practical experiences? | Yes/No | Yes |
| 5 | Is it the goal to challenge assumptions or falsify results from practice using academic research or vice versa? | Yes/No | Yes |
| 6 | Would a synthesis of insights and evidence from the industrial and academic community be useful to one or even both communities? | Yes/No | Yes |
| 7 | Is there a large volume of practitioner sources indicating high practitioner interest in a topic? | Yes/No | Yes |

> "Note: One or more "yes" responses suggest inclusion of GL."
> "The larger the sum the higher is the need for conducting an MLR on that topic."

Note on item 3's adaptation: "item #3 originally [17, 81] was: "Is the context important to the outcome or to implementing intervention?". We have adopted it as shown in Table 4. … It is true that question 3 would (almost) always be yes for most SE topics, but we still would like to keep it in the list of questions, in case."

Additional inclusion arguments the paper reproduces from other fields:
- "GL provides "current" perspectives and complements gaps of the formal literature [25]."
- "Including GL may help avoiding publication bias. Yet, the GL that can be located may be an unrepresentative sample of all unpublished studies [19]."
- "Decision to include GL in an MLR was a result of consultation with stakeholders, practicing ergonomists, and health and safety professionals [80]."
- "If GL were not included, the researchers thought that an important perspective on the topic would have been lost [80]".

**When to EXCLUDE GL:** "This guideline also suggests excluding GL from the reviews of relatively mature and bounded academic topics. In SE, this would mean topics such as the mathematical aspects of formal methods which are relatively bounded in the academic domain only, i.e., one would not find too many practitioner-generated GL on this subject."

Explicit non-universalism: "It should be highlighted that we are not advocating that all SLRs in SE should include GL and become MLRs."

### Process steps or stages defined

Three phases adopted from Kitchenham & Charters [22], with sub-steps (Table 3):

| Phase | Steps |
|---|---|
| Planning the review | Identification of the need for a review; Commissioning a review; Specifying the research question(s); Developing a review protocol; Evaluating the review protocol |
| Conducting the review | Identification of research; Selection of primary studies; Study quality assessment; Data extraction and monitoring; Data synthesis |
| Reporting the review | Specifying dissemination mechanisms; Formatting the main report; Evaluating the report |

**The MLR process (Fig. 7).** Planning = (1) Establishing the need for an MLR in a given topic; (2) Defining the MLR's goal and raising its research questions (RQs). Conducting = five phases, in order:
- Search process (§5.1)
- Source selection (§5.2)
- Study quality assessment (§5.3)
- Data extraction (§5.4)
- Data synthesis (§5.5)

Reporting = (1) reporting style for different audience types; (2) ensuring usefulness to the target audience.

**Which steps differ from SLR:** "To prevent duplication, we do not repeat all steps of the SLR guidelines [22] when they are the same for conducting MLRs, but only present the steps that are different for conducting MLRs. Therefore, our guidelines focus mainly on GL sources as handling sources from the formal literature is already covered by the SLR existing guidelines. Integrating both types of sources in an MLR is usually straightforward, as per our experience in conducting MLRs". The steps flagged as genuinely different are **the search process** and **source quality assessment** (stated in the abstract: "several phases of MLRs differ from those of traditional SLRs, for instance with respect to the search process and source quality assessment").

**The 14 guidelines, verbatim:**

1. **Guideline 1:** "The provided typical process of an MLR can be applied to structure a protocol on how the review will be conducted. Alternatively, the standard protocol structure of SLR in SE can be applied and the provided guidelines can be considered as variation points."
2. **Guideline 2:** "Identify any existing reviews and plan/execute the MLR to explicitly provide usefulness for its intended audience (researchers and/or practitioners)."
3. **Guideline 3:** "The decision whether to include the GL in a review study and to conduct an MLR study (instead of a conventional SLR) should be made systematically using a well-defined set of criteria/questions (e.g., using the criteria in Table 4)."
4. **Guideline 4:** "Based on your research goal and target audience, define the research (or "review") questions (RQs) in a way to (1) clearly relate to and systematically address the review goal, (2) match specific needs of the target audience, and (3) be as objective and measurable as possible."
5. **Guideline 5:** "Try adopting various RQ types (e.g., see those in Table 6) but be aware that primary studies may not allow all question types to be answered."
6. **Guideline 6:** "Identify the relevant GL types and/or GL producers (data sources) for your review study early on."
7. **Guideline 7:** "General web search engines, specialized databases and websites, backlinks, and contacting individuals directly are ways to search for grey literature."
8. **Guideline 8:** "When searching for GL on SE topics, three possible stopping criteria for GL searches are: (1) Theoretical saturation, i.e., when no new concepts emerge from the search results; (2) Effort bounded, i.e., only include the top N search engine hits, and (3) Evidence exhaustion, i.e., extract all the evidence."
9. **Guideline 9:** "Combine inclusion and exclusion criteria for grey literature with quality assessment criteria (see Table 7)."
10. **Guideline 10:** "In the source selection process of an MLR, one should ensure a coordinated integration of the source selection processes for grey literature and formal literature."
11. **Guideline 11:** "Apply and adapt the criteria authority of the producer, methodology, objectivity, date, novelty, impact, as well as outlet control (e.g., see Table 7), for study quality assessment of grey literature.
    - Consider which criteria can already be applied for source selection.
    - There is no one-size-fits-all quality model for all types of GL. Thus, one should make suitable adjustments to the quality criteria checklist and consider reductions or extensions if focusing on particular studies such as survey, case study or experiment."
12. **Guideline 12:** "During the data extraction, systematic procedures and logistics, e.g., explicit "traceability" links between the extracted data and primary sources, should be utilized. Also, researchers should extract and record as much quantitative/qualitative data as needed to sufficiently address each RQ, to be used in the synthesis phase."
13. **Guideline 13:** "A suitable data synthesis method should be selected. Many GL sources are suitable for qualitative coding and synthesis. Some GL sources allow combination of survey results but lack of reporting rigor limits the meta-analysis. Quantitative analysis is possible on GL databases such as StackOverflow. Also argumentation theory can be beneficial for data synthesis from grey literature. Finally, the limitations of GL sources w.r.t. their evidence depth of experiment prevent meta-analysis."
14. **Guideline 14:** "The writing style of an MLR paper should match its target audience, i.e., researchers and/or practitioners.
    - If targeting practitioners, a plain and to-the-point writing style with clear suggestion and without details about the research methodology should be chosen. Asking feedback from practitioners is highly recommended.
    - If the MLR paper targets researchers, it should be transparent by covering the underlying research methodology as well as an online repository and highlight the research findings while providing directions to future work."

**RQ typing (Table 6, classification scheme from Easterbrook et al. [91]).** Categories and their canonical question forms:

| RQ category | Sub-category | Canonical question |
|---|---|---|
| Exploratory | Existence | Does X exist? |
| Exploratory | Description-Classification | What is X like? |
| Exploratory | Descriptive-Comparative | How does X differ from Y? |
| Base-rate | Frequency Distribution | How often does X occur? |
| Base-rate | Descriptive-Process | How does X normally work? |
| Relationship | Relationship | Are X and Y related? |
| Causality | Causality | Does X cause (or prevent) Y? |
| Causality | Causality-Comparative | Does X cause more Y than does Z? |
| Causality | Causality-Comparative Interaction | Does X or Z cause more Y under one condition but not others? |
| Design | Design | What's an effective way to achieve X? |

Finding from the tertiary study [29] used to motivate this: "descriptive-classification RQs were the most popular by large margin … there is a shortage or lack of RQs in types towards the bottom of the classification scheme. For example, among all the studies, no single RQ of type Causality-Comparative Interaction or Design was raised."

Goal-setting method: "we have often made use of the Goal-Question-Metric (GQM) methodology [90]". RQs drive: "The search process must identify primary studies that address the RQs / The data extraction process must extract the data items needed to answer the RQs / The data analysis (synthesis) phase must synthesize the data in such a way that the RQs are properly answered".

### Grey-literature search techniques

**Where to search — four strategies (Guideline 7):**

1. **General web search engine.** "conventional web search engines such as Google were used in many GL review studies in management [79] and health sciences [78]. This advice is valid and easily applicable in the SE context as well."
2. **Specialized databases and websites.** "the choice of websites that the review authors should focus on, would depend on the particular search goals." Named SE-relevant examples: non-peer-reviewed electronic archives (`www.arxiv.org`), social question-answer websites (`www.stackoverflow.com`), AgileAlliance (`www.agilealliance.org`), ISTQB (`www.istqb.org`), the GL database `www.opengrey.eu`. Annual industry surveys usable as MLR input: the World Quality Report [93], the annual State of Agile report [94], IDC worldwide developer estimates, the Finnish software company survey ("Ohjelmistoyrityskartoitus") [95], and the Turkish Software Quality report [96]. Coverage caveat given: OpenGrey "search for "software engineering" resulted in only 4,115 hits as of this writing (March 21, 2017). For comparison, Scopus provides 120,056 hits for the same search."
3. **Contacting individuals directly or via social media.** "Individuals can be contacted for multiple purposes for example to provide their unpublished studies or to find out specialized databases where relevant information could be searched. [79] mentions contacting individuals via multiple methods: direct requests, general requests to organizations, request to professional societies via mailing list, and open requests for information in social media (Twitter or Facebook)."
4. **Reference lists and backlinks.** "Studying reference lists, so called snowballing [92], is done in the white (formal) literature reviews as well in GL reviews. However, in GL and in particularly GL in web sites, formal citations are often missing. Therefore, features such as backlinks can be navigated either forward or backward. Backlinks can be extracted using various online back-link checking tools, e.g., MAJESTIC (www.majestic.com)."

Formal-literature comparison: "Formally-published literature is searched via either broad-coverage abstract databases, e.g., Scopus, Web of Science, Google Scholar or from full-text databases with more limited coverage, e.g., IEEE Xplore, ACM digital library, or ScienceDirect. The search strategy for GL is obviously different since academic databases do not index GL."

**Search-string construction:** "Due to the lack of standardization of terminology in SE in general and the issue that this problem may even be more significant for the GL, the definition of key search terms in search engines and databases requires special attention. For MLRs we therefore recommend to perform an informal pre-search to find different synonyms for specific topics as well as to consult bodies of knowledge such as the Software Engineering Body of Knowledge (SWEBOK) [97] … or … the standard glossary of terms used in software testing from the ISTQB [98]".

**When to stop the search — three stopping criteria (Guideline 8), verbatim:**

1. "Theoretical saturation, i.e., when no new concepts emerge from the search results anymore"
2. "Effort bounded, i.e., only include the top N search engine hits"
3. "Evidence exhaustion, i.e., extract all the evidence"

Rationale, three factors that make GL stopping different from formal-literature "data exhaustion":
- "the stopping rules are intervened with the goals and types of evidence of including GL. If evidence is mostly qualitative, one can reach theoretical saturation, i.e., a point where adding new sources do not increase the number of findings, even if one decides to stop the search before finding all the relevant sources."
- "the stopping rules can be influenced by the large volumes of data. For example, in MLR-AutoTest, we received 1,330,000 hits from Google. Obviously, in such cases, one needs to rely on the search engine page rank algorithm [99] and choose to investigate only a suitable number of hits."
- "stopping rules are influenced due to the varying quality and availability of evidence … in our review of gamification of software testing [54], the quality of evidence quickly declined when moving down in the search results provided by Google search engine."

Worked example: "In MLR-AutoTest, authors limited their search to the first 100 search hits and continued the search further if the hits on the last page still revealed additional relevant search results. This partially matches the "effort bounded" stopping rules augmented with an exhaustive-like subjective stopping criterion."

### Quality/credibility appraisal criteria for grey literature

**Table 7 — Quality assessment checklist of grey literature for software engineering (verbatim, all criteria and all questions).** Synthesized from Adams et al. [17], Yasin & Hasnain [50], Rainer [51] and Tyndall's AACODS checklist [70], plus the authors' own MLR experience.

| Criteria | Questions |
|---|---|
| **Authority of the producer** | • Is the publishing organization reputable? E.g., the Software Engineering Institute (SEI)<br>• Is an individual author associated with a reputable organization?<br>• Has the author published other work in the field?<br>• Does the author have expertise in the area? (e.g. job title principal software engineer) |
| **Methodology** | • Does the source have a clearly stated aim?<br>• Does the source have a stated methodology?<br>• Is the source supported by authoritative, contemporary references?<br>• Are any limits clearly stated?<br>• Does the work cover a specific question?<br>• Does the work refer to a particular population or case? |
| **Objectivity** | • Does the work seem to be balanced in presentation?<br>• Is the statement in the sources as objective as possible? Or, is the statement a subjective opinion?<br>• Is there vested interest? E.g., a tool comparison by authors that are working for particular tool vendor<br>• Are the conclusions supported by the data? |
| **Date** | • Does the item have a clearly stated date? |
| **Position w.r.t. related sources** | • Have key related GL or formal sources been linked to / discussed? |
| **Novelty** | • Does it enrich or add something unique to the research?<br>• Does it strengthen or refute a current position? |
| **Impact** | • Normalize all the following impact metrics into a single aggregated impact metric (when data are available): Number of citations, Number of backlinks, Number of social media shares (the so-called "alt-metrics"), Number of comments posted for a specific online entries like a blog post or a video, Number of page or paper views |
| **Outlet type** | • 1st tier GL (measure = 1): High outlet control/ High credibility: Books, magazines, theses, government reports, white papers<br>• 2nd tier GL (measure = 0.5): Moderate outlet control/ Moderate credibility: Annual reports, news articles, presentations, videos, Q/A sites (such as StackOverflow), Wiki articles<br>• 3rd tier GL (measure = 0): Low outlet control/ Low credibility: Blogs, emails, tweets |

**Scoring anchors and threshold (from the worked application, Table 9).** Total = 20 individual criteria (19 binary 0/1 questions + outlet type scored 1 / 0.5 / 0). "Out of a total quality score of 20 (the total number of individual criteria in Table 7), the five GL sources GL1, …, GL5 received the scores of 13, 19, 16, 15.5, 12, respectively." Normalized scores were "13/20 = 0.65, 19/20 = 0.95, 16/20 = 0.80, 15.5/20 = 0.78, 12/20 = 0.60". Proposed cut-off:

> "If MLR-AutoTest was conduct this type of systematic quality assessment for all the GL sources, it could for example set the quality score of 10 as the "threshold" (20/2). Any source above that would be included in the pool and any source with score below it would be excluded."

Two questions must be **negated** before scoring (an operational trap recorded in the Table 9 notes): for "Is the statement … a subjective opinion?" and "Is there vested interest?", "The original version of the question in Table 8 would get assigned '0' for the positive outcome, thus we negated it."

**Richer scoring than binary is permitted:** "the decision whether to include a source or not can go beyond a bare binary decision ("yes" or "no" …), and can be based on a richer scoring scheme. For instance, da Silva et al. [101] used a 3-point Likert scale (yes = 1, partly = 0.5, and no = 0) to assign scores to assessment questions. Based on these scoring results, agreement between different persons can be measured and a threshold for the inclusion of sources can be defined."

**Formal-literature rigor checklists remain available in parallel:** "To investigate the quality (rigor) of specific study types in detail, checklists tailored to specific study types are available. For instance, Host and Runeson [100] presented a quality checklist for case studies, which can also be utilized for case studies reported in formal literature."

**Merging selection with appraisal (Guideline 9):** "In principle, one can use any checklist item of the quality assessment checklist for source selection as well. For instance, the methodology, the date of publication, or the number of backlinks can be used as a selection criterion. … the more sources one can exclude with certainty based on a set of criteria, the less effort is needed for the more time-consuming study quality assessment."

**Source selection process (Guideline 10):** "The source selection process for GL requires a coordinated integration with the selection process for formal literature. Both formal and GL outlets should be investigated adequately and effort required to analyze one source type shall not reduce the effort required for the other source type. Furthermore, source selection can overlap with the searching process when searching involves snowballing or contacting the authors of relevant papers. When two or more researchers assess each paper, agreement between researchers is required and disagreements must be discussed and resolved, e.g., by voting."

**Argumentation-theory critical questions for expert-opinion GL** (adopted from Walton, Reed & Macagno [52] via Rainer [51]); P = a proposition in a GL source, W = the writer of a GL source:

1. "Expertise: How credible is W ("Writer" of the GL source) as an expert source?"
2. "Field: Is W an expert in the field that P is in?"
3. "Opinion: What did W assert that implies P?"
4. "Trustworthiness: Is W personally reliable as a source?"
5. "Consistency: Is proposition P consistent with what other experts assert?"
6. "Backup evidence: Is W's assertion based on evidence?"

Garousi's own critique of two of these: "while the above questions seem to be useful and rationale, some of them seem slightly questionable, e.g., question #4 cannot be reliably assessed. Also question #5 could be irrelevant since experts should be allowed to have non-consistent opinions with each other."

### Caveats, traps and pitfalls

- **GL is not always advantageous:** "it should be noted that including the GL in review studies is not always straightforward or advantageous [50]. There are some drawbacks as well, e.g., lower quality reporting on particularly when describing research methodology. Thus, careful considerations should be taken in different steps of an MLR study to be aware of such drawbacks".
- **Unrepresentative sampling / publication bias trap:** "Including GL may help avoiding publication bias. Yet, the GL that can be located may be an unrepresentative sample of all unpublished studies [19]."
- **Missing GL types silently corrupts the result:** "Any mistake in missing certain types of GL types could lead to the final MLR output (report) missing important knowledge and evidence in the subject under study."
- **Source selection is far more expensive than in an SLR:** "As GL is more diverse and less controlled than formal literature, source selection can be particularly time-consuming and difficult. Therefore, the selection criteria should be more fine-grained… The source selection process itself is not specific for GL, but typically more time-consuming as the selection criteria are more diverse and can be quite vague".
- **No universal quality model:** "There is no one-size-fits-all quality model for all types of GL."
- **Every appraisal criterion has failure modes:** "Each of our checklist criterion has strengths and weaknesses. Some are suitable only for specific types of GL sources, e.g., online comments only exist for source types open for comments like blog posts, news articles or videos. A highly commented blog post may indicate popularity, but on the other hand, spam comments may bias the number of comments, thus invalidating the high popularity."
- **Link rot, observed in the worked example:** "GL3 became a broken link at the time of this analysis." (Also, GL1 "is a website and does not have a clearly stated date related to its content.")
- **Meta-analysis is generally impossible from GL:** "we see that typically the quality and accuracy of the reporting does not allow to conduct quantitative meta-analysis from practitioner GL reports"; "often the GL surveys fail to report standard deviation, which makes statistical meta-analysis impossible. Furthermore, we have seen virtually no controlled experiments or rigorously conducted quasi-experiments in GL, thus, we see limited possibilities in using meta-analytic procedures to combine experiment results from GL in SE."
- **Rigor weighting when mixing source types:** "researchers should carefully balance synthesis using sources with different levels of rigor. We can easily see that the rigor used in a blog post is different than that of a research paper, and when synthesizing evidence from both types, their contributions to the combined evidence would ideally be not in the same "amount" (weight)."
- **Losing traceability makes peer review impossible:** "When traceability information (verbatim text from inside the primary studies) are not included in the data extraction sheets, peer reviewing of the data by other team members, and also finding the exact locations in the primary studies where the data actually come from become challenging. We have experienced such a challenge in many occasions in our past MLR and SLRs."
- **Under-extraction forces re-reading:** "Researchers should also extract and record as much quantitative/qualitative data as needed to sufficiently address each RQ. If not, answering the RQ under study will be impossible based on inadequate extracted data and would require further efforts to review, read and extract the missing data from the primary studies again."
- **Limitations of the guidelines themselves:** "(1) although they are based on our previous experience and the guidelines in other fields, they still need to be empirically evaluated in future studies; and (2) similar to any set of guidelines, our guidelines are based on our experience and also synthesis of other studies, and thus personal researcher bias could be involved".

### Metadata requirements for grey sources

- **Worksheet fields for recording the search** (from Giustini [25]): "a worksheet sample to extract data from the GL sources including fields such as: database, organization, website, pathfinder, guide to topic/subject, date searched, # of hits, and observations."
- **Chains of evidence:** "The guidelines in [12] suggested maintaining "chains of evidence (records of sources consulted and inferences drawn)". This is similar to what we call "traceability" links in SE".
- **Purpose and coverage of each document:** "because documents in the GL are often written for non-academic purposes and audiences and because documents often address different aspects of a phenomenon with different degrees of thoroughness, it is essential that researchers record the purpose and specify the coverage of each GL document."
- **Position-in-source pointers:** "due to the issue that GL sources have a less standardized structure than formal literature, it is also useful to provide "traceability" links (i.e., comments) in the data extraction form to indicate the position in the GL source where the extracted information was found."
- **Citation form actually used for GL** (Table 8, showing what was recorded per source): author, title, full URL, year, and **"Last accessed: Nov. 2017"** — an access date is carried on every web reference. Example: `B. Galen, "Automation Selection Criteria – Picking the "Right" Candidates," http://www.logigear.com/magazine/…, 2007, Last accessed: Nov. 2017.`
- **Public online repository:** "A useful resource that the authors of MLR/SLR should publish as a public online version is the repository of the review studies included in the MLR… Ideally, the online repository comes with additional export, search and filter functions to support further processing of the data." Benefits given: "transparency on the full dataset, replication and repeatability of the review, support when updating the study in the future by the same or a different team of researchers, and easy access to the full "index" of sources."

### Data extraction and analysis techniques

**Extraction-form design.** Traceable spreadsheet keyed to RQs. The MLR-AutoTest systematic map (Table 10) shows the schema: column 1 = RQ, column 2 = attribute/aspect, column 3 = set of all possible values, column 4 = (M)ultiple/(S)ingle selection.

| RQ | Attribute/Aspect | Categories | M/S |
|---|---|---|---|
| – | Source type | Formal literature, GL | S |
| 1 | Contribution type | Heuristics/guideline, method (technique), tool, metric, model, process, empirical results only, other | M |
| 1 | Research type | Solution proposal, validation research (weak empirical study), evaluation research (strong empirical study), experience studies, philosophical studies, opinion studies, other | S |
| 2 | Factors considered for deciding when/what to automate | A list of pre-defined categories (Maturity of SUT, Stability of test cases, 'Cost, benefit, ROI', and Need for regression testing) and an 'other' category whose values were later qualitatively coded (by applying 'axial' 'open' coding) | M |
| 3 | Decision-support tools | Name and features | M |
| 4 | Attributes of the software systems under test (SUT) | Number of software systems: integer; SUT names: array of strings; Domain, e.g., embedded systems; Type of system(s): Academic experimental or simple code examples, real open-source, commercial; Test automation cost/benefit measurements: numerical values | M |

**Extraction procedure:** "each involved researcher extracted and analyzed data from the share of sources assigned to her/him, then each researcher peer reviewed the results of each other's analyses. In the case of disagreements, discussions were conducted."

**Where grey and white documents describe the same study:** "The authors of [80] found cases where both the grey and peer-reviewed documents described the same study. In those cases, the team decided the primary document would be the peer-reviewed with GL documents as supplemental."

**Getting behind the GL source:** "In [79] the authors emailed and even called individuals to gather more detailed GL data. For GL, often only a subset of the original important data is made available in the GL source (to keep it short and brief) and detailed information is only available in "peoples' heads" [79]."

**Synthesis — the three types of data practitioners provide, and what each permits:**

1. "qualitative and experience-based evidence is very common in the GL as practitioners share their reflections… This requires qualitative data analysis techniques."
2. "quantitative evidence in the form of questionnaires is relatively common in GL, e.g., international surveys such as the state-of the Agile report by VersionOne, and the World Quality Survey by HP & Sogetti… If the same questionnaire is repeated in multiple or sequential surveys, this may allow meta-analysis."
3. "using data from particular GL databases such as question/answer sites (such as the StackOverflow website) may allow both the use of quantitative and qualitative research methods."

Available synthesis techniques cited from Cruzes & Dybå [103]: "descriptive (narrative) synthesis, quantitative synthesis, qualitative synthesis, thematic analysis, and meta-analysis."

**Qualitative coding procedure actually used (Fig. 9):** started "from a list of pre-defined categories: stability (maturity) of SUT, stability of test cases, 'cost, benefit, ROI, and need for regression testing) and a large number of raw factors phrased under the "Other" category. By an iterative process, those phrases were qualitatively coded (by applying axial and open coding approaches [105]) to yield the final result, i.e., a set of cohesive well-grouped factors." Abstraction-level heuristic: "we aimed at finding factors that would accurately represent all the extracted items but at the same time not be too detailed so that it would still provide a useful overview, i.e., we chose the most suitable level of "abstraction"".

**Weighting evidence across source types:** "By carefully combining the two chosen checklists [Host & Runeson for formal case studies; Table 7 for GL], we may be able to objective assign evidence (rigor) weights to different sources and thus synthesize evidence from all types in a more systematic manner."

### Reporting guidance (dual-audience publication strategy)

- "reporting style for scientific journals and practitioners' magazines are quite different [106, 108]. While papers in scientific journals should provide all the details of the MLR (the planning and search process), papers in practitioner-oriented outlets (such as IEEE Software) should be in general shorter, succinct and "to the point"."
- Publication strategy demonstrated (Table 11): a practitioner-facing IEEE Software article plus an extended academic journal version, per topic.
- Title advice: "In two of our review papers published in IEEE Software [9, 62], we entitled them starting with "What we know about …". This title pattern seems to be attractive to practitioners"; and "practitioners usually prefer simpler phrases for the titles of their talks at conferences or their (grey literature) reports, compared with more complex titles used in the formal literature."
- Include an implications/benefits section: "We recommend including in review papers a section about the implications of the results… and if possible, a section on the benefits of the review."
- Validate with practitioners: "we asked several active test engineers in the Turkish embedded software industry to review the review paper and the online spreadsheet of papers, and let us know what they think about the potential benefits of that review paper."

### Empirical findings worth citing

- Nine MLRs published in SE between 2015 and 2018 (Table 2). GL share of the pool ranges from **14.3%** (serious games for software process standards education, 7 sources) to **85.9%** (relationship of DevOps to agile/lean/continuous deployment, 234 sources).
- Table 2, full: technical debt 2013 (35 sources, 100% GL); iOS applications testing 2015 (21, 42.9%); when and what to automate in software testing 2016 (78, 66.7%); gamification of software testing 2016 (20, 70.0%); DevOps→agile/lean/CD 2016 (234, 85.9%); characterizing DevOps 2016 (43, 44.2%); threat intelligence sharing platforms 2017 (22, NA); serious games for SW process standards education 2017 (7, 14.3%); software test maturity and TPI 2017 (181, 28.2%); smells in software test code 2018 (166, 27.7%).
- Search-scope choices observed in those MLRs: "They included top hits 50 from Google and performed two iterations of searches" (technical debt); "The paper studied the first 50 hits provided by Google search engine" (iOS testing); "First 230 hits of Google search engine were included as it was determined that hits below that were mostly job adds" (DevOps); "search was stopped when no additional data could be extracted from new sources" (characterizing DevOps).
- Grey evidence in SE SLRs before MLRs became common: "the ratio of grey evidence in the SE SLRs was only about 9%, and the GL evidence concentrated mostly in the recent past (∼48% between the years 2007–2012)" (from the 2012 MSc thesis [50]).
- From the medical domain [26], demonstrating the reach of proper GL searching: authors searched "44 online resource and database websites, 14 surveillance system websites, nine regional harm reduction websites, three prison literature databases, and 33 country-specific drug control agencies and ministry of health websites" and "75% to 85% of their results were based on data sourced from the GL."
- Scopus scale check: "systematic review" in paper titles returned 86,525 papers overall (April 24, 2018); 401 in SE.
- Secondary studies out-cite primaries: "citation metrics to the secondary studies were higher than the papers in the pool of three SM studies (web testing, GUI testing and UML-SPE)".

---

## garousi_need_2016 — The need for multivocal literature reviews in software engineering: complementing systematic literature reviews with grey literature
**(V. Garousi, M. Felderer, M.V. Mäntylä, EASE '16, Limerick)**

**Type:** empirical study (small, sampled comparison) / position paper

**Role in corpus:** The only paper that *quantifies what an SLR loses* by excluding grey literature, by re-searching the topics of three published SE SLRs and by dissecting three MLRs to attribute each finding to grey vs. formal sources. It is the precursor that motivated the 2019 guidelines.

### Definition and tiers of grey literature

No tier model of its own. Defines GL only as "non-published, nor peer-reviewed sources of information" and "the 'grey' (non-published) literature". MLR definition matches the 2019 paper: "while SLRs and SMs use as input only academic peer-reviewed articles, MLRs in addition also use sources from the grey literature, e.g., blogs, white papers and web-pages".

Notes the origin of the term: "SLRs which include both the academic (formal) and the grey literature were termed as Multivocal Literature Reviews (MLR) in other fields, e.g., education … in the early 1990's."

### Decision criteria: when to include grey literature / when to do an MLR

The paper adopts wholesale the six-element nursing rubric of Benzies et al. [9] as its decision aid, presented as its Table 5:

> "Nursing literature suggests a rubric of six element when grey literature should be included in their area, see Table 5. We claim that for any SE area, there would be at least one 'Yes' in this rubric!"

`[EXTRACTION UNCLEAR: Table 5 — "A rubric to aid decision making on whether to include grey literature in state-of-the-evidence reviews (taken from [9])" — the table body is an image and did not survive text extraction. The prose identifies its elements only by number: elements #1 and #2 concern complexity of the intervention and complexity of the outcome; elements #4 and #5 concern low volume and low quality of evidence; element #6 is the importance of context. Items 1–5 of Table 4 in garousi_guidelines_2019 are the adopted SE version of this same rubric.]`

Prose commentary on the rubric applied to SE:
- "The importance of context (the 6th element in the rubric) has been extensively been discussed in the SE literature".
- "We think that SE is still hampered by the low volume and quality of evidence (elements #4 and 5)."
- "many of our interventions are complex with complex outcomes (elements #1 and 2) as in addition to the technical challenges we often simultaneously face challenges relating to human factors, economics, and management."

Also states when an MLR is *not* worth it: "for some areas of SE, not including the multivocal literature may not lead to missing too much knowledge, e.g., the fields related to formal methods, since the 'voice of practice' is quite limited in such areas." And, from the technical-debt case: "in the area of technical debt, there is currently little to gain by having MLRs. One cause could be that 57% of the sources of the most recent SLR (SLR2) come from Managing Technical Debt Workshop, IEEE software, Cutter IT Journal, and Agile Conference which are academic publication forums with high industry participation. Thus, the industry involvement in those forums could simply make MLRs obsolete."

### Process steps or stages defined

No MLR process is defined — the paper explicitly defers that: "the authors are planning to prepare systematic guidelines for conducting MLRs in SE based on our own experiences and by adopting guidelines of MLRs in other areas, e.g., education [5] and nursing [9]."

Its own two-part method: (RQ1) select SE SLRs that excluded GL, then search GL in their focus areas to identify what was missed; (RQ2) select SE MLRs and identify the contributions and evidence that came specifically from grey sources.

### Grey-literature search techniques

Search venues used for the RQ1 probe: "we planned to conduct the searches using the Google and YouTube search engines and major forums where practitioners post questions and discuss technical issues, e.g., Stack Overflow". Sources uncovered included books, video talks at industry conferences (e.g. Google Test Automation Conference), white papers, commercial tool documentation, webinars, consultant blog posts, and vendor sites.

### Quality/credibility appraisal criteria for grey literature

None proposed. The paper flags the absence as a problem, citing the 2012 MSc thesis [16] whose RQs were "(1) What is the extent of usage of grey literature in SE SLRs? and (2) How can we assess the quality of grey literature?"

### Caveats, traps and pitfalls

- "the inclusion of grey literature brings forward certain challenges as evidence in them is often experience and opinion based."
- "We found that source of evidence in grey literature was often opinion or experience based rather than relying on systematic data collection and analysis as done in scientific papers."
- Quoting Tom et al. [13]: "there are apparent issues of reliability and validity associated with these writings due to their diversity".
- On the ManAutoTest GL pool: "We did not find any hard core empirical evidence. The stated findings were mostly based on claims and experience. However, the source of evidence was difficult to identify as the reporting was low quality. Furthermore, replication of reported results is not possible".

### Threats to validity framework

Uses the four-category checklist of Wohlin et al., *Experimentation in Software Engineering* [50] — internal, construct, conclusion, external validity — with the definitions applied verbatim:

- **Internal validity:** "a property of scientific studies which reflects the extent to which a causal conclusion based on a study and the extracted data is warranted". Threat identified: "selection bias (i.e., randomness of the SLR studies included in our pool of objects under study). We did a random sampling for them".
- **Construct validity:** "concerned with the extent to which the objects of study truly represents theory behind the study". Mitigation: RQs and data items "carefully selected and discussed among the three researchers".
- **Conclusion validity:** "deals with whether correct conclusions are reached through rigorous and repeatable treatment". Mitigation: "we investigated three cases for each RQ and performed a synthesis for each subsequently".
- **External validity:** "concerned with the extent to which the results of this study can be generalized". Mitigation: "we selected different topics from SE to support generalization".

### Data extraction and analysis techniques

Attribution-by-source-type analysis: "we partitioned the synthesis of a major output of that MLR (factors to be considered for deciding when and what to automate in testing) by the type of source where they were mentioned in: either formal or grey literature". This partition-and-count method is the paper's principal analytical device; it also compares synthesized category sets across an MLR and two SLRs on the same topic (Tables 3 and 4).

### Empirical findings worth citing

- **Grey dominance in ManAutoTest:** "out of the total of 15 factor categories, grey sources contributed a total of 219 occurrences (instances) while academic sources discussed only a total 67 of factor instances." And: "if we were to not include the grey literature, two categories (namely: test oracle and development process) would not have existed."
- **Pool composition:** ManAutoTest MLR 26 formal / 52 grey (66% grey); TM/TPI MLR 130 formal / 51 grey (28% grey); TechDebt MLR 0 formal / 35 grey (100% grey).
- **TM/TPI:** "Overall, 57 different TM/TPI models were identified among the sources. From these sources 14 were grey literature reporting test maturity models such as TMap, Agile TMM or Test Maturity Index which would have been lost in a regular SLR".
- **Scale of the practitioner conversation** (hits, Dec 2015): 'User Interface Testing' — Google 74M, YouTube 237K, Stack Overflow 6,286. 'agile lean metrics' — 10M / 42K / 129. 'Technical Debt' — 9M / 216K / 693.
- **Wohlin's five levels of closeness between academia and industry**, applied as an argument: "Level 1: Not in Touch, Level 2: Hearsay, Level 3: Sales Pitch, Level 4: Offline, and Level 5: One Team… When the multivocal literature is not included in SLRs, the synthesis is conducted in a quite 'closed' environment (only the state of the art)… the SLR contents will be mostly in the level 1 (not in touch) or at most in level 2 (hearsay)… When grey literature is included, then the closeness can be characterized as Level 3 (Sales Pitch) or Level 4 (Offline)."
- **A recurring gap tools fall into:** "An important area missed in our SLRs focusing on UI testing, Agile metrics, and Technical debt are available tools and their features."
- **Cost argument for GL** (restated in the 2020 chapter): using GL instead of running interviews/surveys "can save research costs and also improve research quality."

---

## garousi_benefitting_2020 — Benefitting from the Grey Literature in Software Engineering Research
**(V. Garousi, M. Felderer, M.V. Mäntylä, A. Rainer; book chapter, *Contemporary Empirical Methods in Software Engineering*, Springer)**

**Type:** guideline / overview book chapter (secondary survey of GL usage)

**Role in corpus:** Broadens the frame from "MLR as a review type" to "GL as a data source for SE research generally" — it is the only paper here that catalogues the *five distinct ways* GL is used in SE research (of which MLR is only one), supplies a process model of how GL content comes into existence (and therefore where its validity threats originate), and tabulates benefits/challenges/variability dimensions.

### Definition and tiers of grey literature

Definitions carried forward: Cochrane's ("literature that is not formally published in sources such as books or journal articles"); and "According to Institute for Work & Health (2019) GL is essentially any document that has not gone through formal peer review for publication."

**SE-specific definition (the chapter's own):**
> "Grey literature in SE can be defined is any material about SE that is not formally peer-reviewed nor formally published."

**Two classifying dimensions (verbatim, callout box):**
> "Grey literature sources can be classified according to the two dimensions: expertise and outlet control. Expertise is the extent to which the authority and knowledge of the producer of the content can be determined. Outlet control is the extent to which content is produced, moderated or edited in conformance with explicit and transparent knowledge-creation criteria."

**Figure 1 tiers — this extraction preserves the figure's label text verbatim:**
- "3rd tier GL: Low outlet control/ Low credibility: such as blogs, emails, tweets"
- "2nd tier GL: Moderate outlet control/ Moderate credibility: such as annual reports, news articles, presentations, videos, Q/A sites (such as StackOverflow), Wiki articles"
- "1st tier GL: High outlet control/ High credibility: such as books, magazines, government reports, white papers"
- Axes: Outlet control (Known → Unknown, vertical); Expertise (or credibility) (Known → Unknown, horizontal); "'White' literature" occupies the Known/Known corner.
- "To emphasize: the figure is not intended to suggest discrete boundaries between the tiers."

**Table 1 — Spectrum of the 'white', 'grey' and 'black' literature (Giustini and Thompson 2010):** identical to garousi_guidelines_2019 Table 1 (journal papers / conference proceedings / books | preprints, e-prints, technical reports, lectures, data sets, AV media, blogs | ideas, concepts, thoughts).

**Discipline-relativity of the boundary (an important qualification not in the 2019 paper):**
> "Marsolek et al. (2018) treated conference papers as GL. This is because, in some disciplines, conferences accept all submitted papers with no peer review. However, in SE research at least, the highly ranked conferences have established peer review processes … Thus, the SE research community does not in general treat conference papers as GL."
> "MSc and PhD theses are often reviewed by several examiners, and therefore are also often peer reviewed. Also, in most software companies who intend to share technical reports or white papers online, such documents are almost always reviewed to some degree by peers… By contrast, the peer review of technical documents, in practice, may often be undertaken by known colleagues. Thus, in summary, we conclude that what constitutes GL depends on the standards of the respective research discipline."

**Social media tiering:** "Social media is usually 3rd level (tier) GL, in Fig. 1, but some of content sources such as Stack Overflow or Wikipedia can be considered 2nd level GL as there are informal controls and other people can edit and improve the content."

**Quantity/quality trade-off along the tiers:** "as one lowers the quality threshold, i.e., move from tier 1 to 3 (in Figure 1), the amount of available literature grows to enable large-scale quantitative analysis."

GL producers: same seven-category list as garousi_guidelines_2019 (attributed here to Giustini and Thompson 2010).

### Decision criteria: when to include grey literature / when to do an MLR

**"GL materials should be considered when Williams and Rainer (2017):" (Table 3, verbatim — this is the Williams & Rainer eight-condition variant of the Garousi seven-question aid):**

1. "the topic of the research is complex"
2. "the topic is not 'solvable' by using only the peer--reviewed research literature"
3. "there is a lack of quantity and/or quality of best evidence from research, or a lack of consensus in the research"
4. "context is important to the study of the topic"
5. "the researcher intends to challenge existing assumptions and findings, either in research or practice, or both"
6. "a synthesis of practice and research would be valuable to either or both communities;"
7. "the researcher intends to consider trends over time, and"
8. "the researcher seeks to better understand, assess or demonstrate the impact of research in relation to a particular topic."

Credibility bar for GL to be usable: Williams and Rainer (2017) "recommend that GL materials 'need to be rigorous, relevant, well written and experience based for them to be considered credible to [SE] researchers'."

### Process steps or stages defined

**Five ways of using GL in SE research** (the chapter's own taxonomy, Conclusion §6): "(1) Analyzing GL materials to answer GL-specific RQs; (2) Using certain GL materials for qualitative studies; (3) Using certain GL materials quantitative studies; (4) Citing GL materials; and (5) Systematic reviews involving GL."

**Six secondary-study types** (Figure 6) — same taxonomy as garousi_guidelines_2019, restated with the two distinguishing axes: "the difference between an MLR and a GLR is that, while the former reviews both GL and published literature, the latter reviews only the GL. The difference between an MLM and an MLR is that, while both analyze GL, the former reviews only classified the pool of sources, the latter synthesizes the evidence from those sources in addition."

**Process model of GL content generation (Figure 4, simplified from Rainer and Williams 2019):**
`Software engineering activity → [Author: Experiencing / Believing → Self-reflection / Reasoning] → Writes / Shares → Grey-literature materials`, with `Opinion/beliefs from/of peers/other practitioners` influencing the author.

Definitions of the three internal processes, verbatim:
- "**Experiencing** is an active engagement between the author and the empirical world. Experiencing can take place at different levels of scope and resolution, e.g., directly experiencing programming in contrast to experiencing the 'behavior' of a software organization. The formation of experience is influenced by prior beliefs and in turn influences those beliefs; and is influenced by self-reflection and reasoning."
- "**Beliefs** are defined as conceptions, personal ideologies, worldviews and values that shape practice and orient knowledge."
- "Underpinning the processes that occur within the author, the author has the ability to **self-reflect** (to some degree) and to **reason** (to some degree) about her or his experiencing, beliefs and reporting."

**MLR process pointer:** "The guidelines for MLRs in SE cover planning, conducting and reporting the review. The step on conducting an MLR comprises guidelines for the search process, source selection, study quality assessment, data extraction and data synthesis."

### Quality/credibility appraisal criteria for grey literature

**Table 5 — Quality assessment checklist for GL in SE.** Reproduced verbatim from garousi_guidelines_2019 Table 7 (criteria: Authority of the producer, Methodology, Objectivity, Date, Position w.r.t. related sources, Novelty, Impact, Outlet type; identical questions and identical 1 / 0.5 / 0 tier measures). See the full table under garousi_guidelines_2019 above.

Scoring guidance added here:
> "For each type of GL, the relevant quality criteria have to be selected, adapted and finally assessed, which can for instance be done on a two-point Likert scale with values 'yes' or 'no'… For instance, the number of online comments to measure the impact only exist for source types open for comments like blog posts, news articles or videos. A highly commented blog post may indicate popularity, but on the other hand, spam comments may bias the number of comments, thus invalidating the high popularity."

### Caveats, traps and pitfalls

**Table 4 — Challenges of working with and using GL in SE research (Rainer and Williams 2019), verbatim, all rows:**

| Challenge theme | Concrete challenges |
|---|---|
| **Foundations** — e.g. there are a lack of… | • Formal definitions of GL and GL materials<br>• Formal models of GL materials and content, in particular: a data model of GL materials and content; a process model of the creation, review and publication of GL materials and content<br>• Frameworks for evaluating the quality of GL materials and content, and classifying those materials and content |
| **Inherent nature of GL materials** — There are challenges managing… | • The very large quantity of GL materials<br>• The variability of GL materials<br>• The uncertain process for generating, publishing and revising the content of GL materials |
| **Resources** — There are a lack of… | • Central repositories of GL materials<br>• Tools to work with GL materials and content, for example: to select the higher-quality documents when performing a search; and to select particular types of GL materials e.g. those reporting experience, values, explanations etc.<br>• Datasets and corpora of GL materials |
| **Quality-assurance** — "While some efforts have started, e.g. Garousi et al. (2019), there is a shortage of:" | • Well-developed and accepted checklists for the quality assurance of various aspects of GL materials including: the author; the document; the content of the document e.g. claims; the readers' assessment of the credibility of the document; the readers; the readers' feedback on the document e.g. comments, shares, up-votes |
| **Methodology** | • The evidential value of blog-like content<br>• The appropriate research methods to use with GL materials and content |

Further warnings:
- **The IPCC cautionary tale:** "GL should also be treated with caution and cross-checked with other sources. For example, an assessment by the Intergovernmental Panel on Climate Change (IPCC) of climate science in 2007 was subsequently criticized by the Inter-Academy Council (IAC)… the IAC reported that part of the IPCC report contained statements based on little evidence, and the use of GL in that assessment 'sparked controversy'."
- **GL cannot replace primary empirical work:** "we raise some caution about how far one can go (scientifically) with GL-based evidence. While such evidence could clearly complement empirical studies in SE, it cannot substitute conventional data gathered in traditional empirical studies."
- **Where the validity threats originate:** "These descriptions are obviously filtered through the processes that occur between experiencing and reporting in the model. Many of these processes are internal to the GL author. These internal processes therefore introduce threats to validity relating to subjectivity, and also challenges to research due to the invisibility of these processes. Peer review helps to counteract these threats by independently reviewing the outputs from the internal processes, rather than reviewing the processes themselves."
- **Reported findings are incomplete:** "It is very likely that the information reported will be incomplete in some way(s), which could also be the case for papers written by researchers."
- **What GL evidence is and is not** (from ManAutoTest): "the type of evidence found in GL were generally either: valid viewpoints, ideas of cause-effect relationships that could be scientifically studied, as well as explanations of why and in what context certain heuristics worked while others did not. We did not however find any sophisticated (hard-core) empirical evidence, such as controlled experiments, in the GL. The stated findings were mostly based on claims and experience. Also, the source of evidence was difficult to identify as the reporting was low quality. Furthermore, we observed in our study that replication of the GL results was not generally possible."

### Data extraction and analysis techniques

**Table 2 — Dimensions of variability in GL materials (Rainer and Williams 2019)** — the extraction-planning checklist for what a grey source may contain:

| Dimension | Explanation and examples |
|---|---|
| Quality of written language | For example, the formality of language. |
| Natural language | Most research appears to focus on English but there are, of course, a very wide range of other languages to consider. |
| Media | Video, Text, Static image, Animated image, Audio, Presentations |
| 'Encoding' of the media | Text with, for example, HTML; (Proprietary) binary formats e.g., Adobe PDF |
| Structure | Headings, sub-headings |
| Content | Reasoning, e.g., claims, reasons, arguments; Opinions; Reporting of actual experience, perhaps as a 'war story'; Code-related information e.g., source code, documentation, API; Web links e.g., URLs; (Tables of) data; Citations |

**Qualitative analysis:** "With qualitative methods we mean analysis methods where humans read, analyze, and classify GL text in order to produce knowledge. When using a qualitative approach, one can use approaches presented in qualitative research guideline books and articles, e.g., those by Patton (2002) and Cruzes and Dyba (2011)." Exemplars: argumentation-scheme analysis of a single blog post (Rainer 2017 — "may be understood as a case study to complement the survey-like studies of MLRs and Grey Literature Reviews (GLRs)"); case-study-on-secondary-data of startup pivots (Bajwa et al. 2017); content classification of developer blogs (Parnin et al. 2013) and YouTube videos (MacLeod et al. 2015).

**Quantitative analysis:** "research methods range from simple frequency counting to advanced machine learning used for natural language processing such as … topic modeling LDA (Latent Dirichlet Allocation) and … word embeddings. Much of the quantitative analyses of GL appears to concentrate around a small number of sources, principally Stack Overflow. This may be because the data is easy to access and relatively well structured."

**Context model for extraction (Figure 2, UML).** "Technical information (writing)" splits into "Paper in academic literature" and "Artefact in grey literature"; an artefact "could be a Blog-like document, or Video, or White-paper"; per Rainer (2017) it "could include Conclusions which in turn may be backed (supported) by Reasoning, Experience, and/or Evidence; and illustrated by one or more Examples." Attributes modelled per artefact type include title, text_contents, tags, date_written / date_uploaded, abstract, figures — a de facto minimum metadata set for grey sources.

### Empirical findings worth citing

- **Table 7 — 18 SE review studies involving GL, with GL share** (a strong citable dataset):

| Review topic | Type | Year | # AL | # GL | % GL |
|---|---|---|---|---|---|
| Technical debt | MLR | 2013 | 0 | 35 | 100% |
| iOS applications testing | MLR | 2015 | 12 | 9 | 42% |
| When to automate in testing | MLR | 2016 | 26 | 52 | 66% |
| Gamification of SW testing | MLR | 2016 | 6 | 14 | 70% |
| Relationship of DevOps to agile | MLR | 2016 | 33 | 201 | 86% |
| Characterizing DevOps | MLR | 2016 | 24 | 19 | 44% |
| Test maturity and test process improvement | MLR | 2017 | 130 | 51 | 28% |
| Involving security in DevOps (DevSecOps) | MLR | 2017 | 2 | 50 | 96% |
| Choosing the right test automation tool | GLR | 2017 | 0 | 53 | 100% |
| Smells in SW test code | MLR | 2018 | 46 | 120 | 28% |
| Serious games for SW process | MLR | 2018 | 6 | 1 | 14% |
| Pains and gains of micro-services | GLR | 2018 | 0 | 51 | 100% |
| Relevance of software engineering research | MLR | 2018 | 33 | 13 | 28% |
| Ethics in requirements engineering | MLR | 2018 | 98 | 34 | 26% |
| Function-as-a-Service software development | GLR | 2018 | 0 | 50 | 100% |
| Adopting the Scaled Agile Framework (SAFe) | MLR | 2018 | 52 | 47 | 47% |
| Monolithic repositories (Monorepos) | MLR | 2018 | 2 | 21 | 91% |
| Use of DevOps for e-Learning systems | MLR | 2018 | 3 | 22 | 88% |

  (Note: two rows in the source table are internally inconsistent — "Smells in SW test code" 46/120 is labelled 28% and "Relevance of software engineering research" 33/13 is labelled 28%; reproduced as printed.) Trend: "9 out of 18 papers were published in 2018."
- **Community size asymmetry:** "there were about 23 million software developers worldwide in 2018, and that number is estimated to reach 27.7 million by 2023"; "'4,000 individuals' are 'actively publishing in major [SE] journals'" — "on average, there is one SE academic for every 5,750 practicing software engineers".
- **Growth rate of GL:** "according to a paper by Farace (1997), the growth rate of GL was 3-4 times that of conventional peer-reviewed literature."
- **Scale of SE-specific GL:** Tumblr "alone has 440m blogs"; WordPress "Users produce about 136.2 million new posts and 77.7 million new comments each month"; curated lists of ~650 SE blogs (≈250 by individuals), 185 corporate software blogs, 75 software-testing blogs; and, for microservices, "a … massive proliferation of grey literature [on microservices], with more than 10,000 articles on disparate sub--topics".
- **GL is indexed more than assumed:** "Marsolek et al. (2018) found that GL was present in the majority (68%) of the subject databases and almost all institutional repositories (95%)."
- **Highly-cited GL in SE:** the NIST/RTI report "The economic impacts of inadequate infrastructure for software testing" — "cited about 700 times accordingly to Google Scholar (October 2019)"; and the Standish Group "Chaos" reports.
- **Table 3 — Benefits of utilizing the GL in SE research (Rainer and Williams 2019), verbatim:**
  - In general, GL materials: "1. provide information on practitioners' contemporary perspectives on important topics relevant to practice and to research, and 2. promote the voice of practitioners".
  - In particular, GL materials (such as blog-like documents) provide (access to) information on the practitioner's: "1. experience and inexperience of theirs' and others' software practice; 2. motivations for that practice; 3. values relating to that practice; 4. emotions relating to that practice; 5. beliefs about software practice; 6. empirical data from their practice, and 7. explanations of that practice."
  - In providing such information, GL materials: "1. help bridge the divide between research and practice; 2. complement the research literature by 'filling in gaps' in research, and 3. help to counteract bias findings, as a result of publication bias in the research literature."
  - Methodologically, the use of GL materials in research helps researchers to: "1. assess and address publication bias; 2. compensate for the (un)availability of other sources of evidence; 3. increase research visibility into actual software practice; 4. access harder-to-access practitioners e.g. due to logistics, or demographics; 5. gather information for the research in a non-invasive way; 6. scale-up their research to, or with, larger samples; 7. complement and triangulate with, other sources of data; 8. provide an audit trail of their research, and 9. replicate each other's study through public access to original data."

---

## adams_shades_2017 — Shades of Grey: Guidelines for Working with the Grey Literature in Systematic Reviews for Management and Organizational Studies
**(R.J. Adams, P. Smart, A.S. Huff, International Journal of Management Reviews 19 (2017) 432–454)**

**Type:** guideline, derived from an empirical review of reviews (140 systematic reviews in management and organization studies, 2003–2014)

**Role in corpus:** The origin of the two-dimensional "shades of grey" tier model that Garousi imported into SE, and the source of a 12-guideline decision aid organised by systematic-review step. It is also the only paper here with evidence on how often reviewers include/exclude grey literature and *why they say they exclude it*.

### Definition and tiers of grey literature

**General definition (the paper's own):**
> "grey literature is composed of knowledge artefacts that are not the product of peer-review processes characterizing publication in scientific journals (Lawrence et al. 2014)."
> "the diverse and heterogeneous body of material available outside, and not subject to, traditional academic peer-review processes"

**Narrow (Schöpfel 2011), quoted verbatim:**
> "manifold document types produced on all levels of government, academics, business and industry in print and electronic formats that are protected by intellectual property rights, of sufficient quality to be collected and preserved by library holdings or institutional repositories, but not controlled by commercial publishers i.e., where publishing is not the primary activity of the producing body."

**Broad (Levin 2014, librarian), quoted verbatim:**
> "anything that has not been published in a traditional format or, in library parlance, lacks bibliographic control, meaning it can be hard to look up. This includes things such as conference proceedings, conference posters, dissertations and theses, government/institutional reports and raw data . . . luckily, much of it is now online . . . 'Institutional Repositories' . . . Government agencies – federal, state, provincial, etc. – . . . generate many reports that contain excellent data . . . [B]logs, Tweets or Facebook postings . . . can also be a great place to locate valuable information not found elsewhere."

**Table 1 — Instantiations of the grey literature** (compiled after Bellefontaine and Lee 2013, Benzies et al. 2006, Briner and Denyer 2012, Conn et al. 2003, Lawrence et al. 2014, Levin 2014, Petticrew and Roberts 2006, Rutter et al. 2010, Thomas 2008, Tyndall 2008) — all 36 entries:

Bibliographies; Discussion papers; Newsletters; PowerPoint presentations; Program evaluation reports; Technical notes; Publications from governmental agencies; Reports to funding agencies; Unpublished reports; Dissertations; Policy documents; Rejected manuscripts; Un-submitted manuscripts; Conference abstracts; Book chapters; Personal correspondence; Newsletters; Informal communications; Census data; Pre-prints; Standards; Patents; Webinars; Publications from NGOs and consulting firms; Videos; Wiki articles; Emails; Blogs and social media; Data sets; Committee reports; Working papers; Company reports; Catalogues; Speeches; Reports on websites.

**The tier model (Figure 1, "Shades of grey literatures") — the axes, verbatim:**
> "Our observations of the range and types of grey literature included in and excluded from systematic reviews in MOS allow us to build on Kepes et al.'s (2012) taxonomy and posit gradations of grey literature using two dimensions (Figure 1). This gradation, shades of grey literature rather than discrete bands, is framed in terms of **outlet control** (the extent to which content is produced, moderated or edited in conformance with explicit and transparent knowledge creation criteria) and **source expertise** (the extent to which the authority of the producer of content can be determined)."

Predecessor acknowledged: "Conceptualizing around 'source availability', Kepes et al. (2012) propose a taxonomy of grey material that may be included in a meta-analytic review. Their four tiers describe sources from white to unidentifiable or unknown."

`[EXTRACTION UNCLEAR: Figure 1 itself is an image; the per-tier example lists inside the figure did not survive extraction. The tier semantics are fully recoverable from the prose (below) and from the SE-adapted version in garousi_benefitting_2020 Figure 1 / garousi_guidelines_2019 Table 7.]`

**Tier semantics from the prose, verbatim:**
> "Figure 1 emphasizes that boundaries between tiers tend to be fuzzy and permeable; therefore, the examples associated with each tier are only illustrative. Reviewers need to make explicit judgements about relevant grey literature on a project-by-project basis and reconsider categorization as sources and outlets for knowledge evolve. For example, the figure suggests that tweets are likely to be placed in Tier 3, since outlet and source are often unknown; however, in a closed conference of experts the source and 'publication' of tweets might more appropriately be classed as second or even first tier of grey evidence."

> "This categorization recognizes that experts generate a range of material that may be of scholarly interest. Similarly, prominent outlets sometimes publish unreviewed material written by people with unknown training and experience. **In the middle ground lie the many government reports, news articles, company publications and so on that may be of interest even though source expertise and outlet control cannot be fully determined.** In all cases there are dangers of irrelevance, mistakes and fraudulent claims, as can be the case with the white literature… but in our opinion the more significant challenges of assessing grey sources require additional strategies."

Tier 1 as the defensible-by-default band: "For relatively mature and/or bounded academic conversations, with the possible exception of some Tier 1 literatures whose inclusion is defensible on the basis of established decision rules about quality, grey literature might be excluded."

**Table 4 — grey material actually included in vs. excluded from MOS systematic reviews (verbatim, both columns):**

| Grey material **included** (Category A) | Grey material **excluded** |
|---|---|
| Annual reports, blogs, business press, case studies, commercial organizations reports, commissioned reports, community engagement toolkits, conference proceedings/papers, consultancy reports, discussion papers, economic impact studies, editorials, government departments reports, government reports, industry reports, institutional reports, international organization industry reports, key works of few 'gurus', newspaper/magazine articles, NGO reports, patient opinions, policy documents, policy-maker consultations, practitioner articles, papers and reports, business press reports, research reports, teaching cases, theses (Bachelor, Honours, Masters, and Doctoral), think-tank reports, websites and working papers | *(Category B)* Anonymous publications, articles from popular rather than academic sources, book chapters, book reviews, books, commentaries practitioner accounts, conference papers, dissertations, editorials, essays, letters, journalistic or anecdotal articles, literature reviews, monographs, news items, non-refereed publications, opinion pieces, practitioner journals, prescriptive accounts, special issue introductory pieces, trade and popular press, unpublished papers, unpublished reports and working papers. *(Category A)* Blogs, executive summaries of papers, newspaper articles, PowerPoint files, press releases, reports on the results of public consultations, reports or literature that describe implementation of consultation activities, short practitioner articles, unpublished posters, unsupported prescriptions and webmedia |

Note that the same material type (e.g. editorials, conference papers, blogs) appears on both sides — the paper's point: "The observation that Category A reviews deliberately reject some of the grey literatures indicates that selection decisions are not made indiscriminately, and active choices are pursued about inclusion and exclusion."

### Decision criteria: when to include grey literature / when to do an MLR

**Table 6 — A decision aid for deciding whether or not to incorporate the grey literature in an MOS systematic review (all 12 guidelines, verbatim, with their step labels):**

| # | Step | Guideline |
|---|---|---|
| 1 | Including grey literature | "Consider all tiers of grey literature to define and contextualize phenomena of research interest when potentially relevant knowledge is not reported adequately in academic articles, clearly stating the rationale for and source of material included in review." |
| 2 | Including grey literature | "Consider all tiers of grey literature when attempting to (a) validate/corroborate scientific outcomes with practical experience, or (b) challenge assumptions/falsify results from practice using academic research." |
| 3 | Question formulation | "Consult grey literature in formulating questions for research where practitioner or user impact is a significant purpose." |
| 4 | Locating studies | "Record and report all search decisions to support credibility of study process and findings and to build shared procedures for working with grey literature." |
| 5 | Locating studies | "Explore electronic repositories (ideally with editorial independence and professional or institutional affiliations) to identify grey literature, creating site-specific search strings as necessary." |
| 6 | Locating studies | "Deploy a semi-structured approach to identifying grey literature from generalist and specialist sites. Augment results with sources identified by experts from policy and practice." |
| 7 | Selection and evaluation | "Use fit-for-purpose quality criteria when selecting and evaluating grey literature. Develop proxy measures of quality to sort large collections of literature if necessary, but justify them in a pilot exercise that considers the relevance and potential contribution of each artefact." |
| 8 | Selection and evaluation | "Be guided by field experts in identifying sources for and evaluating grey literature, but retain decision-making independence and rationalize systematic review actions." |
| 9 | Analysis and synthesis | "Include the grey literature not as a competing form of evidence, but as supplementary and complementary evidence. Select a mode of analysis and synthesis consistent with the review question, nature of included evidence, and the intended purpose of the review." |
| 10 | Using and reporting results | "To increase report credibility for multiple audiences, consider comparative analyses, descriptive statistics, and inclusion of evidence that do not fit primary conclusions, with explanations of how decisions were made in analysis and synthesis." |
| 11 | Using and reporting results | "Unless academic and grey literatures are of similar status (as they may be in the case of reviews that include only Tier 1 grey literature), findings and confidence levels of systematic reviews of white and grey literature should be reported separately." |
| 12 | Excluding grey literature | "Exclude grey literature from reviews supporting relatively mature and/or bounded academic conversations with the possible exception of some Tier 1 literatures that are relatively easy to defend on the basis of widely acknowledged decision rules about quality." |

Also: "Where the grey literature potentially expands insight, but is judged too overwhelming to review, consider a pilot study or restrict scope in some other way to calibrate potential contribution further."

Fitness-for-purpose as the governing criterion: "A principle criterion for inclusion of grey literature, then, becomes fitness for purpose, how it fits into the ways in which the findings are likely to be used".

### Process steps or stages defined

The paper organises everything around **Denyer and Tranfield's (2009) five-step systematic review outline**, and states how each step changes with grey literature:

1. **Question formulation.** "these reviews integrate user views as part of the stakeholder community … into the formulation of the review question. This is particularly appropriate where the research topic is novel or requires contextualization".
2. **Locate relevant studies.** "Grey literature is tacitly excluded from many systematic reviews by dint of inclusion criteria restricting searches to well-established academic databases, reviewer decisions on search strings and keywords and frequently used search conventions… The decision to include grey literature thus requires conscious, explicit and different procedures, typically involving a review-specific strategy." Also: "a multilayered and semi-structured process is necessary to enable manageability, maintain control over a time-consuming process, and ensure transparency and replicability to the extent possible."
3. **Study selection and evaluation.** "source evaluation is not simply a mechanism for excluding low-quality evidence, but is also about appraising and reporting what is included so that judgement can be made about the reliability of findings".
4. **Data analysis and synthesis.** "the breaking down of individual studies into constituent parts followed by reassembly, during which novel connections between the parts are made … all undertaken in a reflective and transparent manner."
5. **Reporting and using findings.** "the findings and discussion section of the final report should descriptively summarize the salient characteristics of all included studies. These will vary, depending on the nature of the review, but typically include the time period of publications, disciplinary origins, type of literature found (theoretical/empirical/conceptual), methodology, evolution of the field over time, description of method, industry sector and geographic domain."

Review categorisation scheme used for the empirical analysis (Table 3):
- **Category A:** "Articles in which grey literature is incorporated in review findings" — 28 academic, 16 practitioner
- **Category B:** "Articles in which grey literature is recognized as available, but is explicitly excluded" — 31 academic, 0 practitioner
- **Category C:** "Articles that incorporate only the white literature and make no explicit reference to grey literature" — 65 academic, 0 practitioner

### Grey-literature search techniques

- **Specialist/technical repositories, chosen on stated grounds:** "These sources were selected on the basis of their reputation, currency and authority as well as search functionality." One review "screened 17 institutional databases, including those from consulting organizations, manufacturers associations, international research institutes and governmental organizations"; another "explored a similar range of specialist sites as well as five blogs: authority and reputation their yardsticks for selection."
- **Search strings must be rewritten for grey sites:** "Many sites providing specialized knowledge are idiosyncratic in the way they present and archive knowledge content as well as in their search functionality. They are not equally easy to navigate, and often do not have sophisticated search facilities. More flexible processes for search are needed… it may be necessary to modify or replace search strings developed for academic databases."
- **General search engines with an explicit effort bound:** "In their Google searches, both Bowen et al. (2010) and Arvai et al. (2012) reviewed the first five pages of returns, and Bertels et al. (2010) the first 500 results. Kaval's (2011) Google search returned a nominal 462,000 results, but they found only 50 actual results visible and accessible."
- **Expert solicitation:** "A more direct strategy used by reviewers, and less reliant on secondary sources, is to issue requests to practitioner and policy experts for relevant source literature… Experts queried may also be able to identify specialist websites with relative ease and professional confidence." Caveat: one such request "led to a disappointing response. Varied outcomes may be an indication of the immaturity of a field of inquiry".
- **Summary recommendation:** "we suggest deploying a semi-structured approach to identifying grey literature from generalist and specialist sites and augmenting results with sources identified by experts from policy and practice."

### Quality/credibility appraisal criteria for grey literature

The paper deliberately does **not** issue a fixed instrument; it prescribes fit-for-purpose criteria and reports what reviewers actually used.

- "the principal evaluation criteria applied in Category A reviews are **relevance** and **judgement**". Example review-specific criteria quoted: "Does the study examine antecedents of a sustainability culture?" and "Does the study identify practices aimed at embedding sustainability?"
- Three generalized guidelines, verbatim: "First, it is often necessary to use **fit-for-purpose quality criteria** when selecting and evaluating grey literature. Second, it may be necessary to develop **proxy measures of quality** to sort large collections of literature, but justify them in a pilot exercise that considers the relevance and potential contribution of each artefact. Third, it often useful to be **guided by field experts** in evaluating grey literature, but retain decision-making independence and rationalize actions."
- Graded quality reporting: "McDermott et al. (2006) classified studies as of higher, medium or lower quality on a range of criteria, and reported findings against these qualifiers."
- Explicit rejection of a single hierarchy of evidence: quality evaluation "is difficult. The field has been characterized as ontologically and epistemologically diverse … making it difficult to develop a single and agreed paradigm for evaluation, the production of which has been described as 'a forlorn hope'". And in realist/theory-led reviews, "the worth of the included study is determined only by the extent to which it contributes to discourse and pattern-building."
- Requirement that quality assessment move off the journal proxy: "One requirement for assessing grey material more systematically is that quality determinations move beyond the status of journal publication as proxy, since, by definition, grey material is not closely controlled."

### Caveats, traps and pitfalls

- **No abstracts → whole-document screening:** "grey literatures typically have no abstract, and so relevance and other inclusion criteria often cannot be determined without reviewing the entire document (Benzies et al. 2006)."
- **Method opacity:** "Scholarly studies provide methodological descriptions that facilitate evaluating quality; such assurance is usually missing in grey publications, which tend to focus on conclusions rather than the process by which they were reached."
- **Cost deters reviewers:** "Additional and less clearly defined standards add time and expense to the process of systematic review, which has deterred some researchers from using them".
- **Structural heterogeneity:** "The heterogeneity of grey literature is a specific problem that makes it less amenable to traditional forms of archiving, retrieval, analysis, synthesis, bibliographic data capture, data extraction and integration."
- **Search engines are not stable — the replicability trap, verbatim:** "Palomino et al. (2013) demonstrate the instability of search engine results. They found that, rather than repeated search generating an increasing number of results as new content is added over time, results vary at an extremely fast pace – sometimes in only a matter of hours, with variable propensity of results to be higher or lower than in a previous search." And: "Kaval's (2011) Google search returned a nominal 462,000 results, but they found only 50 actual results visible and accessible. This experience raises interesting questions about internet searches, transparency and replicability."
- **Replicability is traded for a documentary record:** "While replicability in subsequent studies may not be entirely possible when using grey literature located with a unique strategy, systematic review requirements for transparency and traceability can be met by reviewers maintaining historical accounts via a researcher diary that records all searches."
- **The conflation trap (the paper's central methodological warning), verbatim:** "grey literature begins to lose its distinctive identity and contribution when treated and analysed as an equivalent to the white literature… It is not our intention to be overly critical, but rather to illustrate a common tendency of current practice to conflate two separate bodies of literature with distinct characteristics and unique contributions. By failing to discriminate between what is and is not contributed from different sources, readers' confidence and willingness to use reported findings may be diminished."
- **Selection criteria may not be applicable to both bodies:** "it is not clear whether these criteria were applied equally to both sets of potential studies in later phases of the review. Given that one of their included studies is an annotated bibliography, it seems unlikely that the same criteria could be applied to both white and grey literature identified."
- **Individual-study quality assessment has been diluted in MOS:** "One unexpected finding of the current study is the extent to which this has been diluted in MOS by application of a journal-level proxy alone… the majority of published systematic reviews in MOS do not report evaluating quality at the level of the individual study."
- **Publication bias may also afflict the reviews:** "the same problems that afflict primary research, which include confirmatory and publication bias, may also afflict systematic reviews. That is, if the effect of including the grey literature is to diminish the strength of findings, might it not be more challenging to get these findings published too?"
- **The claim that grey inclusion improves guidance is not yet evidenced:** "It is tempting to infer that the guidance is de facto better for this inclusion… At best, this is a tenuous rationale… we lack robust, empirical, evaluative evidence from both the academic communities and the fields of practice that reviews are more impactful through the inclusion of the grey literature."

### Metadata requirements for grey sources

- "systematic review requirements for transparency and traceability can be met by reviewers maintaining historical accounts via a **researcher diary that records all searches**."
- "Cataloguing the diversity of the search and specifying sources can be challenging. Some sites do not adhere to the traditional bibliographic format to which scholarly reviewers have become accustomed. However, maintaining a documentary record of decisions and processes enables researchers to report credibly for journal submission. Such records, if made publicly available, are useful for meeting the increasingly common stipulation of funding bodies such as Research Councils (UK) and the National Science Foundation (USA)."
- Guideline 1 requires "clearly stating the rationale for and source of material included in review."

### Data extraction and analysis techniques

**Four purpose-oriented categories of synthesis (Rousseau et al. 2008), with grey literature's role in each — the paper's own mapping, verbatim:**

> "the grey literature can be used in **explanatory synthesis** to provide additional context specificity, in **aggregative synthesis** to counteract publication bias, in **interpretive synthesis** to offer a richer set of accounts and supplementary narratives, and in **integrative synthesis** to explore opportunities for triangulation and contextualization."

Exemplar methods named per category: "aggregative (e.g. meta-analysis), interpretive (e.g. meta-ethnography), integrative (e.g. content analysis) and explanatory (e.g. [critical] realist) approaches."

- Interpretive/integrative predominate with grey material: "In the Category A reviews … integrative and interpretive approaches to synthesis predominate. They principally deliver narrative-style reports using, though sometimes adapting, qualitatively oriented methods (e.g. variations in content and framework analytic and comparative approaches). Narrative summaries allow a highly flexible method, and reviewers appear to be taking advantage of this flexibility, though it appears they may lack awareness of alternative approaches."
- Meta-analysis is not available for heterogeneous grey data: "Meta-analysis … can be understood as a form of survey research in which research reports, rather than people, are surveyed …; it requires homogeneous quantitative data."
- **Keep evidence types separate during synthesis (verbatim):** "In analysis and synthesis, it can be helpful to treat different categories of evidence separately. We believe, as already stated, that this approach should be used more often, because it preserves the unique qualities of each evidence type, provides evidence from each type that might be used to help interpret the other (akin to the 'reciprocal translation' of meta-ethnography discussed by Noblit and Hare 1988) and ensures that conclusions cannot be erroneously attributed to evidence sources".
- Grey as complement, not competitor: "we propose, where appropriate, the inclusion of grey literature not as a competing form of evidence, but as supplementary and complementary."
- Field-maturity determines the synthesis purpose: in **mature fields**, "the grey literature enriches contextual understanding"; in **emergent fields** ("characterized by inconsistency and proliferation of constructs, a widely distributed or fragmented body of knowledge, lack of a universal language, and absence of coalescing and binding theories"), "the purposes of this type of review are interpretation (building higher-order theoretical constructs) and integration (synthesizing across different methods to answer specific questions)."
- Coding at the level of practice, with support level recorded: "Bertels et al. (2010) coded data at the level of 'sustainable practice', coding each practice that they uncovered in terms of level of empirical support. In addition to reporting empirically supported practices, they were able to include practices where practitioner knowledge led extant theory as well as instances where academics had proposed practices that had not been directly used or tested in practice."
- Recommendations from grey-inclusive reviews are expected to be "heuristic rather than algorithmic" (Denyer and Tranfield 2009).

### Empirical findings worth citing

- Sample: 140 systematic reviews (124 academic MOS + 16 practitioner reviews from NBS, EPPI-Centre, Campbell Collaboration), published 2003–2014.
- **Inclusion rates:** "Approximately 23% of the included academic reviews incorporate grey literature (Category A), approximately 48% acknowledge it as at least a potential source (Categories A and B), and 77% exclude it (Categories B and C). **All 16 (100%) of the practitioner reviews include grey literature (Category A).**"
- Category C (no mention of grey literature at all) "account for just under 46% of the total of our sample reviews."
- **Most/least cited grey types:** "The most frequently cited grey material in the Category A reviews are conference proceedings and papers, (doctoral) theses and working papers. The least frequently cited include blogs, newspaper/magazine articles and the business press."
- **Stated reasons for exclusion:** Category C reviews restrict to "'refereed international journals'", "'internationally esteemed journals'", or "'peer-reviewed journal articles'"; "The (often tacit) presumption in Category C reviews is that scholarly journals and, in particular, the double-blind peer-review process, are a reliable proxy for quality." For Category B, "**Manageability of the review task is the critical concern**, often in the face of an overwhelming volume of academic literature… reviews are made more manageable by defining restrictive search criteria."
- **Excluders' own regret:** "in a number of instances where authors reflect on the potential of grey literature, they also point to the loss of relevant input to the review, and the additional information that grey literature might contribute… Pittaway and Cope (2007) conclude that key aspects of their study were somewhat under-represented owing to their inclusion criteria and argue that future studies would benefit from examining grey literature in more detail."
- **A directional difference between white and grey findings:** "Peloza and Yachnin (2008) … note that results in the academic literature tend to show a less positive relationship between sustainability and financial performance than do grey reports." And: "grey sources focused more than white on intermediate outcome metrics."
- **Complementary coverage:** "Of the 20 environmental impact tools identified by Kaval (2011), 12 were identified in the white literature, one in the grey and the remainder across both literatures. Furthermore, within the respective literatures practitioners and academics differed in which tools were the focus of their attention".
- **Proposed evaluation experiment (still open):** "future researchers might consider running trials in which the same question is addressed, but by separate teams, one empowered to include the grey literature, the other not."
- **Definition of publication bias used:** the 'file drawer' problem exists when "'research that appears in the published literature is systematically unrepresentative of the population of completed studies'", "a tendency for journals to publish positive rather than weakly significant or neutral findings".

---

## neto_multivocal_2019 — Multivocal literature reviews in software engineering: Preliminary findings from a tertiary study
**(G.T.G. Neto, W.B. Santos, P.T. Endo, R.A.A. Fagundes, ESEM 2019)**

**Type:** empirical study (tertiary study over 12 MLR/GLR secondary studies, 2009–April 2019)

**Role in corpus:** The only tertiary study of MLR practice in SE — it establishes empirically that early SE MLRs were conducted with SLR guidelines and therefore skipped grey-specific quality assessment and synthesis, and it names that gap as a validity threat to the whole body of MLR work.

### Definition and tiers of grey literature

No tier model of its own; it identifies the absence of one for SE as a research gap: "Adams et al. [23] presents a GL classification scheme in the context of management and organisation studies (MOS). A classification of GL data sources in the context of SE may avoid inconsistencies in future studies."

GL definition adopted verbatim from Schöpfel [6]: "grey literature stands for manifold document types produced on all levels of government, academics, business and industry in print and electronic formats that are protected by intellectual property rights, of sufficient quality to be collected and preserved by library holdings or institutional repositories, but not controlled by commercial publishers i.e., where publishing is not the primary activity of the producing body".

MLR definition: "The MLR study is a type of SLR that includes GL. These studies are considered very useful as it provides an overview of the state of the art and the state of practice in a target area".

Study-type classification used for screening: the Garousi et al. six-type scheme — GLM, GLR, MLM, MLR (these four terms formed the search string).

### Decision criteria: when to include grey literature / when to do an MLR

Applies Garousi's Table 4: "Garousi et al. [5] present seven questions to assist researchers in the decision to include GL in secondary studies. At least one of these questions should be answered as 'yes' for GL to be included in the study."

**Three empirically-derived motivation themes** (thematic analysis, Braun & Clarke), the paper's own contribution:

1. **"Lack of academic research on the topic"** — "Based on the studies analysed, this is the main motivation for conducting MLR studies… a total of nine codes were assigned to this topic." Mapped to Garousi's question 2: "Is there a lack of volume or quality of evidence or a lack of consensus of outcome measurement in the formal literature?"
2. **"Evidence in the GL"** — built from six codes; mapped to Garousi's question 7: "Is there a large volume of professional sources indicating a high interest of the practitioner in a topic?"
3. **"Emerging research on this topic"** — "We observed GL had been included in the researches due to the novelty of the research topic. We used a total of three codes to build this theme." Explicitly *not* covered by Garousi's list: "We did not observe any relation of this theme with the questions proposed by Garousi et al. [5]."

Exclusion case reiterated: "Garousi et al. [5], for example, presents the topic of formal methods research, which is a well-defined topic in the academic literature; this way GL can be excluded from its studies."

Counter-argument recorded: "there are open discussions about the inclusion of the GL in SE SLRs because studies from GL search 'may be relatively poor quality, so excluding them will be equivalent to excluding low-quality papers' [7]."

### Process steps or stages defined

The tertiary study's own protocol (Kitchenham et al. [2] guideline): research questions → inclusion/exclusion criteria → data sources and search strategy → data extraction → synthesis of data (thematic analysis, five Braun & Clarke phases: familiarising yourself with your data; generating initial codes; searching for themes; reviewing themes; producing the report).

Inclusion criteria (verbatim): "(IC1): studies in the area of SE (We used the classification proposed by Software Engineering Body of Knowledge (SWEBOK) [12]); (IC2): the article is peer reviewed (journal article, conference document); and (IC3): secondary studies that explicitly state the inclusion of GL (We used the classification of secondary studies proposed by Garousi et al. [5])."

Exclusion criteria (verbatim): "(EC1): the study is not written in English; (EC2): Incomplete documents, drafts, documents of compilation of proceedings, documents only accessible through the purchase, and short papers; (EC3): it is not characterized as a secondary study with inclusion of GL…; and (EC4): the study is not in the area of SE".

Data extracted per study: "(1) publication year; (2) type of venue: conference or journal; (3) the review type based in classification proposed by Garousi et al. [5]; (4) the review topic based in classification proposed by SWEBOK [12]… (5) motivations for include sources of GL; (6) whether the authors mentioned the types of primary studies included, and if so, which types; (7) search engines used for search for GL; and (8) the guideline it has been used by researchers to conduct the MLR study."

### Grey-literature search techniques

Empirical finding on what MLR authors actually used: "We observed that 83% (10/12) of the studies used Google's regular search engine to perform their searches." One study used both Google and Google Scholar "but they did not make clear what mechanism was used to search GL." One study "manually sought case studies on the implementation of the Scaled Agile Framework (SAFe) on its official website."

Gap identified: "We observed that all studies used only automatic searches to identify GL, except study P14 that conducted manual searches… Future studies identifying a set of websites as well as other types of sources that can be used to search GL can help in conducting MLR studies." And: "Future researchers interested in conducting MLR studies should have a body of knowledge established in the context of manual and automatic searches."

### Quality/credibility appraisal criteria for grey literature

No instrument proposed. Names the gap as its principal finding:

> "The quality evaluation of the primary studies is an important step of the research protocol in SLR, as it provides greater reliability to the results of the study, besides avoiding the bias of the researchers [2]. According to Kitchenham et al. [2], this is a challenging task in the research protocol as there are several criteria available to evaluate the quality of the studies and there is no agreed, no standard definition of study 'quality'. Garousi et al. [5] also consider this phase challenging in studies including GL, because, unlike the scientific literature, GL has studies from several sources, such as videos and blog posts for example."

### Caveats, traps and pitfalls

- **The headline warning (abstract, verbatim):** "The MLR studies were conducted using guidelines for performing SLRs. What we consider to be a threat to the validity of these studies, since guidelines to conduct SLR studies do not provide recommendations for quality analysis and synthesis of primary studies, including GL."
- Restated in the conclusion: "only the guideline proposed by Garousi et al. [5] proposes recommendations for quality analysis and synthesis of GL data sources… we consider a serious threat to the validity of these studies, the quality analysis and the synthesis of the primary studies. Thus, we strongly recommend that future MLR studies use the guideline proposed by Garousi et al. [5] so these threats could be mitigated."
- **Two studies cited a paper that contains no guidance:** "The P9 study state to have used the study [4]. However, this study did not propose any recommendations for conducting MLR studies; it only states the importance of GL for secondary studies in SE." Same for Ogawa et al. [20] in P12: "however this study did not offer any recommendations on how to conduct MLR studies." "Studies P14 and P15 did not use any study as a reference for conducting the MLR study."
- **Synthesis is frequently skipped:** "According to Cruzes and Dyba [21], a secondary study that does not perform a data synthesis should be classified as a scoping study. According to the authors, little attention is paid to the synthesis process in secondary studies."
- **No agreed GL taxonomy for SE:** "We note that there is no consensus among GL data sources in the context of SE."
- **Ampatzoglou's threat framework may not transfer to grey material** (an important limitation quoted verbatim): "According to Ampatzoglou et al. [22] 'we believe that our results are generalizable to good quality papers in the software engineering domain, but not necessarily to grey literature, other venues, and other disciplines'."

### Threats to validity framework

Uses **Ampatzoglou et al. (2018)**, "that provides a set of validity threats in review studies in the context of SE" — the SE-secondary-study-specific threat classification scheme "and a set of mitigation actions for these threats." Threats declared by the authors:
- Search-string completeness: "our search string was defined based on the definitions of secondary studies proposed by Garousi et al. [5]. However, the research including GL is in its initial stage in this way we can not guarantee that using only the definitions of secondary studies proposed [5], we would identify all published studies".
- Criteria defined by a single researcher (mitigated by two-researcher application + third-researcher conflict mediation).
- No quality analysis of the selected studies: "which can be considered a serious threat to our study. However, we observed that 67% of the studies analysed were published in important venues of SE, such as Information Software Technology (IST), Journal of Systems and Software (JSS), and Evaluation and Assessment in Software Engineering (EASE) conference."

### Data extraction and analysis techniques

Thematic analysis per Braun and Clarke [13], tool-supported with ATLAS.ti. Coding history reported transparently: "We analysed the studies in two rounds. First, all the studies were analysed, generating a list of 24 codes. Second, another reading was performed. Finally, 22 codes were generated in this step." Then: "the codes generated in the previous step were grouped into a preliminary list of themes. Four themes were defined, totaling 18 codes. Four codes did not fit into any of the four themes set, these were grouped into a theme called 'miscellaneous'." Theme refinement collapsed "lack of academic studies on this topic" and "lack of secondary study on the topic" into one theme.

Data-corpus vocabulary used verbatim: "Data corpus refers to all data used for an analysis; in our case the secondary studies. And the data set may correspond to a particular topic of interest within the data corpus; in our case, the motivation of studies to include GL."

### Empirical findings worth citing

- **Only 12 SE secondary studies including GL** found in 2009–April 2019 (from 56 raw hits across six engines; 43 after deduplication). "The conducting of MLR studies is still in its early stages".
- Year distribution: "25% (3/12) … published in 2016, 25% (3/12) in 2017, 42% (5/12) in 2018, and 8% (1/12) in the year 2019."
- Venue: "58% (7/12) were published in journals, and 42% (5/12) were published in conferences."
- Type: "83% (10/12) of them are MLR, and 17% (2/12) are GLR." Also: "From the studies classified as MLR, in three of them, the inclusion of the GL was only part of the study, other research methods were also applied."
- SWEBOK topic: "33.3% (4/12) … software testing, 33.3% (4/12) as software design, 17% (2/12) software engineering models and methods, 8% (1/12) software engineering economics, and 8% (1/12) software requirements."
- **What counts as GL in practice:** "Three studies did not present the classification of data sources used as GL. We noted that four studies classify their data sources as internet articles and white papers." Other named source types across the pool: YouTube videos, tools, blog post, books, industrial journal, industrial technical report, report, and website.
- **Guideline provenance:** the MLRs used, variously, Petersen et al. mapping guidelines [14][15], Kitchenham & Charters [16], Templier & Paré [18], Tom et al. [19], Ogawa & Malen [20], a pre-print of Garousi et al. [17] — "all studies were conducted before the publication of the guideline for conducting MLR studies proposed by Garousi et al. [5]."
- Prior tertiary landscape: Rios et al. "identified 25 tertiary studies classified as SE between the years of 2009 and 2017" and "have not identified any tertiary studies analyzing the use of GL in secondary studies in SE."
- Motivation statistic on the research/practice gap: 23M developers (2018), ~4,000 actively publishing SE researchers, "one SE academic for every 5,750 practising software engineer".

---

## lopez_multivocal_2026 — Multivocal Literature Reviews in Emergent Research Areas: An Experience Report
**(L. López, C. Farré, R. Akbarilalaei, X. Franch, WSESE '26, Rio de Janeiro)**

**Type:** experience report (ongoing MLR on GenAI agents in Agile project management; search/selection/quality-assessment phases complete)

**Role in corpus:** The most recent paper, and the only one that (a) treats **preprints** as a distinct grey-literature class requiring their own search, replacement and appraisal rules, (b) documents how practitioners are actually searched on LinkedIn/Reddit/Medium, (c) reports a survey of how 59 recent MLRs operationalised Garousi's stopping criteria and quality thresholds, and (d) proposes an **iterative ("agile") MLR cycle** for fast-moving topics.

### Definition and tiers of grey literature

No new tier model — adopts Garousi et al. [8]. Its definition of GL: "non-peer-reviewed publications (preprints, white papers, standards, . . . ) or digital channels (technical blogs, online discussions, social media posts, . . . )… collectively known as grey literature (GL)".

**Preprints as a distinguished GL class (this paper's contribution):** "Mention is needed for a special type of GL: preprints. Preprints are becoming increasingly important in many areas where innovation speed is paramount (Buckley et al. [3] report up to 60% of primary studies being preprints in recent literature surveys in the realm of LLMs), which fits with the requirements of MLRs (in comparison to SLRs). Therefore, it can be said that MLRs and preprints are growing together".

The paper operationally treats **three** source classes with different rules: white literature; preprints; other GL.

### Decision criteria: when to include grey literature / when to do an MLR

> "Both Garousi et al. [8] and Neto et al. [19] identified similar scenarios in which an MLR is preferred over an SLR: **when the topic is emerging, when practice is evolving faster than scholarly publications, or when practitioner perspectives are central.**"

Applied to their own case: "we decided to conduct an MLR [8] instead of an SLR [12] due to the fast-evolving nature of the topic and the diversity of available sources. Many GenAI contributions appear first in open repositories (e.g., arXiv) or other non–peer-reviewed formats, while valuable insights also emerge from practitioners."

Kitchenham et al.'s (2023) stricter counter-position is recorded verbatim: "Kitchenham et al. [13] recommend a selective, evidence-based selection of GL, requiring **auditability, traceability, and reproducibility**. They suggest that blogs and other social media posts be examined only through qualitative analysis, and that the insights derived from them should not be aggregated with evidence from either white or other GL."

### Process steps or stages defined

Follows Garousi et al. [8] step-for-step (search approach → databases and sources → source selection → selection process → quality assessment), then adds an **iterative/cyclical MLR process**. New cycle steps, verbatim:

1. "Exclude duplications from previous cycle."
2. "Analyse newer version of a source (i.e., newer preprint version or white version of a preprint). If the source from a previous cycle was excluded, then the newer version should be revised in case it includes new evidence that fits with our inclusion criteria. If so, then the new version will be included. If the older source was already included, the newer version will replace the older."
3. "Process sources. For the new sources, the quality assessment is performed and data is extracted. For the newer versions of a previously selected source, the quality assessment and the data extraction form is reviewed."
4. "Update Analysis and Synthesis."

Rationale: "Given the rapid evolution of the topic, we anticipate the need to replicate the review multiple times to capture newly emerging sources… we designed a cyclical process that allows systematic repetition of all MLR stages… Each cycle follows the same predefined protocol, enabling consistency across iterations".

**Preprint replacement rules, verbatim:**
> "Preprints need to be replaced by their peer-reviewed versions when available, following these rules:
> • If a peer-reviewed version is found and accessible, it is added to the sources found and it replaces the preprint.
> • If the preprint is accepted in a peer-reviewed venue but it is not available yet (e.g., only listed in an upcoming conference program), the preprint is retained, but its category is changed to 'White'.
> • If no peer-reviewed version is found, the preprint is retained."
> "To identify whether a preprint has a peer-reviewed counterpart, we first followed the information provided by the authors in the open repository entry (authors use notes to trace publication venues). If the white version was not found, we searched in Google Scholar, DBLP, and Google."

**Two-track selection screening, verbatim:** "For white literature and preprints, the selection process was performed iteratively: first we applied the inclusion and exclusion criteria reading only the title, next we used the abstract, and last we screened the text, basically reading introduction and conclusions and occasionally skimmed the rest of the paper if deemed necessary. For the rest of GL, we checked the criteria following a single-step approach consisting of source fast reading. In case of exclusion, the concrete criterion is recorded for traceability."

**The seven lessons learned, verbatim:**

1. "Use Google Search as a proxy to retrieve practitioner contributions from LinkedIn, Reddit, and Medium by appending the substrings 'site:linkedin.com/pulse', 'site:reddit.com', and 'site:medium.com', respectively."
2. "Adapt the Scopus search string to the specificities of Google search. Consider shortening the search string, changing the order of the sought concepts (AND clauses) and simplifying the concept terms (OR clauses). Piloting is necessary to obtain the final version."
3. "Use Scopus and arXiv advanced search capabilities to search for preprints using the same complex query string as in the white literature."
4. "As part of the source selection process, publication status of preprints need to be carefully checked. If published, they need to be replaced by their peer-reviewed versions when available."
5. "Operationalise the quality critera before the assessment including objective/measurable indicators."
6. "Exclude GL that fails to meet a predefined minimum threshold. In the case of preprints, assess their quality using the same instrument as white literature."
7. "Define a protocol to identify and include new sources, preparing the selection and data collection instruments to easily adding new data."

### Grey-literature search techniques

- **Sources by class:** "we used Scopus for white literature, while for GL we used Google as main engine, complemented with arXiv and Scopus preprints (for preprints), and LinkedIn, Medium and Reddit for other source types."
- **Stopping criteria combination, verbatim:** "For GL, we combined the following two stopping criteria: **effort bounded and partially evidence exhaustion**. For effort bounded, we gather results from the first top 100 Google results and top 50 for LinkedIn, Medium, and Reddit. For each of these search engines, we continued the search until getting a page with less than 50% of hits revealing additional relevant search results."
- **Platform search engines cannot do Boolean:** "the search engines of these platforms cannot handle complex Boolean search queries, limiting their usefulness for systematic searches. To overcome this limitation, Google Search can be used as a proxy, exploiting its feature to restrict its search to specific domains ('sites')."
- **Concrete search-string degradation for Google** (from a 45-term, five-concept Scopus string down to a 23-term, three-concept Google string): "simplifying the list of concepts (AND): we removed the Software Development concept, combining concepts: Agent and GenAI, simplifying some lists of terms (ORs)… and reordering concepts. In our initial searches, the GenAI concept was placed at the end of the search string. This did not affect Scopus' results, but for Google, having this concept at the end yields a lot of results related to agents or AI but not to Generative AI agents."
- **Preprint search infrastructure:** "Scopus' document search has been including preprints since June 2023… Scopus search covers preprints from 2017 onwards from arXiv, ChemRxiv, bioRxiv, medRxiv, SSRN, TechRxiv, Research Square, and eLife." arXiv is recommended for its "advanced search capabilities (field-specific filters, Boolean logic, metadata-based refinements) [which] enable posing complex queries that replicate those used in Scopus."
- **X/Twitter deliberately excluded:** "we are not considering X/Twitter, both given its current dubidous ideological positioning and technological constraints to access its API."

**Survey of stopping criteria across recent MLRs (verbatim):** "tactics differ mainly in two different aspects: (1) **effort bounded**: initial number of pages considered (generally not to high, e.g., 8 pages [4]); (2) **evidence exhaustion**: normally related to a percentage of relevant results (e.g., when the last page has least than 50% relevant results [4], or when less than 25% of results were relevant for three consecutive pages [2]), but eventually until saturation [14]. More pragmatic, Stefanac and Colomo-Palacios limited they search to 20 most relevant Google search results [25]."

**Survey of GL search engines across recent MLRs:** "Google was the main and almost only search engine for GL, although some MLR reports the use of other search engines for particular types of literature, e.g. Twitter, Reddit, Medium, StackOverflow or Hacker News search engines, or some search in some specific web sites, e.g. governance/risk management frameworks. Only one MLR has used additional general-purpose search engines (Bing and Yahoo)."

### Quality/credibility appraisal criteria for grey literature

**Dual-instrument model, verbatim:** "We used source type-dependent dual assessment model. For white literature and preprints, we used Kitchenham and Brereton's quality checklist [11] that includes 12 quality checks based on [5 = Dybå and Dingsøyr]. For the other types of GL, we used the quality check list proposed by Graousi et al. [8] that includes 20 quality checks. The quality assessment scores for both assessment models were normalised to have a value between 0 and 1. For all the GL types, including preprints, sources with normalised quality score less than 0.5 were excluded."

Piloting: "The quality assessment was piloted randomly selecting some papers to be assessed by two of the authors, consolidating the final assessment model after dedicated meetings."

**Operationalisation of Garousi's "authority of the producer" criterion — the paper's most valuable concrete contribution (verbatim, numbers are the score awarded):**

- **Is the publishing organization reputable?**
  - "1: Recognized in the field of Software Engineering, Agile Project Management, and/or AI/LLMs. For example, Software Engineering Institute or Agile Alliance, or well-known companies like Google, Microsoft, Atlassian, IBM."
  - "1: Not well-known company/organisation but with a strong profile on LinkedIn, more than 1000 followers."
- **Is an individual author associated with a reputable organization?** *If the affiliation is stated:*
  - "1: Recognised University, Research Center or company in the field."
  - "1: Reputable using the same criteria defined for the publishing organisations (LinkedIn strong profile)."
- **Has the author published other work in the field?**
  - "1: All the authors have other publications in the field."
  - "0.5: If there are more than one author and at least half of the authors have publications in the field."
- **Does the author have expertise in the area?**
  - "1: For academic authors, when the affiliation is a research group/department related to the field."
  - "1: For practitioners, when the job title or role clearly related to the field (e.g., Principal Software Engineer, Agile Coach, AI Researcher)."

Which Garousi criteria are easy vs. hard: "Some of the aspects are easy to assess, e.g., if the item has a clearly stated date or the outlet type. Researchers can also more easily agree on the qualities related to methodology, objectivity and novelty. But, aspects related to **authority of the producer and impact are not so clear.**"

**Differential action on scores:** "For the white literature, we had already decided **not to exclude** papers with poor WQA scores. For GL, in contrast, we **will exclude** those with poor GQA scores, as Garousi et al. [8] recommend, although we acknowledge that this instrument will rarely filter out preprints."

**Pilot comparison of preprints against the two instruments, verbatim:**
- "WQA: When compared with peer-reviewed papers, preprints achieve comparable overall assessment scores."
- "GQA: Preprints show consistently higher quality scores than other grey sources, particularly in methodological transparency and objectivity. They tend to define their aims and methods clearly, cite related work, engage with the existing literature, and support their analyses with data."

**Survey of appraisal practice across recent MLRs:** "checklists were widely used, either as provided in the MLR guidelines [2], or following other proposals such as Dybå and Dingsøyr's [5] protocol… Criteria themselves were also diverse, some quantitative (e.g., measuring repository popularity in terms of stars), some qualitative, in this case prone to subjectivity risks (e.g., credibility). Only a few studies did not perform GL quality assessment or were not clear at this respect." And on thresholds: "Some required to satisfy at least **10 out of 20 criteria**, while others opted by averaging **3-point Likert scale measure and rejecting if final score was less than 0.5**. Rahman et al. also used Likert measures but didn't exclude GL not reaching the required threshold."

**Exclusion criteria specific to GL, observed across recent MLRs (verbatim):** "Among exclusion criteria particular to GL, we highlight: **lack of traceability of origin**, **credibility**, **excessive brevity**, **a particular type of GL such as videos**, or **commercial contents**. In addition, several studies excluded GL that failed quality assessment."

Their own criteria: common inclusion criterion "sources discussing GenAI agents in Agile project management contexts"; general exclusion "English contribution, removal of duplicates"; source-specific exclusion "(i) white literature and preprints: exclusion of secondary and tertiary studies, unavailability of publication, conference/workshop summaries; (ii) other GL: advertising or promotional material, video or audio files."

### Caveats, traps and pitfalls

**The five challenges of MLR design/execution (Introduction, verbatim):**
> "(1) The additional information sources (known as grey literature) need to be identified, searched, and filtered, looking for a balance among completeness and efficiency of the process; (2) Grey literature is highly heterogeneous, and it is a challenge to extract data from so disparate source types as publication preprints, blogs and youtube videos, to name a few; (3) There are severe reproducibility issues, due to volatility of information, access limitations, etc., that threaten the scientific method; (4) Integrating peer-reviewed scientific publications and grey literature is not easy, due to their differences on rigor and tone; (5) Grey literature is prone to biases, since dominant companies or even individuals may hide other voices, posing on researchers the burden to separate the good from the bad."

Further warnings:
- **Operationalising Garousi's checklist is nontrivial:** "Operationalizing Garousi et al.'s [8] QA checklist proved to be a nontrivial task."
- **Search-engine capability limits cost precision:** "Additional challenges arose from the limitations of Google and the native search engines of Medium, LinkedIn, and Reddit, whose restricted support for complex expressions forced us to simplify and iteratively tune our query strings, **at some cost to precision**."
- **Replicability cannot be fully achieved (verbatim):** "the transient nature of most grey sources, together with search-engine dynamics, compromises full replicability. This is an intrinsic limitation of MLRs that **can only be mitigated through appropriate reporting, although the real problem cannot be avoided.**"
- **Preprint replacement introduces a small fidelity risk:** "We acknowledge that for the replaced preprints appearing as accepted in a peer-reviewed venue without finding the original, the final version could be slightly different from the preprint version. We are assuming that, if the paper has been accepted, the reviewers' comments addressed in the camera ready version should not affect to the core of the proposal."
- **Platform selection bias:** "The inclusion of specific media channels may omit other relevant platforms such as X, Mastodon, or Bluesky. As a mitigation strategy, our methodology (search and selection process) should not change when adding them."
- The overall tension named in the abstract: "the challenge of balancing timeliness with evidence maturity when analyzing a rapidly evolving field characterized by preprints and grey literature"; and "conducting secondary studies in emerging fields requires balancing inclusiveness and rigor."

### Empirical findings worth citing

- **MLR growth:** "Repeating Garousi et al.'s 2021 Scopus lightweight search [9], we found **59 MLRs** in software-related conferences and journals until 2025. This is a significant increase from Neto et al. results and Garousi et al. results, which reported **12** resp. **22** studies."
- **Table 1 — Search and selection results (their own MLR, search performed October 2025):**

| Source | Total | White Lit. | GL (preprints) |
|---|---|---|---|
| Scopus | 20 | 6 | 14 (14) |
| ArXiv | 13 | 0 | 13 (13) |
| Google | 110 | 8 | 102 (2) |
| LinkedIn | 60 | 0 | 60 (0) |
| Reddit | 60 | 0 | 60 (0) |
| Medium | 60 | 0 | 60 (0) |
| **Search results** | **323** | **14** | **309 (29)** |
| Removing dupl. and older | 291 | 11 | 280 (19) |
| After applying IC/EC | 89 | 7 | 82 (6) |
| Preprint replacement | 89 | 9 | 80 (4) |

- **GL prevalence and selectivity:** "Prevalence of GL is clear (96.2%), with very little share from preprints (6.5% of the GL)." "Only 89 sources (31%) passed the inclusion and exclusion criteria, with GL keeping dominance (92.1%, from which 7.3% were preprints)."
- **Scientific sources survive screening at a higher rate:** "the scientific-oriented sources (white literature and preprints) have better inclusion rate than the rest (**50% vs. 30.5%**). For white sources, 7 were selected from 11 (63.6%) and for preprints 6 were selected from 15 (40%)."
- **Preprint search-engine comparison:** "Google Search's simpler query retrieved only two preprints, compared with 14 and 13 from Scopus and arXiv, respectively, using a more precise search string. This combined search yielded 19 unique preprints. Of this set, 9 were common to both Scopus and arXiv, 5 were unique to Scopus, and 4 were unique to arXiv."
- **Preprint→white replacement rate:** "We manually searched the white version of the 6 selected preprints, finding two occurrences that substituted the preprint. In both cases authors mentioned the conference publication in the arXiv notes." ("from the nine white papers selected, two were found as replacements of selected preprints (22.2%)").
- **Saturation was reached quickly:** "in all the GL source types needing only one additional iteration (10 hits) to reach the partial evidence exhaustion condition."
- Preprint prevalence in adjacent surveys: "Buckley et al. [3] report up to 60% of primary studies being preprints in recent literature surveys in the realm of LLMs".

---

## Cross-cutting observations for the methodology document

1. **A single canonical MLR process exists for SE:** Garousi et al. (2019), three phases (planning / conducting / reporting), five conducting sub-steps (search, source selection, quality assessment, data extraction, data synthesis), 14 numbered guidelines. Every other paper in this batch either feeds it (Adams 2017), motivates it (Garousi 2016), extends it to non-review uses of GL (Garousi 2020), audits compliance with it (Neto 2019), or operationalises it (López 2026).
2. **Only two MLR steps genuinely differ from SLR:** search process and source quality assessment. Everything else can be inherited from Kitchenham & Charters.
3. **The tier model has one lineage:** Kepes et al. (2012, four tiers, source availability) → Adams et al. (2017, two axes: outlet control × source expertise, three fuzzy tiers) → Garousi et al. (2019/2020, same model with SE outlets added, tiers made scoreable at 1 / 0.5 / 0). Any methodology document should cite Adams for the model and Garousi for the SE instantiation and scoring.
4. **The decision aid has one lineage too:** Benzies et al. (2006, six-element nursing rubric) + Adams et al. (2017, guidelines 1–2 and 12) → Garousi et al. (2019, Table 4, seven questions, "one or more yes suggests inclusion") → Williams & Rainer (2017, eight conditions, in Garousi 2020) → Neto (2019) empirically adds a ninth motivation not on Garousi's list: **topic novelty / emerging research area**.
5. **Three stopping criteria are the SE standard** (theoretical saturation / effort bounded / evidence exhaustion); López 2026 shows practice combines two of them and gives concrete thresholds (top-100 Google, <50% relevant hits on a page).
6. **The single most-repeated warning across all six papers:** grey and formal evidence must not be silently merged. Adams states it as reporting separately (Guidelines 9–11); Garousi as rigor weighting during synthesis; Kitchenham et al. (2023, via López) as never aggregating blog-derived insights with other evidence; Neto as the validity threat of skipping GL-specific quality analysis and synthesis.
