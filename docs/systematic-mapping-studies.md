# Systematic Mapping Studies

The purpose of a Systematic Mapping Study is to provide a researcher a broad understanding of the research that has taken place within a specific field or topic of interest. The challenge of this type of study is that it is very time consuming to execute. However, a significant amount of this work can be automated with AI Agents. While the goal of the system as a whole is to provide automation across Systematic Mapping Studies, Systematic Literature Reviews, Rapid Reviews, and Tertiary Studies, we want to begin with the Systematic Mapping Study first.

The following describes the extent of my knowledge regarding Systematic Mapping Studies.

## The Process

The following list shows each phase of the process. Each phase has a sublist containing the actions and subactions available to that phase.

- Phase 1: Need for Map
  - Motivate the need and relevance
  - Define objectives and questions
  - Consult with target audience to define questions
- Phase 2: Study Identification
  - Choose search strategy
    - Snowball Sampling
    - Manual Search
    - Database Search
  - Develop the Search
    - PICO(C)
    - Consult librarians or experets
    - Search web-pages of key authors
    - Keywords from known papers
    - Use standards, encyclopedias, and thesaurus
  - Evaluate the search
    - Test-set of known papers
    - Expert evaluates result
    - Test-retest
    - Iteratively try finding more relevant papers
  - Inclusion and Exclusion
  - Decision rules
    - Identify objective criteria for decisions
    - Add aditional reviewer, resolve disagreements between them when needed
- Phase 3: Data Extraction and Classification
  - Identify objective criteria for decision
    - Obscurring information that could bias
    - Add aditional reviewer, resolve disagreements between them when needed
    - Test-retest
  - Domain Modelling
  - Classification Scheme
  - Research type
  - Research method
  - Venue type
- Phase 4: Validity Discussion
  - Validity discussion/limitations provided
- Phase 5: Quality Evaluation

## Phase 1: Need for the Map

### Need Identification and Scoping

Typical research goals for mapping studies:

- To examine the extent, range and nature of research activity.
  - In software engineering, this may refer to the extent different practices are studied and reported in literature
- To determine the value of undertaking a full systematic review
  - Systematic maps may lead the researcher to find existing systematic reviews. In addition, when classifying papers we often distinguish between evaluated or validated research and solution proposals. Identifying evaluation and validation research studies provides the set of studies to continue further investigation on in the form of a systematic review. Also the structuring of the area helps in refining research questions for the conduct of future systematic reviews. They may also be used to determine the potential effort of a full systematic review
- To summarize and disseminate research findings
  - Systematic maps give a comprehensive overview over the area and can also be used as an inventory for papers. Specifically, graduate students may find them useful to orient themselves in a new area early during their Ph.D. studies.
- To identify research gaps in the existing literature
  - Based on the categorization areas, with very few studies or lack of evaluations, the need for future research becomes apparent. In case there are only very few studies in a category, those can be investigated in more depth to see whether they are solving the problem in that category.

Systematic Mapping Study research questions are less specific than in systematic reviews. These questions are about what we know with respect to a specified topic. Often these higher-level questions can be further broken down to drive data extraction.

Examples of Systematic Mapping Study Research Questions:

- What do we know about software product management?
  - What research questions in software product management are being addressed?
  - What original research exists in the intersection of software product management and cloud (service) environment?
  - "What areas in software product management require more research?

- What are existing approaches that combine static and dynamic quality assurance techniques and how can they be classified?

- In which sources and in which years were approaches regarding the combination of static and dynamic quality assurance techniques published?

- Is any kind of evidence presented with respect to the combination of quality assurance techniques and if so, which kind of evidence is given?

## Phase 2: Study Identification

### Choose Search Strategy

- **Database Search**: In this strategy, a search string is developed which can then be applied to one or more research indices and search engines to find papers. Research indices (or databases) of interest to computer science include the following:
  - Infospec/Compendex
  - IEEExplore
  - ACM Digital Library
  - Scopus
  - Web of Science

- **Manual Search**: In this strategy, a search of conference websites, journal sites, special interest websites, author websites, etc. is conducted to find relevent papers of interest.

