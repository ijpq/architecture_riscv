#!/usr/bin/env bash
# Verify a test-only RED commit in a disposable archive, not the user's worktree.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
commit="${1:-HEAD}"
changed="$(git -C "$root" diff-tree --no-commit-id --name-only -r "$commit")"
if [[ -z "$changed" ]] || grep -Ev '^course/test_[^/]+\.py$' <<<"$changed"; then
  printf 'RED isolation failed: commit must change only course/test_*.py\n' >&2
  exit 1
fi
scratch="$(mktemp -d)"
trap 'rm -rf -- "$scratch"' EXIT
git -C "$root" archive "$commit" | tar -xf - -C "$scratch"
set +e
python3 -m unittest discover -s "$scratch/course" -p test_source_bundle.py -v >"$scratch/result.log" 2>&1
status=$?
set -e
while IFS= read -r line; do printf '%s\n' "$line"; done <"$scratch/result.log"
if (( status == 0 )); then
  printf 'RED isolation failed: the committed test passed\n' >&2
  exit 1
fi
printf 'RED isolation PASS: %s contains only tests, which fail in its isolated tree (exit %s)\n' "$commit" "$status"
