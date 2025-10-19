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

# Only validate git checkout -b commands
if tool_name != "Bash" or "git checkout -b" not in command:
    sys.exit(0)

# Extract branch name
match = re.search(r'git checkout -b\s+([^\s]+)', command)
if not match:
    sys.exit(0)

branch_name = match.group(1)

# Allow main and develop branches
if branch_name in ["main", "develop"]:
    sys.exit(0)

# Validate Git Flow naming convention
if not re.match(r'^(feature|release|hotfix)/', branch_name):
    user_msg = f"""🚫 Branch creation blocked

Situation: Branch name doesn't follow Git Flow convention
Complication: Name must start with feature/, release/, or hotfix/
Resolution: Use a valid Git Flow branch name

Your branch: {branch_name}

Correct patterns:
  feature/add-user-login
  release/v1.2.0
  hotfix/fix-crash
"""

    technical_reason = f"""❌ Invalid Git Flow branch name: {branch_name}

Git Flow branches must follow these patterns:
  • feature/<descriptive-name>
  • release/v<MAJOR>.<MINOR>.<PATCH>
  • hotfix/<descriptive-name>

Examples:
  ✅ feature/user-authentication
  ✅ release/v1.2.0
  ✅ hotfix/critical-security-fix

Invalid:
  ❌ {branch_name} (missing Git Flow prefix)
  ❌ feat/something (use 'feature/' not 'feat/')
  ❌ fix/bug (use 'hotfix/' not 'fix/')

💡 Use Git Flow commands instead:
  /feature <name>  - Create feature branch
  /release <version> - Create release branch
  /hotfix <name>   - Create hotfix branch"""

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

# Validate release version format
if branch_name.startswith("release/"):
    if not re.match(r'^release/v\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$', branch_name):
        user_msg = f"""🚫 Branch creation blocked

Situation: Release branch has invalid version format
Complication: Must use semantic versioning (vMAJOR.MINOR.PATCH)
Resolution: Use proper version format

Your branch: {branch_name}

Correct format:
  release/v1.2.0
  release/v2.0.0-beta.1
"""

        technical_reason = f"""❌ Invalid release version: {branch_name}

Release branches must follow semantic versioning:
  release/vMAJOR.MINOR.PATCH[-prerelease]

Valid examples:
  ✅ release/v1.0.0
  ✅ release/v2.1.3
  ✅ release/v1.0.0-beta.1

Invalid:
  ❌ release/1.0.0 (missing 'v' prefix)
  ❌ release/v1.0 (incomplete version)
  ❌ {branch_name}

💡 Use: /release v1.2.0"""

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
