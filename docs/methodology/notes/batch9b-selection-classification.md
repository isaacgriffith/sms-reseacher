# Batch 9b — Study selection strategies, paper classification, grounded theory

Source extractions: `scratchpad/txt/{petersen_identifying_2011, wieringa_requirements_2006, stol_grounded_2016}.txt`

---

## petersen_identifying_2011 — Identifying Strategies for Study Selection in Systematic Reviews and Maps
(Kai Petersen, Nauman Bin Ali; 2011 International Symposium on Empirical Software Engineering and Measurement, ESEM 2011, pp. 351–354, DOI 10.1109/ESEM.2011.46)

**Type:** empirical study (a non-systematic review of 139 SLRs/maps) that yields a catalogue usable as guidance.

**Role in corpus:** This is the only paper that enumerates, names and defines the *decision rules* by which multiple reviewers' individual include/exclude/uncertain votes are converted into a single selection decision — the rule set nobody else writes down. Authors' own words: "To the best of our knowledge this is the first study focusing on the investigation of inclusion and exclusion strategies for systematic reviews in software engineering."

### THE SCHEME OR RULE SET — reproduced in full

The paper's own framing: "In total we identified a total of 13 codes representing different strategies. The strategies are grouped according to their goals. Three goals have been identified:"

- **Objectivity of Criteria**: "Strategies verify the objectivity of the selection criteria."
- **Resolve Uncertainty and Disagreement**: "Strategies aid researchers in resolving uncertainties and disagreements."
- **Clear Decision Rules**: "Strategies based on decision rules determine whether an article is included or excluded."

Conclusion restates the split: "Thirteen different strategies for inclusion and exclusion have been identified. Three are used to assure objective inclusion/exclusion criteria to reduce bias, three to resolve disagreements and uncertainties due to bias, and seven defined decision rules on how to act based on disagreements/agreements."

#### Table I — Strategies Objective Criteria (goal: Objectivity of Criteria)

| ID | Code | Descr. (verbatim) | No. of citations |
|----|------|-------------------|------------------|
| O1 | Objective Criteria Assessment (pre-inclusion/exclusion) | "Test sub-sets of articles with two or more persons before starting the actual inclusion/exclusion process, high agreement indicate objective criteria" | 5 |
| O2 | Objective Criteria Assessment (post-inclusion/exclusion) | "Reviewers measure their agreement after completing inclusion/exclusion to determine level of objectivity on all or a sample set of studies (can also be done on a sub-set)" | 10 |
| O3 | Objective Formulation of Criteria | "Require objective statements (e.g. is X stated, Yes/No)" | 1 |

Commentary the paper gives on this table: "It can be seen that five studies followed strategy O1 and ten studies strategy O2. One possible reason for the frequent usage is that these strategies were recommended in the systematic review guidelines [2], [3]. Objective O1 is related to piloting the inclusion and exclusion criteria. Furthermore, O2 tests the objectivity considering the level of agreement. Objective criteria formulation was explicitly stated as a strategy in [5], the reason being that the review was conducted by a single author."

#### Table II — Strategies Resolve Disagreements/Uncertainties

| ID | Code | Descr. (verbatim) | No. of citations |
|----|------|-------------------|------------------|
| R1 | Another person check | "Additional reviewer(s) is/are consulted to support in the decision of inclusion or exclusion by reviewing/assessing the result" | 14 |
| R2 | Second vote on uncertain and exclude | "Only for papers rated as either uncertain or exclude a second vote is obtained." | 1 |
| R3 | If disagreement or uncertainty in decision then discuss | "If a set of researchers is in disagreement, then a decision for the next step is taken after discussion to resolve the disagreement." | 18 |

Commentary: "A similar observation as for the previous goal can be made. Both strategies that are frequently reported have been proposed in [2], [3], i.e. to consult additional researchers, and to discuss and resolve uncertainties."

#### Table III — Decision Rules to Directly Arrive at a Decision

