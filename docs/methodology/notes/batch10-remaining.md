# Batch 10 — Remaining corpus papers

Synthesis notes for the methodology reference document. All prose below is my own paraphrase of
the source papers; direct quotations are short, in quotation marks, and attributed. Counts,
formulas and numeric results are reported as facts from the papers.

Papers covered, in the order requested:

1. Wieringa, Maiden, Mead & Rolland (2006) — RE paper classification and evaluation criteria
2. Méndez, Graziotin, Wagner & Seibold (2020) — Open science in software engineering
3. Zhang, Zhou, Babar et al. (2020) — Evidence-based software engineering / EBSE
4. Stol, Ralph & Fitzgerald (2016) — Grounded theory in software engineering
5. Fatima, Islam et al. (2023) — Retrieving/identifying papers; search tooling

---

## wieringa_2006 — Requirements engineering paper classification and evaluation criteria: a proposal and a discussion

*Roel Wieringa, Neil Maiden, Nancy Mead, Colette Rolland. Requirements Engineering (2006) 11:102–107.*

**Role in corpus:** This is the origin of the research-type facet — evaluation research,
validation research, solution proposal, philosophical paper, opinion paper, experience paper —
that virtually every software-engineering systematic mapping study has reused since Petersen et
al. (2008) imported it; and uniquely among the corpus it supplies *per-class evaluation criteria*,
not merely per-class labels.

### Origin and motivation (Section 1)

The paper was written by members of the steering committee of the IEEE Requirements Engineering
conference. The trigger was practical rather than theoretical: programme committees kept
disagreeing about the criteria to apply to a submission. The authors' worry is stated plainly —
if reviewers do not all use the same criteria, or use criteria the authors did not anticipate,
then papers get "rejected or accepted for the wrong reasons" (Section 1).

They set the problem between two extremes that then existed in the literature:

- **IEEE Software** used nine distinct genres, each with different evaluation criteria.
- The **Requirements Engineering Journal** recognised effectively a single paper class, evaluated
  on four criteria: originality, utility, technical contribution, and relation to previous work.

The authors read the RE Journal's single class as being, in substance, a paper describing an
original and useful *solution technique* — i.e. IEEE Software's "how to" genre. Their objection
is that this leaves authors and reviewers with no stated criteria for experience reports,
empirical studies or tutorials, none of which propose an original technique. The predicted
failure modes are reviewers applying criteria unknown to authors, and different reviewers of the
same submission applying mutually inconsistent criteria.

Note the paper's own modest framing: it calls itself a "short note", a *proposal* offered to
widen a discussion, not a validated instrument.

### The scheme: rationale

The scheme is derived, not stipulated. The derivation runs in three steps.

**Step 1 — design is not research (Section 2).** The authors' starting observation is that much
of what the RE community calls research is really design. They define the two by their outputs:

- *Designing* is proposing a technique for a purpose. Its output is an **artefact** — a technique,
  notation, device, or algorithm.
- *Research* is investigating something systematically. Its output is **new knowledge**.

This single distinction is what makes the classification more than a list of paper shapes: two
papers can be about the same technique and belong to different classes because one produces an
artefact and the other produces knowledge.

**Step 2 — the engineering cycle (Section 2.1).** The authors take from product development and
systems engineering the idea that engineering activity has a logical structure they call the
*engineering cycle*, on the grounds that this structure is essentially that of rational
decision-making. They illustrate every activity with real papers from the history of the
University of Toronto's i* approach. The six activities are:

| # | Activity | What it is |
|---|---|---|
| (a) | **Problem investigation** | Investigating the current situation — e.g. a field survey of how requirements are actually practised |
| (b) | **Solution design** | Proposing an improvement to the current situation — e.g. proposing i* itself |
| (c) | **Solution validation** | Investigating the properties of a *proposed* solution, predicting whether it would improve current practice |
| (d) | **Solution selection** | Choosing among candidate solutions. The authors note that although i* went through a succession of improvements, the *selection* process was never reported, so they can cite no example — a gap they flag explicitly |
| (e) | **Solution implementation** | Realising the selected solution, e.g. introducing the technique in an organisation |
| (f) | **Implementation evaluation** | Investigating the *new* situation, i.e. practice in an organisation that has recently adopted the technique |

Figure 1 adds a seventh box, the **use** activity, alongside the six, with arrows for impact
relationships.

The paper is emphatic that this is **a list of activities, not a sequential program** (Section
2.1). People may begin with problem analysis, with solution design, with both at once, or even
with validation. Two empirical results are cited in support: Cross found that experienced
designers develop their understanding of the problem *in parallel* with designing and validating
a solution; Witte found that in major management decision processes all tasks in the cycle are
performed in parallel. What the cycle does supply is *justification* structure rather than
sequence: to justify that a design solves a problem the designer should refer to a problem
investigation; to justify selecting one solution over another, to the differing properties
uncovered by solution validations; to justify an implementation, to the chosen solution design.

