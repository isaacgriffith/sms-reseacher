# Batch 3a — Search strategy and snowballing (Wohlin)

Synthesis in my own words from the plain-text extractions. Direct quotation is used sparingly and
kept short; everything else is paraphrase. Section numbers refer to the source papers.

---

## wohlin_2014 — "Guidelines for Snowballing in Systematic Literature Studies and a Replication in Software Engineering" (EASE '14, pp. 321–330)

**Type:** Guideline (procedure definition) + a worked replication used as its evaluation.

**Role in corpus:** This is the only paper in the corpus that specifies snowballing as an
executable, step-by-step search procedure — start set, iteration loop, backward and forward
passes, the use of *where in the text* a reference appears as a screening signal, the
author-contact closing step, and the termination rule. Everything else in the corpus either
assumes database search or discusses snowballing only in outline.

### Process steps or stages defined (Section 3; procedure summarised in the paper's Figure 1)

Wohlin is explicit up front (Section 3, opening) that snowballing changes only the *search*.
Planning, motivation, protocol and the rest of the study design are unchanged from Kitchenham &
Charters' guidelines; the snowballing procedure substitutes for the database-search step alone.

#### Choosing the start set (Section 3.1)

Under database search the first move is to build keywords and a search string. Under snowballing
the equivalent first move is to assemble a **start set** of papers to snowball from. Wohlin
draws a sharp distinction that matters for reporting:

- A search produces a **tentative start set** — the candidates.
- The **actual start set** is only the subset of those candidates that survive inclusion screening
  and end up in the study. Papers that are never included must never be snowballed from.

He recommends running the start-set search in **Google Scholar specifically because it is not tied
to a single publisher**, so the start set does not inherit one publisher's coverage as a bias.

Characteristics of a good start set (his enumerated list, condensed, in his order):

1. **Community coverage.** If relevant work plausibly comes from more than one research
   community, each community must be represented in the start set. This matters most when there
   is a risk of *independent clusters* — groups of papers that simply do not cite each other, and
   which snowballing therefore cannot bridge.
2. **Not too small.** Size should scale with the breadth of the topic: a narrow, specific topic
   needs fewer start papers than a broad one.
3. **Too-large is also a failure mode.** If very general Google Scholar terms return an unwieldy
   candidate set, fall back to picking a number of clearly relevant, highly cited papers.
4. **Diversity across publishers, years and authors.** Diversity is stated as the point of the
   criterion, not a nice-to-have.
5. **Derive it from the research question's keywords, plus synonyms.** The synonym requirement
   exists to stop the start set from being locked to one terminology and silently missing papers
   phrased differently.

He concedes there is no silver bullet here, and that identifying a good start set is as hard as
identifying good search strings; one workable tactic is to find a seminal, highly cited paper in
the area. He flags start-set identification as open future research (also repeated in Section 5).

*Terminology example he cites (Section 3.1, from Jalali & Wohlin 2012):* in a study of agile
practices in global software engineering, a paper phrasing the concept as "cross-continent"
development was missed entirely by the database search, but surfaced obviously during
snowballing. He uses this as the concrete illustration of why inconsistent terminology defeats
search strings and why snowballing is robust to it.

#### The iteration procedure (Section 3.2)

Once the actual start set is fixed — again, only papers that *will* be included — iteration
begins. Each iteration runs backward snowballing and forward snowballing over the current set of
papers. The controlling rule for the whole procedure:

> A paper's full text must be examined and a definite include/exclude decision reached **before**
> that paper is used for snowballing. Otherwise, if the paper is later excluded, everything found
> through it must be rolled back and removed.

Newly included papers from an iteration are collected into a pile that becomes the input of the
next iteration. Wohlin insists on running **one iteration at a time**, explicitly for
traceability.

#### Backward snowballing — what is examined (Section 3.2.1)

Working from the reference list of the paper under examination:

1. **First pass — trivially excludable references.** Remove references failing basic criteria:
   language, publication year, publication type (e.g. if only peer-reviewed work counts).
2. **Second pass — remove already-seen references.** Drop references already examined in this or
   an earlier iteration, whether they were reached by backward or forward snowballing. What
   remains are genuine candidates.
3. **Third pass — extract everything obtainable from the citing paper before leaving it.** This is
   the core efficiency principle: get as much as possible out of the paper in hand, and do not go
   fetch the candidate paper until the paper in hand has nothing left to say. From the reference
   list entry itself, three signals are evaluated:
   - **Title** — is this tentatively includable?
   - **Publication venue** — is it a venue where relevant work appears?
   - **Authors** — have these authors published relevant work in this area before?

   Wohlin is careful about the author signal: a paper may **not** be excluded on the ground that
   its author is not known in the area; a known author only makes inclusion *more likely*. The
   reference-list information must be weighed, not applied mechanically.

4. **Fourth pass — the place and context of the reference.** If the candidate still stands, go and
   look at *where in the examining paper the reference is cited and how it is used*. The location
   and surrounding sentences carry information about the candidate's actual content, and getting
   it from the paper in hand is cheaper than retrieving the candidate. Wohlin returns to this in
   the conclusion (Section 6), calling the place and context of references in both backward and
   forward snowballing "a key to success" for the whole procedure.

5. **Fifth pass — retrieve the candidate.** Only when the examining paper is exhausted. Read the
   abstract first, then read further only until a definite include/exclude call can be made. He
   explicitly recommends *not* reading front-to-back; browse and read the most decision-relevant
   parts.

Lesson 4 (Section 4.9.1) adds a refinement: **iterate between the reference list and the citation
context**. Once a reference is found worth including, go back and look at the other references
used *in a similar way* in the same passage — they are strong candidates too.

#### Forward snowballing (Section 3.2.2)

Forward snowballing identifies new papers from those **citing** the paper under examination.
Citations are obtained from Google Scholar, with quotes removed so that only citations count.
(The 2016 paper adds patents to the things to untick.) Screening is a cheapest-signal-first
cascade:

1. Screen on the information Google Scholar itself displays in the result listing.
2. If that is insufficient, read the abstract.
3. If still insufficient, look at the place in the citing paper where the already-included paper
   is cited.
4. If still insufficient, read the full text.

Lesson 5 (Section 4.9.1) gives the forward analogue of the backward refinement: for a newly found
citing paper, look at *where it cites the paper that led you to it*, and pick up the other papers
it references in the same way. Wohlin notes this is easily missed, because the paper that led you
there was already found and so its own reference list is typically not re-examined in the backward
pass.

