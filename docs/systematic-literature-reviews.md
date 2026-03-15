# Systematic Literature Reviews

A systematic literature review (SLR) is a rigorous, transparent, and reproducible research method used to identify, appraise, and synthesize all high-quality evidence relevant to a specific research question. Unlike traditional reviews, it follows a planned, step-by-step protocol to minimize bias and provide comprehensive answers to focused questions.

- Conducted to "identify, analyze, and interpret all avaialbe evidence related to a specific research question"
- Aims to give a complete, comprehensive, and valid picture of existing evidence
- This must be done in a scientific and rigorous way, using the following 3-step process:
  1. Planning the review
  2. Conducting the review
  3. Reporting the review

## The Process

The following list shows each phase of the process. Each phase has a sublist containing the actions and subactions available to that phase.

- Phase 1: Planning
  - Idnetification of the need for a review
  - Specifying the review questions
  - Develop a review protocol
- Phase 2: Conduct Review
  - Identification of research
  - Selection of primary studies
  - Study quality assessment
  - Data extraction and monitoring
  - Data synthesis
- Phase 3: Reporting the Review

## Need for a Review

The need for an SLR is typically one or more of the following:

- Aiming to understand the state-of-the art in a research area
- A desire to use empirical evidence in decision-making

## Review Questions

- The area of review and the questions set the focus
- To develop appropriate questions use the PICO(C) method
  - Population: the population in which the evidence is collected, i.e., which group of people, programs, or businesses are of interest for the review?
  - Intervention: the inetervention applied in the empirical study, i.e., which technology, tool, or procedure is under study?
  - Comparison: the comparison to which the intervention is compared, i.e., how is the control treatment defined?
  - Outcomes: the outcomes of the experiment should not only be statistically significant, but also be significant from a practical point of view.
  - Context: the context of the study must be defined, which is an extended view of the population, including whether it is conducted in academia or industry, in which industry segment, and also the incentives for the subjects.
- Additionally the experimental designs to include should be noted in the research question

### Population Examples

- A specific software engineering role (i.e., testers, managers)
- A category of software engineer (i.e., novice or experienced)
- An application area (i.e, IT systems, command and control systems)
- An industry group (i.e., Telecomm companies, small IT companies)

### PICO Example

From Kitchenham et al.

- **Population**: software or web project
- **Intervention**: cross-company project effort estimation model
- **Comparison**: single-company project effort estimation model
- **Outcomes**: prediction or estimation accuracy

This led to the following questions:

1. What evidence is there that cross-company estimation models are not significantly different from within-company estimation models for predicting effort for software/web projects?
2. What characteristics of the study data sets and the data analysis methods used in the study affect the outcome of within- and cross-company effort estimation accuracy studies?
3. Which experimental procedures is most appropriate for studies comparing within- and cross-company estimation models?

## Review Protocol

- Defines the review procedures and acts as a log
- The protocol should contain:
  - Background and rationale
  - Research questions
  - Search strategy for primary studies
  - Study selection criteria
  - Study quality assessment checklists and procedures
  - Data extraction strategy
  - Synthesis of the extracted data
  - Dissemination strategy
  - Project timetable
- Ensures consistency
- Ensures validity
- You should also conduct a pre-study to
  - Scope the research questions
  - Validate the search strings
  - Validate the inclusion/exclusion criteria
- Be open to modifying the questions during protocol development
- Once finalized, you should review the protocol for validity

## Research Identification

This step focuses on the search strategies that will be used to find primary studies, which include

- Primary Study Identification
  - Manual Search
  - Database Search
- Snowball Sampling
- Grey Literature

### Manual Search

- Manual search can be conducted in the following locations:
  - Prominent Author's webpages
  - References of existing literature reviews
  - Known Conferences for the research area
  - Known Journals for the research area
- **Goal**: Obtain a representative sample of papers then conduct snowball sampling
  - The tradeoff between manual and database search is
    - Less false positives up front than with database search
    - Requires more rounds of snowball sampling
    - Underrepreentative samples lead to higher chance of missing key primary studies

### Database Search

Use when you do not have enough knowledge to conduct a manual search

- The process is as follows:
  1. Develop your search string
  2. Database selection
  3. Search execution

Note that there is always a tradeoff between:
- finding all relevant primary studies
- being overwhelmed with false positives to be removed manually

Thus, we need to calibrate our search string

### Search String

- Use the research questions to create sets of keywords
- You should have one set per item of your PICO(C) question criteria
- For each item in each set, identify applicable synonyms for each keyword and add to the set
- Build a Boolean search string from the selected keywords
  - **OR** together keywords within a set
  - surround sets with parentheses
  - **AND** together the sets
