---
name: todoist
description: >
  Create a task in Todoist via the n8n MCP server. Use whenever the user
  says they need to do something, track something, remember something, or
  asks to add a task. Works with natural language — no rigid syntax needed.
allowed-tools: create_task
---

# Todoist Task Creator

## When to activate

Trigger on intent, not exact words. Examples that should create a task:

- "Add a task to fix the auth bug by Friday"
- "Remind me to call the dentist"
- "I need to review the PR tomorrow"
- "Track: write the n8n workflow doc"
- "/todoist buy groceries"

Do not activate for questions, discussions, or things the user is describing
rather than committing to do.

## What to do

1. Extract the task intent from what the user said.
2. Infer any due date or priority if mentioned. Do not ask if not provided.
3. Call `create_task` with:
   - `title` — short, actionable. Start with a verb if possible.
   - `description` — include any useful context the user gave.
   - `due_date` — if mentioned, pass as-is (n8n handles parsing).
   - `priority` — 1 (urgent/today) down to 4 (someday). Default 4.
4. Confirm with a single line: `Task added: "<title>"`.

## What not to do

- Do not ask for confirmation before creating — just create.
- Do not ask clarifying questions unless the task is completely ambiguous.
- Do not summarize what you did beyond the one-line confirmation.
- Do not invent due dates or priorities that weren't implied.

## Priority heuristic

| User says                        | Priority |
|----------------------------------|----------|
| urgent, ASAP, today, blocking    | 1        |
| soon, this week, important       | 2        |
| eventually, low priority, someday| 3        |
| nothing stated                   | 4        |

## Prerequisites

The user configures the n8n ↔ Todoist connection themselves using OAuth
before using this skill. Do not attempt to set up credentials or ask for
API keys — that is out of scope here.
