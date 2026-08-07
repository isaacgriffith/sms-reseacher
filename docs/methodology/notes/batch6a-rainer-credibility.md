# Batch 6a — Rainer & Williams on the credibility of blog-like and practitioner-generated content

Extraction notes for the methodology reference document. Three papers:
`rainer_using_2019`, `rainer_heuristics_2019`, `rainer_using_2017`.
All prose below is paraphrase unless enclosed in quotation marks.

---

## rainer_using_2019 — Using blog-like documents to investigate software practice: benefits, challenges, and research directions

Rainer, A. and Williams, A. (2019), *Journal of Software: Evolution and Process*, 31(11):e2197.

**Role in corpus:** The definitional and agenda-setting paper — it supplies a ten-feature
reference definition of the "blog-like document", an organised inventory of five benefits and
fourteen challenges, and an explicit diagnosis that no adequate credibility-assessment framework
for this material yet exists, which is exactly the gap the other two papers begin to fill.

### Definition and scope

The authors deliberately coin **blog-like document** rather than "blog post", because the blog post
resists formal definition (Section 1). Their reference definition (Table 1) is presented as ten
*typical* features, not a set of necessary conditions, and is explicitly offered as a template other
researchers should adapt to their own research questions rather than adopt verbatim:

| No. | A blog-like document typically… |
| --- | --- |
| 1 | is publicly accessible |
| 2 | has an identifiable author who is an identifiable software practitioner |
| 3 | is primarily written content (English assumed for pragmatic reasons), possibly with images, video, and outbound URLs |
| 4 | contains personally written, professionally oriented content |
| 5 | is published at an online location, i.e. as a web page |
| 6 | has content on a topic concerning software engineering and its practice |
| 7 | is published relatively frequently, typically in reverse chronological order |
| 8 | is capable of being revised in response to ongoing reader feedback |
| 9 | is published with a clear date of publication |
| 10 | supports comments and other reader feedback such as upvotes |

Two design intentions are stated for the definition (Section 2.1): it should exclude unsuitable
documents — those irrelevant by topic, or of unknown origin such as unknown authorship — and it is
expected to be *complemented* by a quality-assessment framework still to be developed and by an
appropriate research method (an MLR or a case survey). The definition alone is therefore not a
credibility filter; features 2, 9 and 6 are the ones that do exclusionary work.

**Scope boundaries.** The review deliberately excludes microblogs (Twitter), video (YouTube),
instant messaging (Slack), Q&A sites (Stack Overflow), and email (Section 2.3), on the grounds that
each carries its own distinct benefits and challenges and that microblogs and Q&A sites have already
been heavily studied.

**Relation to grey literature.** Blog-like documents are a *subset* of grey literature and inherit
both its benefits and its problems. Table 6 reproduces four general grey-literature definitions
(Lawrence et al. 2014 — artefacts not the product of peer review; Levin 2014 — anything lacking
bibliographic control; Schöpfel and Farace 2010 — produced across government, academia, business,
where publishing is not the producing body's primary activity; Lefebvre et al. 2008 — not formally
published in books or journals) and two definitions of "blog" (Conniff 2005, who argues defining
blog is "a fool's errand"; Herring et al. 2004 — frequently modified web pages with dated entries in
reverse chronological sequence). The authors' own contribution is the observation that **none of
these definitions isolate a higher-quality subset** suitable for SE research, and that neither
Soldani et al. nor Garousi et al. define "blog" or "blog post" for their own studies at all
(Section 4.1).

**White vs. grey (Section 2.9).** White literature is characterised by standardisation: structural
conventions, citation styles, formal language, long prepare–review–revise–publish cycles, central
indexing with metadata and a globally unique DOI. That standardisation is what makes SLR, SMS,
rapid-review and literature-study protocols workable. Grey literature lacks that infrastructure, so
the protocols do not transfer unmodified. Against this the authors note peer review's own failing —
publication bias, where negative results are much less likely to appear.

### Credibility and quality criteria

This paper's own position is that **an adequate credibility framework does not yet exist**; its
contribution is to specify what such a framework must cover and to catalogue the two existing
checklists as starting material.

**Challenge 12 — the quality-assurance gap (Table 11).** There is no well-developed and accepted
checklist for quality-assuring the various *aspects* of a blog-like document. The authors enumerate
six distinct objects of assessment that a checklist must separate:

1. the author;
2. the document;
3. the content of the document, e.g. its claims;
4. the readers' assessment of the credibility of the document;
5. the readers themselves;
6. the readers' feedback on the document — comments, shares, upvotes.

They press this distinction directly against Garousi et al. (Section 4.9.2): Garousi et al. speak of
"quality assessment of sources", but their *source* appears to be the document being assessed,
whereas one should distinguish the practitioner as source of information from the document that
records it. The five-way distinction the authors draw is: the source of the document (an author);
the document itself; content within the document; feedback on the document; and the source of that
feedback (readers).

**Required dimensions of a better framework (Section 4.3).** The authors judge the Garousi et al.
tiered framework "useful for appreciating the variation in quality" but insufficiently
discriminating, and call for a framework that separates:

- aspects of the author or authors, e.g. their experience;
- aspects of process, e.g. how the document was generated;
- aspects of output, e.g. the age of the document as distinct from its content;
- variation in the content;
- aspects of the reader feedback;
- aspects of the reader;

with each examined **at different levels of analysis**.

**Criticism of the tiered classification (Section 4.3, Figure 1).** Garousi et al.'s framework
classifies grey literature into three tiers by expertise and outlet control. Rainer and Williams
plot Soldani et al.'s three document types (blog post, whitepaper, video) against it as an
alternative reading, to show that **document type does not map onto tier**: whitepapers, videos and
blogs each distribute across all three tiers, and given the range of blogger experience one should
expect blog-like documents to spread across tiers too. (They note Garousi et al. themselves said the
tiers were meant to blend rather than be demarcated.)

**Checklist catalogued #1 — Garousi et al. (Table 10).** Reproduced by the authors as raw material
for a future blog-specific checklist. Its criteria groups, each paraphrased:

- **Authority of the producer** — is the publishing organisation reputable; is an individual author
  associated with a reputable organisation; has the author published other work in this field; does
  the author have expertise in the area.
- **Methodology** — does the source state an aim; does it state a methodology; is it supported by
  authoritative, contemporary references; are limits stated; does the work cover a specific
  question; does it refer to a particular population or case.
- **Objectivity** — is the presentation balanced; is the statement as objective as possible, or is it
  subjective opinion; is there a vested interest; are conclusions supported by the data.
- **Date** — does the item carry a clearly stated date.
- **Position regarding related resources** — have key related grey or formal sources been linked to
  or discussed.
- **Novelty** — does it add something unique to the research; does it strengthen or refute a current
  position.
- **Impact** — described as a normalisation of several impact metrics: citations, backlinks, media
  shares, comments, views.
- **Outlet type** — 1st, 2nd or 3rd tier per the tiered framework.

No numeric weighting or scoring rubric is reproduced for this checklist in this paper; it is
presented as a checklist of questions.

**Checklist catalogued #2 — Soldani et al. (Table 10).** Soldani et al. call using grey literature
"risky" because of the limited amount of rigorous data and analysis in the literature itself, and
found quality assessment very hard mainly because grey literature lacks consistent structure. They
therefore built what they themselves term a "rudimentary quality control framework": inclusion
criteria, exclusion criteria, plus four additional control factors. The stated decision rule is that
a study is selected if it satisfies **all** inclusion criteria and excluded if it satisfies **at
least one** exclusion criterion, and only studies satisfying the four control factors were retained.

- Inclusion — **I1** discusses industrial application of microservices; **I2** discusses benefits or
  shortcomings of microservice design, development or operation; **I3** reports direct experiences,
  opinions or practices by educated practitioners; **I4** refers to a practical case study of design,
  development or operation.
- Exclusion — **E1** no detail on design or implementation; **E2** not tied to industrial cases or
  other factual evidence; **E3** benefits or pitfalls not justified or quantified; **E4** no scope
  and limitations given for proposed solutions or patterns; **E5** no evidence of a practitioner
  perspective.
- Control factors — **C1 practical experience**: author must have 5+ years in service-oriented
  design/development/operation, or the source must concern established microservices solutions with
  2+ years of operation; **C2 industrial case study**: must refer to at least one industrial case
  with a quantifiable number of microservices in operation; **C3 heterogeneity**: the selected set
  must reflect at least 5 top industrial domains and markets; **C4 implementation quantity**: sources
  must show implementation detail for the benefits and pitfalls discussed, so others can act on
  them.

Note that C3 is a **set-level** criterion, not a per-document one — a corpus-composition requirement
rather than a credibility test. Soldani et al. found their criteria easier to apply to blog posts
and whitepapers than to videos.

**Author motivation as a credibility factor (Section 2.7).** Parnin et al. found four motivators for
developer blogging: personal branding, evangelism and recruitment, personal knowledge repository,
and soliciting feedback. Rainer and Williams argue the blogger's motivation "is an important factor
in assessing the credibility of the blog content" and hence its fitness for inclusion — and single
out *personal knowledge repository* as the most relevant motivation for research purposes, because
it corresponds to cataloguing experience.