- If necessary, refine the expression to improve your results
- You should analyze the sensitivity of the results of your search to refine the search string

#### Search String Examples

From Kitchenham et al.

- **Population**: software or web project
- **Intervention**: cross-company project effort estimation model
- **Comparison**: single-company project effort estimation model
- **Outcomes**: prediction or estimation accuracy

Leads to the following search strings:

- **Population**: `software OR application OR product OR web OR www OR Internet OR World-Wide Web OR project OR development`
- **Intervention**: `cross company OR cross organization OR cross organisation OR multiple-organizational OR multiple-organizational model OR modeling OR modeling effort OR cost OR resource estimation OR prediction OR assessment`
- **Comparison**: `within-organization OR within-organizsation OR within-organizational OR within-organisational OR single company or single organization`
- **Outcome**: `accuracy OR mean magnitutde relative error`

The final search string becomes:

```
(software OR application OR product OR web OR www OR Internet OR World-Wide Web OR project OR development)
AND (cross company OR cross organization OR cross organisation OR multiple-organizational OR multiple-organizational model OR modeling OR modeling effort OR cost OR resource estimation OR prediction OR assessment)
AND (within-organization OR within-organizsation OR within-organizational OR within-organisational OR single company or single organization)
AND (accuracy OR mean magnitutde relative error)
```

### Database Selection

- A single database is usually not enough to identify your primary studies
- Using multiple databases will inevitably result in duplicates, but a greater sample of the population as well.
- For CS/SE/AI Studies you should use at least the following:
  - IEEExplore
  - ACM Digital Library
- You should use 2 or more general indices such as:
  - INSPEC/Compendex
  - Web of Science
  - Scopus
- Additionally, you can use the following indices:
  - ScienceDirect
  - SpringerLink
- **Do NOT use Google Scholar** since the results are not replicable
- Realize: you cannot find all primary studies for a given topic, and that what is found is simply a sample

### Search Execution

- Keep a detailed record of the search findings
  - Number found
  - Included studies
  - Excluded studies
  - Duplicate studies