#### Inclusion/exclusion within an iteration (Section 3.2.3)

- Decide include/exclude **before** using any new paper for snowballing (the rollback rule again).
- Only papers reached through *included* papers may be used in the analysis.
- After both backward and forward passes complete, the new inclusions form the next iteration's
  pile.

#### Stopping rule and the closing steps (Section 3.3)

The loop ends when **an iteration of both backward and forward snowballing yields no new papers.**

That is not the end of the search. Two complements follow:

- **Contact the authors** of the included papers to surface further papers, prioritising the most
  active researchers in the area. Wohlin's phrasing is that snowballing should be done on
  *authors* as well as papers. If author contact produces new papers, **the whole procedure of
  Figure 1 must be restarted** with them.
- **Targeted venue search.** Search specific journals or conferences likely to carry more work on
  the topic, identified by looking at where the included papers were published.

#### Data extraction (Section 3.4)

Extraction follows the study's research questions as normal. Wohlin's specific observation: since
snowballing already forces full-paper examination before a paper enters the procedure, it may be
efficient to **perform data extraction at the same moment as the inclusion decision**, rather than
as a separate later pass.

### Search-quality measurement techniques

Wohlin does not use recall/precision/F-measure or a quasi-gold standard. He uses a single
efficiency ratio and reports it at each stage (Section 4.6):

> **efficiency = number of papers included / number of candidate papers examined**

Reported values from the replication:

| Stage | Included / examined | Efficiency |
|---|---|---|
| Start set | 3 / 13 | 23% |
| Iteration 1 | 7 / 25 | 28% |
| Iteration 2 | 1 / 223 | 0.4% |
| Iteration 3 | 0 / 33 | 0% |
| **Overall** | **11 / 294** | **3.7%** |

He then argues this raw figure understates the method, because it counts every reference-list line
that was dismissed on publication year (trivial) or on title. Recomputing over only those
candidates that required real work — i.e. reading the Google Scholar entry, the abstract, or the
paper — gives:

- Start set: 3 of 13 (unchanged)
- Backward: 7 of 12 in Iteration 1 (instead of 7 of 25); 0 of 3 in Iteration 2 (instead of 0 of
  97); 0 of 0 in Iteration 3 (instead of 0 of 26)
- Forward: 1 of 133 across the three post-start-set sets
- **Combined: (10+1)/(28+133) = 6.8%**, with backward snowballing carrying almost all the yield.

He immediately qualifies this (Section 4.6): title-based exclusion is a delicate balance. **Had he
been strict about titles, five of the eleven included papers — P4, P5, P7, P9 and P11 — would have
been excluded.** That is a very concrete warning that title screening in reference lists is where
the recall is lost.

For comparison across methods he falls back on "papers reviewed in detail" as the effort proxy
(Section 4.10, Table 2): Review 1 in MacDonell et al. reviewed 24 in detail, Review 2 reviewed 38,
snowballing reviewed 38 — i.e. **roughly the same effort by that measure**. He notes actual clock
effort was not available in any of the three.

### Reliability and agreement techniques

No inter-rater statistics are computed — the replication is a single-researcher study, which he
acknowledges. Reliability is instead assessed by **outcome overlap against a prior independent
study**: the snowballing replication identified essentially the same papers, with **nine studies
in common with both of the systematic reviews reported by MacDonell et al.** He also notes that
MacDonell et al. judged one of their included papers as one that should have been excluded on
analysis type, and that this paper is P11 — the paper that his citation matrix had already flagged
as anomalous (not cited by P1–P3). His point: the citation matrix can surface papers deserving
closer scrutiny.

Two lightweight analysis instruments he proposes as reliability aids (Section 4.8, lessons 9–10):

- **Citation matrix.** An N×N matrix of included papers, "X" where row cites column, "–" where a
  citation was chronologically impossible. A matrix with many blank cells (i.e. many possible-but-
  absent citations) is a warning that other papers may have been missed. He states its limitation
  plainly: it cannot detect a genuinely independent cluster.
- **Timeline of publication years.** Establishes which citations were even possible, and gives a
  read on activity in the area. He notes two reasons the "possible to cite" inference is
  imperfect: publication lag means a nominally available paper may not have been available when
  the citing paper was written, and authors can cite their own not-yet-published work (P2 is cited
  by P11 for exactly this reason).

### Caveats, traps and pitfalls

On database search (Section 2, and Section 5):

- Automated search is not intrinsically better than manual — the real variable is being
  *systematic*. **A database search is never better than its search string.**
- Good search strings are hard because terminology is not standardised; broad terms return large
  numbers of irrelevant papers, generating substantial and error-prone manual work.
- The practical difficulties compound: selecting databases, incompatible interfaces, different
  search-string syntaxes, different search limitations per database, and identifying synonyms.
- Two consequences he draws explicitly: **(1)** the first step in the search strategy usually
  becomes the *only* step, because the complementary searches the guidelines recommend (reference
  lists, grey literature, specific outlets, contacting researchers) are too costly and are
  routinely skipped; **(2)** important literature is therefore missed.
- The "identify all relevant research" objective is fine as an objective but unlikely to hold in
  practice, especially for broad areas. He cites Kitchenham et al.'s manual search finding 20
  papers, and the same authors' automated repeat finding **33 additional** studies, as the
  illustration that we are always accepting a *sample*, and the job is to get the best possible
  sample from the population.

On snowballing specifically:

- **Start-set bias is the principal threat.** In his own replication he flags his start set as
  "far from perfect" because all three papers shared an author, and states plainly that it would
  have been better to have at least one paper from a different author group to mitigate the risk
  of missing papers not linked to those three. He took no action only because the design required
  using the replicated study's research question as the starting point.
- **Independent clusters.** Snowballing cannot reach a cluster of papers that neither cites nor is
  cited by anything in your set. This is why start-set diversity is criterion 1 and why the
  citation matrix cannot rescue you.
- **Heavy overlap in reference lists is ambiguous** (lesson 2). Seeing the same references
  repeatedly — especially across papers by the same authors — means *either* that you have
  captured a good portion of the area *or* that you have found one author cluster and other
  clusters exist.
