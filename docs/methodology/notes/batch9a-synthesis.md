# Batch 9a — Research synthesis methods for secondary studies

Source extractions: `scratchpad/txt/cruzes_recommended_2011.txt`, `ribeiro_using_2014.txt`,
`cruzes_research_2011.txt`. All prose below is paraphrase unless enclosed in quotation marks.

---

## Cruzes & Dybå 2011 — "Recommended Steps for Thematic Synthesis in Software Engineering" (ESEM'11)

**Role in corpus:** This is the operational how-to for the single most common synthesis method in
SE secondary studies — it turns "we did a thematic analysis" into five named steps with a 21-item
checklist, and is the paper to follow when an SMS/SLR/RR needs to actually synthesise rather than
tabulate.

### What the paper claims as its own contribution

The authors are explicit that they are *extending*, not inventing. Thematic analysis comes from
primary qualitative research; Thomas & Harden's "thematic synthesis" (2008) adapted it to
systematic reviews in three overlapping steps — line-by-line free coding of primary-study findings,
organising free codes into descriptive themes, and developing analytical themes. Cruzes & Dybå's
contribution is (a) conceptualising the approach for SE as a five-step scientific inquiry
paralleling primary research, (b) the checklist in their Table 2, (c) SE-specific adaptations
(chunk-level rather than line-by-line coding; a structured extraction template), and (d)
illustrating every step with quotations drawn from the eight SE reviews their own tertiary study
[Cruzes & Dybå 2011, IST] had classified as thematic syntheses.

A motivating observation from Section I worth carrying forward: **none of those eight SE reviews
cited any synthesis method at all**, which the authors read as strong evidence that concrete steps
and recommendations were needed.

They also note the steps are presented sequentially only to give the recommendations a structure —
in practice reviewers iterate among them. Planning, identification and selection of primary studies
are assumed already done.

### The method, step by step

The process narrows data through increasing abstraction. Figure 1 gives the expected funnel, and
these numbers are useful as sanity checks on a real synthesis:

| Stage | Artefact | Expected volume (Fig. 1) |
| --- | --- | --- |
| Initial reading of data/text | immersion | many pages of text |
| Identify specific segments of text | candidate units | many segments of text |
| Label the segments | codes | 30–40 codes |
| Reduce overlap, translate codes into themes | themes | 15–20 themes |
| Create a model of higher-order themes | model | 5–7 themes |

Figure 4 states the same idea as levels of interpretation: Text → Codes → Themes → Model, with
abstraction (and generalisability) rising at each level.

---

#### Step 1 — Extract data (Section II)

*Purpose.* Obtain the essential text and data from primary studies explicitly and consistently,
against a defined extraction strategy.

*Input.* The selected set of primary studies. *Output.* A populated extraction form; possibly an
updated review protocol.

*Technique.*

- **Read the whole set at least once before extracting.** The paper is emphatic that this immersion
  step is tempting to skip and that the thematic-analysis literature advises strongly against
  skipping it. Immersion is what makes you familiar with the depth and breadth of the evidence, and
  initial ideas and candidate patterns are shaped during this first reading. Immersion was
  explicitly stated in only half of the eight SE thematic syntheses examined.
- After the initial reading, reviewers can **update the protocol**, which contains among other
  things the data extraction strategy and the synthesis strategy.
- Extract via a **structured reading technique** (Cruzes et al.'s technique for exploring the
  evidence of a systematic review), following a procedure for identifying context information and
  findings.