- **Snowball Sampling**: In this strategy, a set of known papers is used as a baseline. From these papers additional papers are identified using one or both of the following:
  - *Forward Snowball Sampling*: In this approach, tools/websites which capture papers citing a paper are used to find papers that refer to a given paper. These papers, if not duplicates, are then reviewed for relevancy, and the process continues until no additional new papers are found meeting the inclusion/exclusion criteria (or when a round produces less than a specified threshold of new papers).
  - *Backward Snowball Sampling*: In this approach, a papers references list or tools/websites which catalog references of a paper are used to find papers cited by a given paper. These papers, if not duplicates, are then reviewed for relevancy and year of publication, and the process continues until no additional new papers are found meeting the inclusion/exclusion criteria (or when a round produces less than a specified threshold of new papers).

  **Note**: Snowball Sampling should be combined with either Manual or Database search to find papers missed by the initial search.

### Develop the Search

#### PICO(C)

PICO(C) (Population, Intervention, Comparison, Outcome, Context) is a structured framework used to formulate precise, answerable research questions for systematic reviews, improving search precision and efficiency. It helps define inclusion/exclusion criteria and identify keywords for databases.

##### Key Components of PICO for Systematic Reviews
* P - Population/Problem: In software engineering experiments, the populations might be any of the following:
    - A specific software engineering role e.g., testers, managers.
    - A category of software engineer, e.g., a novice or experienced engineer.
    - An application area e.g., IT systems, command and control systems.
    - An industry group such as Telecommunications companies, or Small IT companies
    A question may refer to very specific population groups e.g., novice testers, or experienced software architects working on IT systems.

* I - Intervention/Exposure: The intervention is the software methodology/tool/technology/procedure that addresses a specific issue, for example, technologies to perform specific stasks such as requirements specification, system testing, or software cost estimation.

* C - Comparison/Control: This is the software engineering methodology/tool/technology/procedure with which the intervention is being compared. When the comparison technology is the conventional or commonly-used technology, it is often referred to as the "control" treatment. The control situation must be adequately described. In particular "not using the intervention" is inadequate as a description of the control treatment. Software engineering techniques usually require training. If you compare people using a technique with people not using a technique, the effect of the technique is confounded with the effect of training. That is, any effect might be due to providing training not the specific technique. This is a particular problem if the participants are students.

* O - Outcome(s): Outcomes shoudl relate to factors of importance to practitioners such as improved reliability, reduced production costs and reduced time to market. All relevant outcomes should be specified. For example, in some cases we require interventions that imporve some aspect of software production without affecting another e.g., improved reliability with no increase in cost. A pariticluar problem for software engineering experiment sis the widespread use of surrogate measures for example, defects found during system testing as a surrogate for quality, or coupling measures for design quality. Studies that use surrogate measures may be misleading and conclusions based on such studies may be less robust.

* C - Context: For software Engineering, this is the context in whihc the comparison takes place (e.g., academia or industry), the participants taking part in the study (e.g., practitioners, academics, consultants, students), and the tasks being performed (e.g., small scale, large scale). Many software experiments take place in academia using student participants and small scale tasks. Such experiments are unlikely to be representative of what might occur with practitioners working in industry. Some systematic reviews might choose to exclude such experiments althrough in software engineering, these may be the only type of studies available.

##### Application in Systematic Reviews
- Developing Search Strategies: PICO terms are used to generate search queries using Boolean operators (AND/OR).
- Defining Eligibility: Helps in drafting inclusion and exclusion criteria to select relevant studies.
- Data Extraction: Structures the extraction of data to ensure all relevant information is captured. 

##### Common PICO Variations
- PICOS: Includes "Study Design" for restricting to specific research methods.
- PICOT: Adds "Time" to define the study duration.
- SPIDER: Often used for qualitative or mixed-methods reviews (Sample, Phenomenon of Interest, Design, Evaluation, Research type).
- PCC: Used for scoping reviews (Population, Concept, Context). 

Using PICO leads to more specific, relevant results compared to broader, unstructured searches.

The frontend should provide the ability to select versions of PICO to use, and then allow the specification of the components of PICO. It should allow for refinement using AI, and when ready allow the user to save this as part of the Study in the database.

