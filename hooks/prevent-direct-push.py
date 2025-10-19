#!/usr/bin/env python3
import json
import sys
import subprocess

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})
command = tool_input.get("command", "")

# Only validate git push commands
if tool_name != "Bash" or "git push" not in command:
    sys.exit(0)

# Get current branch
try:
    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        stderr=subprocess.DEVNULL,
        text=True
    ).strip()
except:
    current_branch = ""

# Check if pushing to main or develop
push_cmd = command
is_force_push = "--force" in push_cmd or "-f" in push_cmd

# Check if command or current branch targets protected branches
targets_protected = (
    "origin main" in push_cmd or
    "origin develop" in push_cmd or
    current_branch in ["main", "develop"]
)

# Block direct push to main/develop (unless force push which is already dangerous)
if targets_protected and not is_force_push:
    if current_branch in ["main", "develop"] or "origin main" in push_cmd or "origin develop" in push_cmd:
        user_msg = f"""🚫 Push blocked

Situation: You're pushing to a protected branch ({current_branch})
Complication: main/develop require pull requests for team review
Resolution: Use a feature branch instead

Quick fix:
  git checkout -b feature/your-feature-name
  git push origin feature/your-feature-name

Then create a PR for review.
"""

        technical_reason = f"""❌ Cannot push to protected branch!

**What you tried**: `{command}`
**Current branch**: {current_branch}
**Problem**: Direct pushes to main/develop are blocked by Git Flow policy

**Solution**: Use Git Flow branches instead:

1. **For features**:
   - Create: `/myrs-git-flow:feature <name>` or `git checkout -b feature/<name>`
   - Push: `git push origin feature/<name>`

2. **For releases**:
   - Create: `/myrs-git-flow:release <version>` or `git checkout -b release/v<version>`
   - Push: `git push origin release/v<version>`

3. **For hotfixes**:
   - Create: `/myrs-git-flow:hotfix <name>` or `git checkout -b hotfix/<name>`
   - Push: `git push origin hotfix/<name>`

**Why this matters**: Protected branches require pull requests for code review, CI checks, and team visibility.

💡 **Quick fix**: `git checkout -b feature/<descriptive-name>` then `git push origin feature/<descriptive-name>`"""

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