**Ethical self-assessment as indirect evidence (Section 2.6).** Cenite et al. surveyed bloggers'
beliefs and practices against four ethical principles — truth telling, attribution, accountability,
and minimising harm — which the authors describe as relevant to assuring credibility. Non-personal
bloggers jointly ranked attribution, truth telling and minimising harm at a mean of almost 6 on a
7-point Likert scale, i.e. they self-assessed highly. The obvious caveat is that this is
self-assessment, and the paper lists replicating Cenite et al. for software practitioners as
research direction 1.

**Inclusion decision at review level (Table 4, phrasing modified from Garousi et al.).** Seven
questions for deciding whether grey literature belongs in a review at all — a scoping gate that
precedes per-source credibility assessment:

1. Is the subject complex and not solvable from formal literature alone?
2. Is there a lack of volume or quality of evidence, or a lack of consensus of outcomes measurement,
   in the formal literature?
3. Is contextual information important to the subject?
4. Is the goal to validate or corroborate scientific outcomes against practical experience?
5. Is the goal to challenge assumptions or falsify results from practice using academic research, or
   vice versa?
6. Would synthesising insights from the practical and research communities be useful to either or
   both?
7. Is there a large volume of practitioner sources, indicating high practitioner interest?

The authors add (Section 5.2) that these seven questions "appear to apply equally to either
approach" — secondary study or primary study.

### Process steps

**The case-survey protocol (Table 13).** The paper's own methodological proposal for *primary*
studies that treat blog-like documents as data rather than as literature. Six stages:

- **S1 — Establish research objectives, requirements and rationale.** Establish the rationale;
  establish objectives; establish general research questions and specific subquestions, prioritise
  and structure them; define propositions and/or hypotheses if any; define variables; quality-assure
  the objectives themselves.
- **S2 — Define and source cases.** Define the case (the unit of analysis); design the search
  strategy, queries and terms; ensure search strategy and cases stay aligned with the research
  questions; execute searches; download the results; **perform backward snowballing on the URL links
  in the downloaded results**; perform post-search quality filtering; run quality-assurance checks on
  both the downloaded and the filtered data.
- **S3 — Define the survey of cases.** Identify more specific exploratory research questions;
  identify variables; operationalise variables.
- **S4 — Extract data from the surveyed cases.**
- **S5 — Analyse extracted data.** Test propositions and hypotheses; answer the research questions.
- **S6 — Disseminate the findings.**

Two features distinguish S2 from an SLR search: quality filtering happens *after* the search rather
than through a database's editorial gate, and snowballing runs over hyperlinks in the retrieved
documents rather than over reference lists.

**Choosing between secondary and primary framing (Section 5.2, Table 14).** The authors argue the
same body of material can be framed either way, and that two features distinguish the choices:
how the researcher conceives of the document (as literature to review vs. as data to analyse), and
the coverage sought (comprehensive vs. representative sample). Their reading of prior work: Parnin
et al. treated blog-like documents neither as literature nor explicitly as cases; Pagano and Maalej
explicitly treated them as data; Rainer's argumentation study can be read as one case (a single
Joel Spolsky post) with multiple units of analysis.

Table 14, eight similarities between secondary and primary studies of blog-like documents:
both distinguish document from content; both deal with naturally written text of varying formality
and quality; both seek coverage of a body of literature; both face scaling problems from large
volume; both apply quality criteria to select more relevant and higher-quality documents, though the
criteria may differ significantly; both rely on the same keyword-based search engines; both analyse
documents whose editorial generation process is unknown or uncertain; both analyse documents whose
process of knowledge generation or accumulation is unknown or uncertain. Two differences: the
conception of the object of study (publications vs. data), and the degree of coverage
(comprehensive vs. representative sample).

### Search and sampling techniques

**The review's own search (Section 2.3)**, useful as a worked example. Primary search engine was the
ACM Digital Library, chosen because the review's focus was empirical studies of software practice,
complemented by Google Scholar. Primary query `"software engineering" [with] "blog post"` over
2000–2019, returning **336 results**. Titles of all articles were reviewed, then abstracts and full
papers where appropriate, yielding **42 candidates**, reduced on closer inspection to **14**. A 15th
was added from the authors' prior experience and a 16th suggested by a reviewer. Three further
non-SE papers came from exploratory Google Scholar searches of the wider literature, as contrasting
examples. The final tally: **4 primary studies, 3 secondary studies, 2 methodology papers** relating
explicitly to software practice, plus **3 non-SE papers**, plus **12 of the authors' own papers** =
**24 papers** in Table 2.

**Sampling problems specific to this material (Section 5.2).** Systematic reviews ideally seek
comprehensive if not complete coverage of primary studies, but that objective is "extremely
difficult to obtain" with grey literature. A representative sample is the more pragmatic goal — yet
sampling is itself extremely hard here **because the population is hard to define, as is a sampling
frame**. The case-survey design at least makes the sampling step explicit rather than implicit.

**Scale of the population (Section 4.4).** Nearly a decade before the paper, BlogScope tracked more
than 36.88 million blogs with 837.39 million posts, fetching on average 14,000 new documents an
hour. In SE specifically the curated lists are tiny by comparison: Choi lists 650 blogs classified as
company / individual-group / product-technology; Panji maintains 185 software-related corporate
blogs; Merchant over 50 tech blogs; Abstracta 75 software-testing blogs and websites. These manually
curated lists are inevitably far smaller than the real population. Soldani et al. describe a
"massive proliferation" of grey literature on microservices, with more than 10,000 articles across
sub-topics. The unknown size of the population is itself the challenge.

**No stopping rule is offered.** The paper does not propose an effort bound or saturation criterion;
that gap is part of what motivates the heuristics paper (research direction 6 points explicitly at
the search heuristics of Rainer and Williams 2019).

**Tool and infrastructure limits (Sections 4.8.1, 4.8.4).** There is no central repository of
software-related blogs; the available GitHub lists are manually maintained and of unknown
representativeness; alternatives are blog aggregators (Planet) or news aggregators (Reddit). General
search engines — Google, Bing, DuckDuckGo — are all keyword-based, so a searcher has no direct way to
select higher-quality documents, to select a particular grey-literature type such as blog-like
documents, or to select documents that report experience. All use proprietary indexing algorithms
and content delivery networks, which threatens the transparency and reproducibility of searches.
There is no specialist search engine for blog-like content analogous to the ACM DL, IEEE Xplore or
Google Scholar. The authors distinguish three things academic publishing supplies and blogs do not:
quality-assurance processes (peer review), editorial processes that standardise items for repository
inclusion, and the subsequent feedback process.

### Caveats, traps and pitfalls

**The fourteen challenges (Table 11), grouped by the authors' own themes.**

*Foundations — lack of:*
1. formal definitions of grey literature and of blog-like documents and content;
2. formal models of blog-like documents — specifically a **data model** of documents and content and
   a **process model** of their creation, review and publication;
3. frameworks for evaluating the quality of, and classifying, such documents and content.

*Inherent nature — difficulty managing:*
4. the very large quantity of blog-like documents;
5. their variability;
6. the uncertain process by which content is generated, published and revised;
7. the ambiguity of language in blog post content.

*Resources — lack of:*
8. repositories of blog-like documents;
9. tools, in particular tools to select higher-quality documents during a search and tools to select
   particular types of document, e.g. those reporting experience, values, or explanations;
10. datasets and annotated corpora — including a lack of standards for describing and comparing
    datasets and a lack of standards for annotating them.

*Search engines:*
11. proprietary indexing algorithms and content delivery networks undermine independent
    reproducibility of search results.

*Quality assurance:*
12. no well-developed, accepted checklist covering the six aspects listed in the credibility section
    above.

*Methodology:*
13. the evidential value of blog-like content is unestablished;
14. the appropriate research methods to use with such documents are unsettled.

**Variability, in detail (Section 4.5, Table 7).** Dimensions along which blog-like content varies:
quality of written language (e.g. formality); natural language (most research assumes English);
media (video, text, image, presentations); encoding of the media (HTML text vs. proprietary binary
such as PDF); structure (headings, subheadings); and content — reasoning such as claims, reasons and
arguments; opinions; reporting of actual experience, perhaps as a "war story"; code-related
information such as source, documentation and API; web links; tables of data; citations. The
authors judge **Content the most valuable dimension for research** but note every dimension creates
analysis problems, and that the dimensions are not mutually exclusive — a video can contain an
argument, an audio file can report experience, a presentation can carry a real story.

A concrete NLP trap they give: the personal pronoun "I" is a common marker of personal experience,
but lowercase "i" is a common loop-iterator variable name, and a pipeline that lowercases all text
destroys the distinction.

A further trap: having analysed such variable material, there is then the problem of presenting the
analysis concisely enough for interpretation while preserving traceability and reproducibility.

**Recall and time delay (Section 4.6).** Parnin et al. found most developers write up an experience
several days after completing the work, with only **20% writing the post the same day**. The delay
threatens the writer's recall and therefore the validity of the content. The authors' balancing
observation is that this threat is *not unique* to blogs and is probably worse elsewhere: interviews,
surveys and focus groups are even less likely to occur close in time and place to the experience.
Blog-like documents may in fact have an advantage in that the writer is typically writing about one
specific experience, whereas an interviewee is often asked about general experience and opinion.

