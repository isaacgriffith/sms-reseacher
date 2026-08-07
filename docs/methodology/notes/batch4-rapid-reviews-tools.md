# Batch 4 — Rapid Reviews, Grey/Practitioner Material, and Review Tooling

Source extractions: `scratchpad/txt/`. Papers: cartaxo_rapid_2020, kitchenham_how_2023,
wyrich_software_2026, marshall_tools_2013, marshall_tools_2014.

---

## cartaxo_2020 — Rapid Reviews in Software Engineering

Bruno Cartaxo, Gustavo Pinto, Sergio Soares. Book chapter (arXiv:2003.10006v1, 22 Mar 2020).

**Type:** Guideline + experience report (hybrid). The chapter explicitly says it "provide[s]
guidelines to help researchers and practitioners who want to conduct Rapid Reviews" and also
"present[s] the results and experiences of conducting two Rapid Reviews."

**Role in corpus:** This is *the* Rapid Review process definition for software engineering — the
only paper in the corpus that defines the RR phases, enumerates each permitted methodological
concession against its SLR counterpart, and specifies the Evidence Briefing as the
practitioner-facing report format with per-element design rules.

### Definition

> "Rapid Reviews are practice-oriented secondary studies (Watt et al. 2008, Haby et al. 2016,
> Polisena et al. 2015, Tricco et al. 2017). The main goal of a RR is to provide evidence to
> support decision-making towards the solution, or at least attenuation, of issues practitioners
> face in practice. To support this goal and to meet practice time constraints, RRs have to
> deliver evidence in shorter time frames, when compared to SRs, which often take months to
> years (Tricco et al. 2015). To make RRs compliant with such characteristics, some steps of SRs
> are deliberately omitted or simplified."

Footnote 1 defines the comparator: "By SRs we mean the more methodologically rigorous secondary
studies, like: meta-analyzes, the traditional systematic literature reviews, and systematic
mapping studies (Kitchenham & Charters 2007)".

#### The three core aspects every RR shares (Sect. 2.1) — verbatim headers plus text

1. **"Rapid Reviews should be performed in close collaboration with practitioners, bounded to
   practical problems, and conducted within practitioners context:"**
   > "The argument to conduct lightweight secondary studies like RRs holds only in scenarios
   > where time and costs are hard constraints. This kind of scenario is typically observed in
   > the practice of many fields. Therefore, RRs are only conceived bounded to practical
   > problems, and conducted within their practical contexts. Thus, practitioners should be
   > willing to devote part of their busy schedule in order to participate on RRs, although the
   > level of participation can vary. RRs that are either conducted without practitioners'
   > collaboration nor related to a problem that emerged from a practical context are considered
   > deviations, and then, should be avoided by the software engineering community."

2. **"Rapid Reviews are intend to reduce costs and time of heavyweight methods:"**
   > "To better fit in the practitioners' agenda, RRs should be conducted and reported in a
   > timely manner. Many strategies have been applied to RRs in health-care related fields to
   > reduce costs and time, such as: limiting search strategy by date of publication and/or
   > search source; using just one person to screen studies; not conducting quality appraisal of
   > primary studies; presenting results with no formal synthesis, among others (Tricco et al.
   > 2016, 2015)."

3. **"Rapid Reviews results should be reported through mediums appealing to practitioners:"**
   Alternative mediums cited (as prior work, not this paper's contribution): the *Contextual
   Summaries* of Young et al. (2014) — limits the report to a one-page document; the *Briefings*
   of Chambers & Wilson (2012) — summarize main findings of a secondary study in one section;
   the *Evidence Summaries* of Khangura et al. (2012) — an informative box separated from the
   main text highlighting audience and nature of the report. The authors "particularly advocate
   in favor of the Evidence Briefings (Sect. 4.3.1)".

Boundary statement (verbatim):
> "It is important to note that RRs are neither (1) ad-hoc literature reviews, nor (2) an excuse
> for absence of scientific rigour. RRs must be systematic, by means of following a well-defined
> protocol. In addition, all the methodological concessions made to a RR must be documented in
> its protocol. On the RRs report, there must also be a disclaimer about potential
> methodological limitations (although the details can go on the protocol only, aiming to make
> the report as concise as possible)."

### Process steps or stages defined

Section 4, "The Rapid Review Process". Three main phases (Fig. 1): **planning, performing,
reporting**. "These phases are similar to the ones of a SR, as described by Kitchenham &
Charters (2007). Each phase comprises various specific steps, and that is where the differences
between RRs and SRs become evident. While the latter adopts strategies aiming to reduce any type
of research bias and to guarantee evidence quality, the former aims to deliver scientific
evidence in a timely manner to support practitioners decision-making."

#### PHASE 1 — Planning a Rapid Review (4.1)

> "The planning phase of a RR comprehends the creation of a protocol to define all the decisions
> and procedures demanded to conduct the RR. The protocol must also make explicit the practical
> problem it intends to provide evidence for, as well as the roles of each stakeholder aiming to
> guarantee practitioners active participation."

Steps, in the paper's order:

**4.1.1 Demand for a Rapid Review.** "The demand for a RR can emerge from different sources
under different contexts. Some possible arrangements we envision are:"
- **"Practitioners ask for a Rapid Review:** A decision-maker (i.e. practitioner) contacts a
  researcher or research institution asking for a RR aiming to make decisions based on
  evidence."
- **"Researcher aligns her/his research agenda based on a practical problem:** A researcher
  contacts a software company (or an open source team) facing problems related to her/his
  research agenda. A researcher then proposes a RR to both, provide evidence that practitioners
  need, and to bound her/his research on a practical problem."
- **"Researcher prospects a research agenda based on a practical problem:** A researcher
  contacts a software company (or an open source team) aiming to prospect practical problems to
  focus her/his research on. In this case, the RR has initially no predetermined focus. To
  narrow it down, the researcher could leverage interviews with practitioners to grasp the
  problems they are facing, and then decide which one to attack. This is how we conducted the
  two RRs presented in Sect. 3."

**4.1.2 Defining the Problem.**
> "Close collaboration with practitioners is crucial to define the problem that will drive a RR.
> Since sometimes the problem is not already well-defined (or perhaps not even the practitioner
> is fully aware of the main problem s/he is facing), researchers can use qualitative research
> methods such as interviews or focus group to better understand the context and the (eventually
> hidden) problems (Cartaxo et al. 2018a). Depending on how clear is the problem in the
> practitioners' mind, the interview could be more exploratory (e.g., to understand the whole
> challenges and needs), more objective (e.g., to understand missing details), or even skipped
> (e.g., if the problem is very well-defined). One important point to bear in mind when
> interviewing practitioners to define RRs' problem is that this may be an interactive process.
> Sometimes you identify a practical problem but there are no studies approaching such problem,
> so a RR will not be viable, and you may need to find another problem."

**4.1.3 Defining the Research Questions.**
> "Research questions in RRs are as important as in SRs (Kitchenham & Charters 2007). Once they
> are defined, all effort is towards answering them. However, to have useful answers, one has to
> ask meaningful questions. In RRs, answers are considered useful when they help practitioners
> to solve or at least attenuate their practical problem. Consequently, questions are considered
> meaningful only when they lead to such answers."