- **Double-counting and bookkeeping noise** (lesson 6, and Section 4.4.1). Because a reference is
  processed the first time it is seen, the number of references to process for a given paper
  depends on the order papers are examined. Wohlin admits candidly that with large reference
  lists a previously evaluated reference may be re-examined because the researcher does not
  remember it, so the reported counts carry some random error. He judged it inefficient to load
  references into a tool only to discard them immediately.
- **The screening-depth judgement is genuinely hard** (lesson 3): excluding on title generates
  less work but risks dropping includable papers; reading full texts is safe but expensive.
- **Google Scholar is not stable over time** (Section 4.2). What Google Scholar indexes changes,
  so the search date matters — though it mattered little in his case because the time frame was
  historical (1995–2005).
- **Non-decreasing discovery rate is a red flag** (lessons 7–8). Track how many new papers each
  step yields. With a good start set the count should fall each iteration. If it is *not* falling
  substantially, run a fresh search using synonyms of the research-question terms — the likely
  explanation is a missed cluster.

### Snowballing vs. database search — the argument

Wohlin's claim in this paper is deliberately moderate. From the abstract: using snowballing "as a
first search strategy, may very well be a good alternative to the use of database searches."

The argument, assembled from Sections 2, 5 and 6:

- Snowballing *starts from relevant papers* and uses them to drive the search, rather than
  starting from a string and hoping it matches. Reference lists are cheap to examine, and combined
  with the place/context of the reference it is usually straightforward to identify relevant
  papers.
- Because it works from actual citation relations, **noise may be lower than a database approach**
  — his phrasing is a possibility, not a demonstrated result.
- It is robust to terminology drift, where string-based search is not (the "cross-continent"
  example).
- Forward snowballing can be expensive when a paper is highly cited, but the Google Scholar
  listing is usually informative enough to make a tentative call cheaply.
- Section 5, stated flatly: **snowballing should not necessarily be seen as an alternative to
  database search.** Different approaches should preferably be used together for the best possible
  coverage.

He lists four open research needs (Section 5): (1) how to identify a good start set; (2) efficiency
evaluation across search approaches; (3) advantages/disadvantages of each approach in different
contexts — notably broad vs. narrow areas; (4) formulation of a good *hybrid* approach where the
approaches complement one another.

**The one strong claim** — the one the 2016 paper exists to test — concerns extension studies:
snowballing is *particularly* useful for extending an existing systematic literature study,
because a new study on the topic almost certainly cites at least one of the previously relevant
studies or the prior systematic study itself. He calls this "by deduction a better approach than
a database search for extending systematic literature studies" and explicitly leaves the evidence
for that assertion to further research.

He also cites contrary evidence honestly (Section 2): Skoglund & Runeson's reference-based search
raised precision without missing too many relevant papers for *technically focused* reviews, but
performed unsatisfactorily when the search area was wide or the terms general — from which Wohlin
concludes **the right search approach is context-dependent**. Greenhalgh & Peacock are cited for
the finding that protocol-driven search is not necessarily most efficient regardless of database
count, that some sources come only from personal knowledge and contacts, and that **snowballing is
the best approach for identifying sources published in obscure journals**.

### Threats to validity framework

No named framework (no construct/internal/external/conclusion taxonomy). Section 4.9.2 discusses a
single dominant threat and its mitigation:

- **Main threat — prior exposure.** The researcher had read the original MacDonell et al. study
  before deciding to replicate it. He argues this is essentially unavoidable, since having read it
  is what motivated the replication.
- **Mitigating circumstances.** The replication ran 6–12 months after reading, so details were not
  remembered. He does admit remembering the *approximate* expected yield — that the original
  studies found somewhere in the interval **10–19 papers**, though not the exact number — and
  concedes this may have influenced inclusion/exclusion decisions. His argument for why it does
  not invalidate the result: any such effect would change *where in the cascade* decisions were
  taken, not the number of papers examined.
- Also disclosed as design choices rather than threats: the author-contact step was deliberately
  **not** performed, because several authors of the included papers also authored the systematic
  review being replicated, so their responses would be biased by having seen it; and complementary
  searches were deliberately omitted to keep the comparison a clean snowballing-first vs.
  database-first contrast.

### Empirical findings worth citing

The replication target was MacDonell et al.'s reliability study, research question: what evidence
is there that cross-company estimation models are at least as good as within-company models for
predicting software project effort. Search executed in Google Scholar on 20 August 2013 with the
string `cross-company within-company software effort estimation`, time frame 1995–2005.

- Tentative start set: **13 candidates (C1–C13)**. Excluded: C9, C12, C13 (not peer-reviewed
  journal/conference/workshop); C8 (superseded — C7 is an extension of it); C4, C5, C6, C7, C10,
  C11 (out of scope). **Actual start set: 3 papers (P1–P3).**
- Iteration 1 backward: 25 candidates across the three (15 from P1, 4 from P2, 6 from P3) →
  **7 new inclusions (P4–P10)**. Notably, of the five candidates from P1, **two were identified
  from the title and three were identified from how they were referenced** — i.e. the place/context
  signal produced the majority of that iteration's finds. From P3, one paper (P10) came from the
  title and one (P9) from the reference context.
- Iteration 1 forward: **zero new papers.** All papers citing P1–P3 within the time frame were
  already in the tentative start set. Wohlin attributes this to the start set being published at
  the *end* of the time frame (2004, 2004, 2005) — so most discovery necessarily flowed backward.
- Iteration 2 backward: 97 new references examined across P4–P10; the large majority excluded on
  publication year or title; **only three required looking at the citation context**; zero new
  inclusions.
- Iteration 2 forward: 126 citations examined after removing already-seen ones; most excluded on
  the Google Scholar listing alone; **only 12 abstracts read**; **one new inclusion (P11)**.
- Iteration 3: 33 candidates (4 excluded on year, 22 on title from P11's 39 references, 7 citing
  papers excluded on the Google Scholar listing); **zero new inclusions** → stop.
- **Total: 11 included papers.** Nine are in common with both of MacDonell et al.'s reviews.
- Effort comparison (Table 2, papers reviewed in detail): Review 1 = 24, Review 2 = 38,
  snowballing = 38.

Structural finding he stresses in the summary and in Section 4.8: for this topic, **finding any
one of the eleven papers would have led to all the others.** It did not matter which paper was
found first. He acknowledges this makes the case unusually well-suited to snowballing.