#### Consult Librarians or Experts

- The idea here is that we should consult known Human experts for their help in refining the motivation, topic, objectives, and research questions.
- Additionally, these experts and librarians can be utilized to help identify the key papers, key authors, and research groups working in the area.
- For the purposes of this work, it would be helpful to provide the opportunity to allow the user of the system to edit or provide the following:
  - Edit the motivation, topic, objectives, and research questions for a given Study
  - Provide known key papers to "seed" the study
  - Provide a list of known author's to "seed" the study
- Additionally, the system should be capable of providing a "Librarian" agent which is an expert in finding key research papers, authors, and research groups to "seed" the study.
- Additionally, the system should be capable of providing an "Expert" agent which is capable of expertly (without hallucination) identify a small set of 10-20 papers relevant to the research topic.

#### Keywords from Known Papers

The usefulness of finding known papers is that they can provide initial keywords that can be used to build a search string. Regardless of how the papers are found/provided, we will need an agent that can process the papers and extract keywords out.

#### Use standards, encyclopedias, and thesaurus

The idea here is to utilize PICO(C), Keywords from other papers, and Opinions from experts to construct the Logical Search String. With the initial search string defined, it will need to be improved to include additional keywords based on known standards, encyclopedia entries, and thesaurus entries in order to broaden the search string capabilities.

### Evaluate the Search

The purpose here is to evaluate the search string and determine if it is refined enough to be used for the full study.

The evaluation requires that a **Test Set** of known key papers exists. This should be provided as a result of `Phase 1`.

#### Search Evaluation Process

1. Using the PICO(C), librarian/expert data, and keywords for known papers -> generate a search string.
2. Execute the Search String across each Research Database and collect the results -> `Result Set`
3. Compare the `Result Set` to the `Test Set`, the goal is that the `Result Set` should include most or all of the `Test Set`, but also include enough a significantly large enough set of papers to ensure most relevant papers are included. Thus, we are attempting to minimize the size of the `Result Set` while also minimizing the amount of Snowball Sampling required later and ensuring high relevancy of papers found by the search string -> `Comparison Results`
4. If the `Comparison Results` have been deemed adequate by expert judgement, then the search string can be applied to the study; otherwise, the `Search String` is refined to address the issues in the `Comparison Results` and the process starts over at Step 2 with the refined Search String. This loop is the `Test-retest` process.

### Inclusion/Exclusion Criteria

As part of the UI and Data Model, we need the ability to specify the inclusion and exclusion criteria for a paper.

**Examples of Inclusion Criteria**:

- English peer-reviewed aritcles in conferences or journals published since 2011
- Articles that focus on software product lines
- Articles that provide some type of evolution of existing softwar eartifacts, included among the terms selected
- Context, objectives, and research method are reasonably present

**Examples of Exclusion Criteria**:

- Articles that are not related to software product lines
- Articles that do not imply evolution of any software artifacts
- Non-peer reviewed publications
- Articles that are not written in English
- Context, objectives, or research method are manifestly missing

The basic idea is that the criteria need to refer to:
- the relevance of the topic of the article
- the venue of publication
- the time period considered
- requirements on evaluation (should be avoided for systematic mapping studies if the goal is to see recent trends that have not reached the maturity for evaluation yet)
- restrictions with respect to language

### Paper Search

- As part of an academically rigorous study, the study must be replicable. Thus, we need the ability to track the creation of and results from a search.
- This means that we need the ability to generate a search string that can be used against selected indices.
- We should be able to specify indices such as ACM Digital Library, IEEExplore, Web of Science, Scopus, ScienceDirect (Elsevier), Google Scholar. These shold be provided by MCP (either external or the internal `researcher-mcp`)
- Additionally, beyond traditional index search, we should be able to search through journals for a specified period or search author's websites to find papers.
- Finally, as part of the search the process will use selected papers (passing the inclusion/exclusion criteria) should be capable of conducting backward and forward snowball search from those papers. The results of which will be processed.

### Tracking Progress