**Step 3 — collapse the cycle into paper classes (Sections 2.2–2.4).** Of the six activities,
exactly three are research activities: problem investigation ("which problems exist in RE
practice?"), solution validation ("what are the properties of a proposed solution?"), and
implementation evaluation ("what are the experiences with this implemented solution?").

The authors then make the merge that gives the scheme its final shape. Problem investigation and
implementation evaluation are, they argue, very hard to tell apart in practice, because both
investigate the use of RE techniques in the field — the difference is only the researcher's
purpose (understanding problems with techniques, versus understanding one particular technique in
use). They therefore **group these two activities together as evaluation research**.

Solution validation is kept separate because it has a different nature: the technique under
investigation is *not yet implemented*. The authors argue this is "the core business of
engineering research", citing a historical study of the engineering sciences, and give the
cross-disciplinary analogy: civil engineers propose new road-building techniques and investigate
their properties; aeronautic engineers propose new flying techniques and investigate theirs.

### The classification, class by class (Section 3)

The six classes, what distinguishes each from its neighbours, and the evaluation criteria the
paper states for each. The criteria below are paraphrased from the bulleted lists in Section 3.

---

**1. Evaluation research**

*What it is.* Investigation of a problem in RE practice, or of an implementation of an RE
technique in practice. Covers both problem investigation and implementation evaluation.

*What distinguishes it from its neighbours.* From **validation research**: evaluation research
investigates *techniques-in-practice*; validation research investigates techniques *not yet
implemented in practice*. This is stated as the difference (Section 2.2). From **solution
proposal**: evaluation research makes a knowledge claim, not an artefact claim — and critically,
the paper states that if a paper reports the use of an RE technique in practice, **the novelty of
the technique is not a criterion for evaluating that paper**. What is a relevant criterion is the
novelty of the *knowledge claim*, plus the soundness of the research method. From **experience
papers**: an experience paper that draws out lessons learned by systematic means becomes
evaluation research via action research (see class 6 below, and the caveat noted later).

*What "results" mean here.* The paper says research results in either new knowledge of causal
relationships among phenomena, or new knowledge of logical relationships among propositions.
Causal properties are studied empirically — case study, field study, field experiment, survey.
Logical properties are studied by conceptual means — mathematics or logic. Whatever the method,
it must support the paper's conclusions.

*Evaluation criteria.*
- Is the problem clearly stated?
- Are the causal or logical properties of the problem clearly stated?
- Is the research method sound?
- Is the knowledge claim validated — i.e. is the conclusion supported by the paper?
- Is this a significant increase of knowledge of these situations — i.e. are the lessons learned
  interesting?
- Is there sufficient discussion of related work?

---

**2. Validation research**

*What it is.* A paper investigating the properties of a solution proposal that has **not yet been
implemented in RE practice**. The paper explicitly allows that the solution may have been
proposed elsewhere, by the author or by someone else — so validation research need not be
self-validation of one's own proposal.

*What distinguishes it.* Two things. First, the *not yet implemented* condition, as above.
Second, and consequentially, the admissible methods change: the paper states that one would **not**
expect field research to be a useful method in validation research, whereas mathematical analysis
or laboratory experimentation would be (Section 2.2). Section 3 lists possible methods as
experiments, simulation, prototyping, mathematical analysis, and mathematical proof of properties.
The requirement is a "thorough, methodologically sound research setup".

*Evaluation criteria* (the paper says these are similar to those for evaluation research).
- Is the technique to be validated clearly described?
- Are the causal or logical properties of the technique clearly stated?
- Is the research method sound?
- Is the knowledge claim validated — is the conclusion supported by the paper?
- Is it clear **under which circumstances** the technique has the stated properties?
- Is this a significant increase in knowledge about this technique?
- Is there sufficient discussion of related work?

The "under which circumstances" criterion is unique to this class and is worth carrying forward:
it is a scope-of-applicability demand that evaluation research is not asked for in the same words.

---

**3. Proposal of a solution** (commonly cited as "solution proposal")

*What it is.* A paper that proposes a solution technique and argues for its relevance **without a
full-blown validation**. The technique must be novel, or at least a significant improvement on an
existing technique. Proof of concept may be offered by a small example, a sound argument, or some
other means.

*What a solution-design description must contain* (Section 2.3): explain the technique's
ingredients, show how they fit together, explain its intended use, illustrate it with an example,
and state how the authors think it works.

*What distinguishes it.* Solution design is **not a research activity** — this is the pivot of the
whole scheme. The paper defends publishing unvalidated designs on explicitly instrumental grounds:
they are useful to other engineering researchers even without validation, because those researchers
can replicate the technique and validate its properties themselves, or apply it to their own
problems — possibly problems the designer never considered.

*Evaluation criteria.*
- Is the problem to be solved by the technique clearly explained?
- Is the technique novel — or is the *application* of the technique to this kind of problem novel?
- Is the technique described well enough that the author or others can validate it in later research?
- Is the technique sound?
- Is the broader relevance of this novel technique argued?
- Is there sufficient discussion of related work — i.e. are competing techniques discussed and
  compared with this one?

---

**4. Philosophical papers**

*What it is.* A paper that sketches a new way of looking at things — a new conceptual framework,
implying a new way of viewing the world.

*The argument for the class* (Section 2.4). Both research and design use conceptual frameworks to
structure the world being investigated or designed: RE can be viewed as goal analysis, as
specification, as negotiation, or as problem framing, and each view brings its own concepts
(goals, objects, stakeholders, frames). Usually researchers adopt an existing framework;
occasionally they invent one. The authors argue this is distinct from both research and design.
Research *presupposes* a conceptual framework — to make any observation at all you need a language
in which to describe it — and developing that language is a philosophical activity, not a research
one. Likewise, developing the framework in which a solution technique is described is not the same
as inventing a design within a given world-view.

*Evaluation criteria.*
- Is the conceptual framework original?
- Is it sound?
- Is the framework insightful?

Note how short this list is, and what is absent: no research-method criterion, no related-work
criterion.

---

**5. Opinion papers**

*What it is.* A paper expressing the author's opinion of what we should do. It describes no new
research results, no design, and no conceptual framework. Subjects may include the desirable
direction of research, what is good or bad about something, what the community should or should
not do, or anything else concerning values and preferences. The examples given are viewpoint
pieces in the RE Journal and columns in IEEE Software.

*Evaluation criteria.*
- Is the stated position sound?
- Is the opinion surprising?
- Is it likely to provoke discussion?

The second and third criteria are unusual and deliberately so: an unsurprising, non-provocative
opinion fails on its own terms even if correct.

---

**6. Personal experience papers**

*What it is.* A paper describing the author's personal experience of using a particular technique.
The paper's own summary of the emphasis: "the emphasis is on what and not on why" (Section 3). The
experience may cover one project or several, but it must be the author's own. Such papers
typically come from industry practitioners, or from researchers who have used their own tools in
practice, and the experience is reported without a discussion of research methods. The paper states
explicitly that **the evidence presented can be anecdotal**.

*What distinguishes it from its three nearest neighbours* (Section 2.4):
- It does **not** propose a new technique — that would make it a solution proposal.
- It is **not** a scientific experiment — that would make it an evaluation or validation paper.
- Section 2.4 says it need not even contain lessons learned, because drawing lessons would make it
  an evaluation research paper evaluating experiences with a technique in practice by means of
  action research.

*Evaluation criteria.*
- Is the experience original?
- Is the report about it sound?
- Is the report revealing?
- Is the report relevant for practitioners?

*Internal inconsistency to flag.* Section 2.4 says an experience paper "need not even contain
lessons learned"; Section 3 then says "The paper should contain a list of lessons learned by the
author from his or her experience." These two statements are in tension in the published text.
Anyone operationalising the scheme has to decide which reading to apply, and should say which. The
most coherent reconciliation is that an *informal, personal* list of lessons is expected, whereas
lessons derived by a *systematic action-research method* push the paper into evaluation research —
but the paper does not itself state that reconciliation.

---

### Rules for applying the scheme

The paper states several application rules that are routinely dropped when the scheme is reused.

- **Classes are not exclusive.** "Papers can span more than one category, although some
  combinations are unlikely" (Section 3). The worked example given: a paper may propose a new
  technique, present a sound validation of it, and close with the author's opinion of what other
  researchers should do. *This matters for mapping studies that force one research type per paper —
  the scheme's author did not intend a single-label taxonomy.*
- **The purpose is criteria matching, not authorial constraint.** The stated point is "not to force
  authors to write papers that fit within one class"; it is to prevent papers belonging to one
  class being judged by criteria that apply to another.
- **Sound research method is a criterion only for evaluation research and validation research.** It
  is explicitly *not* a criterion for the other four classes.
- **Novelty of the technique is a criterion only for solution proposals.** It is explicitly *not* a
  criterion for evaluation or validation research papers. Conversely, criteria about sound research
  method and interesting knowledge claims are *not* appropriate for solution proposals.
- **No closed list of admissible methods.** The authors "deliberately refrain from listing all
  possible sound research methods", saying the set is bounded only by the researcher's creativity.
  They name laboratory experiments, simulations, field experiments, case studies and action
  research as well known, each with many variants. The criterion for a research paper is therefore
  *not* whether a recognised method was used, but whether the knowledge claims are interesting and
  are justified by the method followed.
- **Openness.** "We have not been able to find paper classes other than the ones above, but we
  remain open for motivated proposals for other paper classes" (Section 2.4).

### What the paper claims about generalising the scheme

This must be stated precisely, because the scheme is now used far outside its origin.

- The paper is titled and scoped to **requirements engineering papers**. It classifies "RE papers"
  (Section 2), its worked examples are all i* / RE papers, and its motivation is the criteria used
  by the RE conference programme committees and the RE Journal.
- **The paper makes no explicit claim that the scheme generalises to software engineering at
  large, or to any other field.** There is no generalisation section and no such sentence.
- What it *does* claim is that the **rationale** is general. The engineering cycle is imported from
  product development and systems engineering, justified as the structure of rational
  decision-making, and illustrated with civil and aeronautic engineering. Section 4 endorses
  Auyang's finding of no difference between research into the properties of artefacts and research
  into the properties of natural objects. So the underlying argument is field-independent even
  though the artefact is not offered as field-independent.
- Section 4 also positions the scheme against Zave's earlier classification of RE research efforts:
  Wieringa et al.'s goal is to identify *paper evaluation criteria*, not to define a taxonomy of
  *topics* that belong to RE. They are concerned with correct research method by authors and proper
  evaluation criteria by reviewers, not with which RE topics can be researched. **A mapping study
  using this scheme as a topic facet is using it against its stated purpose; it is a
  contribution-type facet.**
- The extension of the scheme to software engineering generally, and its adoption as the
  "research type facet" of systematic mapping studies, is the work of *later* authors (Petersen et
  al. 2008 in this corpus) and is not attributable to this paper.

### Caveats, traps and pitfalls

All paraphrased from the paper.

1. **Mismatched criteria are the core failure mode.** If reviewers use criteria different from
   those authors used, papers are accepted or rejected for the wrong reasons.
2. **Applying research-method criteria to a solution proposal is a category error**, and so is
   applying novelty-of-technique criteria to evaluation or validation research.
3. **Do not treat the engineering cycle as a sequence.** It is a list of activities with
   justification relationships; empirical work (Cross, Witte) shows the activities are performed in
   parallel in practice.
4. **Do not force one class per paper.** Papers legitimately span categories.
5. **Do not use a closed list of "acceptable" research methods** as a gate; judge whether the
   knowledge claim is justified by whatever method was used.
6. **Field research is a poor fit for validation research**, because the technique is by definition
   not yet in the field.
7. **Solution selection is under-reported.** The authors could not cite a single paper reporting how
   improvements to i* were selected. This is a documented blind spot in the literature, not merely
   in the scheme.
8. **The scheme is a proposal, not a validated instrument.** The authors present it as the outcome
   of steering-committee discussion and invite further improvement.
9. **Class 6's lessons-learned requirement is stated inconsistently** across Sections 2.4 and 3
   (see above).
10. **Beware the assumption that engineering must follow scientific method.** Section 4 records
    Brooks' position that engineers aim to produce useful things and therefore do not have to
    follow scientific methods — the authors do not endorse it but do not dismiss it either; they
    counter with Auyang and Vincenti.

### Underlying quality standard

The paper accepts **both quantitative and qualitative** research methods, "ranging from controlled
experiments to case study and action research" (Section 4). The single quality standard it names
across all methods is Feynman's: the essential element of any research method is that the scientist
bends over backwards to check every possible way in which the knowledge claim could be wrong. This
is the paper's operational definition of soundness, and it is method-agnostic.

Section 4 also records a suggestion the authors find promising but do not adopt: Davis and Hickey's
proposal to borrow medicine's model of laboratory tests → clinical tests → pilot applications, to
define a **hierarchy of validation levels** for a new RE technique, leading up to actual
implementation. This is a precursor of the idea that validation strength should be graded, not
binary.

### Threats to validity framework

The paper does **not** present a threats-to-validity framework for itself; it is a short position
note without an empirical study of its own. What it offers instead is the per-class criteria above,
which function as quality gates rather than validity categories. The nearest thing to a validity
concept in the paper is the distinction between causal properties (studied empirically) and logical
properties (studied conceptually), and the demand that a validation research paper state under
which circumstances a technique has its stated properties — an applicability-scope condition.

### Empirical findings worth citing

These are all findings the paper *cites from others*, not findings it produces itself. Attribute
accordingly.

- **Validation is absent in roughly 30–50% of software engineering papers that require validation.**
  The paper attributes this to Tichy, Lukowicz, Prechelt & Heinz (1997) and to Zelkowitz & Wallace
  (1997). This is the single most-cited number from this paper.
- A case study by **Wieringa & Heerkens (2004)** indicates the situation in requirements engineering
  "may be just as bad" — the paper's own hedged wording.
- **Glass, Ramesh & Vessey (2004)**, at the opposite extreme: papers in information systems tend to
  be empirical and propose no solutions for the problems they cover.
- The authors' conclusion from this triangulation: the classification shows the community needs to
  do all three — investigate problems empirically, as information systems researchers do; propose
  novel designs, as software engineers do; and validate those solutions, as engineering-science
  researchers do (Section 4).
- **IEEE Software** used **nine** genres; the **Requirements Engineering Journal** effectively used
  **one** class with **four** criteria (originality, utility, technical contribution, relation to
  previous work).
- Auyang's observation, endorsed by the authors: engineering is not the application of natural-
  science knowledge to practical problems but "the application of the scientific method to
  practical problems" (attributed to Auyang 2004, p. 134).

---

## mendez_2020 — Open Science in Software Engineering

*Daniel Méndez, Daniel Graziotin, Stefan Wagner, Heidi Seibold. Chapter 17 in Felderer &
Travassos (eds.), "Contemporary Empirical Methods in Software Engineering", Springer 2020,
pp. 477–501. Open access (CC BY 4.0).*

**Role in corpus:** This is the only paper in the corpus that specifies *what openness concretely
requires* — the artefact taxonomy, the licence traps, the archival requirements, the
preregistration mechanics — and it does so from the authors' direct experience implementing open
science policies as conference and journal chairs, so its warnings are operational rather than
aspirational.

Note the paper's own scope: it is a reflective methods chapter, not an empirical study. Its
contribution is a synthesis, a worked scenario, and a list of experienced challenges; it presents
no data collection of its own.

### The terminology it fixes: repeatability / replicability / reproducibility

The chapter adopts the ACM artefact-review definitions verbatim and reproduces them in Section 1.
Paraphrased:

| Term | Team | Setup | Meaning for computational work |
|---|---|---|---|
| **Repeatability** | Same team | Same experimental setup | A researcher can reliably repeat her own computation |
| **Replicability** | Different team | Same experimental setup | An independent group obtains the same result *using the authors' own artefacts* |
| **Reproducibility** | Different team | Different experimental setup | An independent group obtains the same result using artefacts *they developed completely independently* |

The chapter then argues these definitions do not transfer cleanly to software engineering, and
this argument is one of its distinctive contributions. The reasoning: SE inherits its assumptions
from the natural sciences, where the implicit focus is on quantitative and even purely
computational studies such as simulations, for which the ACM definitions hold as written. But most
SE studies involve humans in some form — "software is made by human beings for human beings"
(Section 1). Human subjects act rationally only in exceptional cases, so **every change in
experimental context will eventually yield different, context-dependent results even when the
setup and procedure are followed exactly**. Such a study fails the literal definition of
reproducibility while it is still reasonable to call it reproducible. The chapter's position is
that open science principles must be *adapted* to the discipline's particularities, as other
disciplines have adapted them, rather than imported unchanged.

Two further discipline-specific obstacles are named in the same passage: much SE data comes from
sensitive (e.g. industrial) settings; and SE relies heavily on qualitative data, where analysis is
less procedural than for quantitative data and which therefore poses significant integrity
challenges. Both push toward anonymisation, which itself degrades comprehensibility.

### The scheme: the six facets of openness in scope for SE

Section 2 scopes the chapter deliberately. Open science is an umbrella term covering many facets
(open access, open data, open source, open government, open notebooks, open standards), and the
chapter selects **six** as being in scope for empirical software engineering (footnote 1):
**open access, open data, open materials, open source, open peer review, and registered reports.**

The overall aim is stated as rendering all artefacts born out of scientific research activities
accessible, without barriers, to any individual on Earth (attributed to Woelfle et al. 2011).

**1. Open access (Section 2.1)** — applies to publications. A publication is open access when it
is freely available on the public Internet with no financial, legal or technical access barrier —
including not forcing users to register with a system. Readers may read, download, copy,
distribute, print, search or link to the full text for any lawful purpose. Minor attribution
constraints may still apply. Typically the authors retain copyright and openness is enabled
through licensing; Creative Commons is the most widely used model.

Sub-distinctions the chapter fixes and that matter for archiving decisions:
- **Self-archiving** = the author makes their own copy openly available. This is **green open
  access**, allowed by the majority of academic publishers subject to regulation.
- **Preprint** = a version of the manuscript not yet accepted at a venue.
- **Postprint** = an author-produced version whose *content* is identical to the accepted
  publication; the only differences from the publisher's version are typesetting and location.
- **Gold open access** = the publisher renders the accepted publication openly licensed and
  unrestricted. Often author-pays, but some publishers charge no article processing charges.

**SHERPA RoMEO colour codes** (reproduced in Section 2.1) — the chapter says it is "imperative to
strictly adhere to these rules":
- **White**: self-archiving not formally allowed
- **Yellow**: authors can archive preprints (pre-refereeing)
- **Blue**: authors can archive postprints (final draft post-refereeing) or the publisher's version/PDF
- **Green**: authors can archive preprint *and* postprint or publisher's version

**2. Open data (Section 2.2)** — the same idea applied to any data produced in the course of
research, e.g. raw data from a controlled experiment. Openness admits degrees: metadata may be
findable and accessible online while the full data set is released only on request and only for
specific research purposes selected by the owners. The chapter anchors the ideal on the **FAIR
principles** — data that is **F**indable, **A**ccessible, **I**nteroperable, and **R**eusable.
Creative Commons deeds are commonly used for data as for publications; the two most employed are
**CC0** (Public Domain, "No rights reserved" — effectively a renunciation of copyright) and
**CC BY 4.0** (reuse and redistribution permitted, attribution the only condition). CC BY-NC 4.0
adds a non-commercial restriction. The chapter flags immediately that CC0 and CC BY-NC, which
"might seem more suitable for academic work", are in fact problematic — see the licence trap below.

**3. Open source (Section 2.3)** — no different from open source software as normally understood.
The chapter highlights **research software** (or scientific software): software built to analyse
empirical data, e.g. Python or R analysis code. This can be released under standard licences such
as MIT or GPLv3. It notes the argument (citing Boisseau et al.) that the open source movement
inspired openness in other fields.

**4. Preregistration of studies (Section 2.4)** — the mechanism most directly relevant to
secondary studies, described below in its own subsection.

**5. Open science badges (Section 2.5)** — publisher- or body-awarded symbols certifying that
content is available and accessible in a persistent location. Some systems are publisher-specific
(the ACM badge system), some independent. The **OSF / Center for Open Science** model distinguishes
three:
- **Open Data** — awarded when shareable data necessary to reproduce a study is made publicly and
  digitally available.
- **Open Materials** — awarded when the materials of the followed research methodology necessary to
  reproduce or replicate that methodology (e.g. analysis scripts) are made available.
- **Preregistered** — awarded for preregistering a study design including the research design and
  study materials.

The chapter reports that badges were, at time of writing, rather rare in SE research (preregistered
badges especially), that some systems are perceived as hard to implement (it names the ACM system,
because of its wide spectrum of often overlapping badges), but that badges are generally recognised
as a valuable incentive that increases participation in open science initiatives (attributed to
Rowhani-Farid et al. 2017) and are being adopted increasingly by journals and conferences.

**6. Open peer review (Section 2.6)** — the chapter is careful here: there is **no commonly
accepted definition and no agreed schema** for open peer review, citing Ross-Hellauer's secondary
study. Implementations range across removing anonymity of authors and reviewers, publishing the
reviews, permitting direct author–reviewer interaction, crowdsourcing reviews, and making
manuscripts public before review. The least common denominator is mutual identity disclosure,
which lets authors and reviewers converse directly rather than through editors or chairs — a model
long familiar in code review. It is not yet adopted by SE journals and conferences; the Journal of
Open Source Software is named as an exception. PeerJ Computer Science is named as a partial
implementation, asking reviewers whether they wish to disclose their names and then asking authors
whether they wish the peer review history published.

### Open science / reproducibility requirements — what must actually be published

This is the section most directly transferable to a secondary-study protocol.

**The three-part disclosure the worked example produces.** Section 4.3 concludes by naming exactly
what an open-science-conforming study should disclose:

1. **A study protocol submitted and reviewed prior to publication** (a preregistered study).
2. **The replication package**, comprising all analysed data (open data) *and* all files, scripts
   and codebooks necessary to comprehend the study (open materials).
3. **A preprint** (in the example, under yellow open access).

**Preregistration (Section 2.4).** Preregistration is described as a tool for assuring a level of
quality in the *study design* — specifically, making sure the hypotheses of a confirmatory study
were genuinely predefined rather than defined after the data were analysed to fit the results. What
researchers register is: what their research questions are, why they want to pursue the research,
and how exactly they will try to answer the questions. The Open Science Framework is named as one
of the most common places to preregister. Journals report that preregistration avoids three named
pathologies:

- **publication bias** (attributed to Dickersin 1990)
- **p-hacking** (attributed to Head et al. 2015)
- **HARKing** — hypothesising after the results are known (attributed to Kerr 1998)

**Registered reports.** Some journals accept a *registered report*: the report goes through peer
review and, on acceptance, is **in principle accepted (IPA)**. If the researchers then conduct the
study as indicated in the registered report, the paper will be published **regardless of the
results**. This is the mechanism that severs publication from outcome. The chapter points to a
guide on writing registered reports at OSF.

**Where to put artefacts, and where not to.** Section 5.4 is unambiguous: a common pitfall is
using a personal or institutional website to publish replication packages quickly. It gives a
unique ID in the form of a URL, but nobody can guarantee that URL stays valid or that the content
stays there — the chapter cites Koehler's longitudinal studies (2002, 2003) empirically
demonstrating that web pages disappear continuously. **Repositories providing a DOI and permanent
archival — Zenodo or figshare — are much preferable.** The chapter's comparison: figshare is
commercial but free to use and its usability seems more polished; figshare participates in data
preservation mechanisms while Zenodo does not; Zenodo's permanency is assured by EU financing and
operation by CERN.

**Long-term reproducibility of the computational environment.** The worked example uses a virtual
machine to fix software versions (containers such as Docker or Singularity are named as an
alternative), but notes a VM is not very portable; the option actually followed is a dependency
version-management system (packrat in R).

**Qualitative data — the fallback requirement (Section 5.5).** This is the passage a secondary-study
protocol should copy. Achieving replicability and reproducibility of qualitative studies is
particularly challenging and, the chapter concedes, many would argue impossible. That does *not*
make disclosure less important: even where reproducibility in the literal sense is unattainable,
disclosure achieves **transparency**, letting researchers outside the study understand how the
authors drew their conclusions. Qualitative data is the hardest to prepare for a replication
package because it is the most personal and the hardest to anonymise within legal and ethical
constraints — a number is more abstract, and easier to open, than transcribed interview speech.
Ideally qualitative data is anonymised and published with the participants' explicit consent, and
the chapter warns that consent often will *not* be forthcoming for qualitative data. **Then it is
all the more important that at least the analysis material is shared** — typically easier to
release, and it may include the study protocol, the coding schema, and the coding rules used when
coding qualitative data, e.g. in a Grounded Theory study. The stated purpose: reviewers and other
researchers can at least check the **trustworthiness of the analysis process** and understand how
the conclusions were reached.

**Anonymisation.** The chapter's footnote defines anonymisation of qualitative data as removal of
any information allowing individuals' identities to be revealed, and of otherwise sensitive
information not directly related to the study. Established techniques for anonymising sensitive
participant data are pointed to (Saunders et al. 2015). Anonymising company names is "often
enough". Sensitive data should be published **only with the explicit consent of study
participants**, on the principle that only the participants themselves can decide what is sensitive
for them; in practice this extends the consent already sought for publication to cover publishing
the data.

**Anonymous data release under double-blind review.** Open data repositories now allow researchers
to publish data anonymously for review, becoming compliant with double-blind restrictions, with
authorship of the data made public after acceptance. Instructions for doing this are attributed to
Graziotin (2019).

### Automation and tooling

The chapter's tooling advice is delivered through the worked scenario in Section 4 — a fictitious
psychometric SE study run by a European team with US psychology partners, the partners running
execution and data collection, the authors running analysis and reporting.

**The pipeline (Fig. 1 and Section 4.2), in order.** Data preparation (check for errors,
inconsistencies, missing values; discuss with partners) → analysis preparation (design the analysis
procedure, updating the data structure to fit the analysis plan) → **make the analysis plan openly
available and ideally submit it as a preregistered study, submitting the study protocol, the
material (analysis scripts) and a detailed sample description so reviewers can judge theoretical
and practical impact** → only after registration and feedback, begin data analysis → interim
presentation of work in progress for community feedback → write up, disclosing the manuscript
preprint before submitting for review.

The ordering constraint is the important part: **the analysis plan is fixed and registered before
the data are analysed.**

**Recommended project structure (Listing 1).** The chapter's rule is to apply a structure and
naming convention concisely and consistently regardless of project size. The structure has:
`README.md`, a `Makefile`, `data/` containing a cleaning script plus separate `data_raw/` and
`data_clean/` subfolders, `analysis_plan/`, `analysis/` with a `functions/` subfolder, slide
sources, a BibTeX file, and the manuscript source and PDF.

Two rules are called out as experience-derived: **keep the original data in a separate folder and
never manipulate the raw files**; create new files in a separate folder for cleaning and analysis.
Combined with a cleaning script, this makes the data-cleaning process itself reproducible to others.

**Tool choices and their justifications:**
- **R** (or Python) for cleaning and analysis, because scripts are text files that give a
  reproducible, version-controllable workflow — explicitly contrasted with click-and-point programs
  (SPSS used without syntax) and programs producing binary files (Excel).
- **Git** plus a hosting service (GitLab in the example) for version control, so all produced text
  documents are traceable and available to collaborators.
- **Make**, with a Makefile recording how files depend on each other and how outputs are produced,
  to automate the workflow.
- **R Markdown** and **knitr** for literate programming (Knuth), combining code chunks with
  explanatory text; Markdown formatting via R Markdown, LaTeX via knitr. The example converts R
  Markdown to Word regularly because the partners use MS Word and comment in it.
- **OSF** for uploading the analysis plan and preregistering.
- **arXiv** for the preprint; **SHERPA RoMEO** consulted first to check the publisher's policy.
- **Virtual machine or container** for environment stability; **packrat** for portable dependency
  versions.
- **Zenodo** with **Restricted Access** for sensitive data.

**The Data Use and Access Committee (DUAC) pattern.** When the partners are reluctant to share data
because of sensitivity and fear of misuse (e.g. data taken out of context), so that FAIR cannot be
followed as intended, the chapter's worked resolution is a graded-access safeguard: deposit on
Zenodo under Restricted Access; publish extensive metadata describing the content and how it was
produced, so prospective users can judge fit; require an application for access; and constitute a
**DUAC formed by the data owners plus a member of the responsible ethics committee** to decide
whether to grant access. This is a concrete pattern worth reusing when a secondary study's included
data cannot be fully opened.

**Compliance check before disclosure.** In the example, before anything is disclosed the team
checks for data needing anonymisation to comply with the EU **GDPR** and with the **Institutional
Review Board** approval notification of the US partners, removing anything allowing observations to
be traced back to participating individuals.

### Evidence-based practice framing

This is not the chapter's frame, but it makes an adjacent argument worth recording. Section 3 argues
that **theory building** is the crucial foundation for turning software engineering into a more
scientific, evidence-based discipline, as happened in other disciplines before it (citing Méndez &
Passoth 2018), and that transparency, credibility and reproducibility are the cornerstones of
building and evaluating robust theories in an emerging field. Open science is positioned as the
foundation for that.

The chapter's argument for *why* is made through an extended thought experiment (Section 3) which is
worth restating because it is the sharpest statement of the problem in the corpus. Imagine a
submission arguing empirically that Go To statements are harmful, drawing on industrial source code
the author does not share (perhaps because of NDAs, though the manuscript does not say) and on
in-depth interviews the author also does not share (perhaps for ethical and legal reasons).
Reviewers find no methodological flaw in the described design, the author is a recognised authority,
the writing is easy to follow, and the results are surprising given contrary published evidence from
public repositories — so it is accepted for its discussion value. The chapter then asks a young
scholar who finds this paper a series of questions, of which the load-bearing ones are: would you
trust the results, and on what basis — the venue's prestige, the writing, the author's name or
affiliation, the citation count? Would the picture change if the author were unknown and the venue
lower-ranked? Could you actually comprehend how the study was carried out, reproduce its conclusions,
or replicate it in your own environment? Would you cite it on the basis of the abstract alone if it
were paywalled, or on the basis of what other papers say about it? Would your treatment of it change
depending on whether it supports or contradicts your own argument?

The conclusion drawn: publication and citation regimes, though rooted in scepticism, have much to do
with trust and conviction; scientific practice is dictated partly by social and political mechanisms
and non-trivial subjective factors. Transparency is therefore the means of breaking with theories
grounded in "common sense, taken-for-granted knowledge, hopes, convictions, and provisional beliefs"
(Section 3). For a secondary study, the operational reading is that unshared primary data forces
reviewers and synthesisers into trust-based assessment, which is exactly what a quality-appraisal
instrument is trying to avoid.

### Caveats, traps and pitfalls

All paraphrased from Section 5 unless noted.

**General (5.1)**
1. **Effort is the dominant barrier.** Every open practice is an additional step on top of the
   non-open research process, and researchers' motivation to do extra steps has limits. The ease of
   the practice is therefore essential. The authors' experience is that difficulty has dropped
   dramatically: GitHub, OSF, Zenodo, figshare and arXiv are easy and cost-free, with residual
   friction in details such as arXiv's LaTeX requirements.
2. **Openness conflicts with confidentiality and anonymity.** Companies have a legitimate interest
   in protecting intellectual property and reputation, often via signed NDAs, forcing reduction or
   anonymisation of shared data — more effort, and **a standing risk of accidentally opening
   something that should have stayed confidential**.
3. **GDPR gives a strong legal basis for individuals' interest in their private data**, and
   therefore a corresponding risk of violating law.
4. **Openness is too often an afterthought** — a preprint and a data drop after the work is done.
   Ideally the *whole process* is open from the start (OSF or GitHub for all documents, data and
   scripts). The anonymity problem makes this hard: one often needs a **shadow repository** holding
   the original raw data, with the raw data carefully filtered before anything goes to the open
   repository. The payoff for full-process openness is stated bluntly: there is then **no way to
   manipulate during the analysis and publication phases** — you cannot make the hypothesis fit the
   data in hindsight, because the hypothesis was documented before the analysis.

**Preprints (5.2)**

5. **Publisher embargo periods** may apply to postprints. Posting a postprint is rarely a problem
   when a preprint already exists and is simply updated; otherwise embargoes must be observed.
6. **Double-blind review actively obstructs open science.** The trend in SE toward double-blind
   models anonymises authors as well as reviewers; the goal of reducing bias is laudable but it
   "complicated open science practices considerably". Preprints cannot easily be made available
   because reviewers might identify the authors. The authors' own mitigation, which they have been
   pushing as a trend, is for conferences to permit self-archiving preprints while instructing
   reviewers not to actively search for papers under review online — but they concede this remains a
   challenge.
7. **Open peer review has an unevidenced but widely felt cost.** The fear is pressure on
   researchers, especially early-career ones — as authors, because reviewers will know who made
   mistakes; as reviewers, because authors will know who proposed changes or recommended rejection.
   The chapter is explicit that for the specific fear that early-career researchers would soften
   their critique **there is no evidence yet**.

**Licences (5.3)** — the most concrete trap in the chapter.

8. **Assigning an unsuitable licence is a common beginner pitfall**, because a licence chosen for a
   preprint can create incompatibilities further down the publishing chain.
9. **Non-commercial (-NC) clauses: do not use them.** The recommendation is unqualified — do not
   license any preprint, postprint or data set with a non-commercial clause. The reasoning: the legal
   meaning of "commercial" is far broader than it looks, potentially catching even a blog that runs
   an advertisement system; and open infrastructure born from commercial entities and hence not
   non-profit — figshare and PeerJ are the named examples — would be barred from using -NC material.
   Useful downstream work such as mining papers and data sets and aggregating results would be
   blocked.
10. **Share-alike (-SA) clauses** require derivative works to carry the same licence. Together with
    -NC, these are in most cases **incompatible with traditional publishing models**, because
    traditional publishers are usually commercial entities requiring either full copyright transfer
    or exclusive distribution rights.
11. **Even CC BY can be a problem with traditional publishing**, because it is non-revocable and
    permits commercial use by anyone, i.e. it is non-exclusive to the publisher.
12. **CC0 has caused problems with traditional publishing in the past** (the chapter cites O'Connor
    2011). It also notes the common argument that CC0 is preferable because it relieves people of
    attribution obligations, and rebuts it: in a scientific context, attributing sources and authors
    is good practice **independent of the licence**.
13. **The chapter's two positive recommendations:** use arXiv's default non-exclusive licence to
    distribute when you are certain the paper will go to a traditional publisher; use **CC BY** when
    you are certain it will go to a gold open access journal. It notes the arXiv default is perhaps
    the most restrictive of the free licences — virtually, it permits only arXiv to distribute and
    display the document — which is precisely what makes it compatible with traditional publishing.
    CC BY is also recommended for postprints where postprint sharing is compatible with the
    publisher agreement, because it credits the researchers while giving others the greatest freedom
    to share and reuse.

**Data and materials (5.4)**

14. **Do not host replication packages on personal or institutional websites** — link rot is
    empirically demonstrated. Use a DOI-issuing archival repository.

**Qualitative data (5.5)**

15. **Expect consent for qualitative data to be refused more often**, and plan the analysis-material
    fallback in advance.

**Open problems the chapter leaves unsolved (Section 6)** — stated as questions the community still
faces:
- How to implement a uniform, transparent guideline for reviewing disclosed artefacts that covers
  all study types, quantitative and qualitative alike.
- How to fit preregistered studies — which the authors consider especially important against
  publication bias and p-hacking — into existing journal and conference review processes, and how
  to redefine roles and responsibilities accordingly.
- How to build a badge system that is clear and easy to use while recognising differences between
  study types and the difficulty of opening sensitive industrial data.
- How to implement open peer review, given that the current trend runs the other way, toward
  double-blind models that make other open science activities harder.

The chapter also records why organisers hesitate: they are "often constraint by a general reluctance
of implementing mandatory open science principles", e.g. mandatory open data policies, which makes
the transition rugged.

### Threats to validity framework

The chapter presents no threats-to-validity framework of its own — it is not an empirical study. Its
functional equivalent is the repeatability/replicability/reproducibility triple above, plus the
argument that literal reproducibility is the wrong standard for human-subject and qualitative SE
work, for which **transparency and trustworthiness of the analysis process** are the achievable
standard. That substitution — transparency where reproducibility is unattainable — is the chapter's
own methodological position and is directly applicable to qualitative synthesis in secondary studies.

### Empirical findings worth citing

- **More than 50% of authors disclosed their data** under the open science policies implemented at
  recent editions of the conferences and journals the authors were involved with — and these were
  **non-mandatory, voluntary** policies supported by dedicated open science chairs (Section 6).
  This is the chapter's headline adoption figure and the one to cite for "voluntary policies work".
- German university libraries alone are estimated to spend **well beyond 200 million EUR per year**
  on publication subscription fees (attributed to Schimmer et al. 2015).
- **arXiv**: founded 1991; receives **more than 10,000 submissions per month**; hosted approximately
  **1.5M manuscripts** at the time of writing, across a distributed archive of multiple digital
  libraries. Free to access, register and submit, with two safeguards — authors must be endorsed by
  existing members before registering, and every submission is moderated by volunteers checking
  scope and copyright.
- Open access is associated with **increased access and citation counts** (attributed to Eysenbach
  2006), with facilitating technology transfer to industry, and with fostering collaboration through
  open repositories.
- **Badges increase participation** in open science initiatives (attributed to Rowhani-Farid et al.
  2017, a systematic review of incentives for data sharing in health and medical research).
- Web pages **disappear continuously** — empirically demonstrated by Koehler's four-year
  longitudinal study (2002) and its continuation (2003).
- Preregistration is reported by journals to avoid publication bias, p-hacking and HARKing
  (Dickersin 1990; Head et al. 2015; Kerr 1998 respectively).
- Contextual note for the Go To example: Nagappan et al. (2015) empirically studied goto in C code
  from GitHub repositories and reached conclusions contrary to Dijkstra's (1968) rationalist
  argument — the chapter uses this only as illustration, not as a finding of its own.
- Institutional signal: ever more public and private funding bodies are implementing open access and
  open data policies (Childs et al. 2014; Van den Eynden et al. 2011); the authors report editors
  and conference organisers already planning transitions to open data, and reviewers becoming more
  sceptical of submissions that do not disclose data.

---

## zhang_2020 — An Evidence-Based Inquiry into the Use of Grey Literature in Software Engineering

*He Zhang, Xin Zhou, Xin Huang, Huang Huang, Muhammad Ali Babar. ICSE '20, Seoul, 23–29 May 2020,
pp. 1422–1434 (13 pages). DOI 10.1145/3377811.3380336.*

**IMPORTANT SCOPE CORRECTION.** The file `zhang_evidence-based_2020.txt` is **not** a general
evidence-based software engineering (EBSE) paper. Its actual title and subject is an
*evidence-based inquiry into the use of grey literature in SE*. "Evidence-based" here qualifies the
authors' **method** — they answer a methodological question with a systematic review plus surveys
rather than with opinion — not the paper's topic. It contains **no** enumeration of the classical
five EBSE steps. Anything in the reference document that needs the canonical EBSE step list must be
sourced from Kitchenham/Dybå/Jørgensen or from Kitchenham & Charters (2007), not from here. What
this paper does supply, and what is genuinely useful, is (a) a demonstration of the mixed-methods
"survey the community about its own methodology" design, and (b) a hard empirical picture of how
badly grey literature is actually handled in published SE secondary studies.

**Role in corpus:** The only paper here that measures — across 102 published SE secondary studies
plus surveys of their authors and of independent experts — the gap between what reviews *claim*
about grey literature and what they actually *did* with it, and which therefore supplies the
quantitative case that grey literature use in SE is currently unsystematic.

### The scheme, method and process

**Overall design (Section 3).** A mixed-methods study in two stages, run from the beginning of 2019.
Stage 1 is a systematic literature review of SE secondary studies that incorporate grey literature
(GL). Stage 2 is an opinion survey with two distinct questionnaires — one to the authors of the
included reviews (the "GL users"), one to independent SE experts. The review stage followed the SE
SLR guidelines (Kitchenham & Charters 2007); the survey stage followed survey guidelines (Harms
2004). The rationale for combining them: the SLR extracts and synthesises what reviews *report*,
while the survey explores the community's *attitudes*, and the two sources supplement each other to
give a holistic picture of state, trend and challenges.

The team was three student researchers (two PhD candidates, one master by research) plus
supervisors, all with prior experience in empirical SE and in SLRs involving GL.

**Research questions.**
- RQ1: What is grey literature in the view of SE researchers?
- RQ2: Why do SE researchers consider grey literature in research?
- RQ3: How does grey literature work in SE research?

**Pilot (Section 3.1).** A pilot on **50 literature reviews** including GL was run at the beginning
of 2019 to develop the detailed study protocol instructions. The pilot's finding is itself the
paper's motivation: many reviews fail to give the *reasons* and the *processes* for using GL, and
many authors do not mention the potential influence of including GL on their results and
conclusions. This is why the study was designed as mixed-methods — the published record alone was
insufficient.

**Search strategy (Section 3.2.1).** Because there is no dedicated venue publishing GL-inclusive SE
research, **only automated search** was applied. Four publisher digital libraries were searched:
ACM Digital Library, IEEE Xplore, ScienceDirect, SpringerLink. The **start year was left open**,
because it is difficult to determine when SE researchers first began incorporating GL. The search
was redone at the end of June 2019 to capture studies published by mid-2019. The search string was:

`((("Multi* review") OR "Multi* literature") OR "Gray Literature") OR "Grey Literature") AND "Software Engineering"`

Retrieval and selection per library:

| Library | Retrieved | Selected |
|---|---|---|
| ACM DL | 8 | 3 |
| IEEE Xplore | 129 | 36 |
| SpringerLink | 152 | 25 |
| ScienceDirect | 172 | 38 |
| **Total** | **461** | **102** |

**Inclusion criteria:** IN-1 the paper is a secondary study; IN-2 the paper includes grey literature
or claims it is a multivocal literature review; IN-3 the full text is accessible.
**Exclusion criteria:** EX-1 not written in English; EX-2 explicitly a short review, position review
or editorial; EX-3 the paper is itself grey literature.

A deliberate scope restriction: only "white literature" incorporating GL was reviewed — i.e. only
*secondary* studies, not primary studies. The justification given is twofold: secondary studies
better reflect the five concerns of GL (scope, search, analysis, evaluation, effects), and a single
review can include a wide range of GL types whereas a primary study tends to include specific,
limited types. Including primary studies would introduce too much noise.

**Study selection (Section 3.2.2).** All three student reviewers read every retrieved paper. Initial
selection was by title–keywords–abstract screening to exclude the irrelevant; the remainder were
independently checked against the criteria by reading full text; individual results were then
cross-checked collectively. Disagreements were discussed in **daily meetings** scheduled for the
duration of the study, and escalated to supervisors and domain experts for a final decision if
unresolved. Search and selection took approximately one month.

**Data extraction (Section 3.2.3).** Nine data items, each mapped to the RQ it serves:

| Code | RQ | Item |
|---|---|---|
| DI1 | — | Year |
| DI2 | 1 | The definition of grey literature |
| DI3 | 1 | The type of grey literature |
| DI4 | 2 | Why choose to use grey literature? |
| DI5 | 2, 3 | What are the roles of grey literature? |
| DI6 | 3 | The search source of grey literature |
| DI7 | 3 | How is data collected and analysed? |
| DI8 | 3 | What specific techniques and practices are used? |
| DI9 | — | The sample size of grey literature |

Extraction was performed independently by three researchers following the protocol, recorded in
spreadsheets, then cross-checked; disagreements resolved in consensus meetings or by consulting
supervisors.

**Survey design (Section 3.3).** Purposive sampling. Two populations:
- **GL users** — authors of all 102 included reviews, contacted by email, because some reviews give
  no detail on GL use.
- **SE experts** — 502 community experts drawn from the programme committees of ICSE, ESEM and EASE
  for 2017–2019. General high-quality conferences were chosen deliberately, rather than
  subfield-specific ones, because GL can be used in any SE topic and the authors wanted
  representativeness; these three were further chosen because they emphasise the methodological
  aspects of conducting and reporting SE research. **Two authors of the paper who had served on
  those committees were excluded from the invitee list to avoid researcher bias.**

Questionnaire structure was built on the six question words (whom, where, when, what, why, how).
For GL users, "whom", "when" and "where" were already known from the reviewed studies, so their
questionnaire concentrated on reasons and process. Three questions were common to both instruments
(SQ1 definition; SQ2 how GL can contribute to planning future research; SQ3 why include GL). GL
users additionally answered SQu4–SQu10, covering: concerns and guidelines for using GL; which
sources were used and why; which search strategies were applied and how reliable GL is obtained;
whether data analysis and synthesis of GL was conducted separately from academic literature and
why; whether a separate quality assessment was applied and how it differed; whether GL was used to
evaluate conclusions; and how GL affected the conclusions. Experts additionally answered SQe4 (at
what stage GL might be introduced), SQe5 (how to obtain reliable GL) and SQe6 (challenges/barriers).

**Administration (Section 3.3.3).** Invitations by email with a two-week reply window per sector;
non-responders reminded once after one week. For GL users, the first author of each paper was
approached first, then co-authors if no reply within the survey period. For experts, reminders
stopped immediately on any reply, including a decline or an automatic unavailability notice.

**Synthesis (Section 3.4).** Both quantitative and qualitative methods. For RQ1, descriptive
statistics over coded definitions from the reviews plus SQ1 replies. For **RQ2 and RQ3, Grounded
Theory** — labelling, multiple iterations of coding, constant comparison, with themes emerging
progressively; "aggregative coding" is named for RQ3. The paper gives a worked coding example: three
sentence-level labels — "obtain more documents", "highly cover", "contain more research" — were
aggregated at a higher abstraction level into the single reason "extend more related research". GL
user data (from reviews plus SRU replies) and expert data (SRE) were analysed independently except
for the three shared questions.

### The GL definition and classification apparatus

**The Luxembourg definition (Section 2.1),** proposed at the Third International Conference on Grey
Literature: GL is information produced at all levels of government, academia, business and industry,
in electronic and print formats, that is **not controlled by commercial publishing**. Some SE
reviews extend this to literature "not formally published in sources such as books or journal
articles", or not formally part of traditional publishing cycles.

**The "grey scales" model (Section 2.3, Figure 2),** attributed to Shpilko et al. building on grey
material classification. Literature is divided into four concentric categories; the higher and outer
the level, the greater the quantity and the harder it is to control quality:
- **Innermost: 'white' literature** — a very small part of the total literature.
- **1st scale (most official GL):** books, magazines, government reports, white papers.
- **2nd scale:** annual reports, news articles, videos, QA sites, Wiki articles. These carry some
  limitations — the example given is a QA site requiring at least 50 reputation points to comment.
- **3rd scale (completely uncontrolled):** blogs, presentations, tweets, emails — everyone has access.

**The empirically derived three-dimensional view (Section 5.1).** From the replies, SE researchers'
perspectives on GL resolve into three dimensions:
- **Accessibility** — whether the content is widely available. Seven replies mentioned public
  documents; **no reply specifically said GL includes private documents.**
- **Quality control** — who provides the content. Nine replies mentioned organisations and
  individuals; **77.8% (7/9) of those considered only organisational documents to be GL.**
- **Expertise** — the authority of the content producer. Nine replies thought scientific background
  should be considered when identifying GL; **only one reply admitted a non-scientific source as GL.**

**The three abstract definitions compiled from those dimensions:**
- **Def1** — GL could be any publicly available material that can be directly obtained and is not
  published in peer-reviewed venues. *(accessibility)*
- **Def2** — GL could be any information provided by organisations without peer review. *(quality control)*
- **Def3** — GL could be from a scientific background/author and with a scientific purpose, but not a
  peer-reviewed document. *(expertise)*

A partial consensus does exist: the statement that grey literature "is produced in some way, but has
not yet been peer-reviewed in academic venue" was supported by **70% of GL users (14 of 20) and 75%
of SE experts (18 of 24)**. But the paper's headline conclusion stands: there is no commonly accepted
definition of GL in SE. One expert's reply, quoted: "There are many shades of grey literature, it is
not easy to draw any clear lines."

### The conceptual model: GL in the research lifecycle (RQ3)

The paper's fourth stated contribution. It adapts a research lifecycle model from the library-science
literature (Vaughan et al. 2013) into **five phases** in which GL can participate:

1. **Generating/proposing ideas.** GL bridges academic state-of-the-art and industrial
   state-of-practice, allowing novel research directions to be identified and prioritised (mentioned
   in 3 replies: 2/20 SRU, 1/24 SRE). Ten replies (6/20 SRU, 4/24 SRE) added that GL catches trends
   and the actual problems and interests of science and society.
2. **Searching GL.** Sources actually used, by count of mentions (Figure 9): web search engine
   (e.g. Google) 24; Google Scholar 21; SEI website 6; arXiv website 3; SAFe website 2; Hacker News
   1; Springer book 1. The paper notes DBLP routinely indexes arXiv publications, which appear to
   constitute the biggest chunk of today's GL in SE apart from theses. **Keyword-based search and
   snowballing are the two main strategies**, typically combined: use keywords on industry websites,
   analyse the returns, then snowball the results.
3. **Evaluating GL.** Overwhelmingly not done — see findings below.
4. **Using GL** (forming and evaluating conclusions).
5. **Reporting findings.**

**Four ways of obtaining GL** are identified from the wider literature (Section 6.2): (1) GL
databases; (2) customised Google search engines; (3) targeted websites; (4) snowballing.

### Evidence-based practice framing

The paper does not lay out EBSE steps. Its framing of evidence is nevertheless usable:

- The purpose of admitting GL is stated as complementing academic evidence with practice-derived
  evidence, in a field where "synthesizing and combining research and practice turn to be very
  important" (Section 2.3) because SE is practitioner-oriented.
- The paper's own contrast between the two evidence types (Section 5.2) is worth carrying forward
  verbatim in substance: **GL tends to be realistic and to report real practice, but may not be
  largely reliable or clearly presented; academic research is expected to be methodologically sound
  and well presented, but may be less relevant and of limited value in guiding industrial activity.**
- Three replies made the aggregation argument explicitly: individual GL items may be biased or
  untrustworthy, **but the aggregated result can still accurately convey the practitioner
  community's views**. That is the strongest defence of GL inclusion in the paper.
- One expert's argument for reproducibility over peer review: work published on arXiv mainly for
  timeliness should count as evidence even though the community has not verified it, because its
  reproducibility means it can be objectively examined as correct or incorrect afterwards.
- Positioning against Garousi et al. (2019): those authors combined existing SE SLR guidelines, MLR
  guidelines from other disciplines, and their own MLR experience into an initial proposal of
  guidelines for incorporating GL in SE secondary studies, structured as **three phases — planning,
  conducting, reporting — with 14 specific recommendations**. Zhang et al. position their own work
  as the complementary empirical half: Garousi et al. give methodological guidance, this paper
  establishes a systematic, evidence-based picture of what is actually being done.

### Caveats, traps and pitfalls

**From the findings (Sections 5–6):**

1. **Claiming GL use is not using GL.** 76 of the 102 reviews merely claim GL coverage in their
   search, without reporting the sample size of included GL, how the GL was used, or anything else.
   This is the paper's central empirical warning.
2. **"We followed the SLR guidelines" is not a reason for including GL.** Five reviews justified
   including GL by reference to SLR guidelines, and four survey replies said they followed
   Kitchenham & Charters to cover GL — but the authors point out flatly that **the SLR guidelines do
   not provide instructive advice on how to use GL.** A named example is given of a review that
   included both web materials and peer-reviewed literature without any detailed reasoning, simply
   stating it followed the guidelines.
3. **Quality-based definitions of GL silently sacrifice timeliness.** A definition restricting GL to
   internally quality-checked technical reports identifiable by author, report number and year of
   publication looks rigorous, but the authors observe that such definitions **overlook the
   timeliness of GL** — recent grey data may be missed entirely. This is a genuine trade-off, not a
   defect to be fixed.
4. **Snowballing-only sourcing has a systematic blind spot.** Snowballing is the most common way GL
   was obtained, and it does confer some quality assurance (reputable authors tend to find and
   produce reputable GL). But it will **miss GL not associated with highly reputed authors**, and it
   is a "relatively passive way that may miss some recent research".
5. **A quarter of GL users had no search strategy at all.** 25% (5/20) were not conscious of using any
   particular strategy, relying on intuition to pick a search string — which the paper says leads to
   continuous trials and is error-prone.
6. **Absence of quality assessment is itself a validity threat.** The paper states directly that
   without a standardised way of assessing GL quality, its use "may be a threat to the validity".
7. **Noise.** GL is often not written for academic purposes, so identifying the useful and
   trustworthy content is hard; without easy reproduction and verification, common trust in GL is
   hard to build. The paper suggests NLP may help reduce noise.
8. **GL vanishes.** Unlike white literature, GL may disappear quickly. If cited GL is not properly
   long-term archived, results cannot be double-checked or repeated, and **citing GL is itself a
   risk** unless there is an iron-cast guarantee of continued availability in a well-curated archive.
9. **There is a paucity of reliable GL sources in SE.** Health sciences has many curated lists of
   GL-producing organisations (HSRIC, MedlinePlus Organizations, Public Health Topic Pages); SE has
   nothing equivalent. Many survey participants said **good reputation is the most useful, and maybe
   the only, criterion for choosing a GL source** — an admission of how thin the tooling is.
10. **Without a common definition, GL cannot be used systematically** — the authors' own summary of
    challenge one. The strictest scope encountered is scientific-background, scientific-purpose,
    non-peer-reviewed documents; the loosest admits any unpublished material (proprietary technical
    documents, personal communications) and any properly archived web content (blogs, forum
    discussions, news reports, analyst reports).
11. **Practical prescription the paper does give:** researchers needing high-quality GL should confine
    themselves to GL close to white literature — dissertations and theses. Researchers needing
    coverage of a newly popular topic can consult more levels of GL — blogs, presentations.
    **Different quality-assessment criteria should be designed for different levels of GL.**
12. **The community wants what it does not do.** 79.2% of experts think a separate quality assessment
    of GL should be performed, while 90% of GL users did not perform one. The gap between stated
    norm and practice is the paper's sharpest finding.

**Limitations the authors state about their own study (Section 6.3)** — these double as caveats for
anyone replicating the design:

- Only secondary studies were reviewed. After trials, the authors found it **difficult to formulate a
  reasonable search string that would effectively cover primary studies including GL**, so primary
  studies were excluded at this stage. Extending to primary studies is named as future work.
- Only white literature incorporating GL was in scope, to avoid noise, consistent with the objective
  of exploring researchers' views on GL *in research*.
- Expert sampling was confined to ICSE/ESEM/EASE programme committees. The authors argue this is
  sufficiently representative because GL spans all SE topics and these are general, methodologically
  attentive venues.
- Response rates are low and are reported openly (below).
- The authors also state an explicit stance that shapes interpretation: because the aim is to improve
  practice, they "avoid to criticize the reviewed studies or their authors by all means" (Section 1).
  Findings are therefore reported in aggregate, not attributed as failings to named reviews.

### Threats to validity framework

The paper does not use a named framework (no construct/internal/external/conclusion validity
headings). Section 6.3 is titled **"Limitations"** and addresses, in effect: scope of the search
(secondary studies only, search-string feasibility), scope of the review population (white
literature with GL only), sampling frame for the expert survey (representativeness of ICSE/ESEM/EASE
programme committees), and response rate with its mitigation (escalating from first author to
co-authors). Mitigations for reviewer bias are described in the method rather than in the
limitations section: independent screening and extraction by three reviewers with cross-checking,
daily meetings for disagreement resolution, escalation to supervisors and domain experts, and
exclusion of the two author-committee-members from the expert invitee list.

**Open science note:** the study protocols (both review and survey) and the complete list of included
studies were published as an online technical report (Nanjing University TR-19-005), which is
exactly the disclosure Méndez et al. call for.

### Empirical findings worth citing

**The corpus:**
- **102** SE secondary studies incorporating GL, published up to June 2019, from **461** retrieved
  records across four libraries.
- **76 reviews (74.5%) merely claim their use of GL**; only **26 (25.5%)** report results including
  GL, e.g. sample size.
- **72 of the 102 reviews were published after 2014** — more than twice the number published before
  2014.
- **23.5%** of reviews (24 of 102: 20 in the rich-detail group, 4 in the little-detail group)
  explained *why* they chose GL.

**Survey response:**
- GL users: **22 replies = 21.6% (22/102)** after escalating from first authors (13.7% alone) to
  co-authors; **2 removed for data quality → 20 analysed.**
- SE experts: **502 invited**; 57 emails bounced and 42 automatic unavailability replies received,
  leaving 403 effective; **35 valid replies = 8.7% (35/403)**; 11 further excluded (declines or
  incomplete) → **24 analysed.**
- Per-venue expert response rates: **ICSE 3.9% (13/337); ESEM 8.5% (11/130); EASE 8.5% (10/118).**
  The authors read the higher empirical-community rates as implying empiricists in SE are more
  likely to use GL and therefore more motivated to respond.

**Types of GL used** (from the 41 reviews that specified types — all rich-detail reviews plus 15
relevant little-detail ones):
- Technical report **65.9% (27/41)** — usually found via Google Scholar (14/27) and SEI (6/27)
- White paper **41.5% (17/41)** — 13 of 17 in combination with technical reports
- Blog **22.0% (9/41)** — websites (4/9) and work-in-progress (2/9) commonly co-occur
- Book/book chapter **22.0% (9/41)** — 8 of 9 co-occur with technical report
- Thesis **17.1% (7/41)**
- **87.8% (36/41)** mentioned at least one of these five types; **61.1% (22/36)** included two types.

**Reasons for including GL** — five themes from **37 data points** (44 minus 7 duplicates), derived
by Grounded Theory:
- To seek/extend more related research — **12/37**
- To avoid publication bias — **9/37**
- To compare different perspectives between researchers and practitioners — **5/37**
- To understand the views of the practitioner community — **5/37**
- To explore uncharted research areas — **3/37**

**Attitudes and practices (Table 6):**

| Question | Yes | No |
|---|---|---|
| Should GL be included as a source of evidence in SE? (experts) | **21 (87.5%)** | 3 |
| Willing to include GL as an evidence source in own research? (experts) | **19 (79.2%)** | 5 |
| Did you conduct **separate data analysis and synthesis** for GL? (users) | 6 | **14 (70%)** |
| Did you conduct a **separate quality assessment** of GL? (users) | 2 | **18 (90%)** |
| Was GL used to **evaluate conclusions**? (users) | 5 (25%) | **15 (75%)** |

- **90% (18/20) of GL users applied no separate quality assessment of GL**, while **79.2% (19/24) of
  experts thought such an assessment should be performed.**
- **75% (15/20) of GL users formed their conclusions from traditional literature together with GL**
  rather than using GL to evaluate conclusions separately. Those who did use GL to evaluate
  conclusions said they put GL on an equal footing with traditional literature.

**Effect of GL on conclusions (Table 7):**
- Providing **similar** evidence to the academic literature — **15 (75%)**
- Providing **different** evidence from the academic literature — **4 (20%)**
- Separately: **21.1% of GL users (4/19)** thought GL offers a perspective different from academic
  literature — used, for example, to identify the gap between state-of-the-art and
  state-of-the-practice in maturity models, or to surface business benefits that only appear in GL.

**Cross-discipline comparators the paper cites (not its own findings):**
- **51% of Cochrane systematic reviews included GL** (attributed to Mallett et al. 2002), the main GL
  source there being unpublished information supplementing published trial reports.
- **Around one third** of the randomized crime-reduction experiments reviewed by Petrosino et al.
  (2000) came from GL such as government documents, dissertations and technical reports.
- GreyNet's OpenGrey database contained **a total of one million grey studies as of August 2019**.
- [EXTRACTION UNCLEAR: Figure 1, "Top 5 subjects of grey literature in GreyNet" — the six values
  401260, 291802, 253800, 99029, 74262 and 64282 cannot be reliably matched to the six labels
  (social science, biological and medical science, physics, mechanical and industrial, computer
  science, others) because the plot's axis layout is destroyed in the text extraction. What the text
  *states* around the figure is safe to use: the amount of GL in SE is growing rapidly even though
  Figure 1 does not reflect that trend, which may imply that GL use in SE is far below that in social
  sciences and medicine.]
- **Five recurring concerns of GL in the wider research literature (Table 1):** scope (what GL is and
  its characteristics), search (efficient searching), analysis (resolving structural differences
  between grey and traditional literature), evaluation (the quality problem), and effects (GL's
  effect on results and conclusions). These five are the axes the paper uses to justify studying
  secondary studies.

**The paper's own conclusion on state of the art:** GL use in formal SE research "has started gaining
acceptance, albeit slowly", but the absence of a commonly accepted definition is described as "a sign
of 'not mature'". The authors name the next task as producing a framework for assessing GL in SE plus
a clear set of recommendations/guidelines for its use, and suggest that **web content may be the next
frontier of GL in SE**, since open communities such as GitHub make far more grey data available.

---

## stol_2016 — Grounded Theory in Software Engineering Research: A Critical Review and Guidelines

*Klaas-Jan Stol, Paul Ralph, Brian Fitzgerald. ICSE '16, Austin TX, 14–22 May 2016, pp. 120–129.
DOI 10.1145/2884781.2884833.*

**Role in corpus:** The only paper here that treats a *named method* as something that can be
falsely claimed, and gives the diagnostic test for the false claim. Its concept of **method
slurring** — and its rule that a study lacking the core practices simply is not a grounded theory
study regardless of what it says — transfers directly to how a secondary study should appraise
primary studies that self-label their methods.

**Research question:** What is the state of practice of grounded theory research in software
engineering?

**Stated stance.** The authors are explicit that their purpose is not to criticise the papers in
their sample or their authors, but to draw attention to prevalent misunderstandings — and they
contend that **only research embodying GT's core principles should claim to be a grounded theory
study.** They also state, in contrast to Glaser, that they **accept any variant of GT as grounded
theory**, while arguing that consistency with a chosen variant is essential.

### What grounded theory is

GT is a method of **inductively generating theory from data**, originally described by Glaser and
Strauss in *The Discovery of Grounded Theory* (1967). Its goal is to **generate** theory, not to
test or validate existing theory. It suits questions of the form "what's going on here?" GT studies
often centre on unstructured text — interview transcripts, documents, field notes — but may also
include structured text, diagrams, images, and even quantitative data.

The paper's argument for why SE needs it: SE is a young discipline that has yet to establish and
validate abundant formal theories, and because of the unique and novel aspects of its underlying
technology, theories borrowed from other disciplines may not adapt easily. Inductive approaches are
therefore needed to construct a relevant conceptual and theoretical foundation.

Historical note the paper makes: GT arose from dissatisfaction with a regime in which new
researchers were trained as "theoretical serfs" who tested the theories of "theoretical capitalists"
(Glaser's phrasing), theories that could lack real-world relevance.

### The core practices (Section 2.1)

These are the features shared across variants. The paper is careful to say the list is not a
complete description of GT — both Glaser and Strauss wrote several books each — but it is the set
against which the review's coding was performed. Eleven items:

1. **Limit exposure to literature.** Rather than opening with a comprehensive literature review, GT
   proponents recommend limiting exposure to existing literature and theories to promote
   open-mindedness and pre-empt confirmation bias. The stated major reason: to prevent the researcher
   from testing existing theories or thinking in established concepts. (Positions differ by variant —
   see the comparison table below.)
2. **Treat everything as data.** Glaser's "all is data" means all: qualitative data, quantitative
   data, semi-structured data, pictures, diagrams, videos, and even existing theories and literature.
3. **Immediate and continuous data analysis.** Analysis begins immediately; data collection does not
   finish before analysis begins. **Collection and analysis are simultaneous**, and subsequent
   collection is driven by theoretical sampling.
4. **Theoretical sampling.** The researcher identifies further data sources based on gaps in the
   emerging theory, or to explore concepts not yet saturated. It is **indeterministic**, unlike
   conventional sampling techniques — you cannot specify the sample in advance.
5. **Theoretical sensitivity.** The researcher's ability to conceptualise and to establish
   relationships between concepts. The paper places this "at the heart of developing grounded
   theory", and notes that both Glaser and Strauss & Corbin highlight the role of **creativity** in
   it.
6. **Coding.** The researcher uses inductive and abductive logic to construct analytical codes and
   infer theoretical categories by labelling 'incidents' and their properties. Crucially, the
   researcher **does not classify data into a preconceived coding scheme, nor infer categories from
   logically deduced hypotheses.** Historical nuance the paper adds: Glaser and Strauss did not use
   the term abduction but emphasised induction, to distance themselves from the deductive theorising
   prevalent at the time; both later admitted a role for deduction.
7. **Memoing.** Writing memos — notes, diagrams, sketches — to elaborate categories as they emerge,
   describe preliminary properties and relationships, and identify gaps. The paper quotes Glaser's
   flat verdict: if the researcher skips this stage, "he is not doing grounded theory" (Glaser's own
   emphasis).
8. **Constant comparison.** From the start of the study, the researcher constantly compares data,
   memos, codes and categories. Both categories and interpretations evolve and saturate until they
   'fit' the data.
9. **Memo sorting** (theoretical sorting). Continuous oscillation between the memos and the emerging
   theory outline to find a suitable fit for all categories resulting from coding. Like memoing,
   Glaser argues sorting **cannot be skipped**.
10. **Cohesive theory.** The researcher must move beyond superficial categories to develop a cohesive
    theory of the phenomenon.
11. **Theoretical saturation.** Collection and analysis stop when the theory's components are well
    supported and **new data no longer triggers revisions or reinterpretations** of the theory.

### Philosophical foundations (Section 2.2)

The paper's point is that **GT does not fit cleanly into either positivism or interpretivism**, and
that mistaking it for a qualitative or interpretivist method is an error — GT was developed in the
1960s, during the shift from positivism/objectivism toward social constructionism and postmodernism,
and was developed out of a desire to build theories more rigorously and dispassionately by grounding
them in objective reality.

**Positivism's five pillars,** as the paper lists them: unity of the scientific method (the same
approach to knowledge acquisition applies to all forms of enquiry); the search for causal
relationships; belief in empiricism (sense-experience is the only source of knowledge, and
subjective perception is not acceptable); science as value-free (independent of politics, ideology,
morality, society and culture); and science founded on logic and mathematics (causal relationships
demonstrated quantitatively). Its assumptions: the universe behaves according to inalterable,
discoverable laws; systems are merely the sum of their components (reductionism); science should be
reproducible, reliable, rigorous and objective, so different scientists observing the same
phenomenon reach equivalent conclusions.

**Interpretivism's opposite assumptions:** no universal truth or reality exists, rather "the
important reality is what people imagine it to be"; systems exhibit emergent behaviours not
reducible to their parts; social science is fundamentally different from natural science, and
natural-science methods including quantitative measurement, statistical significance and hypothesis
testing are insufficient for social phenomena. **Formulating hypotheses is therefore not relevant to
an interpretivist study.** Understanding the social world requires emotion and empathy, which
preclude pure objectivity.

The paper then refuses the dichotomy, giving concrete counterexamples from SE: experiments whose
dependent variable is measured by combining subjective expert ratings; case studies with upfront
hypotheses; interview studies where text is analysed quantitatively; mixed-method inquiries combining
questionnaires with case studies. It endorses the observation that all qualitative data can be coded
quantitatively by counting words and categorising statements, while all quantitative data rests on
qualitative judgement because assumptions are needed to interpret the numbers. Its conclusion:
these groups involve several interconnected philosophical positions that **cannot be reduced to a
single spectrum, let alone a Boolean variable.**

### The variants and their coding procedures (Section 2.3, Table 1)

Denzin lists **no fewer than seven** versions of GT. It is widely acknowledged that there are at
least **three main streams**: Glaser's (classic or Glaserian), Strauss and Corbin's (Straussian),
and Charmaz's constructivist. GT has been labelled a "contested concept" because of the extent of
disagreement about what it is.

**The disputes themselves.** Glaser strongly disagrees with Strauss and Corbin's version, argues
that it is not grounded theory at all, and calls it "full conceptual description". He has called
constructivist grounded theory a "misnomer". Corbin has gradually shifted toward interpretivism;
Charmaz, a student of Glaser, reinterpreted GT from a constructivist stance closely connected to
interpretivism. Strauss increasingly saw GT as a **verificational** method, a position Glaser
strongly rejects.

**The emergence-versus-forcing distinction**, which is the practical heart of the classic/Straussian
split: classic GT has a strong focus on **emergence** — of research questions, of codes, of theory —
whereas Straussian GT prescribes a set of 'mini-steps'. The paper quotes Stern's summary: Strauss, as
he examines the data, stops at each word to ask "What if?"; Glaser keeps his attention on the data
and asks "what do we have here?" Glaser requires every concept to be grounded in the data; Strauss
and Corbin go beyond the data by asking what might be. Strauss's approach has been described as
"more free-wheeling flights of imagination", contrasting with Glaser's faithfulness to the data.

**A terminological trap the paper flags:** the 1998 edition of Strauss and Corbin specifies open,
axial and selective coding; the **2008 edition, authored by Corbin alone after Strauss died in 1996
— which makes "Straussian GT" a misnomer and "Corbinian" more appropriate — no longer defines open
and axial coding as separate activities.** The paper deliberately focuses on the 1998 version
because it is very prevalent, axial coding in particular. Straussian GT is therefore still evolving,
which makes the variants harder to compare.

**Comparison across six elements** (paraphrased from Table 1):

**Research question**
- *Classic:* should **not** be defined a priori but must emerge from the research — this is what
  makes it relevant to the field. The researcher starts with an "area of interest". Literature in
  *other* areas may be consulted to increase theoretical sensitivity. Defining an RQ a priori is
  considered **'forcing'**.
- *Straussian:* the RQ may be defined upfront, derived from the literature or suggested by a
  colleague; it is often broad and open-ended.
- *Constructivist:* research begins with "initial research questions" which evolve throughout.

**Role of the literature**
- *Classic:* an extensive literature review should be **delayed until after the theory is emerging**,
  to prevent existing concepts influencing it. Until the RQ is defined it is not clear which
  literature should be consulted. Existing concepts such as gender and age must not be included a
  priori; they must **'earn' their way** into the emerging theory.
- *Straussian:* literature may be consulted throughout — concepts from it may be used if applicable;
  to enhance theoretical sensitivity; as a secondary data source; to formulate data-collection
  questions or stimulate questions during analysis; and to suggest areas for theoretical sampling.
- *Constructivist:* accepts Glaser's reasons for delay **and** the impracticality of the strategy;
  Charmaz calls for tailoring the literature review to fit the purpose of the GT study.

**Coding procedures** — the operational core:
- *Classic (Glaser):* **Open coding** — 'fracturing' the data; line-by-line coding recommended to
  achieve full theoretical coverage, though coding sentences, paragraphs or whole documents is not
  rejected. **Selective coding** — delimiting coding to only those variables relating to one (or
  sometimes several) **core variables**, to establish a parsimonious theory; the core variable then
  guides further data collection. **Theoretical coding** — establishing conceptual relations between
  substantive codes, resulting in hypotheses; Glaser offers several **'coding families'** of
  theoretical codes, which must themselves earn their way into the theory (e.g. the Six C family).
- *Straussian:* **Open coding** — generation of categories and how they vary dimensionally; may be
  done line by line, by sentence, by paragraph, or over a whole document. **Axial coding** — putting
  the data back together in new ways after open coding by identifying relationships between
  categories; this is effectively Glaser's theoretical coding. Uses the **'paradigm model'** or
  **'conditional matrix'** to identify context, conditions, action/interaction strategies and
  consequences. **Selective coding** — deciding on the central category to which all major categories
  can link. *Note:* Strauss and Corbin interpret selective coding **differently from Glaser** — a
  named source of confusion.
- *Constructivist (Charmaz):* **Initial coding** — examining data word-by-word, line-by-line or
  incident-by-incident to make sense of the text without injecting the researcher's assumptions,
  biases or motivations; similar to Glaser's open coding. Charmaz recommends **"coding with
  gerunds"**. **Focused coding** — selecting categories from the most frequent or important codes and
  using them to categorise the data; **does not require a single core category or variable.**
  **Theoretical coding** — specifying relationships between categories to integrate them into a
  cohesive theory.

**Questions asked during analysis**
- *Classic:* What is this data a study of? What category, or what property of what category, does
  this incident indicate? What is actually happening in the data?
- *Straussian:* questions about whom, when, where, how, with what consequences, and under what
  conditions phenomena occur — to 'discover' important ideas; the "free-wheeling flights of
  imagination".
- *Constructivist:* What is this data a study of? What do the data suggest / pronounce / leave
  unsaid? From whose point of view? What theoretical category does this specific datum indicate?

**Philosophical influences**
- *Classic:* **objectivism** — there exists a single correct description of reality; the researcher
  therefore *discovers* grounded theory from data.
- *Straussian:* **pragmatism and symbolic interactionism** — actors engage in a world requiring
  reflexive interaction; reality is constructed through interaction and relies on language and
  communication.
- *Constructivist:* **social constructionism** — social reality is constructed by individual and
  collective action; GT emerges from shared experiences and relationships with participants;
  observers are not neutral.

**Evaluation criteria** — note that each variant supplies its own, so a study should be judged by
the criteria of the variant it claims:
- *Classic (Glaser's four):* the generated categories must **fit** the data; the theory must **work**
  (it must explain or predict what will happen); the theory must have **relevance** to the action of
  the area; and the theory must be **modifiable** as new data appear.
- *Straussian:* **seven criteria for the research process** (e.g. information on sample selection,
  major categories, derived hypotheses, discrepancies) plus **eight criteria regarding the empirical
  grounding** (e.g. "are concepts generated?", "is variation built into the theory?").
- *Constructivist (Charmaz's four):* **credibility** (is there sufficient data to merit the claims?),
  **originality** (do the categories offer new insights?), **resonance** (does the theory make sense
  to participants?), and **usefulness** (does it offer useful interpretations?).

The paper also observes that there is little agreement on what constitutes *theory* itself: in
classic GT, theory is concepts related to one another offering explanation and prediction;
constructivist GT emphasises understanding and acknowledges that data, interpretations and theory
depend on the researcher's view. In practice, however, **such ontological and epistemological
differences are rarely apparent in the generated theories.**

### The review method (Section 3)

**Search.** Automated search chosen over manual browsing because it is more efficient and
replicable. Pilot testing of several strings: searching "grounded theory" alone returned thousands
of papers from other disciplines; limiting to title/abstract/keywords missed GT studies that do not
use the term in those fields. Final string:

`"grounded theory" AND "software engineering"`

**Databases and constraints** (Table 2). Wiley Online and SpringerLink were excluded as subsumed by
Scopus. Constraints were introduced case-by-case to eliminate obviously irrelevant papers.

| Database | Constraint | Records |
|---|---|---|
| Scopus | none (full text) | 1,668 |
| ScienceDirect | Computer Science only (full text) | 249 |
| IEEE Xplore | metadata only | 73 |
| ACM DL | title, abstract, keywords only | 13 |
| Subtotal | | 2,003 |
| Duplicates removed | | 240 |
| **Total** | | **1,763** |

**Narrowing.** 1,763 was too large for manual analysis, so the review was confined to articles in
nine well-known peer-reviewed SE **journals**. Conference contributions were excluded on the
grounds that journal papers endure greater review, are more polished, and have more liberal page
limits. Peer-reviewed magazines (CACM, IEEE Software) were excluded because their practitioner focus
produces briefer methodological descriptions. Specialist journals (Requirements Engineering,
IJOSSP) were excluded in the interests of representativeness. The journal set coincides with those
used in previous reviews, plus the Software Quality Journal and the descendants of the Journal on
Software Maintenance.

| Journal | Articles |
|---|---|
| Information and Software Technology | 42 |
| Journal of Systems and Software | 16 |
| IEEE Transactions on Software Engineering | 11 |
| Empirical Software Engineering | 10 |
| Software Process: Improvement and Practice | 8 |
| Journal of Software: Evolution and Process | 4 |
| Software Quality Journal | 3 |
| ACM TOSEM | 3 |
| Journal of Software Maintenance and Evolution | 1 |
| **Total** | **98** |

Editorials, secondary studies (systematic reviews), and articles presenting methodological
reflections on GT rather than a GT study were removed, giving the final set of **98 papers** (listed
in an online appendix). Search conducted Spring 2015.

**Data extraction — seven questions asked of every paper:**
- What is claimed concerning the use of GT? (e.g. "we used grounded theory", "we took a grounded
  theory approach", "the data were coded using GT techniques")
- To what extent are different variants of GT discussed and used? To what extent do papers state
  their epistemological stance?
- Is GT mentioned in the title, keywords, abstract, or research question/objective/topic/purpose?
- What specific GT techniques and practices are used? (open coding, constant comparison, memoing)
- How is data collected and analysed?
- What do GT studies produce and how do they present it? (e.g. as a diagram)
- Was the literature review, if any, conducted before, during or after the study; was the resulting
  theory integrated back into the literature?

All recorded in a spreadsheet, with extensive notes on findings outside the predefined questions —
for example, the use of preconceived **'seed categories'** to guide initial analysis, which is
inappropriate in GT. **Extraction and coding were done by the primary author and reviewed by the
remaining authors.**

### What the review found (Section 4)

**Structure of the sample (Figure 3):**

- **N = 98** reviewed.
- **[1] Merely using GT techniques: n = 46** (almost half).
  - [1.1] Adapted, inspired by, or resembling GT: **15**. Example claim: "In a method similar to the
    first step in grounded theory […] we identified a set of categories." The paper's verdict: such
    studies are clearly not GT studies.
  - [1.2] The term 'grounded theory' does not appear in the main text at all, only in the
    bibliography: **18**. These mention specific techniques such as 'coding' or 'theoretical
    saturation' and cite seminal GT works.
  - [1.3] Claiming GT 'techniques' or 'procedures', mostly coding and constant comparison: **13**. In
    several cases the authors explicitly acknowledge their study is not a GT study.
- **[2] Explicitly claiming GT: n = 52.**
  - [2.1] No details at all beyond the bare claim: **18**.
  - [2.2] Deviating from GT so sharply that GT was not used at all: **4**. In three of those, the
    authors developed a set of **preliminary categories** and then combined them with a "grounded
    theory approach" — starting from a classification taken from the literature, which the paper
    calls highly suspect even under Strauss and Corbin's liberal use of literature.
  - [2.3] Detailed: **30**, of which
    - [2.3.1] Comprehensive and detailed: **5**
    - [2.3.2] Comprehensive: **11**
    - [2.3.3] Coding details only: **14**
  - **So only 16 of 98 articles (5 + 11) give a comprehensive presentation of their research method.**

*(Minor textual defect in the paper: Section 4.1 refers to the four sharply deviating studies as
"Box 2.1", whereas Figure 3 places them in Box 2.2 and Box 2.1 holds the 18 no-detail studies. The
figure is the consistent reading.)*

**The "borrowing rhetoric" observation, which is the paper's sharpest rhetorical point.** The
authors note they do not recall ever reading about studies that "use randomized controlled trial
techniques", were "inspired by survey methodology", or "adopted a modified questionnaire approach".
Claiming to use "grounded theory techniques" rather than grounded theory suggests authors are aware
that GT is a comprehensive method from which they are borrowing elements.

**Ambiguity is itself a finding.** Deciding whether a study uses GT is far from trivial; the phrasing
of claims varies substantially and some are ambiguous ("a grounded theory approach" could mean GT was
used, or merely an approach based on GT). The authors state this is **simultaneously a threat to
their own validity and a surprising finding**: the count of 52 should be read with caution, but that
the question is ambiguous at all, and that a large proportion of studies borrow from a method rather
than use it, is unusual and problematic for sound evaluation.

**Signalling:** 6 of the 98 used 'grounded theory' in the title; 14 specified it as a keyword. The
authors read this as suggesting GT was essential to those studies rather than an afterthought, while
cautioning that keyword limits (as low as three in some journals) make this weak evidence.

**Practices actually reported, among the 30 detailed articles (Table 4):**

| Practice | Papers reporting |
|---|---|
| Data sources and collection | 29 |
| Coding | 29 |
| Theoretical saturation | 15 |
| Simultaneous data collection and analysis | 13 |
| Constant comparison | 13 |
| Theoretical sampling | 12 |
| Memoing | 12 |
| Memo sorting | 4 |

**Fewer than half of the 30 describe or confirm the key practices** of simultaneous data collection
and analysis, memoing, memo sorting, constant comparison, or theoretical sampling. All but one
discuss data sources and describe coding. The paper's term for this pattern is **"GT techniques à la
carte"**.

**Misinterpretations found.** One article claimed theoretical sampling but had actually selected case
companies seemingly a priori, based on their experience in the area under investigation, rather than
collecting additional data to investigate unsaturated concepts. Some articles gave brief, incomplete
summaries stating that GT consists of three coding phases — incomplete, and misleading in suggesting
coding happens in three distinct phases, which is not what Glaser or Strauss intended.

**Variants ignored (Table 5).** Of the 52 claiming GT:
- **39 did not acknowledge the existence of different variants.** Among those 39: 10 cited classic
  works (Glaser, Glaser & Strauss); 13 cited Straussian works; **0 cited constructivist works**; 13
  cited a conflicting combination without acknowledging any difference or indicating whose guidance
  they follow; 3 cited neither seminal source but other works.
- **13 acknowledged the classic/Straussian distinction**, some in detail: 5 explicitly claimed
  classic GT, 8 claimed Straussian GT, **0 claimed Charmaz's constructivist GT.**
- Two articles cited works on all three variants. The authors' comment: one reading is that authors
  aware of the differences pile on references to confer legitimacy — but had they actually read all
  three works, the existence of variants would likely have been acknowledged.
- Three articles cite no seminal GT text at all. The authors offer both a charitable and an
  uncharitable reading: innocent mistakes or benevolent simplifications, or **researchers presenting
  research under the guise of techniques they have heard of but not investigated.**
- **Inconsistent use of the claimed variant:** two articles claim or cite classic GT but use **axial
  coding**, a Straussian practice; another claims Straussian GT but uses one of **Glaser's coding
  families**.
- **Only 5 articles state an epistemological position**, all claiming to be interpretivist — and in
  **four of those five, the references given are to Glaser or Strauss & Corbin, which align more
  closely with positivism.** This is a direct internal contradiction.

**Few "GT" studies generate theory (Section 4.4).** Since GT is a method of generating theory, the
authors checked how many of the 52 did so. Few appear or claim to develop a theory, even though "a
lack of existing theories" in an area is frequently the stated motivation for doing a GT study.
- **8 articles presented clearly cohesive theories** consisting of constructs and relationships; a
  **ninth** presented a set of hypotheses that could be considered a theory. Topics theorised
  included how the software development process is managed, how software processes form and evolve,
  and how self-organising agile teams self-organise.
- Some present theory in alternative forms that the authors are willing to count: Hoda et al.'s six
  roles that agile team members assume together explain the social process of self-organisation, and
  so go beyond a taxonomy of roles; the authors argue such a coherent set of findings can be
  considered a theory.
- Most present a graphical representation, usually simple boxes-and-arrows diagrams. **Three use
  Glaser's 'Six C' coding family** for visualisation — Context, Condition, Causes, Consequences,
  Contingencies, Covariance.
- Other outputs, which are useful as foundations for empirical studies but often do not form a theory
  that, in Glaser's words, accounts for a pattern of behaviour: **conceptual frameworks**
  (e.g. factors influencing Software Process Improvement initiatives); **conceptual models** (e.g. a
  model of the process for managing collaborations in open source); **sets of factors** (e.g. success
  factors for globally distributed XP projects); **sets of themes or categories** (e.g. categories
  characterising product managers).
- **10 articles present mere description**, typically structuring results around research questions
  answered with participant quotes — common among studies that used only coding techniques without
  making a theoretical contribution.
- The authors' correlation: **studies producing a 'set of themes' rather than a theory tend only to
  borrow discrete practices from GT** — grounded theory à la carte.

### Method slurring — the misuse of the label (Section 5.1)

**The definition.** Claiming to use a research method without actually following its guidelines is
**"method slurring"**, a term the paper takes from Baker, Wuest & Stern (1992).

**The operational test — stated twice, and this is the most citable part of the paper.**

> If a study does not involve simultaneous data collection and analysis, constant comparison, coding,
> memoing and theory development, it is **not** a grounded theory study.

And the disqualifying behaviours:

> If researchers collect most or all of their data before beginning analysis, collect or categorize
> data according to existing theory, base analysis on seed categories or preconceived analytical
> frameworks, they are **not** using grounded theory.

**Five reasons the authors suggest researchers commit method slurring:**
1. **To confer legitimacy.** GT is more structured, and therefore often perceived as more scientific,
   than other methods of building theory from unstructured data. Charmaz's complaint is quoted: many
   researchers "have invoked grounded theory as a methodological rationale" to justify doing
   qualitative research rather than adopting its guidelines to inform their studies.
2. **To avoid a detailed literature review and initial conceptualisation.** Researchers may embrace
   the GT maxim of avoiding over-familiarity with the literature as an excuse to skip necessary
   background work.
3. **For simplicity.** It is easier to write "we used grounded theory" than to explain how a large
   volume of unstructured text became a cohesive theory. The authors reject this: because GT is not
   widely understood — misunderstood, even — among SE researchers, the bare claim does not suffice.
4. **Because they do not understand GT or its relationship to other methods.** Suddaby is quoted:
   researchers claim to have performed grounded theory research and support the claim with a cursory
   citation to Glaser and Strauss (1967) while describing little of the method; when invited to
   elaborate on how data were collected and analysed, it becomes clear that "grounded theory" was
   interpreted to mean "anything goes".
5. **Per a referee's suggestion.** The authors know of cases where referees told authors their method
   "looks like grounded theory"; authors may then present their research post hoc as GT, where the
   claim is not valid, simply to satisfy reviewers.

**Four consequences of method slurring:**
- **It undermines grounded theory.** Corroborating observations are cited from management ("overly
  generic use of the term") and information systems (the term "has almost become a blanket term for a
  way of coding data"), and others speak of the "erosion of GT as a research method". Using the term
  for any theory-building or qualitative analysis undermines the legitimacy of a method that
  prescribes a highly structured analytical approach, and **engenders undue suspicion of genuine GT
  studies, possibly hindering their publication.**
- **It undermines other qualitative methods.** GT is not the only valid way to analyse predominantly
  qualitative data or to generate theories. Recasting interpretive interview studies, positivist case
  studies and ethnographies as grounded theory **implicitly disparages and devalues** those
  legitimate approaches. There is nothing wrong with conducting an ethnography and researchers should
  not hesitate to label it as such. Theories can also be developed from intuition and experience, or
  by extending and synthesising existing research.
- **It misrepresents the research.** A key principle of science communication is accurately describing
  how data was collected and analysed, so that reviewers and readers can evaluate quality. Claiming
  GT while doing something different violates that principle.
- **It defeats appraisal.** Because so many GT articles lack methodological detail, readers cannot
  assess whether a study actually uses GT or merely references it "as a methodological rationale".

### Guidelines: conducting and reporting (Section 5.2)

**Four broad recommendations:**

1. **Study grounded theory before starting.** GT suffers from its "apparent simplicity" —
   superficially it looks like reading and categorising text, but the key challenge is theoretical
   sensitivity, and GT is a complicated method with multiple variants and conflicting guidance. Many
   SE method overviews do not even include GT. Anyone considering a GT study should **read several
   books before even deciding whether GT is the right method**, let alone before collecting data. GT
   must be considered from a study's conception, because it differs significantly from traditional
   studies. The decisive sentence: **"Research cannot be reconstructed as GT at write-up."**
2. **Describe your implementation of GT, not GT in principle.** Some sampled studies gave reasonable
   summaries of GT but never explained their own practices, deviations, or what they actually did.
   Explicitly describe how key practices — simultaneous data collection and analysis, constant
   comparison, memoing — were used, **and explicitly describe deviations from GT guidelines.**
3. **Avoid 'borrowing' rhetoric.** If techniques have been borrowed from the GT literature, simply
   state that those techniques were used **without discussing GT**. Coding, memoing and constant
   comparison are all part of the contemporary qualitative analyst's toolbox; they can exist
   independently of their proponents or of any particular method. **"Bringing in GT clouds the
   issue."**
4. **Do not claim to have used grounded theory when you have not.** Describe how data was analysed or
   theory generated. If another method was used, name it. If you developed your own method, explain
   it. **If you proceeded ad hoc, explain the "pragmatic, agile approach" rather than dressing it up
   as grounded theory.**

**The reporting checklist (Figure 5)** — synthesised from existing GT and qualitative methodological
guidance plus the authors' own experience. It is explicitly *not* a checklist every paper must
satisfy: "No single article can or should include all of these items"; they are offered as
"questions to ask oneself" before and during a study and at write-up. Five groups:

*General grounded theory issues*
- What variant of GT have you adopted? What published guidance did you follow?
- How and why have you adapted, or deviated from, this variant and guidance?
- State the research area or research question — your initial question, the question that emerged
  during the study, or preferably both.
- State your epistemological and ontological positions (e.g. interpretivism, critical realism).
- State the duration of the study.

*Site selection and description*
- What organisation, team, dataset etc. did you study?
- Why did you study this data?
- Describe the context (kind of organisation, who is involved, what kind of software is being built).

*Role of the literature in the GT study*
- Did you begin data collection with a clean theoretical slate?
- What topic areas did you review before and during the study?
- How does the literature inform, support or refute your analysis and results?

*Presenting and evaluating grounded theory*
- Is the theoretical contribution clearly stated?
- Is the generated theory integrated back into the literature?
- Is the theory evaluated? If so, using which criteria?
- How might your own biases, preconceptions, background and beliefs affect your analysis?

*Grounded theory data collection and analysis*
- What data was collected (field notes, documents, emails, video of meetings), how and when?
- Who collected and analysed the data — an individual or a team? If a team, who did what, and how was
  it coordinated?
- Describe the pacing of analysing data, and how it continued throughout the project.
- Describe your coding, memoing and sorting **with examples**.
- Describe the emergence of your core category, and how this affected your analysis.
- If using classic GT, did you use any of Glaser's coding families? If so, which, and did the
  theoretical codes earn their way into the theory?
- If using Straussian GT, state how you used the conditional matrix.
- How and where was your data stored? How did you manage the volume and heterogeneity of data?
- Describe your theoretical sampling **with examples**.
- Confirm that you employed constant comparison.
- When did you stop collecting data? Describe how theoretical saturation became apparent.
- Describe how the selected GT variant affected data collection and analysis.
- Did you conduct a reliability check — i.e. have your analysis reviewed by someone else? If so, who,
  how, what did they find, and what changes resulted? Describe their expertise.

### Caveats, traps and pitfalls

Consolidated; all paraphrased from the paper.

1. **Method slurring** — claiming a method without following it. The single named pathology.
2. **GT cannot be applied retrospectively.** Research cannot be reconstructed as GT at write-up,
   because the method dictates the *order* of collection and analysis.
3. **Seed categories and preconceived frameworks disqualify a study from being GT.** So does
   collecting all data before analysing, and categorising data according to existing theory.
4. **Starting from a classification taken from the literature is highly suspect**, even under
   Straussian GT's liberal literature stance.
5. **Mixing variants inconsistently** — claiming classic GT while doing axial coding, or Straussian
   GT while using Glaser's coding families — is a concrete, checkable defect.
6. **Citing conflicting seminal works without acknowledging the conflict** signals that the authors
   have not read them.
7. **Declaring an interpretivist epistemology while citing objectivist sources** is an internal
   contradiction found in four of the five papers that stated any epistemology at all.
8. **Describing GT in principle instead of describing what you did** is not a methods section.
9. **"GT consists of three coding phases" is a wrong summary** — it is incomplete and falsely implies
   three distinct sequential phases.
10. **Theoretical sampling is not purposive sampling.** Selecting cases a priori for their relevance
    to the topic is not theoretical sampling; theoretical sampling responds to gaps in the emerging
    theory and is indeterministic.
11. **Memoing and memo sorting cannot be skipped** (Glaser). Memo sorting was the least-reported
    practice in the entire sample — 4 of 30.
12. **A set of themes is not a theory.** Nor is a taxonomy, a set of factors, or a description
    organised by research question. GT that generates no theory has not achieved its purpose.
13. **Space constraints are a weak excuse.** The authors reviewed only journal articles precisely so
    that page limits could not explain the missing detail.
14. **The apparent simplicity of GT is a trap** — it looks like reading and categorising text.
15. **A missing methodological detail is not proof of poor research.** The authors state this
    explicitly in their limitations: they can only analyse how a study is *reported*, not how it was
    *done*.

### Three challenges peculiar to grounded theory in software engineering (Section 5.3)

The paper's fourth contribution, and unique to it. Most GT research the authors have read relies
primarily on interviews and documents, but software contexts offer far more: source code, test
suites, commit logs, task and effort data from project management tools, design diagrams (wireframes,
class diagrams), design documents, domain models (scenarios, personas, user stories, use cases),
project management documents (backlogs, burn-down charts), performance data, issue tracker data,
photographs of whiteboard diagrams, online discussions (IRC, Slack), contracts and financial
statements — all on top of the usual interview and meeting recordings, email and field notes. Three
challenges follow:

1. **Managing large amounts of heterogeneous data.** Version control, project management and team
   communication systems make it trivially easy to acquire an enormous, unreadable dataset.
   Capturing, storing, indexing and managing it is practically hard; a system suited to one data type
   (NVivo for audio, video, transcripts and documents) may be unsuitable for another (code). Deciding
   what to read when there is more text than can be read in a lifetime is harder still, and **the
   implications of data magnitude for theoretical sampling remain unclear.** One strategy the paper
   offers: choose an explicit **primary data source** (e.g. interviews) and theoretically sample from
   the remaining data based on leads arising from that primary source.
2. **Coding unconventional texts.** GT's coding approaches were developed primarily for unstructured
   text. It is not clear how to apply open coding to design diagrams, structured text such as use
   cases, or source code. Two strategies offered: open-code the unstructured text and **move directly
   to memoing for more structured data**; or adopt completely different analytical techniques such as
   static code analysis.
3. **Cross-referencing participant statements with records.** Participants' post-hoc reconstructions
   of how and why they acted are less reliable than their accounts of current frustrations or
   enduring values. Source code, commit logs, project management data and direct observation allow
   many interviewee claims to be triangulated — which raises myriad challenges **not only about how
   to triangulate but about how to resolve conflicting evidence.**

### Threats to validity framework

The paper does not use a named validity taxonomy; it states limitations in the conclusion. Those
limitations, and they are worth reusing as a template for any "state of practice" review:

- **Venue coverage.** Limited to nine well-known SE journals, believed to be a reasonable surrogate
  for the broader literature, but the field has many more including area-specific journals (e.g.
  Requirements Engineering).
- **Publication type.** Conference papers excluded, on the reasoning that page limits would force
  less methodological detail — a deliberate bias in favour of finding *more* detail than exists in
  the literature overall.
- **Search bias.** Articles may have been missed because of the specific search string and strategy,
  or because of publication bias.
- **Reporting versus conduct — the fundamental limit.** "We can only analyze the way each study is
  reported rather than how it was done." A few missing methodological details does not mean the
  research is poor or the authors unskilled; the review reveals that more methodological detail is
  needed and suggests what to include.
- **Self-identified threat from within the analysis:** the ambiguity of GT-use claims makes the count
  of 52 uncertain, and the authors flag this as a threat to their own validity in the same breath as
  reporting it as a finding.

### Empirical findings worth citing

- **98** articles reviewed, from **1,763** deduplicated records (2,003 before removing 240
  duplicates) across four databases, drawn from **nine** SE journals; search conducted Spring 2015.
- **52 of 98 (53%) explicitly claim to use GT; 46 (47%) merely borrow GT techniques.**
- **Only 16 of 98 (16%) provide a comprehensive account of their research procedures.** 30 of the 52
  claimants provide significant methodological detail; 18 provide none at all beyond the bare claim;
  4 deviate so sharply that GT was not used.
- **39 of the 52 claimants (75%) do not acknowledge that GT has variants.** 13 do; of those, 5 claim
  classic, 8 claim Straussian, and **none claim constructivist GT.** No article in the entire sample
  cited Charmaz.
- **Only 5 of 98 articles state an epistemological position**, all claiming interpretivism, and 4 of
  those 5 cite sources aligned with positivism.
- Practice reporting among the 30 detailed articles: data sources 29, coding 29, theoretical
  saturation 15, simultaneous collection and analysis 13, constant comparison 13, theoretical
  sampling 12, memoing 12, **memo sorting 4**.
- **8 articles produced cohesive theories** (a ninth produced hypotheses that could count); **10
  produced mere description.**
- 6 articles used 'grounded theory' in the title; 14 used it as a keyword.
- **Growth trend:** a Scopus search on TITLE-ABS-KEY("grounded theory") limited to computer science,
  run August 2015, shows GT studies in computer science rising over the decade to 2015, from near
  zero in 1996 toward roughly 150–200 per year by 2014. [EXTRACTION UNCLEAR: exact per-year values in
  Figure 1 and Figure 2 are not recoverable from the text extraction; only the axis maxima (200 for
  Figure 1, 25 for Figure 2) and the shape of the trend are legible. Figure 2's 2015 value is
  artificially low because the search was run in Spring 2015.]
- Exemplar GT studies in SE that the paper names as worth consulting (five articles presenting
  extensive documentation of the GT research process) include work by Adolph, Kruchten & Hall and by
  Hoda et al.

**The paper's closing position:** despite the SE-specific challenges, GT "remains one of the most
rigorous methods to generate new theories", and building a strong theory base has been identified as
an important challenge for the discipline — so well-conducted GT studies can contribute significantly
and help develop rich theories to inform future empirical work.

---

## fatima_2023 — Retrieving arXiv, SocArXiv, and SSRN metadata for initial review screening

*Rubia Fatima, Affan Yasin, Lin Liu, Jianmin Wang, Wasif Afzal. Information and Software Technology
161 (2023) 107251. Received 18 Nov 2022, revised 9 Apr 2023, accepted 11 May 2023.*

**SCOPE WARNING — read before using this paper.** This is a **four-page tool/software note**, not a
study of search or screening automation. It contributes one Python web scraper for three preprint
servers. It reports **no accuracy figures, no precision/recall, no comparison against a gold
standard, no user study, and no time-saving measurement.** Its own evaluation is described as
"preliminary pilot evaluations" that show the method is "viable", with the explicit caveat that
"for external validity more evaluations are needed". Any claim in the reference document about
"accuracy of automated approaches" must be sourced elsewhere — from the tool-support papers already
in the corpus (Marshall & Brereton, Ribeiro, Yasin) — and not from here. What this paper *does*
uniquely supply is the concrete argument that **preprint servers are a distinct, poorly served
source stratum for secondary studies**, plus a working method of harvesting their metadata.

**Role in corpus:** The only paper here addressing the mechanics of getting bibliographic metadata
out of preprint servers — a source class that sits between white and grey literature and that the
major database-search guidance in the corpus does not cover.

### The problem it addresses

The paper's framing (Section 1): researchers invest a great deal of time searching literature for
SLRs and MLRs; the steps now include grey literature, preprints, and quality-assessed
non-peer-reviewed literature, with the purpose of **minimising publication bias**. Initial screening
takes time, and bibliographic information is only available online.

**Why preprints matter for secondary studies**, as the paper argues it:
- Computer science researchers were formerly reluctant to post preprints on free servers, preferring
  their own websites; that has changed in recent years.
- **60% of papers published in theoretical computer science were initially shared on arXiv**
  (attributed to Lin et al., *Scientometrics* 2020).
- CS researchers now routinely publish to a preprint server before formally submitting to journals
  or conferences.
- The COVID-19 period demonstrated the mechanism at scale: **approximately 125,000 papers were
  published across different platforms in the ten months after the early cases were detected, of
  which 30,000 were posted and shared on online servers as preprints** (attributed to Fraser et al.,
  *PLOS Biology* 2021).

The paper's definition, given in a footnote: **a preprint is the complete research article,
non-peer-reviewed, uploaded on a free server.**

**Three stated benefits of the free servers**, which are also the reasons the material is worth
harvesting:
1. They allow results to be shared online with an assigned DOI immediately, whereas **SE publishing
   venues typically take three months or more** for review.
2. The author claims authorship of the work by uploading.
3. The researcher gets feedback from the community, which can improve the paper and reveal other
   researchers' viewpoints.

**The gap claimed:** to the authors' knowledge, for arXiv, SocArXiv and SSRN there is **no tool that
can download the basic meta-information of studies** (title, abstract and other relevant
information).

**How the retrieved material should be appraised.** The paper does not propose a quality instrument
of its own; it points the reader at two existing ones for assessing non-peer-reviewed or grey
literature — the checklist of Yasin et al. (2022) on utilising non-quality-assessed literature in SE
research, and Garousi, Felderer & Mäntylä's (2019) guidelines for including grey literature and
conducting MLRs. It also cites Kitchenham, Madeyski & Budgen (2023) on how SE secondary studies
should include grey material, and Paez (2017) on grey literature as an important resource in
systematic reviews.

### The named process

**The algorithm (Section 2.1) — four steps:**
1. Take input (keyword/query) from the user to be searched.
2. Process the input and send a request to the website server.
3. Parse the server's response. **Beautiful Soup** is used for parsing.
4. Store the data in a `.csv`/`.xlsx` file.

**Input:** a search query, a database selection (arXiv, SSRN, SocArXiv), and a custom year.
**Output:** an Excel/CSV sheet of paper metadata — title, abstract, author and other bibliographic
fields — which the user then filters by title and abstract to decide which studies to read, shortlist
or exclude.

The paper defines scraping for its readers: extracting information from websites using automated
software tools, where a web crawler examines a page's HTML, parses it, and extracts relevant
information such as text, images and links.

**Deliverable structure (Section 2.2):**
- `Main.pyw` — runs all the scrapers for arXiv, SSRN and SocArXiv
- `Scraper.py` — defines the core classes and functions of all scrapers
- `Requirements.txt` — the required Python libraries
- `Loading.gif` — GUI feedback while scraping
- `Install.bat` — installs requirements without a command line
- `Start.bat` — runs the script without a command line
- `UIs/` — XML files holding the GUI code

**Two usage paths (Section 2.3):**
- *One-click method* — install Python (adding `python.exe` to PATH), run `install.bat`, then
  `start.bat`; a pop-up appears to select database, custom year and query.
- *VSCode method* — install VSCode, open the supplied folder, install the Python extension, run
  `main.pyw`; a menu pops up for the query and results download automatically.

### Automation and tooling

**What is automated:** retrieval of bibliographic metadata (title, abstract, author) from three
preprint servers for a given query and year, written straight to a spreadsheet for offline screening.

**What is explicitly not automated:** screening itself. The tool produces the sheet; the researcher
still filters by title and abstract to decide what to read, shortlist and exclude. The paper
positions the contribution as helping with the **(early) screening** stage only.

**Why manual copy-paste is not an adequate substitute** — the paper's three concrete arguments
(Section 2.4):
1. **Formatting.** Pasting whole search results into Excel produces data that is time-consuming to
   format into readable form.
2. **A hard result cap.** Copying in one go is **restricted to 50 studies for arXiv**.
3. **Coverage.** Using a script may retrieve literature that the database's own search bar cannot,
   because search scripts allow more advanced and targeted searches than a simple search-bar
   interface — specific keywords, phrases, **Boolean operators**, and other search parameters.

**What could not be automated — Google Scholar.** The plan was to include Google Scholar as a fourth
source, but initial results showed limitations: **the complete abstract information is unavailable
and there is no keyword information.** Google Scholar was therefore excluded from this version of
the study. This is a useful, concretely stated constraint on the most-used free source in the field.

**Verification performed.** The tool was tested with several queries — "grey literature", "testing
software", "python", "testing" — and the results were **cross-verified against the online search
results of the databases.** That is the entire evaluation: a qualitative cross-check, with no
reported counts, no precision/recall, and no timing data.

### Open science / reproducibility

The paper meets the Méndez et al. standard for artefact disclosure: **the source code and videos
showing how to use the tool are deposited on Mendeley Data with a DOI** —
`10.17632/bmwvmdnt5s.1`, "Retrieving arXiv, SocArXiv, and SSRN Metadata", V1 — and the authors
explicitly invite the research community to test, verify, use and extend the code.

### Caveats, traps and pitfalls

All stated by the authors.

1. **Evaluation is preliminary.** The results come from "preliminary pilot evaluations" showing only
   that the method is *viable*. **"For external validity more evaluations are needed"** — the
   authors' own words, repeated in both the abstract and Section 2.4.
2. **Windows only, so far.** Initial testing was performed on Windows; further testing was in
   progress at publication and promised for an extended version.
3. **The advanced search feature is still in testing.** It is shipped but not validated.
4. **Google Scholar is out of scope** because its results lack complete abstracts and keyword data.
5. **Coverage is three servers only** — arXiv, SSRN and SocArXiv. Nothing here covers institutional
   repositories, other preprint servers, or the wider grey literature.
6. **Scrapers are brittle by construction.** The paper does not raise this, but it follows directly
   from the method: the tool parses server HTML with Beautiful Soup, so any change to those sites'
   markup breaks retrieval silently. **[Inference, not stated in the paper — flag as such if used.]**
7. **Retrieved material is non-peer-reviewed by definition** and must be quality-assessed with a
   separate instrument before inclusion; the paper defers that to Yasin et al. (2022) and Garousi et
   al. (2019).

### Threats to validity framework

None presented. The paper names **external validity** once, as the dimension on which more
evaluation is required, and offers no other validity categories, no framework, and no mitigation
discussion.

### Empirical findings worth citing

- **60%** of papers published in theoretical computer science were initially shared on arXiv
  (attributed to Lin et al. 2020, *Scientometrics*).
- **~125,000** papers were published across platforms in the ten months following the first detected
  COVID-19 cases, of which **30,000** were posted as preprints on online servers (attributed to
  Fraser et al. 2021, *PLOS Biology*).
- **arXiv caps a single copy operation at 50 studies** — a hard, citable constraint on manual
  extraction.
- **SE publishing venues typically take three months or more** for review, which is the paper's
  stated timeliness argument for preprints.
- **Google Scholar does not expose complete abstracts or keyword information** to this scraping
  approach — the reason it was excluded.
- No accuracy, precision, recall, coverage, or time-saving figures are reported anywhere in the
  paper.

---

## Cross-cutting notes for the reference document

Points where these five papers reinforce or contradict each other, and where they touch the rest of
the corpus.

**On classification.** Wieringa's six research types were built for requirements engineering and for
*matching review criteria to paper class*, not for topic mapping and not for single-label
classification. Two of that scheme's own rules are routinely violated when it is reused in mapping
studies: papers may span categories, and each class carries its *own* criteria — so a mapping study
that reports a research-type distribution without applying per-class criteria is using the labels
without the instrument.

**On method labels being unreliable data.** Stol et al. establish empirically that a paper's stated
method may not be its actual method: 46 of 98 articles borrowed GT techniques while invoking the
name, and only 16 of 98 described their procedure well enough to judge. Zhang et al. find the same
pattern in a different place — 76 of 102 reviews claim grey-literature use without reporting sample
size, process, or effect. **Consequence for any secondary study: extracted method labels are claims,
not facts, and a quality-appraisal step must test the claim against the reported procedure.** Stol
et al. give the sharpest test available — a named list of practices whose absence disqualifies the
label.

**On "we followed the guidelines" as a justification.** Zhang et al. document reviews justifying
grey-literature inclusion by citing SLR guidelines that say nothing about grey literature; Stol et
al. document articles citing three mutually contradictory GT sources without noticing. Both are the
same failure: a citation standing in for a decision.

**On disclosure.** Méndez et al. supply the requirement (protocol, data, materials, scripts,
codebooks, coding schema and coding rules, deposited under a DOI at an archival repository, licensed
CC BY or the venue's non-exclusive default, never -NC). Zhang et al. and Fatima et al. both meet it —
protocols and study lists in a technical report, code and videos on Mendeley Data respectively. Stol
et al. published their article list as an online appendix. This is the standard the reference
document should require.

**On the reproducibility ceiling for qualitative work.** Méndez et al.'s position — that literal
reproducibility is the wrong standard for human-subject and qualitative work, and that transparency
plus **trustworthiness of the analysis process** is the achievable one — is the same standard Stol
et al. operationalise through their reporting checklist, and the same standard Charmaz's
constructivist evaluation criteria (credibility, originality, resonance, usefulness) encode.
Three independent routes to one conclusion.

**On preregistration.** Méndez et al. is the only paper here treating it seriously: registered
reports, in-principle acceptance, and publication regardless of results, as the defence against
publication bias, p-hacking and HARKing. For secondary studies the analogue is the **published,
reviewed protocol fixed before extraction begins** — Méndez et al.'s worked pipeline makes the
ordering constraint explicit, with the analysis plan registered before any data is analysed.

**On grey literature and preprints as a source stratum.** Zhang et al. supply the definitional
apparatus (Luxembourg definition, the three grey scales, the three abstract definitions along
accessibility / quality control / expertise) and the empirical picture of misuse. Fatima et al.
supply retrieval mechanics for the preprint sub-stratum specifically. Both point at the same
unresolved problem: no standardised quality assessment, and different criteria will be needed for
different grey levels.