Citation-matrix observations: P10, the earliest study, is cited by only four of the ten papers
that could have cited it. P11 is cited by none of the others despite three later publications and
despite sharing an author with P1–P3 — and P11 is precisely the paper MacDonell et al. said should
have been excluded.

---

## wohlin_2016 — "Second-Generation Systematic Literature Studies using Snowballing" (EASE '16)

**Type:** Empirical study (a method-comparison replication), not a guideline.

**Role in corpus:** This is the paper that supplies the evidence for the one strong claim left
dangling in Wohlin 2014 — that snowballing beats database search *for updating an existing
review*. It also defines the vocabulary of **generations** of literature study, and it is the only
paper here that specifies the reduced, forward-only snowballing protocol appropriate to an update.

### Process steps or stages defined

#### Terminology: generations rather than "extensions" (Section 1)

Wohlin argues against calling an update an "extended" study: "extended" is ambiguous (it could
mean adding a complementary *perspective* rather than a later time window), and it does not
compose — extensions of extensions become unwieldy. He therefore names an update by its
**generation**, where the generation number is the number of extensions. Kitchenham et al.'s
cross- vs. within-company review is the first generation (covering up to 2005); Mendes et al.'s
update covering 2006–2013 is the second generation.

#### The four-step snowballing search for a second-generation study (Section 2, end)

1. **Formulate the research questions** — for a second-generation study this means *copying* the
   research questions from the first-generation study.
2. **Identify the start set.** Keyword search in Google Scholar is one route (preferred for
   publisher neutrality); the actual start set is only those tentative papers ultimately included.
   For a second-generation study specifically, it should instead be possible to use **the
   first-generation systematic literature studies plus the primary studies they included** as the
   start set.
3. **Run the snowballing procedure** — normally both backward and forward.
4. **Screen each citing paper** through the cheapest-signal-first cascade: Google Scholar listing
   → abstract → the place where the already-included paper is cited → full text. Only *included*
   papers are snowballed from, which is why the include/exclude decision must be made.

#### How the second-generation protocol differs (Sections 3.2–3.4)

- **Start set composition (3.2):** two sources only — (1) published first-generation systematic
  literature studies on the topic; (2) the papers included by those first-generation studies. The
  second-generation database study being replicated was deliberately *excluded* from the start set,
  to keep the comparison fair.
- **Forward snowballing only (3.3).** No backward snowballing, on the grounds that the assertion
  under test is that newer relevant papers must cite the prior-generation review or its primary
  studies. He notes backward snowballing *could* have been run from papers found forward, but was
  not, because that would not test the assertion.
- **No iterations (3.3).** Forward snowballing is run once, from the start set. The justification:
  it is hard to imagine a paper published in 2006 or later that cites *none* of the start set —
  that would mean a paper written, reviewed and published with no acknowledgement of prior work on
  its own topic.
- **Mechanics per start-set paper (4.2):** find the paper in Google Scholar by title, *or* find an
  author's Google Scholar profile and locate it in the publication list; follow the citation link;
  **untick patents and quotes**; restrict the citation window to 2006–2013. All 12 start-set papers
  had at least one author with a Google Scholar page.
- **Inclusion/exclusion (3.4):** based on the *original* research questions from the first-
  generation study; screening cascade as in step 4 above.

### Search-quality measurement techniques

Two research questions, both comparative rather than metric-based:

- **RQ1 — do the two searches identify the same papers?** Broken into three sub-questions: (a)
  does snowballing include the same papers; (b) if not, were the missing papers at least *seen*
  and evaluated (a different judgement or a researcher mistake, distinct from a search failure);
  (c) does snowballing find *additional* papers not in the database study.
- **RQ2 — is one method more efficient?** He notes candidly that almost no researchers record
  actual hours spent on a systematic literature study, so hour-for-hour comparison is impossible;
  **the number of papers actually evaluated is used as the approximation.**

No recall, precision, F-measure or quasi-gold standard is computed. There is an implicit gold
standard — the database study's included set — but he does not treat it as authoritative, since he
argues snowballing found papers the database search could not have.

### Reliability and agreement techniques

No kappa, no test-retest, no multi-rater protocol. The snowballing was performed by one researcher,
and Wohlin uses that fact as the explanation for a specific discrepancy: two papers included by the
database study were screened out here, and he says this **"may have been avoided if having several
researchers conducting the screening"** (Section 4.4). He diagnoses the cause precisely: Google
Scholar shows only the title and the first part of the abstract, and that fragment was not clear
enough to motivate opening the paper — whereas the full abstracts make inclusion "quite clear".
That is a reliability finding about the *screening surface*, not about the searcher.

### Caveats, traps and pitfalls

- **A review published as both conference and journal paper splits its citations.** The Kitchenham
  et al. review exists as a 2006 conference paper (P11, covering to 2004) and a 2007 journal
  article (P12, adding one 2005 paper). Consequences he documents: papers published in 2006–2007
  may be unable to cite the journal version; researchers who know the conference version and find
  it sufficient may never look for the journal version. Empirically, **most citing papers cite
  either one or the other and only one paper cited both** — so **you must forward-snowball from
  every version of the prior review**, or you will lose roughly half the yield.
- **Google Scholar citation counts drift.** Counts observed in November 2015 had changed slightly
  by a February check. He argues this does not affect the comparison because the regular databases
  (IEEE, ACM, Scopus, Springer) should be stable ~2 years after the end of the window.
- **First-screen truncation.** As above — the Google Scholar snippet is a lossy screening surface
  and caused two false exclusions.
- **Multi-database consolidation is its own cost.** The database study drew on **seven** databases,
  which requires substantial work to merge into one list and de-duplicate. Snowballing largely
  avoids this because Google Scholar links **change colour once visited**, making already-evaluated
  papers visually obvious — with the caveat that you must be sure the page was not visited for some
  unrelated reason.
- **Coverage gaps in the standard databases.** P19 (a Software Measurement European Forum paper)
  does not appear to be in the standard databases at all; a general Google search returns no links
  to them. Wohlin's conclusion is that this paper is **impossible to find by database search alone**.

### Snowballing vs. database search — the argument

This paper's whole purpose. The findings:

- All papers found by the database search were **also found** by snowballing (though two were
  screened out by the single reviewer).
- Snowballing found papers the database search did not, **including at least one (P19) that the
  standard databases do not carry.**
- Snowballing evaluated fewer papers to get there.

