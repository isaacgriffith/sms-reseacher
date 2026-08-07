# Batch 1 — SLR "lessons learned / experience report" papers

Source extractions: `scratchpad/txt/`. All content below is paraphrase and synthesis in my own
words; short attributed quotations only where exact phrasing matters.

> **File-level note.** `brereton_lessons_2007.txt` and `kitchenham_lessons_2007.txt` are
> **byte-identical** (same MD5 `02de16e2…`). Both are Brereton, Kitchenham, Budgen, Turner &
> Khalil (2007), *JSS* 80(1):571–583. There is only one paper here, not two. Kitchenham is the
> second author, so a citation key of `kitchenham_lessons_2007` in the corpus resolves to the same
> work. Extracted once below.

---

## brereton_2007 (= kitchenham_lessons_2007) — Lessons from applying the systematic literature review process within the software engineering domain

Brereton, Kitchenham, Budgen, Turner & Khalil. *Journal of Systems and Software* 80 (2007) 571–583.

**Type:** Experience report (three SLRs run by the authors), structured as lessons against a
process model.

**Role in corpus:** The canonical source of the **10-stage / 3-phase SLR process model** and of the
numbered lessons **L1–L19**; it is the paper that first documented, from direct experience, that SE
digital libraries and SE abstracts are structurally unfit for systematic searching.

### Process steps or stages defined

The paper presents a 10-stage model grouped into three phases (its Fig. 1, §2). This is the model
the lessons are indexed against.

**Phase 1 — Plan review**
1. Specify research questions.
2. Develop review protocol.
3. Validate review protocol.

**Phase 2 — Conduct review**
4. Identify relevant research.
5. Select primary studies.
6. Assess study quality.
7. Extract required data.
8. Synthesise data.

**Phase 3 — Document review**
9. Write review report.
10. Validate report.

The paper also restates the five-step **evidence-based practice** cycle carried over from Sackett
et al. via Kitchenham et al. 2004 (§1): (1) turn an information need into an answerable question;
(2) find the best evidence; (3) critically appraise it for validity, effect size and applicability;
(4) integrate the appraisal with engineering expertise and stakeholder values/circumstances;
(5) evaluate how well steps 1–4 were executed and look for improvements. The authors note that
**steps 1–3 are what constitutes the systematic review itself** — steps 4–5 are practice, not
review. This is guidance the paper *cites* rather than originates.

**Protocol characteristics stated (§2).** The protocol is written during planning, defines in
advance how the review will be done so as to reduce bias, is itself a reviewable document, is under
version control, records the reason for every post-agreement change, and is intended to double as
the skeleton of the final report. The authors report their own second protocol ran to roughly
twenty pages.

**Inputs/outputs asserted for stage 1.** Research questions drive three downstream things: the
search strings for automated searches, the fields on the data-extraction form, and the constraints
on aggregation. Because of that, the paper states that research questions are the one part of the
protocol that must be frozen once the protocol is accepted (§6.1).

### Caveats, traps and pitfalls

**Stage 1 — research questions.**
- Questions will shift during protocol development as understanding improves; all three of the
  authors' reviews refined theirs. Their meta-review (R3) went from two broad questions to five
  more operational ones. Treat early questions as provisional (L1).
- Scoping is genuinely hard in SE because the empirical base is thin and methodologically diverse
  compared with clinical medicine's heavy use of RCTs (§7). Expect more difficulty framing an
  answerable question than a medical reviewer would.

**Stage 2 — protocol development.**
- *Distributed teams degrade protocol ownership.* In R1 the protocol ended up written by only two
  of the reviewers. Those two understood the protocol and the SLR process far better than the rest;
  the consequence appeared later, when one team member simply did not follow the specified search
  process and others did not understand what the data extraction actually required (L3).
- Piloting R2's protocol exposed four separate defects that would otherwise have corrupted the
  results: (a) the people extracting data were less statistically fluent than the person who
  designed the form, producing misunderstandings about correlation versus regression constants;
  (b) primary studies frequently report several tests from one study, so without a refinement the
  extraction would have double-counted results; (c) primary studies reported results in
  incompatible formats, forcing changes to both extraction and aggregation; (d) studies reported
  only subsets of the wanted fields, so a defined missing-value procedure was needed.
- Piloting R3 revealed that data had to be captured at **two levels** — per primary study *and*
  per domain — because the domain-level data was what allowed a judgement of how similar another
  discipline was to SE.
- Piloting can invalidate the chosen method itself. R3's pilot showed that a pure SLR would not
  work, because the literature sat in domains outside the team's expertise and a comprehensive
  search was therefore not feasible; the team had to widen the methodology to include **interviews
  with domain experts** (L4). This is a strong caveat: the pilot may tell you the study design is
  wrong, not merely that the form is wrong.
- The authors cite Staples & Niazi's open question of **when to stop piloting** and move to
  execution (§7) — they do not resolve it.
- They also cite Reeves et al.'s warning that after the initial definition work it is hard to bring
  new people into a review team, because newcomers struggle to absorb the shared norms and
  meanings already established.

**Stage 3 — protocol validation.**
- In R1 the protocol was reviewed informally by an expert (Kitchenham), but the review team did not
  properly or formally act on the results. Informal review with no formal disposition of comments
  is a trap; validation needs to be a defined process with external reviewers (L6).

