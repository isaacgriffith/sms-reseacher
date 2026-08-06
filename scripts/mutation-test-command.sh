#!/usr/bin/env bash
# scripts/mutation-test-command.sh
#
# The test command cosmic-ray runs against each mutant. It exists to make a
# direct `cosmic-ray run` against the real checkout fail immediately and loudly
# instead of quietly rewriting tracked files.
#
# Why this guard is structural rather than an environment flag: cosmic-ray
# mutates source in place, so by the time anything can react, files are already
# being edited. The only reliable question to ask is "am I in a throwaway
# checkout?", and git can answer it. In a linked worktree, --git-dir points at
# .git/worktrees/<name> while --git-common-dir points at the shared .git. In the
# primary checkout the two are identical. An exported variable can be set by
# mistake; this cannot.
#
# Usage (from the test-command key in <package>/cosmic-ray.toml):
#   bash scripts/mutation-test-command.sh <package-dir>
#
# Run mutation testing through ./scripts/run-mutation-safe.sh, which creates the
# worktree this guard requires.

set -euo pipefail

PACKAGE_DIR="${1:?Usage: $0 <package-dir>  (backend|agents|db|agent-eval|researcher-mcp)}"

case "$PACKAGE_DIR" in
    backend)        UV_PACKAGE="sms-backend" ;;
    agents)         UV_PACKAGE="agents" ;;
    db)             UV_PACKAGE="db" ;;
    agent-eval)     UV_PACKAGE="sms-agent-eval" ;;
    researcher-mcp) UV_PACKAGE="sms-researcher-mcp" ;;
    *)
        echo "mutation-test-command: unknown package '${PACKAGE_DIR}'" >&2
        exit 2
        ;;
esac

# ── Refuse to mutate the primary checkout ──────────────────────────────────
git_dir=$(git rev-parse --absolute-git-dir 2>/dev/null || echo "")
common_dir=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || echo "")

if [[ -z "$git_dir" || "$git_dir" == "$common_dir" ]]; then
    cat >&2 <<EOF

  ✖ REFUSING TO RUN — cosmic-ray is mutating the real working tree.

  Mutations are being written to tracked files in:
      $(pwd)

  Stop the run now (Ctrl-C), then inspect and restore:
      git status
      git diff                     # review before discarding anything
      git checkout -- <file>

  Run mutation testing through the isolation wrapper instead:
      ./scripts/run-mutation-safe.sh ${PACKAGE_DIR}

  Committing a mutated tree is not a theoretical risk. Commit ecc32de did
  exactly that, and because a surviving mutant is by definition invisible to
  the test suite, 60+ defects sat in backend/src through five releases with
  every test passing.

EOF
    exit 99
fi

exec uv run --package "$UV_PACKAGE" pytest "${PACKAGE_DIR}/tests/unit" -x -q