Rule (paper's own boxed statement, verbatim):
> "**Research questions in Rapid Reviews should be defined in close collaboration with
> practitioners:** Questions aiming to identify research gaps or to provide more general
> insights to the research community should be avoided, left to SRs. RRs should provide answers
> bounded to the practical context they are inserted into. In other words, they naturally have a
> narrower character."

> "However, in our experience, exploratory questions aiming to identify strategies to deal with
> a particular problem are the cornerstone of RRs (Cartaxo et al. 2018a) since the most important
> thing to practitioners under time constraints is to discovery strategies, supported by
> evidence, to solve their problems (Yourdon 1995)."

Worked RQ templates from the two example RRs:
- Customer Collaboration RR: "What are the strategies to improve customer collaboration in
  software development practice?" / "What are their effectiveness?" — plus two extra: "What are
  the benefits of customer collaboration in software development practice?" / "What are the
  problems caused by low customer collaboration in the software development practice?"
  (justification: "the findings were used by the development team to convince their customers
  about the importance of a better collaboration").
- Team Motivation RR: "What are the strategies to improve software development teams
  motivation?" / "What are their effectiveness?" — the two extra questions "were not necessary
  ... since the problem was internal to the company, and the stakeholders already agreed with
  the importance to improve team motivation. They just did not know how they can do it
  effectively."

**4.1.4 Defining the Stakeholders Roles.**
> "A RR is a joint initiative between researchers and practitioners. Thus, active participation
> of both sides are not only important, but (as we see it) mandatory. The researchers role is to
> guarantee the methodological consistency and transparency, while the practitioners role is to
> make sure that the research is bounded to an actual practical problem, so the evidence will be
> useful."

> "Considering the extremes, it is possible for researchers to perform all activities related to
> the RR (e.g., defining the protocol, selecting primary studies, extracting data, synthesizing
> evidence, and reporting the results) as long as practitioners are involved in the entire
> process, validating each decision and ensuring the RR is bounded to their practical problem.
> We could also perceive, nevertheless, that practitioners could perform all RR's activities, as
> long as researchers are involved, in particular, validating each methodological decision. Any
> level of participation between these two extremes are also possible and encouraged. However,
> the effort of each stakeholder will be defined taking into account the time constraints and
> resources limitations in each specific situation."

**4.1.5 Creating the Protocol.**
> "The protocol of a RR has the same goal as the protocol of a SR: to specify all the
> methodological steps that undertake the review. The protocol itself is one of the most
> important elements that makes both RRs and SRs systematic. In this sense, it is important to
> highlight that RRs are not synonymous of ad-hoc literature reviews, but rather systematic. As
> a consequence, a RR demands a well-documented protocol."

> "A major difference between RRs and SRs protocols, nevertheless, is the natural inclination of
> the former to suffer changes throughout the review process. These changes might happen due to
> the flexible process that RRs allow. However, changes made after the protocol definition must
> be documented and justified transparently (Tricco et al. 2017)."

Protocol components (same as Kitchenham & Charters 2007): "research questions, search strategy,
inclusion/exclusion criteria, selection procedure, extraction procedure, synthesis procedure,
reporting, among others."

#### PHASE 2 — Performing a Rapid Review (4.2)

Framing (verbatim): "In this section we present some strategies that may be used to reduce time
and cost of performing a RR. For each step, we present some suggestions on how to perform the
step. However, one does not have to embrace all strategies, on the contrary, the researcher has
to analyze the context and limitations where a RR is being conducted and define which strategies
better conciliate given trade-offs. For instance, a RR may use more than one search sources to
identify primary studies if ensuring wide coverage is critical, but skip the quality appraisal.
While other RR may use just one search source and conduct a rigorous quality appraisal, if the
reliability on the evidence is critical."

Governing rule (paper's own boxed statement, verbatim):
> "**Transparency is the golden standard in Rapid Reviews:** Regardless the strategies employed
> to reduce cost and/or time to conduct a RR, limitations and threats to validity must be
> reported on the protocol. Practitioners may and are willing to consume evidence based on less
> rigorous methods like RRs, as long as they are aware of the limitations and threats to
> validity (Cartaxo et al. 2018a)."

**4.2.1 Search Strategy.** SRs "usually employ multiple search strategies to guarantee
exhaustive coverage such as, using multiple search engines, manual search on conference
proceedings and journal issues, as well as forward and backward snowballing approaches. Adopting
all these strategies simultaneously can be extremely resource consuming. RR, on the other hand,
may choose to focus on a single search strategy. For instance, instead of using several search
engines, RRs may focus on a single one, more likely Scopus or Google Scholar. These search
engines cover a wide spectrum of research papers, and usually index papers from the major
digital libraries. Complementing the results of the search engine with a snowballing approach
has also shown to be a viable option (Badampudi et al. 2015)."

Enumerated effort-reducing approaches (verbatim list):
1. "Limiting the search by date;"
2. "Restricting the language in which the paper is written;"
3. "Focusing on a given geographical area, or;"
4. "Limiting the primary studies according to their research method (e.g., controlled
   experiments only, or case studies only) (Tricco et al. 2017)."

> "It is important to note that these approaches may lead to relevant studies being not
> included, then reducing RR's potential coverage. If one of these strategies are adopted,
> threats to validity must be transparently reported."

Both example RRs "used one search source only: the Scopus search engine."

**4.2.2 Selection Procedure.** Two goals of restrictive criteria: "to reduce the amount of
studies to screen and to provide evidence that better fit practitioners needs."

Worked exclusion criteria from the Team Motivation RR ("conducted in a small private company
with collocated teams"), verbatim:
- "The study must not be related to large companies;"
- "The study must not be related to distributed teams;"
- "The study must not be related crowd source software development;"
- "The study must not be related to open source software development;"

> "Defining restrictive inclusion/exclusion criteria may reduce the time and effort to conduct a
> RR. However, this procedure does not necessarily incur in threats to validity. In fact, this
> may be considered a good practice, when the restrictions are made aiming to provide evidence
> only from primary studies conducted in contexts similar to the one the RR is being conducted.
> Highly contextualized studies are long considered one of the best ways to have impact in
> practice (Dybå et al. 2012, Cartaxo et al. 2015)."

Reviewer count: "SRs usually require independent screening of studies by at least two reviewers
(Kitchenham & Charters 2007, Tricco et al. 2017), which is very resource intensive. RRs, on the
other hand, may have a selection procedure conducted by a single reviewer. Another option is to
have a second reviewer just to pass through a reduced sample of studies. Such strategies may
obviously introduce selection bias and must be reported accordingly."

**Three-substep screening (a Cartaxo-specific procedural innovation):**
> "Usually, SRs splits the selection procedure in two substeps. In the first, reviewers screen
> primary studies' titles and abstracts, and in the second, the entire papers content. To
> abbreviate this process, one may split the selection procedure in three substeps, instead of
> two. The first substep can be dedicated to screening primary studies' titles only. This might
> accelerate the exclusion of papers that are clearly out of scope since it prevent one to read
> papers abstracts. On the other side, it may provoke false negatives. The second substep would
> select primary studies based on abstract only, and the third sub-step based on the entire
> content."

Practitioner reaction to that trade-off (verbatim quote from a Customer Collaboration RR
participant):
> "Sometimes we search for solutions in just one source [...] Then we do it exactly as
> recommended by that source but it may not work for us. When we do it like this [the RR], we
> can have more possibilities [the strategies identified by the RR], even considering it was
> conducted faster [the RR compared to SRs], and maybe many things [papers] could be lost just
> because of the title [the first round of selection procedure, which we analyzed only the
> titles of the papers], because someone put a bad title. That is ok, who cares?"

**4.2.3 Quality Appraisal.** Three escalating options, in the paper's order:
- Skip entirely: "In a more extreme view, RR researchers can entirely skip this step, but threats
  to validity associated with this decision must be transparently reported. Both the RRs we
  presented in Sect. 3, adopted this strategy."
- Venue proxy: "Another less radical strategy would be to focus only on studies published on
  conferences and/or journals that employ a rigorous review process. This may increase the
  chances of selecting high quality evidence with a low effort (e.g., no need to analyse the
  evidence quality of each and all papers). Although this approach can also have limitations
  (e.g., a potentially relevant study could have published on a less prestigious venue or on
  arXiv), at least we know that the primary studies being included already passed through a
  rigorous sieve."
- Reduced-staffing appraisal: "If evidence quality is critical in the context where the RR is
  being conducted, a strategy that may reduce the time and effort is to have quality appraisal
  carried out by a single reviewer or using pairs to appraise just a sample of papers. In
  contrary to SRs, where quality appraisal is recommended to be conducted fully in pairs."

**4.2.4 Extraction Procedure.**
> "The data extraction procedure can be conducted by a single reviewer in RRs, as long as the
> inherent biases are transparently reported. Both the RRs we presented in Sect. 3, adopted this
> strategy. Moreover, in SRs, when data is missing on the selected studies, it is usually
> recommended to contact the authors. Researchers who conducted RRs in medicine very
> infrequently indeed contacted primary studies' authors (Tricco et al. 2017). That can be a
> viable strategy: studies with missing data should probably be excluded from the RR, and their
> exclusion must be reported. RRs consumers (a.k.a practitioners) can reach those studies later
> if they wish to."

**4.2.5 Synthesis Procedure.**
> "Knowledge synthesis is probably one of the most important steps of any secondary study, but
> at the same time one of the most time consuming activities. However, a tertiary study revealed
> that as many as half of the SRs analyzed in software engineering do not present any kind of
> formal knowledge synthesis procedure (Cruzes & Dybå 2011b)."

> "A possible strategy to reduce time and effort synthesising evidence in RRs is using
> lightweight methods, like Narrative Synthesis (Cruzes & Dybå 2011b, Tricco et al. 2017), in
> contrast to the more rigorous and time/effort consuming ones, like Meta-Analysis (Lipsey &
> Wilson 2001) or Grounded Theory (Stol et al. 2016) methods alike. This decision brings an
> obvious limitation and must be reported, so practitioners consuming RRs evidence can make
> informed decision."

Mandatory conclusions/recommendations:
> "Conclusions, recommendations, and implications are particularly important in RRs since they
> can guide practitioners to adopt the synthesized knowledge. In medicine, they encourage
> researchers to dedicate time to make her/his conclusions and recommendations to practitioners,
> and avoid presenting a report with findings only (Tricco et al. 2017)."

Practitioner quote motivating this (Team Motivation RR):
> "since it [the RR] was focused on our problem, maybe if there was something saying which one
> [strategy identified with the RR] you recommend [...] this is what is missing [...] maybe it is
> missing a conclusion, the researcher's comments."

> "In addition, one should keep in mind that those conclusions, recommendations, and implications
> should be strongly bounded to RRs context, in opposition to the ones draw with SRs that usually
> aims to reach a wider audience and scope (Tricco et al. 2017)."

#### PHASE 3 — Reporting a Rapid Review (4.3)

> "Reporting and disseminating knowledge produced with RRs are as important as conducting the RR
> itself. SRs are usually conducted in academic environment and thus the report is usually
> focused on that audience. That means SRs are commonly reported in scientific paper format and
> diffused through academic journals and conferences."

> "RRs, however, target software practitioners. Therefore, one should consider that not all
> information that is crucial to researchers is also relevant to practitioners (e.g., research
> method, background, related work, etc). As a consequence, RRs must be reported in a more
> straightforward way, focusing on results and recommendations, so practitioners can easily
> consume the information to support their decision making."

**4.3.2 Dissemination of Rapid Reviews Results.**
> "Not all RRs are disseminated beyond the practitioners scope due to sensitive information
> belonging to the software company involved. However, if this is not the case, we recommend RR
> researchers to post the RRs report (e.g., Evidence Briefing) online on the research
> institution's or the company's website. Sharing the report on social networks such as Twitter
> or ResearchGate can also increase the impact of the reviews."

### How this method RELAXES or DIFFERS from a full SLR

**Table 1 reproduced in full** ("Comparison of Rapid Reviews with Systematic Reviews
methodological characteristics"). Note stated in text: "The RRs characteristics are based on
many medicine studies and guidelines (Tricco et al. 2017, Khangura et al. 2012, Abou-Setta et al.
2016, Taylor-Phillips et al. 2017), while the SRs characteristics are based on Kitchenham's
software engineering guidelines (Kitchenham & Charters 2007, Cruzes & Dyba 2011a, Santos & d.
Silva 2013)."

| CHARACTERISTIC | RAPID REVIEWS | SYSTEMATIC REVIEWS |
|---|---|---|
| Problem | Bounded to a practical problem, and conducted within a practical context. | Can emerge from academic and practical contexts (Kitchenham & Charters 2007). However, SRs focusing on problems emerged from practice are the exception (Santos & d. Silva 2013). |
| Research Questions | Lead to answers that helps solving or at least attenuating the practitioners problem. Exploratory questions aiming to identify which are the strategies and their effectiveness to deal with practitioners problem are one of the gold standards. | SRs admit questions aiming to support practitioners decision-making, but also studies that are primarily of interest to researchers, with no practice oriented questions (Kitchenham & Charters 2007). |
| Protocol | Must have a document formalizing the protocol. | Must have a document formalizing the protocol. |
| Stakeholders Roles | Conducted in close collaboration with practitioners, sometimes even having practitioners responsible for executing some of the steps. | Despite practitioners participation is possible, researchers usually conduct the entire process. |
| Time Frame | Days or Weeks | Months or Years |
| Search Strategy | - May use few or just one search source (e.g., Scopus). <br> - May limit search by publication year, language, and study design. | - Multiple sources to search for primary studies are recommended. <br> - May also limit search by publication year, language, and study design, although more comprehensive search is recommended. |
| Selection Procedure | - Can be conducted by a single person. <br> - The inclusions/exclusion criteria can be more restrictive aiming to focus on primary studies conducted in contexts similar to the one motivating the RR. (e.g., studies with small/medium/large companies, with companies in countries under specific laws, with open source projects only, etc) (Tricco et al. 2017) | - Must be conducted in pairs to avoid selection bias. <br> - Usually is less restrictive regarding specificities of primary studies context, specially when it is a mapping study, broader in scope. |
| Quality Appraisal | Conducted by a single person, or not conducted at all (Tricco et al. 2017). | Conducted in pairs to avoid threats to validity due to low primary studies quality. |
| Extraction Procedure | Usually conducted by a single person to reduce time and effort. | Conducted in pairs to avoid extraction bias. |
| Synthesis Procedure | Narrative summaries are the most common way to synthesize evidence (Tricco et al. 2015). | More systematic methods should be applied (e.g., meta-analysis, meta-ethnography, thematic analysis, etc), although it is not always the case (Cruzes & Dyba 2011a). |
| Report | Alternative mediums that better fit practitioners needs (e.g., Evidence Briefings). | Traditional research paper format. |

Derived "relaxation ledger" (activity → what changes → stated justification), drawn from §4.2:

| SLR activity | RR relaxation | Justification the paper gives |
|---|---|---|
| Search strategy | Single search source (Scopus/Google Scholar), optionally + snowballing | Multiple engines + manual + snowballing "extremely resource consuming"; Scopus/GS "cover a wide spectrum ... and usually index papers from the major digital libraries" |
| Search scope | Limit by date, language, geography, or research method | Effort reduction; must be reported as a threat |
| Selection screening | 3 substeps (title-only → abstract → full text) rather than 2 | "accelerate the exclusion of papers that are clearly out of scope"; acknowledged cost: "it may provoke false negatives" |
| Selection staffing | Single reviewer, or second reviewer over a sample only | Pairs "very resource intensive"; concession "may obviously introduce selection bias and must be reported accordingly" |
| Inclusion/exclusion criteria | Deliberately narrower, matched to the practitioner's context | Twofold: fewer studies to screen **and** better-fitting evidence. Explicitly NOT a threat: "this may be considered a good practice ... Highly contextualized studies are long considered one of the best ways to have impact in practice" |
| Quality appraisal | Skipped entirely, or venue-proxied, or single-reviewer / sampled pairs | Time and effort; skipping requires transparent threat reporting |
| Data extraction | Single reviewer | Time and effort; "as long as the inherent biases are transparently reported" |
| Contacting primary-study authors | Not done; studies with missing data excluded and the exclusion reported | Medicine RR practice; "RRs consumers ... can reach those studies later if they wish to" |
| Synthesis | Narrative Synthesis instead of meta-analysis / grounded theory | Time/effort; "brings an obvious limitation and must be reported" |
| Report format | Evidence Briefing (one page), not a research paper | Practitioners do not need method/background/related work |
| Protocol | Still mandatory, but expected to change mid-review | RR process is flexible; changes "must be documented and justified transparently" |

### Caveats, traps and pitfalls (verbatim)

- Not a substitute: "**Rapid Reviews should not be considered as replacements for Systematic
  Reviews:** We believe RRs should be understood as a complementary scientific product. More
  concretely, while SRs are important to curate in-depth knowledge, RRs are important to easily
  and quickly transfer established knowledge to practice."
- When a RR is *not* appropriate — no practitioner and no practical problem: "RRs that are
  either conducted without practitioners' collaboration nor related to a problem that emerged
  from a practical context are considered deviations, and then, should be avoided by the
  software engineering community."
- Time/cost constraints must be real: "The argument to conduct lightweight secondary studies
  like RRs holds only in scenarios where time and costs are hard constraints."
- Not ad-hoc: "RRs are neither (1) ad-hoc literature reviews, nor (2) an excuse for absence of
  scientific rigour."
- RR may be infeasible for a given problem: "Sometimes you identify a practical problem but
  there are no studies approaching such problem, so a RR will not be viable, and you may need to
  find another problem."
- Coverage loss from search restrictions: "these approaches may lead to relevant studies being
  not included, then reducing RR's potential coverage. If one of these strategies are adopted,
  threats to validity must be transparently reported."
- False negatives from title-only screening: "On the other side, it may provoke false negatives."
- Selection bias from single-reviewer screening: "Such strategies may obviously introduce
  selection bias and must be reported accordingly."
- Venue-proxy quality appraisal is lossy: "a potentially relevant study could have published on
  a less prestigious venue or on arXiv".
- Do not over-generalise RR conclusions: "those conclusions, recommendations, and implications
  should be strongly bounded to RRs context, in opposition to the ones draw with SRs that
  usually aims to reach a wider audience and scope".
- Honest overall caveat: "Even looking for all the good results, one to be fair has to highlight
  that RRs are not always a bed of roses. RRs have their limitations, and this must be considered
  carefully. They are certainly not silver bullets nor they are substituting Systematic Reviews."
- **Grey literature should be excluded from RRs** (this paper's own recommendation, in tension
  with MLR advocates): "our experience suggests that researchers should focus only on peer
  reviewed literature when conducting a RR. This is particularly due to the fact that RRs have
  already several limitations and threats to validity. We believe that adding grey literature to
  this equation could weaken the quality of the review produced, at least in the eyes of an
  unconvinced researcher. Obviously, this is an hypothesis that could be tested in follow up
  studies."
- Briefing legibility trap observed empirically: practitioners "found that some findings were
  not clear in the printed version of the Evidence Briefing — although they became clearer after
  discussing with researchers during the workshop".

### Checklists, reporting guidance, templates, evaluation criteria

#### Evidence Briefings — structure and design rules (Sect. 4.3.1)

> "Evidence Briefings are one-page documents reporting the main findings of RRs (Cartaxo et al.
> 2016). A template, as well as examples of such documents can be found online
> [http://cin.ufpe.br/eseg/briefings]. The Evidence Briefings template was defined based on the
> best practices observed in medicine as well as on Information Design (Tondreau 2011) and
> Gestalt Theory (Lupton & Phillips 2015) principles."

Six numbered parts (Fig. 2), reproduced verbatim:

1. "The **title** of an Evidence Briefing should be as concise as possible. Usually, one or two
   lines titles. Titles with more than two lines should be avoided since they might reduce
   document space to report RRs' findings."
2. "To fill the Evidence Briefing's **summary**, we suggest researchers to adopt the following
   structure: `This briefing reports scientific evidence on <RESEARCH GOAL>`. The summary should
   span few lines. Following is an example of Evidence Briefing's summary: *'This briefing
   reports scientific evidence on the challenges involved in using Scrum for global software
   development (GSD) projects, and strategies available to deal with them.'*"
3. "The **findings** section is the most important one. It should list the main findings of the
   RR. When writing the findings, we recommend to use one finding per paragraph. Bullets to
   highlight important points as well as charts, figures, and tables are welcome since they make
   the findings even easier to read. Findings should be short sentences, straight to the point.
   The findings section should not have information about the research method. The idea of the
   Evidence Briefing is to quickly communicate the main findings of a RR to practitioners. If
   they have interest they can refer to the complementary material reference shown in the item 5."
4. "The **box at the right side** of the Evidence Briefing should be filled with information
   about the Evidence Briefing's target audience, clarifications about what information is
   included, and what is not included in the Evidence Briefing. The template has a complete set
   of suggestions to structure information at the right box."
5. "The reference to **complementary material** should be placed at the bottom of the Evidence
   Briefing. It may be a link to a webpage containing at least the following documents/
   information: the RR protocol document and a list of references to the primary studies
   included in the RR."
6. "**Logos** of universities, software companies, and any other institutions involved in the RR
   initiative should be placed at the very top of the Evidence Briefing document. This publicizes
   the institutions producing Evidence Briefings, and might make practitioners search for more RRs
   in the institutions websites."

Empirical warrant for the format: "as observed in an empirical evaluation, both researchers and
practitioners are positive about using Evidence Briefings as medium to transfer scientific
knowledge to software engineering practice (Cartaxo et al. 2016)."

#### Publication guidance (Sect. 5.2), verbatim boxed rule

> "**Rapid Reviews can and should also be published in academic peer reviewed venues:** One may
> argue that a RR will probably not constitute enough contribution to deserve a rigorous
> scientific publication. However, one should note that RRs are usually inserted into broader
> knowledge/technology transfer initiatives (Cartaxo et al. 2018b), and such initiatives are
> usually very enriching and welcomed in scientific venues. The paper may report not only the RR
> protocol and results, but also the perceptions of practitioners participating on the entire RR
> initiative."

Also: "Since RRs are commonly reported in non-scientific paper format (i.e. Evidence Briefings),
they are usually internally reviewed, but not peer reviewed (Tricco et al. 2017)."

### Threats to validity framework

The chapter does not define a named threats-to-validity taxonomy. Instead it prescribes a
*disclosure regime*: every methodological concession is itself a threat that must be recorded.
The operative rules:

- "all the methodological concessions made to a RR must be documented in its protocol. On the
  RRs report, there must also be a disclaimer about potential methodological limitations
  (although the details can go on the protocol only, aiming to make the report as concise as
  possible)."
- "Transparency is the golden standard in Rapid Reviews ... limitations and threats to validity
  must be reported on the protocol."
- Concession-specific threats named in the text: reduced coverage (search restriction),
  false negatives (title-only screening), selection bias (single-reviewer selection), extraction
  bias (single-reviewer extraction), low-quality primary studies (skipped appraisal), limited
  synthesis rigour (narrative synthesis), missing-data exclusions.
- Explicitly *not* a threat: narrowing inclusion criteria to the practitioner's context — "this
  procedure does not necessarily incur in threats to validity. In fact, this may be considered a
  good practice."

### Data extraction and analysis techniques

- Extraction: single reviewer permitted. No extraction form template is given in this chapter.
- Missing data: exclude the study rather than contact authors; record the exclusion.
- Synthesis: **Narrative Synthesis** is the recommended lightweight default; "Narrative summaries
  are the most common way to synthesize evidence (Tricco et al. 2015)"; 78% of RRs in medicine
  "present results as a narrative summary reported in mediums that better fit practitioners'
  needs" (Tricco et al. 2015). Heavier alternatives named but deprecated for RRs: meta-analysis
  (Lipsey & Wilson 2001), meta-ethnography, grounded theory (Stol et al. 2016), qualitative
  metasummary, thematic analysis.
- Analysis must terminate in explicit conclusions, recommendations and implications addressed to
  the practitioner — a findings-only report is called out as a defect.

### Stakeholder / practitioner involvement

- Practitioner participation is "not only important, but (as we see it) mandatory."
- Role split: "The researchers role is to guarantee the methodological consistency and
  transparency, while the practitioners role is to make sure that the research is bounded to an
  actual practical problem, so the evidence will be useful."
- Participation is a spectrum between two extremes (researchers do everything with practitioner
  validation ↔ practitioners do everything with researcher validation); both extremes and all
  intermediate arrangements are legitimate.
- In both reported RRs the arrangement was near the researcher-executed extreme, but "the
  practitioners were aware of every single step made, validating and making suggestions to it.
  This alignment ... is crucial to researchers (who conduct the review) do not lose focus, which
  could lead to, say, research questions that, although interesting from an academic perspective,
  are not related to a practical problem."
- Expected trajectory: "Since RRs and even SRs are not well-known in practice (Cartaxo et al.
  2017), we believe this kind of arrangement (where researchers perform most of the RRs tasks)
  will happen more frequently, at least in the beginning."
- Practitioners shape: the problem, the research questions, inclusion/exclusion criteria (bounded
  to their company size / team distribution / project type), and validate every protocol decision.
- Delivery is not just the document: both example RRs ended in a **workshop** to present and
  discuss findings, followed by post-hoc interviews and (in one case) a two-month follow-up.

### Empirical findings worth citing

From the two SE Rapid Reviews the authors conducted (Sect. 3):

| RR | Setting | Primary studies included | Effort | Outcome |
|---|---|---|---|---|
| Improving Customer Collaboration | Innovation institute; project late, "emails requesting clarification about requirements take one or two weeks for customer to reply" | 17 | **six days** of one full-time researcher experienced in secondary studies — spanning the first problem-identification interview through the closing workshop | Practitioners adopted Story Owner, Change Priority, and Risk Assessment Up Front into daily habits (confirmed at 2-month follow-up) |
| Improving Team Motivation | Software company making educational products, Recife, Brazil; small private company, collocated teams | 35 | **eight days** of one full-time researcher experienced in secondary studies | Reported improvements in team confidence; reliability on RR findings; willingness to embrace RRs in their own process |

Perceptions reported: benefits included "the novelty of the approach, the applicability to their
problem, the reliability of the content"; the RR "fostered the learning of new concepts."
Shortcoming: "some findings were not clear in the printed version of the Evidence Briefing."

Key attitudinal finding: "This particular finding revealed that practitioners are willing to take
the risks of using less rigorous methods, such as RRs, in exchange for evidence delivered in
short time frames."

Findings cited from medicine (not this paper's own data — attribution matters):
- "a study observed that RRs saved approximately $ 3 millions when implemented in a hospital
  (McGregor & Brophy 2005)."
- "a survey exploring the use of 15 RRs revealed that 67% were used as reference material and
  53% were used to, in fact, support decision-making in practice (Hailey 2009)."
- Lawani et al. (2017): "RRs enabled the development of clinical tools more rapidly than with SRs."
- Tricco et al. (2015): mapped 100 RRs published 1997–2013; 78% present results as narrative
  summaries in practitioner-fitting mediums.
- RR vs SR agreement: a scoping review found nine comparison studies, concluding "their results
  are both generally similar (Abou-Setta et al. 2016)"; Corabian & Harstall (2002) compared six
  RRs with peer-reviewed SRs — "The conclusions differed only in one case"; Taylor-Phillips et al.
  (2017) — "both RR and SR identified the same set of papers". Counter-evidence: Van de Velde
  et al. (2011) — "conflicting results were observed."
- Context motivating RRs in SE: "lack of connection with industry" is the 6th of 37 barriers to
  conducting secondary studies (Hassler et al. 2014); of 44 authors of 120 secondary studies
  surveyed, "only six of them affirmed their studies had direct impact on industrial practice"
  (Santos & d. Silva 2013); "only 32 out of 120 secondary studies provide guidelines to
  practitioners."

#### Researcher viewpoints on RRs — Q-Methodology typology (Sect. 5.1)

From Cartaxo et al. (2019), a study with **37 software engineering researchers** using
Q-Methodology; four viewpoints (verbatim descriptions condensed to the paper's own wording):

- **Unconvinced:** "agree the most that further research comparing the methods and results of RRs
  and SRs is required before they decide how they feel about RRs ... They think a well-conducted
  RR may produce better evidence than a poorly conducted SRs, but on the other hand, they have
  more confidence in evidence produced with a SR than in evidence produced with a RR."
- **Enthusiastic:** "generally favorable about RRs, and believe RRs can provide reasonable
  evidence to practitioners, if minimum standards to conduct and report RRs are established. They
  also strongly agree that a well-conducted RR may produce better evidence than a poorly conducted
  SR."
- **Picky:** "very skeptical about RRs, as well as concerned about the quality of primary studies
  included in RRs and how the results are reported. This negative perception can be explained by a
  strong belief ... that knowledge users (practitioners) do not fully understand the implications
  of RR methodological concessions. Researchers with this viewpoint also put little faith in RRs
  validity."
- **Pragmatic:** "pragmatically focus on variety of contextual information to decide if RRs are
  the best fit to support decision-making. They also believe practitioners are able to understand
  the impacts of flexible research methods adopted by RRs. Still, they believe rigid standards in
  RRs could reduce their usefulness to practitioners."

Consensus across viewpoints: "both RRs and SRs can be conducted very well or very poorly, and
that time needed to conduct an evidence synthesis study is not related to its quality." Main
concerns: "the need for more evidence about the effectiveness of RRs, the importance to determine
minimum standards, the relevance of quality assessment to include primary studies, and the
emphasis on transparency in RRs."

### RR vs MLR (boundary definition, Sect. 6)

> "there is a fundamental difference between these two approaches. On the one hand, RRs aims to
> provide knowledge based on scientific evidence from peer-reviewed and rigorous primary studies
> only, as well as deliver evidence in a timely manner. On the other hand, MLRs applies
> systematic methods to synthesize not only primary studies, but also gray literature. Moreover,
> MLRs do not necessarily emerge from a practical problem nor is necessarily concerned about
> delivering evidence in a timely manner to practitioner. Thus, RRs and MLRs are different
> approaches, although both can potentially contribute to reduce the gap between software
> engineering research and practice."

---

## kitchenham_2023 — How Should Software Engineering Secondary Studies Include Grey Material?

Barbara Kitchenham, Lech Madeyski, David Budgen. IEEE TSE 49(2), Feb 2023, pp. 872–882.

**Type:** Methodological position / guideline-clarification paper (the authors describe it as
reporting "our original views on the topic of grey literature reviews and multivocal reviews";
there is no new empirical study beyond a small link-rot check).

**Role in corpus:** Fixes the *admissibility boundary* for secondary studies — it is the only
paper that says precisely which non-peer-reviewed material may enter an SLR as a primary study
(Prague-definition grey literature) and which may not (social media posts, personal
communications), and grounds the rule in auditability/traceability/reproducibility rather than
in snobbery about peer review.

### Research question

> "our high level research question is whether current SR guidelines need to be revised to
> address grey literature?"

Answer: "the current SR guidelines do not need any major revisions for grey literature and
multivocal reviews. Candidate primary studies found in the grey literature that conform with the
Prague definition should be treated in exactly the same way as any other primary studies and can
include industry-based field studies as well as academic experiments."

### The four positions the paper argues from (verbatim)

1. "Systematic Reviews can include grey literature, providing it conforms with the SR eligibility
   criteria."
2. "Social media posts such as blogs and tweets can identify new solutions and new ideas, but do
   not usually report the details of any empirical studies evaluating such ideas and solutions."
3. "Blogs, tweets etc. are not the only source of industry-based and practitioner-based
   viewpoints. If available, reports of industry field studies should always be included,
   otherwise SRs only provide weak evidence."
4. "Surveys of social media sources can be used to understand and interpret SR results in
   mixed-methods studies."

### Definitions (verbatim)

**Luxembourg definition** (Third International Conference on Grey Literature, 1997; expanded New
York 2004):
> "information produced on all levels of government, academia, business and industry in
> electronic and print formats not controlled by commercial publishing, i.e., where publishing is
> not the primary activity of the producing body."

**Prague definition** (12th Int. Conf. on Grey Literature, Prague, Dec 2010) — the definition
this paper adopts for SRs:
> "Grey literature stands for manifold document types produced on all levels of government,
> academics, business and industry in print and electronic formats that are protected by
> intellectual property rights, of sufficient quality to be collected and preserved by library
> holdings or institutional repositories, but not controlled by commercial publishers i.e., where
> publishing is not the primary activity of the producing body."

Why Prague matters for SRs (verbatim, two numbered reasons):
1. "The type of non-white documents that are most likely to provide evidence derived from
   rigorous empirical studies (referred to as primary studies in the context of SRs)."
2. "The type of non-white documents that are most likely to remain accessible in the public
   domain in the long term. This addresses the goal of systematic reviews to be as auditable,
   traceable and reproducible as possible."

**Grey literature sources of particular relevance to SRs** (verbatim bulleted list):
- "PhD and Masters theses,"
- "academic technical reports,"
- "industry and government white papers,"
- "versions of papers, and their supplementary materials that are in press, or published on
  pre-print, archive, or protocol registration sites."

**Proposed replacement terminology** for material outside the Prague definition:
1. "**Social media posts**, when referring to online communication media such as blogs, tweets,
   wiki's, vlogs, online videos, Q&A fora. ... The problem with information obtained from these
   types of document is that, although the material may have been easily accessible at a specific
   point in time, it is not guaranteed to have long-term accessibility in the public domain."
2. "**Personal communications**, when referring to industry and government internal communications
   such as memos, e-mails, meeting notes, minutes and agendas. The problem with information
   obtained from sources such as these is that they are not publicly accessible..."

"White literature" = "conventionally published and catalogued information sources such as books
and book chapters." The authors' position: "any conventionally published book and any of its
individual chapters is the same as any other conventionally published material and should be
classified as white literature."

Competing models it summarises (attributed, not the paper's own):
- R. Adams et al. tiered model: "Grey Literature tier 1 ... high outlet control and high
  credibility, such as books, magazines, government reports, and white papers. Grey Literature
  tier 2 ... moderate outlet control and moderate credibility, such as annual reports, news
  articles, presentations, videos, Q&A sites (such as StackOverflow), and Wiki articles. Grey
  Literature tier 3 ... low outlet control and low credibility and includes blogs, emails, and
  tweets."
- J. Adams et al. three-type model: "grey literature such as internal reports, working papers and
  newsletters which they classify as *informally published*; grey data such as tweets, blogs,
  Facebook status updates, which they classify as *self-published*; and grey information such as
  meeting notes, personal e-mails, and personal memories which they classify as *unpublished*."
- Garousi et al.'s SE definition (which this paper resists): "Grey literature in SE can be defined
  as any material about SE that is not formally peer-reviewed nor formally published."

Critique of definition-by-example: "These models are not exactly equivalent and are largely
defined by example, which is a weak method of definition, because such definitions are seldom
complete, and as new examples occur, they may be classified differently by different people."

### Process rules for secondary studies

- **Unit of analysis:** "the unit of analysis for an SR is the primary study. Thus, it is not the
  source but the type of information that is important. Any report describing a rigorous
  empirical evaluation is a candidate primary study." (Mapping studies are noted as an exception:
  "mapping studies tend to classify studies at the source level.")
- **What a primary study must contain:** "Primary studies need to be full reports of research
  projects including research questions, description of the empirical and analysis methods used,
  their results, and their limitations. This level of detail is necessary in order for any
  evidence they report to be properly assessed for rigour and validity."
- **Reader-facing requirements** (verbatim): readers of an SR or SMS "should be able to:
  1) access all the primary studies identified in the review; 2) link individual primary studies
  to each reported finding."
- **No special processing for grey primary studies:** "No special guidelines are needed for
  processing such primary studies, because after passing the eligibility criteria they are
  regarded as equivalent to primary studies from white literature sources."
- **Why search grey literature:** publication bias — "articles describe primary studies that did
  not find novel results. Such articles may not be formally published, because authors,
  reviewers, or journal editors are not very interested in replications or negative results."
- **Where to search for grey literature** (verbatim): "Authors need to consider citation searching
  of identified primary studies (i.e., snowballing), direct approaches to subject experts,
  searching sources that catalogue PhD and MSc theses, searching sources such as archive sites and
  protocol registration sites, as well as using Google Scholar."
- **Blog admissibility rule:** "A blog should only be included as a primary study in a systematic
  review if it describes a well-conducted empirical study which is not formally published
  elsewhere and which is likely to be available in the long term."
- **Mixed-methods review structure** (from the Cochrane Handbook): "A mixed-method review is based
  on using aggregated qualitative findings to interpret and explain the results obtained from
  aggregated quantitative findings. Thus, the results of both qualitative aggregation and
  quantitative aggregation are kept separate (and can, therefore, be upgraded independently), but
  the findings from each aggregation are compared to provide more nuanced overall findings and
  recommendations."
- **Blog surveys are primary studies, not secondary studies:** "In our opinion, reviewing a blog
  authored by a specific individual and extracting comments related to our own research questions
  is similar to analysing an unstructured interview." Consequently "the methodology required to
  aggregate information from social media sources such as blogs should be based on qualitative
  research methodologies, not secondary study methodologies such as the systematic review
  methodology or systematic mapping study processes."
- **Repeatability vs reproducibility distinction:** "Qualitative primary studies have a
  requirement for methodological repeatability (being able to repeat the study methodology with
  different contexts, participants, or sources), but not reproducibility (being able to trace
  findings from the original study to each individual source)."

### Caveats, traps and pitfalls (verbatim)

- **Terminology drift causes real harm:** "Using the term grey literature to include concepts
  that differ in essence, not just in degree, can lead to a misunderstanding of how information
  from different types of literature can be used."
- **The consequence of ignoring auditability:** "Ignoring the requirement for auditability,
  traceability and reproducibility would cause SRs and mapping studies produced in SE to be
  substantially weaker than those in other disciplines."
- **Bias in blogs** (verbatim): "i) blog authors may have unstated vested interests and ii) they
  do not always represent the viewpoint of software engineering practitioners, because they may
  be produced by managers, consultants or tool vendors. For example, the list of bloggers
  reported by Rainer and Williams includes influential and experienced software experts, but
  these are not typical software engineering practitioners. Furthermore, it is not clear that the
  existence of such biases will be recognised by readers, in particular students, who too readily
  assume that most internet material is trustworthy."
- **Lack of provenance** (verbatim): "Social media posts and private communications do not usually
  observe the need to cite original sources nor to respect copyright relating to graphics. ...
  This means that the notion of identifying independent pieces of evidence cannot be guaranteed,
  and using frequency counts to identify the importance of specific issues becomes
  misleading/valueless. Also, unlike the case for SRs based on primary studies, there is no
  accepted procedure for updating SRs that integrate social media posts and private communications
  with archival empirical studies."
- **No accountability regime for social media:** "For any research reports submitted to scholarly
  journals, there is a reasonable expectation that researchers have adhered to basic scientific
  principles, such as avoiding plagiarism, adhering to good practice in the conduct of their
  research and reporting any external research funding. ... No such expectations apply to social
  media posts."
- **Transience / link rot, with the paper's own measurement:** "Garousi and Mäntylä cited 46
  internet articles and white papers using URL addresses, but, as of 25th May 2021, Kitchenham and
  Madeyski independently confirmed that only 19 were still accessible." Using the Wayback Machine
  they recovered 15 of the 27 missing (56%). "it is clear from our example, that the results
  reported by Garousi and Mäntylä are no longer fully auditable, traceable or reproducible by
  third party readers."
- **Wayback Machine is only a partial fix:** "such a solution may also lead to conflicts with
  copyright laws, while still not guaranteeing the long-term accessibility of the information to
  third parties" — and "use of the Wayback Machine can also be ethically questionable given the
  current debate about issues such as the right to be forgotten."
- **Ethical hazard of unvetted blog content:** "it may be difficult to distinguish malicious and
  untrue comments from fair and reasonable comments. Thus, there is a danger that an academic
  publication including unvetted blog content could add legitimacy to untrue or malicious
  comments."
- **Weak evidence without field studies:** "systematic reviews that do not include industry field
  studies can only provide weak evidence regarding the benefit of a new technique."
- **Self-criticism of existing guidelines:** "It is a fair criticism of the various guidelines
  produced by Kitchenham et al. ... that they do not emphasise and explain the need to search grey
  literature clearly enough"; and "another fair criticism ... is that they do not make the
  importance of field studies clear enough".
- **Expert opinion is unreliable — five worked cautionary cases** (verbatim, condensed):
  Linus Pauling was wrong that vitamin C prevented the common cold, having "missed five important
  studies that had non-significant results"; corticosteroids for premature delivery — evidence
  existed by 1984 but the Royal College only advised use in 1993, and "Delay in adopting the use
  of corticosteroids resulted in many unnecessary infant deaths"; oxygen-rich environments for
  premature babies caused blindness; Boehm and Basili's 2001 claim that "Perspective-based reviews
  catch 35 percent more defects than nondirected reviews" was contradicted by Ciolkowski's 2009
  meta-analysis ("there is not a clear advantage of PBR over other reading techniques"); the
  belief that models beat humans at effort estimation was refuted by Jørgensen's SR (roughly a
  third each way).
- **Belief persistence:** Tatsioni et al.: "Claims from highly cited observational studies persist
  and continue to be supported in the medical literature despite strong contradictory evidence
  from randomized trials". And Devanbu et al.: "practitioner beliefs are primarily based on
  personal experience, which can vary from project to project, but do not necessarily correspond
  to actual project evidence."
- **Researcher bias is detectable in SRs but not in blogs:** Shepperd et al. found defect
  prediction outcomes "much more strongly related to the research group than the different
  prediction methods"; Ciolkowski found "Studies where the principle investigator had been
  involved in the initial PBR study ... tend to produce positive results, while the rest of the
  studies tend to produce negative results". "In general, assessing whether a blog is trustworthy
  is much more difficult than for a conventional research report because they seldom provide
  sufficient information to properly assess the risk of bias associated with their claims."

### Checklists / reporting guidance — the seven Recommendations (verbatim)

1. "**Recommendation 1.** Clearly distinguish information obtained from grey literature
   conforming with the Prague definition from information obtained from other social media
   material."
2. "**Recommendation 2.** Do not arbitrarily exclude primary studies obtained from grey literature
   studies from inclusion in SRs."
3. "**Recommendation 3.** Only systematic reviews that include rigorous field studies or
   large-scale (realistic) empirical evaluations should make recommendations regarding industry
   SE practice."
4. "**Recommendation 4.** Use the term survey, not grey literature review, to refer to any study
   aimed at aggregating personal opinions derived from blogs."
5. "**Recommendation 5.** Use information from studies that aggregate blogs to support the
   interpretation of systematic reviews, and/or the fourth step in the EBSE process."
6. "**Recommendation 6.** Use information from private communication channels to support
   validation of qualitative data and interpretation of quantitative study findings."
7. "**Recommendation 7.** Ensure that any social media material reporting a primary study will be
   permanently and legally available to the SR readers."

Naming rule for blog studies: "if a study examines blogs to identify opinions about the benefits
and risks of the DevOps approach, it should use a title such as 'Risk and Benefits of DevOps: A
Survey of Blogs'."

Also flags: "Guideline 13 from [Garousi et al.], which concerns data synthesis, needs to be
refined." And endorses one item of the MLR guidelines: "Garousi et al.'s checklist in Table 7 is a
good contribution to the discussion of quality assessment of blogs."

### The four-way comparison rule for SR findings vs blog findings (verbatim)

> "1) If we have agreement between findings from a systematic review and findings from blogs, then
> we can have some confidence that our findings can be trusted.
> 2) If the findings are inconsistent, we should give preference to the SR results, but investigate
> possible contextual factors that might explain the inconsistencies.
> 3) If there are blog findings but no corresponding SR findings, we have a potentially important
> topic that would benefit from more formal study and evaluation.
> 4) If SR findings relate to topics that are not mentioned in any blogs, the SR may be reporting
> an issue that is of little relevance to industry."

