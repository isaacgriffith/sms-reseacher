"""Tests for PromptLoader: renders each template with sample context."""

from pathlib import Path

import pytest
from jinja2 import UndefinedError

from agents.core.prompt_loader import PromptLoader

# Sample contexts matching each agent's Jinja2 variables
SAMPLE_CONTEXTS: dict[str, dict[str, str]] = {
    "screener": {
        "inclusion_criteria": "Studies on software testing in agile projects",
        "exclusion_criteria": "Papers published before 2010 or not peer-reviewed",
        "abstract": "This paper presents a controlled experiment on TDD in agile teams.",
    },
    "extractor": {
        "title": "Controlled Experiment on TDD",
        "authors": ["Alice", "Bob"],
        "year": 2022,
        "venue": "ICSE",
        "doi": "10.1145/1234567",
        "research_questions": [{"id": "RQ1", "text": "What is the effect of TDD?"}],
        "paper_text": "We conducted a controlled experiment with 42 participants using Python.",
    },
    "synthesiser": {
        "papers_summary": "Paper A found X. Paper B found Y. Paper C contradicts A.",
        "research_question": "What is the effect of TDD on code quality?",
    },
}


@pytest.mark.parametrize("agent_type", ["screener", "extractor", "synthesiser"])
class TestPromptLoader:
    """Verify PromptLoader loads and renders templates without errors."""

    def test_system_prompt_loads(self, agent_type: str) -> None:
        """system.md exists and loads as a non-empty string."""
        loader = PromptLoader(agent_type)
        system = loader.load_system()
        assert isinstance(system, str)
        assert len(system) > 0

    def test_user_template_renders(self, agent_type: str) -> None:
        """user.md.j2 renders without UndefinedError given sample context."""
        loader = PromptLoader(agent_type)
        rendered = loader.render_user(SAMPLE_CONTEXTS[agent_type])
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_user_template_contains_context_values(self, agent_type: str) -> None:
        """Rendered user prompt includes at least one value from context."""
        loader = PromptLoader(agent_type)
        context = SAMPLE_CONTEXTS[agent_type]
        rendered = loader.render_user(context)
        # At least one context value should appear in the output
        assert any(v in rendered for v in context.values())

    def test_load_messages_structure(self, agent_type: str) -> None:
        """load_messages returns a valid 2-message OpenAI-format list."""
        loader = PromptLoader(agent_type)
        messages = loader.load_messages(SAMPLE_CONTEXTS[agent_type])
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[0]["content"]
        assert messages[1]["content"]

    def test_missing_variable_raises_undefined_error(self, agent_type: str) -> None:
        """Rendering with an empty context raises UndefinedError (strict mode)."""
        loader = PromptLoader(agent_type)
        with pytest.raises(UndefinedError):
            loader.render_user({})


class TestPromptLoaderErrors:
    """Edge-case error handling in PromptLoader."""

    def test_unknown_agent_type_raises(self, tmp_path: Path) -> None:
        """An unknown agent type raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Prompt directory not found"):
            PromptLoader("nonexistent_agent", prompts_root=tmp_path)

    def test_missing_system_md_raises(self, tmp_path: Path) -> None:
        """Missing system.md raises FileNotFoundError."""
        agent_dir = tmp_path / "test_agent"
        agent_dir.mkdir()
        loader = PromptLoader("test_agent", prompts_root=tmp_path)
        with pytest.raises(FileNotFoundError, match="system.md not found"):
            loader.load_system()
