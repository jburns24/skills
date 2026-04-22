#!/usr/bin/env python3
"""
find-commit search helper

Scans git history for commits containing generation-metadata blocks
(embedded by the 'commit' skill) and returns structured JSON results.

Usage:
    python3 search.py [options]

Options:
    --keyword TEXT    Filter by keyword in plan_contents or subject
    --file PATH       Limit to commits that touched this file
    --since DATE      Only commits after this date (git log format)
    --until DATE      Only commits before this date (git log format)
    --hash HASH       Look up a single specific commit
    --unplanned-only  Only return commits with non-empty unplanned_changes
"""

import argparse
import json
import re
import subprocess
import sys


def run(cmd, check=True):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"git error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_commit_body(hash_):
    return run(["git", "log", "-1", "--format=%B", hash_])


def parse_metadata(body):
    m = re.search(r'<!--\s*generation-metadata\s*(\{.*?\})\s*-->', body, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def get_changed_files(hash_):
    out = run(["git", "diff-tree", "--no-commit-id", "-r", "--name-only", hash_], check=False)
    return [f for f in out.splitlines() if f]


def build_candidate_args(args):
    cmd = ["git", "log", "--all", "--format=%H|%s|%ai", "--no-merges"]
    if args.since:
        cmd += [f"--since={args.since}"]
    if args.until:
        cmd += [f"--until={args.until}"]
    if args.hash:
        # Single commit: just use the hash directly
        cmd = ["git", "log", "-1", "--format=%H|%s|%ai", args.hash]
    if args.file and not args.hash:
        cmd += ["--", args.file]
    return cmd


def main():
    parser = argparse.ArgumentParser(description="Search instrumented commits")
    parser.add_argument("--keyword", help="Filter by keyword in plan_contents or subject")
    parser.add_argument("--file", help="Limit to commits touching this file")
    parser.add_argument("--since", help="Only commits after this date")
    parser.add_argument("--until", help="Only commits before this date")
    parser.add_argument("--hash", help="Look up a single commit hash")
    parser.add_argument("--unplanned-only", action="store_true",
                        help="Only return commits with unplanned_changes")
    args = parser.parse_args()

    cmd = build_candidate_args(args)
    raw = run(cmd, check=False)
    if not raw:
        print("[]")
        return

    results = []
    for line in raw.splitlines():
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        hash_, subject, date = parts[0], parts[1], parts[2]

        body = get_commit_body(hash_)
        meta = parse_metadata(body)
        if meta is None:
            continue  # not an instrumented commit

        plan_contents = meta.get("plan_contents")
        unplanned = meta.get("unplanned_changes", [])

        # Keyword filter
        if args.keyword:
            kw = args.keyword.lower()
            in_subject = kw in subject.lower()
            in_plan = kw in (plan_contents or "").lower()
            if not in_subject and not in_plan:
                continue

        # Unplanned-only filter
        if args.unplanned_only and not unplanned:
            continue

        files_changed = get_changed_files(hash_)

        results.append({
            "hash": hash_[:8],
            "full_hash": hash_,
            "subject": subject,
            "date": date,
            "model": meta.get("model"),
            "plan_file": meta.get("plan_file"),
            "plan_contents": plan_contents,
            "unplanned_changes": unplanned,
            "files_changed": files_changed,
        })

    # Newest first (git log already returns newest first, but be explicit)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
