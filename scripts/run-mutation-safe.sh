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

# Fingerprint of the real checkout, taken before the run and re-checked on exit.
# Isolation is the mechanism; this is the proof. A fingerprint is used rather
# than refusing on a dirty tree so ordinary work-in-progress does not block a
# run — what matters is that this run changed nothing, not that the tree
# started pristine.
tree_fingerprint() {
    git -C "$REPO_ROOT" status --porcelain --untracked-files=no \
        | sort \
        | sha256sum \
        | cut -d' ' -f1
}
FINGERPRINT_BEFORE="$(tree_fingerprint)"

verify_tree_untouched() {
    if [[ "$(tree_fingerprint)" != "$FINGERPRINT_BEFORE" ]]; then
        cat >&2 <<EOF

  ✖ THE REAL WORKING TREE CHANGED DURING THIS RUN.

  Isolation failed — mutated files may be sitting in ${REPO_ROOT}.
  Do not commit. Review every change before discarding anything:

      git -C "${REPO_ROOT}" status
      git -C "${REPO_ROOT}" diff

  Then scan for artifacts that survived:
      python3 scripts/check_mutation_artifacts.py

EOF
        return 1
    fi
    echo "  ✓ Real working tree is byte-identical to before the run"
    return 0
}

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
    echo "  ✓ Worktree removed"

    echo ""
    echo "→ Verifying the real working tree was never touched..."
    verify_tree_untouched || exit 1
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

# Belt and braces: the worktree proves isolation, the fingerprint proves it
# held, and this proves no artifact reached the tracked source by any other
# route (a stray editor save, a copied file, a hand-run cosmic-ray).
echo ""
echo "→ Scanning the real source tree for mutation artifacts..."
python3 "$REPO_ROOT/scripts/check_mutation_artifacts.py"
echo "  ✓ No artifacts present"

echo ""
echo "✓ Mutation testing complete — source tree was never modified."
