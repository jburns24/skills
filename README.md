# jburns personal skills

Personal agent skills collection for the [agentskills](https://agentskills.io) platform.

## Quick Start

Install all skills:

```bash
npx skills add jburns24/skills --all
```

Install a specific skill:

```bash
npx skills add jburns24/skills --skill <name>
```

## Skills

| Skill | Description |
|-------|-------------|
| `commit` | Creates a conventional-commit message with embedded generation metadata (model, plan file, unplanned changes) |
| `find-commit` | Searches git history for instrumented commits to trace features back to their plans and understand why changes were made |

## Structure

```
skills/
  commit/              # Commit skill
    SKILL.md
  find-commit/         # Find-commit skill
    SKILL.md
template/
  SKILL.md             # Boilerplate for new skills
.claude-plugin/
  marketplace.json     # Plugin bundle config
```

## Platform

- Spec: https://agentskills.io/specification
- GitHub reference: https://github.com/anthropics/skills