Reporting-form rule for such comparisons: count *primary studies* per topic, not raw mentions —
"If information from the blogs and other white papers were treated as findings from a single
primary study, as we suggest, each finding from the survey would add only a single count to each
of the topics mentioned (perhaps with the details reporting the percentage of blogs that mentioned
the topic)."

### Threats to validity framework

Not a taxonomy paper, but it names three properties as the binding constraints on secondary-study
source admissibility, used throughout as the test: **auditability, traceability, reproducibility**.
Additional named threat categories applied to non-white sources: *bias* (vested interest,
unrepresentative authorship), *lack of provenance* (uncited reuse defeating independence and
frequency counts), *transience* (link rot defeating reproducibility), and *researcher bias*
(detectable in primary-study SRs, not in blogs). It also cites Zhou et al., "A map of threats to
validity of systematic literature reviews in software engineering" as a source on the topic.

### Stakeholder / practitioner involvement

- Field studies, not blogs, are the primary route to the practitioner viewpoint: "any good quality
  industrial field study or case study should be able to help ensure that the findings of a
  systematic review will reflect practitioner values and priorities."
- Curtis et al.'s framing of why lab studies are insufficient: large-scale software development is
  "a complex system involving individual programmers, the teams in which they work, the projects
  on which they work, the organisation that employs them, and the business sector in which the
  organisation does business. Laboratory experiments and small-scale validation studies that remove
  software engineering activities from their natural environment, cannot provide accurate
  assessments of the likely impact of a new technique when it is introduced into an industrial
  software production environment."