**Stages 4/5 — searching and selection. (The paper's hardest-hitting section.)**
- Search engines for two key SE databases are built on **completely different underlying models**,
  so one set of search terms cannot be reused across them. ACM Portal did not support complex
  logical combination; IEEE Xplore did.
- **Boolean semantics are not stable.** In some engines the evaluation of a Boolean string depends
  on the order of terms and ignores bracketing. The authors give two search expressions differing
  only in term order that returned the same *total* result count in IEEE Xplore but a markedly
  different result *ordering* — which matters because that engine sorts by relevance.
- CiteSeer treated a multi-word entry as a single phrase; the phrase search found nothing while the
  same words joined by `and` returned 210 documents, none of which contained the terms together, so
  relevance was very low. Searching the same CiteSeer content through Google returned about forty
  documents. Net effect: the team abandoned a single search string and derived a **different string
  per database** from the protocol's original terms.
- Searching hundreds of conference/workshop papers in a fast-moving area (R1, service-based
  systems) was rejected because no defensible quality criterion existed for choosing which venues
  to include — so the review restricted itself to archival journals. The paper is candid that this
  was **pragmatic, not principled**, and that in retrospect the immaturity of the technology meant
  very few journal papers existed. Identifying relevant research while a technology is still
  developing rapidly is characterised as a problem with **no equivalent in the other domains the
  authors examined**.
- **Abstracts cannot be trusted.** SE and CS abstracts are unstructured; keywords are inconsistent
  between major journals and between ACM and IEEE. When the R2 pilot made include/exclude decisions
  on abstracts alone, it **excluded studies already known to be important**. The protocol had to be
  amended to bring the conclusions section into initial screening (L10).
- In R2, 208 papers were initially flagged as potentially relevant and only 59 survived the
  inclusion/exclusion criteria; the paper calls the false-positive rate "disappointingly high".

**Stage 6 — quality assessment.**
- R1 skipped per-study quality assessment on the rationale that archival-journal publication
  already implied acceptable quality. The authors report this as what they did, and elsewhere note
  it was tied to their inability to define quality criteria for venues — read it as a documented
  compromise rather than a recommendation.
- The trap flagged is **assessing quality without knowing what the score will be used for**; the
  quality rating must have a defined role in later aggregation or sensitivity analysis (L12).

**Stage 7 — data extraction.**
- In R1 the reviewers who had done the pilot produced mostly complete, good data; the others were
  sometimes unsure what to do and sometimes departed from the protocol — and, critically, **never
  asked for clarification**. The authors offer three candidate causes: unclear instructions; a gap
  of several weeks between instructions and the actual extraction; and the fact that the rationale
  and process had been written up as a draft paper rather than as a formal protocol document.
- Extraction is described as time-consuming and skilled; it works well only once reviewers have
  experience of it (§7).

**Stage 8 — synthesis.**
- Meta-analysis broke down immediately in R2: regression coefficients cannot be pooled the way
  correlation coefficients can. Different researchers reported correlations, multiple correlation
  coefficients, or regression coefficients, so the team could not base aggregation on meta-analysis
  alone and fell back on tabular summary (L16).
- With tabulation rather than formal meta-analysis, **it can be unclear whether the review's
  questions have actually been answered**; the reviewers may have to explain explicitly how the
  summarised data addresses each question (L17).

**Stage 9 — reporting.**
- R1's decisions were scattered across many email exchanges plus notes from a single meeting of
  four of the five reviewers. The team could reconstruct the process information, but says a formal
  project log should have been kept (L18).
- SE journals and (worse) SE conferences impose length limits that make full documentation of a
  review hard to fit (L19).

### Clarifications on how a step should be performed

- **Selection is a two-stage process (§6.5).** First, title/abstract screening — preferably by at
  least two researchers — rejecting the clearly irrelevant, and erring towards inclusion: if the
  researchers cannot agree, the paper stays in. Second, obtain full copies of survivors and have
  two or more researchers apply the protocol's inclusion/exclusion criteria; disagreements are
  resolved between them, using an **independent arbitrator** if necessary. The cycle repeats if the
  protocol requires reference-list checking of primary studies.
- **Search string construction (§6.4, R2, following medical practice).** Decompose the research
  question into elements — here technology, study type, and response measure — to get the main
  terms; mine known primary studies' keywords for further main terms; enumerate synonyms; join main
  terms with `AND` and synonyms with `OR`. Additionally fix a start year with a justification (1989
  = first TAM paper), identify any prior systematic review on the topic, and state that reference
  lists of all primary studies will be searched.
- **Search strategies are plural and must be justified (L7).** Different strategies buy different
  completion criteria. R1 deliberately used a restricted, manual, journals-only search because it
  was mapping issues; R2 needed near-complete recall because it was hunting a rarely-used
  evaluation, so restriction was not an option. Choose by question type and say why.
- **No single source suffices (L8).** The authors used IEEExplore, ACM Digital Library, Google
  Scholar, CiteSeer, Keele's electronic library, Inspec, ScienceDirect and EI Compendex.
- **Two extraction protocols compared (§6.7, R2).** (a) Both reviewers extract independently, then
  compare forms and discuss disagreements — the medical-guidelines recommendation. (b) One reviewer
  extracts, the second acts as checker. **The authors found no major difference in effort or time**;
  the extractor/checker split was slightly quicker and so is worth considering when the paper count
  is large (L13). Note this is a mild divergence from strict medical guidance, offered on
  efficiency grounds.
- **Separate the extraction guidance from the protocol (L5).** Data definitions and extraction
  guidelines should be pulled out of the protocol into a short standalone document. R1 found that
  including **definitions of the research methods** likely to appear in the selected papers greatly
  improved coding uniformity.
- **Validation must be distinct from piloting (L6)**, and ideally done by external reviewers. R2
  used two external reviewers completing a questionnaire on the completeness and quality of the
  review items; their comments produced protocol revisions.
- **Missing or ambiguous data (§6.6).** Contact the authors of the primary study and ask. If they
  do not supply it, use the quality rating in a **sensitivity analysis** — i.e. check whether the
  incomplete or ambiguous studies change the overall result.
- **Pre-review mapping study (L2).** Borrowed from the EPPI-Centre. A systematic map describes what
  research activity exists — the distribution of studies, ranges covered, how many evaluate given
  practices. Mapping resembles extraction in that each study is entered on a form, but it is done
  **as fast as possible over a large initial set** and it *describes* studies rather than extracting
  detail. It differs from synthesis in that a map makes no interpretation. Its purposes: give the
  review context, aid interpretation of the later synthesis, narrow the synthesis question and the
  inclusion/exclusion criteria, and cut the number of candidate studies.

### Checklists, reporting guidance, evaluation criteria

**The nineteen lessons (L1–L19), condensed.** Each is my paraphrase; consult §6 of the paper for
the official wording.

| # | Stage | Condensed |
|---|-------|-----------|
| L1 | 1 | Plan on revising your questions during protocol development. |
| L2 | 1 | A mapping study run before the review can help scope the questions. |
| L3 | 2 | Every team member must actively help build the protocol. |
| L4 | 2 | Piloting the protocol is essential; it catches collection and aggregation errors and may show the whole method is wrong for the questions. |
| L5 | 3 | Lift data definitions and extraction guidance out of the protocol into a short separate document. |
| L6 | 3 | Run a validation process distinct from piloting, ideally with external reviewers. |
| L7 | 4 | Several search strategies exist, giving different completion criteria; pick and justify one that fits the question. |
| L8 | 4 | Search many electronic sources — no one source returns all primary studies. |
| L9 | 4 | SE search engines are not built for SLRs, so unlike in medicine, searches must be tailored per resource. |
| L10 | 5 | SE/IT abstracts are too poor to select on; read the conclusions too. |
| L11 | 6 | Medical standards insist on quality assessment, but how much you need depends on the review type. |
| L12 | 6 | Decide up front how the quality assessment will feed aggregation and analysis. |
| L13 | 7 | With many papers, one extractor plus one checker may be preferable. |
| L14 | 7 | Team members must genuinely understand the protocol and the extraction process. |
| L15 | 8 | SE systematic reviews will tend to be qualitative. |
| L16 | 8 | Even with quantitative data, meta-analysis is often impossible because reporting protocols differ so widely. |
| L17 | 8 | Tabulation aggregates usefully but you must explain how the tabulated data answers the questions. |
| L18 | 9 | Keep a detailed record of decisions made across the whole review. |
| L19 | 9 | SE venues need to allow longer papers, or repositories for appendices. |

**Transferability table (Table 1, §7)** — the paper's own verdict on which stages move to SE
unchanged, which need adaptation, and which require SE *practice* to change:

- Stages 1, 2, 3, 7 — **transfer as is**.
- Stage 2 additionally: the authors recommend that *all* SE empirical work, not just reviews, start
  from a study protocol.
- Stage 3 additionally: protocol validation could ride on normal peer review of submitted papers,
  or be a formal expert evaluation.
- Stages 4/5 — **SE practice must change**: digital libraries give poor support, and SE abstracts
  are poor.
- Stage 6 — **adapt to SE**: quality measures must be developed to suit the kinds of empirical
  study a given review includes.
- Stage 8 — **adapt to SE**: aggregation methods must suit the study types included.
- Stages 9/10 — **SE practice must change**: publication mechanisms for longer papers are needed.

**Structured abstracts.** The paper summarises its three reviews under the headings
context / objectives / methods / results / conclusions, attributing these to Khan et al.'s
reporting recommendations, and argues in §7 that SE should consider adopting structured abstracts
as medicine has.

**R3's quality rating for guidelines documents (§6.6)** — an ordinal 0–5 scale for the provenance
of a guideline, running from 0 (written by one person, no formal validation) to 5 (produced by a
multinational group with formal validation by independent reviewers). Driven by questions such as
whether an individual or a group wrote them, and whether the group spanned countries.

**R2's completeness-based quality grades (§6.6):** *questionable* = the study asserts a
relationship but supplies no data or statistical test; *incomplete* = some but not all of the
required information is reported (their example: a paper relating the combined TAM constructs to
actual use without saying whether the relation holds for each construct separately).

### Threats to validity framework

The paper does not propose a threats-to-validity framework of its own. It cites, from Khan et al.
2001, the position that there is **no universal definition of study quality**, but that quality can
be understood as the degree to which bias is minimised and internal and external validity are
maximised (§6.6). Bias reduction is the stated rationale for the protocol (§2) and for defining and
piloting extraction forms before use (§6.7).

### Data extraction and analysis techniques

- Standardised data-recording forms plus guidance notes (R1); a standardised **electronic** form in
  R2.
- Guidance notes should carry definitions of the research methods expected in the corpus, to make
  coding uniform.
- Independent-duplicate extraction versus extractor-plus-checker (see above; effort found
  comparable).
- Defined handling of missing values, and a rule preventing double-counting when one study reports
  multiple tests.
- Qualitative aggregation via **simple tabular formats** — used in R1 and R3 and expected to be the
  SE norm.
- Meta-analysis where possible; the paper points to Egger et al. and Lipsey & Wilson for method,
  and to Lipsey & Wilson for the specific fact that regression coefficients do not aggregate like
  correlation coefficients.
- Sensitivity analysis on quality ratings to test whether incomplete/ambiguous studies drive the
  result.

### Empirical findings worth citing

- **R2 (TAM review) screening yield: 208 potentially relevant papers → 59 retained** after
  inclusion/exclusion.
- **R1 protocol length: about twenty pages.**
- CiteSeer example: the exact-phrase search returned **0** documents; the `and`-joined variant
  returned **210**, none with the terms adjacent; the same database via Google returned **~40**.
- R1 protocol validation used a pilot of the extraction process and forms over **4 papers by 2
  reviewers**.
- R2 protocol validation used **2 external reviewers** completing a questionnaire.
- Search sources enumerated for R2: **8** named services (IEEExplore, ACM DL, Google Scholar,
  CiteSeer, Keele e-library, Inspec, ScienceDirect, EI Compendex).
- R3's identified near-neighbour domains for SE, by empirical practice: **education, criminology,
  and nursing and midwifery**.
- Extraction-approach comparison: **no major difference in effort or time**; checker approach
  "slightly quicker".

---

## bailey_2007 — Search Engine Overlaps: Do they agree or disagree?

Bailey, Zhang, Budgen, Turner & Charters. 2nd Int. Workshop on Realising Evidence-Based Software
Engineering (REBSE'07).

**Type:** Empirical study of the review process itself (a measurement study of search-engine
agreement across three real secondary studies).

**Role in corpus:** The only paper here that **quantifies** the non-overlap between SE digital
libraries. It supplies the hard numbers behind the widely repeated instruction to search multiple
engines, and it identifies missing keyword standardisation as the likely cause.

### Process steps or stages defined

The paper states a **five-stage** systematic review process (§1.2), each stage documented in the
protocol for transparency and replicability. Note this is a coarser grouping than Brereton et al.'s
ten stages, and it folds quality assessment into data extraction:

1. **Searching** — devise a strategy for systematically finding potentially relevant studies;
   involves choosing search engines, keywords and information sources.
2. **Screening** — apply inclusion/exclusion criteria, derived from the review question, to titles,
   abstracts and full texts of the candidates (their example of a criterion: a date cutoff).
3. **Data extraction** — assess quality and extract data from the studies that survived exclusion.
4. **Data analysis / synthesis** — build a framework for analysis and identify key themes.
5. **Reporting and dissemination** — present the findings.

The paper singles out stage 1 as probably the most crucial.

It also defines a **mapping study** as consisting of the first several steps of a review (§1) — two
of its three case studies (OO design, patterns) were mapping studies aiming to assess the scope of
the available primary studies, while the TAM study was a full SLR.

### Caveats, traps and pitfalls

- **Search engines are not built for secondary studies.** The authors' summarising impression is
  that engines are "geared towards a model of an individual purchasing a service rather than mapping
  current literature" (§4.3) — i.e. optimised for a buyer finding one paper, not a reviewer
  enumerating a field.
- **Result-count caps silently truncate your search.** Google Scholar displayed at most 1000
  results per search; ACM returned only 200; IEEE Xplore displayed up to 100; CiteSeer often capped
  at 500 under heavy load. The full result set therefore could not be analysed. (For the OO and
  patterns studies this did not bite, because CiteSeer never exceeded 500 hits.)
- **Per-page display limits** made copying and pasting paper details very time-consuming.
- **Inconsistent user interfaces** made extracting and cleaning search results slow and awkward.
- **Engines go down.** Several were repeatedly unavailable through being busy, or crashed outright.
  The authors call the engines "fragile" and advise planning around outages.
- **Interfaces cannot take one string.** IEEE Xplore accepted the full Boolean string as written;
  Google Scholar and the ACM DL used interfaces built from separate textboxes per string section,
  so the protocol string could not be entered as specified.
- **CiteSeer's Boolean default betrayed the search** (same failure Brereton et al. report): its
  default treated the entry as a whole phrase and returned nothing; the non-Boolean variant returned
  many irrelevant results; searching CiteSeer's database *via the Google interface* returned about
  45. The TAM review consequently searched CiteSeer through Google.
- **Engines change under you.** During the work several engines altered their interfaces and how
  they accept search terms, without any change being published. The authors flag this as a direct
  threat to **replication** of searches.
- **Overlapping index coverage confounds naive overlap metrics.** ACM/Google Scholar agreement was
  inflated because Google Scholar indexes the ACM library. But indexing is not containment: Google
  Scholar also reaches IEEE Xplore, yet five papers found through the Xplore interface were missed
  by Google Scholar.
- **Over-general search terms explode recall without helping.** Patterns search term 6 contained
  "study" and "software", topic-agnostic words, and produced by far the largest recall — especially
  in the multidisciplinary Google Scholar.
- **Root cause of non-overlap: no keyword standardisation.** There is no up-to-date centrally
  maintained keyword repository for SE. Concretely, neither "design patterns" nor "empirical"
  appears in the ACM or IEEE software-engineering taxonomy, so authors invent their own keywords and
  variation is inevitable. A secondary explanation offered: authors do not expect their work to be
  used in a secondary study, so supplying good classification and metadata is not a priority.

### Clarifications on how a step should be performed

The paper's three explicit recommendations (§4.4):

1. **Learn each engine's term-handling before searching it.** Their example: in Google Scholar,
   quotation marks give exact whole-phrase matching.
2. **Write a search plan first** — which terms go to which engines — and, as each is executed,
   record the results *and a timestamp*. This avoids redundant searches and helps catch errors such
   as spelling mistakes. The plan also serves as the schedule to work around outages.
3. **Be patient and opportunistic** given engine fragility: if one engine is down, use the plan to
   redirect effort productively.

Procedure actually used in the TAM study (§2.2, §3.2): two research assistants searched each
database and did an initial screen on titles, keywords and abstracts; survivors went through a more
detailed screen against criteria developed from the research questions.

Term selection in the OO design and patterns studies (§2.1): an initial search was run and its
results examined, and the **best three search terms** were then chosen — i.e. terms were tuned
empirically rather than fixed a priori.

### Checklists, reporting guidance, evaluation criteria

No checklist is proposed. The three recommendations above function as the paper's operational
guidance. The paper's own conclusion is a constraint on protocol design: a researcher **cannot rely
on any one search engine** and must run the search across multiple engines to get significant
coverage.

### Threats to validity framework

No named framework. Threats surfaced implicitly and worth carrying forward as search-stage threats:
result caps truncating recall; silent engine interface changes defeating replication; index
containment inflating apparent agreement; and non-standardised author keywords causing genuine
misses.

### Data extraction and analysis techniques

The overlap measurement itself is a reusable technique (§2.1.2):

- Paste each HTML page of search results into a word processor, which converts it to rich text and
  **preserves the presentational formatting**.
- Use that retained formatting to select and delete unwanted text wholesale (their example: remove
  all green 14-point text), leaving the study titles.
- Clean up residue with regular expressions.
- Normalise titles by stripping whitespace and all non-alphanumeric characters.
- Match with an automated script: two titles match if the normalised strings are equal **or if one
  is a substring of the other**.

The same procedure was used for the TAM study. Results were reported as pairwise overlap matrices
(their Tables 2 and 3), with each cell labelled by search-term number and engine letter (e.g. `1G`
= term 1 in Google Scholar).

### Empirical findings worth citing

Engines used, with the paper's letter codes: ACM Digital Library (A), IEEE Xplore (I), Google
Scholar (G), CiteSeer (C), ScienceDirect (S), Web of Science (W). Six search terms — three for the
OO design study, three for the patterns study — entered into all six engines. ACM, ScienceDirect
and Web of Science required an institutional licence.

**Result counts (Table 1; columns 1–3 = OO design terms, 4–6 = patterns terms):**

| Engine | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| ACM | 28,261 | 32,597 | 8,136 | 122,353 | 34,905 | 126,678 |
| IEEE Xplore | 7 | 21 | 0 | 124 | 84 | 241 |
| Google Scholar | 3,030 | 77,800 | 6,180 | 260,000 | 207,000 | 860,000 |
| CiteSeer | 26 | 35 | 37 | 118 | 184 | 413 |
| ScienceDirect | 4 | 8 | 1 | 31 | 34 | 97 |
| Web of Science | 11 | 26 | 1 | 31 | 81 | 830 |

- Totals returned: **1,613,204** results across the software-patterns study versus **156,181**
  across the OO design study — the patterns terms were far more general.
- Google Scholar consistently returned the most results; ScienceDirect the fewest.
- Result caps observed: Google Scholar **1000** displayed; ACM **200**; IEEE Xplore **100**;
  CiteSeer often **500** under load.

**TAM systematic review (the full SLR).** 71 papers were included in the final review; **4 of the
71 were found only by following references** in already-included papers, not by any database search.
Per-engine contribution to those 71:

| Engine | Included papers found | Found *only* there |
|---|---|---|
| Web of Science | 43 | 12 |
| Google Scholar | 39 | 0 |
| ScienceDirect | 29 | 7 |
| IEEE Xplore | 13 | 5 |
| CiteSeer | 6 | 1 |
| ACM DL | 5 | 0 |

- **14 of the 71** papers were found in Google Scholar, Web of Science and ScienceDirect together —
  35.9% of Google Scholar's included set, 32.6% of Web of Science's, and 48.3% of ScienceDirect's.
- Google Scholar's overlaps with individual engines, among included papers: ACM 2, CiteSeer 2,
  IEEE Xplore 6, ScienceDirect 4, Web of Science 9; plus multi-engine overlaps — ACM+WoS 2,
  CiteSeer+ACM 1, CiteSeer+IEEE 1, CiteSeer+WoS 1, IEEE+WoS 1, ScienceDirect+WoS 14.
- Only Google Scholar and ACM contributed **no** uniquely-found study, consistent with Google
  Scholar indexing ACM.
- Four papers appeared in both Web of Science and ScienceDirect.

**Intra- and inter-engine overlap in the mapping studies.**
- OO design study, highest inter-engine overlap: 7 of the 8 papers returned by `2S` (ScienceDirect,
  term 2) — **87.5%** — were also returned by `2W` (Web of Science, term 2). The only other overlap
  above 50% was `2W` with `2G` at **58%**.
- OO design, *same-engine, different-term* overlap: highest **18%** (`2A` vs `3A`), then **16.8%**
  (`1G` vs `2G`), then **14.5%** (`2G` vs `3G`).
- Patterns study, same-engine overlap was somewhat higher: **27.5%** of `6G` papers also in `4G`;
  **23%** of `6G` also in `5G`.
- In both mapping studies the largest raw shared count was between ACM and Google Scholar,
  attributed partly to their larger recall and partly to Google Scholar indexing ACM.
- Most overlap of any kind occurred between searches on the **same** engine — i.e. different engines
  agreed with each other even less than different terms on one engine did.

---

## staples_2007 — Experiences Using Systematic Review Guidelines

Staples & Niazi. *Evaluation and Assessment in Software Engineering* (EASE 2006 / JSS 2007).

**Type:** Experience report and explicit **critique of Kitchenham's 2004 guidelines**, written
self-consciously "from the perspective of neophytes" — the authors' first SLR (a review of
organisational motivations for adopting CMM-based SPI).

**Role in corpus:** The only paper here that argues for **defining research questions you are
deliberately *not* answering**, and for explicitly fixing the **unit of analysis** — a gap it names
in Kitchenham's guidelines. It is also the sharpest sceptic on whether reviewers can meaningfully
assess other people's study quality at all.

### Process steps or stages defined

The paper restates Kitchenham's three-phase process (§2) and stresses that execution involves
iteration, feedback and refinement rather than a strict sequence.

**Phase 1 — Planning the review.** Output: the review protocol.
1. *Identify the need for a systematic review* — first look for existing systematic reviews of the
   phenomenon, which may make a new one unnecessary or at least seed the protocol.
2. *Develop a review protocol* — a concrete plan whose contents largely prefigure the final report:
   background context, research questions, search strategy, publication-selection criteria,
   treatment of quality assessment, data-extraction plan, data-synthesis plan, and a project plan.
   Pre-definition is what reduces researcher bias.
3. *Protocol review* — the protocol is critical, so it must itself be reviewed.

**Phase 2 — Conducting the review.** Intermediate artefacts named: the initial search record and
archive; the list of selected publications; the quality-assessment records; and the extracted data
per selected publication.
1. *Identification of research* — execute the protocol's formal search over the full population of
   relevant publications; explicit description makes it replicable and externally reviewable; the
   strategy should try to counter **publication bias** by seeking papers reporting negative results;
   search terms and results must be documented and archived.
2. *Selection of primary studies* — multistage: first exclude only the clearly irrelevant, then from
   the shortlist include only publications containing extractable data that addresses the questions.
   The reliability of the selection process must itself be checked.
3. *Study quality assessment* — used both for exclusion criteria and, after selection, in a more
   detailed form to distinguish how well studies were executed. Checklists are built from factors
   that could bias results.
4. *Data extraction and monitoring* — per the protocol's forms and procedures; two or more
   researchers extract, disagreements settled by consensus or extra researchers; "monitoring" covers
   spotting multiple reports of the same study and chasing missing/unpublished data from authors.
5. *Data synthesis* — group and summarise the extracted data against the questions, per the
   protocol; sensitivity analysis is available where some studies are of much higher quality, to see
   what changes if low-quality publications are dropped.

**Phase 3 — Reporting the review.** A single stage. Normally two outputs: a technical report and a
journal/conference paper.

Note the **four bias types** the paper attributes to Kitchenham for checklist construction:
selection bias, performance bias, measurement bias, attrition bias.

**Distinguishing features of an SR versus an ordinary literature survey** (§1, citing Kitchenham):
a protocol documented in advance; a documented search strategy aimed at finding as much relevant
literature as possible; explicit inclusion/exclusion criteria; described quality-assessment
mechanisms; and described review and cross-checking processes involving multiple independent
researchers to control researcher bias. The paper adds that a good SR should be independently
replicable, which is what gives it greater scientific value than a survey — at the cost of much
more effort.

### Caveats, traps and pitfalls

**Effort and calendar time (§4.2).** The authors agree effort should not be underestimated, and add
a point Kitchenham does not make: an SLR consumes far more **calendar time** than effort alone
implies. The cause is the sheer number of **joint review points** — search-term pilot reviews,
protocol reviews, initial-selection reviews, final-selection reviews, data-extraction reviews, and
data-analysis reviews. Each is needed for quality and bias control, but each must be scheduled
across busy independent researchers. The project timetable in Kitchenham's protocol template is
supposed to address this but, they argue, is written far too early — before anyone knows the real
effort per phase.

**Search strategy definition was "unexpectedly difficult" (§3.1.2).**
- The team tried to email search instructions to each other and reproduce each other's results, and
  found each resource had a different search syntax and form interface.
- Worse: some resources returned **different results for the same term** depending on whether the
  Basic or Advanced search form was used.
- Their initial narrow term — logically `("CMM" OR "CMMI") AND ("motivation" OR "reason")` — was too
  restrictive, and they concluded **no search term could restrict results to papers discussing
  organisational motivation**. They broadened to just `"CMM" OR "CMMI"`.
- That broad term then dragged in other fields sharing the acronym — their example is *cutaneous
  malignant melanoma*. For those resources they used `("CMM" OR "CMMI") AND "capability maturity"`.
  **Different resources therefore got different strings, each recorded.**
- They widened sources beyond journal/conference databases to include the SEI website.

**Selection reliability repeatedly failed (§3.2.2).** This is the paper's most valuable failure
narrative.
- To save effort they planned one researcher to select, with a second selecting from a **random
  sample** for an inter-rater reliability check. They tried it: a sample of 14 out of 591 showed
  good agreement — but they were **unsure how many they would have to sample for the agreement to be
  significant**, so they abandoned the shortcut.
- Both researchers then selected independently over all results. **Neither the initial nor the final
  selection reached reliable agreement.**
- They took the *union* of their shortlists (73 publications) and each independently redid the final
  selection. **Again no reliable agreement.**
- Resolution: they discussed the selection criteria, then re-selected independently on the combined
  list of 62, this time **physically highlighting the quotations in each paper that justified its
  inclusion**, then met and worked through each point of difference to agreement. Final result: 46
  publications.
- They also hit an interpretation problem mid-selection: studies about *individual practitioners'*
  motivations for SPI — should they count towards *organisational* motivation, given the
  practitioners are in organisations? Initially resolved by admitting them only into a sensitivity
  analysis.

**Data model and question drift during execution (§3.3, §4.4).** The protocol did not survive
contact:
- Industry-type data was dropped, because industries served could not be reliably determined and
  categorised from the literature.
- Geography and year of adoption were **added** mid-extraction, on the judgement that they were
  cheap and scientifically useful.
- A new entity — the *quote* for a reason — had to be added to the data model so that reasons could
  be categorised and the number of organisations per reason recorded.
- The individual-motivation studies, initially held for sensitivity analysis, were **excluded
  entirely** once extraction showed individual and organisational motivators were different in kind.
- A subtle inclusion trap: papers that listed an organisation's problems and separately noted its
  CMM adoption, **without claiming the adoption was meant to address those problems**, were
  excluded — the review wanted explicitly stated reasons, not the problems of adopting organisations.
- **One of the two research questions was dropped after data extraction** — too few publications
  gave reasons why organisations chose *not* to adopt. The authors note wryly that Kitchenham lists
  gap-identification as a use of SLRs, but they had not set out to use it that way.

**When to stop piloting is unresolved (§4.4).** They agree piloting is very useful but did not know
when to stop, and Kitchenham gave no specific guidance. They suspect their inter-rater reliability
problems mean **they stopped piloting too soon**. This is the same open question Brereton et al.
attribute to them.

**Protocol review can be hollow (§3.1.3).** Their "final" protocol was reviewed by another
researcher who made no significant comments — an experienced empirical SE researcher who **had never
conducted a systematic review**. The implicit caveat: reviewer expertise in the domain is not the
same as expertise in the method.

**Quality assessment may not be feasible as specified (§3.1.2, §5).** They did not believe it was
possible for them — "or perhaps any other individuals" — to judge how well other authors identified
and controlled their own validity threats. See the clarification below for what they did instead.

**Automation prospects are dim (§4.5).** An all-encompassing repository or index supporting every
phase is judged very unlikely, because SE review questions are conceptually complex and expressed in
continually evolving theoretical models; automated selection or extraction would be a "hard AI
problem". They point to a generalised scientific ontology (Hars) as a possible partial step.

### Clarifications on how a step should be performed

- **Define complementary research questions you are *not* investigating (§4.3, §5).** This is the
  paper's headline recommendation. Their actual question was "Why do organizations embark on
  CMM-based SPI initiatives?" and they explicitly wrote down six neighbouring questions as
  out-of-scope: what motivates *individuals* to support adoption; why organisations *should* embark;
  which reasons are *most important*; what *benefits* organisations received; *how* organisations
  decide; and what *problems* they face at the time of deciding. Doing so sharpened both selection
  and extraction.
- **Fix the unit of analysis (§4.3).** An instance of the above: state plainly whether you are
  studying organisations, teams, or individuals. **The authors flag this as absent from Kitchenham's
  SLR guidelines.** They note Kitchenham et al. (2002) raise the experimental unit for empirical SE
  generally, but justify it as protection against inflating sample size by multiple-counting
  organisations that contain several participating individuals. For an SLR, Staples & Niazi say that
  is only a second-order concern; the first-order problem is that organisational and individual
  motivations were **different in character and could not be translated or compared at all**. They
  cite Yin's case-study rationale as the closer analogue.
- **Narrow questions to control effort.** Clear, narrow questions are how you bound the effort and
  duration; the questions determine ease of selection, extraction and analysis.
- **A weaker, defensible form of quality assessment (§3.1.2).** Rather than judging whether authors
  actually controlled their threats, they recorded a simple **YES/NO for each of publication bias,
  internal validity, and external validity, based solely on whether the paper *mentioned*
  methodological issues relating to that threat**. No judgement about effectiveness of treatment.
  They also **deviated from Kitchenham on timing**: the guidelines place quality assessment in a
  separate phase immediately before data extraction, whereas they treated the quality attributes as
  just more fields to extract **at the same time as** the rest of the data.
- **Highlight-then-copy extraction.** Because they had highlighted the justifying quotations during
  selection, raw extraction reduced to copying those quotes into a spreadsheet.
- **Keep extraction trivial; categorise in synthesis (§3.4).** They note Kitchenham's guidelines are
  **not clear about how much categorisation happens during extraction versus synthesis**. Their
  choice: extraction produces a list of quotes, only minimally paraphrased (e.g. splitting
  conjunctive phrases into separate reasons); all categorisation happens in the early part of
  synthesis.
- **Reporting the protocol honestly (§4.4).** They invoke Parnas & Clements' "fake a rational design
  process": despite all the changes, the original protocol still guided execution, kept the work
  closer to plan than it would otherwise have been, and the template raised the quality of a first
  attempt. Their recommendation for the report: show the **final ("fake") protocol**, plus footnotes
  or supplementary commentary describing the nature and reason of every change made to the initial
  protocol — because the changes may themselves reveal researcher bias. They endorse Kitchenham's
  suggestion of a **flow diagram of the study selection** to expose how criteria shifted.
- **Two reports (§3.5).** They agree with Kitchenham that a conference or journal paper will not
  carry the full detail; they issued the full report as an institutional technical report and
  prepared a separate paper covering methodology overview plus results.
- **Search archive format (§3.2.1).** A tabular word-processing document, one section per resource,
  recording the resource name, the exact search string used for it, and per publication an ID, the
  bibliographic details (title; journal, volume, issue, date, pages; authors), an **initial selection
  decision** column and a **final selection decision** column. Electronic copies of the publications
  were kept in a filesystem directory.

### Checklists, reporting guidance, evaluation criteria

No numbered checklist is proposed. The paper's operative lists are:

**Main lessons learned (§5), condensed.**
1. Choose clear and narrow research questions, to bound scope and effort.
2. Define complementary research questions that are explicitly *not* being investigated.
3. Define the unit of analysis clearly.
4. In the full report, show the final protocol but include full notes on changes since the initial
   one.

**Requests for better guidance (§5)** — useful as a list of known gaps in Kitchenham 2004:
- More guidance on piloting protocols during development, especially when to stop.
- A workable account of how valid, reliable quality assessments of others' studies can actually be
  made (they consider this unresolved and used a weaker substitute).
- More, and more accessible, guidance on inter-rater reliability checks: specifically **how many
  items to sample for a partial check to be significant**, and **how to avoid repeatedly failing
  checks**.

**Community-level recommendations (§5).**
- Publish **replications** of existing systematic reviews: successful ones strengthen the original's
  claims and build confidence in the method; unsuccessful ones expose misunderstandings or drive
  methodological improvement.
- Create and maintain a **central index of SE systematic reviews**, analogous to the Cochrane
  Collaboration, both to help researchers find relevant reviews and to act as a focal point for
  methodological and automation improvement.

### Threats to validity framework

The paper does not propose one. It uses three threat headings as *extraction fields* — publication
bias, internal validity, external validity — recording only whether the primary study discussed
them. Separately it relays Kitchenham's four bias categories for quality checklists (selection,
performance, measurement, attrition). Its own methodological anxiety is concentrated on **researcher
bias** in selection and categorisation, which is why every stage was double-performed and
cross-checked.

