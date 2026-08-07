# 13 — Open Science and Reproducibility

**Primary source**: Méndez, Graziotin, Wagner & Seibold 2020, *Open Science in Software Engineering*
— Chapter 17 in Felderer & Travassos (eds.), *Contemporary Empirical Methods in Software
Engineering*, Springer, pp. 477–501. Open access (CC BY 4.0).

The only source in the corpus that specifies **what openness concretely requires** — the artefact
taxonomy, the licence traps, the archival requirements, the preregistration mechanics. Its authors
wrote it from direct experience implementing open science policies as conference and journal chairs,
so the warnings are operational rather than aspirational.

> **Scope note.** It is a reflective methods chapter, not an empirical study. It contributes a
> synthesis, a worked scenario, and a list of experienced challenges; it collects no data of its own.
> Where it reports numbers, they are attributed to others or to the authors' own policy experience.

---

## The terminology, and why it does not transfer cleanly to SE

The chapter adopts the ACM artefact-review definitions:

| Term | Team | Setup | Meaning |
| ---- | ---- | ----- | ------- |
| **Repeatability** | Same team | Same setup | A researcher can reliably repeat her own computation |
| **Replicability** | Different team | Same setup | An independent group obtains the same result **using the authors' own artefacts** |
| **Reproducibility** | Different team | Different setup | An independent group obtains the same result using artefacts **they developed independently** |

**Then it argues these do not fit software engineering**, and this is one of its distinctive
contributions. SE inherited the assumptions from the natural sciences, where the implicit focus is
quantitative and often purely computational work — simulations, for which the definitions hold as
written. But most SE studies involve humans, and human subjects act rationally only in exceptional
cases. **Every change in experimental context will eventually yield different, context-dependent
results even when the setup and procedure are followed exactly.** Such a study fails the literal
definition of reproducibility while it is still reasonable to call it reproducible.

Two further discipline-specific obstacles: much SE data comes from **sensitive industrial settings**;
and SE relies heavily on **qualitative data**, whose analysis is less procedural than quantitative
analysis and which therefore poses integrity challenges. Both push toward anonymisation, which itself
degrades comprehensibility.

> **The chapter's methodological position, and the one this platform should adopt**: where literal
> reproducibility is unattainable — human-subject work, qualitative synthesis — the achievable
> standard is **transparency and the trustworthiness of the analysis process**. That substitution
> applies directly to qualitative synthesis in secondary studies, and it pairs with Cruzes & Dybå's
> four trustworthiness criteria in [08](./08-extraction-and-synthesis.md).

---

## The six facets of openness in scope for SE

Open science is an umbrella term; the chapter selects six as relevant to empirical SE.

### 1. Open access — publications

Freely available on the public Internet with no financial, legal or technical barrier — **including
not forcing users to register**. Readers may read, download, copy, distribute, print, search or link
for any lawful purpose. Authors typically retain copyright; openness is enabled through licensing.

Distinctions that matter for archiving decisions:

| Term | Meaning |
| ---- | ------- |
| **Self-archiving** | The author makes their own copy openly available — **green open access**, allowed by most publishers subject to regulation |
| **Preprint** | A version not yet accepted at a venue |
| **Postprint** | An author-produced version whose *content* is identical to the accepted publication; differs only in typesetting and location |
| **Gold open access** | The publisher renders the accepted publication openly licensed. Often author-pays, though not always |

**SHERPA RoMEO colour codes** — the chapter says it is "imperative to strictly adhere to these rules":

| Code | Permits |
| ---- | ------- |
| **White** | Self-archiving not formally allowed |
| **Yellow** | Preprints (pre-refereeing) |
| **Blue** | Postprints (final draft post-refereeing) or the publisher's version/PDF |
| **Green** | Preprint **and** postprint or publisher's version |

### 2. Open data

The same idea applied to research data. **Openness admits degrees** — metadata may be findable and
accessible online while the full data set is released only on request, for specific purposes the
owners select. The ideal is anchored on the **FAIR principles**: Findable, Accessible, Interoperable,
Reusable.

### 3. Open source

Includes **research software** specifically — the code that analyses empirical data, e.g. R or Python
analysis scripts — releasable under standard licences such as MIT or GPLv3.

### 4. Preregistration of studies

The facet most directly relevant to this platform. See its own section below.

### 5. Open science badges

Publisher- or body-awarded symbols certifying content is available in a persistent location. The
OSF / Center for Open Science model distinguishes three:

- **Open Data** — shareable data necessary to reproduce the study is publicly and digitally available
- **Open Materials** — the methodology materials necessary to reproduce or replicate the methodology
  (e.g. analysis scripts) are available
- **Preregistered** — the study design, including research design and study materials, was
  preregistered

Badges were rare in SE at the time of writing, preregistered badges especially. The ACM system is
named as perceived hard to implement, because of its wide spectrum of often overlapping badges. But
badges are **recognised as a valuable incentive that increases participation**.

### 6. Open peer review

The chapter is careful: **there is no commonly accepted definition and no agreed schema.**
Implementations range across removing anonymity, publishing reviews, permitting direct
author–reviewer interaction, crowdsourcing reviews, and making manuscripts public before review. The
least common denominator is **mutual identity disclosure** — a model long familiar in code review.
Not yet adopted by SE journals and conferences; the Journal of Open Source Software is an exception,
PeerJ Computer Science a partial one.

---

## Preregistration — and why it matters here more than anywhere else

**What preregistration is for**: assuring quality in the *study design*. Specifically, making sure the
hypotheses of a confirmatory study were genuinely predefined, rather than defined after the data were
analysed to fit the results.

**What is registered**: what the research questions are, why the research is being pursued, and how
exactly the questions will be answered. The Open Science Framework is one of the most common venues.

**Three pathologies it avoids**, each attributed:

| Pathology | What it is |
| --------- | ---------- |
| **Publication bias** | Positive results are likelier to be published |
| **p-hacking** | Analysing until something reaches significance |
| **HARKing** | Hypothesising After the Results are Known |

**Registered reports** go further. The report goes through peer review *before the study runs*, and on
acceptance is **in principle accepted (IPA)**: if the researchers conduct the study as registered,
**the paper will be published regardless of the results.** That is the mechanism that severs
publication from outcome.

> ### ⚙ IMPLEMENTATION — a review protocol *is* a preregistration
>
> This is the strongest connection in the chapter, and it needs no new concept. Kitchenham's review
> protocol already specifies the questions, the rationale, and exactly how the questions will be
> answered — which is precisely what preregistration registers. The platform already models it, and
> already versions it.
>
> What is missing is the **commitment property**. A preregistration is only worth something if it is
> **timestamped, immutable, and externally visible before the data exist**. Three consequences:
>
> - The protocol needs a **publishable, citable snapshot** at validation time — the point the status
>   moves to `validated` — not just a version row.
> - **Deviations must be recorded against that snapshot**, which the corpus already demands
>   independently ("report deviations from the protocol" recurs in [01](./01-slr.md),
>   [03](./03-rapid-review.md) and [10](./10-reporting-and-evaluation.md)). Preregistration is what
>   makes deviation *detectable* rather than merely reportable.
> - **Export to OSF** would make the snapshot externally verifiable. That is a small integration on
>   top of machinery that already exists.
>
> Note the ordering constraint from the chapter's worked pipeline: **the analysis plan is fixed and
> registered before the data are analysed.** For a secondary study that means the synthesis strategy
> is committed before extraction completes — which the platform can enforce, and a human working in a
> spreadsheet cannot.

---

## What must actually be published

The chapter's worked example concludes by naming the three-part disclosure an open-science-conforming
study produces:

1. **A study protocol submitted and reviewed prior to publication** — a preregistered study
2. **The replication package** — all analysed data (open data) *and* all files, scripts and codebooks
   necessary to comprehend the study (open materials)
3. **A preprint**

### Where to archive — and where not to

> **⚠ Do not host replication packages on personal or institutional websites.** A URL gives a unique
> ID, but nobody can guarantee it stays valid or that the content stays there. Web pages **disappear
> continuously** — empirically demonstrated by Koehler's four-year longitudinal study and its
> continuation.
>
> **Use a repository providing a DOI and permanent archival — Zenodo or figshare.** The chapter's
> comparison: figshare is commercial but free, with more polished usability, and participates in data
> preservation mechanisms, which Zenodo does not; Zenodo's permanency is assured by EU financing and
> operation by CERN.

This is the same link-rot problem [05](./05-grey-literature-mlr.md) documents for grey-literature
*sources*, arriving from the other direction — your own artefacts rot too.

### Project structure

Apply a structure and naming convention **concisely and consistently regardless of project size**.
The chapter's layout: `README.md`, `Makefile`, `data/` with a cleaning script plus separate
`data_raw/` and `data_clean/`, `analysis_plan/`, `analysis/` with `functions/`, slide sources, a
BibTeX file, and the manuscript source and PDF.

