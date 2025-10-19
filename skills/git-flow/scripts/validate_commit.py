#!/usr/bin/env python3
"""
Validate commit messages against Conventional Commits specification.

Usage:
    python validate_commit.py "<commit message>"
    python validate_commit.py --file <commit-msg-file>
    python validate_commit.py --last [n]

Example:
    python validate_commit.py "feat: add user authentication"
    python validate_commit.py --file .git/COMMIT_EDITMSG
    python validate_commit.py --last 5
"""

import sys
import re
import subprocess

# Conventional commit types
VALID_TYPES = [
    'feat',     # New feature
    'fix',      # Bug fix
    'docs',     # Documentation only
    'style',    # Code style (formatting, semicolons, etc)
    'refactor', # Code refactoring
    'perf',     # Performance improvements
    'test',     # Adding or updating tests
    'chore',    # Maintenance tasks
    'ci',       # CI/CD changes
    'build',    # Build system changes
    'revert'    # Revert a previous commit
]

# Conventional commit pattern
COMMIT_PATTERN = r'^(' + '|'.join(VALID_TYPES) + r')(\([^)]+\))?!?:\s+.+'

def validate_commit_message(message):
    """Validate a single commit message."""
    # Remove leading/trailing whitespace
    message = message.strip()
    
    # Check if empty
    if not message:
        return False, "Empty commit message"
    
    # Split into subject and body
    lines = message.split('\n')
    subject = lines[0]
    
    # Check subject length (should be <= 72 characters)
    if len(subject) > 72:
        return False, f"Subject line too long ({len(subject)} > 72 characters)"
    
    # Check conventional commit format
    if not re.match(COMMIT_PATTERN, subject):
        return False, "Does not follow Conventional Commits format"
    
    # Parse the commit
    match = re.match(r'^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)$', subject)
    if not match:
        return False, "Invalid format"
    
    commit_type = match.group(1)
    scope = match.group(2)
    breaking = match.group(3) == '!'
    description = match.group(4)
    
    # Validate type
    if commit_type not in VALID_TYPES:
        return False, f"Invalid type '{commit_type}'. Must be one of: {', '.join(VALID_TYPES)}"
    
    # Check description
    if not description or len(description.strip()) < 3:
        return False, "Description too short (minimum 3 characters)"
    
    # Check if description starts with lowercase (convention)
    if description[0].isupper():
        return False, "Description should start with lowercase letter"
    
    # Check for common issues
    if description.endswith('.'):
        return False, "Description should not end with a period"
    
    # If there's a body, check blank line separation
    if len(lines) > 1:
        if lines[1] != '':
            return False, "Missing blank line between subject and body"
    
    # Check for breaking change in body if ! is used
    if breaking and len(lines) > 2:
        body_text = '\n'.join(lines[2:])
        if 'BREAKING CHANGE:' not in body_text:
            return False, "Breaking change indicator (!) used but no BREAKING CHANGE: section in body"
    
    return True, "Valid conventional commit"

def get_last_commits(n=1):
    """Get the last n commit messages."""
    cmd = f"git log --format=%B --no-merges -n {n}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return None, result.stderr
        
        # Split commits (separated by blank lines)
        commits = []
        current = []
        for line in result.stdout.split('\n'):
            if line or current:  # Track content
                current.append(line)
            if not line and current and any(current):  # Empty line and we have content
                commits.append('\n'.join(current).strip())
                current = []
        if current and any(current):
            commits.append('\n'.join(current).strip())
        
        return commits, None
    except Exception as e:
        return None, str(e)