### Data extraction and analysis techniques

- **An explicit data model for the review** (their Figures 1 and 3). A *publication* carries
  publication-detail attributes and contains one or more *studies* — a single paper might report
  both a survey and a case study. Where a publication contained multiple case studies they treated
  each as a separate study, while acknowledging that multiple case study is a methodology in its own
  right (Yin). Each study carries the attributes filled in during extraction. The final model added
  a *quote* entity so each reason could be categorised and associated with a count of organisations.
- Reasons for adoption were recorded as **quoted text** from the publications, not as the extractor's
  paraphrase.
- **Emergent, bottom-up categorisation** in synthesis: start with **no pre-defined categories** and
  aggregate reasons into categories incrementally. Two researchers did this independently; **each
  invented a different category list**, and a common list was then agreed. The classification of
  quotes into the agreed categories was then repeated independently and checked with an inter-rater
  reliability check — which **did not show good agreement**; differences were settled by discussion
  between the two, with a **third researcher arbitrating** in some cases.
- Final results came from a **frequency analysis** of the categories plus a statistical analysis of
  their relationship to organisation attributes.
- **Tooling actually used (§4.5):** tabular word-processing documents for the search-result lists;
  filesystem directories for the PDFs; spreadsheets for extracted data and for computing inter-rater
  scores; relational database tables and statistical packages for the analysis. They judged this
  "adequate". Targeted automation they would have valued: a tool unifying disparate resources behind
  one search syntax; file/data management built for review replication and re-analysis; and
  **collaborative tools that detect inter-rater problems early**, which would both catch systematic
  errors sooner and let joint reviews run asynchronously, shortening the calendar duration.