- Every paper found during the search process must be evaluated, it is to be evaluated and marked as one of the following:
  - **A** - Accepted, this paper meets all inclusion/exclusion criteria and is relevant to the topic at hand.
  - **R** - Rejected, this paper does not meet the inclusion/exclusion criteria, or it is not relevant to the topic at hand.
  - **D** - Duplicate, this paper is a duplicate of an already identified paper.

### Essential Search Processes

The search process should work as follows:

#### Index Based Approach:
1. Generate Search String based on PICOC Criteria
2. Work with the User to refine the search string
   - This includes conducting initial searches and comparing the results of the search with known papers.
   - Goal is to find a "happy medium" in size of search results such that the initial results find a significant number of key papers, and the remaining papers can be found using a limited number of snowball rounds
3. Conduct initial search, collecting results from all indices. All key paper metadata should be collected, including Author information and key institutions of the authors
   - Check each paper to determine if it is a duplicate
   - If not a duplicate, add to the list of candidate papers
   - Each paper found is then evaluated to determine if it meets the inclusion/exclusion criteria. Any exclusion criterion met immediately rejects the paper. If the paper meets all inclusion criteria and no exclusion criteria, then it is to be evaluated for relevance. If the paper is determined to be relevant to the study, it is marked as `Accepted`, otherwise it is marked as `Rejected`, along with the reasons.
   - Additionally papers are to be evaluated to determine the type of paper (which may also be an inclusion/exclusion criteria)
   - All decisions and reasons must be logged in the database. Additionally, the phase of the search must be marked as well.
4. For all papers marked as `Accepted`, a backward and forward snowballing cycle is started (in parallel).
   - Backward snowballing uses the paper's references to find additional papers that may be relevant. Each backward snowball cycle is to be marked as `backward-search-X` where `X` is the number of the cycle starting at `1`
   - Forward snowballing uses the paper's citations to find additional papers that may be relevant. Each forward snowball cycle is to be marked as `forward-search-X` where `X` is the number of the cycle starting at `1`
   - Each paper identified is placed into the candidate paper queue, marked by the cycle in which it was found.
5. The candidate papers are evaluated, using the process in step 3. The process continues at step 4 until backward and forward snowballing no longer finds enough papers to continue. What this means is that the backward/forward snowballing process will continue until the number of non-duplicated papers found no-longer surpasses a threshold number of papers (e.g., 5). The exact threshold can be configured as part of a study's configuration.

#### Web-scraping Based Approach:
Similar to the Index Based Approach, but instead uses the PICOC Criteria to determine relevance. Steps 1 and 2 become the following:

1. Generate relevance criteria from the Study's PICOC criteria.
2. Identify key author's, jounrnal's, and paper collecting sites for the topic. Scrape these sites for potentially relevant papers.

Steps 3 - 5 are the same as in the Index-Based Approach.

#### The Funnel

1. Start by applying search method (i.e., index search, manual search (web scraping)) -> Initial Results
2. Remove from initial results any papers published before study cutoff date -> Cutoff results (should be less than initial results), track the number removed.
3. Apply inclusion/exclusion criteria to cutoff results -> Inc/Exc Results, track nubmer removed (should be less than cutoff results), track number removed
4. Peform a full-text reading on each paper in Inc/Exc results to determine relevance to the study -> Reading Results (should be less than Inc/Exc Results), track number removed
5. Perform Snowball Sampling on Reading Results to find additional papers (will require multiple rounds, where the results of each round (forward and backward) should be process through steps 2 - 5, until no new results found, the final set is then combined with Reading Results) -> Snowball Results (should be greater than Reading Results), track number of non-duplicates added.
6. Assess the quality of the papers in Snowball Results, removing any low quality publications -> Quality Results (should be less than Snowball Results), track number removed
7. Finally, review all excluded articles to determine if any should be included -> Review Results (should be greater than or equal to Review Results), track any additions
   - Note that quality assessment should not pose high requirements on the primary studies, as the goal of mapping is to give a broad overview of the topic area.

### Search Metrics

- Each phase of the search must keep, at a minimum, the following counts
  - Total Number of Papers Identified
  - Number of Accepted Papers
  - Number of Rejected Papers
  - Number of Duplicated Papers

