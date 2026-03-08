# Project Setup

This project is to be a mono-repo for a tool that will allow researchers to conduct four key types of studies using an AI enhanced process:
1. Systematic Mapping Studies
2. Systematic Literature Reviews
3. Tertiary Studies which combine multiple SLRs
4. Rapid Reviews

## Sub Project Structure

- `frontend` - The TypeScript/React frontend that provides researches the ability to create, execute, manage, and monitor studies.
- `backend` - The component that provides the backend, implemented as a FastAPI backend providing the logic for the front-end, database operations, and control of the agents.
- `agents` - The implementation of the agents which provide the research capabilities. This is a python project.
- `db` - Defines the database schemas needed to persist data

The relationships between the projects are as follows:

[frontend] --> [backend]
[backend] --> [agents]
[backend] --> [db]

## Harness

- Each of these projects needs to be setup to have a correct harness to allow AI Agents to conduct most of the implementation.
- For Python, we want the projects to be driven by a `pyproject.toml` file, which specifies correct configurations for the following static analysis and testing tools:
  - MyPy
  - PyDoc
  - Ruff
  - pytest
- Python projects must be built using UV, in a separate enviroment, and using the uv build tools for build.
- For TypeScript, we want the projects to be driven by NPM using a combination of ESlint, prettier, and jest tools
- Each project should define a precommit configuration that ensures the associated tools and tests are execute before each commit to ensure quality of the system.

## Quality

In addition to the use of static analysis to ensure quality. All implementations by AI should ensure that good standards of coding are followed, this includes following good principles of practice and using design patterns as necessary. Some examples of good principles of practice include DRY, SOLID, and GRASP (among others).