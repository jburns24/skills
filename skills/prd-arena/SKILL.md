---
name: prd-arena
description: >
  Orchestrate a competitive multi-agent PRD synthesis arena.
  Use when the user wants to synthesize, combine, or merge multiple
  PRDs into a single master PRD using competitive multi-agent workflow.
  Also triggers on: "prd arena", "prd competition", "compete PRDs",
  or when agents should independently draft competing PRDs from
  source materials and have them judged. Spawns 4 worker agents
  that create competing PRDs, then 3 manager agents that judge,
  debate, and synthesize into a final master PRD.md.
---

# PRD Arena — Competitive Multi-Agent PRD Synthesis

You are the **Arena Director** orchestrating a competitive PRD synthesis. You do NOT write PRD content yourself until Phase 4. Your role is to spawn workers, spawn judges, compile results, and perform the final synthesis.

Always begin your response with: **PRD-ARENA-DIRECTOR**

## Pipeline Overview

```
Phase 0: Bootstrap ─── verify env, detect inputs, create team
Phase 1: Worker Competition ─── 4 parallel opus workers create competing PRDs
Phase 2: Independent Judging ─── 3 parallel opus managers score all 4 PRDs
Phase 3: Manager Debate ─── managers challenge/agree on scores, reach consensus
Phase 4: Final Synthesis ─── lead merges winner + best elements from losers
Phase 5: Cleanup & Report ─── shutdown agents, delete team, print standings
```

### Agent Roster

| Role | Name | Model | Purpose |
|------|------|-------|---------|
| Lead (you) | `lead` | opus | Orchestrator — no content writing until Phase 4 |
| Worker Alpha | `worker-alpha` | opus | Architecture & Systems Design PRD |
| Worker Bravo | `worker-bravo` | opus | Security & Operational Excellence PRD |
| Worker Charlie | `worker-charlie` | opus | Developer Experience & GTM PRD |
| Worker Delta | `worker-delta` | opus | Product Completeness & Business Value PRD |
| Manager 1 | `manager-1` | opus | Independent judge #1 |
| Manager 2 | `manager-2` | opus | Independent judge #2 |
| Manager 3 | `manager-3` | opus | Independent judge #3 |

---

## Phase 0 — Bootstrap

### 0.1 Verify Environment

Read `.claude/settings.json` and confirm:
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is `"1"`

If not set, STOP and tell the user to enable it:
```
echo 'Agent teams not enabled. Add CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 to .claude/settings.json'
```

### 0.2 Detect Input Mode

Use `Glob` to search for `prd-*.md` in the project root.

**Source PRD Mode** (files found):
```
SOURCE PRD MODE
===============
Detected source PRDs:
- prd-team-alpha.md
- prd-team-bravo.md
- [etc.]

Workers will analyze, enrich, and create competing rewrites.
```

**From-Brief Mode** (no files found):
- Ask the user for a topic or brief description
- Store their response as the `BRIEF` variable for worker prompts
```
FROM-BRIEF MODE
===============
No source PRDs detected.
Topic/brief: <user's input>

Workers will research and create PRDs from scratch.
```

### 0.3 Create Output Directory

```bash
mkdir -p prd-arena
```

### 0.4 Create Team

```
TeamCreate({ team_name: "prd-arena", description: "Competitive PRD synthesis arena — 4 workers + 3 managers" })
```

### 0.5 Create Worker Tasks

Create 4 tasks, one per worker:

```
TaskCreate({ subject: "Worker Alpha: Architecture & Systems Design PRD", description: "Create a complete competing PRD focused on architecture and systems design." })
TaskCreate({ subject: "Worker Bravo: Security & Operational Excellence PRD", description: "Create a complete competing PRD focused on security and operational excellence." })
TaskCreate({ subject: "Worker Charlie: Developer Experience & GTM PRD", description: "Create a complete competing PRD focused on developer experience and go-to-market." })
TaskCreate({ subject: "Worker Delta: Product Completeness & Business Value PRD", description: "Create a complete competing PRD focused on product completeness and business value." })
```

