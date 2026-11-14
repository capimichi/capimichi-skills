---
name: google-tasks
description: Manage, view, create, update, search, and complete tasks and to-do lists in Google Tasks. Use whenever the user asks to interact with their Google Tasks or to-do list.
---

# Google Tasks Skill

This skill allows the agent to interact with Google Tasks via the official Google Tasks API using an authenticated CLI helper.

## Requirements & Credentials

- **Credentials location**: `~/.config/google-tasks/credentials.json` (OAuth 2.0 Desktop Client ID)
- **Token location**: `~/.local/state/google-tasks/token.json` (Auto-generated OAuth state/session)
- **CLI Helper**: Located at [gtasks.py](./scripts/gtasks.py). Can be executed with `uv run` or directly as an executable.

## Initial Authentication

If `~/.local/state/google-tasks/token.json` does not exist or has expired, run:

```bash
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py auth
```

This opens the Google OAuth consent flow in the browser to generate the local token.

---

## Command Reference

The helper script is executed with:
```bash
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py <command> [options]
```

### 1. List Task Lists
```bash
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py lists
```
Options:
- `--json`: Output raw JSON list objects.

### 2. View Tasks in a List
```bash
# Default list (pending tasks only)
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py list

# Specific list by title or ID
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py list --list "Spesa"

# Include completed tasks
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py list --all

# View only completed tasks
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py list --completed

# JSON output
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py list --json
```

### 3. Add a New Task
```bash
# Simple task in default list
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py add "Comprare pane"

# Task with due date and notes in a specific list
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py add "Pagare bolletta" \
  --list "Personale" \
  --due "tomorrow" \
  --notes "Scadenza fine mese, importo 45 euro"
```
Due date formats accepted:
- Relative: `today`, `tomorrow`, `oggi`, `domani`, `+3d`
- ISO: `YYYY-MM-DD` (e.g. `2026-11-15`)

### 4. Mark Task as Completed
```bash
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py done <task_id> [--list <list>]
```

### 5. Mark Task as Pending (Undo)
```bash
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py undone <task_id> [--list <list>]
```

### 6. Search Tasks
Searches across all task lists (case-insensitive in title and notes):
```bash
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py search "bolletta"
```

### 7. Delete Task
```bash
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py delete <task_id> [--list <list>]
```

### 8. Manage Lists
```bash
# Create a new list
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py add-list "Progetti 2026"

# Delete a list
uv run $USER_SKILLS_DIR/google-tasks/scripts/gtasks.py delete-list <list_id>
```
