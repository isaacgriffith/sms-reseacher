# Update Constitution

- Ensure that any new modules are correctly documented following doc comment requirements. Additionally, all files should have a doc comment at the top of the file
- Before completing a feature and in addition to existing tests coverage requirements, all modified subprojects must be evaluated using mutation testing ensuring that 85% or greater mutants are killed.
- Additionally, before completing a feature, ensure that all tests pass, all linting checks pass, and all static analysis checks pass. This includes any pre-existing issues.

# Grey Literature

- Need to develop an approach which will hunt for appropriate blog posts related to the topic (i.e. websearch)
  - This should include scraping of data from found blogs and converting the data to markdown for processing
  - It will also need to capture related metadata (equivalent to the fields associated with websites/urls in bibtex)
    - Date of Access
    - Author of Post (if available)
    - Title of Post
    - Etc.
- Need to be able to search for Master Theses and Doctoral Dissertations
  - This should include the ability to download the PDF of these and conversion to markdown
  - It should also capture related metadata (equivalent to the fields associated with these items in bibtex)
- Additionally, if not already present, we should have the ability to extract data from arXiv
  - Need the ability to download papers and convert to PDF
  - Need ability to capture related metadata
- In the UI there should be the ability to search for grey literature when setting up the search capabilities
  - This should also include what types of grey literature that we are looking to use

# User Settings

- Add ability to have a user avatar, and add the ability to set the user avatar in user settings

# Automated Improvement

- We are using DeepEval to evaluate our Agents, but we also want to automate their improvement
- Let's implement tooling using DSPy to automate the improvement of the Agents in conjunction with the DeepEval approach

# UI

- Change from using inline styles to using a consolidated style within the component


# Paper Metadata

- If possible during the search extract the necessary paper metadata and the abstract, if available from the index used.