| ID | Code | Descr. (verbatim) | No. of citations |
|----|------|-------------------|------------------|
| D1 | Majority Vote | "The group of researchers take a vote on the article and the decision of the majority is followed" | 1 |
| D2 | At least one "include" then include | "If one of the reviewers includes the paper then it is considered for being an included primary study" | 1 |
| D3 | All "include" then include | "Only if all reviewers include the article then it is included, otherwise it is excluded" | 1 |
| D4 | At least one "uncertain" then include | "If one of the reviewers is uncertain regarding the paper, it is considered in the next step of the systematic review" | 11 |
| D5 | One "exclude" and one "uncertain" then exclude | "If one of the reviewers says exclude the other uncertain then the paper is excluded" | 1 |
| D6 | All researchers vote "uncertain" then include | "If all researchers vote uncertain, then the paper is included" | 1 |
| D7 | All "exclude" then exclude | "If all reviewers agree that the paper should be excluded then it is excluded, otherwise it is included" | 1 |

Commentary: "Table III presents strategies related to the goal 'Clear Decision Rules'. The decision rules are new and have not been reported in the guidelines [2], [3]. Strategy D5 is of interest, as this strategy is inclusive leading to more papers in the following steps. At the same time strategy D5 is in line with the recommendation given by Kitchenham [2], [3] advising to be inclusive in study selection. The remaining strategies were reported in individual studies."

> `[EXTRACTION UNCLEAR / APPARENT PAPER-INTERNAL INCONSISTENCY: the D5 commentary above calls D5 "inclusive", but Table III defines D5 as an EXCLUDING rule and the Discussion section explicitly contrasts them the other way: "an exclusive strategy would be D5 while a more inclusive strategy would be D4." The commentary paragraph most plausibly meant D4 (cited 11 times, the inclusive rule); cite the Discussion wording, not the Table III commentary wording, when characterising D4 vs D5.]`

### Evidence on which strategies perform better / are more used

- The paper explicitly disclaims accuracy evidence: "we are not able to provide information about the accuracy of the strategies." So there is **no** empirical comparison of effectiveness — only frequency of reporting and a reasoned trade-off argument.
- Frequency finding: "the analysis shows that the strategies that have been mentioned in the guidelines are most frequently reported. However, researchers apply strategies beyond that. In total nine strategies have been identified that are not part of the guidelines."
- Combination finding: "Combinations of strategies have been used as well, which is not visible from the tables right away. Most commonly two strategies have been reported. TOnly four studies reported the usage of more than two strategies (cf. [10], [8], [11], [9]). Our investigation revealed that the strategies proposed in the guidelines are often followed together (e.g. R3 with O2, and R1 with R3) [2], [3]." (sic: "TOnly")
- Reasoned trade-off (the closest thing to a performance verdict): "an exclusive strategy would be D5 while a more inclusive strategy would be D4. From a validity point of view D4 would strengthen the study, but would require more effort reading additional parts of the article. With a very high number of articles this effort could mean that the review is not manageable in reasonable time and becomes outdated during writing. With a lower number of articles the more inclusive strategy would be preferable."
- Open questions left unanswered by the paper: "Question 1: Which strategies to combine to get high effectiveness in selection (selecting papers relevant for the population and not excluding relevant papers) and efficiency (reduce the effort in paper selection and subsequent review steps)?" and "Question 2: Which process should be followed (order in which strategies are executed), e.g. at which stage of the process should we follow decision rules, discuss, or calculate inter-rater agreement to achieve effectiveness and efficiency?"

### Strategies the paper attributes to the prior guidelines (NOT its own contribution)

