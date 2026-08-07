# Batch 6b — Grey literature: empirical evidence and information-science perspective

Working notes for the methodology reference document. All prose below is paraphrase unless
enclosed in quotation marks. Section numbers refer to the source paper's own numbering.

---

## kamei_2021 — Grey Literature in Software Engineering: A critical review

**Role in corpus:** The largest empirical audit of how SE secondary studies actually handle grey
literature — a tertiary study of 446 secondary studies (2011–2018) that measures definition use,
search effort, quality appraisal, GL type mix, producer mix and, notably, link rot; it is the
paper to cite when claiming that GL practice in SE is under-specified rather than merely debated.

### Definition and classification of grey literature

Kamei et al. do not coin a definition; they inherit one and then measure which definitions the
field uses (their contribution is the measurement).

- **Working definition adopted (Intro).** GL is literature that has not passed a quality control
  mechanism such as peer review before publication (attributed to their ref. [1]).
- **Recommended definition (Discussion RQ1 overview; Challenge 1).** They endorse Garousi et al.'s
  2020 formulation, which they quote: GL in SE is "any material about SE that is not formally peer
  reviewed nor formally published". They expect future work to benefit from adopting it.
- **Adams et al.'s three grey forms, imported by Kamei (Intro).** Kamei explicitly cites Adams et
  al. for a distinction between:
  - **grey literature** — the conventional sense;
  - **grey information** — material informally published or never published at all, e.g. meeting
    notes and emails;
  - **grey data** — user-generated web content; Kamei notes Williams and Rainer treated tweets,
    blogs and Q&A posts as grey data.
  Kamei observes these finer categories "have not been widely adopted in the SE literature" and
  therefore, for their own study, they fold *all* grey data and grey information into GL. This is
  a deliberate widening of scope and should be noted when comparing their numbers to others'.
- **"Shades of grey" tier model (Intro, Fig. 1; adapted from Garousi et al.).** A pyramid whose
  apex is **white literature** (published journal and conference papers, proceedings). Below it
  sit the GL sources, sorted into **three tiers** along two dimensions:
  - **expertise** of the producer, running from *unknown* to *known*;
  - **outlet control**, running from *lower* to *higher*.
  The darker the shade, the less the source is moderated or edited against explicit, transparent
  knowledge-creation criteria. Kamei used these shades as the reference frame for interpreting GL
  types throughout the paper, and they recommend the SE community do the same to stop
  type-misclassification (Challenge 1).
- **Empirical definition landscape (RQ1, §5.1).** Of the 446 secondary studies, **150 (33.6%)**
  offered some kind of GL definition; only **34** used a general term such as "grey"/"gray", while
  **116** gave no clear definition and instead described GL by its characteristics. The
  characteristic-based categories found (a study can fall in more than one):
  - **Expressed by GL type** — 108/446 (24.2%). E.g. GL enumerated as technical reports plus book
    chapters; or as technical reports, non-peer-reviewed articles and webpages.
  - **Not peer reviewed** — 75/446 (16.8%).
  - **Literature produced by practitioners** — 40/446 (9%). Published in industry, not academia.
  - **Non-published literature** — 24/446 (5.4%). Work in progress, non-indexed works,
    unpublished material.
  - **Others** — 13/446 (2.9%). Includes treating GL as "secondary sources of information", and
    equating GL with a lack of trust in the publisher.
  [EXTRACTION UNCLEAR: the five category counts sum to 260, which exceeds the reported 150
  definitions found in 116 studies even allowing multi-category assignment; the paper's own
  arithmetic note (§4.5.2) says 150 answers were reported in 116 studies. Treat the individual
  category counts as the reliable figures and the 150 total as unreconciled.]

### Process steps

Kamei's own tertiary-study process (§4), which doubles as a worked example of a tertiary
protocol, followed Kitchenham et al.'s guidelines:

1. **Three-pronged search (§4.1)** — (i) harvest secondary studies already listed in five prior
   tertiary studies (Kitchenham 2009, Kitchenham 2010, Da Silva et al., Cruzes and Dybå, Neto et
   al.); (ii) automated search of ACM DL, IEEE Xplore, ScienceDirect and Scopus; (iii) manual
   search of premier venues — journals TOSEM, TSE, EMSE, IST, JSS; conferences ICSE, ESEM, EASE.
2. **Search string (§4.1.1)** — reused Da Silva et al.'s string, extended with GL-specific terms
   ("grey review", "grey literature", "gray review", "gray literature", "multivocal literature",
   "multi-vocal literature") alongside the usual secondary-study synonyms. Practical note: Scopus
   caps search-field length, so the string had to be **split into 24 sub-queries**.
3. **Seven-phase selection (§4.3, P1–P7)** — P1 seed set of 181 studies from prior tertiary
   studies; P2 automated search 13,762; P3 manual search 6,238 (total 20,181, each given a unique
   ID); P4 apply date and duplicate criteria (removed 1,099 out-of-range and 4,755 duplicates,
   leaving 14,327); P5 full reading against EC3–EC7 (removed 13,007, leaving 1,320); P6 apply the
   venue-quality criterion, leaving **446**; P7 data analysis and synthesis.
4. **Duplicate resolution rule (§4.3)** — compare titles; where titles match, compare abstracts;
   if abstracts differ, keep the fuller study (per Kitchenham and Charters); if abstracts are the
   same, drop one, and where publication years differ, drop the older.
5. **Data extraction (§4.4)** — general study information following Da Silva et al. for RQ2, and
   items modelled on Zhang et al. for the rest: authors, publication year, institution, country,
   number of included studies, motivations/reasons regarding GL, plus, for each GL item, **its
   type and whether the data is still available online**.
6. **Analysis (§4.5)** — mixed methods. Qualitative strand is a thematic analysis in four moves:
   familiarisation (each researcher reads and re-reads every study), initial post-formed coding
   done individually, grouping similar codes into categories by a single researcher, then
   category refinement by two evaluators with a third resolving disagreements. Quantitative
   strand is descriptive statistics over two samples — all 446 for RQ1/RQ2/reasons-to-avoid, and
   the 126 GL-using studies for RQ3/RQ4/motivations-to-use/RQ6.

Exclusion criteria used (Table 1) — a reusable template for a tertiary study: published outside
2011–2018 (EC1); duplicate (EC2); not in English (EC3); not a full paper, e.g. position paper,
abstract, poster (EC4); not peer reviewed, e.g. editorial, summary, letter, keynote, slides
(EC5); not a secondary study, i.e. not SLR/MS/MLR/GLR/MA (EC6); not SE, e.g. information systems
or computer science generally (EC7); venue below a minimum h5-index — **20 for conferences, 25
for journals** (EC8). EC1 was deliberately *not* applied to studies inherited from prior tertiary
studies.

**What the surveyed community actually does (RQ3, §5.3).** Kamei found no GLR-specific guideline
in existence at all; the surveyed studies fell back on Kitchenham and Charters (67 studies, the
most used) and on Wohlin's snowballing guidelines. Even MLR and GLR studies leaned on
Kitchenham's or Petersen's guidelines.

### Quality / credibility appraisal criteria

Only **7 of 126** GL-using studies (5.5%) applied any GL-specific quality criteria — three MLRs,
one GLR, three of other types. None of the seven used Garousi et al.'s criteria, which Kamei
identify as the state of the art. The three schemes Kamei did find:

- **Soldani et al. (a GLR), four criterion groups**, combined with inclusion/exclusion criteria:
  - *practical experience* — measured in years of experience in the subject;
  - *industrial case* — whether the source reports prior experience on the subject;
  - *heterogeneity of the results*;
  - *implementation quantity* — the level of detail in which results are discussed.
- **Tom et al. (an MLR)** — argued that an MLR's diversity forces per-type appraisal, and assessed
  each source on: *position and certainty of the source*, *clarity*, *detail*, *consistency*,
  *plausibility*.
- **Garousi et al.** — *authority*, *accuracy*, *coverage*, *objectivity*, *date*, *significance*.