### Empirical findings worth citing

- Searches identified **591 publications**.
- Inter-rater trial on a random sample of **14 of 591** indicated good agreement — abandoned because
  the required sample size for significance was unknown.
- Union of the two independently-produced shortlists: **73 publications**.
- Combined list at the third pass: **62 publications**.
- Final included set: **46 publications**.
- Reliable agreement was **not** achieved at the initial selection, the final selection, or the
  repeat final selection on the 73; it was reached only after criteria discussion plus
  quote-highlighting plus a joint difference-by-difference meeting.
- The inter-rater check on category classification during synthesis also **failed** to show good
  agreement.
- One of the two research questions was dropped entirely for lack of evidence.

---

## dyba_2007 — Applying Systematic Reviews to Diverse Study Types: An Experience Report

Dybå, Dingsøyr & Hanssen. First Int. Symposium on Empirical Software Engineering and Measurement
(ESEM 2007).

**Type:** Experience report, methodological in emphasis — how to run an SLR when the primary studies
are qualitative, quantitative and mixed-method.

**Role in corpus:** The paper that supplies (a) the **11-item quality-assessment checklist** for
mixed study types, organised under rigour / credibility / relevance, widely reused in SE SLRs; and
(b) the SE adoption of **meta-ethnography** as a synthesis method where meta-analysis is impossible.
It is explicit that Kitchenham's guidelines, being largely grounded in meta-analytic technique, had
to be **supplemented** for quality assessment and synthesis.

### Process steps or stages defined

The paper follows Kitchenham's stages verbatim (its Table 2):

1. **Planning the review** — (a) identification of the need for a review; (b) development of a
   review protocol.
2. **Conducting the review** — (a) identification of research; (b) selection of primary studies;
   (c) study quality assessment; (d) data extraction; (e) data synthesis.
3. **Reporting the review.**

It also restates the five EBSE steps (§1): convert an information need into an answerable question;
search for the best evidence; critically appraise it for validity, impact and applicability;
integrate the appraised evidence with practical experience and the customer's values and
circumstances; evaluate performance and seek improvement — noting again that the **first three
constitute the SR itself**.

**Its own four-stage selection pipeline (its Figure 1)** — a concrete refinement of "selection of
primary studies":
- Stage 1: identify relevant studies by searching databases and conference proceedings.
- Stage 2: exclude on the basis of **titles**.
- Stage 3: exclude on the basis of **abstracts**.
- Stage 4: obtain the primary papers and critically appraise them.

**Integrative versus interpretive reviews (§2, after Noblit & Hare).** A distinction the paper
imports and leans on. *Integrative* reviews combine or summarise data to create generalisations —
meta-analysis and pooling of well-specified data, or less formal descriptive accounts. *Interpretive*
reviews synthesise by subsuming the primary studies' concepts into a higher-order theoretical
structure; the concern is developing concepts and theories, and an interpretive synthesis
deliberately **avoids specifying concepts in advance**, grounding them instead in the primary
studies' data. Noblit & Hare associate integrative with quantitative and interpretive with
qualitative — but the paper stresses that **every integrative synthesis contains interpretation and
every interpretive one contains aggregation**, especially when diverse study types are combined.

**Traditional review versus SR (their Table 1, adapted from Mulrow & Cook)** — six dimensions:
*question* (often broad vs. often focused); *identification of research* (unspecified and potentially
biased vs. comprehensive sources and explicit strategy); *selection* (unspecified and potentially
biased vs. criterion-based and uniformly applied); *appraisal* (variable vs. rigorous critical
appraisal); *synthesis* (often a qualitative summary vs. qualitative and/or quantitative synthesis);
*inferences* (sometimes evidence-based vs. usually evidence-based).

### Caveats, traps and pitfalls

**Terminological trap (§2).** "Systematic review", "systematic literature review" and "research
synthesis" are used interchangeably, but **a systematic review and a meta-analysis are not the same
thing**. Meta-analysis is one specific statistical technique for combining quantitative data — one
tool among several that may be used in preparing an SR.

**Both narrative reviews and SRs are retrospective observational studies** and are therefore subject
to systematic and random error. What distinguishes an SR is the extent to which scientific methods
were used to minimise error and bias — including **bias arising from the review process itself**, not
just from the primary studies.

**Keywords are not standardised, and are discipline- and language-specific (§4.2).** Reviewers must
be conscious of terminology differences when defining search terms.

**Comprehensiveness trades against precision (§4.2).** Increasing comprehensiveness necessarily
lowers precision and pulls in more irrelevant articles. The stated goal is not to retrieve
everything, but "to retrieve everything of relevance to the research questions, while leaving behind
the irrelevant".

**Database interfaces (§4.2) — with a pointed finding.**
- The strategy had to be implemented separately for each database because of lack of standardisation.
- The authors found it **conspicuous that the least flexible search interfaces were the SE-specific
  databases**.
- Several trial searches were needed per database simply to learn how each handled Boolean
  expressions, and the trial results "were not always self-evident".
- The **ACM Digital Library could not be restricted to titles/abstracts/keywords**, so the whole
  full text had to be searched there, returning a large proportion of irrelevant studies.
- The ACM DL also offered **no facility for downloading citations with abstracts** into bibliographic
  management software, so ACM citations had to be handled manually and separately from all others.

**Wasted database effort, quantified (§4.2).** After the fact they found that **no publisher-specific
database other than IEEE Xplore and the ACM DL returned any unique hits** — everything from Kluwer
Online, ScienceDirect, SpringerLink and Wiley InterScience Journal Finder was also returned by ISI
Web of Science or Compendex.

**Homonym hits from short search terms (§4.4).** "xp AND software" returned articles about Microsoft
Windows XP; "agile AND software" returned agile *manufacturing* papers.

**Titles mislead (§4.4).** "Clever" or witty titles can obscure an article's actual content, so
title-stage exclusion must be conservative — anything ambiguous passes to the next stage.

**Abstracts are of variable quality (§4.4).** Some were missing, poor, or actively misleading, and
several gave little indication of the article's content. In particular it was often **not obvious
from the abstract whether a study was empirical at all**. Their response was to include, at the
abstract stage, every study that indicated *some* form of experience with agile development.

**PDF text layers are not trustworthy (§4.6).** A concrete and generalisable trap: the text layer of
a PDF may not correspond to the layout layer. From one publisher, the "fi" ligature at the start of
a word was consistently stored as a dot, so "Figure" was stored as ".gure" — meaning **free-text
searches for such words silently return nothing**. The team had to copy all textual data from every
PDF into a text editor, check it against the layout layer, and correct it.

**Extraction diverged between reviewers when papers were thin (§4.6).** Piloting showed many
articles lacked sufficient detail on design and findings, and consequently **the three authors
differed too much in what they extracted**. Their fix was drastic — see clarifications.

**Poor primary-study reporting undermines both appraisal and synthesis (§4.5, §4.6, §4.7).** They
repeatedly found methods poorly described, bias/validity/reliability not addressed, and data
collection and analysis methods, samples and settings poorly explained. Consequences: (a) there is a
real danger that **what is assessed is the quality of *reporting* rather than the quality of the
research** (they attribute this concern to Hawker et al.); (b) missing detail can drive
inclusion/exclusion decisions and end in rejecting an article; (c) it made the synthesis hard —
they "often struggled to understand the findings". They note the same problem was reported by
Brereton et al. and by Staples & Niazi in SE, and by Hawker et al. outside it.

**Synthesis was hampered by conceptual scatter (§4.7).** The primary studies seldom studied the same
basic concepts, leaving very few studies within any one topic area, which made it hard to identify
second- and higher-order interpretations from the primary studies' key concepts.

**A stereotype that did not hold (§4.7).** Contrary to expectation, breadth was not the preserve of
quantitative studies nor depth of qualitative ones. Breadth came from both small-scale qualitative
studies of particular projects and large-scale quantitative studies across organisations; and
**greater depth was not always provided by qualitative studies** — some merely described the range
of developers' views without analysing them further.

**The tension in quality thresholds (§3).** There is a genuine trade-off between the statistical
benefit of including many primary studies and the quality benefit of reviewing fewer studies under
more selective criteria. Some quality assessment is nonetheless necessary, to limit bias, expose
possible comparisons, and guide interpretation.

**Open debate the paper does not resolve (§3).** Whether concepts of quality for qualitative research
should be the same as, parallel to, or wholly different from those for quantitative research; and
how far quality assessment of qualitative inquiry can be formalised at all.

**Reviewing an immature field (§4.3).** Piloting immediately raised whether it was worth reviewing a
field with few empirical studies. Their answer: an SR that documents the **absence** of data and
shows that current understanding rests on limited empirical underpinnings is itself a contribution,
and is an excellent way of identifying gaps and directing future research.