*The three kinds of data to extract* (this triple is the paper's core extraction recommendation):

1. **Publication details** — authors, year, title, source, abstract, aims.
2. **Context descriptions** — subjects, technologies, industry, settings (also instruments, study
   type in the Fig. 2 template).
3. **Findings** — results, behaviours, actions, phenomena, events, quotes; each carrying its origin
   and strength of evidence.

The Figure 2 template is a 1-to-many chain: one publication has at least one context (more if the
paper reports several studies), and each context has at least one finding, probably many. Staples &
Niazi's instantiation (Fig. 3) used Publication → Study → Quote, where a Publication reports one or
more Studies which contain one or more Quotes.

*Where findings live.* Most likely in the results, analysis-of-results, discussion and conclusions
sections. **Tables and figures are also sources of findings** — relationships expressed only
visually can be extracted and translated into textual form.

*Heuristics for deciding whether a statement is a finding.* Ask whether it: states the results of
measurements; summarises raw data; highlights a specific characteristic of the raw data; provides
additional insight about tables or figures; summarises the results of analyses; can be used to
answer the research question(s); reflects the main results of the study.

*Rigour controls.* Extract independently by two or more researchers wherever feasible, compare, and
resolve disagreements by consensus or by arbitration from an additional independent researcher.
Where SE papers lack detail (a recurring problem), extract in **consensus meetings** instead.
Uncertainties about any primary source where agreement cannot be reached should be pushed into
sensitivity analysis or into the trustworthiness evaluation rather than silently resolved.

*Known obstacle.* Publication details extract straightforwardly, but study **aims are often unclear
and may need analytical work to recover**, and **context is the hardest of the three** — papers
frequently omit design detail, do not address bias and validity, and describe data collection,
analysis, samples and settings poorly. In such cases data extraction is hindered outright.

*Checklist items 1–4.* All papers read carefully for immersion; segments pertaining to the synthesis
objectives identified; publication details, context descriptions and findings extracted from all
papers; extraction checked by another researcher.

---

#### Step 2 — Code data (Section III)

*Purpose.* Identify and code interesting concepts, categories, findings and results systematically
across the entire data set.

*Input.* Extracted segments. *Output.* A list of initial codes with definitions and frequencies,
validated by a second researcher; roughly 30–40 codes.

*What a code is.* Descriptive labels applied to segments of text from each study. Coding is more
than applying a label — it requires a clear sense of the context in which the finding was made, and
involves identifying one or more passages exemplifying the same theoretical or descriptive idea. It
lets the researcher organise and group similar data into categories that share a characteristic —
"the beginning of themes". Which data 'look alike' and 'feel alike' is settled by classification
reasoning plus tacit and intuitive sense. The paper is blunt that nobody gets coding right first
time; codes and categories refine as work proceeds. Codes go by many names in the literature —
indices, categories, labels, concepts.

**How codes are created — the three approaches.** This is the part most often needed verbatim in
practice:

| Approach | Origin of codes | Mechanics | Risk |
| --- | --- | --- | --- |
| **Deductive / a priori** (Miles & Huberman) | A provisional "start list" derived from theory, research questions, hypotheses, problem areas, key variables the researcher brings to the study | Structure of initial codes is defined *before* coding the data; a start list typically runs from a dozen up to 30–40 codes — a number holdable in short-term memory without constant reference to the full list, provided the list has clear structure and rationale | Forcing data into a category merely because a code exists for it |
| **Inductive / grounded theory** (Corbin & Strauss) | Purely from the data | Data reviewed line by line; a code is assigned as each concept becomes apparent; specifications of codes are developed and refined as more data is reviewed. To test whether a code is correctly assigned, compare the text segment against segments previously given the same code and judge whether they reflect the same concept — the **constant comparison** method, which both refines existing code dimensions and surfaces new codes | Slow; impractical at scale |
| **Integrated** (Bogdan & Biklen; Lofland) | Both | Inductive ground-up development of codes *inside* a deductive organising framework of code *types*. The framework is a general accounting scheme that is not content-specific but points to general domains within which codes are developed inductively | — |

**Cruzes & Dybå recommend the integrated approach as most relevant for systematic reviews**, because
reviews are driven by theoretical interests embedded in the review questions: the reviewer arrives
with specific questions to code against, while also having to relate to the concepts around which
the primary study authors organised their own findings. Whether codes are pre-specified or emergent,
**clear operational definitions are indispensable** so codes can be applied consistently by one
researcher over time or by several concurrently.

**Four code types particularly useful for generating categories, themes and theory in SE research**
(the paper notes Saldaña describes at least 30 coding methods overall):

1. Conceptual codes — key concepts and their essential dimensions.
2. Relationship codes — links between conceptual codes.
3. Subject codes — subjects' perceptions.
4. Context characteristic codes.

*SE-specific adaptation.* Thomas & Harden's line-by-line coding is judged **unlikely to be practical
for large numbers of studies**; in SE reviews it is more appropriate to work with the *chunks* of
data extracted in Step 1. Depending on the research questions, the reviewer focuses on extracted
findings alone or on some combination of findings and context.

*How thematic coding relates to neighbouring methods.* Because thematic techniques often adopt
constant comparison, thematic analysis gets compared to content analysis and grounded theory. Content
analysis also compares and sorts, but its aim is to *quantify* content against predetermined
categories, establishing significance largely by frequency of themes — thematic analysis does not.
Grounded theory is distinguished by some writers on the basis of the unit of text coded (incident by
incident, or line by line); thematic analysis specifies no particular length of text per code.

*Rigour controls.* Perform coding with at least two researchers who validate the codes. Codes must
have explicit boundaries (definitions) so they are neither interchangeable nor redundant, and must
be limited in scope and focused on the object of analysis — otherwise you end up coding every
sentence. Give equal attention to all papers. Qualitative analysis software helps.

*Checklist items 5–9.* Important segments labelled and coded; coding done across the entire data set
at a level appropriate to the research questions; a list of initial codes with definitions and
frequencies created and checked by another researcher; consistency or inter-rater reliability checks
performed to establish the credibility of coding; clear evident connections between text and codes.

---

#### Step 3 — Translate codes into themes (Section IV)

*Purpose.* Combine codes into overarching themes, sub-themes and higher-order themes.

*Input.* ~30–40 codes. *Output.* ~15–20 themes, plus a visual representation (thematic map).

*What a theme is.* The paper offers three definitions rather than one, because usage varies and
'theme' is used interchangeably with 'category', 'domain', 'phrase', 'unit of analysis':

- Saldaña: a theme is an outcome of coding, categorisation and analytic reflection — not something
  that is itself coded.
- Boyatzis: a theme at minimum describes and organises possible observations, at maximum interprets
  aspects of the phenomenon; it may be identified at the **manifest** level (directly observable in
  the information) or at the **latent** level (underlying the phenomenon).
- DeSantis & Ugarriza: a theme is an abstract entity bringing meaning and identity to a recurrent
  experience and its variant manifestations, capturing and unifying the experience into a meaningful
  whole.

*Technique.* Consider how different codes may combine into an overarching theme. Themes pull a lot
of material into more meaningful and parsimonious units and help build a cognitive map — an evolving
integrated schema for understanding local incidents and interactions. As the researcher distances
from the text, abstraction and generalisability of the theme definitions both rise.

This is explicitly **not a single-pass step**: as codes are analysed, first-cycle codes may be
subsumed by others, relabelled, or dropped entirely; coded data gets rearranged and reclassified
into different and even new codes. The stopping rule is **saturation** of the possible themes
emerging from the data.

*Named techniques available for this step* (via Saldaña): pattern coding, elaborative coding,
longitudinal coding; and more grounded-theory-flavoured options — focused coding (Charmaz), axial
coding and theoretical/selective coding (Corbin & Strauss).

*Representation.* Use visual aids to sort codes into themes — thematic networks, tables, tree-maps,
mind-maps. Figure 5 shows a thematic map: codes clustering into themes, themes clustering into
higher-order themes, arranged around a central topic.

*Observed practice.* In the SE thematic syntheses examined this step was usually **not described in
detail**; authors were generally not explicit about how codes were synthesised and translated into
themes. The exception cited is Beecham et al., who derived 9 themes (aspects of SE that motivate
software engineers) from 21 codes (motivators).

*Checklist items 10–13.* Themes created from a thorough, inclusive, comprehensive review of the
codes of *all* papers; overlap between codes reduced and remaining codes collated and translated
into themes; themes checked against each other and back to the data of the original papers; themes
internally coherent, consistent, and distinctive.

---

#### Step 4 — Create a model of higher-order themes (Section V)

*Purpose.* Explore relationships between themes and build a model, returning to the original
research questions and the theoretical interests underpinning them, and addressing those with
arguments grounded in the emergent themes.

*Input.* ~15–20 themes and the thematic map. *Output.* 5–7 higher-order themes expressed as a
description, a taxonomy, a model, or a theory.

*Definitions the paper supplies for the possible outputs.*

- **Higher-order themes** — recurrent unifying concepts or statements about the subject of inquiry,
  whose purpose is to characterise evidence from individual studies by general insights drawn from
  the whole set of studies.
- **Taxonomy** — a formal system for classifying multifaceted, complex phenomena according to a set
  of common conceptual domains and dimensions, used to increase clarity in defining and comparing
  those phenomena.
- **Model** — empirical model building constructs practical models useful for describing and coping
  with real-world situations; modelling is generating a model as a conceptual representation of
  observed phenomena.
- **Theory** — a statement of relationships between units observed or approximated in the empirical
  world; a system of constructs and variables where constructs relate to each other by propositions
  and variables by hypotheses. Theory matters for understanding potential causal links and
  confounders, for understanding the context in which a phenomenon occurs, and for framing
  subsequent empirical research.

*The four recommended sub-steps for developing higher-order themes:*

1. Review the thematic map from the previous step, taking each branch in turn, describing its
   contents with findings and context information, and creating higher-order themes.
2. Identify connections between the higher-order themes and the underlying evidence and the context
   of that evidence (the arrows in Fig. 5).
3. Explore connections with relevant theory and prior research, to recontextualise, define and
   further refine the higher-order themes.
4. Create a model, taxonomy, thematic map or theory of the higher-order themes and their underlying
   evidence.

*Handling relationships across studies.* Where primary studies reported relationships between
findings and study context, compare and contrast how those relationships were identified and
analysed across studies. Where they did not, use the previously extracted data to look at
relationships between findings and key aspects of the primary studies, comparing and contrasting
across studies. The paper warns this is very time-consuming but **critical to the quality of the
thematic synthesis as a whole**.

*Heterogeneity — three sources of variability to consider when judging the robustness of
higher-order themes and their relationships* (after Popay et al.):

- **Variability in outcomes** — the often long causal chains in SE studies can make the same
  intervention produce inconsistent results across studies.
- **Variability in study designs** — methodological diversity is common in SE reviews. Where the main
  sources of variation are known, heterogeneity can be explored by **subgroup analysis over themes**,
  based e.g. on theories about how the intervention works and for which groups.
- **Variability in study populations, interventions and settings** — the content of complex SE
  interventions varies between settings and populations, and some of that variability is intentional
  because interventions are tailored to context-specific needs.

How far you can consider these depends on whether the primary studies report the relevant
information — and prior research suggests SE studies have a particular problem with inadequate
reporting of exactly this.

*Observed practice.* Most SE review authors describe the themes from the previous step **without
exploring sources of variability at all**. Khurum & Gorschek reported frequencies of primary studies
per data-extraction category, and the number and percentage of studies each datum came from, then
used those characteristics to answer their research questions. Beecham et al. used the research
questions to discuss the most important themes and built a model of SE motivation. Walia & Carver
identified 14 error types, classified them into three higher-order types, and presented the result
as a "requirement error taxonomy", keeping error classes as orthogonal as possible and giving, per
class, a description, a table of the specific errors grouped into it, and an example error with a
fault it would likely cause.

*Checklist items 14–17.* Themes compared across studies, translated into each other and interpreted
into higher-order themes; higher-order themes and inter-theme relationships checked against the
synthesis research questions; clear descriptions of higher-order themes and their relationships; a
model created to show those relationships.

---

#### Step 5 — Assess the trustworthiness of the synthesis (Section VI)

*Purpose.* Assess the trustworthiness of the interpretations that produced the synthesis.

Trustworthiness depends on **both the quality and the quantity of the evidence base**. Including
primary studies of poor methodological quality can degrade it. It also depends on the methods used —
measures taken to minimise bias, and weighting of studies by quality.

The four criteria, imported from Guba and from Graneheim & Lundman, are set out in the next section
of these notes.

*Checklist items 18–21.* Assumptions about, and the specific approach to, the thematic synthesis
clearly explicated; a good fit between what is claimed and what the evidence shows; language and
concepts used in the synthesis are consistent; the research questions are answered on the basis of
the evidence of the thematic synthesis.

### Synthesis method catalogue

This paper's catalogue is narrow — it enumerates the four main *thematic analysis* approaches
(Table 1) and positions thematic synthesis against its neighbours. The broad catalogue of synthesis
methods comes from the tertiary study, appended later in this file.

| Approach (Table 1) | Discipline | Data | Coding | Themes | Trustworthiness |
| --- | --- | --- | --- | --- | --- |
| Braun & Clarke | Psychology | Raw data | Theory- or data-driven | Thematic maps | Transparency |
| Boyatzis | Social science | Raw data | Theory- or data-driven | Constant comparison, scoring, scaling, clustering | Reliability |
| Attride-Stirling | Health improvement | Raw data | Uses a theoretical coding framework | Thematic maps | Not mentioned |
| Thomas & Harden | Social science | **Primary studies** | Line-by-line coding | Axial coding | Transparency, generalizability, quality and sensitivity analysis |

Note the column that matters for secondary research: only Thomas & Harden take *primary studies*
rather than raw data as their unit of analysis — which is what makes theirs a synthesis rather than
an analysis method. Cruzes & Dybå's five steps are built on that column.

Positioning of adjacent methods, as this paper describes them:

| Method | Short definition | When it applies |
| --- | --- | --- |
| Thematic synthesis (Thomas & Harden) | Identifies recurring themes/issues in primary studies, analyses them, draws conclusions; develops analytical themes through a descriptive synthesis to find explanations relevant to the review question. Developed for review questions about need, appropriateness, acceptability and effectiveness of interventions | The default recommendation of this paper for SE reviews; flexible across epistemologies and question types |
| Meta-ethnography (Noblit & Hare) | Identify key concepts from primary studies, compare and translate them into higher-order interpretations. The 'going beyond' the content of primary studies to achieve conceptual innovation is what makes it synthesis | Where conceptual innovation across a comparable set of studies is the goal; used in SE by Dybå & Dingsøyr |
| Grounded theory | Purely inductive coding, line by line or incident by incident, with constant comparison | When forcing a preconceived result must be avoided; shares constant comparison with thematic synthesis |
| Content analysis | Compares and sorts, but aims to quantify content against predetermined categories systematically and reliably; establishes significance largely by frequency of themes | When counting occurrences against a fixed category scheme is the point — explicitly *not* the same as thematic analysis |
| Thematic networks (Attride-Stirling) | Web-like illustrations summarising the main themes constituting a piece of text | As a representation aid within Step 3 |

Boyatzis's two main approaches to thematic analysis are also noted separately: a quantitative
description of the frequency of themes, and the forming of clusters of themes.

### Coding and analysis techniques

Consolidating what this paper prescribes:

- **Coding approaches** — deductive (a priori start list), inductive (grounded), integrated
  (recommended for reviews). See the table under Step 2.
- **Code types for SE** — conceptual, relationship, subject, context characteristic.
- **Constant comparison** — compare each new segment against segments already carrying a code, to
  decide whether they express the same concept; refines code dimensions and reveals new codes.
- **Chunk-level coding, not line-by-line** — the SE-specific departure from Thomas & Harden.
- **Translation** — the step from codes to themes and from themes to higher-order themes is
  described as translating themes *into each other* and comparing across studies, i.e. reciprocal
  translation borrowed from meta-ethnography; the paper says thematic synthesis "invokes reciprocal
  translation and constant comparison".
- **Second-cycle coding for theme formation** — pattern, elaborative, longitudinal, focused, axial,
  theoretical/selective.
- **Tabulation and frequency** — codes carry frequencies (checklist item 7); Khurum & Gorschek's use
  of per-category frequencies and percentages is given as the exemplar; Beecham et al.'s Tables 7–9
  present motivators, de-motivators and moderators each with paper references and a frequency
  (number of studies) column. Frequency counting is however presented as a property of content
  analysis rather than the goal of thematic synthesis, and Beecham et al. themselves warn their
  aggregated frequencies "need to be treated with caution".
- **Visual representation** — thematic maps, thematic networks, tables, tree-maps, mind-maps; models
  and taxonomies as final outputs.
- **Sensitivity analysis** — used both for unresolved extraction disagreements and, in Beecham et
  al., as an explicit validity check across population, location, year and study type.

Vote counting, case survey, qualitative comparative analysis and meta-ethnography as a full method
are not treated in this paper — see the tertiary study section below.

### Trustworthiness / rigour criteria

Four criteria, drawn from the qualitative-research literature (Guba; Graneheim & Lundman):

- **Credibility** — concerns the focus of the research and the confidence that can be placed in how
  well the data and the processes of analysis address the intended focus. Critical decision points:
  the focus of the study, selection of contexts and participants, and the approach to gathering
  primary studies. A second credibility issue is **extracting the right-sized unit of text**: too
  broad (several paragraphs) and segments become unmanageable because they carry several meanings;
  too narrow (a single word or line) and you get fragmentation. **Both extremes risk losing the
  meaning of the text during coding and abstraction.** Credibility also covers how well codes and
  themes cover the data — no relevant data inadvertently or systematically excluded, no irrelevant
  data included — and how similarities within and differences between themes are judged. Two
  remedies: show representative segments of text, and seek agreement among co-researchers, experts
  and participants.
- **Confirmability** — whether other researchers and experts would agree with the way the extracted
  data were coded and sorted. Primary study authors recognising the findings of the synthesis is
  also an aspect of confirmability.
- **Dependability** — the stability of data, the degree to which data change over time, and
  alterations in the researcher's decisions during the synthesis. Remedies: complementary coding
  methods, and establishing an **audit trail** letting an external reviewer examine how data were
  extracted and coded and how interpretations and translations into themes were made.
- **Transferability** — the extent to which findings transfer to other settings or groups. Authors
  can suggest transferability, but it is ultimately the reader's decision. To facilitate it, give a
  clear and distinct description of the selection and characteristics of primary studies including
  context and settings, of data extraction, and of the synthesis process; plus a rich presentation
  of findings with appropriate quotations.

Overarching stance: trustworthiness of interpretations is about **establishing arguments for the most
probable interpretations**. There is no single correct meaning of research findings — only the most
probable meaning from a particular perspective. Trustworthiness therefore increases if findings are
presented so that the reader can look for alternative interpretations.

### Caveats, traps and pitfalls

- **Skipping immersion.** Tempting, and advised against strongly by the thematic-analysis literature.
  Only half the examined SE thematic syntheses stated they did it.
- **Three named coding problems.** Coding at too general a level; identifying what one *wants* to
  see rather than what the text says; coding out of context.
- **Forcing data into a priori categories** simply because a code exists for them — the specific
  hazard of the deductive start-list approach.
- **Segment size errors.** Too broad → unmanageable multi-meaning chunks; too narrow →
  fragmentation. Either way meaning is lost.
- **Interchangeable or redundant codes** from missing operational definitions; unbounded codes
  leading to coding every sentence of the original text.
- **Limited interpretative power.** Thematic analysis has limited interpretative power beyond mere
  description **if it is not used within an existing theoretical framework**.
- **Claiming a method you did not follow.** The paper's own motivating observation is that none of
  the eight SE reviews classified as thematic syntheses referenced a method of synthesis.
- **Stopping at Step 3.** In practice SE authors describe themes and stop, without exploring sources
  of variability, without a model, and without checking themes back against the research questions.
  The step from themes to higher-order themes is where relationships and heterogeneity get handled,
  and it is the step most often skipped.
- **Under-reported context in SE primary studies** hinders extraction (Step 1) and blocks the
  heterogeneity analysis (Step 4). Hossain et al. are quoted conceding that missing contextual
  detail may have introduced inaccuracies in their extraction.
- **No quality appraisal feeding trustworthiness.** None of the thematic syntheses examined used
  quality assessment to evaluate trustworthiness; they discussed extraction/coding bias instead.
- **Aggregated frequencies across heterogeneous time spans and roles.** Beecham et al.'s sensitivity
  analysis showed that grouping different countries, SE areas and roles may have lost detail (roles
  are associated with different motivational needs), and that job titles drifted over 1980–2006, so
  their reported frequencies needed caution.
- **Open methodological debates** the paper flags as unresolved: whether different qualitative
  research methodologies can be combined at all, and whether included studies should be quality
  appraised and if so with what.

### Empirical findings worth citing

- Two-thirds of the SE systematic reviews that synthesised their primary studies performed a
  narrative or thematic analysis (citing the authors' own tertiary study).
- Eight SE systematic reviews were classified as thematic syntheses in that tertiary study; **none of
  them referenced a method of synthesis**.
- Immersion was explicitly stated in **half** of those eight thematic syntheses.
- **Only two** of the thematic syntheses did *not* follow the publication / context / findings
  structure when extracting data.
- Only **14%** of SE systematic reviews performed a quality appraisal of primary studies; **none** of
  the thematic syntheses used a quality assessment to evaluate trustworthiness.
- Beecham et al. derived 9 themes from 21 codes; Staples & Niazi extracted 198 Quote objects and
  agreed 22 categories (two researchers independently derived category lists, agreed a joint list of
  22, then independently classified every quote; initial inter-rater agreement was *not* good and
  differences were resolved in a joint meeting, sometimes with a third researcher arbitrating).
- Beecham et al.'s coded example: text from Frangos was coded as the motivator "Recognition" (for a
  high-quality job done, based on objective criteria); **eleven other papers** had findings on that
  same motivator.
- Walia & Carver identified **14 error types** grouped into **three** higher-order error classes.
- Saldaña describes **at least 30** different coding methods; the paper singles out four as
  particularly useful for SE.
- Expected funnel: 30–40 codes → 15–20 themes → 5–7 higher-order themes.

---

## Ribeiro, Cardoso, da Silva & França 2014 — "Using Qualitative Metasummary to Synthesize Empirical Findings in Literature Reviews" (ESEM'14)

**Role in corpus:** The worked SE example of qualitative metasummary — a *quantitatively oriented*
aggregation of mixed-method findings that sits deliberately between a superficial mapping study and
a full interpretive synthesis, and the source of the two effect-size formulas (frequency and
intensity) that let a review report how often a finding recurs and how much each study contributed.

### What the paper claims as its own contribution

The method itself is Sandelowski & Barroso's (proposed 2007, developed across their 2003–2007 work
and the *Handbook for Synthesizing Qualitative Research*). Ribeiro et al.'s contribution is: an
executed SE example (15 studies on antecedents of software development team performance); an
assessment of the method against ease of use, usefulness and reliability of results; and two
concrete recommendations for adapting it to SE. They are candid that the substantive results are
"somewhat not surprising" and that the contribution is showing how metasummary let the synthesis go
beyond describing a set of research topics.