## Phase 3: Data Extraction

The purpose of data extraction for a Systematic Mapping Study is to extract information from each paper in order to pull together a broad overview of the research topic/field.

Towards this, we want to start by classifying each paper by the following:
- Type of paper
- Type of research
- Venue of Publication and Venue Type
- Key Authors and Research Group
- Author Institution/Locale

Once this information is extracted, we also want to extract infromation from the paper for the following:
- Extract a summary of the paper that presents those conducting the study with a good idea of the work the paper presents, its findings, gaps, and next steps
- Additionally, we want to extract keywords related back to the topic/field. The goal of this is to essentially extract codings such as done in Grounded Theory. These codings and relationships between the codings will be used when extracting the Domain Model and Classification Scheme
- Extract information related to the Research Goals/Questions posed for the study

### Venue Type Classification

- **Peer-Reviewed**
  - Journal aritcle (refereed), orignal
  - Review article, literature review, systematic review
  - Book section, chapters in research books
  - Conference proceedings
- **Non-refereed**
  - Non-refereed journal articles
  - Book sections
  - Non-refereed conference proceedings
  - Scientific books
  - Book
  - Edited book, conference proceedings, or special issue
- **Professional Communities**
  - Trade journal
  - Articles in professional manuals
  - Professional proceedings
  - Published development or research report
- **General public**
  - Popularized article, newspaper
  - Popularized monograph
- **Thesis**
  - Bachelor of Science
  - Master of Science
  - License/Master of Philosophy
  - Doctoral Dissertation
- **Public artistic and design activity**
  - Published individual work of art
  - Public parital realization of art
- **Audiovisual material, software**
  - Audiovisual material
  - ICT software
- **Patents**
  - Granted patent
  - Invention disclosure

### Research Classification

Papres can be classified into several broad classifications:

- **Evaluation Research**: The investigation of a problem in practice or an implementation of a technique in practice. If it reports on the use of a technique in practice, then the novelty of the technique is not a criterion byt which the paper should be evaluated. Rather, novelty of the *knowledge claim* made by the paper is a relevant criterion, as is the soundness of the research method used. In general, research results in new knowledge of causal relationships among phenomena, or in knew knowledge of logical relationships among propositions. Causal properties are studied empirically, such as by case study, field study, field experiment, survey, etc. Logical properties are studied by conceptual means, such as by mathematics or lgoic. Whatever the method of study, it should support the conclusions stated in the paper.
  - Evaluation Criteria:
    - Is the problem clearly stated?
    - Are the causal or logical properties of the problem clearly stated?
    - Is the research method sound?
    - Is the knowledge claim validated? In other words, is the conclusion supported by the paper?
    - Is this a significant increase of knowledge of these situations? In other words, are the lessons learned interesting?
    - Is there sufficient discussion of related work?
  - Subtypes:
    - Industrial Case Study
    - Controlled experimetn with practitioners
    - Practitioner targed survey
    - Action research
    - Ethnography
- **Proposal of Solution**: This paper proposes a solution technique and argues for its relevance, without a full-blown validation. The technique must be novel, or at least a significant improvement of an existing technique. A proof-of-concept may be offered by means oof a small example, a sound argument, or by some other means.
  - Evaluation Criteria:
    - Is the problem to be solved by the technique clearly explained?
    - Is the technique novel, or is the application of the techniques to this kind of problem novel?
    - Is the technique sufficiently well described so that the author or others can validate it in later research?
    - Is the technique sound?
    - Is the broader relevance of this novel technique argued?
    - Is there sufficient discussion of related work? In other words, are competing techniques discussed and compared with this one?
