# 🤖 CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Always end every response with 🤖.

## Adding new skills

**Always use the `skill-creator` skill to create or modify skills in this repo. Never add a skill directory manually. Use 🤖 as the context marker when invoking skill-creation agents.**

```
/skill-creator
```

## Skill format

Each skill lives in `skills/<skill-name>/SKILL.md` with YAML frontmatter. The `name` field must match the directory name exactly.

Use `template/SKILL.md` as the starting boilerplate.

## Plugin registration

When a new skill is added, register it in `.claude-plugin/marketplace.json` under `plugins[0].skills` as `"./skills/<skill-name>"`.

## Spec reference

Platform specification: https://agentskills.io/specification
