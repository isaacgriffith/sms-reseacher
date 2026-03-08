"""Prompt template loader for agent system and user prompts."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError

# Default prompts root relative to this file's package location
_DEFAULT_PROMPTS_ROOT = Path(__file__).parent.parent / "prompts"


class PromptLoader:
    """Loads and renders Markdown prompt templates for a given agent type.

    System prompts are plain Markdown files (``system.md``).
    User prompts are Jinja2 templates (``user.md.j2``) that accept a
    context dictionary for variable substitution.

    Args:
        agent_type: One of ``screener``, ``extractor``, ``synthesiser``.
        prompts_root: Optional override for the prompts directory root.
            Defaults to ``agents/src/agents/prompts/``.

    Raises:
        FileNotFoundError: If the prompt directory or expected files
            do not exist.
    """

    def __init__(
        self,
        agent_type: str,
        prompts_root: Path | None = None,
    ) -> None:
        """Initialise the loader for *agent_type*.

        Args:
            agent_type: Agent type name (``screener``, etc.).
            prompts_root: Optional root directory for prompt files.
        """
        root = prompts_root or _DEFAULT_PROMPTS_ROOT
        self._prompt_dir = root / agent_type
        if not self._prompt_dir.is_dir():
            raise FileNotFoundError(
                f"Prompt directory not found: {self._prompt_dir}"
            )
        self._env = Environment(
            loader=FileSystemLoader(str(self._prompt_dir)),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

    def load_system(self) -> str:
        """Read and return the static system prompt.

        Returns:
            The contents of ``system.md`` as a string.

        Raises:
            FileNotFoundError: If ``system.md`` does not exist.
        """
        system_path = self._prompt_dir / "system.md"
        if not system_path.is_file():
            raise FileNotFoundError(f"system.md not found in {self._prompt_dir}")
        return system_path.read_text(encoding="utf-8")

    def render_user(self, context: dict[str, Any]) -> str:
        """Render ``user.md.j2`` with the given context dictionary.

        Args:
            context: Variable substitutions for the Jinja2 template.
                Keys must match the ``{{ variable }}`` placeholders in
                ``user.md.j2``.

        Returns:
            The rendered user prompt string.

        Raises:
            UndefinedError: If a required template variable is missing
                from *context*.
            FileNotFoundError: If ``user.md.j2`` does not exist.
        """
        try:
            template = self._env.get_template("user.md.j2")
        except Exception as exc:  # noqa: BLE001
            raise FileNotFoundError(
                f"user.md.j2 not found in {self._prompt_dir}"
            ) from exc
        try:
            return template.render(**context)
        except UndefinedError:
            raise

    def load_messages(self, context: dict[str, Any]) -> list[dict[str, str]]:
        """Build a complete OpenAI-format messages list for an agent call.

        Args:
            context: Variable substitutions passed to :meth:`render_user`.

        Returns:
            A list with a ``system`` message and a rendered ``user`` message.
        """
        return [
            {"role": "system", "content": self.load_system()},
            {"role": "user", "content": self.render_user(context)},
        ]
