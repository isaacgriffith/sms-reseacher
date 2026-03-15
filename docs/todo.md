## Project Setup

- [ ] Correct the project setup
      - Have the AI update both CLAUDE.md and constitution.md to explain how to correctly run all types of tests, linters, and static analysis tools for the project correctly on the first try.
      - Run all existing tests, any failures should be remedied, add any additional tests needed to reach code coverage percentation of 85% or higher.
      - Fix mutmut, or if not possible, shift to another python mutation testing approach. Run all tests against mutation, add new tests to ensure that 85% or greater mutants are killed

---

## Frontend Improvements

- [ ] Need to also add a Swagger/OpenAPI documentation endpoint in the frontend to document the api on the backend.
- [ ] Setup the frontend so that it uses material UI
- [ ] Setup frontend so that it has a user preferences section
      - Here the user has the ability to change their password, following best practices
      - Here the user can setup 2FA, which we will need a service for
      - Here the user can change their display preference: Light Mode, Dark Mode, Based-on System

---

## Models and Agents

- [ ] Update all agent prompt templates to be about expertise in SMS's for Software Engineering and Artificial Intelligence, perhaps even make the field something that is variable.
- [ ] Similarly, we should allow the templates to be for any of the study types not just SMSs, but this can be deferred to later.
- [ ] Setup the Administration panel to allow adding new models
      - There should be a providers section, with the following key providers:
        - OpenAI
        - Anthropic
        - OpenAI
        - Ollama (which can be configured to a remote server)
      - There should be an available models section, which loads available models from each of the providers
- [ ] Create an abstraction for Agent, which allows the storage of the following information in the database for each agent.
      - agentId: UUID, unique identifier for the agent
      - roleName: string, Name of the role the agent performs
      - roleDescription: string, Description of the role the agent performs
      - personaName: string, Agent's persona name
      - personaDescription: string, Agent's persona description
      - personaImage: image, An image (SVG) which depicts the agent's persona, can be generated.
      - systemMessageTemplate: string, the string representing the templated system message which uses all of the other information associated with the agent (excluding model)
      - modelId: UUID, the exact model identifier from the available models
      - modelProviderId: UUID, the model provider identifier from the available providers
- [ ] In the Administration section, there should be a tab that allows for the creation and modification of agents.
      - This should include a syntax-highlighted section which allows for the modification of the Agent's System message.
      - There should also be a "Generate/Update System Message" button, which when clicked uses an Agent Generation Agent to update the System message to be optimized for the role, persona, and model selected for the agent.
      - In the Agent's section, there should be a "Create Agent" button, which will walk the user through the process of creating/generating a new agent for the specific task type and model selected. Note that this should be restricted
        to only the task types already identified as part of the Research processes.

---

## Research Protocol Definition

- [ ] Provide a means by which a researcher can define/modify the research process
      - Currently, the process is rigid, and allows only one path for each study type.
      - What we need to do is provide a means by which the workflow, or protocol, of the study can be described using a graph-based description language
        - Nodes:
          - Represent tasks, and have logic specific to what needs to be done. The tasks must be confined to the specific tasks defined as part of any study type.
          - Have inputs defined which represent the information flowing into the task
          - Have outputs defined which describe the information output from the task
          - Have one or more Human Agent, AI Agent, or combination thereof assigned to complete the task
          - Can have quality gates based on metrics which can be measured and evaluated by human or AI agents to determine if the task has been completed
        - Edges:
          - represent the flow of information between nodes
      - These workflows should be able to be described and edited textually or visually.