Framing: full interpretive syntheses such as meta-ethnography demand time, team maturity, experience
with the methodology and a deep grasp of its philosophical stance. Metasummary is offered as the
cheaper bridge.

### The method, step by step

Four steps (paper Section 2), executed in Section 3.

**Step 1 — Extracting findings (§2.1).** Identify what the actual findings of the primary studies
are. Sandelowski & Barroso insist the researcher **first fix a definition of "finding" of interest**,
because that definition governs what material gets extracted and keeps the process consistent. The
definition may need to be revised — expanded or narrowed — during the work, but **every revision
obliges you to return to the reports already extracted under the old definition and re-examine their
findings against the new one.**

- *Worked instance:* their definition was any interpretive claim relating some concept to
  performance of software engineering teams, made in a primary study on the basis of, and supported
  by, data presented in that same paper. The 15 studies were then read thoroughly and the definition
  did not change during the process. **41 findings** were extracted.

**Step 2 — Grouping findings (§2.2).** Assemble groups of findings that appear to address similar
topics — described as working "just as in a regular in-vivo coding process". This gives the
researchers a sense of the variety of topics covered across all the evidence, and surfaces the
relationships between the concepts investigated in the primary studies and the phenomenon of
interest. The grouping must **primarily preserve the meaning and complexity of the findings as given
in the original reports**, in order to optimise the validity of the groups.