- Medical precedent: "the medical guidelines on which the SE systematic review guidelines were
  initially based, considered only field studies of interventions to be admissible evidence.
  Results from animal experiments or laboratory experiments would not be considered for inclusion
  as candidate primary studies."
- Diagnosis of the real problem: "the problem is not that SE systematic reviews exclude industry
  studies, it is more that SE researchers do not perform enough field studies and do not report
  the findings of such studies clearly enough. Nor do systematic reviewers always give enough
  emphasis to field studies in their analyses."
- **EBSE step 4** is where practitioner/opinion material legitimately enters: the four EBSE steps
  are "i) converting the need for information into an answerable question, ii) tracking down the
  best evidence to answer that question, and iii) critically appraising that evidence [systematic
  reviews address these three] ... The fourth step concerns integrating the critical appraisal
  with software engineering expertise and stakeholders' values." Footnote: "The introduction of
  context and personal opinion during this stage of EBSE is one justification for using the term
  evidence-informed rather than evidence-based, as is becoming the norm in other disciplines."

### Empirical findings worth citing

- Kamei et al.: "found 126 SRs out of a total of 446 that included references to grey literature."
  Restricted to Prague-conforming grey literature: "53 references to technical reports, 34 to
  theses, 11 to white papers, and 5 to preprints"; possibly also "web documents (8 references) and
  magazine article (7 references)."
