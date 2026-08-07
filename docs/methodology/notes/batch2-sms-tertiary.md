# Batch 2 — Systematic Mapping Studies & Tertiary Studies

Source texts: `scratchpad/txt/`. Extraction notes for `docs/methodology/`.

Convention: **quoted text** is verbatim from the paper. Counts marked *(derived)* were
computed by counting the study-ID lists in the paper's appendix tables, because the
corresponding figures are images and did not survive text extraction.

---

## Petersen_2015 — "Guidelines for conducting systematic mapping studies in software engineering: An update"
(Kai Petersen, Sairam Vakkalanka, Ludwik Kuzniarz; *Information and Software Technology* 64 (2015) 1–18)

**Type:** guideline (derived from, and reported as, a systematic mapping study of systematic mapping studies)

**Role in corpus:** The authoritative, current SMS process guideline — it supersedes Petersen et al. 2008 by
enumerating *every* activity option observed across 52 published mapping studies plus six competing
guideline sets, and it is the only paper in the corpus that supplies a scoring rubric for evaluating a
mapping study's own methodological rigour.

### Purpose and stated contributions

The paper's three stated contributions:

> - "Assessing the current practice of conducting systematic mapping studies in software engineering."
> - "Comparing the identified guidelines for mapping studies with best practices as identified in Kitchenham and Brereton [8]."
> - "Consolidating the findings to propose updates to systematic mapping guidelines."

Research questions of the underlying map:

- **RQ1**: "Which guidelines are followed to conduct the systematic mapping studies in software engineering?"
- **RQ2**: "Which software engineering topics are covered?"
- **RQ3**: "Where and when were mapping studies published?"
- **RQ4**: "How was the systematic mapping process performed?" — including "Identification of studies (search, inclusion and exclusion)", "Categorization and Classification schemes and processes", "Visualization of results"

### SMS vs. SLR — the framing the guideline rests on

- "Systematic mapping studies or scoping studies are designed to give an overview of a research area through classification and counting contributions in relation to the categories of that classification."
- "While systematic reviews aim at synthesizing evidence, also considering the strength of evidence, systematic maps are primarily concerned with structuring a research area."
- "The research questions in mapping studies are general as they aim to discover research trends (e.g. publication trends over time, topics covered in the literature). On the other hand, systematic reviews aim at aggregating evidence and hence a very specific goal has to be formulated."
- Citing Kitchenham et al.: "the search for studies in systematic maps is based on a topic area, while systematic maps are driven by specific research questions." *(the sentence as printed is internally inconsistent — [EXTRACTION UNCLEAR: the second clause almost certainly should read "systematic reviews are driven by specific research questions"])*
- "Quality assessment is more essential in systematic reviews to determine the rigor and relevance of the primary studies. In systematic maps no quality assessment needs to be performed." — but see the refinement below, where the paper partly walks this back.
- "The outcome of a mapping study is an inventory of papers on the topic area, mapped to a classification. Hence, a mapping study provides an overview of the scope of the area, and allows to discover research gaps and trends."

---

### Process steps or stages defined — THE UPDATED GUIDELINE (Section 5)

> "The mapping process proposed consists of (1) planning, (2) conducting, and (3) reporting the mapping."

#### 5.1 Planning the mapping
"During the planning all the decisions relevant to the conduct of the mapping study are made."

##### 5.1.1 Need identification and scoping

Four typical research goals for mapping studies, quoted from Arksey and O'Malley and glossed by Petersen et al.:

| Goal (verbatim, Arksey & O'Malley) | Petersen et al.'s SE gloss |
|---|---|
| "To examine the extent, range and nature of research activity" | "In software engineering, this may refer to the extent different practices are studied and reported in literature" |
| "To determine the value of undertaking a full systematic review" | "Systematic maps may lead the researcher to find existing systematic reviews… Identifying evaluation and validation research studies provides the set of studies to continue further investigation on in the form of a systematic review… Also, the structuring of the area helps in refining research questions for the conduct of future systematic reviews. They may also be used to determine the potential effort of a full systematic review." |
| "To summarize and disseminate research findings" | "Systematic maps give a comprehensive overview over the area and can also be used as an inventory for papers. Specifically, graduate students may find them useful to orientate themselves in a new area early during the Ph.D. studies." |
| "To identify research gaps in the existing literature" | "Based on the categorization areas, with very few studies or lack of evaluations, the need for future research becomes apparent. In case there are only very few studies in a category, those can be investigated in more depth…" |

On question granularity: "the questions in systematic mapping studies are less specific than in systematic
reviews. Mapping questions are about what we are knowing with respect to a specified topic."

Worked examples of mapping research questions the guideline endorses:
- High-level: "What Do We Know about Software Product Management?" — "Often those high level questions have to be further broken down to drive the data extraction", e.g.
  - "What research questions in software product management are being addressed?"
  - "What original research exists in the intersection of software product management and cloud (service) environment?"
  - "What areas in software product management require more research?"
- Elberzhager et al.-style questions covering approach, venue/year and evidence:
  - "What are existing approaches that combine static and dynamic quality assurance techniques and how can they be classified?"
  - "In which sources and in which years were approaches regarding the combination of static and dynamic quality assurance techniques published?"
  - "Is any kind of evidence presented with respect to the combination of quality assurance techniques and if so, which kind of evidence is given?"

##### 5.1.2 Study identification — four sub-activities

The guideline decomposes study identification into: **choosing the search strategy**, **developing the search**,
**evaluating the search**, and **inclusion and exclusion**.

**Framing statement on the aim of study identification (important — this is a change of position):**
> "In systematic reviews the goal is an exhaustive search where we identify all the relevant evidence.
> Based on previous evaluations for mapping studies there is an indication that this may not be a realistic
> goal. Wohlin et al. state that having more papers is not necessarily better than having fewer, it depends
> on whether the papers are a good representation of the population."

Three questions the guideline offers for reflecting on the population:
> - "Are different a priori known sub-areas of the field covered? Here, existing classifications of the field (e.g. software testing) may help, as well as experts who may point to classifications or could draw up a map of areas they believe are of relevance. This part is about understanding as much as possible about the population of relevant articles."
> - "Are the main publication forums specific to this area (e.g. conferences), or general software engineering forums (e.g. journals), represented when identifying relevant articles?"
> - "Are there explanations for major changes in the number of studies published per year? For example, this may point to new areas that should be added to classifications established earlier."

The Badampudi et al. partitioning technique is presented as the worked example: partition the area of interest by
what you already know (there, by architectural asset type), plot which partitions the snowballing found, then have
"an independent researcher not involved in the snowballing activity" run a database search to fill empty
partitions. Analogy given: "this is similar to the problem of testing, where we do not know the population of
defects in the software when we are searching for them."

**(a) Choosing the search strategy** — three options: **database search**, **manual search**, **snowballing**.
- "From this mapping study we found that database search is the most frequent approach. 23 studies did not take any additional help into account while developing the search, while several studies made use of several search strategies."
- "conducting multiple search strategies may be quite time intensive. Thus, not all of them could be practically applied together in the systematic mapping study, as the trade-off between timely availability of the information and achieving a good overview of the research area needs to be considered. In particular, of the main importance is that the overall conclusions about trends and research gaps do not change. Therefore, we recommend to select one or a sub-set of the activities."
- "Evidence has shown that manual searches are beneficial, and even be more effective in identifying relevant studies."
- "given that too little evidence exist and the findings may depend on the topic studied, we do not know whether one particular approach should be preferred over another."

Wohlin's advice on the snowballing **start set**, reproduced by the guideline:
> - "Choose articles from different clusters (e.g. communities) that are not likely to cite each other, and hence cannot be found through citation relationships. They should of course be relevant for the research question."
> - "The number of articles in the start set should not be too small, the size depending on the focus and size of the area, which may not be known beforehand."
> - "Different authors, years of publication, and also publishers should be covered. For example, when choosing the same authors, these are likely to know about their own work, and hence may limit the breadth of the search."
> - "Keywords from the research question should be the base for formulating the start set, and are essential when searching for the initial set of papers to start the snowballing from."

**(b) Developing the search** — five options: **PICO(C)**, **consult librarians/experts**, **iteratively improve the
search**, **keywords from known papers**, **use standards, encyclopedias and thesauri**.
- On PICO: "PICO(C) has only been used by 11 studies, though we believe it to be useful. As one has to determine what a good population is, it is important to reflect on the population… **The other dimensions (comparison, outcome, and context) may restrict the search too much and remove articles from the topic area. Hence, based on this reflection P and I may be most relevant for mapping studies and should be used.**"
- "For software engineering, standards from the IEEE as well as ISO/IEC standards are of relevance to identify keywords. Swebok provides an overall structure of the field of software engineering that is widely known."
- "The approaches identified… are not highly time intensive and may greatly improve the quality of the search. Overall, such early quality assurance may save effort due to rework when mistakes were made in the early search activity. They may also help in focusing the search and hence reduce the noise, making the study selection process more time efficient."
- Database selection: "As recommended by Dyba et al. and Kitchenham and Brereton the use if IEEE and ACM as well as two indexing databases (e.g. Inspec/Compendex and Scopus) is sufficient."
- Precision/noise: "If a search returns a very large number of irrelevant hits, it may be useful to reflect on whether to further restrict the search (e.g. by making the population more precise)."

**(c) Evaluating the search** — four options: **test-set of known papers**, **expert evaluates result**, **search
web-pages of key authors**, **test–retest**.
- "This can, for example, be done by asking an expert in the area who should provide a set of ten papers that should be found. If no expert is available, key researchers in the field may have the relevant articles to be found on their web-pages. After the search, it may also be useful to have an expert evaluate the search result."
- Stopping rules, from Petticrew and Roberts: "define a stoppage criterion for the search. For example, if we are using database search and a complementary search approach (such as manual search, snowball sampling) does not add a specific number of new articles to the database search then no further searching is done. Another proposal is to set a time budget based on available funds and only include articles that have been identified, and list all other articles that were not considered."

**(d) Inclusion and exclusion.** Criteria "may refer to (a) the relevance of the topic of the article, (b) the venue of
publication, (c) the time period considered, (d) requirements on evaluation, and (e) restrictions with respect to
language. **Though, in the case of systematic maps (d) should be avoided to also see recent trends that have not
reached the maturity for evaluation yet.**"

Worked inclusion criteria (Laguna & Crespo):
> - "English peer-reviewed articles in conferences or journals published until Dec. 2011"
> - "Articles that focus on software product lines"
> - "Articles that provide some type of evolution of existing software artifacts, included among the terms selected"
> - "Context, objectives, and research method are reasonably present"

Worked exclusion criteria (same source):
> - "Articles that are not related to software product lines"
> - "Articles that do not imply evolution of any software artifacts"
> - "Non-peer reviewed publications"
> - "Articles that are not written in English"
> - "Context, objectives, or research method are manifestly missing"

**The study selection process (Fig. 17, from Ali & Petersen), in order:**
1. **Specify selection criteria in the review protocol**
2. **Review of selection criteria** (among the researchers) → may *update* criteria
3. **"Think-aloud" application of criteria** — "one reviewer describes the thought process of inclusion/exclusion by applying them to one study, which aligns understanding" → may *update* criteria
4. **Pilot selection on a subset** → may *update* criteria
5. **Analyse disagreements & calculate inter-rater agreement**
6. Gate: **Acceptable level of agreement?** — No → loop back to update criteria; Yes → proceed
7. **Perform selection** (each researcher rates each study "include", "exclude", or "uncertain") and **apply decision rules**
8. **Calculate inter-rater agreement**

**Decision-rule combination table (Table 6) — two reviewers R1, R2:**

|            | R2 = Include | R2 = Uncertain | R2 = Exclude |
|------------|--------------|----------------|--------------|
| **R1 = Include**   | A | B | D |
| **R1 = Uncertain** | B | C | E |
| **R1 = Exclude**   | D | E | F |

> "The most inclusive strategy is to take all articles (A–E) to the next step and only exclude F right away.
> As has been shown in the study following the most inclusive strategy (A + B + C + D + E) would find all relevant
> studies, but also has 25% more overhead to strategy (A + B + C + D), where 94% of all studies were identified.
> Overhead is defined as the 'percentage of irrelevant articles that had to be analyzed'."

**Quality assessment inside a mapping study.** "In some cases quality assessment may be useful for a systematic map
as well (e.g. to assure that sufficient information is available to actually extract the information)… In general, we
concur with Kitchenham et al. that quality assessment should not pose high requirements on the primary studies as the
goal of mapping is to give a broad overview of the topic area."

##### 5.1.3 Data extraction and classification

**Extraction process** — two alternatives:
1. "more than one researcher is involved and the additional researcher may either check the outcome or conduct all data extractions independently from the first reviewer; if needed a consensus meeting is held."
2. "the objectivity of the criteria is assessed based on a pilot set of articles and/or post-extraction."

"the most common strategy is the first one. Whether an agreement measure can be applied depends on the data extracted.
In particular, mapping studies may support calculating agreement as papers are commonly classified into different
categories. Though, given the trade-off between availability of the results and the reliability of the classification,
Kitchenham and Brereton found it useful to have another person check the data extraction."

**Topic-independent classification.** "The goal is that the topic-independent classifications are used by the majority
of mapping studies conducted, hence they should be generally applicable. Only by using the same or similar
classification schemes consistently enables comparisons."

Five topic-independent facets identified: **venue**, **research type**, **research method**, **study focus**, **contribution type**.
- "Contribution type is only used by very few studies, and appears to not be of high relevance for the general population of mapping studies. **Hence, we encourage the use of venue, research type, and research method.**"
- **Venue classification**: the guideline adopts the Finnish ministry of education classification, "as it is a derivation of actual publication activity" (Fig. 18): Peer-reviewed (Journal article (refereed), original; Review article/literature review/systematic review; Book section, chapters in research books; Conference proceedings; Non-refereed: non-refereed journal articles, book sections, non-refereed conference proceedings; Book: edited book, conference proceedings, or special issue) | Professional communities (Trade journal; Articles in professional manuals; Professional proceedings; Published development or research report; General public: popularised article/newspaper, popularised monograph; Thesis: B.Sc., M.Sc., Lic./MPhil, Doctoral dissertation) | Public artistic and design activity (Published independent work of art; Public partial realisation of art; Audiovisual material, software; ICT software; Patents: granted patent, invention disclosure). "The venue classification may also be of use when deciding which publication forums to include and exclude during study selection."
- **Study focus**: "refers to the context being studied. Examples are distinctions between academic, industrial, government, project, and organization context."
- **Contribution type**: "refers to determining the type of intervention being studied, this could be a process, method, model, tool, or metric."

**Research type decision table (Table 7) — Petersen et al.'s own disambiguation of Wieringa's scheme.**
T = True, F = False, blank = irrelevant or not applicable. R1–R6 are rules.

| Condition | R1 | R2 | R3 | R4 | R5 | R6 |
|---|---|---|---|---|---|---|
| Used in practice | T | | T | F | F | F |
| Novel solution | | T | F | | F | F |
| Empirical evaluation | T | F | F | T | F | F |
| Conceptual framework | | | | | T | F |
| Opinion about something | F | F | F | F | F | T |
| Authors' experience | | | T | | F | F |
| **Decision** | **Evaluation research** | **Solution proposal** | **Experience papers** | **Validation research** | **Philosophical papers** | **Opinion papers** |

*(Note: the decision block in the text extraction lists the outcome labels in the order Evaluation research,
Solution proposal, Validation research, Philosophical papers, Opinion papers, Experience papers with the check
marks offset; the mapping above follows the paper's own prose, which states R1 and R4 are evaluation and validation
research respectively and that R3 is characterised by "authors' experience" + "used in practice" without empirical
evaluation. [EXTRACTION UNCLEAR: exact column-to-label alignment for R3/R5/R6 in the printed table.])*

The accompanying prose, which is the substantive refinement:
> "The main confusion with respect to the classification originated from the distinction between validation and
> evaluation research (R1 and R4 in Table 7). **Whether the solution validated or evaluated is novel is not a key
> criterion. Both have to be empirically evaluated, however, validation is not used in practice (i.e. it is done in
> the lab), while evaluation studies take place in a real-world industrial context. Furthermore, a new solution may
> be reported to be used in practice, though it is still a solution proposal if the empirical evaluation is missing.**"

**Research method classification (Fig. 19).** Set of methods: "Survey, case study, controlled experiment, action
research, ethnography, simulation, prototyping, and mathematical analysis." "The method selection has to be consistent
with the classification of research type… Please note that research methods may belong to both categories. For example,
experiments with students are classified as validation research, while experiments with practitioners would be
classified as evaluation research."

| Research type | Methods mapped to it |
|---|---|
| **Evaluation research** | Industrial case study; Controlled experiment with practitioners; Practitioner targeted survey; Action research; Ethnography |
| **Validation research** | Simulation as an empirical method; Laboratory experiments (machine or human); Prototyping; Mathematical analysis and proof of properties; Academic case study (e.g. with students) |

**Topic-specific classification** — two alternatives: an **emerging scheme** (keywording) or **use of an existing
scheme/standard**.
- "Based on availability, it is useful to take an existing classification as the baseline as this supports the comparability between mapping studies. As for the identification of keywords standards (IEEE and ISO/IEC) as well as Swebok are of use. Before starting the classification we propose to consult experts in the area to identify existing classification schemes."
- **Keywording, clarified** (this is an explicit repair of the 2008 guideline): "Petersen et al. proposed to use keywording as a means to create a classification scheme and later count the number of articles per category. The process first identifies keywords and concepts from the papers' abstracts. These are then grouped and refined to create a classification scheme. **As pointed out by Portillo-Rodríguez et al. the keywording process is not clear. It was intended to be similar to open coding from grounded theory.** During open [coding] we assign labels or keywords to concepts we find in the text. A number of open codes would be obtained, which thereafter have to be put into an overall structure. In the process the codes representing the categories may be merged or renamed. After having identified the categories the papers are sorted into them, and the number of studies per category are represented. **Depending on the quality of abstracts, the process may only be applied on the abstracts. If the abstracts are not clear, further parts of the paper may be considered (e.g. introduction and conclusion).**"

##### 5.1.4 Visualization
Six types identified: **line diagram, pie diagram, bar plot, bubble plot, Venn diagram, heatmap**.
> "The most commonly used means for visualization are bubble plots, bar plots, and pie diagrams. All visualizations
> are useful in the context of mapping studies. **To illustrate the number of studies for a combination of
> categorizations (e.g. topic category with research type) bubble plots and heat-maps are particularly suited.**"

##### 5.1.5 Validity threats
"For any empirical study the discussion of validity threats is of importance and is a quality criterion for study
selection. Hence, possible validity threats shall also be discussed in the context of mapping studies." (See the
validity framework section below.)

