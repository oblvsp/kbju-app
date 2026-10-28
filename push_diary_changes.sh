#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/vsp/Документы/Calc"
cd "$REPO_DIR"

# Check if the current directory is a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: $REPO_DIR is not a git repository."
    exit 1
fi

# Stage all changes (you can adjust patterns if needed)
git add -A

# Commit with a generic message (you can customize as needed)
COMMIT_MSG="Update Diary feature: added DiaryScreen and database changes"
if ! git diff --cached --quiet; then
    git commit -m "$COMMIT_MSG"
else
    echo "No changes to commit."
fi

# Push to the current branch (assumes remote "origin" exists)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$CURRENT_BRANCH"

echo "Push completed for branch $CURRENT_BRANCH."

# Ensure the script is executable (can be called again later)
chmod +x "$0"