- *Worked instance:* findings were grouped by their antecedent variable of interest, yielding groups
  G1 Personality, G2 Tasks, G3 Cohesion, G4 Motivation, G5 Member characteristics, G6 Team
  characteristics, G7 Organization characteristics, G8 Conflict, G9 Group spontaneity.

**Step 3 — Abstracting findings (§2.3).** Once relevant findings are grouped, assign labels
carefully so they are as accessible as possible to readers without prejudicing their original
meanings. Sandelowski & Barroso propose creating files in which all topically similar findings can
be seen together; the researcher then moves back and forth between the edited statements of
topically similar extracted findings and develops **statements of abstracted findings** until the
set concisely but comprehensively captures the content of those findings, preserving the context in
which they appeared. A noted side effect: organising findings this way can surface **new findings
that were apparently not there** but could be expected theoretically or logically.

- *Worked instance:* 14 abstract findings A1–A14 across the nine groups, e.g. G1/A1 "…affects team
  performance" (PS02, PS03, PS04, PS09) and G1/A2 "…has a non-significant impact on team
  performance" (PS04). Note that a single group can carry both supporting and refuting abstract
  findings — G3 Cohesion carries A5 (affects), A6 (non-significant impact) and A7 (does not affect).

**Step 4 — Calculating frequency and intensity effect sizes (§2.4).**

> **Frequency effect size.** Take the number of studies containing a finding — *ignoring reports
> derived from common parent studies that present the same data and findings* — and divide it by the
> total number of studies.
>
> `frequency effect size (of an abstracted finding) = (# studies containing that finding) / (total # studies)`

Rationale given (attributed to Onwuegbuzie): frequency effect sizes are how you assess the relative
magnitude of the abstracted results. The index communicates how recurrent each abstract finding is
within the total universe of articles, leading researchers to identify patterns *and conflicts*
among the primary studies.

> **Intensity effect size.** Take the number of findings in each study and divide it by the total
> number of findings across all studies.
>
> `intensity effect size (of a study) = (# findings in that study) / (total # findings across all studies)`

Rationale given: it ascertains which reports contributed the most to the set of findings; it also
communicates the focus of each study and can help track possible connections between abstract
findings.

**Both formulas are stated unambiguously in the extraction and are corroborated arithmetically by
the paper's Table 3.** Frequency is a per-abstract-finding index with denominator 15 (e.g. A1 =
4/15 — the four studies PS02, PS03, PS04, PS09; A2 = 1/15; A3 = 3/15). Intensity is a per-study
index with denominator 41 (e.g. PS01 = 6/41, PS04 = 7/41, PS12 = 5/41). The 15 intensity numerators
in Table 3 sum exactly to 41, which confirms the reading that the table's inner cells are counts of
findings, that frequency counts *studies* (non-zero cells in a row), and that intensity sums
*findings* down a column.

**Step 5 (implicit) — Interpretation.** The paper adds an interpretation pass (§3.4) reading
patterns and conflicts off the two indexes: which concepts are most investigated, where studies
agree, and where apparently contradictory results actually address different facets of the
phenomenon.

### Synthesis method catalogue

This paper enumerates few methods, but positions metasummary sharply against them:

| Method | Short definition | When it applies |
| --- | --- | --- |
| Qualitative metasummary (Sandelowski & Barroso) | Quantitatively oriented **aggregative** study that finds and exposes patterns of findings from mixed-method research; extract → group → abstract → compute frequency and intensity effect sizes | When you need more than a topic map but cannot afford, or cannot justify, a full interpretive synthesis; when the primary set is mixed qualitative *and* quantitative descriptive findings; as an explicit **intermediary step** between a systematic mapping study and a deeper synthesis |
| Meta-ethnography | Full interpretive synthesis; requires time, team maturity, methodological experience and understanding of its philosophical stance | Better suited to a **small** set of consistently comparable studies — comparable in objectives, conceptual background and contexts. The authors propose selecting that small set *from the output of a metasummary* |
| Qualitative meta-synthesis | Named as the interpretive counterpart the authors intend to evaluate next, to build a comparative index of synthesis methods | Future work in this paper; not executed |
| Systematic mapping study | The "more superficial review" end of the spectrum | The thing metasummary is meant to improve on |

### Coding and analysis techniques

- **In-vivo-style grouping.** The grouping step is explicitly likened to in-vivo coding; groups are
  formed around the antecedent variable of interest rather than around a pre-existing framework.
- **Label editing under a preservation constraint.** Abstraction edits labels "with care to avoid
  bias and to preserve their meaning" — the constraint, not the technique, is what carries the rigour.
- **Tabulation.** Three tables do the analytical work: examples of raw findings mapped to groups
  (Table 1); abstract findings with their supporting references (Table 2); and the study × abstract
  finding matrix carrying frequency in the right margin and intensity along the bottom (Table 3).
  The matrix is the artefact that makes conflicts visible — a group with both an "affects" and a "does
  not affect" abstract finding shows up immediately.
- **Frequency counting as evidence of replication.** The stated logic is that higher-frequency
  findings carry the replication evidence that underwrites validity in quantitative research and the
  claim to have discovered a pattern in qualitative research.
- **Conflict reading, not conflict resolution.** Where PS04 and PS05 appeared to present inconsistent
  evidence, careful examination revealed their conflicting data addressed different facets of the
  phenomenon of interest — the resolution came from re-reading, not from the arithmetic.

### Trustworthiness / rigour criteria

The paper does not import a formal criteria framework; it assesses the method on three axes drawn
from its own experience:

- **Ease of use.** Straightforward and cost-effective. Documentation is adequate, though the authors
  could find no informative example of its use in SE — which is why they wrote one.