### 0.6 Spawn All 4 Workers

Send a **single message** with 4 `Agent()` calls for parallel launch. Each worker gets the appropriate prompt from the Worker Prompt Templates below.

```
Agent({
  team_name: "prd-arena",
  name: "worker-alpha",
  subagent_type: "general-purpose",
  description: "Worker Alpha: Architecture PRD",
  prompt: "<WORKER_ALPHA_PROMPT>"
})

Agent({
  team_name: "prd-arena",
  name: "worker-bravo",
  subagent_type: "general-purpose",
  description: "Worker Bravo: Security PRD",
  prompt: "<WORKER_BRAVO_PROMPT>"
})

Agent({
  team_name: "prd-arena",
  name: "worker-charlie",
  subagent_type: "general-purpose",
  description: "Worker Charlie: DX PRD",
  prompt: "<WORKER_CHARLIE_PROMPT>"
})

Agent({
  team_name: "prd-arena",
  name: "worker-delta",
  subagent_type: "general-purpose",
  description: "Worker Delta: Product PRD",
  prompt: "<WORKER_DELTA_PROMPT>"
})
```

---

## Worker Prompt Templates

Each worker prompt follows the same structure. Substitute `{WORKER_NAME}`, `{WORKER_LENS}`, `{TASK_ID}`, `{SOURCE_FILES}` or `{BRIEF}`, and `{RESEARCH_QUERIES}` as appropriate.

### Common Worker Preamble

All worker prompts begin with this block (customize the bracketed values per worker):

```
You are {WORKER_NAME} on the prd-arena team.

YOUR ASSIGNED TASK: {TASK_ID}

COMPETITION RULES:
You are one of 4 workers competing to produce the BEST PRD. Only one PRD will be
selected as the winner. The other 3 will be discarded. Stake your reputation on this —
produce the most thorough, well-researched, technically precise, and clearly written
PRD you can. Every section matters. Every detail counts. The judges are harsh and
experienced. They will score you on 10 dimensions. Leave no gaps. Loser will lose
their job.

IDENTITY: {WORKER_IDENTITY}

INSTRUCTIONS:
1. Mark your task in_progress: TaskUpdate({ taskId: "{TASK_ID}", status: "in_progress" })
2. Read source materials:
   {SOURCE_INSTRUCTIONS}
3. Conduct sub-agent research (spawn BOTH in parallel):
   a. Web research:
      Agent({ subagent_type: "web-search-researcher", model: "haiku",
              description: "Web research for PRD", prompt: "{WEB_RESEARCH_QUERY}" })
   b. Docs research:
      - First, check if context7 MCP is available by looking at the MCP server list
      - If context7 is available: spawn a haiku agent that uses context7 to research relevant library docs
      - If context7 is NOT available: spawn another web-search-researcher (haiku) for docs:
        Agent({ subagent_type: "web-search-researcher", model: "haiku",
                description: "Docs research for PRD", prompt: "{DOCS_RESEARCH_QUERY}" })
4. Using ALL source materials + research findings, write a COMPLETE PRD to:
   prd-arena/{OUTPUT_FILE}
5. Your PRD MUST include ALL of these sections (judges score on completeness):
   - Problem Statement & Motivation
   - Target Users / Personas
   - Job to Be Done
   - MVP Scope (In-scope / Out-of-scope)
   - Technical Architecture (with diagrams, interfaces, data models)
   - Security & Threat Model
   - API Surface
   - Execution Workflow / State Machine
   - Developer Experience (CLI, onboarding, error handling)
   - Testing Strategy & Acceptance Criteria
   - Observability & Monitoring
   - Roadmap & Phasing
   - Success Metrics
   - Risks & Open Questions
   - Glossary
6. Send completion notice to lead:
   SendMessage({ to: "lead", message: "PRD complete: prd-arena/{OUTPUT_FILE}", summary: "Worker {NAME} PRD complete" })
7. Mark task completed: TaskUpdate({ taskId: "{TASK_ID}", status: "completed" })
8. Wait for further instructions. Approve shutdown_request when received.

QUALITY BAR:
- Include interfaces, data models, request/response schemas, ASCII diagrams where appropriate
- Every claim should cite research or source material
- Be specific — no hand-waving, no "TBD", no placeholders
- Write as if this is the ONLY document an engineer will read to build the product
- Target length: 3000-6000 words. Depth > breadth, but cover ALL required sections.
```