Two experience-derived rules:
- **Keep the original data in a separate folder and never manipulate the raw files**
- Create new files in a separate folder for cleaning and analysis

Combined with a cleaning script, this makes the **data-cleaning process itself reproducible**.

**Computational environment**: a VM fixes software versions but is not very portable; containers
(Docker, Singularity) are an alternative; the option actually followed was a dependency
version-management system.

---

## Qualitative data — the fallback that a secondary-study protocol should copy

Achieving replicability and reproducibility of qualitative studies is particularly challenging, and
the chapter concedes **many would argue impossible**. That does not make disclosure less important:
even where reproducibility is unattainable, disclosure achieves **transparency**, letting outside
researchers understand how the authors drew their conclusions.

Qualitative data is the hardest to prepare for a replication package — the most personal, the hardest
to anonymise within legal and ethical constraints. A number is more abstract, and easier to open, than
transcribed interview speech. Ideally it is anonymised and published with participants' explicit
consent, and **consent often will not be forthcoming**.

> **Then it is all the more important that at least the analysis material is shared** — typically
> easier to release. That means the **study protocol, the coding schema, and the coding rules**.
> Purpose: reviewers and other researchers can at least check the **trustworthiness of the analysis
> process** and understand how the conclusions were reached.

> **⚙ IMPLEMENTATION.** This is directly actionable and it lands on gap **G8**. Cruzes & Dybå's method
> requires codes with explicit operational definitions and a code→theme mapping; Méndez requires that
> **the coding schema and coding rules be publishable** when the underlying data cannot be. Persisting
> codes as first-class rows — which G8 already proposes for methodological reasons — is simultaneously
> what makes the open-science fallback possible. One change, two justifications.

**Anonymisation**: remove any information allowing identities to be revealed, and otherwise sensitive
information not directly related to the study. Anonymising company names is "often enough". Sensitive
data should be published **only with participants' explicit consent**, on the principle that only the
participants can decide what is sensitive for them.

**Anonymous release under double-blind review**: open data repositories now allow publishing data
anonymously for review, with authorship made public after acceptance.

---

## The licence traps

The most concrete trap in the chapter, and the one most likely to bite someone who has not read it.

> **⚠ Assigning an unsuitable licence is a common beginner pitfall**, because a licence chosen for a
> preprint can create incompatibilities further down the publishing chain.

| Trap | Why |
| ---- | --- |
| **Non-commercial (-NC) — do not use it at all** | The recommendation is unqualified, for preprints, postprints and data sets alike. The legal meaning of "commercial" is far broader than it looks — potentially catching a blog that runs advertising — and open infrastructure born from commercial entities (**figshare, PeerJ** are the named examples) would be **barred from using -NC material**. Downstream work such as mining papers and aggregating results would be blocked |
| **Share-alike (-SA)** | Requires derivatives to carry the same licence. With -NC, **usually incompatible with traditional publishing**, which requires either full copyright transfer or exclusive distribution rights |
| **CC BY** | Can still be a problem with traditional publishing: non-revocable, permits commercial use by anyone, therefore **non-exclusive to the publisher** |
| **CC0** | Has caused problems with traditional publishing. The common argument for it — that it relieves people of attribution obligations — is rebutted: in a scientific context, **attributing sources is good practice independent of the licence** |

**The two positive recommendations:**

| Situation | Licence |
| --------- | ------- |
| Certain the paper goes to a **traditional publisher** | **arXiv's default non-exclusive licence.** Perhaps the most restrictive of the free licences — virtually, only arXiv may distribute and display it — which is exactly what makes it compatible |
| Certain the paper goes to a **gold open access journal** | **CC BY.** Also recommended for postprints where postprint sharing is compatible with the publisher agreement, because it credits the researchers while giving others the greatest freedom to share and reuse |

---

## Caveats

> **⚠ Effort is the dominant barrier.** Every open practice is an extra step on top of the non-open
> process, and researchers' motivation for extra steps has limits. **Ease is therefore essential.**
> The authors note difficulty has dropped dramatically — GitHub, OSF, Zenodo, figshare and arXiv are
> easy and cost-free — with residual friction in details such as arXiv's LaTeX requirements.

> **⚠ Openness conflicts with confidentiality and anonymity.** Companies have legitimate interests in
> protecting IP and reputation, often via NDAs, forcing reduction or anonymisation — more effort, and
> **a standing risk of accidentally opening something that should have stayed confidential.**