**Absence of external control (Section 4.6).** The lack of a peer-review process is not an isolated
defect: because there is no external mechanism, there is nothing controlling the *quantity*, nothing
controlling the *variability*, and no post-generation process to moderate how documents are
produced. Corporate constraints add a further distortion — Parnin et al. observed that some
developers blog publicly but not at work, citing limited exposure and censorship.

**Language ambiguity and annotator disagreement (Section 4.7).** Formality varies between posts and
even *within* a single post. Swanson et al. analysed 50 personal stories drawn from 5,000 posts
taken from 44M articles, using three annotators, and achieved annotator agreement of **0.58**; they
attribute this to the task being highly subjective, requiring interpretation of the narrative and of
the author's intention. Rainer and Williams' inference from Swanson et al.'s comparison with an
earlier study of Aesop's Fables (high agreement, extremely high machine-learning accuracy) is that
classical written-down stories are much easier to work with than blog posts.

**Dataset incomparability (Section 4.8.2).** Two studies of ostensibly the same object can produce
wildly different pictures because they sampled differently. Pagano and Maalej found source-code
paragraphs in only 934 of 50,701 blog posts (**1.8%**), averaging 2.5 code paragraphs in those
posts. Parnin and Treude found **90%** of posts (336 of 373) had code snippets, median 3 per post.
The explanation is sampling: Pagano and Maalej took all blog-like documents produced in four open
source projects; Parnin and Treude took documents found by Google searches for jQuery API method
calls. The lesson is that dataset provenance must be reported, because otherwise proportions are
uninterpretable. Aniche and Treude's comparison of r/programming with Hacker News found more than
85% of posts in each came from personal blogs, but r/programming skewed technical while Hacker News
had a broader business/commerce/economics focus.

**Corpus annotation (Section 4.8.3).** A significant challenge is establishing an annotation
standard — what should be annotated, why and how. Table 9 lists argumentation-mining corpora
(Rinott et al. 2015 and Aharoni et al. 2014 on Wikipedia pages; Boltuzic and Snajder 2014 and Park
and Cardie 2014 on user comments; Habernal et al. 2014 on web documents; Rosenthal and McKeown 2012
on blogs and forums; Biran and Rambow 2011 on blog threads) and experience-mining corpora (Swanson
et al. 2014, 229 blogs containing personal stories; Inui et al. 2008, one year of Japanese weblog
posts; Qamra et al. 2006, over one million blog posts crawled Dec 2004–Sep 2005).

**Misconception about evidential status (Section 1).** The authors flag a specific misconception to
guard against: treating a grey literature review as though it accords grey literature the same
evidential value as the primary studies of a systematic review.

**Threats to the review itself (Section 6).** Small number of primary and secondary studies
identified, partly a real scarcity and partly an artefact of the search and selection process;
reliance on ACM DL plus Google Scholar means other bibliographic engines were not searched — and
notably **one of the four selected primary studies was not returned by the ACM DL search** despite
being one they would expect to be indexed there; and potential shared bias, since although both
authors reviewed papers independently they have worked closely together for a long time.

### Metadata requirements

The paper does not give a bibliographic-recording checklist, but the requirements are implied at
several points and can be assembled:

- **A clear publication date** is definitional feature 9 and is separately a Garousi et al. quality
  criterion ("Date: Does the item have a clearly stated date?"). Documents of unknown date fail the
  reference definition.
- **An identifiable author who is an identifiable software practitioner** is definitional feature 2;
  documents of unknown origin are explicitly to be excluded (Section 2.1).
- **The URL / online location** is definitional feature 5, and web links within the document are one
  of the content dimensions in Table 7 — links are also the substrate for backward snowballing in
  case-survey stage S2.
- **Author expertise and organisational affiliation** are demanded by the Garousi et al. Authority
  criteria and by Soldani et al.'s C1 (years of experience).
- **The age of the document must be recorded separately from its content** — this is one of the
  aspects the authors say a better framework must discriminate (Section 4.3).
- **Reader-feedback counts** — comments, shares, upvotes, follows, reshares, views, backlinks — are
  both a Garousi et al. impact metric and one of the six aspects Rainer and Williams say must be
  assessed separately (challenge 12). Section 4.6 notes the common forms of appreciation are
  comments, shares, and some form of up- or down-voting, and that similar measures have been used in
  Stack Overflow analyses.
- **Provenance of the dataset itself** — how documents were searched for and selected — is required
  to make proportions comparable across studies (Section 4.8.2 above).
- Link rot is demonstrated rather than discussed: the paper's own footnote records that BlogScope's
  website no longer responds, and one dataset in Table 8 (TUAW) is described as obsolete though its
  dataset survives. Content disappears; the archived dataset is what persists.

### Data extraction and analysis techniques

- **Case-survey framing.** Each blog-like document is treated as a case (per Runeson and Höst),
  comprising one or more units of analysis — e.g. the textual content relevant to the research topic.
  The case survey combines the depth focus of case study with the breadth of survey, which is what
  the volume of available documents requires. The authors are developing a variant specifically for
  blog-like documents; the protocol is Table 13 above.
- **Argumentation analysis.** Rainer's use of argumentation theory to analyse practitioners'
  defeasible evidence, inference and belief is cited as the exemplar; his study of a single Spolsky
  post is read as one case with multiple units of analysis, each unit an instance of reasoning
  comprising argumentation, citations to sources, and reports of experience as stories.
- **Reasoning indicators for search.** The authors validated reasoning indicators against a corpus of
  persuasion essays (Stab and Gurevych) and then used them as Google keyword search terms — i.e.
  argumentation markers used as a *retrieval* device, not only an analysis device.
- **Tooling.** A suite named **COAST** (`coast_core` and `coast_search` on GitHub) was developed and
  was under evaluation at time of writing.
- **Content coding by type.** Parnin and Treude classified blog posts by type, the most frequent
  being *experience*, where the post documents development knowledge drawn from a recent experience.
- **Automated / large-scale analysis.** Pagano and Maalej's automated topic analysis of blog content
  across four open source communities is the exemplar of treating documents as data at scale.
- **Trend analysis.** Glance et al. continuously crawl and analyse blogs to detect trends over time;
  the authors flag trend analysis as valuable for both research and industry, and as one of the
  circumstances under which blog-like documents should be considered (benefit 4).
- **Triangulation.** Documents can be triangulated across sites (GitHub, Stack Overflow) and against
  proactively collected data (interviews, surveys); such triangulation helps address publication
  bias. A blog read as a *series* of posts by one author allows the researcher to check the
  consistency and coherence of that practitioner's experiences and beliefs over time — something a
  one-hour interview cannot supply.

**Two dimensions of experience (Section 3.1)** worth carrying into any extraction form: the degree of
experience *reported in* the document (e.g. as factual stories), and the degree of experience the
blogger *has* of software practice generally. These are separate variables.

### Empirical findings worth citing

- **Blog coverage of API documentation.** Parnin and Treude analysed 1,730 web pages for jQuery API
  coverage and identified **376 unique blog posts**; the blog posts collectively covered **88%** of
  API methods (reported as 87.9% in Section 2.7). Only the official API site covered more, at
  approximately **99%** (99.4%); Stack Overflow covered **84.4%**.
- **Blog posts as a share of grey literature in GLRs.** Soldani et al. selected **51 documents**:
  **20/51 blog posts, 21/51 whitepapers, 10/51 videos** — approximately 40% blog posts. (A fourth
  type, industry magazine, appears to have been dropped or folded into whitepapers.) It was in a
  blog post that Lewis and Fowler first introduced the term microservices.
- **Raulamo-Jurvanen et al.** identified **60 sources**; **59** reported experiences or opinions and
  **7** reported examples. The paper cannot determine how many were blog-like, but at least 35
  sources had comments, suggesting roughly **60%** were blog-like if comments are taken as the
  defining feature.
- **Blogging behaviour** (Table 3). From the fourth Orbit Media Studios blogger survey, N = 1,377:
  average time to write a post **3 h 20 min** — about three times the length of a usual research
  interview; bloggers typically write several times a month; average post length **1,142 words**;
  **55%** of bloggers update posts at least sometimes. From Cenite et al.'s non-personal bloggers,
  N = 332: mean age **34.9 years (SD 12.2)**; **19.2%** female — which the authors note is consistent
  with SE's own skewed demographics, while insisting the male/female ratio is not itself a measure of
  the value of the content; reasons for blogging **36%** commentary, **21%** information, **11%**
  expressing thoughts and feelings; **48%** report their primary audience is people not known to them
  personally.
- **Blogger ethics.** Cenite et al.'s non-personal bloggers jointly ranked attribution, truth
  telling and minimising harm at a mean of almost **6 on a 7-point scale** (self-assessed).
- **Motivation to blog.** Parnin et al.: **93%** of surveyed participants cited that the process of
  writing helped them learn and remember the information better — the most cited benefit of blogging
  about coding.
- **Blog vs. commit comment richness.** Pagano and Maalej found project-specific blog articles
  contain roughly **14 times** the word count of version-control commit comments, and cover
  high-level concepts and functional requirements rather than low-level change descriptions. Common
  topics across all four open source communities studied were "functional requirements and domain
  concepts" and "community and contributions", leading them to conclude developers blog mainly to
  promote new features and system requirements and to build communities.
- **Code content is sampling-dependent.** 1.8% of posts (934/50,701) vs. 90% of posts (336/373) — see
  the dataset-incomparability trap above.
