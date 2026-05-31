#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-c2u-ner-tallip-anonymous-supplement}"
VISIBILITY="${2:-private}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. Install it first, then run: gh auth login" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login" >&2
  exit 1
fi

if [ ! -d .git ]; then
  git init
fi

git add .
git commit -m "Prepare anonymous C2U-NER TALLIP supplement" || true

if gh repo view "$REPO_NAME" >/dev/null 2>&1; then
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$(gh api user --jq .login)/${REPO_NAME}.git"
else
  gh repo create "$REPO_NAME" "--${VISIBILITY}" --source=. --remote=origin
fi

git branch -M main
git push -u origin main

echo "Repository ready:"
gh repo view "$REPO_NAME" --web