Kamei's own recommendations (Challenges 3 and 6):
- Define an appraisal instrument fitted to the *types* of GL the search actually returned; a
  single instrument is hard to apply across heterogeneous GL forms (a point they credit to Tom et
  al., and to Kitchenham's general warning that quality instruments must match study types).
- Prefer sources in the **1st and 2nd tiers** of the shades model — producers with high or
  moderate expertise and high or moderate outlet control.
- Use credibility heuristics from prior work: Kamei et al.'s own earlier finding that sources from
  renowned authors, institutions, companies, or renowned producers cited by others are worth
  preferring; and Williams and Rainer's criteria that a GL source be **rigorous, relevant, well
  written, and experience-based**.

### Search techniques and stopping rules

Procedures used by the 126 GL-using studies (Table 3; percentages of 126):

| Source | # | % |
|---|---|---|
| Academic search engines (automatic) | 102 | 80.9% |
| Google Scholar (automatic) | 47 | 37.3% |
| Google (automatic) | 28 | 22.2% |
| Microsoft Academic Research (automatic) | 3 | 2.4% |
| Manual search | 31 | 24.6% |
| Specialized databases | 14 | 11.1% |
| Snowballing | 50 | 39.7% |

- **62.7%** of secondary studies combined multiple search methods (automatic + manual +
  snowballing).
- **All** GLRs and MLRs used Google as a primary search engine.
- Of the 10 GLR/MLR studies that clearly intended to find GL, **only 2** used sources different
  from those a conventional secondary study would use. Only **14** studies overall used
  specialised databases (examples given: Agile Alliance, YouTube, Stack Overflow).
- Two studies stood out for search design: one searched GL across Google, Bing, DuckDuckGo,
  Yahoo! and Webopedia; another (Williams) used reasoning markers to find rigorous blog articles.
- **Kamei's advice (Challenge 2):** general web search is not a substitute for specialised
  sources. They relay Bonato's argument that specialised data sources are reproducible and reach
  Deep Web content that Google may miss — Google "may not identify more than 16% of the content
  available". They point to Rainer and Williams' heuristics as the way to raise relevance and
  rigour without drowning in irrelevant hits.
- **Stopping rules:** none reported. Kamei document *no* saturation criterion or effort bound in
  the surveyed studies, and record "time-consuming" as a perceived challenge instead — the
  absence is itself the finding.

### Caveats, traps and pitfalls

Kamei's six named challenges, each with their proposed mitigation:

1. **No agreed GL definition, and misunderstanding of GL types.** Different studies classify the
   same artefact differently — PhD/master's theses were treated as peer-reviewed by one study and
   as GL by another; the same conflict appeared for books and book chapters. This introduces
   classification bias. *Mitigation:* state explicitly what GL means for the study and which types
   are in and out; adopt Garousi's definition; classify with the shades model.
2. **No search effort aimed at GL-specific sources.** Most studies used Google or Google Scholar
   as the primary GL channel. *Mitigation:* understand which sources (blogs, Q&A sites, videos)
   carry the relevant content and what each offers; use search heuristics to control volume.
3. **No GL-specific quality assessment criteria.** Applying peer-review-shaped criteria to GL
   evaluates the wrong thing; a single instrument cannot fit all GL forms. *Mitigation:* build
   criteria matched to the retrieved GL types.
4. **No GL classification in the reporting.** Only **46%** of the GL-using secondary studies
   classified the GL they used, forcing Kamei to reconstruct types by reading reference metadata
   or opening links — with interpretation bias as a result. *Mitigation:* classify each GL item by
   type, as scientific papers are classified by publication channel.
5. **GL availability / link rot.** See metrics below. *Mitigation:* archive everything collected
   in an external, preferably open-access, preserved archive (Zenodo, Figshare are named, citing
   Mendez et al.); and use web-archiving services such as the Internet Archive — Kamei demonstrate
   recovering a dead GL URL through it.
6. **Lack of reliability/credibility.** The direct trade-off against "hearing the practitioners'
   voice". *Mitigation:* restrict to tiers 1–2 and apply credibility criteria (above).

Additional pitfalls surfaced by the study itself:

- **The epistemological problem** (5/126 studies, 4%) — practitioners may be restating opinions
  heard from other practitioners, and GL rarely reveals its own source of knowledge. Kamei quote
  the vivid formulation: "We do not know how we know what we know". A related observation is that
  GL evidence tends to be opinion- or experience-based rather than resting on systematic data
  collection.
- **Non-structured information** (8/126, 6.3%) — GL has no format acknowledged across sources,
  and varies in structure and formality of language, making assessment hard.
- **Time cost** (4/126, 3.2%) — screening GL is slow because there is usually no usable abstract
  or summary; the sheer volume makes location and synthesis impractical.
- **Difficulty measuring quality** (2/126, 1.6%) — one team concluded it is very hard to measure
  GL quality uniquely within a systematic, controllable and replicable secondary study. Another
  offered the sharp counter-observation that the demands of formal publishing actually *increase*
  the amount of empirical evidence present.
- **Reference verification** — one study reported that verifying references became troublesome
  precisely as more of them came from web-hosted GL, since many had moved or vanished.
- **Terminology drift** — several SLRs and MSs ran systematic GL searches without ever using the
  word "multivocal", so counts of MLRs in the literature are probably underestimates.
- **Trade-offs are structural, not resolvable by preference.** The same property that makes GL
  attractive (practitioner voice, publication-bias reduction) is what makes others avoid it
  (reliability, credibility). Kamei present this as two explicit trade-offs requiring a criteria-
  based decision rather than a blanket policy.

### Metadata requirements

Derived from the study's own extraction form and from Challenges 4–5, what should be recorded per
GL item:

- **Type** of the GL source, using an explicit scheme (Kamei recommend the shades-of-grey tiers);
  and the tier assigned.
- **Producer** — the class of author/organisation. Kamei classified producers following Maro et
  al. into: Consultant/Company, Academia, Practitioner, Tool vendor, Standardization Body, Agency,
  Others, Unknown. This exists specifically because Garousi's appraisal asks about the reputation
  of the author and publishing organisation, which cannot be judged if the producer is unrecorded.
- **URL** — Kamei treat a missing URL as a defect in its own right (24.8% of items had only a
  reference title). Cite Kitchenham et al. on traceability: data must remain available to others
  later.
- **Accessibility status at time of use**, and ideally an archived copy (Zenodo/Figshare/Internet
  Archive snapshot) so that the appraisal remains checkable.
- **Publication year** — Kamei track GL by year of publication, which is what lets them show the
  rise of blog posts.

### Threats to validity framework

Kamei use a plain two-category frame (§8, headed "Limitations"), not a named taxonomy:

- **Internal validity** — their own interpretation and classification of GL types where the
  studies did not classify them. Mitigation: where a study stated a GL count, they independently
  counted GL entries in its reference list and compared (difference ≈ **3%**). They flag openly
  that counting books and book chapters as GL is contestable: excluding those types would remove
  **38 of the 126** studies that used only that type of GL.
- **External validity** — mitigated by breadth (2011–2018, premier venues), but the restriction
  to top conferences and journals may under- or over-represent GL use; and reliance on authors'
  own labelling means MLR counts may be understated because of the terminology drift noted above.
- **Reliability of selection** (reported in §4.3 as part of the method rather than §8) — because
  applying criteria in pairs across all studies was infeasible, a random **21% sample (n = 3,030)**
  was dual-reviewed by six authors with conflict-resolution meetings and a third author as
  tie-breaker; agreement was **Cohen's Kappa = 0.571**, "moderate" on the scale they cite (slight
  0–0.20, fair 0.21–0.40, moderate 0.41–0.60, substantial 0.61–0.80, almost perfect 0.81–1.00).
  The remaining **79% (n = 11,297)** were screened by a single reviewer.

### Empirical findings worth citing

Prevalence and contribution:

- **126 of 446** secondary studies (**28.2%**) used or searched for GL; use grew over the
  2011–2018 window.
- **95 of 126** (**75.4%**) used GL to support the answer to at least one research question. But
  fewer than half of GL-using studies used GL for more than half of their RQs; **31 studies
  (24.6%)** included GL yet used it to answer no RQ at all; and **6 MLRs (4.8%)** answered none of
  their RQs with GL support.
- Across the whole corpus GL-derived evidence represents **under 21%** of all 446 secondary
  studies' evidence base.
- **Distribution of GL share within studies** (Table 2): most SLRs and MSs included **≤10%** GL
  (48 SLRs, 31 MSs). MLRs are the opposite — none had ≤25% GL; 3 had 26–50%, 3 had 51–75%, 1 had
  76–100%. No GLR fell in any band [reported as zero across all bands, presumably because a GLR is
  100% GL by construction].

Disagreement with prior tertiary studies — useful for showing how definitional choices move the
numbers:

- Yasin et al. found **76%** of secondary studies included GL; Kamei attribute the gap to Yasin
  counting conference proceedings and workshop papers as GL, which Kamei reject for SE because
  highly ranked SE conferences have established peer review.