> **⚠ GDPR gives a strong legal basis for individuals' interest in their private data**, and a
> corresponding risk of violating law.

> **⚠ Openness is too often an afterthought** — a preprint and a data drop once the work is done.
> Ideally the *whole process* is open from the start. The anonymity problem makes this hard: you
> often need a **shadow repository** holding the original raw data, carefully filtered before
> anything reaches the open repository.
>
> The payoff is stated bluntly: with full-process openness there is **no way to manipulate during the
> analysis and publication phases** — you cannot make the hypothesis fit the data in hindsight,
> because the hypothesis was documented before the analysis.

> **⚠ Double-blind review actively obstructs open science.** The SE trend toward double-blind models
> anonymises authors as well as reviewers. The goal of reducing bias is laudable but it "complicated
> open science practices considerably" — preprints cannot easily be made available because reviewers
> might identify the authors. The authors' proposed mitigation is for conferences to permit
> self-archiving while instructing reviewers not to search for papers under review, and they concede
> this remains a challenge.

> **⚠ Open peer review has an unevidenced but widely felt cost** — pressure on researchers,
> especially early-career ones, as authors and as reviewers. The chapter is explicit that for the
> specific fear that early-career researchers would soften their critique, **there is no evidence yet.**

> **⚠ Publisher embargo periods** may apply to postprints. Rarely a problem when a preprint already
> exists and is simply updated; otherwise embargoes must be observed.

---

## Open problems the chapter leaves unsolved

Worth knowing, because a platform touching any of them is entering unsettled territory:

- How to implement a **uniform, transparent guideline for reviewing disclosed artefacts** covering all
  study types, quantitative and qualitative alike
- How to fit **preregistered studies** into existing journal and conference review processes, and how
  to redefine roles and responsibilities accordingly
- How to build a **badge system** that is clear and easy to use while recognising differences between
  study types and the difficulty of opening sensitive industrial data
- How to implement **open peer review**, given the trend runs the other way

Organisers hesitate because they are "often constraint by a general reluctance of implementing
mandatory open science principles", which makes the transition rugged.

---

## Findings worth citing

- **More than 50% of authors disclosed their data** under open science policies at recent editions of
  the conferences and journals the authors were involved with — and these were **non-mandatory,
  voluntary** policies supported by dedicated open science chairs. This is the figure to cite for
  "voluntary policies work"
- German university libraries alone are estimated to spend **well beyond €200 million per year** on
  subscription fees
- **arXiv**: founded 1991; **more than 10,000 submissions per month**; approximately **1.5M
  manuscripts** hosted at the time of writing. Two safeguards — authors must be endorsed before
  registering, and every submission is moderated for scope and copyright
- Open access is associated with **increased access and citation counts**, with facilitating
  technology transfer to industry, and with fostering collaboration
- **Badges increase participation** in open science initiatives
- Ever more public and private funding bodies are implementing open access and open data policies;
  the authors report **reviewers becoming more sceptical of submissions that do not disclose data**

---

## What this means for the platform

> **⚙ IMPLEMENTATION SUMMARY.**
>
> | Requirement | Where it lands |
> | ----------- | -------------- |
> | **Protocol snapshot at validation** — timestamped, immutable, citable | New. The protocol model exists and is versioned; the commitment property does not |
> | **Deviations recorded against the snapshot** | Extends the existing protocol versioning; already required independently by the reporting standards |
> | **Replication package export** — data plus scripts plus codebooks, to a DOI-issuing repository | New. Zenodo and figshare both have APIs |
> | **Never archive to a project-local URL** | Constrains any "download your review" feature. Link rot applies to our own outputs, not only to grey sources |
> | **Publishable coding schema and coding rules** when data cannot be released | Lands on **G8** — persisting codes as first-class rows serves both the synthesis method and the open-science fallback |
> | **Licence selection guidance at export time** | Small, and prevents a genuinely common mistake. Never offer -NC |
> | **Anonymisation support** before any export of participant-derived data | Relevant if the platform ever holds interview or survey data from Rapid Review stakeholder work |
>
> **The framing to adopt**: for secondary studies over human-subject and qualitative evidence, the
> achievable standard is **transparency and trustworthiness of the analysis process**, not literal
> reproducibility. That is what the platform can actually deliver — a complete, inspectable record of
> what was decided, by whom, when, and why — and the chapter's own argument says that is the right
> target rather than a consolation prize.