- **Personal blogs dominate aggregators.** Aniche and Treude: greater than **85%** of blog posts in
  both the r/programming and Hacker News datasets came from personal blogs.
- **Annotator agreement on personal-story annotation:** **0.58** (Swanson et al., three annotators).
- **Blogs in health research.** Wilson et al.'s scoping review covered **44 studies**: **38** used
  blogs for data collection, of which **21** collected data about experiences, feelings and
  perceptions and **17** about blogger behaviour; in **11** studies blog data were combined with
  another source such as interviews, surveys or focus groups. Wilson et al.'s stated methodological
  benefits — instantaneous access to distant populations, research clarity and transparency with
  built-in audit trails, and circumventing lengthy interview transcription — are adopted by Rainer
  and Williams into their own benefits table.
- **Contribution counts of this paper itself:** 5 main benefits (with multiple more specific
  benefits), **14 main challenges**, and **15 directions for research**; 24 papers reviewed.

---

## rainer_heuristics_2019 — Heuristics for improving the rigour and relevance of grey literature searches for software engineering research

Rainer, A. and Williams, A. (2019), *Information and Software Technology*, 106:231–233. A three-page
short paper.

**Role in corpus:** The operational counterpart to the 2019 review — it converts "quality criteria"
from a post-hoc appraisal checklist into *search keywords*, and proposes a set-theoretic stratified
sampling design so a grey-literature search yields comparison strata rather than one undifferentiated
result list.

### Definition and scope

The paper addresses **online grey literature (GL)** generally rather than blog-like documents
specifically, and is framed around the practical problem that keyword-based search engines are
simultaneously unsuited to systematic searching and "the only general–purpose search mechanism
currently available" for it (Section 1). Its stated context of use is an MLR, a Grey Literature
Review, or a Rapid Review.

Three search-engine limitations are named as the motivating problem (Section 1):

- queries are keyword-based, so they do not permit finer-grained searching or more sophisticated
  lexical features such as grammatical structures;
- results are likely optimised to the individual searcher, based on that searcher's prior search
  history;
- engines maintain their own topic models to decide relevance, e.g. whether an article relates to
  software testing.

Added to these, the size of the World Wide Web is unknown "(even unknowable)", so there is no way to
judge how representative a set of results is of any wider online population. The consequence stated
in the abstract and Section 1 is a search that produces both **false positives** (irrelevant articles
returned) and **false negatives** (relevant articles not returned), damaging both effectiveness and
efficiency.

### Credibility and quality criteria

The paper's distinctive move is to sort quality criteria into two classes by **implementability as a
search keyword**.

**Class A — quality criteria that can be operationalised as keywords (element 4).**

- **(4a) Reasoning.** Reasoning indicators can be included directly as search keywords. The authors'
  prior work (Williams 2018 on reasoning markers) identified a number of reasoning indicators with
  **high precision but low recall** — a property that matters, because it means a reasoning-keyword
  search returns a trustworthy but incomplete slice.
- **(4b) Identity.** Keywords naming particular institutions or individuals previously associated
  with higher-quality articles in a given context. The authors explicitly flag that choosing
  particular institutions or individuals carries validity threats, say discussion of those threats is
  beyond the paper's scope, and point the reader to Garousi et al.'s inclusion of *authority* in
  their quality-assessment checklist and to the **AACODS checklist** (Tyndall 2010 — Authority,
  Accuracy, Coverage, Objectivity, Date, Significance).

**Class B — quality criteria not suitable for keyword implementation (element 7).** Two examples are
given: **quality of writing** and **presence of citations**. These must be applied to the *post-search*
samples instead. The authors stress that the stratified-sampling logic continues to hold in this
second phase: "layers of search–produced samples and, within those layers, sub-layers of post-search
sub–sampling."

The demonstration illustrates the split concretely: standard search engines cannot search for
articles containing citations (e.g. anchor tags), so URL-citation searching had to be a post-search
process (Section 3).

**Relation to existing checklists.** The paper does not propose its own quality checklist. Its stated
position (Section 4) is that Garousi et al.'s MLR quality checklist "suggests the basis of quality
criteria to use in the post–search filtering", and that implementing that checklist in post-search
filtering should improve the rigour of the articles the researcher ends up analysing. Formal
evaluation of the heuristics *against* Garousi et al.'s checklist is named as future work.

No weighting or scoring rubric is offered. The criteria are used as sampling and filtering
predicates, not as a score.

### Process steps

The heuristics are enumerated as seven elements (Section 2):

1. **Assume an existing topic keyword set.** The researcher already has topic-related keywords
   intended for online searches. The worked example is Garousi et al.'s MLR search string
   `<decision automated software testing>`.
2. **Push inclusion/exclusion criteria into advanced search settings where possible.** Search engines
   often allow restriction by date range, file type, or natural language, and these implement some
   inclusion and exclusion criteria directly — e.g. only PDF documents, in English, dated 2008–2018.
   The paper is explicit that other criteria "must often be applied after the searches have been
   conducted", and that post-search exclusion can only operate on what the search actually returned.
3. **Distinguish *types* of topic keyword and manage each set separately.** Given examples: separate
   the generic topic (automated software testing) from the specific sub-topic (decision-making about
   automated software testing); or separate a topic from a *perspective* on the topic, such as
   practitioner experience (experience keywords) or empirical studies of that topic (empirical-study
   keywords).
4. **Add quality criteria as keywords** — reasoning indicators (4a) and identity keywords (4b), as
   above.
5. **Sample stratified, and sample negatively.** (5a) Conduct stratified sampling of searches based
   on set-theoretic combinations of the keyword sets (Table 2); (5b) include *negative* searches,
   i.e. searches for the negation of a keyword. The result is "stratified positive and negative
   sampling based on topic keywords and quality–criteria keywords."
6. **Compare the resulting strata.** The stratified samples let the researcher investigate the
   properties of each sample and compare them using measures relevant to the research — the paper
   names distance metrics and information metrics. Aside noted by the authors: the strata can
   potentially serve as datasets for machine classifiers.
7. **Apply the non-keyword-able quality criteria to the post-search samples**, preserving the
   stratification as sub-layers.

**The search-set design (Table 2).** With three keyword sets — T (topic), R (reasoning), E
(experience) — and their negations, nine search sets are defined:

| Set | Composition |
| --- | --- |
| S1 | !T, !R, !E |
| S2 | R, !T, !E |
| S3 | R, E, !T |
| S4 | E, !T, !R |
| S5 | T, R, !E |
| S6 | T, R, E |
| S7 | T, E, !R |
| S8 | T, !R, !E |
| S9 | !T (marked as a special/constrained case in the table), !R, !E |

**S6 is the target stratum** — content containing reasoning and experience about the topic. Every
other set exists to let the researcher *evaluate* S6 by contrast. The paper's example: S3 finds
content with reasoning and experience but not about software testing.