From Kitchenham 2004 [2] / 2007 [3], as summarised in Related Work — cite as prior guidance, not as this paper's finding:
- "assess the goodness of the objectivity of inclusion/exclusion criteria by calculating inter-rater agreement using Cohen Kappa statistic";
- "additional persons should be involved to discuss inclusion and exclusion, especially when the step is done by a single researcher";
- "In case of uncertainty sensitivity analysis is proposed as a solution, but no detailed guide is given of how to conduct the sensitivity analysis."
- From the 2007 update: "every agreement/disagreement needs to be resolved through discussion"; and **test–retest** for single researchers — "In test-retest a random sample of studies is re-evaluated by a single researcher to determine intra-rater reliability."

### Process steps or stages defined

**Strategy-identification coding procedure (the paper's own method, reusable as a coding protocol):**
- **S1:** "Identify the reported strategy and create a code for the strategy. Log the code in the data record for the paper currently under review."
- **S2:** "Identify the next strategy and determine whether there already exist a code for that strategy. If a code exist, log the code for the paper currently being under review, otherwise create a new code and log the code."
- **S3:** "Repeat step S2 until the last paper/last strategy in the set has been recorded."

Input gate for extraction: "A paper was only considered for data extraction when the review protocol/method section within the paper provides information of strategies for reducing bias/resolving disagreements. This information is usually found under the heading inclusion/exclusion and paper selection, or in the section 'Conducting the review'." Extracted fields: "the author names, title, and strategies for each paper".

**The paper's own study identification/selection (inputs → outputs):**
- Study identification: studies **citing** three guideline papers (Kitchenham 2004, Kitchenham 2007, Petersen et al. 2008 mapping guidelines), located via Google Scholar. "Papers that are systematic, but were published before the guidelines have been released, will not be included."
- Inclusion criteria (verbatim): "The abstract or title has to explicitly state that the article is a literature review or systematic literature review." / "The article is in the area of software engineering or computer science." / "The article is a journal paper, conference paper, thesis, or technical report. As Google Scholar is able to capture gray literature theses and technical reports are considered as well."
- Exclusion criteria (verbatim): "Article is not in English." / "The retrieved document is an editorial or an introduction to proceedings." / "The articles is not within the area of software engineering/computer science." / "The article is not accessible in full-text." / "The article is a duplicate of an article already in the set."
- Yield: 300 hits (2004 guidelines) + 122 (2007) + 19 (mapping guidelines) → "After applying the inclusion/exclusion criteria 139 systematic reviews in software engineering/computer science were left." → "Papers that did not report any strategies for bias reduction and disagreement resolution were discarded. In the end of the process 40 articles containing strategies remained."
- Note the paper's own justification for single-reviewer selection: "The inclusion and exclusion criteria are objective, and are easy to check without requiring interpretation (e.g. looking for the word literature review/systematic literature review in the title and abstract) ... As a consequence the choice was made that the first author conducts the inclusion/exclusion process individually."

### Caveats, traps and pitfalls (verbatim)

- Under-reporting means the tables understate use: "It is important to point out that the researchers might have used more of the presented strategies in their studies, but did not report them. However, it is still interesting to observe the number of reported articles as they represent what the researchers think are important strategies when conducting the paper selection. At the same time reporting a strategy means that an informed decision has been taken about that strategy."
- Reporting a single rule does not define the whole rule table: "It should also be observed that reporting a single strategy does not mean that this is the only strategy applied. For example, regarding D4 we cannot be sure if the paper is also included if one reviewer says 'exclude', and the other 'uncertain'. This further supports the claim that making strategies explicit is a prerequisite for complete reporting."
- Rules under-specify the vote space: "It was also noticed that the decisions rules in the reviews did not clearly explain how the various possibilities were handled, e.g. 8 studies use D4 which states to include an article if there is at least one 'uncertain' (as shown in Table III). It is not clear whether it means we include the studies even if two of the three reviewers classified it as irrelevant. If it does, is it a justified choice considering the effort that will be put again to review something that might very well be irrelevant."
- Do not exclude early on thin evidence: "As mentioned earlier, the reason for disagreements is that abstracts are often not clear. In general, given the lack of clarity one has to look at additional information and the article should not be excluded too early."
- Bias is endemic to human selection: "given that the inclusion and exclusion is done by humans there is a risk of bias, which might lead to exclusion of relevant studies, or inclusion of irrelevant ones. Bias in study selection is commonly reported in systematic reviews ... In case the titles or abstracts are not clear, the bias is further fortified."
- Documentation is a repeatability requirement: "One aim of the systematic reviews is to follow a repeatable process [3]. Therefore it is imperative that the selection criteria and steps to resolve disagreements are documented and reported in systematic reviews. Doing this will also show that a conscious decision was made from the different available choices and bring more transparency in the review process."
- Field-level problem statement: "study selection and getting agreement are two of the main challenges in systematic reviews. Hence, one of the success factors mentioned is the need of clear criteria." (attributed to Babar & Zhang's interview study, not this paper's data.)

> `[EXTRACTION UNCLEAR / PAPER-INTERNAL INCONSISTENCY: two counts disagree with Table III. (a) Table III lists D4 at 11 citations, but the Discussion says "8 studies use D4". (b) The abstract, results and conclusion all say 13 strategies (3 + 3 + 7 = 13, consistent with Tables I–III), yet the validity section refers to "Strategy 13 ... found in the 35th [8] paper reviewed, and strategies 14, 15, and 16 were found in the 41st paper reviewed [9]" and to a set of "40 articles" that is elsewhere "41st paper reviewed". Report the table values (13 strategies, D4 = 11) and flag the discrepancy rather than reconciling it.]`

### Reliability and agreement techniques

- The agreement machinery in the catalogue is O1 (pilot agreement on a sub-set *before* selection), O2 (agreement measured *after* selection, on all or a sample), R1 (extra reviewer), R2 (second vote restricted to uncertain/exclude), R3 (discussion to resolve).
- The named statistic is inherited, not introduced: "assess the goodness of the objectivity of inclusion/exclusion criteria by calculating inter-rater agreement using Cohen Kappa statistic" (from Kitchenham 2004).
- Intra-rater option for solo reviewers: test–retest, "a random sample of studies is re-evaluated by a single researcher to determine intra-rater reliability."
- **No kappa values or agreement rates are reported by this paper.** It counts how often strategies are *reported*, nothing more.

### Threats to validity framework

The paper names three threats ("The main validity threats in this study are that strategies are missed, bias in the interpretation of strategies, and the use of a single search engine"):

| Threat | Verbatim statement / mitigation |
|--------|--------------------------------|
| Missing Strategies | "One threat to validity is that strategies for inclusion and exclusion are missed due to bias of the researcher. This threat is considered relatively low as after reviewing the first 7 of 40 papers 9 out of 13 codes/strategies have been identified and almost all strategies in the remaining papers fit well into these categories. ... With each additional review considered the number of newly identified strategies reduced and stabilized after paper 7." (i.e. an informal saturation argument) |
| Interpretation of Strategies | "The strategies were interpreted by a single researcher, which makes this step prone to bias." |
| Single Search Engine | "The use of a single search engine leads to a risk of missing systematic reviews. We also only focused on all articles mentioning the guidelines. However, even though we might miss papers due to the limitation in search engines, we saw that most of the strategies were already identified after reading 7 of 40 papers. Hence, this threat is considered as being under control." |

### Empirical findings worth citing

- 139 SLRs/maps met inclusion criteria; **only 40 reported any bias-reduction or disagreement-resolution strategy at all** — i.e. roughly 71% of the SLRs that passed screening reported none.
- 13 strategies total; **nine of the 13 are not in the guidelines**.
- Most-reported strategies: R3 discuss (18), R1 another person check (14), D4 at-least-one-uncertain-then-include (11), O2 post-hoc agreement (10), O1 pilot agreement (5). Everything else is cited once.
- "Most commonly two strategies have been reported"; only four studies reported more than two.
- Saturation of the coding: 9 of 13 codes appeared within the first 7 of 40 papers.
