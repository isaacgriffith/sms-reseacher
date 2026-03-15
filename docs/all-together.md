# Researcher

This project is focused, currently, on automating the processes of conducting emprical reviews. The idea is that there are essentially the following types of reviews:

- Secondary Studies
  - Systematic Literature Reviews - described in `docs/systematic-literature-review.md`
    - The most rigorous with the goal of aggregating existing empirical evidence (i.e., from empirial studies such as case studies or controlled experiments).
    - Typically, these are conducted after a Systematic Mapping Study, if a significant number of high-quality empirical studies are found within the topic area.
  - Systematic Mapping Studies - described in `docs/systematic-mapping-studies.md`
    - A more broad approach, with the goal of understanding a research area, conducting gap analysis, and tending to have more general research questions than an SLR. While these studies do utilize the same techniques as Systematic Literature Reviews, they tend to analyze studies beyond those with higher empirical value such as case studies and experiments.
  - Rapid Reviews - described in `docs/rapid-reviews.md`
    - The least rigorous of the three, in that these tend to have more restrictive context and timeframes, leading to a more relaxed protocol.
- Tertiary Studies - These studies are Systematic Literature Reviews of Systematic Literature Reviews.
  - Typically these are conducted, when a significant number of secondary studies are found during the course of conducting a Systematic Mapping Study.

**Note**:
- Primary Studies are studies which conduct direct research and collect evidence.
- Secondary Studies are reviews of primary studies with the purpose of aggregating and synthesizing a large body of evidence related to a particular topic
- Tertiary Studies are reviews of secondary studies with a similar purpose of secondary studies but with a larger goal in mind.

# What has been implemented?

- So far, we have already implemented via the feature described in `specs/002-sms-workflow` the approaches defined in `docs/systematic-mapping-studies.md`
- What we want is to extend the existing implementation by integrating the above mentioned concepts as defined in the linked documents.
- Furthermore, we also want to also include the improvements and capabilities defined in `docs/todo.md`

Using this information, we want to construct a high-level PRD subdividing all of this work into separate feature documents written in `docs/features` which can be be provided to `speckit` in order to drive the work following spec-driven approach.