- **Validation Research**: This paper investigates the properties of a solution proposal that has not yet been implemented in practice. The solution may have been proposed elsewhere, by the author or by someone else. The investigation uses a thorough, methodologically sound research setup. Possible research methods are experiments, simulation, prototyping, mathematical analysis, mathematical proof of properties, etc.
  - Evaluation Criteria:
    - Is the technique to be validated clearly describe?
    - Are the causal or logical properties of the technique clearly stated?
    - Is the research method sound?
    - Is the knowledge claim validated (i.e., is the conclusion supported by the paper)?
    - Is it clear under which circumstances the technique has the stated properties?
    - Is this a significant increase in knowledge about this technique?
    - Is there sufficient discussion of related work?
  - Subtypes:
    - Simulation as an empirical method
    - Laboratory experiments (machine or human)
    - Prototyping
    - Mathematical analysis and proof of properties
    - Academic case study (e.g., with students)
- **Philosophical Papers**: These papers sketch a new way of looking at things, a new conceptual framework, etc.
  - Evaluation Criteria:
    - Is the conceputal framework original?
    - Is it sound?
    - Is the framework insightful?
- **Opinion Papers**: These papers contain the author's opinion about what is wrong or good about something, how we should do something, etc.
  - Evaluation Criteria:
    - Is the stated position sound?
    - Is the opinion surprising?
    - Is it likely to provoke discussion?
- **Personal Experience Papers**: In these papers, the emphasis is on *what* and not on *why*. The experience may concern one project or more, but it must be the author's personal experience. The paper should contain a list of lessons learned by the author from his or her experience. Papers in this category will often come from industry practitiones or from researchers who have used their tools in practice, and the experience will be reported without a discussion of research methods. The evidence presented in the paper can be anecdotal.
  - Evaluation Criteria:
    - Is the experience original?
    - Is the report about it sound?
    - Is the report revealing?
    - Is the report relevant for practitioners?

### Decision Rules for Research Type Classification

- R1: Used in Practice AND Empirical Evaluation AND NOT Opinion about something THEN Evaluation Research
- R2: Novel Solution AND NOT Empirical Evaluation AND NOT Opinion About Something THEN Solution Proposal
- R3: Used In Practice AND NOT Novel Solution AND NOT Empirical Evaluation AND NOT Opinion about something AND Author's Experience THEN Experience Paper
- R4: NOT Used in practice AND Empirical Evaluation AND NOT Opinion about something THEN Validation Research
- R5: NOT Used in practice AND NOT Novel Solution AND NOT Empirical Evaluation AND Conceptual framework AND NOT Opinion about something AND NOT Author's experience THEN Philosophical Paper
- R6: NOT Used in practice AND NOT Novel Solution AND NOT Empirical Evaluation AND NOT Conceptual framework AND Opinion about something AND NOT Author's experience THEN Opinion Paper

### Venue

- Extract from the article the venue in which the article was published
- Extract from the article the authors information including the institute and locale where the author was at the time of publication
- Identify the venu type based on the **Venue Type Classification** above

### Domain Modelling

Using the Open Coding, Relationships, Keywords, and Summaries of papers, we want to construct a domain model (using UML) to describe the key concepts and their relationships across the body of knowledge represented by the papers.

### Classification Scheme

Using the Open Coding, Keywords, and Summaries of papers. We want to create bubble charts classifying the research according to the results of the questions, by venue, by author, by locale, by institute, by year of publication, by area/subtopic, by research type, and by research method. The goal is to produce publication ready SVG visualizations of this data.

## Phase 4: Validity Discussion

### Descriptive Validity

Validity evaluating the extent to which observations are described accurately and objectively. This threat can be reduced by utilizing a JSON data structure representing a form for data collection. Furthermore, while an Agent will be used to extract the data, it will then be evaluated by a second Agent, and finally a Human Expert will review the final results.

### Theoretical Validity

Maps to Construct Validity. That is, does the study capture what was intended to be captured. Here bias and selection of subjects plays an important role.

Threats to validity here for Systematic Mapping Studies include the fact that during the search papers could have been missed. Thus, two studies conducted could return different final result sets. To mitigate this, snowball sampling should be used after full-text reading.

Additionally, there is a threat due to researcher bias during the data extraction and classification phase. This can be mitigated by using an Agent for extraction, while another Agent evaluates the results of extraction.

### Generalizability

Maps to both internal and externa validity.

- Internal Validity: generalizability within a group.
- External Validity: generalizability between groups or organizations.

### Interpretive Validity