- Budgen et al. tertiary study: "selected 49 SE systematic reviews (from a set of 276) that
  included findings relevant to teaching about SE practice. They analysed 48 data sets used by
  these. ... they were confident that 23 of the secondary studies were based mainly on industry
  studies and that a further 18 almost certainly included industry studies."
- Garousi & Mäntylä's multivocal review: "found only six sources that reported empirical evidence,
  and all of those sources were classified as being formal literature." Hence "there is no evidence
  that social media material will provide additional value in the context of evaluation-based SRs."
- Link-rot measurement (this paper's own): 19/46 URLs still live after ~5 years; 15 of 27 missing
  recovered via the Wayback Machine (56%).

---

## wyrich_2026 — Software Engineering Podcasts: An Empirical Study of Their Potential as a Research Resource

Marvin Wyrich, Marcos Kalinowski, Adolfo Neto, Sven Apel. arXiv:2605.26793v1, 26 May 2026.

**Type:** Empirical study (two-part: systematic landscape analysis + researcher survey);
explicitly exploratory and descriptive, with no pre-registered hypotheses.

**Role in corpus:** The only paper here that examines *audio* practitioner material as a
prospective evidence source, and the only one that measures what SE researchers say would have to
change (transcripts, discoverability, sourcing) before such material could be cited in reviews.

### Research questions (verbatim)

- "RQ1: What topics and formats characterize the current landscape of SE podcasts?"
- "RQ2: How do SE researchers perceive podcasts as a resource for empirical research?"

### Process steps or stages defined

The paper defines no review process. It does define a reusable **corpus-construction procedure**
for a landscape/mapping study over a non-bibliographic medium:

1. **Define the artefact type.** "We define software engineering podcasts as podcasts that deal
   thematically with the development of software systems. These may include discussions on topics
   related to the act of programming, design, testing, management, and maintenance of software
   systems, as well as discussions about the people who participate in the software process, their
   professional practices, aspirations, challenges, and skills." Deliberately broad: "It is
   opportune to define the term rather broadly to be able to identify a certain variety of podcasts
   and potentially also to find podcasts that are at the intersection to other disciplines."
2. **Reject purely automated filtering.** "We consider fully automatic filtering, for example,
   based on terms that must appear in the title of the podcasts, to be too restrictive. One reason
   for this is that podcasts tend to use creative wordplay in their names, which are recognizable
   to a human, but not a keyword search."
3. **Apply inclusion criteria, unanimously across three assessors** — verbatim:
   - "I1 At least three out of the podcast's six most recent episodes explicitly refer to software
     engineering in their title or description, according to our definition of SE podcasts provided
     above."
   - "I2 The language of the podcast is English."
   - "I3 At least three episodes have been published."
   - "I4 At least one episode has been published since 2021."
   Justifications given: I2 "to ensure that our study results can be transparently understood by
   the international research community"; I3 "to ensure that our results are not skewed, for
   example, by podcasts that have discontinued after only one or two episodes or merely serve as a
   storage location for a single audio file"; I4 to focus on podcasts "active within, at least, the
   past five years."
4. **Search.** Spotify API, term "software engineering", markets US/GB/AU/IN ("markets where the
   language of the target audience is likely to be English and which also have a good geographical
   distribution"), searched 19 September 2024.
5. **Filter and screen.** After duplicate removal and automatic filtering on I3/I4, 828 results
   remained; manual assessment yielded 224; "After a sanity check by the fourth author and an
   attempt to listen to each podcast at least once, eight more were excluded due to lack of access
   or contents that did not correspond to the podcast description." Final corpus: **216** podcasts.
   Metadata retrieved June 2025.
6. **Categorise content and format, then supplement with metadata.**

Survey procedure: "we follow Kasunic's seven-step guideline for survey design, complemented by
Linåker et al.'s more recent annotations." Convenience sampling via social networks, email lists
and snowballing; 15-minute design target; questionnaire in four sections (points of contact — 4
questions; perceived value — 5; barriers — 3; demographics — primary role, years in SE research,
age, region) plus a closing open question; 17 questions total, 4 open-ended, one ranking question.
Pilot with 3 target-population members (1 professor, 1 PhD student, 1 industry researcher); online
21 days with three reminders. Filtering: "we removed all cases in which participants had clicked
through the survey without providing any responses. Then, for each individual question, we
performed sanity checks where appropriate"; partial responses retained, so "the number of valid
answers may vary across questions."

### Data extraction and analysis techniques

- **Failed classification scheme, reported honestly.** First attempt used "the research areas
  listed in the ICSE 2025 call for papers ... nine research areas". Why it failed (verbatim): "we
  soon observed that the more episodes we examined from a given podcast, the more likely it was
  that nearly all areas would be covered, especially in podcasts with a wide-ranging focus. The
  ICSE categories offer a fairly academic partitioning of research topics, which may work well for
  structuring scholarly work, but are less suitable for classifying the more fluid, overlapping
  discussions typically found in podcasts. This led to inconsistent assignments between authors and
  an overall low explanatory value of the classification."
- **Replacement inductive content scheme** (multi-label), verbatim:
  - "Technical & Practical Knowledge – On how software engineering works,"
  - "Industry & Trends – On what is happening in the software world,"
  - "Career & Social Aspects – On the people behind software engineering."
- **Format scheme** (two categories, after "two rounds of refinement"), verbatim:
  - "Interview and Narrative-Driven Podcasts – These focus on conversations between hosts and
    guests or feature structured storytelling. Formats include expert interviews, co-host
    discussions, or panel episodes that aim to provide engaging insights, experiences, or opinions."
  - "Monologues and Personal Journaling – These involve a single host sharing thoughts, experiences,
    or expertise in a reflective or informative manner, without external guests. Formats range from
    structured topic exploration to spontaneous, journal-like recordings."
  Assignment rule: "A podcast was assigned to both categories if, at least, one episode matched
  each respective format."
- **Metadata extracted per podcast** (verbatim list): "podcast ID, publisher, description, total
  number of episodes, date and duration of the latest episode, podcast image URL, and a list of
  countries in which the podcast is available."
- Analysis: "largely descriptive and exploratory"; UpSet plot for topic-set intersections; violin
  plots for source rankings; raw data shared (Zenodo DOI 10.5281/zenodo.18962642).

### Caveats, traps and pitfalls

- **Loss of researcher control** (the central methodological caveat, verbatim): "Researchers have
  no control over how topics are introduced, structured, or elaborated during an episode, including
  the specific questions asked in interview-style podcasts or the narrative choices made in
  monologue formats. This lack of researcher control should therefore be considered when evaluating
  podcasts as empirical data sources."
- Ryan et al.'s trade-off list, cited: podcasts "offer context-rich, publicly available data without
  the need for recruitment or data collection. At the same time, they come with challenges such as
  limited control over the conversation, ethical ambiguity, and the lack of follow-up questions."
- Guideline transferability is unproven: "it is difficult to assess how well existing guidelines for
  working with grey literature apply to podcasts."
- Complementary, not substitutive: "SE podcasts function primarily as a complementary information
  channel rather than as a substitute for existing knowledge sources."
- **Author conflict-of-interest disclosure, verbatim:** "It is important to note that the third
  author of this paper is the host of a software engineering podcast, bringing firsthand experience
  to the study. His podcast is distributed on platforms such as Spotify. However, none of the
  authors, including the third author, stand to gain personally or professionally from research on
  this specific topic, and we have no affiliation with Spotify."

### Threats to validity framework

No named framework; a "Limitations" section (5.3) with three items:
1. **Search/selection subjectivity and recall gap:** "the identification of SE podcasts relied on a
   semantic inclusion criterion rather than a purely keyword-based search. Although this approach
   helped avoid missing relevant podcasts that do not explicitly use predefined keywords, it
   introduces a degree of subjectivity. Some podcasts mentioned by survey respondents were not
   retrieved through our search procedure" — a documented instance: The Haskell Interlude
   "apparently does not mention 'software engineering' in either the podcast description or episode
   descriptions and, we suspect, was therefore not found."
2. **Sampling/geographic bias:** "the survey sample is geographically concentrated, with respondents
   predominantly based in Europe and South America. This may partly reflect the authors'
   professional networks." Also, English-only corpus.
3. Self-assessed severity: "we do not consider these limitations severe, but they rather reflect the
   exploratory nature of this study."

### Stakeholder / practitioner involvement

The paper's motivating argument for practitioner-authored media as evidence (verbatim):
> "While these initiatives reflect a genuine effort to foster dialogue, they still rely on
> practitioners taking time to enter academic spaces, adopt academic formats, and speak the language
> of research. But practitioners are already communicating—openly, informally, and at scale—on
> platforms and in formats they choose themselves. It may not always be necessary to ask them to
> write or come to academic venues. It may simply require listening."

Existing academic mechanisms it contrasts against: the JSS "Dear Researchers" column and the ICSE
Industry Challenge Track.

### Empirical findings worth citing

**Landscape (n = 216 podcasts, data to June 2025):**
- Episodes per podcast: median **34** (M = 126, SD = 270, range 3–2,093).
- Latest-episode duration: median **39 minutes** (M = 40, SD = 25, range 2.2–146); majority between
  20 and 60 minutes.
- "Nearly half of the podcasts (∼47%) can be considered still active, having released, at least,
  one episode in the first half of 2025."
- Publisher concentration: near-zero — "only three exact name matches where a publisher is
  associated with two podcasts."
- Topics: Technical & Practical Knowledge **196**; Career & Social Aspects **150**; Industry &
  Trends **85**. Largest intersection: technical + career/social, **73** podcasts. 15 podcasts were
  career/social only. "pure trend podcasts ... are less common."
- Formats: **157** interview-only, **39** monologue-only, **20** mixed. "all SE podcasts in our
  sample can be classified using this simple format categorization and fit in very well."

**Survey (83 consented; 67 gave ≥1 response; 53 completed; median completion ~7 minutes):**
- Demographics: Faculty 21, PhD student 13, Other 7, Industry researcher 6, Postdoc 3. Experience:
  >10 years 18; 6–10 years 16; 3–5 years 10; 0–2 years 7. Age: 25–34 = 21, 35–44 = 21, 45–54 = 6,
  <25 = 2, 55+ = 1. Region: Europe 25, South America 21, North America 2, Asia 1, Africa 1,
  Australia/Oceania 1.
- Private listening (n=67): Daily 25.4%, Weekly 32.8%, Monthly 10.4%, Rarely 22.4%, Never 9.0% —
  "a large proportion of 68.7% listen to podcasts, at least, monthly in their private time."
- Work-time listening: Daily 7.5%, Weekly 14.9%, Monthly 9.0%, Rarely 28.4%, Never 40.3% — "about
  68.7% rarely or never listen to podcasts during work hours."
- Ever listened to an SE podcast: Yes **61.2%** (41), No 28.4% (19), Unsure 10.4% (7).
- 84 different podcasts named by respondents; most-cited was *Fronteiras da Engenharia de Software*
  (18 mentions, hosted by the third author); ≥4 mentions also for Software Engineering Radio,
  Hipsters Ponto Tech, Software Engineering Daily, The Pragmatic Engineer, The Changelog.
- Relevance to own research: strongly agree 7 (11.5%), agree 22 (36.1%), neutral 23 (37.7%),
  disagree 4 (6.6%), strongly disagree 5 (11.5%). "for roughly every second respondent, SE podcasts
  are either already relevant to their research or are seen as having potential relevance."
- Value aspects (multi-select, median 3 selected): learning about new research **43**, expert
  opinions **43**, industry insights **38**, inspiration for new research questions **32**, other 6.
- **Source ranking (n=59), most→least relevant:** Scientific Papers > Books > Conference
  Presentations > Blogs > Podcasts ≈ Social Media (podcasts and social media "shared the lowest
  rank").
- Barriers (multi-select, median 2 selected): too time-consuming **28**, hard to find and/or
  reference **26**, lack of credibility **15**, not research-focused **14**, not enough high-quality
  content **9**, other 9. Free-text additions: "informality", "subjectivity", "the difficulty in
  explaining ideas (sometimes complex), without the support of visual or written content", lack of
  clarity whether statements "are findings grounded in research or [...] just opinions and ideas",
  "lot of noise (other data)", and the unlikely prospect of "getting reviewers accept [podcasts] as
  reliable source of information".
- **68% agreed or strongly agreed that SE podcasts can be considered a form of grey literature**
  ("suggesting that positioning podcasts within the GL discourse is appropriate").

**Four improvement themes from 25 open responses** (what would make podcasts usable as evidence):
1. **Credibility / sourcing** — hosts should provide "sufficient references" and "sources for the
   topics they discuss" in episode descriptions; podcasts should be used alongside other sources
   "but not the sole reference"; "as any other grey literature source, [podcasts] need an additional
   evaluation to consider what is said and by whom."
2. **Visibility and discoverability** — "a high-quality dataset of SE podcasts with reliable means
   of automatic analysis"; "a single web page or something where all/most podcasts can be found",
   searchable "by keyword, length, topic, or speaker background"; "a globally established platform"
   comparable to Google Scholar, arXiv, or Zenodo but SE-specific.
3. **Citable transcripts** — "ideally allowing specific statements to be linked to exact timestamps
   within an episode. Transcripts would also make podcasts more accessible overall."
4. **Content expectations** — focus on "current industrial practices, tools, and programming
   languages", "expert insights, practical tips, and guidance for conducting research"; suited to
   "sharing informal, experience-based knowledge and real-world perspectives that often do not
   appear in formal publications."

Overall stance characterised by the authors as "cautious curiosity combined with optimism", with
two prerequisites: "methodological guidance to ensure scientific rigor, and practical tools that
enable efficient work with podcast datasets."

**Grey-literature statistics cited from others** (attribution matters): Yasin et al. — "76% of SE
systematic literature reviews include, at least, one grey source, although GL accounts for only
about 9% of all cited primary studies"; Kamei et al. survey of 76 researchers — "over half of
respondents avoid citing it due to concerns about scientific credibility. The most frequently
reported challenges were lack of reliability, lack of scientific value, and difficulties in
searching and structuring GL sources"; and "the most common GL types reported are
practitioner-produced artifacts such as blog posts, slide decks, and project descriptions—podcasts
are not represented in these analyses."

---

## marshall_2013 — Tools to Support Systematic Literature Reviews in Software Engineering: A Mapping Study

Christopher Marshall, Pearl Brereton. ESEM 2013, pp. 296–299.

**Type:** Mapping study (secondary study) about tool support.

**Role in corpus:** Establishes the tooling *landscape and its gaps* — which SLR stages had tool
support in 2012, which had none, and how weakly the tools had been evaluated. It is the input that
motivates the 2014 feature analysis.

### Research questions (verbatim)

- "RQ1) What tools to support the SLR process in software engineering have been reported?"
- "RQ2) Which stages of the systematic literature review process do the tools address?"
- "RQ3) To what extent have the tools been evaluated?"

### Process steps or stages defined

The study itself follows Kitchenham & Charters (2007). Its method is reproduced here because it is
a compact worked example of a mapping-study protocol:

**Search process.** "automated keyword search of Google Scholar, ACM DL and IEEE Xplore plus
snowballing (pursuing references of included papers). The search used a start date of 2004. This
was the year that Kitchenham introduced the first version of guidelines for performing SLRs in SE.
The end date for the search was 2012."

Four search strings, verbatim:
- "(tool OR support OR approach OR supporting) AND ('systematic literature review' OR 'systematic
  review' OR 'systematic literature reviews' OR 'systematic reviews' OR SLR) AND ('software
  engineering')"
- "(tool OR support OR approach OR supporting) AND ('systematic literature review' OR 'systematic
  review' OR systematic literature reviews' OR 'systematic reviews' OR SLR) AND (automatic OR
  automated OR automation)"
- "(tool OR support OR approach OR supporting) AND ('mapping study' OR 'systematic mapping study')
  AND ('software engineering')"
- "(tool OR support OR approach OR supporting) AND ('mapping study' OR 'systematic mapping study')
  AND ('software engineering') AND (automatic OR automated OR automation)"

**Search validation (quasi-gold standard).** "Following the advice reported by Kitchenham et al.
the search process was assessed for completeness by 'obtaining a large and varied set of known
studies based either on personal or manual search of important sources'. Relevant papers identified
in a related study provided the set of 11 known papers. All but one paper was identified using the
automated search. However, the paper in question was referenced in a number of articles in the known
set. Since we intended to use snowballing as part of our search strategy, we concluded our overall
approach adequate."

**Two-stage selection.** "Firstly, papers located by the initial search were assessed for inclusion
based upon analysis of their title and abstract. This stage was carried out by the first author only
and papers that were clearly of no relevance were discarded. In the second stage, papers were
assessed against the inclusion/exclusion criteria by both authors using the full text."

**Inclusion criteria** (verbatim):
- "The publication must report on a tool that supports an SLR, MS or both within the software
  engineering field."
- "The tool can support any stage of the SLR/MS process."
- "The paper can report on any stage of development of the tool (i.e. proposal, prototype,
  functional etc.)."

**Exclusion criteria** (verbatim):
- "Papers that are not written in English."
- "Abstracts and PowerPoint Presentations."

**Data extraction items** ("extracted from each paper, independently, by the two authors.
Disagreements were resolved through discussion") — verbatim:
- "Abstract and bibliographic information"
- "Study type (e.g. experiment, case study, discussion)"
- "Aims and objectives"
- "Type of approach underlying the tool (e.g. visualisation, text analysis etc.)"
- "Name and short description of support tool"
- "The particular stage of the SLR process that the tool supports (e.g. study selection, data
  extraction)"
- "Whether the tool has been independently evaluated"

**Two operational definitions agreed during extraction** (worth reusing):
- Example vs small experiment: "A study that involved applying a tool to elements of a published SLR
  and then discussing the outcomes in relation to those of the published study was classified as an
  example. An experiment involving a small number of participants was considered a small experiment."
- Independent evaluation: "It was agreed that where no author had been involved in developing the
  tool the evaluation should be considered independent."

Selection funnel: 21 papers after title/abstract → 16 judged relevant on full text → 2 excluded
during extraction → **14 papers final**.

### Evaluation criteria / classification schemes (all tables reproduced)

**Table II. Underlying approach**

| Underlying approach | Paper ID | Total |
|---|---|---|
| Visualisation | P01; P02; P03; P04; P07; P11 | 6 |
| Text mining | P01; P02; P03; P04; P05; P08; P09; P14 | 8 |
| Visual text mining (VTM) | P01; P02; P03; P04 | 4 |
| Tools that support the whole SLR process | P05; P10; P15 | 3 |
| Ontology | P12 | 1 |
| Search tool | P16 | 1 |

**Table III. Support tools**

| Support tool | Paper ID | Total |
|---|---|---|
| Project Explorer (PEx) | P01; P02; P11 | 3 |
| ReVis | P03; P04 | 3 |
| SLR-Tool | P05 | 1 |
| Hierarchical Cluster Explorer (HCE) | P07 | 1 |
| Site Content Analyzer | P08 | 1 |
| UNITEX | P09 | 1 |
| SLuRp | P10 | 1 |
| SLRONT | P12 | 1 |
| StArt | P15 | 1 |
| DBpedia | P14 | 1 |
| Unnamed tool | P09; P14 | 2 |

(Note: the ReVis row is printed with Total = 3 but lists two paper IDs; the PEx row lists three.
[EXTRACTION UNCLEAR: whether ReVis's total of 3 is a typo in the original or a third paper omitted
from the ID list.])

**Table IV. SLR stage targeted by tool** — this doubles as the paper's stage taxonomy.

| SLR Phase | SLR Stage | Paper ID | Total |
|---|---|---|---|
| Planning the review | Identification of the need for a review | – | – |
| Planning the review | Development of protocol | – | – |
| Conducting the review | Identification of research | P16 | 1 |
| Conducting the review | Study selection | P01; P03; P04; P12; P14 | 5 |
| Conducting the review | Study quality assessment | – | – |
| Conducting the review | Data extraction | P02; P09; P12 | 3 |
| Conducting the review | Data synthesis | P02; P07; P08; P11 | 4 |
| Reporting the review | — | P11 | 1 |
| Whole process | — | P05; P10; P15 | 3 |

**Table V. Method of evaluation**

| Type of study | Study ID | Total |
|---|---|---|
| Small experiment | S01; S03; S04; S05; S09 | 5 |
| Experiment | S08 | 1 |
| Example | S02; S04; S05; S06; S09; S10 | 6 |
| Survey | S11 | 1 |

**Table I. Set of included papers** (paper → study → year)

| Paper ID | Study ID | Year |
|---|---|---|
| P01 | S01 | 2007 |
| P02 | S02 | 2010 |
| P03 | S03 | 2011 |
| P04 | S04, S05 | 2012 |
| P05 | – | 2010 |
| P07 | S06 | 2007 |
| P08 | – | 2007 |
| P09 | S07 | 2012 |
| P10 | – | 2012 |
| P11 | S08 | 2011 |
| P12 | S09 | 2012 |
| P14 | S10 | 2007 |
| P15 | S11 | 2012 |
| P16 | – | 2012 |

### Caveats, traps and pitfalls

- **Zero tool support for two stages.** Nothing addressed "Identification of the need for a review",
  "Development of protocol", or "Study quality assessment" (all blank in Table IV).
- **Evaluation is almost entirely non-independent.** "Most (9) of the evaluation studies were
  carried out by the tool developers or by researchers who had adapted or applied generic tools to
  support the proposed approach. Two studies report independent evaluations of a tool (S07, S11)."
- **Immaturity:** "The majority of papers only presented preliminary investigations, often
  describing an example of the tool in use, or a small experiment to assess its effectiveness. ...
  These results reflect the immaturity of the research area"; "most of the tools identified are in
  early stages of development and usage. This has led to very little primary data regarding their
  effectiveness, and generally only speculation over their potential."
- **Limitations of the mapping study itself** (verbatim): "Due to a low number of resources and the
  absence of any manual search, there is the possibility that not all relevant papers were located."
  And a candid reviewer-independence threat: "the fact that one of the authors is a PhD student and
  the other his supervisor might have influenced the outcomes."
- Recommendation: "An empirical investigation to assess the effectiveness of SLR tools could be a
  beneficial contribution to the topic."

### Empirical findings worth citing

- 14 papers accepted; **8 present text mining tools, 6 discuss visualisation**; three target the
  whole SLR process (SLR-Tool, SLuRp, StArt).
- "The stage most commonly targeted was study selection" (5 papers); then data synthesis (4), data
  extraction (3).
- "Only two papers reported an independent evaluation of the tool presented."
- Evaluation scale: "Five studies report a small experiment with a sample size between three and
  five. S08 is a full-scale experiment with 24 participants. The participants had a range of levels
  of experience and most were PhD and Masters students. A survey reported in S11 involved 49
  Computer Science graduate students overall."
- Motivating premise, repeatedly cited: conducting SLRs/MSs "remains a manual and labour intensive
  process ... making SLRs/MSs prime candidates to benefit from technological support."

---

## marshall_2014 — Tools to Support Systematic Reviews in Software Engineering: A Feature Analysis

Christopher Marshall, Pearl Brereton, Barbara Kitchenham. EASE '14, London.

**Type:** Tool evaluation (qualitative feature analysis under DESMET).

**Role in corpus:** Supplies the *requirements specification* for review-support tooling — a
weighted, four-set feature model with explicit judgement scales — plus a scored comparison of the
four whole-process SR tools that existed. This is the single most directly reusable artefact in the
corpus for anyone building software to support reviews.

### Aim (verbatim)

"The aim of this research is to evaluate a set of candidate tools that provide support for the
overall systematic review process." Also framed as "the first step toward the development of a
rigorous evaluation framework for tools that support SRs."

### Process steps or stages defined

**Context model:** "An SR comprises several discrete stages that can be grouped into three phases;
namely, the planning phase, the conduct phase and the reporting phase (see Figure 1)." Figure 1 is
captioned "10-Stage Systematic Review Process". [EXTRACTION UNCLEAR: the ten individual stage names
inside Figure 1 are not present in the extracted text — the figure content did not survive
extraction. The 2013 companion paper's Table IV gives the equivalent stage list.]

**DESMET method** (Kitchenham, Linkman & Law 1997), as described here:
- "DESMET is a methodology for evaluating methods or tools. It defines nine different evaluation
  types and a set of criteria to assist the evaluator in selecting the most appropriate one based on
  their needs."
- "A DESMET evaluation is context-dependent and comparative. This means it is not used to rank tools
  in terms of effectiveness, but instead to retrieve information on which to base a decision about a
  tool's suitability in a particular context." Context here: "an academic one, specifically where
  researchers are undertaking an SR within the SE domain."
- Selection logic: "If the primary aspects of a tool to be evaluated are the effect it has within an
  organisation, then quantitative methods of evaluation are deemed most appropriate. If, however,
  the objective of the evaluation is more concerned with the suitability of a tool in a given
  setting, then this can be better determined using a qualitative form of evaluation. Both
  categories of evaluation can be organised as a formal experiment, case study or survey.
  Qualitative forms of evaluation, however, can also be organised as a feature analysis."
- Feature analysis: "a qualitative form of evaluation involving the subjective assessment of the
  relative importance of different features plus an assessment of how well each of the features is
  implemented by the candidate tools. It is an established evaluation method in SE. The feature sets
  are based on the requirements that users have for the particular tasks that they expect the tool
  to support. For this study, a feature analysis is organised as an initial screening and focuses on
  evaluating simple features. Simple features relate to aspects that are either present, partially
  present or absent."

**Scoring process** — three elements, verbatim:
- "scoring each tool against each feature to produce a raw score,"
- "assigning a level of importance to each feature which is used as a weighting (i.e. a multiplier)
  to convert raw scores to weighted scores for each feature,"
- "determining scores for each feature set and an overall score for each candidate tool."

Validation: "Each tool was initially scored against each feature by the first author (CM). The
scores were then discussed by all of the authors to produce a set of validated raw scores."

Feature-set percentage: `Percentage Score = (Sum of Weighted Scores / Maximum Score) × 100%`, where
"The maximum score for a feature set is assumed to be the sum of the weighted scores where all
features in the set are fully present (or fully supported)." Maxima: F1 = 6, F2 = 16, F3 = 23,
F4 = 17 (total 62).

Overall: `Overall score = Σᵢ₌₁⁴(wᵢ·TPᵢ) / Σᵢ₌₁⁴(wᵢ)` (Eq. 3.1), "where wᵢ is the weighting for the
ith feature set and TPᵢ is the percentage score for the ith feature set." Normalised (percentage)
scores are required "Since there are a different number of subfeatures in each of the feature sets."

Where the features came from (verbatim): "Features for this study are based on: the experiences of
performing SRs reported in the literature; a preliminary screening of the four candidate tools;
discussions between the authors." And per DESMET: "As well as covering technical aspects, features
should also include economic, cultural and quality aspects. A feature can be decomposed into
subfeatures and further broken down into subsubfeatures if required."

### Evaluation criteria — the full feature model (Table 1, all 23 subfeatures verbatim)

| id | Feature Set | id | Subfeature | Level of Importance | Judgement Scale | Feature Set Weighting |
|---|---|---|---|---|---|---|
| F1 | Economic | F1-SF01 | The tool does not require financial payment to use. | HD | JI1 | 0.1 |
| F1 | Economic | F1-SF02 | Maintenance | HD | JI1 | 0.1 |
| F2 | Ease of introduction and setup | F2-SF01 | The tool has reasonable system requirements. | M | JI1 | 0.2 |
| F2 | Ease of introduction and setup | F2-SF02 | Simple installation and setup. | HD | JI2 | 0.2 |
| F2 | Ease of introduction and setup | F2-SF03 | There is an installation guide. | HD | JI1 | 0.2 |
| F2 | Ease of introduction and setup | F2-SF04 | There is a tutorial. | HD | JI1 | 0.2 |
| F2 | Ease of introduction and setup | F2-SF05 | The tool is self-contained. | HD | JI1 | 0.2 |
| F3 | SR activity support | F3-SF01 | Protocol development | D | JI3 | 0.4 |
| F3 | SR activity support | F3-SF02 | Protocol validation | D | JI3 | 0.4 |
| F3 | SR activity support | F3-SF03 | Supports automated searches | HD | JI3 | 0.4 |
| F3 | SR activity support | F3-SF04 | Study selection and validation | HD | JI3 | 0.4 |
| F3 | SR activity support | F3-SF05 | Quality assessment and validation | HD | JI3 | 0.4 |
| F3 | SR activity support | F3-SF06 | Data extraction and validation | HD | JI3 | 0.4 |
| F3 | SR activity support | F3-SF07 | Automated analysis | HD | JI3 | 0.4 |
| F3 | SR activity support | F3-SF08 | Text analysis | N | JI1 | 0.4 |
| F3 | SR activity support | F3-SF09 | Meta-analysis | N | JI1 | 0.4 |
| F3 | SR activity support | F3-SF10 | Report write up | N | JI3 | 0.4 |
| F3 | SR activity support | F3-SF11 | Report validation | N | JI3 | 0.4 |
| F4 | Process Management | F4-SF01 | Support for multiple users | M | JI1 | 0.3 |
| F4 | Process Management | F4-SF02 | Document management | M | JI1 | 0.3 |
| F4 | Process Management | F4-SF03 | Security | D | JI1 | 0.3 |
| F4 | Process Management | F4-SF04 | Management of roles | HD | JI1 | 0.3 |
| F4 | Process Management | F4-SF05 | Support for multiple projects | M | JI1 | 0.3 |

(Note on an internal inconsistency: Table 1 lists F2-SF01 as **M** and F4-SF04 as **HD**, but §5.1
says quality assessment was "assigned ... a mandatory level of importance", while Table 1 lists
F3-SF05 as HD. [EXTRACTION UNCLEAR: whether §5.1's "mandatory" is loose prose or the table's HD is a
typo.])

#### Feature-set narrative requirements, verbatim by set

**F1 — Economic.** "This set concerns economic factors relating to the initial cost of the tool and
the subsequent support for maintaining (or upgrading) the tool. For this study, highest scores are
awarded if no initial payment is required (F1-SF01) and the tool is well (and freely) maintained by
its developers, including having regular updates and a single point of contact for users to obtain
support if needed (F1-SF02)."

**F2 — Ease of introduction and setup.** "This feature set focuses on the level of difficulty
inherent in setting up and using the tool for the first time. Each tool should:
- have reasonable system requirements (F2-SF01) and not require any advanced hardware or software to
  function,
- have a simple installation and setup procedure (F2-SF02) that is supported by an installation
  guide (F2-SF03) and/or a tutorial (F2-SF04),
- be as self-contained as possible i.e. able to function, primarily, as a stand-alone application
  with minimal requirements for other external technologies (F2-SF05)."

**F3 — SR activity support.** "These features relate to how well the tool supports each of the three
main phases of an SR and the steps within these phases."

*Planning Phase:* "the tool should support the collaborative development of a review protocol, using
a template, and the control of versions, to keep track of any changes to the protocol during its
development (F3-SF01). It should also support validation of the protocol (F3-SF02). This might be
achieved by enabling evaluation checklists to be distributed to and completed by members of a review
team."

*Conduct Phase:* "the tool should support:
- **automated searching for relevant papers (F3-SF03).** Ideally, the user should be able to perform
  an automated search from within the tool which should identify duplicate papers and handle them
  accordingly.
- **study selection and validation (F3-SF04).** In particular, the tool should provide support for a
  multi-stage selection process (i.e. title/abstract then full paper), for multiple users to apply
  the inclusion/exclusion criteria independently and a facility to reconcile disagreements.
- **quality assessment and validation (F3-SF05).** The tool should enable the use of suitable quality
  assessment criteria, should allow multiple users to perform the scoring and should provide a
  facility to resolve conflicts.
- **data extraction (F3-SF06).** In particular, the tool should support the extraction and storage of
  qualitative data using classification and mapping techniques. In addition, the extraction of
  quantitative data, which manages specific numerical information from a reported study, should also
  be supported.
- **data synthesis (F3-SF07).** The tool should be able to provide automated analysis of extracted
  data. Other types of analysis, such as text analysis (F3-SF08) and meta-analysis (F3-SF09), would
  also be useful."

*Reporting Phase:* "The tool should support the reporting phase of the SR process. This might be
achieved using a template to assist the write-up (F3-SF10) and using automated checklists to support
the validation (F3-SF11)."

**F4 — Process Management.** "This set of features relates to the management of an SR. Undertaking
an SR is a collaborative process. Therefore, the tool should allow multiple users to work on a single
review (F4-SF01). It should support document management (F4-SF02), in particular, managing large
collections of papers, studies and the relationships between them. The tool should be secure
(F4-SF03) and include a user log-in or similar system. It should be able to manage the roles of users
(F4-SF04). For example, it would be useful to state which users will perform certain activities (e.g.
study selection, quality assessment, data extraction etc.) and allocate papers accordingly. Finally,
the tool should be able to support multiple SR projects (F4-SF05)."

#### Judgement scales (Tables 2–4, verbatim)

Base scale: "Where a feature is fully present or strongly supported it was awarded a score of 1,
where it was partly present or partially supported it was awarded a score of 0.5 and where it was
absent or minimally supported it was awarded a score of 0."

**JI1 — Is the feature present?** Yes = 1; Partly = 0.5; No = 0.

**JI2 — Is the tool simple to install and setup?**

| Judgement | Score |
|---|---|
| Yes | 1 |
| Some difficulties — "The tool could be installed, but there were a number of slight difficulties throughout the process." | 0.5 |
| No — "The tool could be installed but the process was very difficult." / "No - The tool could not be installed." | 0 |

**JI3 — Is the activity supported?**

| Judgement | Score |
|---|---|
| Yes – Fully | 1 |
| Partly — "Support is limited. Some aspects of the activity are not supported." | 0.5 |
| No | 0 |

#### Levels of importance (Table 5) and feature-set weights (Table 6)

| Importance | Multiplier |
|---|---|
| Mandatory (M) | ×4 |
| Highly Desirable (HD) | ×3 |
| Desirable (D) | ×2 |
| Nice to have (N) | ×1 |

Rule cited from Kitchenham et al.: "if a tool fails to include a mandatory feature, then it is, by
definition, unacceptable. Non-mandatory features allow the evaluator to judge the relative merit of a
group of otherwise acceptable tools."

| Feature Set | Weight |
|---|---|
| F1 | 0.1 |
| F2 | 0.2 |
| F3 | 0.4 |
| F4 | 0.3 |

Rationale for these weights: "The values here emphasise support for SR activities (F3) and for
process management (F4). Other weightings could be used, perhaps to emphasise usability, as tools to
support SRs become more mature. ... we chose values of the overall weights that emphasised the
feature sets that provide the functions needed by an SR research team performing an SR (i.e. Feature
Sets 3 and 4) and reduced the weights for the feature sets related to economic and installation
issues (i.e. Feature Sets 1 and 2) that are generic tool issues."

### The candidate tools (verbatim descriptions)

- "**Systematic Literature unified Review Program (SLuRp)** which is described as an open source
  web-enabled database that supports the management of SRs. The tool has been developed using Java
  and SQL."
- "**State of the Art through systematic review (StArt)** which aims to provide support for each
  stage of the SR process in SE."
- "**SLR-Tool**, developed in Java, which is described as a freely-available tool to support each
  stage of the SR process in SE."
- "**SLRTOOL** which aims to support the SR process in SE, amongst other disciplines. The developers
  state that the guidelines, established by Kitchenham and Charters, underpin its design. SLRTOOL was
  not identified by the mapping study reported in [9]."

Developer engagement is documented per tool (SLuRp demo attended; StArt supplied an updated version,
a publication and a video tutorial; SLR-Tool supplied an updated version plus user manual and
installation guide; SLRTOOL's developers went unresponsive after an initial reply).

### Results — full score tables

**Table 11. Feature Set Scores and Overall Scores**

| Tool | F1 (/6) | F1 % | F2 (/16) | F2 % | F3 (/23) | F3 % | F4 (/17) | F4 % | Total (/62) | Total % | Overall Score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SLuRp | 6 | 100% | 6.5 | 41% | 10 | 43% | 17 | 100% | 39.5 | 64% | **65.4%** |
| StArt | 6 | 100% | 14.5 | 90% | 8.5 | 37% | 6 | 35% | 35 | 56% | **53.3%** |
| SLR-Tool | 4.5 | 75% | 14.5 | 90% | 10 | 43% | 6 | 35% | 35 | 56% | **53.2%** |
| SLRTOOL | 3 | 50% | 11.5 | 72% | 4.5 | 20% | 10 | 59% | 29 | 46% | **45.1%** |

**Per-subfeature weighted scores** (Tables 7–10, all four tools):

| Subfeature | SLuRp | SLRTOOL | StArt | SLR-Tool |
|---|---|---|---|---|
| F1-SF01 | 3 | 3 | 3 | 3 |
| F1-SF02 | 3 | 0 | 3 | 1.5 |
| F2-SF01 | 2 | 4 | 4 | 4 |
| F2-SF02 | 0 | 1.5 | 3 | 3 |
| F2-SF03 | 3 | 3 | 3 | 1.5 |
| F2-SF04 | 0 | 0 | 1.5 | 3 |
| F2-SF05 | 1.5 | 3 | 3 | 3 |
| F3-SF01 | 0 | 0 | 1 | 2 |
| F3-SF02 | 0 | 0 | 0 | 0 |
| F3-SF03 | 0 | 0 | 1.5 | 0 |
| F3-SF04 | 1.5 | 0 | 1.5 | 1.5 |
| F3-SF05 | 3 | 1.5 | 0 | 1.5 |
| F3-SF06 | 1.5 | 1.5 | 1.5 | 1.5 |
| F3-SF07 | 1.5 | 1.5 | 1.5 | 3 |
| F3-SF08 | 1 | 0 | 1 | 0 |
| F3-SF09 | 0.5 | 0 | 0 | 0 |
| F3-SF10 | 1 | 0 | 0.5 | 0.5 |
| F3-SF11 | 0 | 0 | 0 | 0 |
| F4-SF01 | 4 | 2 | 0 | 0 |
| F4-SF02 | 4 | 2 | 2 | 2 |
| F4-SF03 | 2 | 2 | 0 | 0 |
| F4-SF04 | 3 | 0 | 0 | 0 |
| F4-SF05 | 4 | 4 | 4 | 4 |

Note: **F3-SF02 (protocol validation) and F3-SF11 (report validation) scored 0 for every tool.**

Per-tool strengths and weaknesses, verbatim:
- **SLuRp** (65.4%): "Provides full support for a team-based SR process. / Can be used for standard
  SRs as well as for mapping studies (good support for quality assessment). / Actively supported by
  its developer." Weaknesses: "its complex installation, lack of support for protocol development and
  difficulties associated with the use of the performance form." Setup requires Tomcat, MySQL, LaTeX
  and R. Two data-extraction form types: "a coding form and a performance form. The coding form
  allows the user to extract and record qualitative data about each paper. It is particularly useful
  for classification and mappings. The performance form allows users to extract more specific
  quantitative data from a study." Conflict handling: "SLuRp identifies disagreements between quality
  scores, inclusions and exclusions. To resolve disputes, SLuRp supports moderation whereby a user,
  outside of the conflict, acts as a mediator."
- **StArt** (53.3%): "Active support and maintenance by its developers. / Its simple setup
  procedure." Weaknesses: no multiple users, no quality assessment — "Since we have assigned quality
  assessment a mandatory level of importance we suggest that StArt is not yet suitable for standard
  SRs (as opposed to mapping studies)." Cannot search digital libraries directly; instead "search
  sessions" per resource+string. Text analysis: "The tool generates a 'score' for each paper. A score
  is calculated by matching keywords from a paper's title and abstract, with keywords defined in the
  protocol."
- **SLR-Tool** (53.2%): "Strong support for developing a review protocol. / Effective support
  provided to new users; notably, the ability to load an example project into the tool. / Effective
  support for automated analysis." Main weakness: "its lack of support for multiple users"; bulk
  import failed during evaluation.
- **SLRTOOL** (45.1%): "The tool has a number of promising and potential features, yet fails to
  implement them effectively. In particular, it is clear that support for collaboration, amongst
  multiple users, was a primary design objective. ... Unfortunately, SLRTOOL doesn't really allow
  users to collaborate, in any meaningful way." Its automated search "only allows informal, ad-hoc
  keyword searches of Google Scholar."

### Cross-cutting tool gaps (verbatim)

> "A number of limitations are common across all (or most) of the candidate tools. Support for
> protocol development, by most tools, is generally quite limited. Only one tool, SLR-Tool, assisted
> this stage effectively. In addition, support for the search process (a frequently stressed issue
> within the community), is largely absent. SLRTOOL is the only tool that provides an internal search
> facility (i.e. a facility within the tool for searching digital libraries). However ... its
> implementation is rather limited. Poor support for this aspect of an SR may be a consequence of the
> inherent difficulties associated with automated searching which, we suggest need to be addressed,
> before effective tool support can be realised. Support for collaboration within a team-based SR is
> also limited. Only SLuRp provides reasonably effective facilities for collaboration amongst
> multiple users. It is believed that a deeper understanding of what are considered the collaborative
> activities in an SR is needed, in order to develop effective support."

### Caveats, traps and pitfalls

- **Standard SR vs mapping study have different tool requirements** (verbatim): "SRs in SE usually
  take one of two forms. The 'standard' form, aims to address specific research questions relating to
  SE methods or procedures. The alternative form, termed a mapping study, aims to classify the
  literature on a specific SE topic. For mapping studies, the search strategy is often less stringent
  than for standard SRs and quality assessment is not usually required. We consider these slightly
  different requirements within the discussion of results."
- A missing mandatory feature is disqualifying, not merely low-scoring (quality assessment → StArt
  ruled out for standard SRs).
- **Evaluator misunderstanding is a real scoring hazard.** SLuRp's data extraction score was reduced
  because "it became clear that the lead evaluator (CM) failed to fully understand the 'performance
  form' and how to use it effectively. Although demonstrated by one of SLuRp's developers, it was
  agreed that full marks could not be justified until this feature had been properly tested."
- Two features were never fully exercised: "The performance form feature of SLuRp and 'bulk-import'
  feature of SLR-Tool were not fully evaluated."
- DESMET's scope limit: "it is not used to rank tools in terms of effectiveness, but instead to
  retrieve information on which to base a decision about a tool's suitability in a particular
  context."
- Feature set is provisional: "The features used are essentially a preliminary set based on our own
  experiences and those reported in the literature. We hope that this exercise will provide the
  foundations for further study of the features expected from an SR tool."

### Threats to validity framework

No named taxonomy; a "Limitations of the Study" section (5.2), verbatim:
> "The main threats to validity arise from the subjective nature of many of the elements of the
> feature analysis process. The features used are essentially a preliminary set ... Similarly, the
> levels of importance, both for individual features and for feature sets, are based on experience.
> However, these can easily be adjusted and weighted scores re-calculated where priorities differ. Of
> course the scoring is also subjective however as independent evaluators we have no vested interest
> in any of the candidate tools. Also, to mitigate any potential bias we performed a substantial
> validation exercise with all authors reviewing all scores for all tools."

Mitigations used, worth reusing: multi-author score validation; documented and justified score
modifications (2 for SLuRp, 4 for SLRTOOL, 5 for StArt, 3 for SLR-Tool); evaluator independence from
tool developers; adjustable weights so third parties can recompute under different priorities.

### Conclusions worth citing

> "Although the tools do not yet support the whole systematic review process they provide a good
> basis for further development. We suggest a community effort to establish a set of features that can
> inform future tool development."

> "We believe that one of its most interesting and significant outputs are the features presented in
> Table 1 ... The feature set is based on our assessment of what we believe an effective tool should
> include. The next stage is to circulate these features within the community in order to refine and
> validate them. It would also be interesting to explore SR tools in other domains to determine
> whether they could inform the development of tools in SE."

---

## Cross-paper notes for the methodology document

- **Rapid Review is a distinct study type, not a degraded SLR.** Cartaxo's Table 1 gives the
  authoritative 11-row activity-by-activity comparison; the binding invariants that survive every
  relaxation are: a documented protocol, practitioner collaboration, a real practical problem, and
  full transparency about every concession.
- **Two papers disagree, usefully, about grey literature.** Cartaxo recommends excluding grey
  literature from RRs (it would compound already-numerous threats). Kitchenham et al. permit grey
  literature in SRs but only under the Prague definition, and reclassify blog aggregation as a
  *qualitative primary study* ("survey of blogs"), not a secondary study. Wyrich et al. find 68% of
  their respondents treat podcasts as grey literature — a medium that fails the Prague test on
  preservation and lacks transcripts, so by Kitchenham's rule it is survey material, not SR input.
- **Tooling requirements trace directly to relaxation decisions.** Marshall 2014's F3/F4 features
  (independent multi-user selection, conflict reconciliation, per-reviewer quality scoring, role
  allocation) are exactly the capabilities an SLR needs and an RR is allowed to forgo — a tool
  supporting both study types must make single-reviewer mode an explicit, recorded configuration
  rather than a silent default.
- **Persistent tooling gaps as of 2014:** protocol validation and report validation scored zero
  across all four tools; automated searching was effectively absent; quality assessment was absent in
  StArt. Marshall 2013's stage map shows the same holes one year earlier (no tools at all for
  "identification of the need for a review", "development of protocol", or "study quality
  assessment").