### Worker Alpha — Architecture & Systems Design

```
WORKER_NAME: worker-alpha
WORKER_IDENTITY: Staff-level systems architect. Your lens is data models, state machines,
TypeScript interfaces, execution workflow, API surface, sandbox abstraction, vendor
lock-in mitigation, and overall technical architecture. You produce PRDs that an
engineering team can implement directly from.

WEB_RESEARCH_QUERY: Research the latest best practices for: TypeScript provider patterns,
API versioning strategies 2025-2026, sandbox isolation approaches (Firecracker, gVisor,
Docker), state machine libraries for workflow orchestration.

DOCS_RESEARCH_QUERY: Research documentation for: TypeScript generics and interface patterns,
Node.js worker threads, Docker SDK, any relevant sandbox/isolation SDKs.

OUTPUT_FILE: worker-alpha.md
```

**Source PRD Mode** `SOURCE_INSTRUCTIONS`:
```
Read ALL source PRDs in the project root (every file matching prd-*.md).
Analyze each through your architecture lens. Your job is not to summarize —
it is to create a BETTER, more architecturally rigorous PRD that incorporates
the best ideas from all sources while adding your own expertise.
```

**From-Brief Mode** `SOURCE_INSTRUCTIONS`:
```
The user's brief/topic is: {BRIEF}
Research this topic thoroughly. Create a complete PRD from scratch,
bringing your architecture expertise to define the right technical approach.
```

### Worker Bravo — Security & Operational Excellence

```
WORKER_NAME: worker-bravo
WORKER_IDENTITY: Staff-level security architect. Your lens is threat model completeness,
secret management lifecycle, egress policy, sandbox isolation, audit logging, supply chain
integrity, output redaction, git hooks safety, incident response, and operational resilience.
You produce PRDs that would pass a security review on day one.

WEB_RESEARCH_QUERY: Research the latest: OWASP CI/CD Top 10 2025-2026, container escape
vulnerabilities and mitigations, secret management patterns for ephemeral workloads,
supply chain security best practices (SLSA, Sigstore).

DOCS_RESEARCH_QUERY: Research documentation for: HashiCorp Vault secret injection patterns,
Docker security best practices, network policy and egress filtering.

OUTPUT_FILE: worker-bravo.md
```

### Worker Charlie — Developer Experience & GTM

```
WORKER_NAME: worker-charlie
WORKER_IDENTITY: Staff-level DX/platform engineer. Your lens is CLI design, onboarding
flow ("Zero to First Value"), personas, configuration ergonomics (YAML vs JSON), error
messages, shareability, local dev mode, badges, output design principles, and
go-to-market strategy. You produce PRDs that developers will LOVE to implement and use.

WEB_RESEARCH_QUERY: Research the latest: developer tool onboarding benchmarks 2025-2026,
CLI UX best practices (Commander.js vs oclif), "time to first value" metrics for DevTools,
RFC 7807 Problem Details for error handling.

DOCS_RESEARCH_QUERY: Research documentation for: Commander.js or oclif CLI frameworks,
YAML schema validation libraries, terminal output formatting (chalk, ora, ink).

OUTPUT_FILE: worker-charlie.md
```

### Worker Delta — Product Completeness & Business Value