- **Usefulness.** Produces results very well connected to the findings of the primary studies. Its
  ability to handle mixed-method studies is itself useful for SE.
- **Reliability of results.** Produces **transparent and auditable** data: although findings are
  abstracted away from their original context, the method keeps track of the whole process. The
  authors add the SE-specific caveat that access to raw data can be a particular challenge in this
  field.

Two rigour recommendations they add for SE use:

1. **Augment the metasummary with primary-study quality assessment data** — common in systematic
   reviews, and absent from metasummary as specified. They state that adding it "could significantly
   improve the meaning of these results".
2. **Report the system of concepts, with explicit definitions for every group of abstract findings**,
   so that incompatible constructs can be treated separately rather than silently merged.

The method also demands **seniority**: its interpretive aspect requires experienced researchers.

### Caveats, traps and pitfalls

- **Simplistic arithmetic.** The authors say directly that computing "frequency" and "effect size"
  with such simple mathematical formulas "also seems too simplistic".
- **The indexes do not measure strength of effect.** Because metasummary does not *integrate*
  findings — the data being of mixed nature limits integratability — "the effect sizes actually do
  not communicate strength of the effects". They uncover literature conflicts and point to research
  opportunities; they do not weigh evidence.
- **The intensity effect size is of questionable value.** This is the paper's headline caution. It
  is not clear how the calculus of intensity adds to the result: when you are aggregating
  mixed-method studies and saying nothing about primary-study quality, it is unreasonable to claim
  one study contributed the most on the basis of its intensity index alone. Their first
  recommendation for SE is to question its utility.
- **Construct conflation during abstraction.** Their own stated main limitation: by abstracting
  findings and grouping them into similar categories, they may have counted distinct constructs as
  apparently similar concepts. The same risk appears as the concept-definition problem — primary
  studies used *team success* and *effectiveness* as near-synonyms for performance, which made
  inclusion decisions hard.
- **Loss of contextual information.** Researchers must be careful during abstraction and label
  editing to avoid losing detailed contextual and important information.
- **Effort at scale.** One of the three stated limitations is the great deal of effort demanded to
  synthesise larger sets of papers.
- **Cannot generate theory alone.** The method "is not able to underpin or generate complete
  theories, so it needs to be composed with other more powerful methods."
- **Self-evaluation bias.** The paper is an experience report and its validity may be limited by the
  fact that the people who applied the method were the same people evaluating it.
- **Two internal inconsistencies in the paper, noted for accuracy.** The abstract claims a
  "10-factor model", while §3.4 and Tables 2–3 describe **nine** groups G1–G9. And §3.4 says
  personality is supported by "four out of five studies" while the following sentence and Table 2
  both reference **four** articles (PS02, PS03, PS04, PS09), with PS04 supplying both the supporting
  A1 and the refuting A2. Similarly §3.4's claim that six concepts were investigated more than once
  yields five (G1, G2, G3, G5, G6) if counted as distinct studies per group; G9's two findings both
  come from PS05. [EXTRACTION UNCLEAR: whether these are typographic errors in the original or an
  artefact of the PDF-to-text conversion — the tables themselves are internally consistent.]

### Empirical findings worth citing

- Input funnel: **281 papers** from the union of three prior systematic reviews by the same group
  (personality of programmers, motivation of software engineers, distributed software development) →
  **15 studies** met the added criterion that performance of SE teams be the unit of analysis.
- **41 findings** extracted from those 15 studies, abstracted into **14 abstract findings** across
  **9 groups**.
- Frequency effect sizes reported (all /15): A1 personality affects performance 4/15; A3 tasks affect
  3/15; A5 cohesion affects 3/15; A9 member characteristics 3/15; A10 team characteristics 3/15; A8
  motivation 2/15; A2, A4, A6, A7, A11, A12, A13, A14 each 1/15.
- Intensity effect sizes reported (all /41): PS01 6/41; PS02 1/41; PS03 1/41; PS04 7/41; PS05 3/41;
  PS06 3/41; PS07 4/41; PS08 1/41; PS09 1/41; PS10 3/41; PS11 3/41; PS12 5/41; PS13 1/41; PS14 1/41;
  PS15 1/41. Sum of numerators = 41.
- Conflicts surfaced by the matrix: cohesion is supported by PS05, PS07, PS10 and disputed by PS06
  and PS11; personality is supported by four studies with PS04 casting doubt specifically on the
  group-heterogeneity effect; group spontaneity carries a positive *and* a negative relationship,
  both from PS05.
- Structural gap identified: SE research has concentrated on team **structure** (G3, G6, G7) and
  **composition** (G1, G2, G4, G5, G9), with team **processes** largely unstudied.
- Only nine distinct concepts have been related to SE team performance at all, and (per the authors)
  only six of them more than once — the evidence base is thin.

---

## Cruzes & Dybå 2011 — "Research synthesis in software engineering: A tertiary study" (IST 53(5):440–455)

**Role in corpus:** The audit. It is the paper that establishes, with numbers, that half of the SE
studies calling themselves systematic reviews performed no synthesis at all — and it supplies the
field's standard catalogue of thirteen synthesis methods and four qualitative appraisal frameworks
to choose from instead.

### What the paper claims as its own contribution

An extension of the authors' earlier conference paper, broadened in Section 2 (fuller account of
research synthesis, emerging synthesis methods, new material on appraisal methods), in Section 4
(number of studies included, topics covered), and in Section 5 (implications, future research). The
catalogues in Tables 2 and 3 are compiled from the wider methodological literature — the authors are
explicit that Table 2 "is by no means meant to be an exhaustive list". What is original is the
classification of 49 SE reviews against those methods, the reappraisal against the full DARE
criteria, and the head-to-head comparison with Dixon-Woods et al.'s healthcare tertiary study.

Their own reflexive classification is worth noting: because they tabulated rather than synthesised,
they call their own study a scoping study that 'maps' the SR literature in SE.

### The method, step by step (how the tertiary study itself was run)

*Research questions.* (1) What is the basis, in terms of primary study types and evidence included,
in SE systematic reviews? (2) How, and according to which methods, are the findings of SE systematic
reviews synthesised? (3) How are the syntheses of the findings presented?

*Search.* ISI Web of Knowledge across SCI-EXPANDED, SSCI, A&HCI, CPCI-S and CPCI-SSH, using
`Title=(systematic review)`, refined to the four computer-science subject areas (Information Systems;
Interdisciplinary Applications; Software Engineering; Theory & Methods), timespan 2005–2010 —
1 January 2005 to 31 July 2010. Start date chosen because earlier papers would not be expected to be
influenced by the seminal EBSE papers or the SR procedures. A **separate ACM Digital Library search**
was run for proceedings papers, because of previously reported inadequacies with the ACM DL and
because ISI does not index ACM proceedings. The articles included in Kitchenham et al.'s two tertiary
reviews were also examined.

*Selection funnel.* 84 articles retrieved → 2 duplicates and 2 conference versions of later journal
articles removed → **80 unique** → 40 excluded (short papers, clearly outside SE such as medical
informatics, or tertiary reviews / lessons-learned reports on conducting SRs) → of the remaining 40,
one could not be retrieved → 10 further SRs added from Kitchenham et al.'s tertiary reviews →
**49 articles** analysed. Inclusion required the secondary study itself to claim to be an SR, either
by saying so in the title or by explicitly referencing Kitchenham & Charters' guidelines.

*Extraction — the eleven items.* Source and full bibliographic reference; main topic area, overall
aim and research questions; how the authors perceived synthesis within the context of an SR;
databases used to search for primary studies; number and time span of primary studies included;
whether the types of primary studies were mentioned and which; whether a separate section on
synthesis method(s) was included and whether a method was explicitly named with a corresponding
reference; quality assessment approach and its use; whether findings were synthesised according to
primary study type or study quality; the types and methods of synthesis used; how the synthesis was
performed and presented.

*Analysis.* Cruzes extracted and categorised, Dybå checked the extraction, disagreements discussed
to agreement. Data analysed both qualitatively and quantitatively; results mostly tabulated.

*The three-perspective classification of synthesis (§4.2) — the analytical move worth reusing.*
The findings are split into (1) the method of synthesis **as described by the authors of the SR**,
(2) the method **as the tertiary reviewers classified it** against the original methodological
literature and the synthesis actually described in the paper, and (3) the **appropriateness** of the
method given the SR's goal. The gap between (1) and (2) is where the paper's most damaging findings
live.

### Conceptual apparatus the paper supplies

