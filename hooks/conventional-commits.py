#!/usr/bin/env python3
import json
import sys
import re

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only validate git commit commands
if tool_name != "Bash" or "git commit" not in command:
    sys.exit(0)

# Check for heredoc format FIRST (before trying to extract message)
if '$(cat <<' in command or 'cat <<' in command:
    user_msg = """🚫 Commit blocked

Situation: You're trying to commit with heredoc syntax
Complication: Hooks run before shell expansion, so heredoc doesn't work
Resolution: Use multiple -m flags instead

git commit -m "feat: your change" \\
           -m "Additional details" \\
           -m "More context if needed"
"""

    technical_reason = f"""❌ Heredoc syntax not supported in commit hooks

Your command uses heredoc ($(cat <<EOF...EOF)) which doesn't work in pre-commit hooks.

**Solution**: Use multiple -m flags instead:

git commit -m "type(scope): short description" \\
  -m "Longer description paragraph 1" \\
  -m "Longer description paragraph 2"

Example:
git commit -m "feat(skill): add Git Flow skill" \\
  -m "Add comprehensive Git Flow implementation" \\
  -m "Includes 8 scripts and rationalization table"

**Why this happens**: Hooks receive the command string before shell expansion,
so $(cat <<EOF) is literal text, not the expanded content."""

    # Output JSON with BOTH systemMessage (for user) and permissionDecisionReason (for Claude)
    output = {
        "systemMessage": f"\n{user_msg}\n",  # Concise message for user
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": technical_reason  # Technical details for Claude
        }
    }
    print(json.dumps(output))
    sys.exit(0)  # Exit 0 with JSON output

# Extract commit message from -m flag
# Handle both -m "message" and -m 'message' formats
match = re.search(r'git commit.*?-m\s+["\']([^"\']+)["\']', command)

if not match:
    # Can't extract message, allow it (might be using git commit without -m)
    sys.exit(0)

commit_msg = match.group(1)

# Check if message follows Conventional Commits format
# Format: type(scope)?: description
# Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
conventional_pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?:\s.+'

if not re.match(conventional_pattern, commit_msg):
    user_msg = f"""🚫 Commit blocked

Situation: Your commit message doesn't follow the required format
Complication: Message must start with a type (feat/fix/docs/etc)
Resolution: Rewrite using this pattern

git commit -m "type: brief description"

Examples:
  feat: add user login
  fix: resolve crash on startup
  docs: update README

Your message: {commit_msg}
"""

    technical_reason = f"""❌ Invalid commit message format

Your message: {commit_msg}

Commit messages must follow Conventional Commits:
  type(scope): description

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation changes
  style:    Code style changes (formatting)
  refactor: Code refactoring
  perf:     Performance improvements
  test:     Adding or updating tests
  chore:    Maintenance tasks
  ci:       CI/CD changes
  build:    Build system changes
  revert:   Revert previous commit

Examples:
  ✅ feat: add user authentication
  ✅ feat(auth): implement JWT tokens
  ✅ fix: resolve memory leak in parser
  ✅ fix(api): handle null responses
  ✅ docs: update API documentation

Invalid:
  ❌ Added new feature (no type)
  ❌ feat:add feature (missing space after colon)
  ❌ feature: add login (wrong type, use 'feat')

💡 Tip: Start your message with one of the types above followed by a colon and space."""

    # Output JSON with BOTH systemMessage (for user) and permissionDecisionReason (for Claude)
    output = {
        "systemMessage": f"\n{user_msg}\n",  # Concise message for user
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": technical_reason  # Technical details for Claude
        }
    }
    print(json.dumps(output))
    sys.exit(0)  # Exit 0 with JSON output

# Allow the command
sys.exit(0)