### Clarifications on how a step should be performed

- **Plan iteratively (§4.1).** The planning stage should be an iterative process of definition,
  clarification and refinement. They found piloting parts of the process during planning "extremely
  useful", specifically the **search strategy and the citation management procedures**.
- **Question formulation is the most important planning activity (§4.1),** because everything else
  depends on it. The questions determined not just content and structure but the strategies for
  locating, selecting, appraising and analysing. Note the paper's claim that the protocol plus the
  questions are what distinguish an SR from a traditional review — **"not necessarily the number of
  included studies"**.
- **Protocol basis (§4.1).** Built from the Campbell Collaboration's guidelines/procedures/policies,
  the Cochrane Reviewers' Handbook, and CRD Report 4 (Khan et al.), plus consultation with SE
  specialists on both topic and method. It specified research questions, search strategy, inclusion,
  exclusion and quality criteria, data extraction, and synthesis methods. It was informally reviewed
  by Kitchenham.
- **Hand-search as well as database-search (§4.2).** The strategy included hand searches of specific
  conference proceedings, since relevant studies may not be fully indexed. They hand-searched all
  volumes of XP, XP/Agile Universe, and the Agile Development Conference.
- **Search-string design (§4.2).** Nine basic strings derived from the questions and refined by pilot
  searches — `agile AND software`; `extreme programming`; `xp AND software`; `scrum AND software`;
  `crystal AND software AND (clear OR orange OR red OR blue)`; `dsdm AND software`; `fdd AND
  software`; `feature AND driven AND development AND software`; `lean AND software AND development`
  — all joined by `OR`, so a single match sufficed. Applied to titles, abstracts and keywords
  (except in ACM, see above).
- **Publication-type exclusions applied at search time (§4.2):** editorials, prefaces, article
  summaries, interviews, news, reviews, correspondence, discussions, comments, readers' letters, and
  summaries of tutorials, workshops, panels and poster sessions.
- **Inclusion/exclusion rules actually used (§4.3).** Included: any study presenting empirical data
  on agile development that passed the minimum quality threshold; students *and* professionals; any
  research method, intervention type or outcome measure; qualitative, quantitative and mixed-method;
  published 2005 and earlier; English only. Excluded: not (mainly) about agile development; no
  empirical data; **focused on a single technique or practice** such as pair programming, unit
  testing or refactoring — because the questions concerned agile development as a whole; and
  "lessons learned" or pure expert-opinion papers.
- **Two independent reviewers, with kappa (§4.4).** At the abstract stage the abstracts were divided
  so that **each abstract was reviewed by two of the three authors independently**. They recorded
  observed agreement *and* computed Cohen's Kappa, which corrects for chance agreement. All
  disagreements were resolved in consultation with **all three** authors before moving on.
- **Ambiguity resolves upward.** If title, abstract and keywords left it unclear whether a study met
  the screening criteria, it was **passed to detailed quality assessment** rather than excluded.
- **Quality assessment by two independent authors**, dichotomous yes/no per criterion, and —
  importantly — **no overall grade was awarded**. Each reviewer instead used the **whole yes/no
  pattern** of a study as the basis for an include/exclude recommendation.
- **Consensus extraction (§4.6).** Because piloting revealed too much divergence, they abandoned
  independent extraction: **all data from all primary studies were extracted by all three authors in
  consensus meetings.**
- **Verbatim capture.** Aims, settings, research-method descriptions, findings and conclusions were
  copied **verbatim, as reported by the primary authors**, into NVivo.
- **Citation management (§4.4).** All citations except ACM's went into EndNote, then into Excel,
  recording per citation: its source, the retrieval decision, the retrieval status, and the
  eligibility decision. **A separate EndNote database and Excel sheet was created for each stage** of
  the selection pipeline. Duplicates were identified and removed jointly by two authors at stage 1;
  at stage 2 two authors sat together and went through all titles.
- **Choosing a synthesis method (§3).** Dixon-Woods et al.'s survey is cited as the menu, running
  from largely qualitative/interpretive to largely quantitative/integrative: narrative summary,
  thematic analysis, grounded theory, meta-ethnography, meta-study, realist synthesis, Miles &
  Huberman's data-analysis techniques, content analysis, case survey, qualitative comparative
  analysis, and Bayesian meta-analysis. These differ in strengths, in their ability to handle
  qualitative versus quantitative evidence, and in the question types they suit. The authors chose
  **meta-ethnography** because it is the most well-developed method for synthesising qualitative
  data, one of the few with an active funded methodological research programme, and because it
  originates in the same interpretive paradigm as most primary qualitative methods.
- **Final recommendation (§5).** Use the structured stage model; search multiple databases likely to
  hold SE interventions *plus* targeted journals and conference proceedings; and **thoughtfully
  assess the heterogeneity of study designs and interventions to decide whether a qualitative,
  quantitative or mixed-methods synthesis is appropriate**. Also: encourage decision-makers to
  combine review evidence with their own experience and problem-solving skills rather than relying
  on the SR alone.

### Checklists, reporting guidance, evaluation criteria

**The 11 quality criteria (§4.5, their Table 3), condensed.** Graded yes/no; grouped under three
quality issues — *rigour* (has a thorough, appropriate approach been applied to the key research
methods?), *credibility* (are the findings well presented and meaningful?), and *relevance* (how
useful are the findings to industry and the research community?). The criteria were based on the
Critical Appraisal Skills Programme (CASP) instruments, particularly those for qualitative research,
plus Kitchenham et al.'s principles of good practice for empirical SE research.

*Screening criteria — reporting of rationale, aims and context (1–3):*
1. Is it research, or merely a "lessons learned" report based on expert opinion?
2. Are the aims of the research clearly stated, including a rationale for why the study was done?
3. Is the context in which the research was carried out adequately described?

*Rigour criteria — validity of data-collection tools and analysis, hence trustworthiness (4–8):*
4. Was the research design appropriate to the aims?
5. Was the recruitment/sampling strategy appropriate to the aims — is the sample and how it was
   identified and recruited adequately described?
6. Was there a control group to compare treatments against?
7. Was data collected in a way that addressed the research issue — were appropriate collection
   methods used and described?
8. Was the data analysis sufficiently rigorous — are the analysis methods described, and were
   appropriate methods used to ensure the analysis was grounded in the data?

*Credibility criteria — are the findings valid and meaningful (9–10):*
9. Has the relationship between researcher and participants been adequately considered?
10. Is there a clear statement of findings, with credible results and justified conclusions?

*Relevance criterion (11):*
11. Is the study of value for research or practice?

Note that single-technique / single-practice papers were identified and excluded as part of this
screening step.

**Report contents (§4.8).** The paper's own report format, useful as a template — textual summaries
plus tables comprising: a summary of previous literature reviews; tables précis-ing every included
article; a table showing how studies were graded for methodological rigour; a descriptive evaluation
of the assessed literature against each research question; a table mapping primary-study concepts to
higher-order interpretations and themes; and tables summarising findings across themes. The authors
also observe that the SR has two audiences with different interests — practitioners want practical
implications, researchers want methodological detail and future questions.

### Threats to validity framework

No new framework is proposed. The operative quality dimensions are the paper's own triad — **rigour,
credibility, relevance** — which functions as the appraisal framework for mixed study types. Beyond
that the paper works with: bias in primary studies versus bias arising from the review process
itself; publication bias implicitly, via its comprehensive-search argument; and the caution that a
quality assessment may be measuring reporting quality rather than research quality. It flags
**inter-rater reliability in abstracting qualitative data** — both within a study type and across
study types — as an unresolved technical challenge.

### Data extraction and analysis techniques

- **Pre-defined extraction form** recording full article details and specifically how each article
  addressed each research question.
- **NVivo** (QSR) used as the extraction and qualitative-analysis store; verbatim text only.
- **EndNote + Excel** for citation management, one pair per selection stage.
- **Cohen's Kappa** for chance-corrected agreement, interpreted against Landis & Koch's bands.
- **Meta-ethnography (Noblit & Hare), seven phases:** (1) getting started; (2) deciding what is
  relevant to the initial interest; (3) reading the studies; (4) determining how the studies are
  related; (5) translating the studies into one another; (6) synthesising translations; (7)
  expressing the synthesis.
- **The three possible relations between studies** in a meta-ethnographic synthesis: directly
  comparable (*reciprocal* translations); standing in opposition (*refutational* translations); or
  together forming a *line of argument*. Translation may be literal (word for word) or idiomatic
  (meaning preserved). Interpretations and explanations in the primary studies are **treated as
  data** and translated across studies.
- **Their concrete procedure (§4.7):** identify the main concepts of each primary study **using the
  original authors' own terms**; organise the key concepts in tabular form to allow cross-study
  comparison and reciprocal translation into higher-order interpretations — a process they describe
  as analogous to the **constant comparison** method of qualitative data analysis; where findings
  differed, examine whether the differences are explained by differences in method or in study
  setting.
- What the synthesis delivered: a set of higher-order interpretations (themes) recurring across
  studies; documentation that the intervention had both positive and negative dimensions; and
  identification of gaps in the evidence.
- **Future-work needs they name:** specialised software support for qualitative synthesis, and
  better ways of integrating qualitative synthesis with meta-analysis.

### Empirical findings worth citing

- Search yield: **2,946 hits**, comprising **1,996 unduplicated citations**.
- Databases searched (**8**): ACM Digital Library, Compendex, IEEE Xplore, ISI Web of Science,
  Kluwer Online, ScienceDirect (Elsevier), SpringerLink, Wiley InterScience Journal Finder.
- Conference proceedings hand-searched (**3**, all volumes): XP, XP/Agile Universe, Agile
  Development Conference.
- **Only IEEE Xplore and the ACM DL contributed unique hits** among the publisher-specific
  databases; Kluwer, ScienceDirect, SpringerLink and Wiley added nothing beyond ISI Web of Science
  and Compendex.
- **Nine** search strings; **11** quality criteria; **4** selection stages.
- Quality-based inclusion/exclusion agreement — the headline number: **94% observed agreement**, with
  **Cohen's Kappa = 0.80**, which Landis & Koch classify as "almost perfect agreement". The authors
  note this was **higher than they expected**; they had assumed quality-based decisions would be the
  hardest to agree on.
- Publication cut-off: studies published **2005 and earlier**; English only.

---

## badampudi_2015 — Experiences from using snowballing and database searches in systematic literature studies

Badampudi, Wohlin & Petersen. EASE '15, Nanjing.

**Type:** Empirical study of the review process — a head-to-head comparison of snowballing (SB)
versus database (DB) search, run inside a real systematic mapping study on choosing among software
development options (in-house / outsource / COTS / open source).

**Role in corpus:** The only paper here that **measures snowballing against database search on the
same questions, criteria and time period**, with independent researchers on each arm. It supplies
the efficiency and reliability numbers, and — its most transferable finding — a diagnosis of exactly
*how* a weak start set causes snowballing to miss whole subtopics.

### Process steps or stages defined

**Definitions.** Backward snowballing (BSB) = review the **reference lists** of relevant papers to
find new ones. Forward snowballing (FSB) = review the **citations of** relevant papers. Database
search = apply predefined search strings to databases.

**The snowballing procedure used (§3.1):**
1. **Create a start set.** Nine search strings (Table 1) were run in **Google Scholar**, chosen as
   the index database because it is not restricted to specific publishers. The **first 10 results of
   each string** were reviewed against the inclusion/exclusion criteria — 90 results in total.
2. **Screen in two phases.**
   - *Phase 1:* tentative inclusion on title, abstract and introduction; occasionally more sections;
     **no extensive full-text review**.
   - *Phase 2:* include/exclude on **full-text reading**.
   Both phases were done independently by the first two authors, with a **review meeting at the end
   of each phase** to analyse the review process.
3. **Iterate BSB and FSB.** Review the reference lists (BSB) and the citations (FSB, retrieved from
   Google Scholar) of the papers in the current set; add included papers to the set; snowball the
   newly added papers in the next iteration; stop when an iteration yields no new papers. The set at
   that point is the final set of primary studies.

**The Phase-1 screening order differs between BSB and FSB** — a deliberate refinement:
- BSB: (1) title of the referenced paper; (2) **the reference context** — the text surrounding the
  citation in the citing paper; (3) abstract of the referenced paper.
- FSB: (1) title of the citing paper; (2) abstract of the citing paper; (3) the reference context.