The deductive argument, restated and reinforced (Sections 3.3 and 4.5): a paper published after a
review on its own topic is overwhelmingly likely to cite either that review or some of its primary
studies. Wohlin adds three social-mechanism reasons why this holds even for authors who are
unaware of or ignore prior work: **knowledgeable reviewers would comment on the weak related
work**; and **editors and programme chairs would most likely not accept a paper citing none of the
previous work on a specific topic**. Hence forward snowballing from a prior review has a structural
guarantee that a search string does not.

His conclusion is scoped, not universal: snowballing is "a competitive and viable option as the
first search strategy" for second-generation studies, and generalisability cannot be claimed from
one comparison. He notes the replicated review is a little special because one of its authors also
authored several of the primary studies, but does not think this invalidates the finding. He adds
a time-boundedness caveat in the conclusion: this holds **"until primary studies actually are
written for synthesis."**

Cited supporting work, distinguished from his own contribution: Jalali & Wohlin compared database
search vs. snowballing for agile in a global context and found both produced a reasonable sample
of the relevant literature (comparable results); Badampudi et al. used snowballing first and then
added a database search to assess the "goodness" of snowballing.

### Threats to validity framework

No named validity taxonomy. Limitations are discussed inline (Section 4.5): single comparison so no
generalisability claim; the replicated review has an author overlap with its own primary studies;
differences in included papers may reflect the researcher's subjective judgement rather than the
search strategy — and he says this explicitly for the three extra papers (P15, P19, P22) and for
the two he excluded. He is also explicit that it is **hard to know retrospectively** whether the
snowballing-found papers were also found-but-rejected by the database search, or genuinely missed.

### Empirical findings worth citing

Start set: **12 papers** — the 10 primary studies of the first-generation journal review (P1–P10)
plus the two versions of the review itself (P11 conference 2006, P12 journal 2007).

Citations in the 2006–2013 window per start-set paper (searches run November 2015):

| P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | P11 | P12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 77 | 45 | 40 | 179 | 149 | 92 | 101 | 32 | 41 | 38 | 53 | 171 |

- **794 citations to the ten primary studies (P1–P10); 224 to the two systematic literature
  studies (P11, P12); 1018 in total.** Large overlap among citing papers meant the real workload
  was far below 1018 unique inspections.
- **Every one of the 16 candidates came from the two systematic literature studies. Zero new
  candidates emerged from the 794 citations to the primary studies.** This is the single most
  striking result: for a second-generation study, forward-snowballing the prior *review* was
  sufficient, and forward-snowballing its primary studies added nothing. Wohlin reads this as
  direct evidence that researchers do build on systematic literature studies.
- 16 candidates → **12 included** (4 rejected). Six identified from P11, seven from P12, with one
  paper citing both.
- **Head-to-head with the database-search second-generation study (Mendes et al.):**

| | Database search (Mendes et al.) | Snowballing |
|---|---|---|
| Candidate papers | 1641 | 1018 |
| Papers after first screening | 100 | 16 |
| Papers included | 11 | 12 |
| In common | 9 | 9 |

- Two papers included by the database study but not here (Kocaguneli & Menzies 2011; Top et al.
  2011) — both were *found*, both were screened out on the Google Scholar snippet. Diagnostic
  detail Wohlin supplies: Kocaguneli & Menzies cites **none** of P1–P10 but does cite the journal
  review P12; Top et al. cites **five** of P1–P10 but neither review. Between them these two papers
  demonstrate that you need forward snowballing from *both* the reviews and the primary studies to
  have complete structural coverage, even though in this run the primary studies yielded nothing
  new.
- Three papers included here but not by the database study (P15, P19, P22); it is unknown whether
  they were missed, found-and-excluded, or overlooked. P15 is in IEEE and ACM; P22 is in ACM;
  **P19 appears to be in no standard database.**

---

## wohlin_2013 — "On the Reliability of Mapping Studies in Software Engineering" (Journal of Systems and Software 86(10):2594–2610)

Authors: Claes Wohlin, Per Runeson, Paulo Anselmo da Mota Silveira Neto, Emelie Engström, Ivan do
Carmo Machado, Eduardo Santana de Almeida.

**Type:** Empirical study — specifically a **participant-observer case study with two cases**.

**Role in corpus:** This is the paper that supplies the **actual population / study population /
sample** framework — the conceptual apparatus for reasoning about *why* two honest secondary
studies on the same topic produce different paper sets, and which decision in the protocol causes
which loss. It is also the corpus's counterweight to MacDonell et al.: the first reliability study
of **two independent mapping studies on the exact same topic**, and it concludes that mapping-study
reliability cannot be assumed.

### Process steps or stages defined

The paper does not define a new search procedure. What it defines is a **decision inventory** —
the complete list of choices that determine which papers a secondary study can possibly find, and
which it actually finds. This is the paper's core deliverable and is set out in Section 6.1 and
summarised in its Table 5.

Three nested sets, sample ⊂ study population ⊂ actual population:

**1. Actual population** — "sometimes called the gold standard" — the set of all papers in the
area as the researchers define it, i.e. what you would get with unlimited resources. Fixed by five
*factual* criteria:

- **Definition of the area.** Two teams studying "the same" area may bound it differently. Their
  worked example: does software product line testing include formal verification and dynamic
  analysis? The authors read this as evidence that software engineering may lack sufficiently
  strong definitions of its areas, or that existing ones (SWEBOK) are not used.
- **Research type** — e.g. requiring some form of empirical evaluation. They highlight that for a
  systematic literature review the papers must carry data suitable for meaningful synthesis.
- **Years** — any date restriction.
- **Language** — research is published in many languages; most studies restrict to English.
- **Publication type** — journal only, peer-reviewed only, specific venues, etc.

They note it is close to impossible to find every paper in this population unless the study is
very tightly focused (one conference series, one journal, one year).

**2. Study population** — what the chosen procedures make it *possible* to find. Instantiated
across three areas:

- **Search strategy:** where to search — publisher databases (Scopus, IEEE Xplore), general
  meta-databases (Inspec, Citeseer), search engines (Google Scholar), specific relevant journals
  or conferences, key authors in the area; **whether snowballing will be used** (listed as its own
  decision, since it may add completeness); which keywords go into search strings *and* which
  keywords act as triggers for a closer look at a reference-list entry when snowballing; and
  whether authors of identified papers will be contacted.
