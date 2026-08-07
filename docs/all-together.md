# Researcher

This project is focused, currently, on automating the processes of conducting emprical reviews. The idea is that there are essentially the following types of reviews:

- Secondary Studies
  - Systematic Literature Reviews - described in `docs/methodology/01-slr.md`
    - The most rigorous with the goal of aggregating existing empirical evidence (i.e., from empirial studies such as case studies or controlled experiments).
    - Typically, these are conducted after a Systematic Mapping Study, if a significant number of high-quality empirical studies are found within the topic area. **But note the caution**: a mapping study "may miss significant numbers of relevant papers and should not be the basis for SRs without additional more focused searches".
  - Systematic Mapping Studies - described in `docs/methodology/02-sms.md`
    - A more broad approach, with the goal of understanding a research area, conducting gap analysis, and tending to have more general research questions than an SLR. While these studies do utilize the same techniques as Systematic Literature Reviews, they tend to analyze studies beyond those with higher empirical value such as case studies and experiments.
    - **Why the broader net matters**: restricting a map to methodologically rigorous papers *biases* it, because some sub-areas are easier to study empirically than others. The breadth is a correctness requirement, not a convenience. This is also why an SMS does not assess primary-study quality.
  - Rapid Reviews - described in `docs/methodology/03-rapid-review.md`
    - Defined by being **bound to a practitioner's actual problem and conducted with that practitioner**. The methodological relaxations — a single search source, single-reviewer screening, optional quality appraisal, narrative synthesis — follow from the time constraint that context imposes; they are not the defining property. Time frame is days or weeks rather than months or years.
    - Cartaxo et al. are explicit that a Rapid Review is *not* an ad-hoc literature review and *not* an excuse for absent rigour: a review conducted without practitioner collaboration and without a problem from practice is a **deviation the community should avoid**. Every methodological concession must be recorded in the protocol — "transparency is the golden standard in Rapid Reviews".
- Tertiary Studies - These studies are Systematic Literature Reviews of Systematic Literature Reviews. Described in `docs/methodology/04-tertiary.md`.
  - Typically these are conducted, when a significant number of secondary studies are found during the course of conducting a Systematic Mapping Study. The published SE examples were motivated differently — asking whether the *method* is being adopted and whether its quality is improving — and both motivations are legitimate, but they imply different research questions.
  - There is **no separate tertiary methodology**: the SLR process is applied with secondary studies as the unit of analysis. What differs in practice is that terminology dominates the search, and that **DARE** is the quality instrument because the primary studies are themselves secondary studies.

**Note**:

- Primary Studies are studies which conduct direct research and collect evidence.
- Secondary Studies are reviews of primary studies with the purpose of aggregating and synthesizing a large body of evidence related to a particular topic
- Tertiary Studies are reviews of secondary studies with a similar purpose of secondary studies but with a larger goal in mind.

# What has been implemented?

- So far, we have already implemented via the feature described in `specs/002-sms-workflow` the approaches defined in `docs/systematic-mapping-studies.md`
- What we want is to extend the existing implementation by integrating the above mentioned concepts as defined in the linked documents.
- Furthermore, we also want to also include the improvements and capabilities defined in `docs/todo.md`

Using this information, we want to construct a high-level PRD subdividing all of this work into separate feature documents written in `docs/features` which can be be provided to `speckit` in order to drive the work following spec-driven approach.
