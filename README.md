# jburns personal skills

Personal agent skills collection for the [agentskills](https://agentskills.io) platform.

## Adding new skills

**Always use the `skill-creator` skill to create or modify skills in this repo. Never add a skill directory manually. Use 🤖 as the context marker when invoking skill-creation agents.**

```
/skill-creator
```

## Structure

```
skills/
  hello-world/         # Example placeholder skill
    SKILL.md
spec/
  agent-skills-spec.md # Link to platform specification
template/
  SKILL.md             # Boilerplate for new skills
.claude-plugin/
  marketplace.json     # Plugin bundle config
```

## Platform

- Spec: https://agentskills.io/specification
- GitHub reference: https://github.com/anthropics/skills