**Three definitions of synthesis** (Merriam-Webster), each mapped by Noblit & Hare onto a synthesis
situation:

| Definition of synthesis | Noblit & Hare's corresponding form |
| --- | --- |
| Combination of parts or elements to form a whole | Synthesis of directly comparable studies — **reciprocal translations** |
| Dialectic combination of thesis and antithesis into a higher stage of truth | Studies standing in opposition — **refutational translations** (forms of resolution) |
| Combination of often diverse conceptions into a coherent whole | Studies representing a **line of argument** (forms of reconceptualisation) |

**Integrative vs interpretive synthesis** (Noblit & Hare). *Integrative* synthesis combines or
summarises data to create generalisations; it involves quantification and systematic integration
through techniques such as meta-analysis (assembly and pooling of specific data) or less formal ones
such as a descriptive account. *Interpretive* synthesis subsumes the concepts identified in primary
studies into a higher-order theoretical structure; its primary concern is developing concepts and
theories integrating those concepts, so it avoids specifying concepts before the synthesis and
grounds them in the data reported by the primary studies. Crucially: **every integrative synthesis
includes elements of interpretation, and every interpretive synthesis includes elements of
integration** — the labels describe the dominant mode, not a partition.

**Knowledge support vs decision support.** An SR directed at knowledge support brings together and
synthesises research evidence on a topic; one aimed at decision support is more specific and includes
analytical tasks to help make a decision within a particular context. For knowledge support, avoiding
bias may be prioritised; for decision support, avoiding bias is necessary but not sufficient and the
reviewer must be explicit about the basis of the judgments that inevitably get made. Decision-support
reviews may need to include non-research evidence and modelling or simulation methods, which changes
the SR's methodological focus.

**Systematic review vs traditional review** (Table 1, adapted from Mays et al./Popay):

| Feature | Traditional review | Systematic review |
| --- | --- | --- |
| Question | Often broad in scope | Often a focused research question |
| Identification of research | Not usually specified, potentially biased | Comprehensive sources and explicit search strategy |
| Selection | Not usually specified, potentially biased | Criterion-based selection, uniformly applied |
| Appraisal | Variable | Rigorous critical appraisal |
| Synthesis | Often a qualitative summary | Qualitative and/or quantitative synthesis |
| Inferences | Sometimes evidence-based | Usually evidence-based |

**Scoping study.** Less likely than an SR to address very specific research questions or to assess
the quality of included studies; typically addresses broader topics and is designed to give an initial
indication of the size and location of the literature on a topic as a prelude to a comprehensive
review, or to establish how a term is used in what literature by whom and for what purpose. It draws
on a diverse range of qualitative, quantitative and non-research sources that cannot easily be
appraised or synthesised. **The lack of research synthesis and quality appraisal is precisely what
distinguishes a scoping study from an SR** — and the paper's operational rule follows directly:
without synthesis, a secondary study is "at best, a scoping study".

**Meta-analysis preconditions.** Meta-analysis is additive synthesis combining numerical results of
controlled experiments, estimating descriptive statistics, explaining inconsistencies of effects and
discovering moderators and mediators, with the purpose of aggregating results to predict future
outcomes in analogous conditions. For it to be convincingly performed, **the experiments must
represent results from a single underlying effect rather than a distribution of effects.**

### Synthesis method catalogue

The paper's Table 2 — the reference list of methods for synthesising qualitative and mixed-methods
evidence. Definitions paraphrased; applicability column is partly inferred from the same table and
the surrounding discussion.

| Method | Short definition | When it applies |
| --- | --- | --- |
| **Narrative synthesis** (Popay et al.) | Defined by adopting a narrative rather than statistical summary of primary-study findings. A general framework of selected narrative descriptions and ordering of primary evidence, with commentary and interpretation, combined with specific tools and techniques that increase transparency and trustworthiness | Applicable to reviews of quantitative and/or qualitative research; the general-purpose fallback when statistical pooling is impossible |
| **Meta-ethnography** (Noblit & Hare) | Resembles the qualitative methods of the primary studies. Synthesises by induction, interpretation and translational analysis to understand and transfer ideas, concepts and metaphors across studies. Its product is the translation of studies into one another, then synthesis of those translations to identify concepts going beyond individual accounts to produce a new interpretation. Interpretations and explanations in the primary studies are treated as data | Small, conceptually comparable sets where a genuinely new interpretation is the aim |
| **Grounded theory** (Corbin & Strauss; Charmaz) | A primary research approach — qualitative sampling, data collection and analysis with simultaneous phases, constant comparison, theoretical sampling, and generation of new theory. Applied to synthesis, it treats study reports as a form of data on which analysis generates higher-order themes and interpretations | When new theory is the target and the corpus can bear inductive, incident-level analysis |
| **Cross-case analysis** (Miles & Huberman) | A variety of devices — tabular displays, graphs, meta-matrices for partitioning and clustering data — to manage and present qualitative data without destroying its meaning, through intensive coding. Evidence from each primary study is summarised and coded under broad thematic headings, then summarised within themes across studies with brief citation of primary evidence; commonalities and differences noted | Multi-case evidence where displays and matrices can carry the comparison |
| **Thematic analysis / synthesis** (Braun & Clarke) | Identifying, analysing and reporting patterns (themes) within data; minimally organises and describes the data set in rich detail and frequently interprets aspects of the research topic. Usable within different theoretical frameworks; can be essentialist/realist or constructionist | Broad applicability; **has limited interpretative power beyond mere description if not used within an existing theoretical framework** |
| **Content analysis** (Krippendorff) | Systematic categorising and coding of studies under broad thematic headings using extraction tools designed to aid reproducibility; occurrences of each theme are counted and tabulated, with frequencies determined by precise category specifications and systematic rule application | When reproducible frequency counts against fixed categories are wanted — with the stated risk that counting may fail to reflect the structure or importance of the underlying phenomenon, oversimplify, and count what is easy to classify rather than what matters |
| **Case survey** (Yin & Heald / Lucas) | A formal process for systematically coding relevant data from a large number of case studies for quantitative analysis. A set of structured closed-ended questions extracts data so answers can be aggregated. Qualitative evidence is converted to quantitative form, synthesising both. Each primary study is treated as a case; findings and attributes extracted by closed-form questions for reliability; survey analysis methods applied to the extracted data | Large numbers of case studies; when reliability of extraction matters more than depth |
| **Qualitative comparative analysis (QCA)** (Ragin) | A mixed synthesis method analysing complex causal connections using Boolean logic to explain pathways to a particular outcome, based on a **truth table**. Boolean analysis of necessary and sufficient conditions for outcomes, based on presence/absence of independent variables and outcomes in each primary study | Configurational causal questions — which combinations of conditions produce the outcome |
| **Aggregated synthesis** (Estabrooks et al.) | An interpretive process containing elements of both grounded theory and meta-ethnography. Attempts to preserve the context of the original research while enhancing generalisability by building mid-range theories | When theory development and cumulative knowledge that can both explain and predict behaviour is the goal |
| **Realist synthesis** (Pawson) | A theory-driven approach encompassing quantitative and/or qualitative research from any kind of evidence, focused on explaining how interventions work and why they fail in particular contexts. Data extraction takes the form of interrogating baseline inquiries for information on what works for whom under what circumstances; the theory underlying the intervention is central | When the same intervention cannot be implemented identically and context is the explanation. The paper flags it as "a particularly relevant method for future research synthesis in SE" — aim is explanatory: what works for whom, in what circumstances, in what respects, and how |
| **Qualitative metasummary** (Sandelowski & Barroso) | Quantitatively oriented aggregation of qualitative findings. Goal: discern the frequency of each finding and find, in higher-frequency findings, the evidence of replication foundational to validity in quantitative research and to the claim of having discovered a pattern or theme | See the Ribeiro section above for the executed procedure and formulas |
| **Qualitative metasynthesis** (Sandelowski & Barroso) | Interpretive integration of qualitative findings that are themselves interpretive syntheses of data — conceptual/thematic descriptions or interpretive explanations. Offers novel interpretations derived from considering all studies in a sample as a whole. **Validity does not reside in replication logic but in interpretation** | The interpretive counterpart of metasummary |
| **Meta-study** (Paterson et al.) | Analysis of the theories, methods and findings in qualitative research, plus synthesis of those insights into new ways of thinking about phenomena. Goal is to transform an accumulation of findings into a legitimate body of knowledge, generating new theory and informing practice. Unique in the extent to which it focuses on understanding findings in terms of the methods and theories that drive them | When methodological and theoretical drift across a literature is itself the object of study |