- Zhang et al. found a GL ratio of **22%** (close to Kamei's <21%) but reported only **25%** of
  studies using GL to evaluate conclusions, versus Kamei's **75.4%** answering ≥1 RQ — Kamei
  attribute the divergence to measuring different things (per-RQ support vs. conclusion
  evaluation). Yasin et al. reported only **9.2%** of GL used to support findings.

Types, producers, availability:

- **1,314** GL items were mentioned; only **1,273** could be retrieved from reference lists (41
  missing); **25** were peer-reviewed papers misclassified as GL and removed — leaving **1,246**
  GL items in **21 distinct types**.
- **54% (68/126)** of studies did not classify their GL at all.
- Most common types: **books/chapters (65 studies)**, **technical reports (53 studies)**, then
  theses, web articles, blog posts, whitepapers. Mapped onto the shades model: 4 types in tier 1,
  9 in tier 2, 8 in tier 3 — i.e. most GL used sits at a *medium* level of control and expertise.
- Blog posts dominate in MLR and GLR studies specifically. Blog posts become frequent from 2000
  and rise steadily; growth in GL use overall dates from 2009, driven by blog posts, theses and
  web/news articles. Books/chapters stayed flat. Whitepapers, videos and descriptions of
  projects/software/tools are recent additions.
- **Producers** (Table 4, n = 1,246): Consultant/Company **391 (31%)**; Academia **361 (28.6%)**;
  Practitioner **230 (18.2%)**; Tool vendor **67 (5.3%)**; Standardization Body **10 (0.8%)**;
  Agency **7 (0.6%)**; Others **14 (1.1%)**; Unknown **166 (13.2%)**. The top three account for
  roughly 80%. Consultants/companies produced most books/chapters, blog posts, web articles,
  slides and videos; academia most theses, technical reports and books/chapters; practitioners
  most blog posts, web articles and whitepapers. Kamei's finding differs from Yasin et al., who
  put academia first at 38.3% — again traced to Yasin's inclusion of conference/workshop papers.
- **Link rot (the headline number).** Of 1,246 GL references: **24.8% (309)** gave a title but no
  URL; **23.7% (295)** had a URL that failed (server not found, page not found); **51.5% (642)**
  were still reachable. The abstract summarises this as **49% of GL URLs no longer working** at
  the time of the study. Among items with no URL, more than half were produced by academia; among
  failing URLs, more than 30% came from consultants/companies.

Motivations and reasons (with how rarely they are stated at all):

- **Motivations to use GL** (Table 5, n = 126; 35 studies gave any): identify more studies **16
  (12.7%)**; incorporate practitioners' point of view **10 (7.9%)**; reduce publication bias **5
  (4%)**; others **4 (3.2%)**; **no motivation given — 91 (72.2%)**.
- **Reasons to avoid GL** (Table 6, n = 446; 28 studies gave any): lack of quality **23 (5.1%)**;
  hard to identify GL **3 (0.7%)**; others **2 (0.4%)**; **no reason given — 418 (93.7%)**. Sub-
  reasons under "lack of quality": absence of peer review (most common), validity constraints
  (external validity of the synthesis depends on the external validity of the identified
  literature), and source reliability. One study excluded GL explicitly to keep the SLR
  straightforward and repeatable, accepting the loss of valuable studies as the price.
- **Field-maturity effect:** teams working a well-established field tend to skip GL because
  peer-reviewed papers are plentiful; teams working a new topic (the microservices example) turn
  to GL precisely because academic work is scarce while industry output is large.
- **Perceived benefits** (n = 126; only 13 studies said anything): provision of practical
  evidence **13 (10.3%)**; knowledge acquisition **9 (7.1%)** — excluding grey sources would
  "miss a major pile of experience and knowledge" from practising engineers; makes academic
  studies more interesting to practitioners **6 (4.8%)**, with the recommendation that GL be
  included when a topic has few academic studies but high practitioner interest; coverage of
  results not found in scientific studies **3 (2.4%)**; easy to access and read **1 (0.8%)**.
- **Perceived challenges** (n = 126; only 14 studies said anything): non-structured information
  **8 (6.3%)**; epistemological problem **5 (4%)**; time-consuming **4 (3.2%)**; difficulty
  measuring quality **2 (1.6%)**; others **2 (1.6%)**.

Replication package: the study's data is deposited at Zenodo (doi 10.5281/zenodo.4079994) — a
practical demonstration of the archiving advice they give under Challenge 5.

---

## yasin_2020 — On Using Grey Literature and Google Scholar in Systematic Literature Reviews in Software Engineering

**Role in corpus:** The earlier, narrower tertiary measurement (138 SE SLRs, 2004–mid-2012, 6,307
primary studies) that quantifies GL as a *share of primary studies* rather than a share of
studies, and which additionally proposes eight practical GL categorisation strategies and a GL
quality checklist — plus a separately useful side finding on whether Google Scholar alone can
recover an SLR's primary studies.

Important compatibility caveat before using any of its numbers: Yasin et al. count **conference
papers not indexed in the four major databases** as grey literature. Kamei et al. explicitly
reject this for SE and attribute their much lower GL prevalence figures to it. Yasin's headline
76% and Kamei's 28.2% are therefore not measuring the same thing.

### Definition and classification of grey literature

- **Primary definition adopted (§I).** GL is informally published written material not indexed by
  major database vendors such as IEEE Xplore and ACM DL, typically attributed to government,
  academia, pressure groups, trade unions and industry, and not rigorously peer reviewed. They
  contrast it with "white" literature, which they characterise as peer-reviewed material
  obtainable through commercial information sources.
- **Luxembourg / GreyNet definition (§I), which they also quote.** Information produced at all
  levels of government, academia, business and industry, in electronic and print formats, not
  controlled by commercial publishing — the operative clause being "where publishing is not the
  primary activity of the producing body". They add that GL publications are volatile and lack
  bibliographic controls such as place and date of publication and author/publisher details.
- **"Fugitive literature" (§I).** GL is often called this because it is semi-published and hard to
  locate; these same traits make it hard to index and categorise.
- **Their own operational taxonomy of GL forms (§III-A-6, Table 9).** The text says GL was
  classified into **7 categories** but names six, each defined:
  - *Conference papers* — those **not indexed** in ScienceDirect, IEEE Xplore, ACM DL or
    SpringerLink are treated as GL.
  - *Technical reports* — research reports, internal progress and review reports, scientific
    reports.
  - *Theses/dissertations* — academic theses at undergraduate and postgraduate level.
  - *Workshop/seminar papers* — working papers from research groups and committees, typically
    presented at workshops and seminars.
  - *Guidelines/lecture notes* — includes company white papers and problem-solving guides.
  - *Preprints* — drafts not yet published in a peer-reviewed journal.
  [EXTRACTION UNCLEAR: the seventh category is not named in the extracted text; Table 9 itself is
  an image and did not extract.]
- **Origin taxonomy (§III-A-7, Table 10).** GL producers classified as: universities;
  international organizations; research institutes/labs/scientific societies; government
  organizations; others.
- They note the live debate over whether theses and dissertations should still count as GL at all,
  given that graduation involves a quality review process (citing Schöpfel and Rasuli).

### Process steps

Their own method (§II-A), a systematic mapping study following Kitchenham's guidelines, run as a
tertiary study:

1. **Three-phase search.** Phase 1 — search ACM DL, IEEE Xplore, ScienceDirect and SpringerLink.
   Phase 2 — scan the reference lists of everything found, then contact the authors who had
   written the most SLRs and scan their personal web pages. Phase 3 — use Google Scholar to catch
   anything missed.
2. **Search-string construction.** Identify alternate words and synonyms for the research-question
   terms; join synonyms with OR; join major terms with AND. Terms used: systematic review;
   systematic literature review; meta-analysis; empirical evidence; empirical studies; empirical
   study. Several queries pair these with "Kitchenham" or with "software engineering".
3. **Pilot-based search-string validation (a reusable technique).** A pilot set of **37 SLRs**, at
   least one per year 2004–2012, was assembled first — 22 taken from Kitchenham et al.'s tertiary
   study and 15 more obtained by contacting prominent authors. A candidate search term was
   **retained only if it recovered more than 90% of the pilot set**. This is a concrete,
   quantified stopping/acceptance rule for search-string design.
4. **Selection.** Inclusion: the paper is an SLR written to Kitchenham's guidelines; peer-reviewed;
   in English; published between January 2004 and June 2012 (2004 chosen because the SE SLR
   guidelines first appeared that year). Exclusion: full text unavailable; not SE; a shorter
   version of a similar paper; editorials, position papers, keynotes, tutorial summaries, panel
   discussions; reports of lessons learned, expert judgments, anecdotal reports and observations.
5. **Quality assessment deliberately skipped**, on the stated grounds that the inclusion criterion
   ("follows Kitchenham's guidelines") already implies reasonable quality and rigor, and that the
   research questions did not evaluate research outcomes. They concede assessment *would* be
   required if the mapping study were extended into a full SLR.
6. **Extraction.** A form capturing the SLR's full citation, its number of primary studies, and
   the **full citation of every primary study**. Where an SLR listed its primary studies that list
   was used; otherwise the full text was read to reconstruct it. For each primary study the source
   was then established (grey, or indexed where). SLRs were divided among authors and every
   extraction was **cross-checked by a different author**.

### Quality / credibility appraisal criteria

Yasin et al.'s contribution here is a proposed **GL quality checklist (Table 16)** together with
the motivation for each criterion. [EXTRACTION UNCLEAR: Table 16 is an image and its rows did not
extract; the paper's prose states only that the criteria are drawn from the authors' experience
searching GL during the study, that the list is explicitly incomplete, and that **its validity has
not yet been evaluated** — a planned future study. Use the checklist's existence and its self-
declared unvalidated status; do not attribute specific criteria to it without the original table.]

The surrounding argument is stated in prose (§IV-A): GL does not undergo rigorous peer review, so
its quality must be assessed against **a minimum number of preset criteria** rather than assumed.

### Search techniques and stopping rules

**Eight proposed GL categorisation/filtering strategies (§IV)** — presented as the paper's own
contribution, derived from the authors' experience during the study, each with its stated
weakness:

1. **Filter by page views** — a page's view count as a popularity proxy. Weaknesses: a new page
   cannot have a high count; high counts do not correlate with quality; the count is often
   unavailable.
2. **Filter by user comments** — comment counts on blogs, discussion boards and bulletins as an
   interest signal. Weakness: many comments are replies to other comments, not responses to the
   post.
3. **Number of citations** — heavy citation indicates importance. Operationalised as: include a
   highly cited source; a low-cited source warrants a full-text read to establish quality.
4. **Filter by GL type** — some types carry more evidence than others (conference proceedings
   versus a company brochure); literature from certain research labs may be reliably good. This is
   why they built the type taxonomy in Table 9.
5. **Filter by author** — in any SLR a few authors publish disproportionately; scan their web
   pages and their research groups' resources for GL.
6. **Filter by affiliation** — justified by their own finding that 67.7% of GL came from
   universities, research institutes, labs and scientific societies. Recommended as a *second*
   step after author-based filtering.
7. **Filter by research methodology** — exclude methodologies the RQ does not need (e.g. keep
   experimental evidence, drop surveys and case studies).
8. **Filter chronologically** — GL's speed advantage means date-sorting reveals trends and
   innovations early and exposes research gaps.

**Hybrid use is the explicit recommendation** — every strategy has drawbacks, so combine them. The
worked example given: (1) search the string/keyword; (2) categorise by GL type (conference
proceedings, thesis, reports, etc.); (3) categorise by number of hits or number of citations.

**Stopping rules:** none for GL search. The only quantified stopping/acceptance rule in the paper
is the >90% pilot-recovery threshold for search-term retention (above).

**Google Scholar as a search instrument (RQ2, §III-B).** Searching all 6,307 primary studies in
Google Scholar produced **6,026 hits and 281 misses — 95.5%, reported as 96%**. Per database:
ScienceDirect 3,383/3,573 (94.6%); IEEE 1,946/2,018 (96%); ACM 229/240 (~95%); SpringerLink
468/476 (~98%). Crucially, **38.4% of the studies Google Scholar could not find were grey
literature** — GL is exactly where a Scholar-only strategy fails. Many of the misses *were*
retrievable through plain Google; the residue found by neither were all conference and workshop
papers, either published before 2000 or from particular proceedings. The practical conclusion: the
**combination of Google Scholar and Google** maximises recovery, and Scholar alone is insufficient
precisely for grey sources.

### Caveats, traps and pitfalls

- **GL's volatility is the mechanism behind the search failures** — Yasin attribute Scholar's GL
  misses to GL being volatile, sometimes not published electronically, sometimes not published on
  the web at all.
- **Bibliographic control is often missing.** They observed a small percentage of GL with no
  date of write-up and no company name.
- **Classifying conference proceedings as GL is genuinely ambiguous** — they did not know the
  review policy of some conferences and had to assume that any proceedings not in the four major
  databases were grey. They name this as a threat and flag that a more detailed classification
  mechanism is needed.
- **Undated sources exist in the corpus** — 12 grey primary studies (~2%) gave no publication date.
- **Quality is not uniformly low.** They stress the counterweight, citing Osayande and Ukpebor:
  GL is often produced by scholars and scientists in their own fields and can be of high quality
  and detail. Its advantages are timeliness (available before commercially published literature —
  conference papers reach the public long before journal articles), focus, depth and currency.
- **The publication-bias argument.** Studies with positive results are more likely to end up as
  SLR primary studies than studies with negative results; scanning for GL, conference proceedings
  and unpublished results (including by contacting colleagues) is a named counter-strategy.
- **A cautionary example about unreviewed dissemination** (§I): a claim to predict human longevity
  from genes with 77% accuracy drew substantial online criticism within an hour of publication —
  used to illustrate that online circulation cuts both ways.

### Metadata requirements

Stated explicitly and minimally (§III-A-5), on the grounds that a GL source must be **traceable**:
a GL item should carry at least

- **name(s) of the author(s)**,
- **date of write-up**, and
- **name of the sponsoring company**.

They observed that GL produced by universities, international organizations and research
institutes/labs/scientific societies tends to have well-formed bibliographic details and to be
highly accessible — a usable heuristic for which sources will actually be citable later.

### Threats to validity framework

No named taxonomy; a single "Validity Threats" subsection (§V-A) organised by concern:

- **Search coverage** — only ACM DL, IEEE Xplore, ScienceDirect and SpringerLink were searched;
  Scopus and others were not. Partially defended by citing Hasteer et al. and Dybå et al. that
  these four cover the most relevant SE journals, conferences and workshop proceedings; they
  concede adding databases would increase validity. Mitigations already applied: piloting the
  search strategy on a small set, scanning reference lists, asking researchers about missed SLRs,
  and using Google Scholar as a third sweep.
- **Absence of quality assessment** — justified by the guideline-conformance inclusion criterion
  and by the descriptive nature of the RQs; acknowledged as necessary if extended to an SLR.
- **Extraction and synthesis reliability** — extraction was lengthy but not complex; where primary
  study lists were hard to reconstruct, two researchers compared outcomes and resolved
  differences; all extracted data was cross-checked by other researchers.
- **Classification validity** — the conference-proceedings-as-GL assumption (above), mitigated by
  the authors' SE domain knowledge.

### Empirical findings worth citing

Three explicitly defined indicators, worth reusing as measurement definitions:

- **Frequency of GL use** — the proportion of SLRs containing any GL, out of all SLRs examined.
- **Frequency of GL citing** — the proportion of primary studies that are GL, out of all primary
  studies examined.
- **Intensity of GL use** — the average number of grey primary studies per GL-using SLR, i.e.
  total grey primary studies divided by the number of SLRs that contain any.

Results over 138 SLRs and 6,307 primary studies:

- **Frequency of GL use: 76.09% (105 of 138 SLRs)** included at least one GL primary study.
- **Frequency of GL citing: 9.23% (582 of 6,307 primary studies)** were GL; the average across the
  four databases is given as **8.61%**. **4,920 (78%)** came from the four major databases.
- **Intensity of GL use: 5.54** grey primary studies per GL-using SLR (the abstract rounds this to
  "5 primary studies on average").
- Per-database GL share: ACM DL SLRs — 27 of 240 primary studies, **11.25%**; SpringerLink SLRs —
  23 of 476, **4.83%**; ScienceDirect SLRs (67 SLRs, 3,573 primary studies) had the **lowest** GL
  percentage of any source; IEEE Xplore SLRs numbered 48 with 2,018 primary studies.
- **Statistical comparison of sources.** Mean percentage of primary studies by source: IEEE Xplore
  33.97, ACM DL 15.96, ScienceDirect 14.65, SpringerLink 14.64, other journals/books 12.17. A
  **Kruskal-Wallis test** rejected equality of medians (**p = 0.004, α = 0.05**); a **Tukey-Kramer
  multiple-comparisons test (α = 0.05)** found only one significant pair — **IEEE Xplore differs
  significantly from GL**; no other pair of sources differed significantly.
- **Forms of GL cited** — conference papers are the most cited GL type, then technical reports,
  then theses/dissertations. Note an internal inconsistency: §III-A-6 gives **43% / 25.2% /
  12.4%**, while the abstract and conclusion give **43.3% for conference papers and 28.52% for
  technical reports**. The conclusion also states that conference proceedings and technical reports
  **together account for 68%** of GL. Cite the abstract's figures with the section discrepancy
  noted.
- **Origins** — universities plus research institutes/labs/scientific societies are the largest
  producers at **~68%** of grey primary studies (**67.7%** in the abstract), which is what motivates
  the affiliation-based search strategy above.
- **Recency** — about **48% (280)** of included grey primary studies were published within the
  preceding five years; **12 (~2%)** carried no publication date at all.
- **Overall characterisation:** despite GL's acknowledged importance, SE SLRs remain
  overwhelmingly built on published, peer-reviewed material — the level of grey evidence is around
  **9%**. Yasin contrast this with health and medical science, where including grey trials is
  treated as necessary to limit publication bias given the sensitivity of the topics.

---

## gul_2021 — Is grey literature really grey or a hidden glory to showcase the sleeping beauty

**Role in corpus:** A library-and-information-science narrative literature review (Emerald,
*Collection and Curation*) that assembles the *definitional history* of grey literature across
disciplines and catalogues the practical problems of collecting, describing, discovering and
preserving it. Its value to an SE methodology document is almost entirely upstream of SE: it
supplies the genealogy of the definitions SE papers cite second-hand, and it names the
infrastructure-level failure modes (metadata, indexing, regional bias, sustainability) that
explain *why* grey sources are hard to find and hard to keep.

Note on paper type: this is labelled "Literature review" and is **not** a systematic review. It
reports no protocol, no inclusion/exclusion criteria, no selection counts and no appraisal. Cite
it for definitions, history and problem taxonomy — not for prevalence evidence.

### Definition and classification of grey literature

Gul et al.'s contribution is the compilation; each definition below belongs to the cited source,
not to them.

**Definitions assembled, roughly chronologically:**

- **Origin of the label.** "Grey" connotes something gloomy, low-spirited and unattractive — a
  poor fit for any literature; the term stuck to author works and came to stand for any literature
  a library cannot easily access or subscribe to. Initially GL covered only scientific and
  technical reports from research and industry, often foreign (Auger 1989; Chillag 1993). Wood and
  Smith (1993) record that **dissertations were not part of the initial concept**, entering only
  as the concept and the acquisition infrastructure (notably SIGLE) expanded.
- **Nonconventional / semi-published** (Wood and Smith 1993) and **informal, running away,
  invisible, half-published** (Nahotko 2008) as near-synonyms. Nahotko also labels GL "the
  chameleon of information resources" because it can be almost anything, written for and by
  anyone, in almost any format.
- **Black literature** (Schöpfel 2019, p. 137) — a narrower shade: confidential and protected,
  open source in some sense and not classified.
- **Moahi (1995)** — material not commercially published and therefore absent from the normal
  channels of commercial publishing.
- **David Wood (via Magnuson 2009)**, one of the most-quoted formulations — literature "not
  readily available through normal bookselling channels", and therefore hard to identify and
  obtain.
- **Cesare and Sala (1995)** — documents outside conventional commercial distribution channels,
  hence difficult to identify and obtain.
- **Debachere via Auger (1989)** — a term used variably by the intelligence community, librarians,
  and medical and research professionals for material not easily found through conventional
  channels such as publishers, but which is frequently original and usually recent.
- **US Library of Congress Subject Headings** — reports, theses, conference papers, translations
  of limited circulation, and government documents.
- **Russian National Public Library for Science and Technology** — publications of limited
  circulation, operationalised as **fewer than 1,500 copies**, issued by minor publishing houses
  and hardly accessible. (Rare example of a *numeric* GL criterion.)
- **The "modern" definition, officially adopted at the 3rd International Conference on Grey
  Literature, 1997** (Siegel 2004, p. 62) — literature produced at all levels of government,
  academia, business and industry, in print and electronic formats, but not controlled by
  commercial publishers. Cassell (2005) gives the same wording. This is the definitional ancestor
  of the Luxembourg/GreyNet definition Yasin et al. use.
- **Schöpfel (2010)** — the same producer/format scope, with three added conditions: the documents
  are **protected by intellectual property rights**, are **of sufficient quality to be collected
  and preserved** by library holdings or institutional repositories, and are **not controlled by
  commercial publishers**. This is the version that builds a quality floor into the definition.
- **ODLIS (Online Dictionary for Library and Information Science)** — documentary material in
  print and electronic formats: reports, preprints, internal documents (memoranda, newsletters,
  market surveys), theses and dissertations, conference proceedings, technical specifications and
  standards, trade literature — not readily available through regular market channels because it
  was never commercially published or listed, or was not widely distributed.
- **Gul et al.'s own reading:** the disagreement among authorities does not matter much, because
  the **core traits are constant — limited availability and difficulty of obtaining**. They locate
  GL under the broader concept of **"ephemera"**: material carrying a verbal or illustrative
  process but not in standard book, pamphlet or periodical format (Makepeace 1985).

**Classification models presented:**

- **Shades of grey (Figure 1)** — Adams et al. (2016), reproduced via Garousi et al. (2019, p.
  103); the same diagram that underpins the SE tier model. [EXTRACTION UNCLEAR: Figure 1 is an
  image; the extracted text carries only the caption "Shades of 'grey literature'", not the tier
  labels.]
- **Schöpfel's four structural components (Figure 2, Schöpfel 2019, p. 140)** — GL is produced at
  the intersection of four positions, laid out on two axes: **research** (upside) and
  **professional** (downside), **academic** (left) and **extra-academic** (right). Gul et al. use
  this to argue that a researcher should not sort GL along scientific/non-scientific lines but see
  it as the joint contribution of these four kinds of player.
- **Scientific vs non-scientific axis.** GL can be either. Institutional repositories are the
  storehouse of *scholarly* grey literature; governmental and special repositories hold large
  quantities of *non-scholarly* GL (OpenDOAR 2019). Crucially, falling in the non-scientific
  category "does not make the works less authentic and unreliable" — Gul cite US federal legal
  grey resources with clear scientific character (expert reports, environmental impact statements
  and assessments under the National Environmental Policy Act; permits under the Clean Air Act,
  Clean Water Act and Endangered Species Act; inspection reports under the Occupational Health and
  Safety Act), and note that NGO survey reports are often vetted by experts.
- **Enumerated type list (Okoroma 2011)** — faculty research works; theses and dissertations;
  seminars and workshops; conferences; students' projects; reports of meetings; in-house
  publications of associations and organisations; white papers produced by businesses; and all
  forms of government publication including budgets, legislative materials and development plans.
- **Electronic GL forms** — websites, weblogs, electronic pre-prints and other online publications
  in formats such as PDF and HTML, plus discussion boards (de Blaaij 2004; Malina and Nutt 2000;
  Mathews 2004). Davis-Castro (2019) goes further and treats **social media as a reflection of
  grey literature**.

**Historical timeline (its own section), useful for framing:**

- The term has been debated and redefined since around the 1920s (Rucinski 2015); existence of
  such literature is traceable in German-speaking countries as far back as **1920** (Kargbo 2005).
- Widely recognised across Europe — German *graue Literatur*, Italian *letteratura grigia*, French
  *littérature grise* (Auger 1996). [The extracted German term is garbled in the source text.]
- The term **first appeared in scientific publications in the 1970s** (Bogdanski and Chang 2005).
- UK starting point: a **seminar at York, December 1978**, organised by the EEC with the British
  Library, which led to the **SIGLE** database, primarily EEC-supported.
- Attention grew after a *Financial Times* headline, "Grey Literature Comes in from the Cold"
  (Auger 1982).
- The term was **not formally coined until the second edition of *Information Sources in Grey
  Literature*, 1989** (Gelfand and Lin 2019).
- **1996** — Virginia Tech creates the Networked Digital Library of Theses and Dissertations
  (NDLTD).
- **1997** — modern definition adopted at the 3rd International Conference on Grey Literature.
- **2004** — 6th International Conference on Grey Literature, New York Academy of Medicine (6–7
  December), where the keynote addressed GL's transformation by electronic information trends, and
  where a Boekhorst/Farace survey found GL policy provisions unpromising.

### Process steps

Gul et al. describe their own literature-gathering method only (Design/methodology/approach) —
there is no proposed procedure for others to follow. Their method, at the level of detail given:

1. Search three indexing/abstracting services: **Web of Science, SciVerse Scopus, Google
   Scholar**.
2. Use a broad keyword set covering the concept, its institutions and its adjacent topics: grey
   literature; black literature; The Grey Journal; The International Journal on Grey Literature;
   International Conference on Grey Literature; non-conventional literature; semi-published
   literature; SIGLE; EAGLE (European Association for the Exploitation of Grey Literature); white
   literature; white papers; theses and dissertations; GreyNet; grey literature-electronic media;
   grey market; open access; OpenNet; open access repositories; institutional repositories; open
   archives; electronic theses and dissertations; institutional libraries; scholarly
   communication; access to knowledge; metadata standards for grey literature; metadata
   heterogeneity; disciplinary grey literature.
3. Use both **simple and advanced search** features of each database.
4. Use the databases' **"citing articles" feature** to pull more recent and updated work — a
   forward-snowballing step — selecting citing articles **on the basis of relevance to the subject
   content**.

That is the whole protocol; no screening counts, no criteria, no appraisal step.

### Quality / credibility appraisal criteria

Gul et al. propose no instrument. What they contribute is the **argument structure** for and
against trusting GL, which is directly reusable when writing an appraisal rationale:

*Against:*
- Quality is "one of the main issues with the grey literature" (Smart 2015, reporting the
  Editor-in-Chief of *Learned Publishing*).
- The majority of GL is not peer reviewed and has limited referencing of information (Bogdanski
  and Chang 2005, p. 56).
- Researchers are hesitant to include GL because they are unsure of its quality (Adams et al.
  2016); a number of misconceptions about GL quality and credibility persist in the literature.
- GL produced by governmental, corporate, NGO and union bodies is often *tagged* as research
  output, but its political, business or administrative nature means it may lack scientific
  integrity and scientific ambition; peer review and editorial process are frequently absent
  (Schöpfel and Rasuli 2018). Even scholarly works hosted on institutional repositories are not
  always the result of validated and authenticated research (Börjesson 2016).

*For:*
- **Some GL forms do undergo rigorous peer review** — Schöpfel (2019, p. 148) names review by
  scientific committees (conferences), by juries (theses and dissertations), and by institutions
  or peers (reports, working papers).
- ETDs are reviewed and evaluated by teams of subject experts, so acceptable quality may be
  assumed, especially at PhD level (Larivière et al. 2008); an ETD embodies at least **three
  years** of scientific work within a laboratory, research team, institute, school or company
  (Schöpfel et al. 2014).
- **The no-publication-pressure argument** (Adams et al. 2016) — high-quality work is published
  outside the white literature by people not under pressure to publish in academic journals, and
  the absence of that pressure can raise content quality.
- **The public-scrutiny argument** (Wolfert et al. 2017, p. 77) — GL findings may lack the
  scientific rigour expected of peer-reviewed articles, but because GL articles are publicly
  available they are subject to public scrutiny and can therefore be regarded as reasonably
  reliable.
- **Management-of-GL argument** (Schöpfel 2015) — GL management is a good indicator precisely
  because it is not driven by commercial publishing's financial interests.

*Procedural suggestions offered:*
- **Third-party expert intervention** — subject experts can be taken into confidence both before
  librarians provide access and before the user community accepts a grey item (Farace 2011).
- Apply existing **evaluative parameters for traditional and electronic sources** to validate GL
  authenticity (Enticott et al. 2017; Higgins and Green 2011 — i.e. the Cochrane handbook).

They also relay Garousi et al.'s (2019) framing of the **multivocal literature review** as a form
of systematic literature review that includes grey literature such as blog posts, videos and white
papers, valuable to researchers and practitioners alike because it summarises both the state of
the art and the state of practice.

### Search techniques and stopping rules

No search protocol or stopping rule is proposed. What the paper contributes is a map of **where GL
actually lives**, which is the practical input to designing a grey search:

- **Open access repositories (OARs)** as the modern GL channel. Pinfield et al.'s (2014)
  repository typology: **institutional** (run by academic or research institutions),
  **disciplinary** (formed by subject communities), **aggregating** (harvested from other
  sources), and **governmental** (run by national governments and government-sponsored agencies).
- **Disciplinary repositories specialising in GL** (Marsolek et al. 2018): arXiv (physics, maths,
  computer science), PhilSci Archive (philosophy of science), AgEcon Search (agricultural and
  applied economics).
- **OpenGrey**, the OA-era successor concept to SIGLE, arising from the OA publishing movement
  (Gelfand 2006).
- **National ETD platforms** — Digital Australian Theses via Trove (Australia), Theses Canada,
  EThOS (UK), Theses.fr (France), IranDoc ETDs (Iran), National Thesis Center (Turkey), Brazilian
  Digital Library of Theses and Dissertations, ETD Portal (South Africa), NARCIS (Netherlands),
  CALIS ETD (China), Digital Dissertation Library of the Russian State Library, Theses and
  Dissertations in Spain, NDLTD Taiwan, doiSerbiaPhD (Serbia), eLABa ETD (Lithuania), Shodhganga
  (India, via INFLIBNET).
- **Commercial channels now carry GL too** — Web of Science, SciVerse Scopus, ScienceDirect, EBSCO
  Host and others have added refinement options for accessing grey literature in their search
  interfaces (Bonato 2016; Marsolek et al. 2018). ProQuest Dissertations and Theses is singled out
  for scholarly theses; commercial vendors in Italy and Spain collect and sell dissertations at
  national level.
- **Acquisition routes for institutions** (Auger 1998, p. 30) — exchange agreements with other
  organisations, and purchases by subscription or single-item order.
- Scientific and technical information centres place special emphasis on GL and hold important
  grey collections, especially of **conference proceedings, technical reports and dissertations**
  (Boukacem-Zeghmouri and Schöpfel 2006).

### Caveats, traps and pitfalls

Gul et al.'s "issues, challenges and possibilities" section is effectively a named taxonomy of GL
failure modes. Reproduced with their headings:

1. **Collection development and organisation** — many information professionals avoid integrating
   GL into collections (Okoroma 2011); collecting it is a major challenge for libraries (Luzi
   2000). Root causes named by Debachere (1995) and Auger (1989): poor organisation, dissemination
   and exploitation; limited print runs; poor publicity; poor bibliographic control; flimsy or
   insubstantial materials; transience; availability contingent on where, by whom, for what
   purpose and where produced; and acquisition/storage burden. Corporate libraries hold less GL
   than academic and government libraries.
2. **Organisation (classification and cataloguing)** — GL is time-consuming to find and catalogue,
   is not distributed through established channels, and **does not fall into standardised
   categories of document classification** (Lawrence et al. 2015, p. 231). The subject diversity
   makes "where to shelve what" and "where to find what" genuinely hard. Special libraries hold
   large uncatalogued GL holdings with no title-level access. Digital GL adds a curation and
   preservation problem, flagged by both the UK Finch review (2012) and the US Blue Ribbon Task
   Force on digital preservation (2010).
3. **Metadata, indexing and retrieval** — see the dedicated section below.
4. **Discoverability** — GL's difficulty of acquisition means it often requires **special
   collection teams and collecting policies** (Lawrence et al. 2015, p. 231). Counterweight: the
   internet, IRs and organisational/government websites now give free instant access to much
   organisational GL (Tillett and Newbold 2006, p. 72).
5. **Unorganised format and poorly structured components** — in both print and electronic form,
   with poor structure directly causing poor and untimely accessibility. Suggested remedy is
   mundane: adopt standard structural conventions (page numbers, contents page, index page) for
   sequential structuring and clearer content visibility.
6. **Content validity** — the mistrust problem, argued out above.
7. **Subject bias** — databases covering GL are frequently subject-specific (Okoroma 2011). SIGLE,
   produced by EAGLE, was an attempt to address this but has limited centres. Multidisciplinary
   OARs have largely tackled the problem.
8. **Regional bias** — GL is more indigenous in character; geographical boundaries restrict access
   so that GL is at times effectively **"region specific literature"**. Technology (NDLTD, national
   ETD platforms) has eroded but not eliminated this.
9. **Non-availability in indexing/abstracting databases** — GL falls outside traditional indexing
   and abstracting and is usually produced locally; it is largely absent from bibliographic
   databases and from most national bibliographies (Sturges and Neil 1990, via Okoroma 2011).
   Proposed remedy: aggregate into globally accessible databases discoverable through
   international catalogues.
10. **Less knowledge and lack of awareness** — the ambiguous, vague definition itself hinders
    collection and access; users struggle to search for GL because the diversity of what counts as
    grey is itself the obstacle (Aloia and Naughton 2017). Remedy proposed: LIS curricula and
    training (Farace and Schöpfel 2010, p. 6).
11. **Legal and copyright issues** — GL may carry legal implications and privacy exposure since it
    originates in organisations and public platforms. Copeland et al. (2017) raise data-ownership
    tensions and the copyrightability of official records (proceedings, minutes) and data. Farace
    and Schöpfel (2010, p. 6) note that all restrictions, exceptions and technical constraints of
    new IP, authors' rights and copyright law — including DRM and interoperability constraints —
    **apply to grey resources too**. Lipinski frames information policy relating to copyright in a
    grey context.
12. **Differentiation from white literature is eroding** — mainstream providers now offer full-text
    GL, and Banks (2005, 2006) argues this creates a non-distinction between grey and non-grey
    content. Gul et al.'s own position is that metadata is what still draws the boundary line.
13. **Sustainability in the electronic domain** — repository-hosted GL depends on continuous IT
    expertise and financial capital; multiple studies raise concerns about repositories'
    operational status. Farace and Schöpfel (2010, p. 6) state the unresolved question bluntly:
    **who should archive what, where, when and for how long** remains largely unanswered. This is
    the LIS-side statement of the same problem Kamei measured as link rot.
14. **The greyness of ETDs is unsettled** — Schöpfel and Rasuli (2018) hold that greyness remains a
    challenge for ETDs, a problem awaiting solution on the road to open science through the
    **FAIR principles (findability, accessibility, interoperability, reusability)**.

### Metadata requirements

This is the section where Gul et al. are most directly useful to a methodology document, because
they state *why* GL metadata is unreliable and *what* to do about it.

**Why GL metadata fails — Childress and Jul (2003), six recurring problems:**

- little or no embedded metadata;
- no formally presented metadata (e.g. no title page);
- conflicted or suspect metadata (e.g. multiple and/or suspect dates);
- unfamiliar or obscured responsible parties (e.g. author's initials only, acronyms only);
- content that is interdisciplinary, highly specialised, or on topics too new or too different to
  admit easy subject access;
- probably not listed in familiar bibliographies or in indexing and abstracting services.

Because GL is not controlled by commercial publishers, there is no consistency or standard in its
metadata elements; and indexes designed for non-grey literature do not fit, because they assume a
formal metadata description.

**What to do about it:**

- Use existing standards, deliberately and in combination. Named: **Dublin Core**, Encoded
  Archival Description, Metadata Encoding and Transmission Standard, Metadata Object Description
  Schema, Categories for the Description of Works of Art Lite, Visual Resources Association Core,
  Public Broadcasting Metadata Dictionary, Government Information Locator System, and the Federal
  Geographic Data Committee Content Standards for Digital Geospatial Metadata. For ETDs
  specifically, **ETD-MS** is the worldwide interoperability standard.
- Accept a **mixed metadata environment**. Chapman et al. (2009, p. 309) name three sourcing
  strategies that coexist: metadata converted from other systems; metadata elicited from the
  document creator or manager; and metadata created by library or repository staff. Aggregating
  heterogeneous metadata is what makes a grey item indexable and retrievable at all.
- **Marsolek et al.'s (2018) recommendation**, quoted in substance: develop **consistent metadata
  standards for grey literature** to improve searching within individual resources and to support
  future interoperability, and include **descriptions rich enough to identify and locate** the
  item. As repository interoperability grows, those seeking GL benefit from **common terminology
  and enhanced description**.
- The minimum user requirement (Vickers and Wood 1982, p. 125): a potential user of literature,
  grey or white, needs to know **what has been written, where it has been published, and in what
  form**.

### Threats to validity framework

None. This is a narrative review and offers no validity taxonomy. The paper's own
"Research limitations/implications" statement is confined to two points:

- the study rests on published literature indexed by **only three databases** (Web of Science,
  SciVerse Scopus, Google Scholar); and
- **only some aspects** of grey literature are covered.

For a methodology document, treat this as an illustration of what a non-systematic review does
*not* provide — no protocol, no screening record, no appraisal, no reliability check, and
therefore no basis for a coverage or reproducibility claim.

### Empirical findings worth citing

Gul et al. report no primary data; every figure below is relayed from a cited source, and should
be attributed accordingly.

- **The file-drawer mechanism, quantified (Floyd et al. 2011):** the lag between article acceptance
  and publication in many scholarly journals ranges from **2 to 11 months**, and rejection rates
  for submitted manuscripts range from **31% to 88%**. This is the concrete basis for the claim
  that a large volume of important research never reaches its audience through white channels —
  the "file-drawer" effect (Conn et al. 2003; Dickersin 1990; Helmer 1999).
- **Botswana (Aina 1992):** across a three-year period, **98%** of the literature produced showed
  grey characteristics — cited as evidence that in some national contexts GL *is* the literature.
- **Australia (Lawrence et al. 2015, pp. 236–237):** **30,000 organisations** produce grey
  literature, spending **$234m per annum** on projects that generate it; approximately **3.8
  million people** may be GL users; and the estimated **use value is $33–43 billion per annum**.
  Lawrence et al. also find GL to be "a key method used by surveyed organisations across all
  sectors" for translating and disseminating new research or policy positions.
- **Open access raises GL's uptake:** Ferreras-Fernández et al. (2016) find that OA institutional
  repositories are an advantageous channel for grey literature such as dissertations and PhD
  theses, because openness increases visibility and use and produces a significant citation rate.
- **Domain examples of GL carrying decisive evidence**, each attributed: GL influences policymaking
  in marine sciences (Cossarini et al. 2014); GL is a key component of the information geoscientists
  use (Bichteler 1991); reviews of GL supported implementing managed alcohol programmes in
  hospital settings (Brooks et al. 2018) and play streets for safe active play (Bridges et al.
  2019); GL gave insight into traumatic stress and grief among families bereaved on 9/11 (Bauwens
  2017); GL is an important outlet for women's writing and an alternative publication route for
  underrepresented views (Magnuson 2009; Aina 2000; Malina and Nutt 2000); Padgett (2008) holds
  that GL-based investigation provides depth and breadth in areas where little research exists;
  Claeys et al. (2013) note GL provides access to information absent from sources dealing largely
  with high-methodological-quality studies; Paez (2017) confirms GL's role in systematic reviews
  and meta-analysis, where it can give more focused answers, aid critical appraisal, avoid bias and
  support decision-making.

---

## schopfel_2021 — How scientific papers mention grey literature: a scientometric study based on Scopus data

**Role in corpus:** Schöpfel and Prost (the authors of the canonical LIS definitions themselves)
measure how the *rest of science* actually uses the term — 8,853 Scopus papers over 1999–2018,
with a content analysis of 70 open-access 2018 papers. It is the cross-disciplinary counterpart to
Kamei's SE-specific audit, and it reaches the same core verdict independently: authors describe
grey literature by negation rather than defining it. It also supplies the disciplinary context SE
lacks — that grey search is *mandated* in medicine by PRISMA and Cochrane.

### Definition and classification of grey literature

**The two canonical GreyNet definitions, both stated in the paper:**

- **New York definition** (promoted by GreyNet International, launched 1992; see Schöpfel and
  Farace 2010) — grey literature is produced at all levels of government, academia, business and
  industry, in print and electronic formats, but is not controlled by commercial publishers; the
  qualifying clause is "where publishing is not the primary activity of the producing body".
- **Prague definition** (Schöpfel 2011), the updated version — the same scope, adding three
  qualifiers: the document types are **protected by intellectual property rights**, are **of
  sufficient quality to be collected and preserved** by library holdings or institutional
  repositories, and are still **not controlled by commercial publishers**, with the same
  publishing-is-not-the-primary-activity clause. This is the definition Gul et al. attribute to
  "Schöpfel (2010)"; the two are the same lineage.

**Their empirical finding about definitions is the important part.** Outside the small expert
community, the meaning of GL is widely unknown or misunderstood; the concept is applied and
interpreted with great diversity, sometimes with rather simplistic ideas of what it covers. The
concept was created and promoted by information professionals — especially acquisition librarians
in scientific and technical information (Auger 1989) and people in scientific or economic
intelligence — while many researchers work with theses, reports and working papers apparently
without knowing the concept exists at all (Prost and Schöpfel 2014).

**What the sampled papers actually do (content analysis of 70 open-access 2018 papers):**

- **Only 5 of the 70** supply an explicit definition — typically the New York definition or the
  older Auger (1989) definition.
- The rest give **descriptive attributes or a negative definition by exclusion**, leaving the
  reader to guess what is and is not grey. Schöpfel and Prost make the methodological point
  sharply: negative definitions say only roughly what GL is *not*.
- The **dominant attributes are "unpublished" and "not peer reviewed"** — and "not peer reviewed"
  generally carries the implication of doubtful quality. A third recurring attribute is "not in
  databases".
- Other descriptors found in the corpus: ephemeral, with internal dissemination; difficult to
  locate if they have survived; inconsistent; unconfirmed; without statistically significant
  findings; ongoing studies; time-consuming to search (Bramer et al. 2018); and, at the opposite
  extreme, simply "publicly accessible Internet resources".
- Frequently GL is defined operationally as documents **not in bibliographic electronic
  databases** — specifically not in Scopus, Web of Science or Medline — hence "a complement to
  databases", "not in journals", or bluntly "not articles". One paper opposes grey literature to
  scientific literature, as though grey implied non-scientific.

**Types actually meant, from the same content analysis** — this is a useful empirical type list,
ordered by how often it appeared:

*Commonly meant (reports and conference material):* published reports; technical reports;
governmental and institutional reports; official police or medical expert reports; policy papers
(strategy); conference proceedings; meeting papers; presentations.

*Less often mentioned:* white papers; conference abstracts; posters; theses and dissertations;
fact sheets; standards; technical notes; guidelines; guidance notes.

*Edge cases some authors still counted as grey:* primary material; unpublished observational
studies and clinical trials; opinion pieces; editorials; letters to the editor; blogs; a forum;
"research objects"; a governmental gazette.

**Prescriptive minimum from prior work they endorse (Carlson et al. 2017):** any resource intended
to inform people about grey literature — their example is library LibGuides — should carry at
least a **reference definition**, a **typology of grey items**, and **resources and tools for
discovery and retrieval**. That triple is a serviceable checklist for the "grey literature" section
of any review protocol.

### Process steps

Their own scientometric method (Methodology section), reproducible as a template for a
term-usage study:

1. **Query:** `"grey literature" OR "gray literature"` in Scopus **All fields** — covering
   metadata (title, keywords, abstract) *and* full text — restricted to the 20 years 1999–2018.
   Corpus exported 7 October 2019; analysis in MS Excel.
2. **Scientometric variables**, computed with Scopus's own discovery tools: for the whole period,
   number of publications per year; for 2018 only, authors, affiliations, countries, document
   type, source title, source type, subject.
3. **Content analysis:** restricted to freely available (open access) items, a **random sample of
   70** (stated as 10%). The four assessed criteria were: **cited definitions (references);
   semantics (description, characteristics, examples); types; sources.**

**The GL-search options their corpus actually used — five categories** (from the sampled papers'
methodology sections). This is the paper's most directly reusable output:

1. **General or academic search engines** — Google Search (advanced), Google Scholar.
2. **Specialised databases and digital libraries.** International: SIGLE (discontinued), OpenGrey,
   DissOnline.de, ProQuest Dissertations and Theses. Domain: PubMed, Cochrane Library, LILACS
   (Latin American and Caribbean Health Sciences Literature), Scopus. Institutional: e.g. the
   Digital Library of the Federal University of Minas Gerais. National discovery tools: the CAPES
   thesis and dissertation bank and the Brazilian Digital Library of Theses and Dissertations.
   Disciplinary servers: governmental and international trial registers, the AIDSFree Resource
   Library, the USAID Development Experience Clearinghouse. Several studies named the New York
   Academy of Medicine's **Grey Literature Report** as a valuable medical GL source (since
   discontinued — the only widely known GL alert service, and it no longer exists).
3. **Reference screening** — handsearch or snowballing through the bibliographies of included
   studies and of relevant systematic reviews.
4. **Relevant websites** — manual search of institutional sites, explicitly dependent on the
   authors' own expertise about which organisations matter, or failing that on expert advice.
   Examples in the corpus: WHO, World Bank, Joseph Rowntree Foundation, Age UK, Alzheimer's
   Association, InterGen, Manchester Institute for Collaborative Research on Ageing, the Andalusian
   Health Service, BioBran Research Foundation.
5. **Experts** — contacting key experts, authors of potentially relevant conference proceedings,
   the most productive researchers in the field, or key organisations, in order to identify grey
   items and learn of ongoing or unpublished research.

### Quality / credibility appraisal criteria

Schöpfel and Prost propose no appraisal instrument. Their contribution here is diagnostic: they
show that **"not peer reviewed" is doing the work of an appraisal criterion** across the
literature, functioning as a proxy for untrustworthiness rather than as a prompt to appraise.

- They record the latent suspicion directly: papers routinely distinguish journal articles indexed
  in bibliographic databases (trustworthy because peer reviewed) from other documents needing more
  attention, care and control — and conclude the effort is too time-consuming for an uncertain
  result. That calculation, they argue, is itself a reason authors invest no effort in
  understanding grey literature properly.
- They quote a corpus paper conceding both sides at once: access, quality and heterogeneity of
  grey literature are "stumbling blocks to its inclusion in a systematic review" — yet the same
  paper admits that excluding grey literature was a limitation of the review.
- **The counterexamples matter for balance.** One sampled paper reports that publication bias
  across studies was minimised by including grey literature and consulting experts. Baines and
  Regan de Bere (2018) included grey literature on the grounds that it helps validate published
  literature searches, identifies the most up-to-date information, and answers the criticism that
  existing literature operates in silos — grey sources often carry the newest information from
  people working on the ground and so present alternative perceptions to the peer-reviewed
  literature. Here GL is treated as a **bias-reducing** instrument rather than a bias risk.
- The two positions are irreconcilable without appraisal criteria, which is exactly the gap this
  paper documents.

### Search techniques and stopping rules

Beyond the five source categories above:

- **The Google problem (Piasecki et al. 2018), which they highlight as a warning.** Two named
  defects: the **lack of transparency of Google's search algorithms**, and the **bias induced by
  personalised search**. Their stated consequence is the serious one — **uncontrolled
  personalisation risks non-replicable systematic reviews**. This is the citation to use when
  arguing that a Google-based grey search must be documented (date, locale, logged-out/incognito
  state) or it cannot be reproduced.
- **Mandated grey search in medicine.** PRISMA (Moher et al. 2009) makes searching for grey
  literature a **mandatory** part of the systematic review procedure. Cochrane's methodological
  expectations (MECIR; Higgins et al. 2019) treat searching grey sources — explicitly naming
  reports/dissertations/theses databases and databases of conference abstracts — as **"highly
  desirable"**, in order to reduce the risk of publication bias and identify as much relevant
  evidence as possible.
- **Effort is the recurring theme, and no stopping rule is offered.** They quote Haddaway et al.
  (2015) that considerable effort is typically required within systematic reviews to search for
  grey literature, and conclude that grey search still requires **time, domain-specific knowledge
  and networking**. Their closing structural observation is worth carrying into any methodology
  document: the digital transformation of the research environment has **shifted the effort from
  the library to the scientist** — description, dissemination and conservation as well as
  discovery and retrieval are now the researcher's burden.

### Caveats, traps and pitfalls

- **Negative definition is the norm, not the exception.** With 5 of 70 papers defining the term,
  most reviews leave readers unable to determine what was included. This directly undermines
  replicability of the selection step.
- **Non-replicability through personalised search** (above).
- **Grey yield is often near zero, and reviewers should expect that.** See the metrics below; the
  practical trap is spending large effort on a channel that contributes almost nothing to the final
  evidence set — while, in other reviews, grey material is half the retrieved corpus. The variance
  is enormous and the paper offers no predictor for which case a given review will be in.
- **Key infrastructure is disappearing.** SIGLE is discontinued; the New York Academy of Medicine's
  Grey Literature Report — described as the only widely known GL alert service — is discontinued.
  A protocol that names a grey database must verify it still exists.
- **The disciplinary blind spot.** Medical and life sciences appear to be the only large field
  where grey literature is an explicit and even core element of scientific methodology. Schöpfel
  and Prost argue the near-absence of GL discourse elsewhere is **not** a deficit of grey resources
  in social sciences, humanities, physics, chemistry, mathematics, informatics or agriculture, but
  a **lack of awareness of the concept**. (They note a soil-science counterexample: Augusto et al.
  2010.)
- **Why researchers do not engage with the concept** — three reasons they advance: (i) the
  definition is a product of LIS professional experience and research, with limited penetration
  into researchers' practice, much as researchers use catalogue formats and metadata without ever
  naming them; (ii) grey literature matters less than journal and book publishing for academic
  assessment and ranking, so precision about it carries no reward; (iii) the equation of
  "not peer reviewed" with untrustworthiness makes the effort look unprofitable.
- **The historical prediction that failed.** Twenty years earlier some argued the web would make
  dissertations, reports and working papers so findable that the concept of grey literature would
  become meaningless (Schöpfel 2006). The Scopus data refutes this: the concept is in use more than
  before.

### Metadata requirements

No metadata specification is given for individual grey items. The paper's relevant contribution is
the **Carlson et al. (2017) minimum triple** — reference definition, typology of grey items,
discovery/retrieval resources and tools — and its closing observation that responsibility for
**description, dissemination and conservation** of grey literature has moved from the library to
the individual scientist. Read alongside Kamei's link-rot findings and Gul's metadata chapter, the
implication for a review protocol is that the reviewer must now do the librarian's descriptive job
themselves.

### Threats to validity framework

No named taxonomy; a single "Limitation" subsection stating a **systematic bias** with three named
directions and three named exclusions:

- Restriction to Scopus — the largest academic scientometric database worldwide, but one that
  biases the sample **in favour of journal articles, of research published in English, and of
  medical and life sciences**.
- Consequently the study **neglects** non-English papers, reports, dissertations and unpublished
  conference papers.
- And it **underestimates** scientific production in the social sciences and humanities.
- Self-aware irony worth noting: a study of grey literature that can only see the white-literature
  index. The limitation is structural to the instrument, not correctable within the design.

### Empirical findings worth citing

**Volume and trend (Scopus, 1999–2018):**

- **8,853 publications** mention grey (or gray) literature across the twenty years.
- Growth from **26 papers (1999) to 1,606 papers (2018)**, an **average annual increase of 28%** —
  well above the Scopus database's own average annual growth of **5%**.
- Share of all Scopus output for the period: **0.02%** (against a denominator of **45,059,595**
  publications). Rising from **0.01% or less before 2010 to 0.05% in 2018** — i.e. in 2018 **one
  academic paper in 2,000** contained the term. Schöpfel and Prost call this too low for a concept
  meant to characterise a significant part of scientific publishing.

**Composition of the 2018 corpus (n = 1,606):**

- **95%** published in academic journals — **articles 46%**, **reviews 44%**; **4%** conference
  papers in proceedings; **1%** book chapters. The dominant document type is the systematic review.
- **704 papers (44%)** are open access.
- Authors from **113 countries**. **United Kingdom, USA and Canada together account for half** of
  the items; adding Australia, Brazil, Italy, Germany, the Netherlands, France, Switzerland, Spain
  and China reaches **80%**. Nearly all papers are in English.
- Long tail of institutions; the ten highest-ranked are mainly Canadian and Australian —
  University of Toronto, University of Alberta, McMaster University, University of Oxford,
  University of Ottawa, University of Queensland, Monash University, University of Calgary,
  University of Sydney, University of Melbourne.
- **Fields: 80% medical science and health** (including nursing, pharmacology, dentistry and
  veterinary); **30%** social sciences, humanities, arts or economics; **29%** natural sciences and
  mathematics; **9%** engineering sciences. (Categories overlap, so the percentages exceed 100.)
- Leading journals are medical and life-science titles — BMJ Open, PLoS One, Cochrane Database of
  Systematic Reviews, Systematic Reviews, BMC Public Health, BMC Health Services Research,
  Medicine — but the top ten also include **The Grey Journal** and the **International Conference
  Series on Grey Literature** (both Textrelease Amsterdam, affiliated with GreyNet), and
  **Environmental Evidence**.

**Definition practice (n = 70 open-access papers):**

- **Only 5 of 70 (about 7%)** give an explicit definition of grey literature. The rest rely on
  attributes or negation.

**How much grey literature a review actually keeps — the yield figures:**

- Where systematic reviews report search statistics, grey literature is typically **between 0.1%
  and 1%** of retrieved items.
- But in other studies grey literature accounts for **nearly half** of the retrieved items — for
  example 3,000 or more references.
- **Attrition after screening is severe.** One study retrieved **52 grey documents and used only
  4**. Other systematic reviews appear to **retain none** of the grey documents they retrieved.
- Read against Kamei's SE figure (75.4% of GL-using secondary studies used GL to answer at least
  one RQ) and Yasin's (9.23% of primary studies were grey), this is the cross-disciplinary
  counterpart: high search cost, highly variable retrieval, and frequently near-zero contribution
  to the final synthesis.