#### 5.2 Conducting the mapping
> "When conducting the mapping the process as defined during the planning phase has to be implemented. Kitchenham and
> Charters and Petticrew and Roberts recommend to record the information at all stages of the process. **It is also
> noteworthy to highlight that the process is iterative and may require revisions.** Furthermore, tools to record data
> are useful, such as spreadsheets and software for reference management."

#### 5.3 Reporting the mapping — the recommended report structure

> "As far as possible, we should aim to have the same reporting structure and style in each systematic map. This makes
> them easier to evaluate and to compare. Based on the information gathered in this study, we propose the following structure."

| Section | Content (verbatim) |
|---|---|
| Introduction | "Provide information on the background of the topic studied. Describe the need for the mapping, and highlight the usefulness." |
| Related work | "Provide an overview of existing secondary and tertiary studies in the area." |
| Research method | "In the research method present the following in separate subsections: research question, search, study selection, data extraction (and if conducted quality assessment), analysis and classification, validity evaluation (discuss the different types)." |
| Results | "Present the outcomes of the study and structure the section with respect to the mapping questions." |
| Discussion/Conclusions | — |
| Appendix | "Appendix with included as well as excluded borderline papers." |

#### 5.4 Evaluate the mapping process
"Having conducted and reported the process, an important step of evidence-based software engineering is to evaluate
the evidence-based process." Motivation: "Kitchenham and Brereton found that a common request to include in guidelines
is a pocket guide for evaluation as support for researchers during the design, and reviewers during the assessment of
mapping studies."

#### 5.5 Dissemination
"The classification of publication venues available for publication are provided in Fig. 18… It can be observed that
the median value for journals is higher than for conference publications, which may be due to the space for reporting,
which could be a motivation to favor journals over conferences when reporting extensive literature studies."

---

### Clarifications and refinements to earlier guidance

| Topic | Old position | New position in Petersen 2015 |
|---|---|---|
| Sufficiency of a single guideline | Kitchenham & Charters 2007 and Petersen et al. 2008 each presented as a complete process | "The most frequently followed guidelines are not sufficient alone." "Overall, 24 mapping studies used more than one guideline. Thus, individual guidelines do not appear to be complete enough to characterize the whole mapping process." The reason authors combined them "was that they differed in the recommendations given." |
| Goal of the search | Exhaustive search / "all studies must be found" (K&C position for SLRs, carried into maps) | "Based on previous evaluations for mapping studies there is an indication that this may not be a realistic goal." Aim for **a good sample representative of the population**; "having more papers is not necessarily better than having fewer." An explicit **stoppage criterion** or **time budget** is legitimate. |
| PICO | K&C 2007 recommend full PICO(C) for search-string construction | Only **P** and **I** are recommended for mapping studies: "The other dimensions (comparison, outcome, and context) may restrict the search too much and remove articles from the topic area." |
| Keywording | Petersen et al. 2008 described keywording of abstracts without defining the mechanism | Explicitly identified as unclear in 2008 and re-specified as **open coding from grounded theory** (assign labels → group into structure → merge/rename codes → sort papers → count). Also: fall back to introduction/conclusion when abstracts are poor. |
| Which classification facets to use | Petersen et al. 2008 emphasised **contribution type** and **research type** | Empirically, contribution type is used by only 6 of 52 studies *(derived)*. New recommendation: **venue, research type, and research method**; three facets not in the 2008 guideline are identified — **venue, study focus, research method**. |
| Research type (Wieringa) classification | Wieringa's categories used as-is; recommended by Petersen 2008 | Because two independent studies using it agreed on only 33% of classifications, the paper adds a **decision table (Table 7)** and rules out "novelty" as a discriminator: validation = lab, evaluation = real-world industrial context; a solution reported as used in practice but without empirical evaluation is still a **solution proposal**. |
| Quality assessment in maps | Kitchenham et al.: "In systematic maps no quality assessment needs to be performed." | Softened: "In some cases quality assessment may be useful for a systematic map as well (e.g. to assure that sufficient information is available to actually extract the information)" — but "quality assessment should not pose high requirements on the primary studies." |
| Inclusion criteria | General SLR criteria include requirements on evaluation | For maps, **requirements on evaluation should be avoided** "to also see recent trends that have not reached the maturity for evaluation yet." |
| Evaluation of the review itself | Not covered by 2008 guideline | New: a **checklist of 26 actions + five scoring rubrics** and a **ratio metric** (actions taken ÷ 26). |
| Reporting | Not prescribed for maps | New: a fixed report structure including a related-work section covering existing secondary/tertiary studies and an appendix of included **and excluded borderline** papers. |

---

### Caveats, traps and pitfalls