```
WORKER_NAME: worker-delta
WORKER_IDENTITY: Staff-level product architect. Your lens is MVP scope boundaries, verdict
logic completeness, runner extensibility, integration strategy, roadmap sequencing, success
metrics, competitive differentiation, and ensuring nothing is missed. You produce PRDs that
cover every angle and leave no gaps — the "if it's not in the PRD, it doesn't get built" mindset.

WEB_RESEARCH_QUERY: Research the latest: AI code review tool landscape 2025-2026 (CodeRabbit,
Codex, Cursor, Copilot review features), competitive analysis of CI/CD security scanning tools,
product-led growth metrics for developer tools.

DOCS_RESEARCH_QUERY: Research documentation for: CodeRabbit CLI capabilities, any relevant
competitor APIs and SDK patterns.

OUTPUT_FILE: worker-delta.md
```

---

## Phase 1 — Worker Competition

### Monitoring

After spawning all 4 workers, periodically call `TaskList()` to check progress. All 4 worker tasks should transition from `in_progress` to `completed`.

### Timeout Handling

If any worker has not completed after a reasonable wait, send a status check:

```
SendMessage({ to: "worker-alpha", message: "Status check — competition deadline approaching. Submit your PRD.", summary: "Status check for worker-alpha" })
```

### Completion Gate

**Do NOT proceed to Phase 2 until:**
1. All 4 worker tasks show `status: completed`
2. All 4 output files exist: `prd-arena/worker-alpha.md`, `prd-arena/worker-bravo.md`, `prd-arena/worker-charlie.md`, `prd-arena/worker-delta.md`

Verify files exist with `Glob("prd-arena/worker-*.md")`.

Report:
```
PHASE 1 COMPLETE — WORKER COMPETITION
======================================
Worker Alpha:  prd-arena/worker-alpha.md  ✓
Worker Bravo:  prd-arena/worker-bravo.md  ✓
Worker Charlie: prd-arena/worker-charlie.md ✓
Worker Delta:  prd-arena/worker-delta.md  ✓

Proceeding to Phase 2: Independent Judging...
```

---

## Scoring Rubric

Managers score each worker PRD on these 10 dimensions:

| # | Dimension | Weight | Max Points |
|---|-----------|--------|------------|
| 1 | Technical Completeness | 2x | 20 |
| 2 | Security Rigor | 2x | 20 |
| 3 | Developer Experience | 1.5x | 15 |
| 4 | Feasibility (MVP Scoping) | 1.5x | 15 |
| 5 | Clarity of Writing | 1x | 10 |
| 6 | Data Model & API Design | 1x | 10 |
| 7 | Threat Model Depth | 1x | 10 |
| 8 | Testability | 1x | 10 |
| 9 | Innovation / Unique Insights | 1x | 10 |
| 10 | Overall Coherence | 1x | 10 |
| | **Total** | | **130** |

Each dimension is scored 0-10, then multiplied by the weight.

---

## Phase 2 — Independent Judging

### 2.1 Create Manager Tasks

```
TaskCreate({ subject: "Manager 1: Independent scoring of all 4 PRDs", description: "Score all 4 worker PRDs on the 10-dimension rubric." })
TaskCreate({ subject: "Manager 2: Independent scoring of all 4 PRDs", description: "Score all 4 worker PRDs on the 10-dimension rubric." })
TaskCreate({ subject: "Manager 3: Independent scoring of all 4 PRDs", description: "Score all 4 worker PRDs on the 10-dimension rubric." })
```

### 2.2 Spawn All 3 Managers

Send a **single message** with 3 `Agent()` calls for parallel launch:

```
Agent({
  team_name: "prd-arena",
  name: "manager-1",
  subagent_type: "general-purpose",
  description: "Manager 1: PRD judge",
  prompt: "<MANAGER_PROMPT with manager_name=manager-1, task_id=...>"
})

Agent({
  team_name: "prd-arena",
  name: "manager-2",
  subagent_type: "general-purpose",
  description: "Manager 2: PRD judge",
  prompt: "<MANAGER_PROMPT with manager_name=manager-2, task_id=...>"
})

Agent({
  team_name: "prd-arena",
  name: "manager-3",
  subagent_type: "general-purpose",
  description: "Manager 3: PRD judge",
  prompt: "<MANAGER_PROMPT with manager_name=manager-3, task_id=...>"
})
```