The rationale for BSB's order is to squeeze all available information out of the paper in hand
before going to a new paper. Steps 2 and 3 are reversed in FSB because when looking at papers that
cite a study, it is easier to read title and abstract first.

**The DB search arm (§3.2).** Search terms decomposed by **PICO** (population, intervention,
comparison, outcome), then applied to **Scopus** and **Inspec/Compendex**. Same inclusion/exclusion
criteria. Included papers were then reviewed by the first author for relevance, with disagreements
discussed to resolution.

**Study design (§3).** SB and DB were conducted **by independent authors during the same time
period** — SB by Badampudi and Wohlin, DB by Petersen — using identical research questions and
identical inclusion/exclusion criteria specifically so the two arms would be comparable and so that
differences could not be attributed to differing judgement about the criteria. The paper notes the
single-researcher DB arm as a controlled risk on the grounds of that researcher's experience.

### Caveats, traps and pitfalls

**The start set governs everything.** The paper's central caveat. The papers found by snowballing
depend entirely on the start set. Their start set left three of six comparison categories empty
(anything involving *outsource*), and snowballing never recovered them: **In-house vs. Outsourcing
was the one development option SB missed altogether**, and half the DB-only papers fell in that
category. Critically, **all four DB-unique papers were in fact findable in Google Scholar using the
SB search strings — just not in the first 10 results.**

**Do not rely on cross-category bridging.** Snowballing did carry papers between categories (a paper
in one category found papers in others, and new categories such as *Only OSS* and *Make vs. buy vs.
share* emerged that were not in the start set at all). But relying on that to populate *empty*
categories **did not work**. The paper is explicit: proceeding with empty categories in the start set
is a risk of missing relevant papers, and one should aim to cover every category with at least one
paper.

**A first-10-results cap is too shallow**, particularly for categories that return nothing. More
results should have been reviewed for those categories.

**Adding a disambiguating keyword did not help here.** Because the outsource-related strings returned
many non-software papers, three extra strings were added with "software" appended. **They produced no
additional papers.**

**Reference context is much less useful than expected (§4.2.4).** Only **16** decisions in the whole
study rested on the reference context. Failure modes:
- *The context may not reflect the paper's goal.* Their example: a context about code quality, where
  the paper also compared OSS with COTS — invisible from the context.
- *The context is vague.* "Previous studies have looked at using COTS and OSS components…" — "looked
  at" says nothing. Sometimes the context is just a keyword. When unintelligible, they read the
  enclosing paragraph.
- *The context can be actively deceiving.* A context describing building the same system three
  different ways read as a perfect OSS-vs-in-house match, but the paper was about operating-system
  development, out of scope; it was excluded only after full-text reading.
- *The context can be hard to locate at all.* Reference styles vary — numbers versus author names —
  and without ordering, navigation is difficult; e.g. the first citation encountered may be `[15]`
  rather than `[1]`.
- Asymmetry worth remembering: **it is easier to exclude than to include on reference context.**
  Their clean exclusion example was a context making it obvious the cited work was a method paper.
- The paper's conclusion: usefulness "highly depends on how well the reference context is described
  in the primary studies", and it calls on authors to describe their references more clearly.

**Noise composition differs between BSB and FSB.**
- BSB tends to surface references unrelated to the research topic — research-methods papers, tool
  papers.
- FSB risks a lot of **grey literature**, because a citation can be any document — master's theses,
  project reports. (In the event, FSB returned *less* grey literature than expected.)
- FSB returned far more **non-English** material: 8.0% versus BSB's 0.2%.

**Titles dominate the decisions, increasingly so.** The share of decisions made on title alone rose
each iteration — 61.9%, 77.7%, 75.5%, 91.7% — because the number of already-reviewed papers grows.
This distorts naive efficiency figures (see below).

**Unclear inclusion/exclusion criteria are more costly in SB than in DB search.** If a paper is
wrongly included, you snowball it, and then everything found from it must also be excluded when the
mistake is caught. Wasted effort compounds.

**A contradiction with prior work, stated by the authors.** Jalali & Wohlin found relatively *little*
noise in snowballing despite more general search strings. This study found the opposite: SB noise was
**98.23%** against DB's **95.17%**, and the authors say explicitly that this "contradicts with the
findings of [Jalali & Wohlin]".

**Efficiency metrics are not comparable unless normalised.** Counting all papers reviewed makes SB
look worse than DB (1.76% vs 3.21%); counting only abstracts reviewed reverses it (6.23% vs 5.70%).
Because excluding on title — and excluding duplicates, grey literature and non-English items —
costs very little effort, the paper argues **comparing on abstracts reviewed is the more reasonable
measure**.

### Clarifications on how a step should be performed

- **Organise the start set into categories that mirror the study's concepts**, and ensure **at least
  one paper in every category**. This is the paper's headline procedural recommendation.
- **Cluster the start set to avoid inbreeding.** They organised the start set into clusters where
  papers within a cluster had no citation relation to one another — no mutual references and no
  common authors — so that the start set represented genuinely different parts of the literature.
  They caution that the number of true clusters may turn out smaller, since papers found later may
  bridge two apparently separate clusters.
- **Prefer a start set that is not too recent.** Their start-set papers were not recently published,
  which they note gives a good chance of finding papers through *both* FSB and BSB.
- **Run both BSB and FSB.** Found equally efficient here (BSB 1.5%, FSB 1.4%), and each contributed
  roughly half the newly found papers (7 vs 8). Given how the start set was chosen, choosing only one
  direction risked missing a substantial number of papers. The authors endorse Jalali & Wohlin's
  recommendation to implement both. They add the caveat that the balance may shift with the start
  set — e.g. if it contains a highly cited seminal paper.
- **Extract data from an included paper *before* snowballing it (§4.2.5).** Two benefits: the
  detailed reading confirms the inclusion is valid, and it gives a good sense of the reference
  context. Reference-context-based include/exclude decisions can be made during extraction.
- **Explicit two-reviewer decision rules (their Table 2, citing Petersen & Ali).** Both accept →
  include for the next step. Both reject → exclude. **Either one accepts → include for the next
  step.** (I.e. disagreement resolves towards inclusion at the screening stage.)
- **Choose an index database that is not publisher-restricted** for building the start set — their
  reason for using Google Scholar.
- **Recalculate efficiency after removing cheap exclusions.** Report efficiency both on all papers
  reviewed and on abstracts/reference contexts reviewed, and separately on non-relevant papers after
  removing duplicates, grey literature and non-English items.
- The DB arm's own clarification: build search strings by **PICO** decomposition.

### Checklists, reporting guidance, evaluation criteria

**Characteristics of a good start set (their Table 4, taken from Wohlin's 2014 snowballing
guidelines), condensed, with the authors' self-assessment of compliance:**
1. *Papers in the start set should not reference each other.* — 4 of their 5 complied.
2. *The number of papers must be reasonable*, with focused research areas needing fewer papers than
   broad ones. — They judged 5 papers appropriate for a topic they did not perceive as extensively
   researched.
3. *The start set should span several different publishers, years and authors.* — Theirs covered
   three different years; **two papers shared authors**, a partial non-compliance.
4. *The start set should be formulated from keywords in the research questions.* — Complied.

Note the authors' own gloss: even though not every paper in the start set met the guidelines, **each
cluster** had the properties of a good start set.

**Their three exclusion-on-title rules (§4.2.1)** — a paper is excluded on title if (a) the title is
unrelated to the research topic/questions; (b) it is grey literature or not in English; (c) it has
already been reviewed.

**Efficiency definitions used.** RQ2 defines efficiency as the number of papers included relative to
the total reviewed — equivalently the noise-versus-relevance ratio. RQ3 defines reliability as the
ability to identify all relevant papers.

### Threats to validity framework

No named framework. The design controls threats structurally: identical research questions and
identical inclusion/exclusion criteria across both arms to remove judgement differences; independent
researchers per arm; the same time period; and a DB search run explicitly as a **validation step**
for the SB results. The single-researcher DB arm is acknowledged as a reliability threat, mitigated
by that researcher's experience. The paper positions itself against a prior reliability literature:
MacDonell et al. (two independent groups, same questions — reviews robust to differences in process
and people); Greenhalgh & Peacock's audit; Skoglund & Runeson (reference-based search satisfactory
for technically focused reviews, unsatisfactory where the search area is wide or terms general — so
precision is context-dependent); Jalali & Wohlin; Wohlin's replication; and Wohlin et al.'s mapping
study reliability work.

### Data extraction and analysis techniques

- **Citation matrix (their Figure 2).** A square matrix over all included papers marking who
  references whom (×) and who cites whom, with (−) where citation was impossible because the paper
  was not yet published, and blanks where no relation exists. Papers are grouped by the iteration
  that found them and ordered within a group by publication year. Useful for diagnosing start-set
  quality: they observed one anomaly where a 2007 paper referenced a 2008 paper, because the
  reference was to an unpublished version of the same work.
- **Evolution diagram (their Figure 1).** Papers plotted by category, with the shape of the marker
  encoding the iteration that found them (circles = start set, triangles = 1st iteration, squares =
  2nd, diamonds = 3rd) — this is what makes category coverage and cross-category bridging visible.
- **Venn diagram** of SB-unique / DB-unique / common papers.
- **Coverage comparisons** on three axes: papers, development options, and "dimensions" of research.
- **Conclusion-level comparison (their Table 9)** — the most interesting technique here. Rather than
  comparing only paper sets, they took each of the **15 conclusions** the mapping study actually drew
  and asked whether it would still hold if only SB, or only DB, had been used, marking each ✓ or ✗.
  This directly answers "does the search strategy change the answer?" — the same question Jalali &
  Wohlin asked.
- Research types were classified using **Wieringa et al.'s** requirements-engineering paper
  classification.

### Empirical findings worth citing

**Headline recall.** Of the 24 papers found in total, **SB identified 83% (20) and DB 45.9% (11)**.
Overlap: **7 common**; **13 SB-unique**; **4 DB-unique**. Overlap exceeded DB-unique (7 > 4).
(The abstract states 83% vs 46%.)

**Start set and iterations.**
- 9 search strings × first 10 Google Scholar results = **90 papers reviewed**; **5 included** →
  start-set efficiency **5.6% (5/90)**, or **6.4% (5/78)** counting only abstracts/introductions
  reviewed.
- Start-set composition: 3 papers from *COTS vs. OSS*, 1 from *In-house vs. COTS*, 1 from *In-house
  vs. OSS* (reclassified to a new *In-house vs. COTS vs. OSS* category). **No papers at all** for
  In-house vs. Outsource, COTS vs. Outsource, or Outsource vs. OSS.
- **2 of the 5 start-set papers generated nothing** under snowballing.
- **Four iterations** to saturation. Papers added: iteration 1 → **10**; iteration 2 → **3**;
  iteration 3 → **2**; iteration 4 → **0**. **Half of all 20 SB papers (10/20) came from the first
  iteration.**
- Per-iteration efficiency (all papers reviewed): 5.5% (10/181); 0.5% (3/627); 1.0% (2/188); 0.0%
  (0/48). **Revised** efficiency counting only abstracts and reference contexts: **14.5% (10/69);
  2.1% (3/140); 4.4% (2/46); 0.0% (0/4)**.
- **1,044 papers reviewed across the four iterations, of which 785 decisions were made on title
  alone.**
- Share of decisions made on title, by iteration: **61.9%, 77.7%, 75.5%, 91.7%**.
- After the first iteration, *In-house vs. COTS* had the most papers (overtaking *COTS vs. OSS*), and
  **5 of its 8 papers arrived from the COTS vs. OSS category**.

**BSB versus FSB.**
- Papers found: **BSB 7, FSB 8** (15 in the iterations).
- Papers reviewed: **BSB 470, FSB 574**.
- Efficiency: **BSB 1.5% (7/470), FSB 1.4% (8/574)** — effectively equal.
- Already-reviewed (duplicates): BSB **22.1% (104/470)**, FSB **20.7% (119/574)**.
- Grey literature: BSB **19.8% (93/470)**, FSB **16.0% (92/574)**.
- Non-English: BSB **0.2% (1/470)**, FSB **8.0% (46/574)**.
- Total noise: BSB **463**, FSB **566**.
- Non-relevant papers (noise minus grey/duplicate/non-English): BSB **265** = **56.3%** of papers
  reviewed; FSB **309** = **53.8%**.

**Snowballing overall.**
- Papers reviewed across start set plus iterations: **1,134** (90 + 181 + 627 + 188 + 48);
  20 included → overall efficiency **1.8%**.