- **Inclusion/exclusion criteria:** the *focus* — making the factual criteria concrete enough to
  judge. Their examples of the ambiguity involved: if empirical evaluation is required, does an
  experience report count? An experiment on toy artefacts? Is the phrase "case study" in the title
  enough, or must further criteria be met? And the **level of evaluation** — are decisions made on
  title, keywords, abstract, partial reading (introduction and conclusions), or full text?
- **Quality evaluation criteria:** whether quality is assessed at all, whether it excludes papers
  below a threshold, and finding criteria applicable consistently across different paper types.

The point: as soon as a database set is fixed, a ceiling is placed on what can be found.

**3. Sample** — what you actually end up with, given the procedures. The additional factors:

- **Search strings** — keywords must be combined into strings; databases have different
  limitations; the search functions genuinely work differently across databases; sources like
  Google Scholar are not consistent over time; capabilities differ (e.g. whether title-only search
  is even possible). So *identical* search strings do not guarantee identical behaviour.
- **Individual judgement on inclusion/exclusion** — each criterion must be judged. The common
  procedure they describe is at least two people evaluating individually on a three-point scale:
  **include / maybe / exclude**. Research expertise in the area is called out as an important
  factor.
- **Combining individual judgements** — the rule for merging is itself a decision that changes the
  outcome.
- **Quality evaluation** — same two sub-decisions as inclusion/exclusion.

Also summarised: Petersen et al.'s five-step mapping process (Section 2) — 1. define research
questions; 2. search for primary studies; 3. screen on inclusion/exclusion; 4. classify the papers;
5. extract and aggregate data.

**Definitions the paper adopts (Section 1):**

- *Systematic mapping study* (a.k.a. scoping study), from Kitchenham & Charters: "A broad review
  of primary studies in a specific topic area that aims to identify what evidence is available on
  the topic."
- *Systematic literature review*, same source: a secondary study using a well-defined methodology
  to identify, analyse and interpret all available evidence on a specific research question,
  unbiasedly and (to a degree) repeatably.
- *Reliability*, from Yin: "Demonstrating that the operations of a study – such as the data
  collection procedures – can be repeated, with the same results."

The authors split reliability into **repeatable** (one can redo the study and follow the authors'
reasoning) and **consistent** (an independent new study obtains similar results) — and stress
these are not the same thing.

They also stake out a methodological position (Section 1): the **procedures for selecting primary
studies should be the same for reviews and for maps**, even though Kitchenham et al. expect a
"less stringent" search strategy for maps while simultaneously demanding completeness and rigour
for maps to serve as a basis for further research.

### Search-quality measurement techniques

No recall/precision/F-measure is computed. Quality is measured as **overlap between two
independent studies**, decomposed by *cause*: for every paper in one study but not the other, the
original authors were asked whether it was **never found** (a search-strategy failure) or **found
and excluded** (a judgement difference), and at which step.

They introduce **"gold standard"** as a synonym for the actual population (citing Dieste et al.
and Zhang et al.), and they call for "a small set of empirically proven strategies… including both
strategies starting with database searches and snowballing", judged on **high precision and high
recall** (Section 6.3).

A concrete availability audit method is used to diagnose misses (Section 5.1). For each of the 21
papers found by the Swedish study but not the Brazilian/USA one:

1. Search Google Scholar to identify the publisher and whether the paper is in one of the
   databases the other study used — searching (a) all words in the title, (b) all words in title
   plus authors, (c) exact title.
2. Classify into: available in the databases used / available in another database / PDF available
   via Google Scholar / visible only through citations.

**Result (Table 2):** in databases used = 6; in other databases = 1; PDF available = 12; only
cited = 1; not found = 1. So all 21 were reachable via Google Scholar (two not available as such),
but the authors caution that even a full-title search returns a large number of results, making the
papers very hard to find in practice — "It is definitely a challenge to identify search strings in
GoogleScholar that lead to high precision and high recall." They further note Google Scholar's
content changes more dynamically and less controllably than ISI Web of Science, while granting its
very broad coverage.

### Reliability and agreement techniques

- **Cohen's kappa was deliberately not calculated.** Given how low the classification agreement
  was, the authors judged a kappa computation (of the kind Henningsson & Wohlin performed) as not
  very useful, and studied the disagreements in depth instead. This is a notable methodological
  judgement to cite: kappa was rejected as uninformative at very low agreement, in favour of
  pattern analysis.
- **Agreement measured as raw concordance:** of the 33 papers both studies included, only **11
  (33%)** received the same research-type classification. They temper this by noting that with six
  categories perfect agreement is close to impossible — but call 33% "discouraging" nonetheless.
- **Pattern analysis of disagreement.** The 22 discordant papers spread across **11 different pairs
  of classifications**. The one discernible pattern: the Swedish study tended to classify as
  *evaluation* or *validation* what the Brazilian/USA study classified as *solution proposal* —
  visible in **10 of the 22**. Their interpretation: these categories are **not disjoint**, because
  a solution can be proposed *and then* evaluated or validated, leaving the researcher to decide
  which aspect dominates, or to assign multiple types. They regard the existence of a pattern as
  making the disagreement less critical than a random scatter would be.
- **Within each original study**, papers were classified by two researchers working independently,
  with disagreements discussed and resolved. Both studies used this same procedure — which is
  precisely why the cross-study disagreement is alarming.
- **Recommended practice cited from Kitchenham et al. (2012b)**: for quality assessment of formal
  experiments, **the median of three reviewers gave the most reliable results** — from which this
  paper concludes it is beneficial to have three reviewers in classification where possible.
- **Method-level reliability controls in this study itself:** the first author was independent of
  both mapping studies and drove the comparison to preserve impartiality; original authors were
  first only asked questions, then shown summaries to check for correctness, then shown the
  results; the whole exchange was conducted by email; the paper was iterated for review and
  comment.

### Caveats, traps and pitfalls

- **Research questions leak into the search even in a mapping study.** A map is supposed to be a
  *broad* review of an area and so should not be driven by specific research questions the way a
  review is — but search strings are very likely to be formulated from whatever research questions
  were posed. The Brazilian/USA study derived **18 search strings** from nine specific research
  questions; this both broadened the field definition (adding performance, security, verification,
  static analysis) and, the authors suspect, constrained scope elsewhere.
- **The same search string does not mean the same search.** Database search functions are
  implemented differently, have different limitations, and differ in capability (e.g. title-only
  search). Google Scholar is not consistent over time.