Choice of method is said to depend on the research question, the anticipated number of primary
studies, and the knowledge and expertise of the review team. The paper's stronger recommendation
appears in §5.1: rather than letting epistemological and ontological foundations decide, take a
pragmatic approach and let **the SR's research questions and the primary studies' designs, data
collection methods and data analysis methods drive the choice of synthesis method**.

### Coding and analysis techniques

Techniques as they surface across the paper, and how SE reviews actually used them:

- **Coding / classification analysis.** Nine reviews described their work as "classification
  analysis"; the tertiary authors reclassified six of these as scoping studies, one as thematic
  synthesis and two as narrative synthesis. Classification alone was treated as *not* synthesis.
- **Translation.** Reciprocal translational analysis was claimed by S39 (citing Noblit & Hare) but
  reclassified as narrative synthesis. Only S5 (agile software development) was accepted as a genuine
  meta-ethnography — 1 of 49, versus almost half of healthcare SRs.
- **Tabulation.** Tables are the simplest graphic presentation and appeared in almost all SRs that
  performed a synthesis; they provide structure and sequencing that make logical trends easier to
  follow. But **only 25% of the studies had a table comparing the findings of the primary studies**.
  The paper's demand: go beyond large tables listing large amounts of per-study data, and build a
  *tabular synthesis* that combines key findings accessibly.
- **Vote counting.** Claimed by three reviews (S45, S36, S46); reclassified as narrative synthesis
  (S45, S36) and comparative analysis (S46). S46 used vote counting explicitly because an effect-size
  meta-analysis was not possible in its sample. S36 described a *modified* vote-counting approach and
  used the results to describe how the intervention worked, why, and for whom — which the tertiary
  authors say approaches a realist review. Vote counting is thus documented as a fallback that
  reviewers reach for, not as a method with standing in the catalogue.
- **Narrative synthesis.** The largest genuine category (9 SRs). S1 described the evidence from each
  study chronologically, then discussed differences and possible explanations, organised by the
  categories found for non-functional search-based software testing. S7 combined graphs of empirical
  relationships between regression-test-selection techniques with narrative.
- **Thematic synthesis.** 8 SRs. S12 identified themes from findings in each primary study, presented
  frequencies for the number of times each theme was identified across studies, then synthesised
  findings against the research questions by theme. S29 described requirement errors and their
  characteristics per the research questions, organised them into a taxonomy, then synthesised and
  described each error class with its constituent errors and backing references.
- **Comparative analysis.** 4 SRs. S4 tabulated studies providing evidence for and against a result
  plus aggregation-related issues. S21 tabulated options for cross-company vs within-company
  estimation studies, weighed pros and cons of each, identified which primary studies used each
  option, and produced a summary advice table based on the evidence for and against each item.
- **Meta-analysis.** 2 SRs, from the same group on the same 103 experimental papers. S6 aggregated
  the statistical power of each test relative to Cohen's small/medium/large effect-size definitions
  (post hoc power). S18 performed a meta-analysis using **Hedges' g** as the standardised effect-size
  measure.
- **Case survey.** 1 SR (S14). Each research question was mapped to a data extraction form in the
  shape of a closed-ended questionnaire concerned with the credibility of the evidence and the degree
  to which practitioners could use it to guide technology adoption decisions; the evidence was then
  synthesised considering its strength.
- **Qualitative comparative analysis.** Claimed via Ragin by S4, but **none of the four comparative
  analyses fully applied the method — none used a truth table or Boolean algebra.**
- **Presentation devices beyond tables.** A flowchart was developed during one SR (S30, on software
  changes) giving insight into the architecture change process plus a framework for assessing change
  characteristics and impact. Graphs were used in S7 to show connections among primary-study findings
  and then to *drive* the synthesis. Timelines and hierarchy illustrations also appeared, useful for
  overview and for showing relationships when findings become hard to view in a table. **The hazard
  of these charts is that all findings may appear to carry equal weight visually**; S11 countered this
  by ensuring all studies in the figure were of the same type (experiments).

### Trustworthiness / rigour criteria

**The DARE criteria** (Centre for Reviews and Dissemination, University of York). Reviews are
included in DARE if they meet at least four of five, with criteria 1–3 mandatory:

1. Were inclusion/exclusion criteria reported?
2. Was the search adequate?
3. **Were the included studies synthesized?**
4. Was the validity of the included studies assessed?
5. Are sufficient details about the individual included studies presented?

The paper's central methodological complaint is that Kitchenham et al. used the DARE criteria to
evaluate SE SRs in two tertiary reviews, and Kitchenham & Charters referenced DARE in the SLR
guidelines, but **all of them omitted the mandatory Criterion 3 on synthesis** — which the tertiary
authors argue may explain why so many SE secondary studies claiming to be SRs are actually scoping
studies. They also note that if Criterion 4 is not met, the report must contain enough detail for an
independent assessment, which normally means a full bibliography of the included primary studies.

**Appraisal frameworks for qualitative and mixed-methods evidence** (Table 3):

| Framework | Shape | Areas covered |
| --- | --- | --- |
| **CASP** (Critical Appraisal Skills Programme) | 10 questions in the qualitative tool, dealing broadly with principles/assumptions characterising qualitative research | Rigor, credibility, relevance |
| **Long & Godfrey** | 34 questions across four key areas; relatively lengthy, incorporating both descriptive and evaluative elements | Characteristics of the study (type, sampling, setting); how the study was done (rationale for setting, sample, data collection, analysis); research ethics; policy and practice implications |
| **Spencer et al.** (UK Cabinet Office) | 18 appraisal questions across nine key areas; a guide for assessing credibility, rigor and relevance of individual studies | Findings, design, sample, data collection, analysis, reporting, reflexivity and neutrality, ethics, auditability |
| **Walsh & Downe** | 53 items across eight key areas; a practice-oriented checklist synthesised from a review of existing frameworks | Scope and purpose, design, sampling strategy, analysis, interpretation, reflexivity, ethical dimensions, relevance and transferability |

Framing caveats the paper attaches to appraisal: there is **no general agreed definition of
"quality"**; journal articles and especially conference papers rarely give enough methodological
detail because of space limits; and some authors argue against standard quality criteria
("criteriology") for qualitative studies altogether. Quality appraisals are typically used for one of
three purposes — establishing a minimum threshold for inclusion, discriminating between overall
contributions of studies, or gaining a better understanding of the strength of evidence.

**The synthesis-legitimacy debate**, stated fairly by the paper: proponents see qualitative synthesis
as essential to the evidence-based paradigm; opponents point to epistemological and ontological
commitments underlying qualitative research and argue qualitative research is as resistant to
synthesis as poems are. Estabrooks et al.'s pragmatic middle position — synthesis of multiple studies
can contribute to theory building more powerfully than any single study, allowing larger narratives
and more general theories, overcoming the isolation of individual qualitative studies and enabling
cross-study themes and higher-order analytical categories.

**Overall rigour stance (§5.2):** "a quality SR is one that demonstrates procedural and methodological
rigor in all steps", plus explicit identification of the practical, methodological and theoretical
limitations of the approach undertaken so others can interpret and use the findings appropriately.

### Caveats, traps and pitfalls

This paper is largely a catalogue of the ways synthesis goes wrong. The most important, in order of
how often they bite:

- **Synthesis claimed but not performed.** The headline finding. 24 of the 49 reviews were
  reclassified as scoping studies — 49.0%. Their defining property was that they did not synthesise
  evidence from the area in focus but provided an overview of the subject area. Twenty-two reviews
  were "not explicit about the method" at all.
- **Naming a method without following it.** When authors did attempt to describe their synthesis
  method they were "mostly correct", but many used the wrong terminology for it. Table 10 is a
  crosswalk of claimed method (rows) against actual method (columns), and the diagonal is thin:
  classification analysis → mostly scoping; vote counting → narrative or comparative; reciprocal
  translational analysis → narrative; grounded approach → scoping; content analysis → scoping.
- **Citing a reference that does not define the method.** Only ten of 49 reviews (20.4%) gave any
  reference for their synthesis method, and **four of those references were inadequate**. Two worked
  examples: one review cited, for narrative synthesis, a paper on systematic mapping studies that
  does not discuss narrative synthesis; another claimed a "grounded approach" citing Robson, and
  neither the cited book nor the grounded-theory literature contains the steps described. Only **six**
  original references contained a detailed explanation and definition of the method.
- **Applying half a method.** None of the four comparative analyses fully applied Ragin's QCA — no
  truth tables, no Boolean algebra.
