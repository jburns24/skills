---
name: find-commit
description: Searches git history for commits that contain generation-metadata blocks (created by the commit skill) and returns the plan intent, model, and unplanned changes for each match. Use this skill whenever an agent or user needs to understand why a change was made, trace a feature back to its plan, audit planned vs. actual changes, or find commits related to a topic. Triggers include "why was this changed", "find commits related to", "what plan drove this", "search commit history", "show me instrumented commits", "what was the intent behind", "trace plan history", or any question about the reasoning or plan behind past changes.
---

# Find Commit

Searches git history for commits instrumented with `generation-metadata` blocks — embedded by the `commit` skill — and surfaces the original plan, model, and any unplanned changes for each match. This lets agents and users understand the *intent* behind a change, not just what changed.

## Metadata block format

Each instrumented commit message contains a block like this:

```
<!-- generation-metadata
{
  "model": "claude-sonnet-4-6",
  "plan_file": "/Users/jburns/.claude/plans/<name>.md",
  "plan_contents": "<full plan text, JSON-escaped>",
  "unplanned_changes": ["<filepath>: <description>", ...]
}
-->
```

`plan_contents` is the most valuable field — it captures the full reasoning and context that drove the implementation.

## Query parameters

Accept any combination of these from the user:

| Parameter | Meaning |
|-----------|---------|
| `keyword` | Match against `plan_contents` or commit subject (case-insensitive) |
| `file` | Return only commits that touched this file path |
| `since` / `until` | Date filters, passed directly to `git log` |
| `hash` | Look up one specific commit |
| _(none)_ | List every instrumented commit in the repo |

## Instructions

### Step 1 — Parse the query

Read the user's request and identify which parameters apply. When no specific criteria are given, the intent is usually "show me everything instrumented" — proceed with a full listing.

### Step 2 — Find candidate commits

Use a bundled helper script for reliable parsing. Run it directly:

```bash
python3 scripts/search.py \
  [--keyword "term"] \
  [--file path/to/file] \
  [--since 2024-01-01] \
  [--until 2024-12-31] \
  [--hash abc1234]
```

The script (`scripts/search.py` in this skill directory) handles:
- Running the appropriate `git log` command
- Filtering commits that contain `generation-metadata`
- Parsing the JSON block from each matching commit message
- Applying keyword filters against `plan_contents` and subject
- Fetching changed files per commit
- Emitting structured JSON output

If the script isn't available or fails, fall back to running the steps manually (see **Manual fallback** below).

### Step 3 — Handle the results

The script outputs a JSON array of match objects:

```json
[
  {
    "hash": "53b254b",
    "subject": "feat: add commit skill with generation metadata tracing",
    "date": "2026-02-22T20:54:00-05:00",
    "model": "claude-sonnet-4-6",
    "plan_file": "/Users/jburns/.claude/plans/generic-wobbling-russell.md",
    "plan_contents": "# Plan: Add `commit` Skill\n\n...",
    "unplanned_changes": ["skills/hello-world/SKILL.md: deleted placeholder..."],
    "files_changed": ["skills/commit/SKILL.md", ".claude-plugin/marketplace.json"]
  }
]
```

If the array is empty, report that no instrumented commits matched the query and stop.

### Step 4 — Format and present results

For each match, render a block like this (newest first):

```
## 53b254b — feat: add commit skill with generation metadata tracing
Date: 2026-02-22
Model: claude-sonnet-4-6

### Plan intent
<plan_contents verbatim if ≤ 500 words, or a clear 5–10 sentence summary if longer>

### Files changed
- skills/commit/SKILL.md
- .claude-plugin/marketplace.json
- skills/hello-world/SKILL.md

### Unplanned changes
- skills/hello-world/SKILL.md: deleted placeholder boilerplate skill (user-requested cleanup, outside plan scope)
```

If `plan_contents` is null, note: *"Metadata block present but plan contents were not recorded."*

Close with a one-line summary: **"Found N instrumented commit(s) matching your query."**

---

## Manual fallback

If `scripts/search.py` is unavailable, do these steps directly:

**Find candidates:**
```bash
# All commits
git log --all --format="%H|%s|%ai" --no-merges

# File-scoped
git log --all --format="%H|%s|%ai" --no-merges -- <file>
```

**Filter to instrumented commits** — for each hash:
```bash
git log -1 --format="%B" <hash> | grep -q "generation-metadata" && echo <hash>
```

**Parse metadata** — use Python inline:
```python
import re, json, subprocess
body = subprocess.check_output(["git", "log", "-1", "--format=%B", hash_]).decode()
m = re.search(r'<!-- generation-metadata\s*(\{.*?\})\s*-->', body, re.DOTALL)
meta = json.loads(m.group(1)) if m else None
```

**Get changed files:**
```bash
git diff-tree --no-commit-id -r --name-only <hash>
```

---

## Examples

**List all instrumented commits:**
> "show me all instrumented commits"
→ Runs full scan, lists every match newest-first.

**Keyword search:**
> "find commits related to custom domain"
→ Returns commits where `plan_contents` or subject contains "custom domain".

**File trace:**
> "what plan drove changes to src/auth/login.ts?"
→ Scans `git log -- src/auth/login.ts`, shows plan intent for each instrumented hit.

**Single commit lookup:**
> "show me the plan behind commit 53b254b"
→ Fetches that commit's metadata directly.

**Unplanned changes audit:**
> "show me commits that had unplanned changes"
→ Lists instrumented commits where `unplanned_changes` is non-empty. Useful for auditing implementation drift.