- **Title-based search misses generically titled papers.** One paper was missed in the Swedish
  study because its title was very general while its content was specific to software product
  lines.
- **Papers get overlooked by simple mistake.** One of the four papers missed in the Swedish study
  was overlooked by error — acknowledged plainly.
- **Papers you can search for correctly may still not be in your databases.** Sixteen of the 21
  papers found by snowballing-style search were **not findable in the databases the other study
  used at all**. Of the six that *were* in those databases (3 IEEE Xplore, 2 SpringerLink, 1 ACM
  DL), the miss is attributed to a mismatch between the wording used in the papers and the search
  strings used.
- **A preliminary search that returns too much and too little at once.** The Brazilian/USA study's
  first search generated too many results and too few relevant ones, forcing a rephrase — a normal
  and expected iteration, worth planning for.
- **Different papers, same study.** Authors of secondary studies should report papers they excluded
  *because they report the same study as another paper*. It is natural to include only the most
  comprehensive paper for a given study, but the others must be reported so completeness — and
  therefore reliability — can be judged. Correspondingly, primary-study authors should clearly
  distinguish papers from studies, since one paper may hold several studies and one study may span
  several papers.
- **Bigger is not automatically better.** A larger sample is not necessarily better; what matters
  is **representativeness**. A smaller but representative sample may give a better picture of an
  area, and its conclusions need not be weaker — though a larger *representative* sample is
  normally preferable.
- **Novices are not well equipped to run secondary studies.** Cited from Kitchenham et al. (2011a),
  and echoed in their own recommendation that student-run literature studies should be done
  together with researchers experienced both in secondary studies and in the subject area.
- **Non-comparable classification schemes make maps mutually unreadable.** The two studies used
  different research-focus schemes *and* used them at different intensities — the Swedish study
  assigned barely more than one focus subcategory per paper (only one paper got more than one; 74
  contribution classifications for 64 papers), while the Brazilian/USA study assigned close to
  three per paper (130 subcategory assignments for 45 papers). This made research-focus comparison
  "close to impossible."

### Snowballing vs. database search — the argument

The two studies were not designed as a method comparison, but they contrast in method and the
paper reads them that way.

- **Swedish study** ([Engström11]) used a five-step, snowballing-led strategy: (1) *exploratory
  search* — six known papers scanned for references to and from, giving 24 articles; (2) *related
  work* — introductions and related-work sections of those papers read, adding 10 papers; (3)
  *conference proceedings* — two conferences identified from the venues of steps 1–2 and searched,
  adding 19; (4) *databases* — the set validated against keyword searches in Google Scholar and
  ISI using general keywords ("product", "line/lines/family/families", "test/testing"), adding 11;
  (5) *earlier review* — checked an existing review for anything missing; **no new papers**. Total
  64 papers, peer-reviewed only, up to and including 2008.
- **Brazilian/USA study** ([Neto11]) used a six-step, database-led strategy: (1) preliminary
  keyword search — too many results, too few relevant; (2) rephrase into 18 search strings derived
  from the nine research questions; (3) search ScienceDirect, Scopus, IEEE Xplore, ACM Digital
  Library, SpringerLink; (4) complement with targeted searches of major journals (Elsevier, IEEE,
  ACM, Springer); (5) targeted search of major conferences; (6) reference lists of found articles
  scanned for further sources such as book chapters, technical reports and theses. Steps 4 and 5
  largely re-found what step 3 had. 120 papers investigated, screened first on abstract and
  conclusions and then on full paper, giving **45 included**, up to and including 2009, mostly
  peer-reviewed but including some book chapters, reports and theses — the non-peer-reviewed
  sources coming mainly through the snowballing step 6.

The argument is stated as **Conjecture 1** (Section 7), and it is offered as a conjecture requiring
further research, not a finding:

> Snowballing based on researcher expertise and knowledge of an area is more efficient than trying
> to find optimal search strings — it gives more relevant papers, less noise, and makes better use
> of researcher expertise.

The authors then immediately marshal the evidence against their own conjecture, which is what makes
it citable:

- **For:** the snowballing-led Swedish study found more papers (64 vs. 45), and snowballing is the
  recommended approach in Information Systems (Webster & Watson).
- **Against:** Skoglund & Runeson's strictly formalised snowballing procedure was contradicted for
  **two out of three** secondary studies in software engineering.
- **Mixed:** Jalali & Wohlin found that database search and snowballing did not find exactly the
  same papers, but that the **actual findings from the two approaches were comparable**.
- Their closing position: more research is needed to know which search strategy is best under which
  circumstances.

Section 6.3 makes the corresponding process recommendation: it may be infeasible to identify one
strategy, but the field should have **a small set of empirically proven strategies covering both
database-first and snowballing-first**, selected by evaluation and comparison.

### Threats to validity framework

Section 5.4 uses the classical named categories, briefly:

- **External validity / generalisability** — explicitly low: this is an analysis of two systematic
  maps.
- **Internal validity** — judged high, because the main analysis was performed by a researcher
  working independently of both mapping studies who could nevertheless obtain complementary
  information from their authors.

They also reason about the validity of the *comparison* with MacDonell et al. (Sections 5.4 and
6.5), giving two reasons their lower reliability finding need not contradict that study's higher
one:

1. **Expertise.** Authors on both MacDonell teams had contributed substantially to the field —
   five of eleven papers were co-authored by researchers in the study — so they were experts, and
   experts are more likely to identify relevant papers than non-experts.
2. **Breadth.** MacDonell et al. studied a narrower area, as an SLR addressing a specific research
   question typically does. Their argument: secondary studies resemble qualitative research in that
   information must be coded and observations may be interpreted or weighted differently by
   different researchers; therefore **a broader secondary study (typically a mapping study) requires
   more judgement than a focused one (typically an SLR), so the two can legitimately show different
   reliability without either being wrong.**

Additionally, MacDonell's two teams started from a **shared research question**, which the two
mapping studies did not.

### Empirical findings worth citing

Overlap between the two independent maps on software product line testing (Table 1):

| | Brazilian/USA | Swedish |
|---|---|---|
| Included | 45 | 64 |
| Common | 33 | 33 |
| Not included in the other study | 5 | 31 |
| — of which not *found* by the other | 4 | 21 |
| — of which *excluded* by the other | 1 | 10 |
| Not possible to find in the other (out of its scope) | 7 | 0 |
| Potentially in common | 33+1 | 33+10 |