Maps to Conclusion Validity, essentially how reasonable are the conclusion given the data collected. Threats to this include research bias and interpretation bias.

### Repeatability

An analysis of how repeatable the study is.

## Phase 5: Study Quality Evaluation

The following rubrics have been developed to evaluate the quality of a Systematic Mapping Study. The goal of this is to encode these rubrics into an LLM-as-a-Judge Agent which will evaluate the study as it currently exists. The judge should then propose actions that can be taken to improve the study's quality and allow the user to direct the system as needed.

### Rubric: Need for Review

| Evaluation | Description | Score |
|------------|-------------|-------|
| No description | The study is not motivated and the goal is not stated | 0 |
| Partial evaluation | Motivations and questions are provided | 1 |
| Full evaluation | Motivations and questions are provided and have been defined in correspondence with target audience | 2 |

### Rubric: Choosing the search strategy

| Evaluation | Description | Score |
|------------|-------------|-------|
| No description | Only one type of search has been conducted | 0 |
| Minimal evaluation | Two search strategies have been used | 1 |
| Full evaluation | All three search strategies have been used | 2 |

### Rubric: Evaluation of the search

| Evaluation | Description | Score |
|------------|-------------|-------|
| No description | No actions have been reported to improve the reliability of the search and inclusion/exclusion | 0 |
| At least one action has been taken to improve the reliability of the search xor the reliability of the inclusion/exclusion | 1 |
| Partial evaluation | At least one action has been taken to improve the reliability of the search and the inclusion/exclusion | 2 |
| Full evaluation | All actions identified have been taken | 3 |

### Rubric: Extraction and classification

| Evaluation | Description | Score |
|------------|-------------|-------|
| No description | No actions have been reported to improve on the extraction process or enable comparability between studies through the use of existing classifications | 0 |
| Minimal evaluation | At least one action has been taken to increase the reliability of the extraction process | 1 |
| Partial evaluation | At least one action has been taken to increase the reliability of the extration process, and research type and method have been classified | 2 |
| Full evaluation | All actions identified have been taken | 3 |

### Rubric: Study validity

| Evaluation | Description | Score |
|------------|-------------|-------|
| No description | No threats or limitations are described | 0 |
| Full evaluation | Threats and limitations are described | 1 |

## Results

### Mapping Studies

- Frequency of Publication (Infographic)
- Publications per Year (Barchart)
- Venues of Publication
- Research Locale
- Key Authors
- Extracted Keywords Bubble Map to answer questions
- Domain Model to answer questions

# UX Requirements

The User Experience will need the following, if not already present:

- A Login page, which has the login form on the left 1/3 of the page, centered vertically. The remaining 2/3 of the page should show a infographic related to the product. Login should be maintained as part of the user session, thus if the user enters the "/" route they reach the actual content if already logged in, or will be redirected to the login page (this latter action occurs for all pages when not logged in)

- Studies, are owned by research groups. Research groups are composed of Users, with one or more users having admin permissions for the group.

- On the left hand side of all pages is a navigation component. This component has a circle avatar icon at the top allow the user to access their account configuration, logout, etc. Additionally, below the avatar icon, the user can view select a "Research Groups" button to view all research groups they are attached to. The remaining navigation items below this are associated with a selected research group. Upon login, if the user is associated with multiple research groups, they enter the page which lists the research groups they are attached to and allows them to select one to view and work in. If they are only attached to a single research group or they select one to working, then they are redirected to that research group's studies page.

- The primary page should display a list of all studies to which the user has access to for the research group being viewed. The list should show information related to the study, including the name of the study, the topic of the study, and the current progress. If the user has correct permissions for the study, they should also be able to "archive" or "delete" the study. Additionally, if the user has permission in the research group, they can also create new studies and assign research group members to those studies.

- When creating a new study, the user is presented with a "New Study Wizard". This wizard walks them through the process of creating a new study, which includes:
  - Naming the study
  - Study Type (Systematic Mapping Study, Systematic Literature Review, Rapid Review, Tertiary Study)
  - Selecting research group members to participate in the study
  - Optionally, they can also add the following:
    - Research Objectives
    - Research Questions
    - Motivation