- **Building on non-empirical primary studies.** Contrary to the aims of systematic review research,
  most of the SRs included non-empirical primary studies; some based findings on statements and the
  authors' own experience. The paper's conclusion is blunt: this means current SE SRs "lack the
  necessary basis to synthesize results for knowledge support as well as decision support".
- **Classifying but not using the classification.** 63.3% classified primary studies by type of
  intervention; only 20.4% used that classification as a basis for synthesis. The authors read this
  as reviewers valuing intervention type for description but not attributing the same importance to
  the choice of synthesis method.
- **Appraising quality but not acting on it.** Where quality was assessed it was basically used to
  *characterise* studies — not as a basis for inclusion/exclusion decisions, and not to support the
  synthesis or weight the evidence. Reviews also failed to report whether quality judgments excluded
  papers, and failed to state how appraisal outcomes were taken into account in the synthesis.
- **Presentation without structure.** At the centre of every findings section was a narrative, but
  sometimes it was a compelling narrative of the topic and other times just a brief description of
  tables; in some cases no logical structure was recognisable at all.
- **Equal-weight visual illusion.** Charts and network diagrams make all findings look equally
  weighted.
- **Uncritical inclusion of lessons-learned and experience reports.** These "are unlikely to add much
  value and confidence to the final conclusions of a SR"; the recommendation is to be much more
  restrictive about included primary studies, or at minimum to factor low-quality studies into the
  presentation or discussion.
- **The tension between publication bias and manageability.** Cochrane pushes for including even
  unpublished trials to overcome publication bias; SRs transforming raw data or including large
  numbers of primary studies need greater resources, and where the question or evidence range is very
  broad it may be necessary to sample. Healthcare has debated sampling; **a similar debate was not
  raised in any of the SE reviews examined**, despite SE's much larger median.
- **Chasing average effects.** For SE, evaluating *why* results differ and weighing contrasting
  insights from qualitative and quantitative studies will generally be more helpful than identifying
  average effects. Seemingly unpatterned and disagreeing quantitative findings may have underlying
  consistency once study design, settings, developer types, customer and domain characteristics,
  application details and organisational culture are accounted for.
- **Limitations of the tertiary study itself** (stated): selection bias, since only ISI + ACM DL +
  Kitchenham's tertiary reviews were consulted and "meta-analysis" was deliberately *not* a search
  term — so the count of meta-analytic secondary studies is not comprehensive; inaccuracy in data
  extraction, because several articles lacked sufficient information about included primary studies
  and their synthesis methods; and author bias, since Dybå wrote papers included in the review — in
  those cases Cruzes alone decided on inclusion and judged the extraction, categorisation and
  analysis.

### Empirical findings worth citing

**Corpus.** 49 SRs, 2005–mid-2010. Growth: 2005 = 2 (4.08%), 2006 = 5 (10.20%), 2007 = 7 (14.29%),
2008 = 12 (24.49%), 2009 = 12 (24.49%), 2010 (to July) = 11 (22.45%).

**Venues.** *Information and Software Technology* 22 (44.9%), conferences 12 (24.5%), *IEEE TSE* 5
(10.2%), workshops 4 (8.2%), *EMSE* 2 (4.1%), others 4 (8.2%).

**Topics.** 21 broad research areas. Most-studied: requirements engineering 6/49, software design
5/49, experimental methods in SE 5/49.

**Searching.** Manual searches included in more than 60% of the studies. About 70% of searches used
IEEE Xplore and the ACM DL; ISI, Google Scholar, Inspec, Ei Compendex and ScienceDirect each appeared
in roughly 20–50%. A few studies did not describe their search procedures in detail.

**Scale.** Number of primary studies per review ranged **10 to 304, median 54**; eight articles were
unclear about how many primary studies they examined.

**Basis for the reviews (Table 7).**

| Question | Yes | No |
| --- | --- | --- |
| Classified the types of studies (case studies, experiments, surveys)? | 63.3% | 36.7% |
| Synthesis based on study types? | 20.4% | 79.6% |
| Quality appraisal? | 34.7% | 65.3% |
| Quality appraisal used for the exclusion of papers? | **6.1%** | 93.9% |
| Quality appraisal used for synthesis? | **14.3%** | 83.7% |

(The last row's percentages sum to 98.0 rather than 100 in the published table — reproduced as
printed.)

**Non-empirical content of primary study sets — the worked examples.** In S12, 16 of 20 studies were
lessons-learned reports based on expert opinion. In S20, more than 90% of primary studies were based
on claims and expert opinions with no corresponding empirical data. In S25, **117 of 173** primary
studies were advocacy research, proof of concept, or experience reports. In S13, half the included
studies conducted no empirical evaluation at all.

**DARE reappraisal of the 49 SE reviews (Table 8).**

| DARE criterion | % Yes | % No |
| --- | --- | --- |
| 1. Inclusion/exclusion criteria reported? | 98.0% | 2.0% |
| 2. Search adequate? | 79.6% | 20.4% |
| 3. **Included studies synthesized?** | **51.0%** | **49.0%** |
| 4. Validity of included studies assessed? | 34.7% | 65.3% |
| 5. Sufficient details about individual included studies presented? | 79.6% | 20.4% |
| **Would be included in DARE?** | **36.7%** | **63.3%** |

Criterion 3 — the one Kitchenham et al. omitted — was the main criterion that would have excluded SE
studies from DARE.

**Methods of synthesis as actually classified (Table 10 column totals, n = 49).**

| Actual method | Count | Percentage |
| --- | --- | --- |
| Scoping study (no synthesis) | 24 | **49.0%** |
| Narrative synthesis | 9 | 18.4% |
| Thematic synthesis | 8 | 16.3% |
| Comparative analysis | 4 | 8.2% |
| Meta-analysis | 2 | 4.1% |
| Case survey | 1 | 2.0% |
| Meta-ethnography | 1 | 2.0% |

Of the 25 reviews that did synthesise, narrative plus thematic account for 17 — **roughly two thirds**.

**Method reporting.** Almost half the SRs gave no indication of a synthesis method being followed;
22 reviews were categorised "not explicit about the method". Half the papers contained a synthesis
*section*, but only **ten (20.4%)** included a reference for the method of synthesis, and the authors
did not always follow the method described in the reference they cited. Only **six** original
references contained a detailed explanation and definition of a method (Noblit & Hare's
meta-ethnography; Ragin's QCA; Miles & Huberman; Strauss & Corbin's constant comparison; Cohen's
post hoc power calculations; Kline/Rosenthal & DiMatteo on standardised effect sizes). **Four** of
the located method references were inadequate.

**Goals vs methods (Table 11).** Scoping goals: 23 SRs (46.9%) — of which 16 ended up classified as
scoping studies, 4 as thematic analysis, 3 as narrative synthesis. Decision support: about 10% of
studies — of these only one was classified as a scoping study, because it did not fulfil its stated
goals. Knowledge support: 21 SRs (42.9%) — of which **seven** were classified as scoping studies,
with the remaining fourteen using various synthesis methods.

**Presentation.** Tables appeared in almost all SRs that performed a synthesis, but only **25%** had
a table comparing the findings of the primary studies. One flowchart was developed during a review.

**SE vs healthcare (Table 12; healthcare figures from Dixon-Woods et al.).**

| Criterion | Health and healthcare | Software engineering |
| --- | --- | --- |
| Time span | 1994–2004 | 2005–2010 |
| No. of SRs | 42 | 49 |
| Databases searched specified | 64.3% (27/42) | **95.9% (47/49)** |
| No. of studies synthesised | 3–292, median **15** | 10–304, median **54** |
| Appraisal of candidate studies described | 50% (21/42) | ~35% (17/49) |
| Synthesis | **All** SRs performed some type of synthesis; almost 50% (19/42) used meta-ethnography | Only **50% (24/49)** performed synthesis; narrative (9) and thematic (8) were the two most common methods |

Additional contrasts drawn in §5: SE searches were markedly more explicit than healthcare's and SE
included far more primary studies per review, but SE was less rigorous on quality and analysis;
meta-ethnography carried half of healthcare's syntheses and one of SE's; and some healthcare SRs
reported attempts to innovate or adapt synthesis methods, whereas **no innovation was evident in the
SE SRs**.

**Two headline conclusions to quote by the numbers.** Half of the studies calling themselves
systematic reviews included no synthesis and were scoping studies that merely mapped and categorised
primary studies; and **as many as two-thirds of the studies did not use synthesis methods specific to
the types of evidence included in their primary studies**.