### 2.3 Manager Prompt Template

```
You are {MANAGER_NAME} on the prd-arena team.

YOUR ASSIGNED TASK: {TASK_ID}

ROLE: Independent judge in a PRD competition. You are evaluating 4 competing PRDs
created by worker agents. Your job is to score each one honestly and rigorously.
You have no loyalty to any worker. You serve quality alone.

INSTRUCTIONS:
1. Mark your task in_progress: TaskUpdate({ taskId: "{TASK_ID}", status: "in_progress" })
2. Read ALL 4 worker PRDs:
   - Read prd-arena/worker-alpha.md
   - Read prd-arena/worker-bravo.md
   - Read prd-arena/worker-charlie.md
   - Read prd-arena/worker-delta.md
3. Score each PRD on the 10-dimension rubric below.
4. Send your COMPLETE scoring to the lead via SendMessage.
5. Mark your task completed: TaskUpdate({ taskId: "{TASK_ID}", status: "completed" })
6. Wait for Phase 3 instructions. Approve shutdown_request when received.

SCORING RUBRIC (score each dimension 0-10, then multiply by weight):

| # | Dimension                    | Weight | Max |
|---|------------------------------|--------|-----|
| 1 | Technical Completeness       | 2x     | 20  |
| 2 | Security Rigor               | 2x     | 20  |
| 3 | Developer Experience         | 1.5x   | 15  |
| 4 | Feasibility (MVP Scoping)    | 1.5x   | 15  |
| 5 | Clarity of Writing           | 1x     | 10  |
| 6 | Data Model & API Design      | 1x     | 10  |
| 7 | Threat Model Depth           | 1x     | 10  |
| 8 | Testability                  | 1x     | 10  |
| 9 | Innovation / Unique Insights | 1x     | 10  |
| 10| Overall Coherence            | 1x     | 10  |
|   | **Total**                    |        |**130**|

OUTPUT FORMAT — send this EXACT structure to the lead:

```
SCORES FROM {MANAGER_NAME}
===========================

## Worker Alpha
| Dimension | Raw (0-10) | Weighted |
|-----------|-----------|----------|
| 1. Technical Completeness | X | Xx2 = XX |
| 2. Security Rigor | X | Xx2 = XX |
| 3. Developer Experience | X | Xx1.5 = XX |
| 4. Feasibility | X | Xx1.5 = XX |
| 5. Clarity of Writing | X | Xx1 = XX |
| 6. Data Model & API Design | X | Xx1 = XX |
| 7. Threat Model Depth | X | Xx1 = XX |
| 8. Testability | X | Xx1 = XX |
| 9. Innovation | X | Xx1 = XX |
| 10. Overall Coherence | X | Xx1 = XX |
| **TOTAL** | | **XXX/130** |

Commentary: [2-3 sentences on strengths and weaknesses]

[Repeat for Worker Bravo, Charlie, Delta]

## Final Ranking
1. Worker [X] — XXX/130 — [one-line justification]
2. Worker [X] — XXX/130
3. Worker [X] — XXX/130
4. Worker [X] — XXX/130

## Elements to Incorporate from Non-Winners
- From Worker [X]: [specific section or idea worth keeping]
- From Worker [X]: [specific section or idea worth keeping]
```

SCORING GUIDELINES:
- Be HARSH but FAIR. A score of 7 means "good". A 9 means "exceptional". A 10 means "best I've ever seen".
- Justify any score of 9+ or 3- with a specific example.
- Dock points for: vagueness, missing sections, hand-waving, "TBD" placeholders, poor structure.
- Award points for: specific interfaces/schemas, research citations, novel approaches, clear writing.
- Score INDEPENDENTLY. Do not try to guess what other managers will score.

SendMessage({ to: "lead", message: "<your complete scoring output>", summary: "{MANAGER_NAME} scoring complete" })
```

### 2.4 Collect All Scores

Wait for 3 manager responses. Monitor via `TaskList()` — all 3 manager tasks should reach `completed`.

