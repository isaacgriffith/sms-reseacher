#!/usr/bin/env bash
# scripts/run-mutation-safe.sh
#
# Run cosmic-ray mutation testing in an isolated git worktree so that any
# mutations left behind by a crash or interruption never touch the real
# working tree.
#
# Usage:
#   ./scripts/run-mutation-safe.sh <package>
#   ./scripts/run-mutation-safe.sh backend
#   ./scripts/run-mutation-safe.sh agents
#   ./scripts/run-mutation-safe.sh db
#   ./scripts/run-mutation-safe.sh agent-eval
#   ./scripts/run-mutation-safe.sh researcher-mcp
#
# After a successful run the HTML report is written to
# <package>/mutation-report.html and any SQLite session files are copied back
# to <package>/ so that `cosmic-ray results` can be re-run against them.

set -euo pipefail

PACKAGE="${1:?Usage: $0 <package>  (e.g. backend, agents, db)}"
CONFIG="${PACKAGE}/cosmic-ray.toml"

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
WORKTREE_DIR=$(mktemp -d "/tmp/cosmic-ray-${PACKAGE}-XXXXXX")

results_saved=false

cleanup() {
    if [[ "$results_saved" == "false" ]]; then
        echo ""
        echo "⚠  Run did not complete cleanly — salvaging any partial results..."
        # Copy back any SQLite session databases created during the run.
        find "$WORKTREE_DIR" -maxdepth 3 -name "*.sqlite" 2>/dev/null \
            | while read -r db; do
                cp "$db" "$REPO_ROOT/$PACKAGE/" && echo "  ✓ Copied $(basename "$db")"
            done || true
        # Best-effort report generation.
        (
            cd "$WORKTREE_DIR"
            uv run cosmic-ray html-report "$CONFIG" \
                > "$REPO_ROOT/$PACKAGE/mutation-report.html" 2>/dev/null
            echo "  ✓ Partial HTML report saved"
        ) || true
    fi

    echo ""
    echo "→ Removing worktree ${WORKTREE_DIR}..."
    git -C "$REPO_ROOT" worktree remove "$WORKTREE_DIR" --force 2>/dev/null || true
    echo "  ✓ Worktree removed — source tree is clean"
}
trap cleanup EXIT

# ── 1. Create the worktree ─────────────────────────────────────────────────
echo "→ Creating isolated worktree for '${PACKAGE}' at ${WORKTREE_DIR}..."
git -C "$REPO_ROOT" worktree add "$WORKTREE_DIR" HEAD --quiet

# ── 2. Install dependencies inside the worktree ───────────────────────────
echo "→ Installing dependencies (UV cache makes this fast)..."
cd "$WORKTREE_DIR"
uv sync --all-packages --quiet

# ── 3. Run mutation testing ────────────────────────────────────────────────
echo "→ Running cosmic-ray — mutations are isolated to the worktree..."
echo ""
uv run cosmic-ray run "$CONFIG"

# ── 4. Collect results ─────────────────────────────────────────────────────
echo ""
echo "→ Mutation kill rate:"
uv run cosmic-ray results "$CONFIG"

# ── 5. Generate HTML report and copy artefacts back to the real repo ───────
echo ""
echo "→ Generating HTML report..."
uv run cosmic-ray html-report "$CONFIG" \
    > "$REPO_ROOT/$PACKAGE/mutation-report.html"
echo "  ✓ Report saved to ${PACKAGE}/mutation-report.html"

# Copy session database(s) back so 'cosmic-ray results' works without re-running.
find "$WORKTREE_DIR" -maxdepth 3 -name "*.sqlite" 2>/dev/null \
    | while read -r db; do
        cp "$db" "$REPO_ROOT/$PACKAGE/"
        echo "  ✓ Session database $(basename "$db") saved to ${PACKAGE}/"
    done || true

results_saved=true
echo ""
echo "✓ Mutation testing complete — source tree was never modified."