**S1 and S9 are special cases.** Formally S1 is the universe of other potential online content and
should be included for completeness of evaluation; practically the authors say they lack the
resources to search the universe of online content (or even Google's indices of it), and anticipate
S1 would be "a sparse and unpredictable dataset". They therefore constructed a **random sample of
search queries with query length between two and five keywords** for S1, and complemented it with
the more constrained S9, defined as all articles relating to software engineering *excluding* those
referring to testing.

### Search and sampling techniques

**The demonstration's search protocol (Section 3)** — the concrete effort bound this paper supplies:

- Research question of the demonstration: whether practitioners cite other sources (researchers or
  practitioners) when writing online articles about their experiences of software testing.
- Three keyword sets (Table 1): **Topic** = `software AND testing`; **Reasoning** = *but, because,
  for example, due to, first of all, however, as a result, since, reason, therefore*; **Experience**
  = *i, me, we, us, my, experience, experiences, experienced, our*.
- Provenance of the sets: the reasoning indicators were derived from a review of prior research. For
  experience there is "little prior research on searching for experience online" (they cite Jijkoun
  et al. 2010 and Inui et al. 2008), so they constructed a basic keyword set and are explicit that
  its validity is **not** central to the demonstration — it is used as proof of concept only.
- Engine: the **Google Custom Search API**, chosen to permit automation; the authors note prior SE
  research (e.g. Dieste and Juristo) has tended to search Google manually.
- Effort bound and mechanics: daily searches for all nine search sets over a continuous **four-week
  (28-day)** period, October–November 2017. The Google Custom Search API caps free searches at
  **100 per day**. They therefore ran **10 searches per search set per day** across **nine
  independent search engines** (i.e. nine configured custom search engines). Each search returns
  **10 pages × 10 results**, so **1,000 results per day per set**.
- Rationale for repeating queries ten times a day: **to smooth the proprietary variation in results**
  returned by the API. This is the paper's practical answer to search irreproducibility.

**Stopping rule.** None is stated as a saturation criterion; the bound is temporal and quota-driven
(28 days at the API's free limit), not evidence-driven.

**Effort cost, acknowledged.** The heuristics "potentially introduce additional effort" through a
greater number of, and more complex, searches (elements 5–6 and Section 4). The authors' answer is
automation: a tool (`zedrem/coast` on GitHub) to conduct the stratified searches automatically, plus
software to assist with downloading results and post-search filtering. Their claimed net effect is
that stratified samples give more flexibility in selecting articles to analyse, so the researcher can
**both reduce effort** (being more selective about what is studied) **and be more effective** (working
with the higher-quality set).

### Caveats, traps and pitfalls

- **Searcher personalisation biases results.** Engines optimise to the individual based on prior
  search history — the same query run by two researchers is not the same query.
- **The engine's own topic model decides relevance**, using criteria the researcher cannot inspect
  or control.
- **Proprietary result variation** is real enough that the demonstration had to run each query ten
  times daily just to smooth it.
- **The population is unknowable**, so representativeness of any result set cannot be assessed.
- **Keyword searching cannot express grammar or structure**, which is why criteria such as presence
  of citations cannot be searched for at all.
- **Post-search filtering can only subtract.** Anything the search missed is unrecoverable at the
  filtering stage — stated plainly in element 2.
- **Identity-based quality keywords carry validity threats** that this paper explicitly declines to
  analyse (element 4b). Selecting on named institutions or individuals bakes a prior about quality
  into the sample.
- **High precision, low recall** for the reasoning indicators means the reasoning strata are biased
  towards a subset of reasoning-bearing articles.
- **The experience keyword set is unvalidated** and offered only as proof of concept.
- **The heuristics themselves are unevaluated.** Stated twice (Sections 3 and 4): the heuristics have
  contributed to prior research but "have yet to formally evaluate the heuristics", and they are
  discussed explicitly for the first time in this paper. Only the reasoning indicators have been
  evaluated separately, for precision.

### Metadata requirements

Not addressed as such. What the method *does* require to be recorded, implicitly, is the full search
configuration: the three keyword sets verbatim, the nine set-theoretic combinations, the engine and
API used, the date window, the queries-per-day and results-per-query figures, and the fact of
repeated daily execution — since without these the search cannot be reconstructed at all given
proprietary index variation. The advanced-search settings used as inclusion/exclusion criteria
(date range, file type, language) are likewise part of the recorded protocol.

### Data extraction and analysis techniques

- **Semi-automated citation analysis.** Having sampled, the authors performed semi-automated analysis
  of the articles for the presence of citations, then classified each cited URL into categories.
- **Sub-sampling then qualitative analysis.** The stratification allows the researcher to select
  particular *sub-samples* of relevance and analyse those qualitatively — the stated efficiency
  argument for the whole design.
- **Cross-stratum comparison as measurement.** By comparing strata the authors establish a *relative*
  size of citation to research, rather than an absolute rate. This is the analytical pay-off of the
  negative search sets.
- Suggested comparison measures across strata: distance metrics, information metrics.

### Empirical findings worth citing

From Table 3, the percentage of source articles citing an external URL, by category of cited URL and
by search set (S1–S9). The values are low across the board:

| Category of cited URL | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Peer-reviewed research (e.g. IEEE Xplore) | 0% | 0% | 1% | 0% | 1% | 1% | 0% | 1% | 1% |
| Education (e.g. .edu domains) | 2% | 2% | 3% | 2% | 3% | 3% | 1% | 4% | 12% |
| Developer authorities (e.g. MSDN) | 0% | 0% | 1% | 0% | 2% | 4% | 2% | 1% | 1% |
| Developer Q&A (e.g. Stack Overflow) | 0% | 0% | 0% | 0% | 0% | 1% | 1% | 0% | 0% |
| Repository (e.g. GitHub) | 0% | 1% | 1% | 0% | 4% | 2% | 1% | 2% | 1% |

The headline reading the authors give: in **S6** — the target stratum of topical content containing
both reasoning and experience — developers cite **developer authorities four times as much as they
cite research** (4% vs. 1%). The broader point for a methodology document is that citation of
peer-reviewed research in practitioner online articles is at or near **1% in every stratum**, which
sets a realistic expectation for how much traceable evidential grounding grey literature carries.

Effort figures worth quoting: **1,000 results per day per search set**, nine sets, over **28
consecutive days**, under a **100-free-searches-per-day** API quota, with each query run **10 times
daily** to smooth result variation.

---

## rainer_using_2017 — Using argumentation theory to analyse software practitioners' defeasible evidence, inference and belief

Rainer, A. (2017), *Information and Software Technology*, 87:62–80. Single-authored.

*Note on identification:* the file is catalogued as the practitioner-generated-content-as-evidence
paper; the actual article is the argumentation-theory paper above. It is the right paper for the
topic — it supplies the per-claim credibility machinery that the other two papers say is missing.

**Role in corpus:** Where the 2019 review says a credibility framework is needed and the heuristics
paper handles retrieval, this paper supplies the *evidential test itself* — a set of criteria,
imported from legal evidence scholarship, for deciding when an item of information in a
practitioner's report may be treated as evidence at all, plus argumentation schemes with critical
questions for interrogating the inference from that evidence to the practitioner's belief.

### Definition and scope

**Practitioners as fallible generators, not conduits.** The framing premise (Section 1) is that
practitioners observe the world, hold beliefs about it, share information, and act to change it, and
in all four they *choose*. They are therefore "active generators" of information rather than passive
conveyors. The paper is explicit that practitioners, like researchers, are fallible: their
observations, beliefs, information sharing, actions and choice making "are often unreliable in some
way (although not intentionally deceptive)". Note the parenthesis — the model is unreliability, not
deception, which is a different threat profile from the one usually assumed of marketing content.

**Naturally produced reports.** The object of study is the very large volume of information
practitioners produce in the course of practice — email exchanges, technical reports, blog posts. The
paper scopes itself to **blog posts written by software practitioners**, and treats these posts as
**a type of testimonial evidence from (expert) witnesses**. That legal framing is the paper's central
analytical commitment.

**Primary vs. secondary practitioner information (Section 2.2).** A distinction the paper introduces
and that is directly usable as an extraction variable:

- **Primary information** — information clearly informed by the practitioner's own personal
  experience;
- **Secondary information** — information not clearly informed by personal experience, which may
  instead derive from indirect sources such as peers.

The paper is "particularly interested" in evidence based on primary practitioner information, because
this is in principle the evidence most closely connected with observation. Fig. 1 relates sources of
information → evidence → beliefs, with arrows signifying inference; the paper flags the model as a
simplification, since secondary information can shape how a practitioner interprets personal
experience, and prior personal experience can shape interpretation of current experience.

**Evidence as a relation, not a property (Sections 2.1, 3.3).** Evidence is defined relationally —
"A is evidence of B"; the SE example given is that a failure in a module is evidence of a fault in
that module. Schum's conclusion is quoted to the effect that the word cannot be defined so that
everything acceptable in all disciplines is included and everything else excluded. Twining's
formulation is that information has a potential role as relevant evidence if it tends to support or
negate, directly or indirectly, a hypothesis. Schum again: a datum becomes evidence in a particular
inference only when its relevance to that inference has been established, and that relevance must be
established by cogent argument. **The arguer chooses what to treat as evidence and what to discard,
and carries the obligation to argue for that choice.**

**Why existing evidence machinery does not fit (Section 2.1).** SE research has worked on
classifying and ranking evidence, combining and synthesising it statistically and
non-statistically, and describing its aspects — but all of these operate on information *already
defined as* evidence. They are applied at the level of a study's findings and therefore *ex post
facto*, which makes them more applicable to secondary studies such as systematic reviews. They become
problematic during primary research, where the task is precisely to evaluate whether items of
information *should* be treated as evidence. That is the gap Table 1 fills. The criteria are offered
as complementary to grading schemes such as Wohlin's evidence profile, which applies ex post facto to
a study's findings.

**Standpoint (Sections 3.1, 3.10).** Two perspectives exist on any situation of interest: the
practitioner's and the researcher's. Schum's three reasons why standpoint matters: (i) practitioner
and researcher perceive the situation differently and will therefore judge relevance differently;
(ii) information relevant at one stage of the inferential process may be dismissed as irrelevant at
another — e.g. once a proposition is rejected, its supporting information may become irrelevant;
(iii) different standpoints carry different objectives — the practitioner is trying to understand
their own project so as to act effectively in it, the researcher is trying to understand that project
in order to understand projects in general. Fig. 4 formalises the corresponding preference split:
researchers seek more generalised knowledge and generalised explanations and tend toward
propositional knowledge; practitioners seek more contextual, specific knowledge and explanations and
tend toward practical knowledge.

### Credibility and quality criteria

**Table 1 — preliminary generic criteria for using information as evidence** (based on Schum). This
is the paper's core credibility instrument. It is deliberately **"substance-blind"** — intended to
apply across different types of evidence — and gives **no indication of the granularity** at which
information should be assessed, granularity ranging from a measure of a line of code to a measure of
a key process area's maturity. There is **no scoring or weighting rubric**; these are tests, applied
qualitatively.

| Criterion | What it requires |
| --- | --- |
| **Relevance** | Information can be evidence if it lets us (a) revise our beliefs about how likely a proposition is to be true or false, or (b) revise one or more existing propositions, or (c) generate entirely new propositions. |
| **Competence of witness** (for testimonial evidence) | A competent witness is someone who *could* have made the relevant observation or gathered the relevant information, *and* who understands what they observed or gathered. Both halves are required. |
| **Credibility of tangible evidence** | Requires sufficient **chain of custody** — knowledge of how the information was generated — and sufficient **accuracy**, i.e. the degree of conformance to what the information represents. |
| **Credibility of testimonial evidence** | Requires sufficient **observational sensitivity** (ability in the observer to discriminate occurrence from non-occurrence of the event of interest), **objectivity** (ability to attend to the event itself without being swayed by personal motivation or prior expectation), and **veracity** (ability to communicate truthfully what the observer believes did or did not occur). |
| **Inferential force** | Information can be evidence if it bears on *how much and in what direction* we revise our probabilistic beliefs. |
| **Standpoint** (not a criterion, but a required declaration) | Three questions: What role am I taking — researcher or practitioner? At what stage in what process am I? What am I trying to do? |

**Relevance vs. inferential force (Section 3.6)** — a distinction the paper insists on because the
two look similar. Relevance is the general sense that information may influence the probability of a
proposition, its substance, or the generation of a new one: a *higher-level* judgment about whether a
practitioner's report, or part of it, may influence our beliefs. Inferential force concerns the
*magnitude and direction* of influence: a *lower-level* judgment about how particular items
specifically influence our beliefs.

**Chain of custody, applied to a blog post (Section 3.8).** The tangible evidence is the report the
practitioner produced; the testimonial content is what actually interests the researcher. To
establish chain of custody, "we need to know how the report came to be written and disseminated."
This is the same gap the 2019 review calls the missing *process model* of creation, review and
publication.

**Sufficiency is relative to research standards (Section 3.7).** The paper's goal is stated as
identifying naturally produced reports written by *sufficiently competent* practitioners containing
*sufficiently credible* testimony — with an explicit caveat that "sufficiently" means by the
standards research requires, and implies nothing more general about practitioners' competence or
credibility. A significant difficulty is acknowledged straight away: **practitioners do not
necessarily naturally gather and generate the kinds of information suitable for research.**

**Argument-from-expert-opinion scheme and its critical questions (Tables 3, 4).** The scheme in
syllogistic form: *Major premise* — source W is an expert in domain D containing proposition P;
*Minor premise* — W asserts that P (in D) is true or false; *Conclusion* — P may plausibly be taken
to be true or false. Six critical questions are used to evaluate such an argument:

| # | Category | Question |
| --- | --- | --- |
| 1 | Expertise | How credible is W as an expert source? |
| 2 | Field | Is W an expert in the field that P is in? |
| 3 | Opinion | What did W assert that implies P? |
| 4 | Trustworthiness | Is W personally reliable as a source? |
| 5 | Consistency | Is P consistent with what other experts assert? |
| 6 | Backup evidence | Is W's assertion based on evidence? |

The paper notes that Walton et al.'s scheme has four increasingly sophisticated versions; the most
sophisticated integrates the critical questions into the scheme itself so it is complete in itself.
Where critical questions are folded in, **each question becomes an additional premise**. Rainer keeps
them separate to show each contribution. In Toulmin terms (Fig. 3), an argumentation scheme provides
the **backing B** for the generalisation **G** that warrants the inference from evidence E to
proposition P.

**Critical questions for other schemes** — these function as per-claim quality tests and are directly
reusable:

- **Argument-by-analogy (Table 6).** CQ1 — Are there respects in which C1 and C2 are too different,
  which would undermine the force of the cited similarity? CQ2 — Is A the correct conclusion to draw
  from C1? CQ3 — Is there some other case C3 also similar to C1 but from which a different conclusion
  should be drawn?
- **Argument from example (Table 8).** 1 — Is the proposition claimed in the premise in fact true?
  2 — Does the cited example support the generalisation it is supposed to instantiate? 3 — Is the
  example typical of the kinds of case the generalisation covers? 4 — How strong is the
  generalisation? 5 — Do special circumstances of the example impair its generalisability?
- **Argument from popular opinion (Table 8).** 1 — What evidence, such as a poll or an appeal to
  common knowledge, supports the claim that A is generally accepted as true? 2 — Even if A is
  generally accepted, are there good reasons for doubting it is true? The paper points out that this
  scheme "is relevant to the conduct of surveys", a common SE practice: a survey finds that a
  majority of respondents report P true and infers that there is reason to favour P. **The critical
  questions therefore apply to research instruments, not only to practitioner content.**
- **Argument from distress (Table 8).** 1 — Is x really in distress? 2 — Will y's bringing about A
  really relieve it? 3 — Is it possible for y to bring about A? 4 — Would the negative side effects
  of y's bringing about A be too great?
- **Argument from danger appeal (Table 8).** Critical questions not specified.

**The three ways to attack (and therefore judge) a defeasible argument** (Walton et al., Section
3.2): attack a premise (d or E in the model), attack an inference (G or B), or present a
counter-argument.

**The Principle of Charity (Section 3.2).** Because defeasible arguments routinely leave premises,
conclusions or inferences unstated, they are easy to attack and prematurely dismiss. The evaluator
should therefore first interpret the argument in its **most robust, persuasive form** before
evaluating it — the point being to evaluate the best available argument rather than the one easiest
to criticise. This is a procedural safeguard against under-crediting grey material.

**Defeasibility is not fallacy (Section 3.2).** Walton et al. are quoted: a defeasible argument is one
whose conclusion can be accepted tentatively given the evidence known so far but may need to be
retracted as new evidence arrives; the typical case rests on a generalisation subject to
qualifications. Common defeasible forms such as expert opinion were long classed as fallacious in
logic textbooks. The paper's stance, following Walton, is that condemning expert evidence as
fallacious is not helpful — "the problem is to judge in specific cases when an argument from expert
opinion can properly be judged as strong, weak or fallacious." Rainer's own position is that **both
researchers and practitioners must inevitably make defeasible arguments**, because of constraints on
research, constraints on decision making in practice, and the complex, often invisible,
always-changing nature of software practice.

**Story elements as a proxy for personal experience (Section 3.5).** The paper hypothesises that
information containing Bex's story elements, or Twining/Ricoeur's, "is more likely based on
practitioner's personal experience", and that story elements connected by argument to propositions
suggest beliefs more likely justified by personal experience than by peer opinion, a mentor's
opinion, a trade journal, or research. The elements: for Bex, a story is a coherent sequence of
events, often involving subjects, objects, outcomes and other attributes, and he is interested in the
moral of a story, the values it promotes, and how it persuades. For Twining, drawing on Ricoeur, a
story is a narrative of particular events arranged in time sequence forming a meaningful totality,
whose necessary elements are **particularity, time, change and connectedness between events** — where
connectedness need not be causal. Twining also distinguishes stories from scenarios: one *narrates*
stories but *describes* scenarios. Twining separately distinguishes generalisations that are
logically necessary in rational argument from stories that are psychologically necessary in human
decision making.

**Detail as a proxy for directness of experience (Section 7.1).** Comparing the four examples, the
practitioner gives more detail when drawing on his own direct experience than when relaying others'
indirect experience — more events in the story, more detail of the situation. Two hypotheses are
drawn: researchers who push practitioners toward their *own* personal experience should get richer,
more detailed responses; and researchers could **test the degree to which a belief rests on personal
versus indirect experience by comparing the amount of detail offered in its support or refutation**.

### Process steps

**Four research objectives (Section 5.1)**, which are effectively the appraisal pipeline:

1. evaluate the **competence of the producer** — e.g. how far the practitioner who wrote the report
   can be considered an expert witness;
2. evaluate the **credibility of the information** — e.g. the relevance and inferential force of the
   stories and arguments in the report;
3. examine how credible information from a competent practitioner can be used as evidence and
   argument in relation to practitioners' beliefs and explanations;
4. examine how practitioners' evidence, arguments, beliefs and explanations relate to findings from
   other studies of practice.

**Methodology overview (Fig. 6, Section 5.2).** Reports are treated as testimonial information;
argumentation schemes and argumentation maps are used to identify, aggregate and evaluate their
evidence, inferences and beliefs. The flow is **considerably iterative**: identify one or more texts
→ identify relevant excerpts within each text → for each excerpt identify components of arguments,
evidence and explanations. An excerpt may yield zero, one or many arguments, items of evidence or
explanations, and **it is during identification and construction that the analyst can properly
determine whether any of these are present at all**. Once an excerpt's individual arguments, evidence
and explanations are sufficiently developed, they are integrated into an **Argument-eXplanation-
Evidence (AXE) structure** for that excerpt; the per-excerpt AXE structures are then aggregated into
an overall AXE structure. Each stage produces artefacts — marked-up excerpts, structured textual
summaries of the excerpt's components, and excerpt-specific argument maps.

**The 31 steps (Appendix A).** Grouped by phase:

*Selecting a text (step 1).* Read the texts of interest to understand both overall meaning and the
meaning of specific parts. Select texts relevant to your topic that, on initial review, appear to
contain substantive arguments and inferences, stories, analogies and examples, or explanations.

*Extracting excerpts (steps 2–5).* Read the text several times, iterating over the methodology's
steps as you read. Look for coherent, relatively self-contained sections containing one or more
inferences, stories, analogies, examples or explanations — grammatical structures such as paragraphs
and subsections often suggest them. Extract candidate excerpts, e.g. into their own text file. Note
that a single excerpt may contain both explicit arguments and explicit stories, so it must be
evaluated **as an argument and as a story**, with one or more argument maps built and then merged.

*Extracting arguments (steps 6–13).* Border the indicators of inference (Table 17). Cross out
statements not relevant to the emerging argument, to simplify the material. Identify reasons — they
tend to occur close to inference indicators. Mark up the argument components (Table 18). Extract and
rearrange the components so there is an explicit chain from premises to conclusions. **Note any
information missing from the argument** that would help understand or clarify it. Rephrase components
carefully where that clarifies meaning. Prepare an argument map.

*Extracting personal experience / stories (steps 14–22).* Identify indicators of personal experience,
e.g. story events. Mark up the story components (Table 19). Cross out irrelevant statements. Identify
explicitly stated explanations in the story — noting these are **not necessarily causal**. Note
missing information. Rephrase for clarity where helpful. **Identify the moral of the story**, which
is often implied rather than stated and which becomes a candidate conclusion for an
argument-from-story. Choose appropriate argumentation schemes — argument from story, from analogy,
from example. Prepare argument maps.

*Extracting explanations (steps 23–30).* Border explanation indicators, taking care because
explanations are distinct from arguments and action verbs (making, doing, creating) suggest a cause.
Cross out irrelevant statements. Identify explanations, which may occur near explanation indicators
and **may be implied rather than stated** — a story may rest on an unstated explanation. Mark up the
explanatory components. Extract and rearrange them into an explicit structure. Note missing
information. Rephrase for clarity, which the paper says matters particularly for unstated
explanations. Prepare an argument map showing the explanation in relation to an argument.

*Aggregating (step 31).* Once a set of argument maps exists, aggregate them into a larger structure
to better understand the overall argument the author is putting forward.

**Integrating with research evidence (Section 6.7).** Two directions in which a practitioner belief
and research evidence can be related, both presented as routes to EBSE:

1. A practitioner puts forward a belief, possibly with supporting personal experience, and
   researchers test that belief using evidence from empirical research. Here the *research evidence*
   is selected for its relevance to the practitioner's belief; it may corroborate or rebut.
2. A researcher has published empirical findings and seeks ways they can be applied to or integrated
   with practitioners' personal experiences. Here the *practitioner's belief and evidence* is
   selected for its relevance to the research evidence.

### Search and sampling techniques

This paper is not a search-methods paper; sampling is its acknowledged weak point.

- **The demonstration sample is one blog post.** *Language Wars*, published by Joel Spolsky to *Joel
  on Software*, chosen because it concerns technology stacks and technology adoption. Deliberately a
  single post, so the examples stay coherent and concentrated — using several posts would require
  background on each and risk fragmenting the analysis. The post is roughly two A4 pages: **1,300
  words, 20 paragraphs, 90 lines of text**. Several excerpts were identified and analysed; **four**
  are presented, space-constrained.
- **Recency was explicitly not a selection criterion.** The post was a decade old at the time of
  writing; the stated interest is in *how the practitioner argues* and uses evidence and
  explanations, not in the post's contemporaneousness. Useful precedent: for method-focused analysis
  of reasoning, currency criteria may be inapplicable.
- **Scaling plan (Section 7.7).** A toolset comprising a **web crawler, a topic classifier, and a set
  of consolidated argument indicators**, piloted on the Joel Spolsky blog site with **over 1,000 blog
  articles**. The stated target is **40,000 articles from over 20 blogs**, from which a subset would
  be carefully selected to build a marked-up corpus. That corpus must contain a **balanced set of
  positive and negative examples**, covering arguments, evidence and explanations, for training
  purposes; it would then train and evaluate machine-learning algorithms to identify automatically
  those blogs and articles containing arguments, evidence and explanations, with further analysis via
  argumentation mining and experience mining.
- **Other corpora suggested for the same treatment:** the Python Enhancement Proposals (PEP) as a
  rich dataset of email exchanges representing different participants' views, and StackExchange /
  Stack Overflow.

**No stopping rule or effort bound is given**, and the paper is candid that the manual methodology's
resource requirements themselves cap how many examples can be investigated at a time.

### Caveats, traps and pitfalls

- **Beliefs need not track evidence from the practitioner's own project.** Devanbu et al. found a
  practitioner's beliefs do not necessarily correspond with actual evidence from the project the
  practitioner is currently working on. The paper calls this "a significant challenge" and derives
  the required discrimination: separate opinions grounded in the practitioner's *immediate personal
  experience* from opinions formed from other sources.
- **Source credibility can outweigh content.** Schum is quoted: what we believe we know about the
  credibility of a person giving testimony "is often at least as inferentially important as what this
  person tells us."
- **Conclusions are usually implied, not stated.** In every one of the four worked examples the main
  conclusion is only implied (e.g. *do not use Lisp for developing critical web applications*), and
  the paper reports generally that "conclusions to arguments are often left implied" and that only a
  small amount of explicit explanation is stated. An extraction process that requires explicit
  conclusions will find nothing.
- **Missing premises make arguments easy to dismiss unfairly** — hence the Principle of Charity.
- **Implied causality is a reader artefact.** In Example 1 the two-event story contains no explicit
  causal information, but the ordering of events may imply causation to the reader — using Ruby on
  Rails "causes" 37 Signals to make money. The analyst must not import causation the text does not
  assert.
- **Explanations may be entirely unstated**, and a story may depend on one (step 25 and Section 6.6).
- **Ambiguous indicator words.** "Because" may indicate a cause in an explanation *or* a reason in an
  argument; "so", "for", "since" and "consequently" straddle inference and event. The mark-up must be
  flexible enough to allow **concurrent tagging of the same chunk of text**.
- **Expertise cannot be assessed from the document alone.** Stated plainly: "Assessing the expertise
  of a blog writer will likely require information beyond the blog post itself" — the paper's own
  footnote points at Spolsky's Wikipedia entry.
- **Personal reliability is hard to assess at all.** The answer given to critical question 4 for
  Spolsky is that it is difficult to assess personal reliability, though the writer is a well-known
  public figure in his field. Public prominence is offered as a partial and admittedly weak proxy.
- **Consistency with other experts requires separate work** — critical question 5 could only be
  answered by analysing other experts' views and empirical evidence.
- **Practitioners argue toward general conclusions from particular experience.** The conclusions are
  generalised practical propositions of the form "in situations of type S, for applications of type
  A, do not use X" — inferred from one or two cases.
- **Practitioner argument may omit rigorous evidence entirely.** In the four examples analysed, the
  practitioner "does not reference any evidence resulting from rigorous empirical study", though the
  author flags the sample is small. He does occasionally use URLs to provide corroborating or
  clarifying information.
- **Practitioners prefer local data and expertise.** Consistent with Rainer et al.'s earlier finding,
  the blog writer references other practitioners' stories chiefly in order to argue *against* the
  conclusions those stories imply.
- **Limitations the paper states of itself (Section 7.6).** Applied to only a few cases; needs more
  and more carefully worked examples, from other blogs and other kinds of naturally produced report,
  and crucially **negative examples — cases where argumentation schemes cannot be applied**; needs
  scale to gauge representativeness; the framework and methodology need further development,
  including applying the evidential tests the way Wohlin applied his grading profile; and the
  methodology is **manual**, requiring effort to work and rework analyses, which constrains how much
  can be studied.
- **Generalisability, two open questions (Section 7.2).** Do findings from the illustrative examples
  generalise to other examples from practitioners' blogs? — left to further research, requiring
  either a larger carefully selected sample for statistical generalisation or an analytical framework
  for analytical generalisation. Do argumentation schemes generalise from law to SE research? — the
  paper answers this by argument-from-analogy, i.e. by its own method: law and SE research are
  sufficiently similar in that both must handle information, evidence, inference and beliefs from
  people and must deal with testimonial evidence from witnesses including expert witnesses; schemes
  are well developed in law; therefore it should be possible to exploit them in SE. This is, self
  consciously, a defeasible argument.
- **Retrospective analysis is only one option (Section 7.7).** The analysis reported is retrospective
  analysis of an existing document. Alternatives: prospective analysis, designing interviews or focus
  groups to gather new data — e.g. asking practitioners to present arguments and evidence about
  technologies they adopted — which allows more detailed, concentrated collection; and a "seeding"
  design that presents existing arguments, evidence and explanations and asks practitioners to
  evaluate them.

### Metadata requirements

- **Chain of custody** — how the report came to be written and disseminated — is a named requirement
  for treating the document as credible tangible evidence (Section 3.8).
- **Author identity and biography, sourced externally.** The worked answers to the expert-opinion
  critical questions for Spolsky record years of experience as a developer, six-plus years of
  blogging about software development at the time of the post, and a career record (created Trello,
  Program Manager on the Microsoft Excel team, worked for Viacom and Juno Online Services, founded Fog
  Creek Software, co-launched Stack Overflow). None of this is in the blog post; it must be gathered
  and recorded separately.
- **Domain of expertise, recorded as such** — critical question 2 asks whether W is an expert in the
  field *that P is in*, so the extraction must record both the claim's domain and the author's
  domain. Section 6.6 notes that Example 4 is valuable partly because it supplies information about
  the domain S in which the writer is expert, which then feeds back into the critical questions.
- **Publication date**, since the paper explicitly reasons about the post being a decade old and
  distinguishes cases where currency matters from cases where it does not.
- **Provenance of every claim as primary or secondary information** — whether it is clearly informed
  by the author's own experience or relayed from peers, mentors, trade journals or research.
- **Citations within the document, typed.** The mark-up carries `<CITATION TYPE={URL | …}>` for
  arguments and a `<CITATION>` element for stories, so cited sources are recorded as structured
  elements rather than prose.
- **Unique IDs on every extracted component** — arguments, reasons, inferences, explanations, stories,
  events, agents all carry `ID = [unique numeric identifier]`, which is what makes the argument maps
  and the aggregate AXE structure traceable back to text.

### Data extraction and analysis techniques

**Indicator words (Table 17).** The trigger list used to spot components, with the ambiguity mapped
explicitly across three columns:

| Indicator | Inference in argument | Event in story | Explanation |
| --- | --- | --- | --- |
| Therefore… | suggests a conclusion | | |
| So | suggests a conclusion | suggests an event | |
| Hence | suggests a conclusion | | |
| Consequently | suggests a conclusion | suggests an event | |
| Because | suggests a premise | | suggests an explanation |
| For | suggests a premise | suggests an event | |
| Since | suggests a premise | suggests an event | |
| When [and other time indicators] | | (listed as a story/time indicator) | |
| Next | | suggests an event | |
| Who, I, we, they [personal nouns] | | (listed as a story indicator) | |
| do, doing, did [actions] | | | suggests an explanation |
| Cause, causes, causing | | | suggests an explanation |

General guidance (Section 5.3): "therefore" suggests a conclusion and hence a potential argument;
"cause" suggests an explanation; **proper nouns and events suggest stories**.

**Mark-up notation for arguments (Table 18).** Main elements: `<ARGUMENT>` (suspected argument
present), `<REASON>` (a reason that may be premise, conclusion, or other part of an argument),
`<INFERENCE>` (an inference indicator), `<EXPLANATION>` (some explanation, not necessarily causal —
may simply clarify something; possibly to be subsumed into an assertion tag later), `<THEREFORE>` (a
tag inserted to clarify the relationship between two assertions), a strike-out convention for text
ignored in presentation (formally `<ignore>`), and `<IF… THEN…>` for a hypothetical. Each carries a
unique numeric ID. Elements flagged for future development: `<CONCLUSION>` — a **bracketed** reason
or conclusion marks a component that is *implied in the excerpt but not explicitly stated*;
`<QUALIFIER>` — indicates the assertion applies to a specific case or class of cases; `<EVIDENCE>`;
`<CITATION TYPE={URL | …}>`.

**Mark-up notation for stories (Table 19).** `<STORY>` with a unique ID; `<EVENT>` with a unique ID
and `TYPE = {ACTION | OUTCOME | BENEFIT | …}`, where *outcome* refers to a result or consequence
arising in the story; plus the ignore convention. Flagged for future development: `<CHARACTER>` — a
character or other autonomous agent within the story — and `<CITATION>`. The paper states the
notation needs extending to handle additional concepts (context, emotive language) and additional
attributes for stories such as characters and outcomes.

**Representation template (Table 9).** Each analysed excerpt is written up as: Section / Marked-up
excerpt / Structured textual representation of argument, story and explanation / Argument / Evidence
(e.g. story, analogy) / Explanation / Argumentation scheme / Main beliefs or conclusions abstracted
from the argument or story. The textual representations are interim; **argument maps** — undirected
and directed graphs — are the second representation, used both at the level of individual arguments
and at the level of aggregated arguments.

**Argumentation schemes as the catalogue (Table 2).** Walton et al. analyse over **60** schemes.
The classification reproduced covers: *Reasoning* — deductive (modus ponens, disjunctive syllogism,
reductio ad absurdum), inductive (argument from a random sample to a population), practical reasoning
(from consequences, from alternatives, from waste, from sunk costs, from threat, from danger appeal),
abductive (argument from sign, argument from evidence to a hypothesis), causal (cause to effect,
correlation to cause, causal slippery slope); *Applying rules to cases* — arguments based on cases
(from example, from analogy, from precedent), defeasible rule-based arguments (from an established
rule, from an exceptional case, from plea for excuse), verbal classification arguments (from verbal
classification, from vagueness of a verbal classification), chained arguments connecting rules and
cases (from gradualism, precedent slippery slope, sorites slippery slope); *Source-based arguments* —
arguments from position to know (position to know, witness testimony, expert opinion, argument from
ignorance); *Arguments from commitment* (inconsistent commitment); *Arguments attacking personal
credibility* (allegation of bias, poisoning the well by alleging group bias, ad hominem); *Arguments
from popular acceptance* (popular opinion, popular practice). The paper also uses **defeasible modus
ponens** (Verheij), which allows exceptions to the universal generalisation of classic modus ponens.

**Story-related schemes.** Argument-by-analogy (Table 5): *Major premise* — generally, case C1 is
similar to case C2; *Minor premise* — P is true (false) in C1; *Conclusion* — P is true (false) in
C2. Practical reasoning based on a story (Bex, Table 7): *Major premise* — character x performs
action A, which promotes (demotes) value V, and gets positive (negative) results [outcome O]; *Minor
premise* — I am in a situation as character x; *Conclusion* — therefore I should (not) prefer actions
that promote (demote) value V. No critical questions are given for this last scheme. Broadly, stories
can serve as evidence in their own right (argument-from-story) or form the basis of an
argument-by-analogy; either way they enter the model as evidence for a proposition, with **the minor
premise becoming the evidence E and the major premise supplying the generalisation** that supports
the inference to P.

**Relation to conventional qualitative analysis (Section 7.4).** Qualitative analysis typically codes
each excerpt against one or more categories, which then permits some quantitative analysis. This
framework instead analyses **the semantic structure of each excerpt in more detail**, letting the
researcher look closely at the relationship between evidence, arguments and beliefs. The paper
suggests it is particularly useful for designing interview protocols that *probe* for the inferences,
evidence (e.g. stories articulating personal experience) and explanations that support a
practitioner's beliefs.

**Suggested contribution to synthesis (Section 7.5).** Because a large number of schemes exist and
they apply to diverse evidence, argumentation schemes could provide "a new, flexible and
complementary approach to synthesising evidence and to knowledge translation" — integrating
practitioner expertise into steps 1–3, and separately into step 4, of the evidence-based paradigm.

### Empirical findings worth citing

- **Ranking of information sources by practitioners.** Devanbu et al.'s large Microsoft survey,
  **564 respondents**, asked for opinions on claims about software engineering and for a ranking of
  the sources that influenced those opinions. Ranked highest to lowest: **personal experience, peer
  opinion, mentor/manager, trade journal, research paper, other.** Research papers rank second to
  last. Devanbu et al. also found a practitioner's beliefs do not necessarily correspond with actual
  evidence from the project they are currently working on.
- **What practitioners most value.** Rainer et al.'s earlier work found practitioners most valued
  information provided by other practitioners, the ideal being information sourced from a **local
  expert**.
- **What the practitioner actually used as evidence.** Across the four analysed excerpts, Spolsky
  uses **(factual) stories, analogies, examples, and popular opinion** as evidence, and uses that
  evidence in defeasible reasoning both to justify his own beliefs and to rebut other practitioners'
  beliefs. He argues against other practitioners' stories, and for or with stories from his own
  professional experience. **He cites no rigorous empirical study** in these four examples.
- **Three forms of the experience–argument relationship** observed: experiences (e.g. stories)
  presented in isolation from an argument; aligned with an argument; or connected to an argument.
- **Yield per unit of text.** The four illustrative excerpts are short in word count, yet each
  "contains substantial information from which relatively sophisticated argument maps are derived" —
  a 1,300-word post supported four analysed excerpts with multiple argument structures each. Example
  1 alone yielded two argument structures — an incomplete argument from analogy or from story, and a
  rebuttal comprising three further structures (defeasible modus ponens, argument from distress,
  argument from danger appeal). Example 2 yielded three structures: argument from analogy or story
  including a simple causal explanation, a rebuttal of that causal explanation based on a *negative*
  argument from popular opinion, and a rebuttal of the original argument by re-interpreting the
  analogy — i.e. the practitioner both attacks a premise *and* presents a counter-argument.
- **Corroborating research evidence used in the demonstration.** El Emam and Koru's replicated web
  survey of software project failures, reasons for cancellation, **n = 18**: senior management not
  sufficiently involved 33%; too many requirements and scope changes 33%; lack of necessary
  management skills 28%; over budget 28%; lack of necessary technical skills 22%; no more need for
  the system 22%; over schedule 17%; **technology too new / didn't work as expected 17%**;
  insufficient staff 11%; critical quality problems with software 11%; end users not sufficiently
  involved 6%. The paper's reading (note it discusses *technology too new* as ranking 8th at 11% in
  the prose while the table shows 17%, so treat the prose figure with care —
  **[EXTRACTION UNCLEAR: prose says "Technology too new, ranks low in the table (8th) with 11% of
  responses" but Table 16 lists 17% for that row; the 11% rows are "Insufficient staff" and "Critical
  quality problems"]**) is that in relative terms **technical skills matter more than the technology**
  (22% vs. the technology row), which **corroborates** Spolsky's belief that experience matters more
  than technology, while simultaneously **elaborating** it by showing several more significant
  factors he ignores — management involvement and requirements churn both at 33%. This is the paper's
  demonstration that research evidence can corroborate and enrich a practitioner belief at once.
- **Scale of the pilot:** over **1,000** blog articles crawled from one blog site; target **40,000**
  articles from over **20** blogs.