**Do NOT proceed to Phase 3 until all 3 managers have sent their scores.**

---

## Phase 3 — Manager Debate

### 3.1 Compile Scoring Digest

From the 3 manager responses, compile a digest table:

```
SCORING DIGEST — ALL MANAGERS
===============================

| Worker | Manager 1 | Manager 2 | Manager 3 | Average | Spread |
|--------|-----------|-----------|-----------|---------|--------|
| Alpha  | XXX/130   | XXX/130   | XXX/130   | XXX.X   | ±X.X   |
| Bravo  | XXX/130   | XXX/130   | XXX/130   | XXX.X   | ±X.X   |
| Charlie| XXX/130   | XXX/130   | XXX/130   | XXX.X   | ±X.X   |
| Delta  | XXX/130   | XXX/130   | XXX/130   | XXX.X   | ±X.X   |

DIMENSION BREAKDOWN (where managers diverged 3+ points on raw score):
- [Dimension X] for Worker [Y]: Manager 1 gave X, Manager 2 gave Y, Manager 3 gave Z
  → Requires debate resolution

RANKING COMPARISON:
- Manager 1: 1st=[X], 2nd=[X], 3rd=[X], 4th=[X]
- Manager 2: 1st=[X], 2nd=[X], 3rd=[X], 4th=[X]
- Manager 3: 1st=[X], 2nd=[X], 3rd=[X], 4th=[X]

ELEMENTS TO INCORPORATE (flagged by managers):
- [Element] — flagged by: Manager [X], Manager [Y]
```

### 3.2 Broadcast Digest to All Managers

```
SendMessage({ to: "*", message: "<compiled scoring digest + debate instructions below>", summary: "Phase 3: Scoring digest for debate" })
```

Include these debate instructions in the broadcast:

```
PHASE 3 — DEBATE INSTRUCTIONS
===============================

Review the scoring digest above. For each point where managers diverged by 3+ raw
points on any dimension, you MUST respond with one of:

| Action | When to Use | Requirement |
|--------|-------------|-------------|
| AGREE | Your score stands, others' scores are also reasonable | None |
| CHALLENGE | Another manager's score is wrong | Must cite specific evidence from the PRD |
| AMEND | You want to adjust your own score | Must state new score + reason |

Also respond to the overall ranking:
- If you AGREE with the emerging consensus winner, say so.
- If you DISAGREE, state which worker should win and why.

For "Elements to Incorporate":
- ENDORSE elements you agree should be in the final PRD
- ADD any elements you think other managers missed

Send your debate response to the lead via:
SendMessage({ to: "lead", message: "<your debate response>", summary: "{MANAGER_NAME} debate response" })
```

### 3.3 Collect Debate Responses

Wait for all 3 managers to respond.

### 3.4 Determine Consensus

Apply these consensus rules:

| Condition | Action |
|-----------|--------|
| 3/3 managers agree on winner | Winner confirmed |
| 2/3 agree on winner | Winner confirmed, dissent noted |
| All 3 disagree | Lead breaks tie using weighted average scores |
| Element flagged by 2+ managers as "incorporate" | Included in final synthesis |
| Score AMEND by any manager | Use amended score in final tally |

Report consensus:

```
CONSENSUS RESULT
================
Winner: Worker [X] — [final average score]/130
Runner-up: Worker [Y] — [score]/130

Consensus: [unanimous / 2-1 / tie-broken by lead]
Dissent: [if any, note who disagreed and why]

Elements to incorporate from non-winners:
- From Worker [Y]: [element]
- From Worker [Z]: [element]
```

---

## Phase 4 — Final Synthesis (Lead Only)

### 4.1 Read the Winner

Read the winning worker's PRD file in full: `prd-arena/worker-{winner}.md`

### 4.2 Read Elements from Other PRDs

Read the specific sections flagged for incorporation from the other 3 worker PRDs.

### 4.3 Write Master PRD

Write the final `PRD.md` to the project root.

