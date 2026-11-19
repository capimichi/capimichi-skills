---
name: google/tasks
description: Manage, view, create, update, search, and complete tasks and to-do lists in Google Tasks. Use whenever the user asks to interact with their Google Tasks or to-do list.
---

# Google Tasks Skill

This skill allows the agent to interact with Google Tasks via the official Google Tasks API using an authenticated CLI helper based on Click.

## Requirements & Credentials

- **Credentials location**: `~/.config/google-tasks/credentials.json` (OAuth 2.0 Desktop Client ID)
- **Token location**: `~/.local/state/google-tasks/token.json` (Auto-generated OAuth state/session)
- **CLI Helper**: Located at [cli.py](file://$USER_SKILLS_DIR/google/tasks/cli.py).

## Initial Authentication

If `~/.local/state/google-tasks/token.json` does not exist or has expired, run:

```bash
python3 $USER_SKILLS_DIR/google/tasks/cli.py auth
```

This opens the Google OAuth consent flow in the browser to generate the local token.

---

## Command Reference

The helper script is executed with:
```bash
python3 $USER_SKILLS_DIR/google/tasks/cli.py <command> [options]
```

### 1. List Task Lists
```bash
python3 $USER_SKILLS_DIR/google/tasks/cli.py lists
```
Options:
- `--json`: Output raw JSON list objects.

### 2. View Tasks in a List
```bash
# Default list (pending tasks only)
python3 $USER_SKILLS_DIR/google/tasks/cli.py list

# Specific list by title or ID
python3 $USER_SKILLS_DIR/google/tasks/cli.py list --list "Spesa"

# Include completed tasks
python3 $USER_SKILLS_DIR/google/tasks/cli.py list --all

# View only completed tasks
python3 $USER_SKILLS_DIR/google/tasks/cli.py list --completed

# JSON output
python3 $USER_SKILLS_DIR/google/tasks/cli.py list --json
```

### 3. Add a New Task
```bash
# Simple task in default list
python3 $USER_SKILLS_DIR/google/tasks/cli.py add "Comprare pane"

# Task with due date and notes in a specific list
python3 $USER_SKILLS_DIR/google/tasks/cli.py add "Pagare bolletta" \
  --list "Personale" \
  --due "tomorrow" \
  --notes "Scadenza fine mese, importo 45 euro"
```
Due date formats accepted:
- Relative: `today`, `tomorrow`, `oggi`, `domani`, `+3d`
- ISO: `YYYY-MM-DD` (e.g. `2026-11-15`)

### 4. Mark Task as Completed
```bash
python3 $USER_SKILLS_DIR/google/tasks/cli.py done <task_id> [--list <list>]
```

### 5. Mark Task as Pending (Undo)
```bash
python3 $USER_SKILLS_DIR/google/tasks/cli.py undone <task_id> [--list <list>]
```

### 6. Search Tasks
Searches across all task lists (case-insensitive in title and notes):
```bash
python3 $USER_SKILLS_DIR/google/tasks/cli.py search "bolletta"
```

### 7. Delete Task
```bash
python3 $USER_SKILLS_DIR/google/tasks/cli.py delete <task_id> [--list <list>]
```

### 8. Manage Lists
```bash
# Create a new list
python3 $USER_SKILLS_DIR/google/tasks/cli.py add-list "Progetti 2026"

# Delete a list
python3 $USER_SKILLS_DIR/google/tasks/cli.py delete-list <list_id>
```