**When to Stop Searching**
- Search is a time-consuming process, and we will never be able to find all of the papers
- To save time, adopt a search stoppage criteria (and don't forget to note them in the report)
  - If using database and another complementary search (manual or snowball sampling)
    - Stop when the man ual or snowball sampling does not return more than a certain number of studies (i.e., < 4 new studies added to the list of primary studies)
  - Use a time budget (based on fundign or time constraints) and create a list of reviewed studies and a list of not considered studies

### Snowball Sampling

- Snowball sampling is simply a manual search for primary studies based on a selection of identified primary studies.
- There are two types of snowball sampling:
  - **Backward Snowball Sampling**:
    - Search the references of a primary study for new primary studies
    - Can be done either by:
      - Search actual paper reference sections, or
      - Searching through listed references on online paper citation sites/databases
  - **Forward Snowball Sampling**:
    - Search the items citing a primary study for new primary studies
    - Can be done either by:
      - Using Google scholar cited-by listings
      - Using "Citations" section of paper listing in databases/indices
- After each round, you will need to apply inclusion/exclusion criteria
- This process continues until no new studies are added

### Primary Study Selection

- Primary studies are selected based on a set of well-defined inclusion/exclusion criteria
  - These need to be defined before the earch is conducted to reduce bias
- To reduce threats to validity it is wise to have more than one reviewer
  - Because selection is based on researcher judgement, you need to address this
  - After all researchers have made their assessments
    - Measure the **inter-rater agreement** with **Cohen's Kappa**
    - Use the **Think-Aloud technique** to attempt to come to a consensus
    - Measure the inter-rater agreement again
    - Report all of this in the final report
- Studies are selected based on research judgement and the application of inclusion/exclusion criteria
- Reducing the search results to the set of primary studies should be done in an iterative fashion
  - Start by removing those studies which can easily be excluded by their title or abstract alone
  - Next, expand to those studies which can be excluded by their introduction and conclusions
  - The remainin studies should be thoroughly reviewed by a full-text reading
- At anytime during this process, papers should only be removed when agreement between reviewers is made
- Remove any papers with more than one version (conference and journal) keeping only the most recent version

### Inclusion and Exclusion Criteria

- We need to define inclusion/exclusion criteria to select our primary studies
  - The relevance of the topic of the article -> does it answer the research questions
  - The venue of publication and type of publication
  - The time period considered (typically 10 years, usually excluding the current partial year)
  - Requirements on evaluation (avoid if research has not yet reached maturation for evaluation)
  - Restrictions with respect to publication language

#### Inclusion/Exclusion Criteria Examples

**Inclusion Criteria**

- "English peer-reviewed articles in conferences or journals published until Dec. 2025"
- "Aritcles that focus on software project lines"
- "Articles that provide some type of evolution of existing software artifacts, included among the terms selected"
- "Context, objectives, and research methods are reasonably present"

**Exclusion Criteria**

- "Articles that are not related to software product lines"
- "Articles that doe not imply evolution of any software artifact"
- "Non-peer reviewed publication"
- "Articles that are not written in English"
- "Context, objectsives, or research method are manifestly missing"

### Publication Bias

- There is a bias associated with published primary studies
  - They typically focus on positive results and discount negative results

- To overcome this bias you should consider grey literature
  - Technical Reports
  - Dissertations and Theses
  - Rejected Publications
  - Works in progress

### Study Quality Assessment

- Primary study quality is important as it
  - Can be used to analyze cause of contradicting results
  - Can be used in weighting the value of evidence from primary studies
- We measure quality through the use of checklists, several of which have been published
- Note that the quality of the study not the reporting are to be evaluated

### Data Extraction

- After primary studies are selected, data is extracted
- A form for data collection should be developed from research questions
  - Expedites data collection
  - Increases reliability of data collection
- You should conduct a small data extraction using your forms on a subset of studies to validate the form

### Data Synthesis

There are several approaches to synthesize the data from a literature review

- Meta-analysis
- Descriptive synthesis
- Qualitative approaches for inhomogenous and mixed-method studies

Independent of approach used, a sensitivity analysis should take place

- Analyzes whether results are consistent across different subsets

#### Meta-Analysis

- Most advanced and most constrained
- Assumptions
  - primary studies are homogenous - same type, same hypotheses, same measure, report on same explanatory factors
  - or cause of in-homogeneity is known
- Compares **effect sizes** and **p** values to assess synthesized outcome
- Primarilyh applicable to replication studies
- Studies to be included in a meta-analysis must:
  - Be of the same type, for example, formal experiments
  - Have the same test hypothesis
  - Have the same measures of the treatment and effect constructs
  - Report the same explanatory factors
- Process
  1. Decide which studies to include in the meta-analysis
  2. Extract the effect size from the primary study report, or estimate if there is no effect size published
  3. Combine the effect sizes from the primary studies to estimate and test the combined effect
- In addition to the procedures noted
  - Include an analysis of **publication bias**
    - Funnel plots - where observed effect sizes are plotted against measure of study size (inverse of variance or other dispersion measure)
- Effect size (i.e., difference between mean values) for each study
  - normalize between studies by dividing by combined standard deviation
- Statistical evaluation
  1. Determine homogeneity by evaluating heterogeneity using either the **Q test** or **Likelihood Ratio test**
  2. Homogenous studies use a fixed-effects model
  3. Inhomogenous studies use a random effects model

#### Descriptive Synthesis

- tabulates data from the primary studies to shed light on the research questions
- tabulated data should contain the following, at a minimum
  - Sample size for each intervention
  - Estimates of effect size for each intervention (with standard errors)
  - Difference between mean values for each intervention
  - Confidence interval for the differences
  - Units used for measuring the effect
- Forest plot can visualize
  - means of differences between treatments of each study
  - variance of difference between treatments of each study

#### Qualitative Approaches

- **Thematic analysis** - aims at identifying, analyzing and reporting patterns or themes in the primary studies. At a minimum, it organizes and presents the data in rich detail, and interprets various aspects of the stopic under study.
- **Narrative synthesis** - tells the story originating from the primary evidence
- **Comparative analysis** - aims at analyzing complex causal connections. It uses Boolean logic to explain relations between cause and effect in the primary studies.
- **Case survey** - aggregates existing research by applying a survey instrument of specific questions to each primary study. The data from the survey is quantitative and is aggregated using statistical methods.
- **Meta-ethonography** - translates studies into one another, and synthesizes the translations into concepts beyond the individual studies. The data is the interpretations and explanations in the primary studies.
- **Meta-Analysis** - can use statistical methods to integrate quantitative data from several cases

## Document Review

### Reporting the Review

The results of your research should be published where your intended audience can review it

**Practitioner Oriented**
1. Practitioner Journals and Magazines
2. Press Releases to popular or specialist press
3. Short summary leaflets
4. Posters
5. Websites
6. Direct communication

**Academia**
1. Academic Journals
2. Academic Conferences
- If publication constraints prevent providing necessary detail for replication, write an accompanying Tech Report which can be posted online

## References

- Chapter 4 of "Experimentation in Software Engineering" 2nd Edition by Wohlin et al.
- Kitchenham and Charters, "Guidelines for performing Systematic Literature Reviews in Software Engineering", version 2.3