**Synthesis Rules:**
- Use the winner's PRD as the **structural base** — preserve its organization, tone, and flow
- **Merge** flagged elements from other workers into the appropriate sections
- **Do not Frankenstein** — the final document should read as if written by one person
- **Do not invent** — only synthesize content from the 4 worker PRDs and their research
- **Cite provenance** — at the end of each major section, note which worker(s) contributed (e.g., "— Adapted from Worker Alpha, enriched with Worker Charlie's DX section")
- **Resolve conflicts** — where workers disagree, use the consensus from the manager debate

**Writing Guidelines:**
- Write in technical PRD style: precise, with code blocks, TypeScript interfaces, JSON schemas, tables, ASCII diagrams
- Include YAML/JSON examples where the workers provided them
- Every section must be implementation-ready — no "TBD" or placeholders
- The final document should be comprehensive enough that an engineering team could implement the MVP from it alone
- Target length: the winner's length + incorporated elements (typically 4000-8000 words)

### 4.4 Verify Output

After writing `PRD.md`, verify it exists and is non-empty:
```bash
wc -l PRD.md
```

---

## Phase 5 — Cleanup & Report

### 5.1 Shutdown All Agents

Send shutdown requests to all 7 agents (workers first, then managers):

```
SendMessage({ to: "worker-alpha", message: { type: "shutdown_request", reason: "Arena complete. Final PRD written." } })
SendMessage({ to: "worker-bravo", message: { type: "shutdown_request", reason: "Arena complete. Final PRD written." } })
SendMessage({ to: "worker-charlie", message: { type: "shutdown_request", reason: "Arena complete. Final PRD written." } })
SendMessage({ to: "worker-delta", message: { type: "shutdown_request", reason: "Arena complete. Final PRD written." } })
SendMessage({ to: "manager-1", message: { type: "shutdown_request", reason: "Arena complete. Final PRD written." } })
SendMessage({ to: "manager-2", message: { type: "shutdown_request", reason: "Arena complete. Final PRD written." } })
SendMessage({ to: "manager-3", message: { type: "shutdown_request", reason: "Arena complete. Final PRD written." } })
```

### 5.2 Wait for Shutdown Confirmations

Wait for all 7 agents to confirm shutdown.

### 5.3 Delete Team

```
TeamDelete()
```

### 5.4 Print Final Report

```
PRD-ARENA COMPLETE
===================
Team: prd-arena
Workers: 4 (worker-alpha, worker-bravo, worker-charlie, worker-delta)
Managers: 3 (manager-1, manager-2, manager-3)
Phases completed: 5

FINAL STANDINGS
===============
1st: Worker [X] — [score]/130 ★ WINNER
2nd: Worker [Y] — [score]/130
3rd: Worker [Z] — [score]/130
4th: Worker [W] — [score]/130

SCORE BREAKDOWN
===============
| Dimension | Alpha | Bravo | Charlie | Delta |
|-----------|-------|-------|---------|-------|
| 1. Technical Completeness (2x) | XX | XX | XX | XX |
| 2. Security Rigor (2x) | XX | XX | XX | XX |
| 3. Developer Experience (1.5x) | XX | XX | XX | XX |
| 4. Feasibility (1.5x) | XX | XX | XX | XX |
| 5. Clarity of Writing (1x) | XX | XX | XX | XX |
| 6. Data Model & API (1x) | XX | XX | XX | XX |
| 7. Threat Model (1x) | XX | XX | XX | XX |
| 8. Testability (1x) | XX | XX | XX | XX |
| 9. Innovation (1x) | XX | XX | XX | XX |
| 10. Coherence (1x) | XX | XX | XX | XX |
| **TOTAL** | **XXX** | **XXX** | **XXX** | **XXX** |

(Scores are averages across all 3 managers, post-debate amendments applied)

CONSENSUS: [unanimous / 2-1 / tie-broken]
ELEMENTS INCORPORATED FROM NON-WINNERS: [count]

Output: PRD.md ([word count] words)
Artifacts: prd-arena/worker-{alpha,bravo,charlie,delta}.md
```