- Noise **1,114 of 1,134 = 98.23%**. Of the 1,134: grey literature + duplicates + non-English =
  **483 (42.59%)** — broken out as 195 + 239 + 49; non-relevant papers = **631 (55.64%)**.
- Efficiency against non-relevant papers only: **3.17% (20/631)**.

**SB versus DB efficiency (their Table 8).**

| | Total efficiency | Abstracts only |
|---|---|---|
| Snowballing | **1.76% (20/1134)** | **6.23% (20/321)** |
| Database | **3.21% (13/404)** | **5.70% (13/228)** |

Noise: **SB 98.23%, DB 95.17%.**

**Coverage of development options.** SB and DB each covered **5** options; **3** were common
(In-house vs. COTS; COTS vs. OSS; Make vs. buy vs. share). DB-only: *In-house vs. OSS* and *In-house
vs. Outsourcing* — but SB did find one In-house-vs-OSS paper that also covered COTS, so
**In-house vs. Outsourcing was the only option SB missed entirely**. SB-only: *Only OSS* and
*In-house vs. COTS vs. OSS* — i.e. **single-option papers and three-option papers were found only by
snowballing**, even though the search strings compared options pairwise. Neither search found
anything for COTS vs. Outsource or Outsource vs. OSS. Of the 7 common papers, **5 were In-house vs.
COTS**; **5 of the 6 COTS vs. OSS papers** came via SB. **Half (2 of 4) of the DB-unique papers were
In-house vs. Outsource.**

**Dimensions.** Both searches found papers in **all** dimensions — notable because the DB strings
carried extra keywords ("decision", "trade-off", "selection") that the SB strings did not.

**Conclusion robustness (Table 9).** Of the 15 conclusions the mapping study drew: **only 1 would
fail if SB alone had been used; 9 would fail if DB alone had been used.** The single SB failure is
conclusion 3 ("only two studies consider outsource"). Conflicting/contradictory findings among
primary studies — entries 9, 11 and 12 (cost; market evolution/ease of use/vendor support; whether
OSS harms or helps maintainability) — were **reported only by SB-found papers**. Likewise, DB
recovered only a subset of Wieringa's research types, while **SB-found papers covered all of them**.