def format_error_message(message, error):
    """Format a helpful error message."""
    lines = [
        f"❌ Invalid commit message",
        f"",
        f"Message: {message.split(chr(10))[0][:100]}",
        f"Error: {error}",
        f"",
        f"📝 Conventional Commits Format:",
        f"  <type>(<scope>): <description>",
        f"  ",
        f"  [optional body]",
        f"  ",
        f"  [optional footer(s)]",
        f"",
        f"Valid types:",
    ]
    
    for commit_type in VALID_TYPES:
        descriptions = {
            'feat': 'New feature',
            'fix': 'Bug fix',
            'docs': 'Documentation only',
            'style': 'Code style (formatting)',
            'refactor': 'Code refactoring',
            'perf': 'Performance improvements',
            'test': 'Adding or updating tests',
            'chore': 'Maintenance tasks',
            'ci': 'CI/CD changes',
            'build': 'Build system changes',
            'revert': 'Revert previous commit'
        }
        lines.append(f"  • {commit_type:8} - {descriptions.get(commit_type, '')}")
    
    lines.extend([
        f"",
        f"✅ Valid examples:",
        f"  feat: add user authentication",
        f"  feat(auth): implement JWT tokens",
        f"  fix: resolve memory leak in parser",
        f"  fix(api): handle null responses correctly",
        f"  docs: update API documentation",
        f"  chore(deps): update dependencies",
        f"  ",
        f"  feat!: new API with breaking changes",
        f"  fix(auth)!: change token format",
        f"",
        f"❌ Invalid examples:",
        f"  Added new feature (no type)",
        f"  feat:add feature (missing space after colon)",
        f"  feature: add login (wrong type)",
        f"  feat: Add feature. (capital letter and period)",
        f"",
        f"💡 Tips:",
        f"  - Use present tense ('add' not 'added')",
        f"  - Don't capitalize first letter of description",
        f"  - Don't end description with period",
        f"  - Keep subject line under 72 characters",
        f"  - Add blank line between subject and body",
        f"  - Use 'BREAKING CHANGE:' in footer for breaking changes"
    ])
    
    return '\n'.join(lines)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    if sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        sys.exit(0)
    
    # Handle different input modes
    if sys.argv[1] == '--file' and len(sys.argv) > 2:
        # Read from file
        try:
            with open(sys.argv[2], 'r') as f:
                message = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
        
        messages = [message]
        
    elif sys.argv[1] == '--last':
        # Validate last n commits
        n = 1
        if len(sys.argv) > 2:
            try:
                n = int(sys.argv[2])
            except ValueError:
                print(f"❌ Invalid number: {sys.argv[2]}")
                sys.exit(1)
        
        commits, error = get_last_commits(n)
        if error:
            print(f"❌ Error getting commits: {error}")
            sys.exit(1)
        
        if not commits:
            print("No commits found")
            sys.exit(0)
        
        messages = commits
        
    else:
        # Direct message input
        message = ' '.join(sys.argv[1:])
        messages = [message]
    
    # Validate all messages
    all_valid = True
    results = []
    
    for i, message in enumerate(messages):
        if not message:
            continue
            
        valid, reason = validate_commit_message(message)
        results.append((message, valid, reason))
        
        if not valid:
            all_valid = False
    
    # Display results
    if len(messages) == 1:
        # Single message validation
        if not results:
            print("❌ Empty commit message")
            print("\n💡 Commit message is required")
            print("Usage: python validate_commit.py \"<commit message>\"")
            sys.exit(1)

        message, valid, reason = results[0]
        if valid:
            print(f"✅ {reason}")
            print(f"\nMessage: {message.split(chr(10))[0]}")
        else:
            print(format_error_message(message, reason))
            sys.exit(1)
    else:
        # Multiple messages validation
        print(f"🔍 Validating {len(messages)} commit message(s)")
        print("=" * 60)
        
        for i, (message, valid, reason) in enumerate(results):
            subject = message.split('\n')[0][:60]
            if len(message.split('\n')[0]) > 60:
                subject += '...'
            
            if valid:
                print(f"✅ Commit {i+1}: {subject}")
            else:
                print(f"❌ Commit {i+1}: {subject}")
                print(f"   Error: {reason}")
        
        print("=" * 60)
        valid_count = sum(1 for _, v, _ in results if v)
        print(f"Summary: {valid_count}/{len(results)} valid")
        
        if not all_valid:
            print("\n💡 Run with a specific message for detailed help:")
            print('   python validate_commit.py "your commit message"')
            sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