- The two studies **could** have had **44 papers in common**; only **33** actually were. So **25% of
  the papers the studies might have shared were excluded by one of them** — a pure judgement loss,
  with no search failure involved.
- Almost **50%** of the Swedish study's papers do not appear in the Brazilian/USA study.
- Of the four papers the Swedish study missed: two were consequences of a **different definition of
  the field** (one never mentions "product lines"; one is about static verification, outside the
  Swedish definition); one was missed by title-based search because its title was very general; one
  was **overlooked by mistake**.
- Of the 21 papers the Brazilian/USA study missed, **16 were not findable in the databases it
  used at all**; the six that were (3 IEEE Xplore, 2 SpringerLink, 1 ACM DL) were most likely
  missed through wording/search-string mismatch. The authors observe that 6 vs. 4 makes the two
  studies **comparable in the number of findable-but-missed papers**.
- Research-type classification agreement on the 33 joint papers: **11/33 = 33%**, across **11
  distinct disagreement pairs**, with the evaluation/validation-vs-solution-proposal pattern
  accounting for 10 of the 22 disagreements.

Research-type distributions (Table 3), using Wieringa et al.'s six-category scheme:

| Research type | Swedish (all) | Brazilian/USA (all) | Swedish (joint 33) | Brazilian/USA (joint 33) |
|---|---|---|---|---|
| Evaluation research | 10 (15%) | 5 (11%) | 8 (24%) | 5 (15%) |
| Validation research | 12 (19%) | 4 (9%) | 8 (24%) | 3 (9%) |
| Solution proposal | 26 (40%) | 26 (58%) | 10 (30%) | 19 (58%) |
| Conceptual proposal | 11 (17%) | 2 (4%) | 5 (15%) | 1 (3%) |
| Experience report | 2 (3%) | 4 (9%) | 2 (6%) | 4 (12%) |
| Opinion paper | 4 (6%) | 4 (9%) | 0 (0%) | 1 (3%) |
| **Total** | **65** | **45** | **33** | **33** |

The two maps agree only that solution proposals dominate and that experience reports and opinion
papers are few. They **disagree even on whether evaluation or validation research is the larger
category**, and disagree sharply on conceptual proposals. Findings for RQ2: the conclusions are the
same only at the most abstract level — "More validation and evaluation research is needed…" and
"additional investigation, empirical and practical, should be performed" respectively.

**The Wieringa et al. research-type scheme as used here** (Section 4.1; the Brazilian/USA study
used Wieringa's original term "philosophical paper" where the Swedish study said "conceptual
proposal" — same definition, and this paper adopts "conceptual proposal"):

- **Evaluation research** — techniques, methods, tools or other solutions implemented and evaluated
  **in practice**, with outcomes investigated.
- **Validation research** — a novel solution developed and evaluated **in a laboratory setting**.
- **Solution proposal** — a solution is proposed and its benefits discussed, but **not evaluated**.
- **Conceptual proposal / philosophical paper** — structures an area as a taxonomy or conceptual
  framework; a new way of looking at existing things.
- **Experience report** — the author's own experience of what happened in practice and how.
- **Opinion paper** — personal opinion on a matter, without relying on related work or research
  methodologies.

**The four conjectures (Section 7)** — the paper's stated deliverable for future research:

1. **Snowballing based on researcher expertise beats optimising search strings** — more relevant
   papers, less noise, better use of expertise. (Evidence for and against as set out above.)
2. **Secondary studies will not find the same papers** unless the area is relatively narrow *and*
   experts conduct the study. Research is needed on when two independent secondary studies can be
   expected to converge.
3. **Secondary studies may reach the same general conclusions even when the paper sets differ.**
   Research is needed on the circumstances under which this holds.
4. **Secondary studies are not reliable per se.** Reliability is highly dependent on context — the
   area studied, the researchers, the search approach, and the data available in the primary
   studies. Research is needed on the influence of contextual factors.

**Recommendations to improve reliability (Section 6.3):**

- A **standardised classification scheme with an agreed interpretation.** Wieringa's scheme was not
  built for secondary studies generally — it came from requirements engineering — and it sits at a
  higher abstraction level than, say, Kitchenham et al.'s criteria for classifying empirical
  evaluations; added detail and worked examples would reduce ambiguity.
- A classification scheme for **research focus** as well as research type, possibly an extension or
  adaptation of the ACM Computing Classification System (which they note is often felt to be
  narrowly technical), covering cross-topic software engineering terms such as process, method,
  technique, tool and measurement.
- **Agreement on search strategy** — a small set of empirically proven strategies, both
  database-first and snowballing-first, optimising precision and recall.
- **Agreement on inclusion/exclusion strategy** — how many people, what relevance scale, rules for
  merging individual scores, and when a kappa analysis of evaluator agreement is worth doing.
- **Consistency in reporting** — distinguishing papers from studies, and reporting papers excluded
  as duplicate reports of the same study.
- **Write for synthesis** (Section 6.4) — primary-study authors should use standardised
  terminology, classify their own papers under a standard scheme, and use structured abstracts.
  The authors acknowledge this is a major shift: writing to make synthesis easier rather than
  purely to publish one's own results.

Their overall verdict: this study **does not support the conclusion that mapping studies are
reliable**. But their explicit corollary is not to abandon them — an unstructured approach is
worse, because it makes the reliability of a literature study impossible to evaluate at all.

---

## Cross-cutting notes for the methodology document

- The three papers give a **progression on the same live design question**: 2013 conjectures that
  snowballing beats search-string optimisation while listing the evidence against it; 2014 defines
  the procedure and concludes snowballing is "a good alternative" and should complement rather than
  replace database search; 2016 supplies evidence for the narrow, strong case — second-generation
  (update) studies, where forward snowballing from the prior review has a structural guarantee that
  a search string does not.
- **Wohlin's own position across all three is that these are complements, not competitors.** The
  strongest form of the recommendation is hybrid — and formulating a good hybrid approach is listed
  as open research in 2014 §5.
- Wohlin 2014 §5 and Wohlin 2013 §6.3 both call for **empirical comparison of search strategies**
  and note that no one records actual effort (restated in 2016 §3.1 RQ2) — so effort claims in this
  literature rest on proxies (papers examined, papers reviewed in detail), not hours.