**Prior-work numbers cited (not this paper's own):** Greenhalgh & Peacock's audit found only **30%**
of studies via DB search versus **51%** via snowballing.

**Efficiency baseline for context:** the authors note their start-set review load was low compared
with traditional search-based reviews, citing two SE reviews that each screened an initial set of
**over 600 papers**.

---

## da_silva_2011 — Six Years of Systematic Literature Reviews in Software Engineering: an Extended Tertiary Study

da Silva, Santos, Soares, França & Monteiro. Center of Informatics, UFPE, Brazil. (Submitted to
ICSE'2010; the corpus dates it 2011.)

**Type:** Empirical study of reviews — a **tertiary study** (a mapping study *of* secondary studies),
extending and integrating two earlier tertiary studies by Kitchenham et al.

**Role in corpus:** The only paper here that measures, at population scale, **how SE reviews actually
perform against a quality instrument** — and the only one that reports what predicts a review's
quality score. It is also a worked example of the tertiary-study design itself, including an
explicit **decision-and-consensus procedure** for a five-person team, and it supplies the DARE
four-question quality criteria as applied in SE.

### Process steps or stages defined

**The EBSE five steps (§1)**, restated by analogy with evidence-based medicine: (1) convert an
information need about SE practice into answerable questions; (2) track down, with maximum
efficiency, the best evidence to answer them; (3) appraise that evidence critically for validity
(closeness to the truth) and usefulness (practical applicability); (4) implement the appraisal's
results in SE practice; (5) evaluate the performance of that implementation. **SLRs are the preferred
method for steps 2 and 3.** The authors press the point that a practice counts as evidence-based only
if *all five* steps happen — citing Greenhalgh that evidence-based practice means reading the *right*
paper and then changing behaviour, not merely summarising results without bias.

**Two review types distinguished (§1, after Petticrew & Roberts and Arksey & O'Malley):**
- *Conventional SLRs* aggregate results about the effectiveness of a treatment, intervention or
  technology, and answer specific questions of the form "is intervention I on population P more
  effective in obtaining outcome O in context C than comparison C?" — giving the **PICOC** structure.
  Where enough quantitative experiments exist, **meta-analysis** can integrate effect results.
- *Mapping (or scoping) studies* aim to identify all research on a topic and answer broader questions
  about research trends; typical questions are exploratory — "what do we know about topic T?"

**Their own tertiary-study process (§3):**
1. **Research questions** (RQ1–RQ5, below), with RQ1 split by time period.
2. **Search** — combined **automatic** search (6 engines) *and* **manual** search (named journals and
   proceedings), run in parallel, then merged and de-duplicated. Later augmented by a **backward
   search** of the reference lists of selected studies.
3. **Study selection** — full reading of all potentially relevant articles.
4. **Quality assessment** — DARE four-question instrument.
5. **Data extraction** — nine defined fields.
All three judgement-bearing activities run through the DCP (next section).

**The Decision and Consensus Procedure (DCP, §3.3, their Figure 1)** — reusable for any multi-person
review. Applied identically to **study selection, quality assessment, and data extraction**:
1. Start from a list of non-evaluated studies.
2. R1 **randomly allocates** each study to two researchers, Ri and Rj.
3. Ri and Rj evaluate individually, producing ri and rj.
4. R4 and R5 integrate the results into an **Agreement/Disagreement Table (ADT)**.
5. R1 randomly allocates ADT entries to researchers, **ensuring a different researcher Rk** handles
   them. (The two PhD students do not participate at this stage — only the three lecturers judge.)
6. Rk judges each disagreement and returns one of three outcomes: endorse one of the prior decisions;
   supply a **third** result rk; or leave the disagreement standing.
7. Remaining disagreements go to a **consensus meeting of all five researchers**.
8. R4 and R5 integrate everything into the final list of evaluated studies.

**Research questions (§3.1)** — RQ1: how many SLRs were published 1 Jan 2004 – 31 Dec 2009 (RQ1.1 to
30 Jun 2008 from prior studies; RQ1.2 for the new window)? RQ2: what research topics are addressed?
RQ3: which individuals and organisations are most active? RQ4: are the limitations observed in the
two previous studies still an issue? RQ5: is the quality of SLRs improving?

**Study nomenclature** used throughout: **OS** = Kitchenham et al.'s Original Study (20 SLRs,
Jan 2004 – Jun 2007, manual search); **FE** = the First Extension (33 additional unique studies,
Jan 2004 – Jun 2008, automatic search over five engines/indexes); **SE** = this Second Extension
(67 SLRs, Jul 2008 – Dec 2009); **OS/FE** = 53 studies; **OS/FE+SE** = 120 studies.

### Caveats, traps and pitfalls

**Limitations of prior SE reviews carried forward from the OS**, all of which this study re-tests:
- A large share of reviews investigated **research methods or trends rather than technique
  evaluation**, which ought to be a conventional SR's focus.
- The spread of SE topics was narrow, with technical reviews concentrated on cost estimation.
- Mapping studies analysed far more primary studies than SLRs.
- **Few SLRs assessed the quality of primary studies.**
- **Few provided advice oriented to practitioners.**
The authors single out the last two as the most concerning, because informing practitioners with
good-quality evidence is the entire point of evidence-based practice.

**A manual-only search misses studies** — the stated limitation of the OS, confirmed when the FE's
automatic search found 33 additional unique studies over an overlapping window.

**Automatic search alone is also insufficient.** Their validation found three OS/FE papers their
automatic search could not recover: one had been obtained in the OS by **directly contacting the
authors** and was not retrievable even by searching its exact title across all six engines; a second
behaved the same way; a third **is** indexed in the ACM DL but its authors used the word "survey"
rather than "review", so the search string missed it. That third case is the generalisable trap:
**terminology choice by primary authors defeats string-based search.**

**Backward search earns its keep.** A manual search of the reference lists of selected studies found
two further studies. One was missed because the EASE 2008 conference fell just outside the window
(included anyway, since OS/FE had missed it too); the other **was not found by the automatic IEEE
Xplore search even when searched for by exact title.** The authors say plainly that without the
reference-list search they would have missed an article.

**The DARE quality instrument has defects, as applied.** From §6:
- **QA4 is too subjective.** It caused many disagreements between evaluators that could only be
  settled in the consensus meeting.
- **QA2 is inconsistent.** They resolved the inconsistency by **consulting the researchers who ran
  the OS/FE studies** — i.e. by importing tacit scoring conventions that the published criteria did
  not carry.
- They also note the **DARE criteria had changed** to a five-question version by the time of their
  study, but they deliberately kept the older four-question version **for comparability** with OS/FE
  — a documented trade-off of currency against comparability.

**Classification of review type is not stable across tertiary studies.** They classified SLR vs. MS
using da Silva et al.'s method; the OS and FE used an **unreported** method, and the **OS did not
distinguish mapping studies from SLRs at all**, classifying everything as SLR. Re-classifying OS/FE
by their method changes its proportions from 32% MS / 68% SLR to **72% MS / 38% SLR** (as printed —
these do not sum to 100%, presumably a typographical error in the source), much closer to the SE
figures. **Caveat for anyone comparing tertiary studies: apparent trends in review type may be
classification artefacts.**

**Three explanations the authors found for missing quality assessment of primary studies (§5.4.3)** —
useful as failure modes to guard against:
1. Some researchers **confused quality assessment with stating inclusion/exclusion criteria**, and so
   believed no further assessment was needed.
2. Some deemed assessment unnecessary because studies came from "trustworthy sources" such as
   peer-reviewed journals — venue treated as a quality proxy.
3. Some found so few relevant studies that they appear to have **feared applying quality criteria
   would leave them with nothing to analyse**.

**Poor synthesis, and its suspected cause (§6).** Integration of primary-study results was poorly
done by many reviews. The authors' diagnosis: these reviews — mapping studies especially — are
trying to combine and synthesise results from **too diverse a set of primary studies**, which they
attribute in turn to the **scarcity of empirical replications in SE**.

**More primary studies correlates with *lower* quality.** A significant inverse correlation. The
proposed explanation, following Kitchenham et al.: faced with too many studies, researchers may skip
quality assessment and struggle to present good per-paper synthesis — precisely the behaviours that
QA3 and QA4 score.

**EBSE is not being fully realised (§6).** Beyond the low practitioner-guideline rate, the authors
could not determine from the reported data **whether the problem a review investigated originated in
industrial practice or was an academic problem**. Since practical problem origin and practitioner
guidelines are what steps 1, 4 and 5 of EBSE depend on, they conclude EBSE is not fully realised —
SLRs are instead being adopted as a research method for finding gaps and trends to guide *academic*
research, a reading corroborated by the rising proportion of mapping studies.

**Quality assessment matters differently by review type (§6).** Missing quality assessment is
critical for conventional SLRs — above all where meta-analysis pools effect sizes — but the authors
consider it a **minor problem for mapping studies**, whose goal is a broad overview of research
trends rather than a combined effect size. And since meta-analysis is very rare in SE, they judge
that in practice this has not been an issue. *(Note this is a softer line than Kitchenham & Charters
take on quality assessment in general.)*

**A discrepancy worth flagging:** their Table 6 is headed `OS/FE + SE (N=121)` while the rest of the
paper consistently uses **N = 120**. Treat the country breakdown's denominator with care.

### Clarifications on how a step should be performed

- **Use a mixed search process.** Their explicit recommendation from experience: automatic search on
  engines, *plus* manual search of relevant journals and proceedings, *plus* backward (reference-list)
  search of selected studies. Their conclusion is that missing only 1 indexed article in 51 "can be
  considered good **if the automatic search is complemented by manual procedures**."
- **Validate your search process against a known set.** They ran their search against the papers
  already found by OS and FE and reported exactly which ones it failed to recover and why. This is
  a directly reusable technique for arguing search adequacy.
- **At least two researchers per judgement, with a defined tie-break** — the DCP above. Their claim:
  the multi-evaluator procedure increases confidence in the reliability of the quality assessment.
- **Handle duplicate publication explicitly.** Where an SLR appeared in more than one venue, **both
  versions were read for data extraction** but only one — the **first published**, for consistency
  with OS/FE — was counted in the statistics.
- **Selection criteria they used:** exclude anything that is not an SLR — defined as a literature
  review with defined research questions, a search process, data extraction and data presentation —
  and exclude reviews on Information Systems, HCI or other computer-science topics clearly outside
  software engineering.
- **Search string design at tertiary level (§3.4).** `("Software engineering") AND` a long OR-list of
  seventeen review-naming phrases — including "review of studies", "structured review", "systematic
  review", "literature review", "literature analysis", "in-depth survey", "literature survey", "meta
  analysis", "past studies", "subject matter expert", "analysis of research", "empirical body of
  knowledge", "overview of existing research", "body of published research", "Evidence-based"/
  "evidence based", "study synthesis", "study aggregation". Searches ran over the **entire paper**
  including title and abstract — **except ISI Web of Science**, restricted to title and topic by the
  engine, and requiring minor syntax changes while keeping the semantics unchanged.
- **Preserve the earlier protocol when extending someone else's study (§3).** The team agreed two
  methodological decisions with the original authors: the extension would be performed
  **independently, with as little information exchange as possible**, and would use **as close as
  possible the same protocol** as the First Extension. Rationale: neither study should bias the
  other, while the shared protocol keeps the results comparable. A clean template for replication or
  extension of a secondary study.
- Reviews that cited the EBSE papers or the guidelines were found in every case to do so as
  **methodological justification** for their own study, so all such reviews were treated as
  "EBSE-positioned".

### Checklists, reporting guidance, evaluation criteria

**The DARE four-question quality instrument (§3.6)**, from the Centre for Reviews and Dissemination
at York, as used by OS, FE and this study — condensed:
- **QA1:** Are the review's inclusion and exclusion criteria described, and are they appropriate?
- **QA2:** Is the literature search likely to have covered all relevant studies?
- **QA3:** Did the reviewers assess the quality/validity of the included studies?
- **QA4:** Were the basic data/studies adequately described?

**Scoring.** Each question is answered Y / P / N and scored **Y = 1, P = 0.5, N = 0**; the four are
summed to a quality score out of 4. The worked rubric given for QA1: **Y** = inclusion criteria are
explicitly defined in the paper; **P** = the criteria are implicit; **N** = the criteria are neither
defined nor readily inferable. Studies were ranked by total score and split into quartiles.

**The nine data-extraction fields (§3.7)** — a usable extraction form for any tertiary study:
1. Year of publication.
2. Quality score.
3. **Review Type** — conventional SLR, meta-analysis (MA), or mapping study (MS).
4. **Review Scope/Focus** — a detailed technical question (**RQ**), research trends within an SE
   topic area (**SERT**), or research methods in software engineering (**RT**).
5. SE **topic area** addressed.
6. Whether the study **cited EBSE papers** and/or **cited guidelines** (recorded separately).
7. **Number of primary studies** analysed, as stated explicitly or derivable from tabulations.
8. Whether **practitioner guidelines** are present as an identifiable part of the paper — a section,
   a table — not merely implied.
9. **Source type** in which the study was first reported: journal (J), conference (C), workshop (WS),
   book series (BS).

### Threats to validity framework

No named framework. Validity is handled procedurally: independence from the study being extended;
protocol reuse for comparability; the DCP's two-evaluator-plus-tie-break design across all three
judgement activities; and empirical validation of the search process against a known reference set,
with failures itemised. The paper is candid about instrument-level threats — QA4's subjectivity,
QA2's inconsistency, and review-type classification differing between tertiary studies.

### Data extraction and analysis techniques

- Agreement/Disagreement Table as the shared artefact between independent evaluators.
- Quartile ranking of studies by quality score, reporting the top and bottom quartiles in detail
  (space precluded the middle two).
- Per-question inspection of the quality table to locate *which* criteria the weak studies fail.
- **Medians, not means, for primary-study counts** — appropriate given the extreme skew mapping
  studies introduce.
- **Regression analysis** with quality score as dependent variable and review characteristics as
  factors; **Pearson correlation** between number of primary studies and quality score. Note the
  paper reports a *negative* result too: a regression using "Cited Guidelines" as the factor showed
  **no statistical significance** over the whole set of 120 SLRs, even though Kitchenham et al. had
  found guideline use significantly correlated with quality.
- Future work they flag as needed: methods for **integrating qualitative data**, given the rising
  incidence of case studies and other qualitative research in SE, with the aim of producing
  guidelines for SLRs of qualitative studies.

### Empirical findings worth citing

**Search and selection funnel (their §3.4–3.7).**
- Automatic search across **6** engines (ACM DL, IEEE Xplore, ScienceDirect, CiteSeerX, ISI Web of
  Science, Scopus) → **1,389 documents**.
- Title-and-abstract filter → **157 papers**.
- Manual search of the named journals/proceedings → **66 potentially relevant articles**.
- Merged and de-duplicated → **154 unique papers**, all read in full.
- Reference-list (backward) search added **2** studies.
- → **77 articles** to data extraction and quality assessment.
- **10 excluded** after extraction: 4 not software engineering; 3 were reports of two SLRs already in
  the FE; 1 from 2010 (outside the window); 1 a shorter version of another included paper; 1 scored
  **zero** on quality and lacked most required information.
- Final: **67 SLRs**, addressing **24** SE topics.
- Search validation: of **51** indexed articles from OS/FE, **only 1 was missed**; three papers in
  total were not found, two of which are not indexed anywhere reachable.

**Population growth (their Table 4).** OS/FE: 53 studies over 4.5 years (Jan 2004 – Jun 2008). SE:
67 studies over 1.5 years (Jul 2008 – Dec 2009). Combined **120**. Per year (OS/FE + SE = total):
2004 = 6; 2005 = 11; 2006 = 9; 2007 = 15; 2008 = 12 + 16 = **28**; 2009 = **51**. **2009 alone
accounts for 43% (51/120)** of all SLRs. EBSE-positioned studies (citing EBSE papers and/or the
guidelines) per year, as a share: 2004 **17%**, 2005 **45%**, 2006 **67%**, 2007 **60%**, 2008
**79%**, 2009 **80%**; overall **84/120 = 70%**. In the SE window, **80% (53/67)** cited the EBSE
paper, the guidelines, or both.

**Topics (RQ2).** SE's 67 reviews covered **24** topics, **14 of them not present in OS/FE**. Most
frequent in SE: Requirements Engineering (8), Distributed Software Development (8), Software Product
Line (7), Software Testing (6), Empirical Research Methods (5), Software Maintenance and Evolution
(4), Agile Software Development (4) — the top six topics accounting for **54% (36/67)**. By
contrast OS/FE's 53 reviews covered **18** topics with **55% (29/53)** in just three: Software Cost
Estimation (12), Empirical Research Methods (11), Software Development in general (6). Across all
**120** studies: **38 distinct topics**, with the top six — Empirical Research Methods (16),
Software Cost (13), Requirements Engineering (10), Distributed Software Development (9), Software
Development in general (9), Software Testing (9), Software Maintenance and Evolution (7) — covering
**55%**. **Reviews of empirical research methods are the single most frequent topic overall, at over
13% (16/120).**

**Research-methods focus (RQ4).** OS reported **40% (8/20)** of studies aimed at research methods;
FE reported a fall to **18%**; **SE found 27% (18/67)** — i.e. the decline did **not** continue.

**Review type.** SE: **82% (55/67) mapping studies**, **18% (12/67) conventional SLRs**. OS/FE as
originally classified: **32% (17/53) MS**, **68% (36/53) SLR**. Re-classified by da Silva et al.'s
method, OS/FE becomes **72% MS / 38% SLR** (as printed in the source).

**Primary studies per review (their Table 7, medians).** SLRs and meta-analyses: 2004 = 26.5 (n=6);
2005 = 19.5 (n=8); 2006 = 32 (n=7); 2007 = 21 (n=8); 2008 = 26.5 (n=8); 2009 = 20 (n=11). Mapping
studies: 2004 = – (n=0); 2005 = **119** (n=3); 2006 = **403.5** (n=2); 2007 = **137** (n=7);
2008 = **49** (n=20); 2009 = **54.5** (n=40). Mapping studies consistently analyse far more primary
studies.

**People and organisations (RQ3).** OS/FE: **103 researchers, 17 countries, 46 organisations** (the
text also gives 43 organisations for OS/FE when computing the combined figure). SE: **159
researchers** — a **50% increase** against a **26% increase** in the number of SLRs, so authors per
study rose. Studies with **3 or more authors** rose from **58% (31/53)** to **67% (45/67)**;
**single-author** studies fell from **13% (7/53)** to **1% (1/67)**. Across OS/FE+SE: **21 authors**
have co-authored three or more SLRs, **24** have co-authored two, and **125** appear on only one.
Organisations: **55** in SE, **90 distinct** across OS/FE+SE. Countries: **17 → 25**, with **8 new
countries** in SE. **59 newcomers** — researchers doing their first review — appear in SE.

**Geography (their Table 6).** Europe **85%** of OS/FE, **84%** of SE, **83%** overall (101 studies).
North America 17% → 10% → 13%. South America 9% → 12% → 11%. **Asia 0% in OS/FE → 15% (10/67) in
SE.** Middle East 2% → 0%. Oceania 9% → 3% → 6%. **US researchers account for fewer than 12%
(14/120)** of all studies. Israel and Colombia appeared in OS/FE but not in SE.

**Practitioner orientation (RQ4, their Table 8) — the headline negative result.** In SE, 20 reviews
addressed questions of potential practitioner interest, of which **11 directly addressed technical
evaluation questions (RQ scope)**. But only **18% (12/67)** explicitly provided practitioner
guidelines. Rates: OS/FE **17% (9/53)**, SE **18% (12/67)**, combined **18% (21/120)** — i.e. **no
improvement at all** across six years. Meanwhile **58% (39/67)** of SE reviews addressed research
trends of only indirect practitioner interest, and **8** studies investigated research methods, of
no interest to practice.

**Quality assessment of primary studies (their Table 9).** Reviews that evaluated their primary
studies' quality: OS/FE **30% (16/53)**; SE **67% (45/67)**; combined **51% (61/120)** — where "yes"
includes both full evaluation (score 1) and implicit evaluation (score 0.5). Reviews performing a
**full and explicit** evaluation in SE amount to only **21% (14/67)**.

**Use of guidelines (their Table 10).** Cited EBSE papers: OS/FE **13% (7/53)** → SE **18% (12/67)**
→ combined **16% (19/120)**. Cited guidelines: OS/FE **51% (27/53)** → SE **76% (51/67)** →
combined **68% (81/120)** — the SE figure excludes 3 studies that cited non-EBSE review guidelines,
which is why the combined count exceeds 27 + 51. Cited both: **6% → 15% → 11% (13/120)**.

**Quality trend (RQ5, their Table 11).** Mean quality score, all studies, by year: 2004 **2.08**;
2005 **2.27**; 2006 **2.61**; 2007 **2.43**; 2008 **2.50**; 2009 **2.61**. Year-on-year change:
**+5%, +7.5%, −5%, +2.5%, +2.5%**. **Total increase across 2004–2009: 12.5%** — a steady rise except
for the 2007 dip. Split by guideline citation, the gap is large: studies *not* citing guidelines
averaged 2.08 / 2.33 / 2.00 / 1.79 / 1.50 / 2.15 across 2004–2009, while those citing guidelines
averaged – / 2.20 / 3.10 / 3.00 / 2.80 / 2.72.

**What the quality scores are made of (§5.5).** Almost all studies in both the top and bottom
quartiles scored well on **QA1 and QA2** (inclusion/exclusion criteria and search coverage) —
attributed to the growing use of the guidelines at planning time. Fourth-quartile studies scored
well on all four. **First-quartile studies characteristically failed QA3 or QA4** — quality
assessment of primary studies, and synthesis/presentation of per-study findings.

**What predicts quality (§5.5).** Mean quality scores by factor:
- Provides practitioner guidelines **2.85** (sd 0.91) vs. does not **2.38** (sd 0.83).
- Published in a **journal 2.69** (sd 0.94) vs. **conference 2.44** (sd 0.81).
- Scope **RQ 2.88** (sd 0.76) vs. **SERT 2.41** (sd 0.91) vs. **RT 2.28** (sd 0.79).

Regression on these three factors, significant at 95%: practitioner guidelines **B = 0.183, se =
0.038, p = 0.000**; journal **B = 0.117, se = 0.041, p = 0.005**; RQ scope **B = 0.081, se = 0.036,
p = 0.025**.

**Number of primary studies vs. quality:** significant **inverse** correlation, **Pearson r = −0.204,
N = 120, p = 0.05**.

**A negative result:** regressing quality score on "Cited Guidelines" showed **no statistical
significance** over the full set of 120 SLRs — despite Kitchenham et al. having reported guideline
use as significantly correlated with quality.