- **Two independent maps of the same topic disagree.** "even though the studies had a similar aim, the articles included turned out to be different. Second, the classification of articles included in both studies was different… **On the same set of articles included in both studies the research only agreed in 33% of the cases.**" Sources of difference discussed: "research question phrasing (open versus specific), scoping (where to draw the boundaries for the research area), restrictions on research types and methods (e.g. only including empirical work), time span, and exclusion of specific publication types (e.g. gray literature)."
- **Classes are not disjoint**: "classes may not be clearly disjoint and hence classification in more than one category may be possible."
- **Even a good map misses papers within its own clusters**: Kitchenham et al.'s validation-set study found that "Even though important groups of articles were identified sufficiently well, within each group represented by the different systematic reviews articles were missed."
- **The population is unknowable in advance**: "As the population is not known before, and one cannot randomly sample from the population, the ability to reflect on the sample may be very limited."
- **Reliable classification is the specific weak point of maps**: "The scheme proposed by Wieringa et al. and used by two independent studies on the same topic led to inconsistent classifications, which indicates that this is a major concern specific to systematic mapping studies."
- **Data extraction is as bias-prone as selection, but is checked less often**: "the total number of studies evaluating the quality of data extraction is lower than the number for inclusion and exclusion. Even though, one may argue that the process for data extraction is equally prone to biases as the inclusion and exclusion of articles."
- **Noise costs more than it looks**: on their own search — "retrospectively we may have had an equally good result just searching for ('Systematic mapping' and 'Systematic map') AND ('software engineering' OR 'software development'), but would have saved significant effort in the study selection phase."
- **Snowballing is only as good as the start set** (see Wohlin's four rules above).
- **Diminishing returns on rigour**: "even though more actions taken increases the reliability of the mapping studies, there maybe a point where the return on investment is very low. Hence, to determine which are the right scores to achieve in the rubric further empirical studies are needed."
- **Single-reviewer stages are the dominant validity threat.** Their own study: "each article was only reviewed by a single author, which poses a threat to the reliability of the mapping study." Mitigations they applied: two validation sets built by a different author, and a full re-review of everything excluded during quality assessment and full-text reading (which recovered 8 wrongly excluded studies).
- **Maps may be mislabelled as reviews**: "There is also the possibility that systematic mapping studies are referred to as systematic reviews. During the inclusion and exclusion phase there is a threat that these studies are dismissed."
- **Guidelines are analysed only as reported**: "There is a potential threat that activities may be overlooked, misunderstood, or incompletely reported as we based our analysis solely on the reporting."
- **Rubric scoring is scoring of the report, not the work**: "it has to be pointed out that the rating is conducted based on the reported information."

---

### Checklists, rubrics, scoring schemes, evaluation criteria

#### Their own quality-assessment questions for including a mapping study (Section 3.3)
> - "Is the motivation for conducting systematic mapping clearly stated?"
> - "Is the process of conducting systematic mapping clearly defined (study identification, data extraction, classification)?"
> - "Is there any empirical evidence for the defined mapping process? This question is concerned with whether the results of the mapping study are presented. That is, studies focusing on evaluating mapping studies without presenting their results are excluded."

#### Their data extraction form (Table 3)

| Data item | Value | RQ |
|---|---|---|
| Study ID | Integer | |
| Article Title | Name of the article | |
| Author Name | Set of Names of the authors | |
| Year of Publication | Calendar year | RQ3 |
| Area in SE | Knowledge areas in SWEBOK | RQ2 |
| Venue | Name of publication venue | RQ3 |
| Guidelines | Which guidelines were adopted | RQ1 |
| Search strategy | What search strategy is followed, and how were studies selected | RQ4 |
| Search type | Manual or automated or both | RQ4 |
| Classification schemes | How were articles classified | RQ4 |
| Visualization type | What visualization types were used in order to present the data in a pictorial manner | RQ4 |

#### THE 26-ACTION CHECKLIST (Table 8) — "A total of 26 actions have been identified that could be applied by a systematic mapping study."
The right-hand column records whether Petersen et al. applied the action **in this very study**; their self-assessed
ratio is **31%** (8/26).

| Phase | Action | Applied in Petersen 2015? |
|---|---|---|
| Need for map | Motivate the need and relevance | ✔ |
| Need for map | Define objectives and questions | ✔ |
| Need for map | Consult with target audience to define questions | ✘ |
| Study ident. — choosing search strategy | Snowballing | ✔ |
| Study ident. — choosing search strategy | Manual | ✘ |
| Study ident. — choosing search strategy | Conduct database search | ✔ |
| Study ident. — develop the search | PICO | ✔ |
| Study ident. — develop the search | Consult librarians or experts | ✘ |
| Study ident. — develop the search | Iteratively try finding more relevant papers | ✘ |
| Study ident. — develop the search | Keywords from known papers | ✘ |
| Study ident. — develop the search | Use standards, encyclopedias, and thesaurus | ✘ |
| Study ident. — evaluate the search | Test-set of known papers | ✔ |
| Study ident. — evaluate the search | Expert evaluates result | ✘ |
| Study ident. — evaluate the search | Search web-pages of key authors | ✘ |
| Study ident. — evaluate the search | Test–retest | ✘ |
| Study ident. — inclusion and exclusion | Identify objective criteria for decision | ✘ |
| Study ident. — inclusion and exclusion | Add additional reviewer, resolve disagreements between them when needed | ✘ |
| Study ident. — inclusion and exclusion | Decision rules | ✘ |
| Data extr. and class. — extraction process | Identify objective criteria for decision | ✘ |
| Data extr. and class. — extraction process | Obscuring information that could bias | ✘ |
| Data extr. and class. — extraction process | Add additional reviewer, resolve disagreements between them when needed | ✔ |
| Data extr. and class. — extraction process | Test–retest | ✘ |
| Data extr. and class. — classification scheme | Research type | ✘ |
| Data extr. and class. — classification scheme | Research method | ✘ |
| Data extr. and class. — classification scheme | Venue type | ✘ |
| Validity discussion | Validity discussion/limitations provided | ✔ |

#### THE FIVE SCORING RUBRICS (Tables 9–13) — all rows, all anchors, verbatim

**Table 9 — Rubric: need for review**

| Evaluation | Description | Score |
|---|---|---|
| No description | "The study is not motivated and the goal is not stated" | 0 |
| Partial evaluation | "Motivations and questions are provided" | 1 |
| Full evaluation | "Motivations and questions are provided, and have been defined in correspondence with target audience" | 2 |

**Table 10 — Rubric: choosing the search strategy**

| Evaluation | Description | Score |
|---|---|---|
| No description | "Only one type of search has been conducted" | 0 |
| Minimal evaluation | "Two search strategies have been used" | 1 |
| Full evaluation | "All three search strategies have been used" | 2 |

**Table 11 — Rubric: evaluation of the search**

| Evaluation | Description | Score |
|---|---|---|
| No description | "No actions have been reported to improve the reliability of the search and inclusion/exclusion" | 0 |
| Minimal evaluation | "At least one action has been taken to improve the reliability of the search xor the reliability of the inclusion/exclusion" | 1 |
| Partial evaluation | "At least one action has been taken to improve the reliability of the search and the inclusion/exclusion" | 2 |
| Full evaluation | "All actions identified have been taken" | 3 |

**Table 12 — Rubric: extraction and classification**

| Evaluation | Description | Score |
|---|---|---|
| No description | "No actions have been reported to improve on the extraction process or enable comparability between studies through the use of existing classifications" | 0 |
| Minimal evaluation | "At least one action has been taken to increase the reliability of the extraction process" | 1 |
| Partial evaluation | "At least one action has been taken to increase the reliability of the extraction process, and research type and method have been classified" | 2 |
| Full evaluation | "All actions identified have been taken" | 3 |

**Table 13 — Rubric: study validity**

| Evaluation | Description | Score |
|---|---|---|
| No description | "No threats or limitations are described" | 0 |
| Full evaluation | "Threats and limitations are described" | 1 |

**Aggregate metric:** "We also suggest to calculate the ratio of the number of actions taken in comparison to the total
number of actions. For this mapping study the ratio is 31%."

#### Table 14 — Rubric evaluation of the 52 existing mapping studies (– = not applicable)

| Activity | No Desc. | Min. E. | Part. E. | Full E. |
|---|---|---|---|---|
| Need for review | 0 | – | 52 | 0 |
| Search strategy | 30 | 12 | – | 10 |
| Evaluate search | 23 | 22 | 7 | 0 |
| Extract./Class. | 5 | 32 | 15 | 0 |
| Validity | 7 | – | – | 45 |

> "As can be seen, the majority of studies falls into the 'No description' or 'Minimal evaluation' categories for the
> choice of search strategy and search evaluation. Furthermore, the result for validity and stating the need for the
> review is very good."
> "It is visible that the median quality of studies is 33[%], with 25% of all studies having a quality score of above 40%."

#### Table 5 — Guideline comparison (which activities each guideline covers)
Columns: Kitchenham 2004 / Kitchenham & Charters 2007 · Petersen et al. 2008 · Budgen et al. · Arksey & O'Malley ·
Durham template · Biolchini et al. · Petticrew & Roberts · **This study** · Kitchenham & Brereton.

[EXTRACTION UNCLEAR: the per-cell tick marks in Table 5 did not survive the PDF-to-text conversion in a
column-aligned way and must not be reproduced cell-by-cell.] What *is* reliable is the row taxonomy, which is the
paper's full activity inventory and matches the guideline text:

- **Need for the map**: Motivate the need and relevance · Define objectives and questions · Consult with target audience to define questions
- **Study ident. — Choosing search strategy**: Database search · Snowballing · Manual search
- **Study ident. — Develop search**: PICO(C) · Consult experts · Iteratively improve search · Keywords from known papers · Use standards, encyclopedias
- **Study ident. — Search evaluation**: Paper test-set · Expert evaluation · Authors' web pages · Test–retest
- **Study ident. — Inclusion/exclusion**: Identify objective criteria for decision · Resolve disagreements among multiple researchers · Decision rules
- **Extr./Class. — Extraction process**: Identify objective criteria for decision · Obscuring information that could bias · Resolve disagreements among multiple researchers
- **Extr./Class. — Topic-independent**: Research type · Research method · Study focus · Contribution type · Venue type
- **Extr./Class. — Topic specific**: Emerging scheme · Use of standards, etc.
- **Study validity**: Discussion of threats
- **Visualization**: Line diagram · Pie diagram · Bar plot · Bubble plot · Venn diagram · Heatmap

The paper's own conclusion about this table: "the guidelines differ with respect to which activities are proposed.
The mapping shows that existing guidelines do not represent the activities conducted in the mapping studies."

---

### Threats to validity framework

Petersen 2015 adopts **Petersen and Gencel's** four-category scheme (plus repeatability), and this is the scheme it
recommends for mapping studies ("validity evaluation (discuss the different types)"):

| Category | Definition (verbatim) | Their own mitigations |
|---|---|---|
| **Descriptive validity** | "the extent to which observations are described accurately and objectively. Threats to descriptive validity are generally greater in qualitative studies than they are in quantitative studies." | "a data collection form has been designed to support the recording of data. The form objectified the data extraction process and could always be revisited" |
| **Theoretical validity** | "determined by our ability of being able to capture what we intend to capture. Furthermore, confounding factors such as biases and selection of subjects play an important role." | Covers study identification/sampling and researcher bias in selection and extraction; mitigated by backward snowballing, a reference set built by a second researcher via forward snowballing, and cross-checking of extractions |
| **Generalizability** | "a distinction between external generalizability (generalizability between groups or organizations) and internal generalizability (generalization within a group)" | Wide range of topics ⇒ internal generalizability not a major threat; results "may not apply to systematic literature reviews as they are different in their goals" |
| **Interpretive validity** | "achieved when the conclusions drawn are reasonable given the data, and hence maps to conclusion validity. A threat in interpreting the data is researcher bias." | Declared conflict: "The first author is a co-author on one of the guidelines, which may be a bias in interpretation." |
| **Repeatability** | "requires detailed reporting of the research process." | Reported process + reliance on existing guidelines |

**The generic threat list the guideline tells mapping-study authors to consider (Section 5.1.5), with the category
each maps to:**
> - "Publication bias, as negative or new and controversial views may not be published (theoretical validity)."
> - "Poorly designed data extraction forms and recording of data (descriptive validity)."
> - "Potential researcher bias in the selection of studies and reporting of the data (theoretical validity)."
> - "The quality of the sample of studies obtained with respect to the targeted population (theoretical validity)."
> - "Generalizability of the results of the mapping. This includes within the population (internal generalizability) and between different populations (external generalizability)."
> - "The reliability of the conclusions drawn in relation to the data collected, e.g. due to a possible bias of the researchers in the interpretation of that data."

---

### Data extraction, classification and analysis techniques (as practised in this study)

- **Search string construction**: keywords grouped into three sets — Set 1 scoping ("software engineering"); Set 2 intervention terms ("systematic mapping", "systematic maps"); Set 3 "search terms related to the process of classification and categorization, e.g. methods, tools, classification, framework". Databases: IEEE Xplore, ACM, Scopus, Inspec/Compendex; searched on all fields; "The databases have been selected based on the experience reported by Dyba et al."
- **Reference management**: "EndNote X6, a reference management tool, was used to remove duplicates and to manage the large number of references."
- **Search validation by two independent validation sets**: (1) eight papers the first author already knew ought to be included; (2) papers derived from the 321 citations to Petersen et al. 2008 (forward snowballing). Four additional missed papers were found this way.
- **Analysis/classification method**: "The information for each item extracted was tabulated and visually illustrated. The extracted strategies were grouped and given a theme by the first author during analysis. Thereafter, the papers belonging to each theme were counted." Sub-themes for inclusion/exclusion were "known a priori" from Petersen & Ali.
- **Topic classification**: SWEBOK, with two categories added because SWEBOK did not cover them — **Education** and **research methodologies**.
- **Selection funnel (Fig. 1):** 7752 results from databases → remove articles before 2004 (−2666) → 5082 → apply inclusion/exclusion (−5022) → 60 → full-text reading (−17) → 43 → snowball sampling (+11) → 54 → quality assessment (−10) → 44 → review of excluded articles (+8) → **52**.

---

### Empirical findings worth citing (52 mapping studies, 2007–2012)

Hits per database: IEEE 5610; ACM 360; Scopus 1215; Inspec/Compendex 567.

**Guidelines used (Table B.17)** *(derived counts)* — "Ten different guidelines have been followed."

| Guideline | Studies |
|---|---|
| Kitchenham 2004 + Kitchenham & Charters 2007 | 30 |
| Petersen et al. 2008 | 31 |
| Petticrew and Roberts 2006 | 5 |
| Budgen et al. 2008 | 3 |
| Arksey and O'Malley 2005 | 3 |
| Dybå and Dingsøyr 2008 | 1 |
| Bailey et al. 2007 | 1 |
| Jørgensen and Shepperd 2007 | 1 |
| Durham template | 1 |
| Biolchini et al. 2005 | 1 |

- **24 of 52 mapping studies used more than one guideline.**

**Search strategy (Table B.18)** *(derived)*: database search 50; manual 20; snowballing 14.
**Developing the search (Table B.19)** *(derived)*: PICO 11 (paper states 11); keywords from known papers 11; standards/encyclopedias/thesaurus 7; iteratively improve 7; consult librarians/experts 6. "23 studies did not take any additional help into account while developing the search."
**Evaluating the search (Table B.20)** *(derived)*: test-set of known papers 8; expert evaluates result 1; author web pages 1; test–retest 1.
**Inclusion/exclusion (Table B.21)** *(derived)*: add additional reviewer / resolve disagreements 22; identify objective criteria 8; decision rules 4.
**Quality assessment (Table B.22)**: **Yes 14, No 38** — "only 14 out of 52 studies assess the quality of primary studies, hence it is not very common to do so."
**Data extraction process (Table B.23)** *(derived)*: add additional reviewer 17; identify objective criteria 4; test–retest 1.
**Topic-independent classification (Table B.24)** *(derived)*: venue 27; research type 21; research method 17; study focus 11; contribution type 6.
**Topic-related classification (Table B.25)** *(derived)*: emerging classification 41; existing scheme 16.
**Visualizations (Table B.26)** *(derived)*: bubble plot 24; bar plot 22; pie diagram 12; Venn diagram 3; line diagram 2; heatmap 1.
**Validity threats discussed (Table B.27)**: **Yes 45, No 7.**
**Venues (Table B.16)** *(derived)*: conference 26; journal 23; workshop 3. Top venues: Information & Software Technology (14 articles / 12 listed IDs), EASE, ESEM.
**Topics (Table B.15)** *(derived)*: testing 11; design 10; management 8; tools and methods 6; requirements 6; research methods 6; quality 5; process 4; construction 2; configuration management 1; education 1.
**Timeline**: first mapping study 2007 (Bailey et al.); moderate growth 2008–2010; "a significant increase can be observed in 2011 and 2012."

---
---

## Kitchenham_2010 — "Systematic literature reviews in software engineering – A tertiary study"
(B. Kitchenham, R. Pretorius, D. Budgen, O. P. Brereton, M. Turner, M. Niazi, S. Linkman; *IST* 52 (2010) 792–805)

**Type:** tertiary study (an SLR/mapping study of secondary studies)

**Role in corpus:** The canonical worked example of **how a tertiary study is actually conducted end-to-end** —
including the only fully specified multi-rater "consensus and minority report" extraction protocol in the corpus, and
the DARE-4 quality instrument with its complete scoring anchors.

### Process steps or stages defined

"We applied the basic SLR method as described by Kitchenham and Charters." The paper is explicitly a **replication and
extension** of an earlier tertiary study (T1), and the design is a three-set comparison:

- **T1** — SLRs reported in the original study, Jan 2004 – 30 June 2007 (manual search of 13 sources)
- **T2-1** — SLRs in the same period found by the *broad automated* search but missed by T1
- **T2-2** — SLRs published 1 July 2007 – 30 June 2008

Two declared method differences from the original study:
> - "We used a broad automated search rather than a restricted manual search process."
> - "Three researchers collected quality and classification data. For the papers found in the same time period as the original search, they took the median or mode value (as appropriate) as the consensus value. For the set of papers found after the time period of the original search, they used a 'consensus' and 'minority report' process for data extraction."

**Research questions:**
- RQ1 "How many SLRs were published between 1st January 2004 and 30th June 2008?"
- RQ2 "What research topics are being addressed?"
- RQ3 "Which individuals and organizations are most active in SLR-based research?" — note the deliberate revision: "The third question in our original study was 'Who is leading the research effort?'. However, since we actually measured activity not leadership we have revised the research question."
- RQ4 "Are the limitations of SLRs, as observed in the original study, still an issue?" — revised from "What are the limitations of current research?"
- RQ5 "Is the quality of SLRs improving?"

#### 1. Search process
- Sources: "IEEE Computer Society Digital Library; ACM; Citeseer; SpringerLink; Web of Science" plus **SCOPUS**. "All searches were based on title, keywords and abstract."
- **15 simple search strings** aggregated per source (the terminological breadth is the point):
  1. "Software engineering" AND "review of studies"; 2. …"structured review"; 3. …"systematic review"; 4. …"literature review"; 5. …"literature analysis"; 6. …"in-depth survey"; 7. …"literature survey"; 8. …"meta-analysis"; 9. …"past studies"; 10. …"subject matter expert"; 11. …"analysis of research"; 12. …"empirical body of knowledge"; 13. "Evidence-based software-engineering" OR "evidence-based software engineering"; 14. …"overview of existing research"; 15. …"body of published research".
- SCOPUS used two complex strings instead, each run separately for 2004–2007 and for 2008 (rationale: "reducing the number of searches reduces the problem of integrating of search results").
- **Search validation against the earlier manual search**: the automated search found 15 of the 18 manually found studies. Two misses were borderline; one "used the term 'review' but not 'literature review'". Conclusion: "the automated search was almost as good as the manual search for the most important software engineering sources."
- **Re-running the search a year later** (the "2009 search") to test indexing lag — it found all three previously missed papers, confirming they "were not in the indexing system when the original search was performed."

#### 2. Study selection — two-step screening with random reviewer allocation
> **Step 1**: "Three researchers screened each paper for inclusion independently. Two researchers from a pool of five researchers, excluding Kitchenham, were assigned at random to each paper. Kitchenham reviewed every paper. Each paper was screened to identify papers that could be rejected based on abstract and title on the basis that they did not include literature reviews or were not software engineering topics. **Any disagreements were discussed but the emphasis was on not rejecting any disputed papers.** This led to the exclusion of 42 papers."
>
> **Step 2**: "We obtained full copies of the remaining 119 papers and undertook a more detailed second screening using the following inclusion and exclusion criteria:
> - That there was a full paper (not a PowerPoint presentation or extended abstract)
> - That the paper included a literature review where papers were included based on a defined search process.
> - The paper should be related to software engineering rather than IS or computer science."
>
> Process: "To assign two of five researchers at random to review each paper and for Kitchenham to review each paper. Disagreements were discussed and resolved. The emphasis was on not rejecting any possibly relevant papers."

Attrition: 1757 papers → initial screening → 161 → step 1 (−42) → 119 → step 2 rejects 54 ("performed a literature
survey but did not have any defined search process") and 25 (related-work-only, duplicates, or not SE) → 40 → split
into T2-1 (14) and T2-2 (26) → −4 out of time frame → 22 → −3 duplicate reports (2 removed) → 20 → +3 papers known to
researchers → 23 → −4 rejected during data extraction → **19 unique SLRs in T2-2**; 33 additional unique studies overall.

Four papers rejected *during* data extraction: "Two papers were excluded because apart from the search there was
nothing systematic about their literature review… Two papers were excluded because of incompleteness. One specified
that it was presenting preliminary results based on the papers found to date. The other was a short paper which did
not report any aggregation of the identified papers."

#### 3. The "consensus and minority report" data extraction process (Fig. 3) — used for T2-2
> 1. "Two from a pool of five researchers, excluding Pretorius and Kitchenham, were randomly allocated to each study.
> 2. The two researchers independently answered the quality questions, and provided a justification for each answer.
> 3. The two researchers compared their results and came to a consensus.
> 4. Kitchenham answered the quality questions for all SLRs providing a justification for each answer.
> 5. The consensus result was then compared with a third independent extraction (performed by Kitchenham) and the two original data extractors discussed any disagreements until they reached final consensus. **Note Kitchenham did not take part in the final discussion in order for one person not to have too much influence on the results.**"

For T2-1 a simpler rule was used: "three researchers extracted information from each paper… The median value was taken
to represent the consensus view." Non-subjective data (publication sources, publication type, authors, affiliations)
was extracted by one person.

#### 4. Data extracted per SLR
> - "The type of study (SLR or mapping study)."
> - "The review focus i.e. whether the SLR was software engineering oriented or research methods oriented."
> - "The number of primary studies included in the SLR (to address the issue of whether there are sufficient primary studies in software engineering for SLRs to be useful)."

Plus, per Section 3: whether the paper posed detailed technical questions (**RQ**), addressed trends in an SE topic
area (**SERT**), or addressed the way software engineers do research (**RT**); the quality score; year; whether it
"positioned itself explicitly as an EBSE study by citing any of the EBSE papers or the SLR guidelines"; publication
source and type; number of primary studies; whether it included practitioner guidelines; the topic.

### Clarifications and refinements to earlier guidance

- **Definition split, made explicit.** "There are two different types of SLRs: **Conventional SLRs** aggregate results related to a specific research question… **Mapping studies**… aim to find and classify the primary studies in a specific topic area. They have coarser-grained research questions such as 'What do we know about topic x?' They may be used to identify available literature prior to undertaking conventional SLRs. **They use the same methods for searching and data extraction as conventional SLRs but rely more on tabulating the primary studies in specific categories.**" And: "This distinction between mapping studies and conventional SLRs can be somewhat fuzzy."
- **DARE Q3 scoring tightened relative to the 2009 tertiary study:** "These are the same criteria that were used to evaluate quality in the original tertiary study 1, except for scoring N for Q3 if papers collected quality data but did not use it. (Note the decision to penalize papers that collected quality data but did not use it was applied only to papers published after 30th June 2007.)"
- **New advice on omitted quality assessment:** "We suggest authors should provide a rationale if they do not evaluate primary study quality, for example, this is reasonable for a large scale mapping study where follow-on SLRs would be expected to consider the quality of the primary studies."
- **New advice on search practice:** "automated searches need to be backed up with manual searches of the most recent relevant conference proceedings. It may also be wise to undertake another search using an indexing system such as SCOPUS prior to publishing the results of an SLR."
- **New advice to SLR authors on discoverability:** "We strongly recommend authors to use the terms 'systematic review' or 'systematic literature review' in their keywords or title if they want their studies to be easily found."

### Caveats, traps and pitfalls

- **Indexing lag defeats automated searches.** "there may be considerable delay between a conference paper being published and information about the paper appearing in any indexing system. Furthermore, this problem is likely to affect any SLR not just our tertiary study."
- **Non-standard terminology defeats automated searches.** Seven SLRs were missed because they "Did not use the term 'literature review' (e.g. used terms such as 'literature survey' or 'assembly of studies', or just the term 'review' without any qualification)"; "Did not use any terms related to review (e.g. explained that they 'searched publication channels' or 'analyzed software engineering experiments')"; "Did not appear to be indexed by the SCOPUS system."
- **Adding "software" to a search string silently drops cross-domain SE papers.** Removing `AND TITLE-ABS-KEY("software")` recovered two relevant papers but raised the result count from 134 to 578.
- **Big primary-study counts correlate with low quality.** "a large number of papers can be obtained but the resulting studies may lack quality, in particular traceability from primary studies to conclusions (Q4) and repeatability (Q1) are likely to be compromised and individual papers will probably not be assessed for quality (Q3)."
- **Mapping studies score lower than SLRs on DARE, for structural reasons.** "mapping studies, on average, have a lower quality score than conventional SLRs. This is because mapping studies seldom assess the quality of primary studies and often do not have clear traceability between individual studies and their individual characteristics."
- **Quality-assessment blinding was not achieved.** "A threat to the validity of these results is that our assessment of SLR quality might have been influenced by knowledge that an SLR did or did not reference the guidelines… there was no attempt to formally blind the reviewers to the SLR references during the quality extraction process." Partial mitigations: form ordering (quality first), and citation data collected only after quality data.
- **Mixed extraction methods across sets limit cross-set comparison.** "the quality assessment in the study was performed in two different ways… However, quality comparisons within each group of studies are comparable."
- **One person seeing everything is a known bias, accepted deliberately.** "one person (Kitchenham) reviewed and extracted data from all the papers. Although this might potentially have introduced bias, we felt it was important for one person to have an overview of all the papers."
- **Grey literature omitted on an explicit argument:** "We make the assumption that good quality grey literature studies will appear as journal or conference papers… the main reason for grey literature not being formally published is publication bias, which occurs when negative results are not published. However, this does not appear to be a problem for systematic reviews in software engineering."
- **Border zone between SE, IS and CS is leaky**: "there is a probability that we have missed some studies that are on the borderline between software engineering, information technology and computer science."

### Checklists, rubrics, scoring schemes, evaluation criteria

**The DARE criteria** (York University CRD, Database of Abstracts of Reviews of Effects) — four questions, scored
**Y = 1, P = 0.5, N = 0**, total out of 4.

| # | Question (verbatim) | Y | P | N |
|---|---|---|---|---|
| Q1 | "Are the review's inclusion and exclusion criteria described and appropriate?" | "the inclusion criteria are explicitly defined in the paper" | "the inclusion criteria are implicit" | "the inclusion criteria are not defined and cannot be readily inferred" |
| Q2 | "Is the literature search likely to have covered all relevant studies?" | "the authors have either searched four or more digital libraries and included additional search strategies or identified and referenced all journals addressing the topic of interest" | "the authors have searched 3 or 4 digital libraries with no extra search strategies, or searched a defined but restricted set of journals and conference proceedings" | "the authors have searched up to 2 digital libraries or an extremely restricted set of journals" |
| Q3 | "Did the reviewers assess the quality/validity of the included studies?" | "the authors have explicitly defined quality criteria and extracted them from each primary study" | "the research question involves quality issues that are addressed by the study" | "no explicit quality assessment of individual papers has been attempted **or quality data has been extracted but not used**" |
| Q4 | "Were the basic data/studies adequately described?" | "Information is presented about each paper so that the data summaries can clearly be traced to relevant papers" | "only summary information is presented about individual papers e.g. papers are grouped into categories but it is not possible to link individual studies to each category" | "the results of the individual studies are not specified i.e. the individual primary studies are not cited" |

Two important qualifications:
> "Note that scoring question 2 also requires the evaluator to consider whether the digital libraries were appropriate for the specific SLR."
> "It should be noted that the information provided to help determine the answer for each question is intended to provide support for the assessment; **it is not a strict mutually exclusive classification process.**"

**Secondary evaluation frames used:** mapping of each SLR's topic onto (a) the *Software Engineering 2004 Curriculum
Guidelines for Undergraduate Degree Programs* section codes, and (b) *SWEBOK* chapter/section references — with the
rationale that "SLRs could be used by academics to help prepare course material and text books" and "the SWEBOK is
intended to identify knowledge needed by practitioners with up to 5 years experience." A per-study "Useful for
education / Useful for practitioners / Why?" judgement is also recorded.

### Threats to validity framework
No named framework; a "Study limitations" section enumerating: search completeness (missed papers due to indexing lag
and terminology), the SE/IS/CS boundary, no search for technical reports or graduate theses, mixed quality-extraction
methods across sub-sets, and single-person overview bias.

### Data extraction, classification and analysis techniques
- Classification of review focus into three types: **RQ** (detailed technical questions), **SERT** (trends in an SE topic area), **RT** (how software engineers undertake research).
- Aggregation is descriptive: counts per year, medians of primary-study counts, means of quality scores by citation status and by publication source.
- **Regression analysis** with total quality score as dependent variable and publication year, review type, guideline citation, EBSE citation, and publication type as factors. Two significant factors: "Guidelines with a parameter estimate = 0.55 and 95% confidence interval (0.257 to 1.123)" and "Mapping Study with a parameter estimate = −0.48 and 95% confidence interval (−0.876 to −0.090)." "The results of the regression analysis changes slightly if studies published in Springer book chapters were treated as a separate publication category. In that case the impact of guidelines is no longer significant at the 0.05 level (with p = 0.06), but the difference between mapping studies remains significant (p < 0.01)."

### Empirical findings worth citing

**Number of SLRs per year (Table 3)**

| Time period | Number of SLRs | Average per month | EBSE-positioned SLRs |
|---|---|---|---|
| 2004 | 6 | 0.50 | 1 |
| 2005 | 11 | 0.92 | 5 |
| 2006 | 9 | 0.75 | 6 |
| 2007 (first 6 months) | 8 | 1.33 | 3 |
| 2007 (second 6 months) | 7 | 1.12 | 6 |
| 2008 (first 6 months) | 12 | 2.0 | 10 |
| **Total** | **53** | | **31** |

**Median number of primary studies (Table 6)**

| Statistic | T1 (targeted search, 2004–Jun 2007) | T2-1 (broad search, extra papers, same period) | T2-2 (broad search, Jul 2007–Jun 2008) |
|---|---|---|---|
| Median primary studies in SLRs | 20 | 26 | 23 |
| Number of SLRs (incl. meta-analyses) | 11 | 5 | 11 |
| Median primary studies in mapping studies | 103 | 133 | 92.5 |
| Number of mapping studies | 9 | 9 | 8 |

**SLR quality by guideline citation (Table 7)**

| Cited guidelines | Statistic | T1 | T2-1 | T2-2 |
|---|---|---|---|---|
| No | Number of SLRs / Mean | 12 / 2.42 | 12 / 1.75 | 5 / 2.0 |
| Yes | Number of SLRs / Mean | 8 / 2.70 | 2 / 3.00 | 14 / 2.93 |

**SLR quality by source (Table 8)**

| Source | 2004–Jun 2007 (T1+T2-1): n / avg quality | Jul 2007–Jun 2008 (T2-2): n / avg quality |
|---|---|---|
| Journal | 17 / 2.42 | 8 / 2.56 |
| Conference | 8 / 2.69 | 4 / 3.12 |
| Workshop | 5 / 1.9 | 2 / 3 |
| Book chapter | 3 / 1.7 | 5 / 2.4 |
| — Conference | 0 / n/a | 3 / 2.5 |
| — Working conference | 2 / 1.75 | 0 / n/a |
| — Workshop | 1 / 1.5 | 2 / 2.25 |
| Technical report | 1 / 1 | 0 / n/a |

Other headline numbers:
- 33 additional unique SLRs found by the broad search over Jan 2004 – Jun 2008; "Of these papers, 17 appeared relevant to the undergraduate educational curriculum and 12 appeared of possible interest to practitioners."
- **54 literature reviews were found that used no defined search strategy at all** (versus 53 SLRs) — "it is still the case that many literature reviews are not performed in accordance with any methodology."
- Proportion of reviews aimed at research methods fell "from 40% to 18%."
- "Only six SLRs (including one mapping study) performed a full quality evaluation and two more performed a partial quality evaluation."
- "Twelve of the reviews (addressing 10 different topic areas) seemed targeted at issues of interest to practitioners with seven of the reviews explicitly concentrating on industrial studies. However, only four papers explicitly provided practitioner-oriented advice."
- Curriculum coverage (Table 5): 29 SLRs mapped onto only **17 of 233** curriculum sub-topics — "coverage of core SE topics is extremely sparse."
- Geography: "Only 7 of the 34 studies published before 30th June 2007, and only one of the 19 studies published after 30th June 2007 were co-authored by researchers with US affiliations. Most of the studies were co-authored by Europeans (42 of the 53)."
- Adoption stage: "these results suggest that groups and individuals undertaking systematic literature reviews are no longer just the innovators, but can increasingly be regarded as early adopters." / "SLRs appear to have gone past the stage of being used solely by innovators but cannot yet be considered a main stream software engineering research methodology."

---
---

## Kitchenham_2009 — "Systematic literature reviews in software engineering – A systematic literature review"
(B. Kitchenham, O. P. Brereton, D. Budgen, M. Turner, J. Bailey, S. Linkman; *IST* 51 (2009) 7–15)

**Type:** tertiary study (this is "T1", the study Kitchenham 2010 extends)

**Role in corpus:** The first SE tertiary study — it establishes the tertiary-study template (manual search of a fixed
source list, DARE quality scoring, extractor+checker) and is the baseline against which all later claims about SLR
growth and quality improvement are measured.

### Process steps or stages defined

> "This study has been undertaken as a systematic literature review based on the original guidelines as proposed by
> Kitchenham. In this case the goal of the review is to assess systematic literature reviews (which are referred to as
> secondary studies), so **this study is categorised as a tertiary literature review.**"

**Research questions:** RQ1 "How much SLR activity has there been since 2004?"; RQ2 "What research topics are being
addressed?"; RQ3 "Who is leading SLR research?"; RQ4 "What are the limitations of current research?" — decomposed into:
> - RQ4.1 "Were the research topics limited?"
> - RQ4.2 "Is there evidence that the use of SLRs is limited due to lack of primary studies?"
> - RQ4.3 "Is the quality of SLRs appropriate, if not, is it improving?"
> - RQ4.4 "Are SLRs contributing to practice by defining practice guidelines?"

**Search process — manual, fixed source list of 10 journals + 4 proceedings** (Table 1): IST, JSS, TSE, IEEE Software,
CACM, ACM Computing Surveys, TOSEM, Software Practice and Experience, EMSE, IEE/IET Software; ICSE, Metrics, ISESE.
Selection rationale: "The journals were selected because they were known to include either empirical studies or
literature surveys, and to have been used as sources for other systematic literature reviews related to software
engineering."

Process: "Each journal and conference proceedings was reviewed by one of four different researchers… The researcher
responsible for searching the specific journal or conference applied the detailed inclusion and exclusion criteria to
the relevant papers. **Another researcher checked any papers included and excluded at this stage.**"
Supplementary identification: "we contacted Professor Guilherme Travassos directly and Professor Magne Jørgensen
indirectly by reviewing the references in his web page."

**Inclusion criteria** (peer-reviewed, Jan 1 2004 – Jun 30 2007):
> - "Systematic Literature Reviews (SLRs) i.e. literature surveys with defined research questions, search process, data extraction and data presentation, **whether or not the researchers referred to their study as a systematic literature review.**"
> - "Meta-analyses (MA)."
> - "we included articles where the literature review was only one element of the articles as well as articles for which the literature review was the main purpose of the article."

**Exclusion criteria:**
> - "Informal literature surveys (no defined research questions; no defined search process; no defined data extraction process)."
> - "Papers discussing the procedures used for EBSE or SLRs."
> - "Duplicate reports of the same study (when several reports of a study exist in different journals the most complete version of the study was included in the review)."

**Data collected per study:**
> "The source (journal or conference) and full reference. Classification of the study Type (SLR, Meta-Analysis MA); Scope (Research trends or specific technology evaluation question). Main topic area. The author(s) and their institution and the country where it is situated. Summary of the study including the main research questions and the answers. Research question/issue. Quality evaluation. Whether the study referenced the EBSE papers or the SLR Guidelines. Whether the study proposed practitioner-based guidelines. How many primary studies were used in the SLR."

Extraction protocol: "One researcher extracted the data and another checked the extraction. **The procedure of having
one extractor and one checker is not consistent with the medical standards summarized in Kitchenham's guidelines, but
is a procedure we had found useful in practice.**" Allocation "was not randomized, it was based on the time
availability of the individual researchers."

Quality-scoring protocol: "Kitchenham assessed every paper, and allocated 4 papers to each of the other authors… to
assess independently. When there was a disagreement, we discussed the issues until we reached agreement. **When a
question was scored as unknown we e-mailed the authors of the paper and asked them to provide the relevant information
and the question re-scored appropriately.**"

**Data analysis** — tabulations mapped to RQs: SLRs per year and source (RQ1); guideline/EBSE citation (RQ1); count per
category, trends vs technology (RQ2, RQ4.1); topics and scope (RQ2, RQ4.1); affiliations (RQ3); number of primary
studies per SLR (RQ4.2); quality score per SLR (RQ4.3); practitioner guidelines (RQ4.4).

**Deviations from protocol, reported explicitly** (a practice worth adopting):
> "As a result of an anonymous review of an earlier version of this paper, we made some changes to our original experimental protocol: We explained our concentration on SLRs as part of EBSE. We extended the description of our research questions. We asked the authors of studies for which the answers to certain quality questions were unknown to provide the information. We clarified the link between the research questions and the data collection and analysis procedures."

### Checklists, rubrics, scoring schemes
Same DARE-4 instrument as Kitchenham 2010, here labelled QA1–QA4, scored **Y = 1, P = 0.5, N = 0, or Unknown**. The QA3
"N" anchor at this point is the *un*tightened version: "no explicit quality assessment of individual primary studies has
been attempted" (no penalty for collecting-but-not-using quality data). QA4 anchors are also looser: "Y Information is
presented about each study; P only summary information about primary studies is presented; N the results of the
individual primary studies are not specified."

### Caveats, traps and pitfalls
Three protocol deviations flagged as limitations, each with its consequence spelled out:
> - "The search was organised as a manual search process of a specific set of journals and conference proceedings not an automated search process." ⇒ "we may have missed some relevant studies… In particular, we will have missed articles published in national journals and conferences. We will also have missed articles in conferences aimed at specific software engineering topics which are more likely to have addressed research questions rather than research trends. **Thus, our results must be qualified as applying only to systematic literature reviews published in the major international software engineering journals, and the major general and empirical software engineering conferences.**"
> - "A single researcher selected the candidate studies, although the studies included and excluded were checked by another researcher." ⇒ "we are likely to have erred on the side of including studies that were not very systematic, rather than omitting any relevant studies."
> - "A single researcher extracted the data and another researcher checked the data extraction." ⇒ "**A detailed review of one of our own systematic literature reviews has suggested that the extractor/checker mode of working can lead to data extraction and aggregation problems when there are a large number of primary studies or the data is complex.**"

Other warnings:
- "The quality assessment criteria proved the most difficult data to extract because the DARE criteria are somewhat subjective."
- On a narrow-search SLR: "Juristo et al.'s study was based on a search of only the ACM and IEEE electronic databases, so this may be an example of area where a broader search strategy would be useful."
- On limited quality assessment: "relatively few SLRs have assessed the quality of the primary studies included in the review. **This is acceptable in the context of studies of research trends but is more problematic for reviews that attempt to evaluate technologies.**"

### Empirical findings worth citing
- **20 relevant studies** (19 SLRs + 1 meta-analysis) from 2506 papers screened across 14 sources; 33 relevant, 19 selected (Table A1). "Twelve studies addressed technology evaluation issues and 8 addressed research trends."
- "8 studies referenced Kitchenham's guidelines and two referenced the EBSE paper. Thus, half the studies directly positioned themselves as related to Evidence-based Software Engineering."
- Quality: "all studies scored 1 or more on the DARE scale and only three studies scored less than 2. Two studies scored 4 and two studies scored 3.5."

**Average quality score by year (Table 4)**

| | 2004 | 2005 | 2006 | 2007 |
|---|---|---|---|---|
| Number of studies | 6 | 5 | 6 | 3 |
| Mean quality score | 2.08 | 2.4 | 2.92 | 3 |
| SD of quality score | 1.068 | 0.418 | 0.736 | 0.50 |

"The average quality score appears to be increasing, the Spearman correlation between year and score was 0.51 (p < 0.023)."

**Average quality by guideline use (Table 5)**

| | Referenced SLR guidelines | Did not reference SLR guidelines |
|---|---|---|
| Number of studies | 8 | 12 |
| Mean quality score | 2.69 | 2.46 |

"A one way analysis of variance showed that the mean quality score of studies that referenced the SLR guidelines
compared with those that did not, was not significant (F = 0.37, p = 0.55). **Thus, it appears that the quality of SLRs
is improving but the improvement cannot be attributed to the guidelines.**"

- Topic concentration: "7 related to software cost estimation… 3 articles related to software engineering experiments (all investigated research trends). 3 articles related to test methods." "Of the conventional software engineering lifecycle, only testing, with three studies, has been addressed."
- Primary-study counts: "the research trends studies were based on a larger number of primary studies (i.e. 63–1485) than the technology evaluation studies (i.e. 6–54)."
- Practitioner impact: "of the 12 SLRs that addressed research questions only four offered advice to practitioners."
- Leadership: "European researchers… have been involved in 14 of the studies, in particular the Simula Research Laboratory in Norway which has been involved in 8." Their success is attributed to "the strategy of constructing databases of primary studies related to specific topic areas and using those databases to address specific research questions" — an explicitly recommended practice: "We recommend other research groups adopt similar research procedures, allowing the results of their own literature reviews to build up into a data base of categorised research papers."
- The value-of-mapping-studies argument: "Mapping studies can highlight areas where there is a large amount of research that would benefit from more detailed SLRs and areas where there is little research that require more theoretical and empirical research. Thus, instead of every researcher undertaking their own research from scratch, a broad mapping study provides a common starting point for many researchers and many research initiatives."

---
---

## Kitchenham_2013 — "A systematic review of systematic review process research in software engineering"
(B. Kitchenham, P. Brereton; *IST* 55 (2013) 2049–2075)

**Type:** empirical study of reviews / methodological SLR (the authors call it both an SR and, in the conclusions, "This systematic mapping study")

**Role in corpus:** The evidence base behind the post-2007 amendments to Kitchenham & Charters — it is the only paper
that states, item by item, **what should be removed from and added to the 2007 SLR guidelines**, and it demonstrates a
three-stage manual + citation search design with measured Kappa and search-effectiveness figures.

### Process steps or stages defined

**Aim:** "to assess whether our guidelines for performing systematic reviews in software engineering need to be
amended to reflect the results of methodological investigations of SRs undertaken by software engineering researchers."

**Research questions:**
- RQ1 "What papers report experiences of using the SR methodology and/or investigate the SR process in software engineering between the years 2005 and 2012 (to June)?"
- RQ2 "To what extent has research confirmed the claims of the SR methodology?"
- RQ3 "What problems have been observed by SE researchers when undertaking SRs?"
- RQ4 "What advice and/or techniques related to performing SR tasks have been proposed and what is the strength of evidence supporting them?"

**Initial search (Fig. 1):** informal search of EASE + ESEM proceedings 2005–mid 2012 plus personal knowledge →
55 known papers. Purpose: "This initial search confirmed that there are a substantial number of papers on the topic
and that a systematic review would be appropriate. **It also provided the information needed to guide the manual
search process.**" Gate: "Sufficient papers for study" — if no, "No study necessary."

**Stage 1 — two searches run in parallel:**
- *Manual search* of the sources the known set identified (EASE 21, ESEM 18, IST 6, ESE 2, JSS 2, ICSE 2 papers), each author searching independently, classifying include/exclude, collating, then reading and discussing disagreements. Rule: "If we could not come to an agreement about a paper we classified it as 'include'."
- *Citation-based search (forward snowballing)* on SCOPUS for papers citing five seed papers: Kitchenham & Charters 2007; Kitchenham 2004; Kitchenham, Dybå & Jørgensen 2004; Dybå, Kitchenham & Jørgensen 2005; Brereton et al. 2007.
- Both branches: collate results, **calculate Kappa**, read and discuss any papers with disagreement until agreement.

**Stage 2 — selection (Fig. 2):**
1. "Include in list of candidate papers all unique papers found from the known papers, and papers agreed for inclusion by the manual and automated search."
2. "Read the full versions of candidate papers and apply detailed inclusion/exclusion criteria **during the data extraction and quality extraction process.**"
3. "Discuss any papers that appear to violate the inclusion/exclusion conditions until all candidate papers are finally classified."
Anomaly handling: "Any papers excluded in one search and selection process but included in the other or the known set, were identified and further discussed. If we could not come to a decision about a paper it was included."

**Stage 3 — validation, snowballing, contacting researchers (Fig. 3), run in parallel with extraction:**
1. "Search process validation" — compare manual and citation results against the known set; separately, "SCOPUS was used to find papers that cited the Biolchini et al. guidelines" as an independent check.
2. "Backward snowballing. Once the search process and initial data and quality extraction was completed, the references of the selected papers were reviewed and any missing candidate papers were assessed against the inclusion/exclusion criteria."
3. "Approaching individual researchers. After snowballing, we approached any researcher or research group that produced more than two papers included in the set of selected papers and asked them if they had any other papers or research reports related to SR methodology."

**Primary study identification rules (paper ≠ study)** — the most careful treatment of this problem in the corpus:
> - "Papers were each given a unique identifier of the form PX… Each paper was given a study number of the form SY… If a paper reported the same study as another paper each was given the same study identifier."
> - "If papers by the same authors refer to the same topic but use different materials/subjects for validation, they were given different study numbers."
> - "If papers reported multiple studies, we distinguished between **validation replications** i.e. studies using the same experimental method but different materials and **independent validations** i.e. validation that use different experimental methods and/or, in the case of formal experiments, use different human subjects. **Replication validations were treated as multi-case case studies (and were only given one quality assessment since the methodology was the same) Replication validations increase the scope/size of a study not its quality. Independent validations were treated as separate studies and were given individual quality assessments.** Separate studies reported in the same paper were given an additional identifier i.e. SY.a, SY.b."
> - Duplicate reports were kept in the selected set and flagged: "We have cited the duplicate reports to increase the repeatability of our study. If we included only the most recent paper, other researchers would not know whether other related papers they found had been found by our search process and rejected (as duplicates) or not found at all."

**Inclusion criteria (verbatim):**
1. "That the main objective of the paper which may be a primary, secondary or tertiary study was either to discuss or investigate a methodological issue related to systematic reviews."
2. "That the paper discusses or investigates the construction of and/or evaluation of quality instruments used to assess the quality of primary studies or the general strength of evidence."
3. "That the paper must have a software engineering context."
4. "That the paper must be written in English."
5. "That short papers which fulfill the above criteria be included."

**Exclusion criteria (verbatim):**
1. "Secondary or tertiary studies whose main objective was to report the results of a systematic review or mapping study. Thus we excluded papers that commented on problems with searches or other processes as part of reporting an SR or mapping study."
2. "Papers discussing EBSE principles."
3. "Methodological studies with general (i.e. non-software engineering) focus."
4. "Papers for which only PowerPoint presentations or extended abstracts were available."
5. "Papers producing guidelines for performing or reporting primary studies… as opposed to guidelines for quality evaluation of primary studies."

**Data extraction.** Kitchenham extracted bibliographic data alone; **both authors independently** extracted the
study-specific data (full scheme reproduced under "Data extraction…" below); "A data collection form was set up in an
Excel spread sheet and finalized after both authors trialed the data extraction on several papers."
Broad lessons-learnt/opinion papers used a **separate free-text extraction form** (Appendix A) with columns: Issue Id ·
Issue text (in the paper authors' own words) · Type (Advice incl. best practice / Problem incl. challenge / Value incl.
benefit) · Suggestion for guidelines Yes/No · Novice issues Yes/No · Education issues Yes/No · Position in Paper (page
or table number) · Stage in SR Process addressed (Research question / Protocol / Search / Selection / Data extraction /
Quality Assessment / Data Aggregation / Data Synthesis / Reporting) · Importance (ratio of "votes", or textual) ·
Related Issue · Comment.

**Data aggregation and synthesis — three-stage meta-ethnography-like procedure:**
> "The problems and advice mentioned in more than one paper were collated by comparing the results extracted from each
> study and looking for similarities, **using an approach similar to the meta-ethnography approach proposed by Noblit
> and Hare**. This was done in three stages. Firstly Kitchenham extracted individual issues from the text and tables
> **in the terminology used in the paper, linking the issue to its position in the paper**. This was then checked by
> Brereton… Next, Kitchenham extracted from each paper the issues that seemed most important (i.e. were mentioned by
> many subjects in a specific paper, were mentioned in several other papers, or corresponded to our own experience). In
> addition, repeated issues… were identified as single issues. The extracted issues were summarized using a more
> consistent terminology… Then the issues from each paper were integrated into two lists, one for problems and one for
> advice, by comparing the important issues from each paper and **including any issue that was mentioned at least
> twice**."

Then: grouping into categories, narrative synthesis within category, and assessment of each result set for
**"Consistency (i.e. the extent to which results reported on a specific issue from different studies were consistent)"**
and **"Strength of evidence based on the number, type and quality of studies that reported the results."**

### Clarifications and refinements to earlier guidance — the 11 recommended changes to Kitchenham & Charters 2007

> 1. "To remove the proposal for constructing structured questions and using them to construct search strings. It does not work for mapping studies and appears to be of limited value to SRs in general since it leads to very complex search strings that need to be adapted for each digital library."
> 2. "To recommend the use of the Quasi-Gold standard approach to integrate manual and automated searches and evaluate the effectiveness of the search process."
> 3. "To recommend that researchers consider the use of textual analysis tools to evaluate the consistency of inclusion/exclusion decisions and categorizations."
> 4. "To remove the reference to using a data extractor and a data checker."
> 5. "To include more information about data synthesis issues, particularly the problem of dealing with qualitative methods and studies utilizing mixed methods and provide appropriate references in the guidelines."
> 6. "Either to include more advice on mapping studies or produce a separate set of guidelines for mapping studies."
> 7. "To mention the need to report how duplicate studies are handled."
> 8. "To emphasize the need to keep records of the conduct of the study."
> 9. "To mention the use of citation-based search strategies (i.e. snowballing)."
> 10. "To include more examples and advice concerning the construction of protocols."
> 11. "To included references to SE study-specific checklists."

Plus, on quality checklists: "It is also apparent that the discussion of quality checklists in the current guidelines is
not useful… **We believe that the current unhelpful guidelines should be removed but it is not clear what should
replace them.**"

Recommended database set (a refinement of earlier advice): "if researchers plan an automated search using search
strings (as opposed to a citation analysis methods such as forward snowballing), we recommend searching IEEE, ACM which
ensures good coverage of important journals and conferences and **at least two general indexing systems such as SCOPUS,
EI Compendix or Web of Science**."

The **quasi-gold standard** method, as endorsed: "an initial manual search be used to identify a set of known papers.
The known papers then act as a quasi-gold standard to assist the construction of search strings and assess the quality
of the resulting automated search by calculating the **quasi-sensitivity** of the automated search relative to the
known papers." Practical constraints added by Kitchenham & Brereton: "Manual searches should be based mainly on topic
specific conferences and journals over a specified time period. However, to act as a quasi-gold standard, it is also
useful to include some more general SE journal and conference sources… **If the sources searched manually are not
indexed by the current digital libraries (as was the case of the EASE conference before 2010), they cannot act as gold
standard for automated searches.**" A refinement from P33: "the set of known papers should be split into two sets, and
one set be used to construct search strings while the other independent set should be used to evaluate the
effectiveness of the search process."

### Caveats, traps and pitfalls

**The three dominant problems (RQ3):**
> 1. "Digital libraries in SE are not well-suited to complex automated searches."
> 2. "The time and effort needed for SRs."
> 3. "The problem of quality assessment of papers based on different research methods."

**Table 7 — Problems identified by lessons learnt and opinion survey papers** (all rows)

| Problem/issue | Mentioned pre-2008 | Mentioned post-2007 |
|---|---|---|
| Digital library interfaces & functionality inappropriate for SRs | Brereton (P6); Dybå (P23); Staples (P54); Mian (P66) | Babar (P1); Riaz (P51) |
| Time/effort consuming | Mian (P66) | Babar (P1); Riaz (P51); Zhang (P61) |
| Protocol will take a long time and/or will be revised | Brereton (P6) | Babar (P1) |
| IT and software engineering abstracts are poor | Brereton (P6); Dybå (P23) | Riaz (P51) |
| Qualitative studies complicate SR procedures | Dybå (P23); Brereton (P6) | Babar (P1) |
| Paper selection/Inclusion exclusion | Staples (P54) | Babar (P1); Riaz (P51) |
| Defining research questions is difficult | — | Babar (P1); Riaz (P51) |
| Quality assessment depends on study type | Brereton (P6); Dybå (P23) | Zhang (P61) |
| Managing quality evaluation of mixed study types | Dybå (P23) | Riaz (P51) |
| Data model and data extraction forms may change during extraction | Staples (P54) | Riaz (P51); Turner (P58) |
| Structured questions not appropriate | Staples (P54) | Riaz (P51) |
| Space constraints for papers | Brereton (P6) | Riaz (P51) |
| Choosing appropriate digital libraries | Dybå (P23) | Riaz (P51) |
| Need domain knowledge | — | Babar (P1); Riaz (P51) |
| Papers omit information | Dybå (P23); Staples (P54) | Riaz (P51) |
| Need tool/methods to support SRs | Staples (P54); Mian (P66) | — |
| SE keywords are not standardized | Dybå (P23) | Mian (P66) |

**Mapping-study-specific traps:**
> - "Using structured questions to construct search strings would not be very helpful for mapping studies that are searching for papers on a specific topic as opposed to a comparison of specific technologies."
> - "**Paper selection is more difficult for mapping studies because it is harder to define inclusion/exclusion criteria for broad topic areas** – as we noted in this study it is hard to be certain how best to react to papers that mention a topic issue in passing rather than have the topic of interest as the main focus of the paper."
> - "there is also evidence that mapping studies may miss significant numbers of relevant papers and **should not be the basis for SRs without additional more focused searches**."
> - Mapping studies "cannot be guaranteed to be complete and may quickly become out of date."

**One directly conflicting piece of advice, reported as such:** "Two papers suggested using an extractor and a checker,
whereas one paper which used that approach felt it had allowed invalid data collection procedures to go unnoticed."

**Repeatability is conditional on experience:** "**We are only likely to find reliable, auditable and consistent results
when SRs are undertaken by experienced researchers with domain knowledge.**" Evidence both ways: P45 (two expert groups,
9 of 10 studies identical, same conclusions) vs P34 (two research associates, different studies found, different from a
prior expert review). "These two results suggest that the extent of repeatability achieved is very dependent on both the
domain experience and the research experience of the researchers."

**Timescales:** "three PhD students took between 8 and 9 months to perform an SR… In spite of complaints that SRs take a
long time, 9 months is not unreasonable in the timescale of a PhD… However, SRs undertaken by MSc students are usually
constrained into a 2–3 month period which is likely to be insufficient both to learn the process and to perform a
high-quality study."

**Against automated data extraction:** "we distrust the idea of automatic extraction of results from primary studies
unless our ability to evaluate the quality of different studies improves… **If tools are used to extract data from cost
estimation studies, without considering whether the study has used an invalid metric (i.e. without appropriate
evaluation of study quality), the extracted results may be obtained very quickly but will be wrong.**"

**Problems with their own quality instrument (a warning about generic checklists in general):**
> - "we found some questions were inappropriate due to the context of the study."
> - "Our assessment of validation method type differed frequently from that of the authors of the study."
> - "**We found that using the checklist, small studies could obtain good scores although, by nature of their limited size, they could provide only limited evidence of the value of the methodology… It seemed that the quality score should only be used to differentiate between studies of the same type and size.**"
> - "applying the quality checklist will not identify invalid empirical practices such as the use of MMRE to compare cost estimation models."
- Their own reliability was poor: Pearson correlation between the two authors on *number of applicable questions* = 0.67; on *average quality score* = 0.54 ("statistically significant (p < 0.001) but still disappointingly low").

**Self-declared limitations:** authoring their own primary studies ("We may base our assessment… on our understanding of
our papers not just the information that was reported, potentially losing traceability. We may be systematically too lax
(or stringent) in our evaluation of the quality of our own papers."); automated search restricted to citation analysis of
five papers; a single digital source (SCOPUS); excluding papers that raised process issues only incidentally
("it means we may have missed some relevant papers"); and using extractor-checker for the broad lessons-learnt papers.

### Checklists, rubrics, scoring schemes, evaluation criteria

**The generic quality checklist used (adapted from Dybå & Dingsøyr), 12 items, verbatim:**

| # | Question | Response scale |
|---|---|---|
| 1 | "Is the paper based on research (or is it a discussion paper based on expert opinion)?" | Yes/No |
| 2 | "What research method was used: Experiment, Quasi-Experiment, Lessons learnt, Case study, Opinion Survey, Tertiary Study, Other (specify)? Note This is to be based on our reading of the paper not the method claimed by the author of the paper." | categorical |
| 3 | "Is there a clear statement of the aims of the study?" | Yes/Partly/No → 1, 0.5, 0; "Interpolation is permitted." |
| 4 | "Is there an adequate description of the context in which the research or observation was carried out?" | Yes/Partly/No → 1, 0.5, 0 |
| 5 | "Was the research method appropriate to address the aims of the research?" | Yes/Partly/No/Not applicable (i.e. Expert Opinion) → 1, 0.5, 0 or NA |
| 6 | "Was the recruitment strategy (for human-based experiments and quasi-experiments) or experimental material or context (for lessons learnt) appropriate to the aims of the research?" | Yes/Partly/No/NA |
| 7 | "For empirical studies (apart from Lessons Learnt), was there a control group or baseline with which to evaluate SR procedures/techniques?" | Yes/Partly/No/NA (i.e. Lessons Learnt or Expert opinion) |
| 8 | "For empirical studies (apart from Lessons Learnt), was the data collected in a way that addressed the research issue?" | Yes/Partly/No/NA |
| 9 | "For empirical studies (apart from Lessons Learnt), was the data analysis sufficiently rigorous?" | Yes/Partly/No/NA |
| 10 | "Has the relationship between researcher and participants been considered to an adequate degree?" | Yes/Partly/No → 1, 0.5, 0 |
| 11 | "Is there a clear statement of findings?" | Yes/Partly/No → 1, 0.5, 0 |
| 12 | "Is the study of value for research or practice?" | Yes/Partly/No → 1, 0.5, 0 |

Scoring convention: percentage = 100 × (points scored) / (number of *relevant* questions). Q7 and Q10 "were the
questions that we deemed inappropriate most frequently." Pure discussion papers were not scored at all.

**Table 8 — Advice given by lessons learnt and opinion survey papers** (all rows)

| Advice | Pre-2008 | Post-2007 |
|---|---|---|
| "Guidelines work well – so read them" | Dybå (P23); Staples (P54) | Babar (P1) |
| "Defining research questions is critical" | Brereton (P6); Dybå (P23); Staples (P54) | — |
| "Get your protocol validated externally" | Brereton (P6) | Babar (P1) |
| "Consult domain expert to help with search strings" | Mian (P66) | Riaz (P51) |
| "Do pilot review or mapping study before SR" | Brereton (P6); Dybå (23); Mian (P66) | Babar (P1) |
| "Do bookkeeping, record as much as you can during the review" | Brereton (P6) | Babar (P1) |
| "You should have good reasons for everything you do, justify your process (particularly the search process)" | Brereton (P6) | Babar (P1) |
| "Have one extractor & one checker" | Brereton (P6); Staples (P54) | **Contrary view – Turner (P58)** |

**Table 9 — Benefits/value of SRs** (all rows)

| Benefit/value | Benefit type | Mentioned by |
|---|---|---|
| New research findings | Scientific advances | Babar (P1); Zhang (P61) |
| Learning from studies | Personal | Babar (P1) |
| Recognition from community | Personal | Babar (P1) |
| Paper publication | Personal | Babar (P1) |
| Working experience | Personal | Babar (P1) |
| Learning research skills | Personal | Babar (P1) |
| Clear statement and structure of the state of the art | Scientific advances | Zhang (P61) |
| SRs provide a systematic way of building evidence | Methodology | Zhang (P61) |
| More reliable findings based on synthesis of literature | Methodology | Zhang (P61) |
| Repeatability | Methodology | Zhang (P61) |
| Identification of problem areas for new research | Scientific advances | Zhang (P61) |
| A source for supporting practitioners' decisions about technology selection | Industry | Zhang (P61) |

**Table 12 — Common issues (education/novices)**

| Issue | Demonstrated by |
|---|---|
| Novices can do SRs/Mapping Studies | P3, P5, P38, P47 — **Contrary view: P34** |
| Time and effort required is major problem for undergrads/MSc students | P5, P38, P47 |
| Paper selection (i.e. inclusion/exclusion) is difficult for novices | P5, P34, P47 |

**Requested guideline improvements, from P1's structured interviews, in order of popularity:**
> - "More/better quality assessment guidelines (mentioned five times)."
> - "More experiences and examples of good protocols (mentioned four times)."
> - "Simplified 'pocket' guide for people reviewing SRs and novices (mentioned four times)."
> - "More references to statistical texts and details about meta-analysis (mentioned twice)."
> - "More explanation of how to deal with qualitative studies such as case studies (mentioned once)."
> - "Templates for protocols and instructions on how to complete them (allowing for different types of SR) (mentioned once)."
> "Unfortunately, the most requested change is the one for which there is very little practical help."

**The "best compromise" quality-assessment procedure they propose (5 steps, verbatim):**
> 1. "Use a checklist similar to the one proposed in P23 and apply it to all types of empirical study (even if some checklist elements are not applicable to some types of study) but to include consideration of the empirical study type and its size/scope. However, if you are concentrating on only a few different study types, it might be preferable to have tailored checklists for each type."
> 2. "Ensure that all researchers understand how to apply the quality checklist. Checklists need to be trialed by all researchers and the reasons for disagreements investigated."
> 3. "With two researchers assess quality of primary studies, apply the checklists independently and use discussion to arrive at agreement. With more researchers use three independent assessors and take the mean score. It should also be noted that P22 disputed the value of checklists unless composed of validated items and, in particular, recommended against summing numerical values of checklist elements to form overall scores."
> 4. "Consider the issue of the validity of the empirical methods separately for different types of study."
> 5. "Consider the GRADE method for assessing overall strength of evidence (P24)."
> "However, (apart from step 3) this advice is not supported by empirical evidence nor is it obvious how more empirical evidence could be gathered."

**The three validated checklist items** (P22, correlating checklist scores against an objective measure of bias
computed by comparing a paper's effect size with the meta-analytic pooled effect):
> - "Are hypotheses being laid [sic] and are they synonymous with the goals discussed before in the introduction?" (Correlation of −0.744 with bias)
> - "Does the researcher define the process by which he applies the treatment to objects and subjects (e.g. randomization)?" (Correlation of −0.694 with bias)
> - "Are the statistical significances mentioned with the results?" (Correlation of −0.406 with bias)
*(signs shown as negative per the paper's note that "a negative correlation with bias is equivalent to a positive correlation with quality")*

### Threats to validity framework
No named taxonomy. Structured instead as "Limitations of the research method" (Section 3.9, design-time) and
"Limitations" (Section 6.3, conduct-time) — a two-part split worth borrowing: threats that arise from *how the study
was designed* versus threats that emerged from *how it actually went*.

### Data extraction, classification and analysis techniques

**Study-specific extraction scheme (both authors independently), verbatim:**
> 1. "Type of Paper: Problem identification and/or problem solution (PI) or Experience Paper, Opinion Survey or Discussion paper (E)."
> 2. "Scope of the study: Mapping studies/Conventional Systematic review/Both/Updating studies/Other."
> 3. "Summary of aims of Study."
> 4. "Main topics covered (NOT mutually exclusive): a. Educational issues: Yes/No. b. SR Participant Viewpoint: Experience Researcher (E)/Novice (N)/Not specified (NS). c. Research questions: Yes/No. d. SR claims: Repeatability, Auditability, Objectivity, Value, Other. e. Protocol Development: Yes/No. f. Search processes: Yes/No. g. Search validation/evaluation: Yes/No. h. Selection processes: Yes/No. i. Quality evaluation of primary studies: Yes/No. j. Data Extraction: Yes/No. k. Data Synthesis: Yes/No. l. Reporting: Yes/No."
> 5. "Method proposed: Name or description (e.g. Quasi-Gold Standard, Visual Text Mining)."
> 6. "Validation/Evaluation performed: Yes/No."
> 7. "Actual Validation method (as judged by each researcher): Experiment, Quasi Experiment, Tertiary Study, Case study, Data Mining (i.e. papers analyzing historical data sets), Opinion survey (Interview), Opinion Survey (Questionnaire), Lesson Learnt, Example, Other."
> 8. "Claimed Validation method (as specified by authors of paper)."
> 9. "Summary of main results."
> 10. "Any process recommendations (suggested by data extractors)."

**Reliability measurement:** Kappa for categorical extraction; Pearson correlation for quality scores. Table 5 reports
per-category Kappa — the useful lesson is *which* categories are hard to code:

| Data extracted | Kappa |
|---|---|
| Type of study | 0.795 |
| Focus of study (SRs/Mapping study/Both/NA) | **0.413** |
| Education/training related | 0.810 |
| Takes a specific viewpoint (Novice/Expert/Both/NA) | **0.277** |
| Protocol related | **0.347** |
| Discussed SLR claims | 0.624 |
| Research question related | 0.846 |
| Related to search process | 0.840 |
| Related to search validation | 0.778 |
| Related to paper selection | 0.847 |
| Related to quality assessment | 0.689 |
| Related to data extraction | 0.543 |
| Related to data synthesis | **0.372** |
| Related to reporting | **0.344** |
| Validation method | 0.507 |

Diagnosis of the low values: "one of the main reasons for disagreement was that studies often mentioned several steps
in the SR process but reported in detail only one or two steps. **We only recognized somewhat late in the data
extraction process that we were only interested in categorizing a study against SR steps that were discussed or
investigated in detail, not against all the steps that were mentioned.**" And on synthesis: "many of our disagreements
were caused by making different assumptions about what was meant by 'analysis' and what was meant by 'synthesis'."

**Textual-analysis techniques catalogued (Table 15)** — 10 papers / 11 studies, the largest cluster found. Uses:
> 1. "To refine automated search strings, P29."
> 2. "To identify similar papers as part of the paper selection process, P11, P26, P28, P46, P50, P57."
> 3. "To categorize and classify articles for a mapping study, P27."
> 4. "To select articles that address a specific research question, P50, P56."
> 5. "To extract the data needed to answer specific research questions P56, P68."

Tools named: ReVis, PEx (visual text mining); Site Content Analyser; Apache Lucene (SLR-Tool); Stanford Parser + SPARQL
(ontology); DBpedia + OpenCalais + naïve Bayes (linked data); Ibekwe-SanJuan / Agarwal / Teufel sentence-classification
algorithms; NVivo (rejected by Dybå et al. "because of problems converting pdf to text").
Evidence caveat: "**To use Wieringa's terminology, the current studies are concerned with solution validation not
implementation evaluation**… none scored 80% or more."

**Synthesis methods discussed:** thematic synthesis guidelines (P13); case-study synthesis (P12); context-distance
clustering of comparable studies (P10); meta-analysis method comparison by Monte Carlo (P20: Weighted Mean Difference,
Statistical Vote Counting, Parametric Response Ratio, Non-Parametric Response Ratio) and the finding (P21) that "the Q
test for heterogeneity is not very powerful" ("many researchers prefer the I² test, although there are also concerns
about its power"); statistical vote counting as a fallback (P67) "when meta-analysis is not applicable due to small
number of studies, diversity of measures and/or limited data."

**Reporting/visualisation evidence:** P25 — 24 participants, 8 given graphs, 8 tables, 8 both; "There was no significant
difference in comprehensibility; however, in terms of performance/time taken, graphs were the least time-consuming."
Kitchenham & Brereton's own position: "researchers should use the most appropriate mechanism to answer the research
question… However, **SRs should always provide full traceability to the source papers.**"

### Empirical findings worth citing
- **68 unique papers reporting 63 unique studies**, 2005 – mid-2012.
- Automated (citation) search: 410 unique papers from five seed papers (Kitchenham 2004: 178; K&C 2007: 150; Brereton et al.: 80; Kitchenham et al. 2004: 96; Dybå et al.: 75). Selection Kappa **0.844**; final 45 included; **precision 11%**.
- Manual search: 3418 papers screened; overall Kappa **0.849** (per source: EASE 0.783, ESEM 0.857, ESE 0.854, IST 1, JSS 1, ICSE 0.799); 54 candidates; **precision 1.6%**.
- **Search effectiveness (Table 4):** Manual 45/46 = **97.8%**; Citation 29/36 = **80.6%**; Overall 47/49 = **95.9%**. "the manual search was more effective. However, the manual search had worse precision than the automated search (1.6% compared with 11%)." Cause of citation misses: "until 2010 the EASE proceedings (although available online) were not indexed by SCOPUS."
- Independent check via Biolchini citations: 48 papers, six methodology papers, "all six had already been found by our search process."
- Stage-3 yield: 10 candidates from backward snowballing → 3 included; contacting prolific authors → 1; attending EAST 2012 → 1.
- Quality by study type (Fig. 4): "Tertiary studies exhibited the largest quality scores while examples and small experiments exhibited usually relatively low quality scores."
- Synthesis practice (P15, Cruzes & Dybå tertiary study of 49 SRs): "**half the 49 SRs they reviewed did not contain any formal study synthesis, and of those that did two thirds performed a narrative or thematic synthesis.**"
- Research-question types (P16, 53 SRs): "63% of research questions were exploratory and only 15% investigated causality… 17 of the 18 studies classified as mapping studies reported exploratory studies. However, only 13 of the 32 studies classified as SRs asked causal questions which might mean that some of the SRs were really mapping studies."
- Inclusion/exclusion practice (P48, Petersen, 139 SRs): most common objective criterion = "calculating a measure of agreement"; most common disagreement resolution = "discussion or adding another reviewer"; most common decision rule = "**at least one uncertain then include**".
- SR value evidence: "80% of the 52 SR authors responding to a questionnaire reported SRs can unexpectedly bring new research innovation"; SRs get more citations than conventional literature reviews.
- Empirical result on quality-consensus process: "using two researchers with a period of discussion did not necessarily deliver high reliability… They suggest using three or more researchers and taking an average of the 'total score'… **Simple aggregation of scores appeared more efficient (i.e. involved less effort) than incorporating periods of discussion without seriously degrading reliability.**"
- Search-string finding on empirical methods (P17): "using only the term 'experiment' achieved good precision and sensitivity. However, they note that terms describing empirical methods are used inconsistently."
- VTM efficiency (P46): "3 researchers studied 100 articles, two used VTM (B & C), one did not (A). Using an oracle of 40 papers selected by 2 researchers: A found 8.67 articles/h, B & C found 24.49 and 23.53 articles/h, with precision of 82.8% (A), 81.28% (B) and 92% (C)."

**Further research they call for:**
> - "The development and evaluation of tools to manage the SR process."
> - "The evaluation of textual analysis tools in prospective case studies (rather than post-hoc examples) and large scale experiments."
> - "Procedures for quality evaluation of SE papers when the primary studies have used a variety of different empirical methods."

---
---

## Babar_2009 — "Systematic Literature Reviews in Software Engineering: Preliminary Results from Interviews with Researchers"
(M. Ali Babar, He Zhang; ESEM 2009)

**Type:** empirical study of reviews (interview-based survey; qualitative)

**Role in corpus:** The only paper here that gets its evidence directly from SLR *practitioners' own accounts*,
stratified by experience level (advocates / followers / novices) — it is the source of the widely cited "best
practices" list and of the demand for a pocket guide and better quality-assessment guidance. Kitchenham 2013 uses it
as primary study **P1**.

### Process steps or stages defined (of the study itself — an interview survey protocol worth reusing)

- **Design:** "A survey research method… Our survey design was a cross-sectional, case control study." Data collection by **semi-structured open-ended interviews**.
- **Instrument:** "a set of open-ended questions carefully worded and arranged into six different sections. The structure of the interviewing instrument was designed with the intention of taking each respondent through the same sequence and asking each respondent the same questions with essentially the same words." Probing plan: "focus not only on the 'What' questions but also 'How' and 'Why' probes… Elaboration probes are used to keep an interviewee talking more about a subject." Piloted: "it was estimated that an interview would take between 70 and 90 minutes."
- **Sampling frame and stratification (verbatim definitions):**
  - **Advocates** — "Researchers who introduced SLR methodology and EBSE in SE, and have published many SLRs they conducted in the past years"
  - **Followers** — "Researchers who have participated in planning, conducting and reporting one or more SLRs"
  - **Novices** — "PhD research students who have experiences in performing SLRs"
- **Recruitment:** 24 identified "based on sampling their publications on SLRs in SE"; 21 replied; **17 interviewed** across seven countries and ten organisations; 13 interviews in English, 4 in Mandarin (all translated for analysis).
- **Preparation step worth copying:** "A few days (2 or 3 days) before the scheduled interview, each participant was provided, via email, with a document outlining the main themes… We also asked them to gather some facts and figures about their respective SLRs in order to facilitate the discussion."
- **Ethics/confidentiality protocol:** a written data-protection statement sent in advance and repeated before each interview; explicit permission sought for recording; "we explicitly made it clear to the participants that the research team would not share the data with anyone in a way that could reveal the opinions and views of individuals."
- **Recording:** "Most interviews were recorded with two digital recorders, one for each researcher. The researchers also took extensive notes." ~28 hours of audio.
- **Analysis:** staged transcription (a defined subset of questions transcribed first); "content analysis was used to analyze the data"; "All transcriptions were entered into NVivo for qualitative analysis."

**Interview instrument sections and example questions (Table 9), verbatim:**

| Session | Example question |
|---|---|
| Working with Guidelines | "What are the source(s) that you learned SLR from?" · "What were the key documents to guide the execution of your SLR?" · "Are you able to access any other kinds of help or advice (such as your colleagues) except the guidelines for your SLR?" |
| Values of SLRs | "Do you think SLR in SE will be as effective as in other disciplines? Why?" · "What is the value to people conducting SLRs?" · "Do you think SLR is appropriate for novices, esp. first-year research student? Please explain." |
| Experiences & Best Practices | "If your colleagues are planning their own SLR, what are the best practices you want to share with them?" · "From your point of view, what are the major reasons caused the problems in your systematic review" · "Will you perform another SLR in the near future? If so, how much do you expect to improve your productivity?" |
| Challenges and Fulfillment | "What encouraged and motivated you most in your SLRs?" · "What frustrated you most in your SLRs?" |

### Checklists, rubrics, scoring schemes, evaluation criteria

**Table 6 — Best practices from SLR practitioners** (all nine rows verbatim; columns are counts of Advocates / Followers / Novices endorsing)

| # | Best practice | Adv. | Fol. | Nov. |
|---|---|---|---|---|
| 1 | "Make your research questions as concrete and explicit as possible, keep focus on them and a narrow world. Don't waste lots of time on irrelevant literature" | 1 | 3 | 2 |
| 2 | "Read the guidelines, e.g. Kitchenham's guidelines, make sure your understand, and then follow the guidelines; but never expect the guidelines give all answers to the problems" | 1 | 2 | 1 |
| 3 | "Find and read good SLR examples, experiences, and protocols from others as many as you can." | 0 | 3 | 1 |
| 4 | "Expect protocol take a long time, allocate appropriate time for it, and expect changes. Get your protocol validated externally, as a low-quality protocol may lead to a lot of rework. Share the protocols within community." | 0 | 2 | 2 |
| 5 | "Do pilot review, it is necessary especially when you're not familiar with the domain for SLR" | 0 | 1 | 3 |
| 6 | "Have somebody with experience in conducting SLRs involved or being in touch, make them available to consult to, and ask them check your questions and results." | 0 | 3 | 0 |
| 7 | "Do bookkeeping, record as much as you can during the review." | 0 | 2 | 1 |
| 8 | "You should have good reasons for everything you do; you should be willing to do it. Don't stop thinking, and be very careful about what you're doing" | 1 | 0 | 2 |
| 9 | "Clarify criteria for search, selection and quality as much as you can, and as good as you can." | 0 | 2 | 1 |

Plus an unnumbered team-size heuristic: "two followers recommended the ideal team size for SLR is to get three people
involved. If less, it might be difficult to avoid subjective bias; if more, it may take much time and effort in
communication, coordination and getting agreement, particularly in a distributed working environment."

**Table 2 — Improvement suggestions for SLR guidelines** (all rows verbatim)

| Topic | Description | Adv. | Fol. | Nov. |
|---|---|---|---|---|
| Quality assessment | "Needs to know how to assess the quality of evidence; the current quality criteria could not be applied to all SLRs." | 0 | 2 | 3 |
| Experience/examples | "Some experiences should be grouped for different topics; real examples of good protocols could be helpful." | 1 | 2 | 1 |
| Simplified version | "Some kind of pocket version guide for people who are reviewing SLR papers; a simplified version is needed for novices." | 0 | 2 | 2 |
| Quantitative analysis | "More references of statistic methods should be included in guidelines; more details about how to do meta-analysis are expected." | 0 | 1 | 1 |
| Qualitative analysis | "Most of guidelines are relevant to quantitative studies and analysis, however in SE, we also have to deal with qualitative studies, like case studies." | 1 | 0 | 0 |
| Protocol template | "Need to improve review protocol templates, to describe how to fill the protocol, which depends on the type of SLR." | 0 | 1 | 0 |

**Table 7 — Most challenging things in SLRs**

| Challenge | Adv. | Fol. | Nov. |
|---|---|---|---|
| Time/effort consuming | 2 | 3 | 1 |
| Searching literature | 1 | 3 | 1 |
| Guiding students | 1 | 2 | 0 |
| Defining research questions | 0 | 2 | 1 |
| Too much rework | 0 | 1 | 0 |
| Study selection | 0 | 1 | 0 |
| Getting agreement | 0 | 1 | 0 |
| Lack of guidance | 0 | 0 | 1 |
| Lack of domain knowledge | 0 | 0 | 1 |
| Writing protocol | 0 | 0 | 1 |
| Rejection of paper | 0 | 0 | 1 |

**Table 8 — Encouragements and fulfillment in SLRs**

| Motivator | Adv. | Fol. | Nov. |
|---|---|---|---|
| New findings from SLR | 0 | 5 | 0 |
| Learning from studies/getting knowledge | 1 | 2 | 1 |
| Recognition from community | 0 | 3 | 0 |
| Paper publication | 0 | 1 | 2 |
| Working experience | 0 | 1 | 0 |
| Learning research skills | 0 | 1 | 0 |

**Table 3 — Is SLR appropriate for novices?** Yes: 1 Adv / 3 Fol / 4 Nov · No: 0 / 1 / 0 · It depends: 2 / 4 / 2.
**Table 4 — Factors influencing appropriateness to novices:** Experience needed 3 (43%); Too much time & effort 3 (43%);
Work with experts 2 (29%); Get focused 2 (29%); Domain knowledge needed 1 (14%).
**Table 5 — SLR's effectiveness in SE vs medicine:** "It could be" 1/5/2; "I don't think so" 2/1/4; "Hard to say/I don't know" 0/1/0.

### Caveats, traps and pitfalls
Three problem clusters, in the interviewees' own words:
- **Databases**: "It is the most frustrating thing with us, because it needs a lot of work, a lot of noise risk you." And on non-determinism: "**When I search ACM, we got one result, when I search two days after, I got different results. Sometime the paper includes, sometime the (same) paper not included. So what to do?**"
- **Publication**: "Some people who are reviewing papers that claim as an SLR do not know well what is SLR, which results in some low quality SLRs being published in conferences and journals. Some of them do not have explicit research questions, well-defined search strategy and selection process."
- **Education**: "some PhD student worked in his SLR, but his supervisor who have never done one before, you couldn't believe the kinds of questions come up. It's like try to help someone write Java application, where you haven't done really coding with Java?"

Other warnings:
- Guidelines will not cover you: "the problems you have may be really specific or difficult, you couldn't get support in guidelines, because they are not covered."
- Reporting: an SLR "is only valuable if (the authors) list papers (included), … even it has retrieved only a small number of papers."
- On SE vs medicine: "the context or environment in SE is not mature and controllable enough (like in medicine)"; "questions need to be chosen very carefully in SE to make sure SLR is actually suitable tool to use."
- On the novice question, the dissenting view: "PhD students should do a lot of literature reviews, but doing SLR is quite different thing, it's very focus and (needs) very well-defined research questions."
- Mapping study as the on-ramp: "In EBSE, mapping study should be 'a starting point to identify sources of material in particular topic area'"; for first-year students "it can be started with mapping study."

### Threats to validity framework
No named taxonomy; a "Limitations" section covering: **recall bias** ("our results are based on the recollection of the
interviewees. This is a well known weakness of retrospective interviews"); **accuracy/completeness of what was heard**
(mitigated by two recorders, verifying transcriptions against notes, two researchers present at most interviews);
**interpretation validity** ("One way was to minimize the amount of interpretations and speculations at this stage. We
intend to interpret the findings in light of the data that we plan to acquire, e.g. papers of the interviewees, in order
to apply triangulation"); **external generalizability** ("qualitative studies are usually considered weak in this
respect and we do not claim the generalizability of the findings").

### Empirical findings worth citing
- Methodology sources actually used: "The most influential SLR guidelines in SE have been developed by Kitchenham and Charters, which are recognized by almost all interviewees." "In addition to Kitchenham's guidelines, **all advocates also learned and followed the guidelines and materials from other disciplines, especially medicine and sociology**"; Petticrew & Roberts "was recommended to SE community by three of our interviewees independently."
- Knowledge transmission is social, and unequally distributed: "**All followers except one have direct connections to at least one advocate. In contrast, all novices were not able to access the guidance from any advocate directly.**"
- Productivity improves with repetition: "The effort at beginning is on understanding how to write protocol, what SLR really needs … after that, you concentrate on the analysis of your data"; "it could be half time now, because we had already done that, we know how to do things." Caveat: "if the (subject) domain changes, then perhaps no significant improvement."
- Perceived audience: "Compared to the value to industry, most interviewees recognize SLR is more valuable to academia."

---
---

## Mourao_2017 — "Investigating the Use of a Hybrid Search Strategy for Systematic Reviews"
(Erica Mourão, Marcos Kalinowski, Leonardo Murta, Emilia Mendes, Claes Wohlin; ESEM 2017)

**Type:** empirical study of reviews (method proposal + two replication case studies)

**Role in corpus:** Defines and gives the first evaluation of the **hybrid search strategy** — one database (Scopus) as
a structured way to obtain a snowballing seed set, followed by backward and forward snowballing. It is the paper that
supplies the boundary condition on when the strategy works (narrow SE topics) and when it does not (broad,
cross-disciplinary populations).

### Process steps or stages defined — the hybrid search strategy

Positioning: "Our proposed hybrid search strategy is to be applied during the conducting the review phase… it addresses
the first two activities that happen within this phase, as per the SLR process in [Kitchenham & Charters]:
**identification of research** and **selection of primary studies**."

**A. Identify Research using Scopus Database Search.**
> "The first step of the hybrid strategy is to define the search string to identify relevant studies using the chosen
> digital library. This should be done similarly to traditional SLRs, e.g., based on the PICO strategy. **Given that
> snowballing should be done on the identified papers, it is less critical to identify all possible synonyms as if the
> database search is the sole driver for identifying relevant papers.** Scopus was chosen as the digital library
> because it covers several disciplines and is defined as the largest abstract and citation database of peer-reviewed
> literature. Moreover, it presents a clear and consistent search interface."

**B. Select Primary Studies.**
> "Once the search has been performed, selection criteria are applied to identify relevant primaries studies, hence
> resulting in a set of candidate studies. **The seed set should only include papers that eventually will be included,
> and hence the quality of the papers needs to be investigated before being used within the seed set.**"

**C. Apply Backward Snowballing.**
> "BS is conducted on the set of studies obtained from activity B and is executed in several steps. The first step is
> to carefully review the reference list of each paper searching for new studies. New studies should only be included
> in the SLR if they pass the selection criteria. As described by Wohlin, the process continues with new iterations on
> the papers selected during the previous iteration and ends if there are no new papers to be selected."

**D. Apply Forward Snowballing.**
> "FS is also conducted from the obtained seed set and divided in iterations. It comprises searching for new studies
> that cite the studies contained in the seed set. As done by Wohlin, we suggest using **Google Scholar**. Similarly to
> BS, new studies should only be included in the SLR if they pass the selection criteria and the process continues with
> new iterations until there are no new papers to be selected."

Declared deviation (which makes their own evaluation conservative): "When conducting BS, a minor deviation from the
guidelines was made by not applying FS on the papers found in BS. **The deviation disfavours snowballing, and hence it
makes the evaluation somewhat conservative.**" The same was done in reverse for FS.

Output: "The result from applying the hybrid strategy is a set of papers that we hypothesize to include the same
studies that would have been retrieved by means of database searches using different databases, and, potentially with
more effort."

### Clarifications and refinements to earlier guidance
- Refines Wohlin's snowballing guidelines by giving a **structured, reproducible way of constructing the seed set** — a single-database search with the PICO-derived string, rather than an ad hoc start set: "enable identifying a good seed set for BS and FS in a structured way."
- Refines K&C 2007's multi-database search advice by arguing one broad-coverage database suffices as an entry point, on the grounds that snowballing compensates for missed synonyms.
- Endorses the Wohlin et al. sampling position over the exhaustiveness position: "According to Kitchenham et al. the aim of an SLR is to find and summarize all relevant studies addressing one or more research questions using an unbiased search strategy, **while Wohlin et al. argue that it is more a matter of how good sample it is possible to identify.**"

### Caveats, traps and pitfalls
- **The strategy's scope condition:** "a preliminary interpretation is that **the hybrid strategy may be more reliable for more narrow study populations and not recommended for large study populations covering a broader range of domains.**"
- **Cross-disciplinary populations break citation-based search:** "this could be due to the large study population, including papers from different areas, **which do not tend to cite each other**."
- **BS and FS are not substitutes:** "BS and FS do not replace each other and may both contribute to the recall of relevant papers. This makes sense, given that BS may help identifying older references while FS favours finding newer ones. Since the hybrid strategy involves selecting a seed set from only one digital library in which older and newer references that are not indexed might still be missing, **ideally BS and FS should both be applied according to the guidelines**."
- **Grey literature is systematically missed** — one of the five missed papers in case study 1 was a master's dissertation.
- **A paper can be indexed in your database and still be missed by your string** — two of the five misses (S12, S17) "indexed in Scopus, but not found using the search string when applied in Scopus."
- **Digital library heterogeneity is a real cost, not just an annoyance:** "the search strings of SLR1 and SLR2 had to be adapted for the different digital libraries. In particular, the ACM DL required significant adaptations in both cases until retrieving a manageable amount of results" — in SLR2's case the unadapted string "would have returned 386442 papers" in ACM DL.
- **Published SLR baselines are often not fully documented, which corrupts the comparison:** SLR1's authors "performed additional opportunistic and unspecified searches using Google Scholar. The paper does neither document which (if any) of the included papers were identified from those additional searches, nor the number of analysed papers… Consequently, 4062 is an underestimate."
- **Relative recall understates the strategy:** "the use of relative recall may miscount true positive studies obtained by the hybrid approach that were not included in the original SLR. Consequently, the precision and the relative recall of the hybrid approach are lower bounds."

### Threats to validity framework
Four named categories, the standard Wohlin/Runeson set:
- **Internal validity** — "The hybrid approach was defined based on the SLR process described in the guidelines for conducting SLRs and for applying it we followed the guidelines for conducting snowballing with a minor deviation. The first author applied the approach and each step was reviewed by at least one of the other authors."
- **Construct validity** — "we only verified which of the included studies were also retrieved by the hybrid strategy, and hence the authors of the original SLRs applied all inclusion and exclusion criteria. Moreover, the use of relative recall may miscount true positive studies…"
- **Reliability** — "We evaluated the hybrid strategy using Scopus and Google Scholar for FS. The evaluation process was straightforward, clearly described and replicable."
- **External validity** — "The study of applying the hybrid strategy was conducted on two peer reviewed SLRs. However, the study findings are not generalizable and replications on other SLR to reinforce our findings are required."
Overarching limitation: "our analyses were based on evaluating the hybrid strategy on only two SLRs."

### Data extraction, classification and analysis techniques — the evaluation metrics
- **RQ1 (efficiency) → precision**: "we measure precision as being the percentage of the analysed papers that were included in the SLR. Note that precision is an appropriate metric for representing efficiency since it degrades in face of noisy results."
- **RQ2 (completeness) → relative recall**: "we measure the relative recall as being the percentage of included papers of the published SLR that were retrieved by the hybrid research strategy."
- Supporting artefacts: citation graphs for both SLRs, and a **Venn diagram of studies found by BS vs FS** used to argue the two are complementary.

### Empirical findings worth citing

**Case study 1 — SLR on requirements elicitation techniques (Dieste & Juristo 2011; cross-disciplinary, 26 included papers)**

| Step | Result |
|---|---|
| Scopus seed set | 15 of 26 included studies retrieved, out of 737 results |
| Backward snowballing | iter. 1: +4 within 425 references; iter. 2: 0 new within 125 references → **19/26 (73%) via Scopus + BS** |
| Forward snowballing | iter. 1: +2 within 459 citing papers; iter. 2: +1 within 36; iter. 3: 0 within 2 → **18/26 (69%) via Scopus + FS** |
| Combined | **21 of 26; relative recall 81%; precision 21/1804** |
| Baseline (published SLR) | 4062 papers retrieved; precision 26/4062 |
| Verdict | RQ1 **yes** (fewer papers, higher precision); RQ2 **no** (5 papers missed) |

Diagnosis of the five misses: "three papers not found using the hybrid approach are from other disciplines (S8, S17 and
S23), one paper is from SE (S12) but with relatively few citations and finally one paper is from the grey literature (S25)."

**Case study 2 — SLR on cross- vs within-company cost estimation (Mendes et al.; narrow SE topic, 25 included papers)**

| Step | Result |
|---|---|
| Scopus seed set | 17 of 25 included studies retrieved, out of 603 results |
| Backward snowballing | iter. 1: +6 within 422 references; iter. 2: 0 new within 148 references → **23/25 (92%) via Scopus + BS** |
| Forward snowballing | iter. 1: all 8 remaining found, analysing 1089 citing papers → **25/25 (100%) via Scopus + FS** |
| Combined | **25 of 25; relative recall 100%; precision 25/2262** |
| Baseline (published SLR) | 1752 papers analysed (772 original + 980 update), plus undocumented manual searches |
| Verdict | RQ1 **no** (more papers, lower precision — but "the hybrid approach involves a simpler search process and did not require handling awkward adjustments"); RQ2 **yes** |

Interpretation offered: "We believe that this behaviour could be related to having a narrower study population, where
relevant papers tend to cite each other more consistently."

Overall conclusion: "the hybrid strategy potentially represents a reasonable alternative when conducting an SLR on a
specific topic within the SE domain. However, additional evaluations are required before drawing further conclusions."

### Related prior evidence catalogued by the paper (useful as citation chain)
- Jalali & Wohlin: database search vs snowballing on agile practices in GSE — "there were no major differences between results."
- Wohlin (2014): snowballing guidelines validated by replicating a database-search SLR — "using snowballing, as a search strategy might be a good alternative to using database searches; however results are also dependent on selecting a seed set carefully."
- Badampudi et al.: independent researchers ran database vs snowballing — "the effectiveness of snowballing is comparable to that of database searches."
- Wohlin (2016) and Felizardo et al. (2016): **forward snowballing for updating SLRs (second-generation studies)** — "FS was able to find all relevant papers to update the SLR"; caveat: "these studies had a different focus… in which previously included studies are already available, making it easier to define a representative seed set."

---

## Cross-cutting notes for `docs/methodology/`

1. **SMS process spine** = Petersen 2015's three phases (plan / conduct / report) with the 26-action checklist as the
   operational task list and the five rubrics as the acceptance criteria. Petersen 2008 should be cited only for
   keywording and bubble plots, both of which Petersen 2015 restates more precisely.
2. **Tertiary study process spine** = Kitchenham 2009 (manual, fixed source list) → Kitchenham 2010 (broad automated
   search + consensus-and-minority-report extraction). The DARE-4 instrument with the tightened Q3 anchor (2010
   version) is the reusable quality rubric.
3. **Two irreconcilable positions on search completeness** must be represented as a choice, not a rule:
   exhaustiveness (K&C 2007, carried by Kitchenham 2010's Q2 anchors, which reward ≥4 digital libraries) versus
   good-sample (Petersen 2015 §5.1.2, Wohlin et al., Mourão 2017). Mourão 2017 supplies the deciding variable:
   population breadth.
4. **Guidance that is explicitly withdrawn** and should not be reproduced: structured questions → search strings
   (Kitchenham 2013 #1); extractor + checker (Kitchenham 2013 #4, contradicted by two earlier papers that recommended
   it); full PICO(C) for mapping studies (Petersen 2015); the K&C 2007 quality-checklist discussion (Kitchenham 2013 §6.2).
5. **Two distinct validity frameworks** appear: Petersen & Gencel (descriptive / theoretical / generalizability /
   interpretive / repeatability) used by Petersen 2015, and the Wohlin/Runeson four (internal / construct /
   reliability / external) used by Mourão 2017. Kitchenham 2009/2010/2013 use no named framework, only a limitations
   narrative — with Kitchenham 2013's design-time vs conduct-time split being the most transferable structure.
