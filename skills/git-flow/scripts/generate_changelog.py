#!/usr/bin/env python3
"""
Generate or update CHANGELOG.md from conventional commits.

Usage:
    python generate_changelog.py [--version <version>] [--from-tag <tag>]

Example:
    python generate_changelog.py
    python generate_changelog.py --version v1.2.0
    python generate_changelog.py --from-tag v1.0.0 --version v1.1.0
"""

import subprocess
import sys
import os
from datetime import datetime
import re

def run_command(cmd, check=False):
    """Execute a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            return None, result.stderr
        return result.stdout.strip(), None
    except Exception as e:
        return None, str(e)

def get_latest_tag():
    """Get the latest tag."""
    output, _ = run_command("git describe --tags --abbrev=0", check=False)
    return output if output and "fatal" not in output else None

def get_commits_since_tag(tag=None):
    """Get commits since the specified tag with full commit info."""
    if not tag:
        cmd = "git log --pretty=format:'%H|%s|%b|%an|%ae|%ad' --date=short"
    else:
        cmd = f"git log {tag}..HEAD --pretty=format:'%H|%s|%b|%an|%ae|%ad' --date=short"
    
    output, _ = run_command(cmd, check=False)
    if output:
        commits = []
        for line in output.split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 6:
                    commits.append({
                        'hash': parts[0][:7],  # Short hash
                        'subject': parts[1],
                        'body': parts[2],
                        'author': parts[3],
                        'email': parts[4],
                        'date': parts[5]
                    })
        return commits
    return []

def parse_commit_message(commit):
    """Parse a conventional commit message."""
    subject = commit['subject']
    
    # Check for conventional commit format
    pattern = r'^(\w+)(?:\(([^)]+)\))?!?:\s*(.+)$'
    match = re.match(pattern, subject)
    
    if match:
        commit_type = match.group(1)
        scope = match.group(2)
        description = match.group(3)
        
        # Check for breaking change indicator in subject
        breaking = '!' in subject.split(':')[0]
        
        return {
            'type': commit_type,
            'scope': scope,
            'description': description,
            'breaking': breaking or 'BREAKING CHANGE' in commit.get('body', ''),
            'raw': subject,
            'hash': commit['hash'],
            'author': commit['author']
        }
    
    return {
        'type': 'other',
        'scope': None,
        'description': subject,
        'breaking': False,
        'raw': subject,
        'hash': commit['hash'],
        'author': commit['author']
    }

def categorize_commits(commits):
    """Categorize commits by type."""
    categories = {
        'breaking': [],
        'feat': [],
        'fix': [],
        'perf': [],
        'refactor': [],
        'docs': [],
        'style': [],
        'test': [],
        'build': [],
        'ci': [],
        'chore': [],
        'revert': [],
        'other': []
    }
    
    for commit in commits:
        parsed = parse_commit_message(commit)
        
        # Add to breaking changes if applicable
        if parsed['breaking']:
            categories['breaking'].append(parsed)
        
        # Add to type category
        commit_type = parsed['type']
        if commit_type in categories:
            categories[commit_type].append(parsed)
        else:
            categories['other'].append(parsed)
    
    return categories

def format_commit_line(commit):
    """Format a single commit line for the changelog."""
    if commit['scope']:
        line = f"- **{commit['scope']}**: {commit['description']}"
    else:
        line = f"- {commit['description']}"
    
    # Add commit hash reference
    line += f" ([{commit['hash']}])"
    
    return line

def generate_changelog_section(version, categories, date=None):
    """Generate changelog section for a version."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    lines = []
    lines.append(f"## [{version}] - {date}\n")
    
    # Breaking changes - most important
    if categories['breaking']:
        lines.append("### ⚠️ BREAKING CHANGES\n")
        for commit in categories['breaking']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Features
    if categories['feat']:
        lines.append("### ✨ Features\n")
        for commit in categories['feat']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Bug fixes
    if categories['fix']:
        lines.append("### 🐛 Bug Fixes\n")
        for commit in categories['fix']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Performance improvements
    if categories['perf']:
        lines.append("### ⚡ Performance Improvements\n")
        for commit in categories['perf']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Code refactoring
    if categories['refactor']:
        lines.append("### ♻️ Code Refactoring\n")
        for commit in categories['refactor']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Reverts
    if categories['revert']:
        lines.append("### ⏪ Reverts\n")
        for commit in categories['revert']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Documentation
    if categories['docs']:
        lines.append("### 📚 Documentation\n")
        for commit in categories['docs']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Tests
    if categories['test']:
        lines.append("### 🧪 Tests\n")
        for commit in categories['test']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Build and CI
    build_ci = categories['build'] + categories['ci']
    if build_ci:
        lines.append("### 🔧 Build System & CI\n")
        for commit in build_ci:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Style changes
    if categories['style']:
        lines.append("### 💄 Styling\n")
        for commit in categories['style']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Maintenance
    if categories['chore']:
        lines.append("### 🔨 Maintenance\n")
        for commit in categories['chore']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    # Other changes
    if categories['other']:
        lines.append("### 📝 Other Changes\n")
        for commit in categories['other']:
            lines.append(format_commit_line(commit))
        lines.append("")
    
    return '\n'.join(lines)

def update_changelog_file(new_content, version):
    """Update or create CHANGELOG.md file."""
    changelog_path = "CHANGELOG.md"
    
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r') as f:
            existing = f.read()
        
        # Check if version already exists
        if f"## [{version}]" in existing:
            print(f"⚠️  Version {version} already exists in CHANGELOG.md")
            response = input("Overwrite existing entry? [y/N]: ").strip().lower()
            if response != 'y':
                return False
            
            # Remove existing version section
            pattern = rf"## \[{re.escape(version)}\].*?(?=## \[|$)"
            existing = re.sub(pattern, '', existing, flags=re.DOTALL)
        
        # Insert new content after header
        if "# Changelog" in existing or "# CHANGELOG" in existing:
            # Find the header line
            lines = existing.split('\n')
            header_index = -1
            for i, line in enumerate(lines):
                if line.startswith('# Changelog') or line.startswith('# CHANGELOG'):
                    header_index = i
                    break
            
            if header_index >= 0:
                # Insert after header (and potential blank line)
                insert_index = header_index + 1
                if insert_index < len(lines) and lines[insert_index].strip() == '':
                    insert_index += 1
                
                lines.insert(insert_index, new_content)
                updated_content = '\n'.join(lines)
            else:
                updated_content = f"# Changelog\n\n{new_content}\n{existing}"
        else:
            updated_content = f"# Changelog\n\n{new_content}\n{existing}"
    else:
        # Create new file
        updated_content = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{new_content}"""
    
    # Write the file
    with open(changelog_path, 'w') as f:
        f.write(updated_content)
    
    return True

def main():
    # Parse arguments
    version = None
    from_tag = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--version' and i + 1 < len(sys.argv):
            version = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--from-tag' and i + 1 < len(sys.argv):
            from_tag = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ['-h', '--help']:
            print(__doc__)
            sys.exit(0)
        else:
            i += 1
    
    print("📝 Generating Changelog")
    print("=" * 60)
    
    # Get version if not provided
    if not version:
        # Try to get from current branch name
        current_branch, _ = run_command("git branch --show-current")
        if current_branch and current_branch.startswith("release/"):
            version = current_branch.replace("release/", "")
            print(f"📌 Detected version from branch: {version}")
        else:
            # Suggest next version
            from_tag = from_tag or get_latest_tag()
            if from_tag:
                # Simple increment of patch version
                parts = from_tag.lstrip('v').split('.')
                if len(parts) >= 3:
                    try:
                        major = int(parts[0])
                        minor = int(parts[1])
                        patch = int(parts[2].split('-')[0])
                        version = f"v{major}.{minor}.{patch + 1}"
                        print(f"📌 Suggested version: {version}")
                    except:
                        version = "v0.0.1"
            else:
                version = "v0.0.1"
                print(f"📌 No previous version found, using: {version}")
    
    # Ensure version has 'v' prefix
    if not version.startswith('v'):
        version = f'v{version}'
    
    # Get commits
    if not from_tag:
        from_tag = get_latest_tag()
    
    if from_tag:
        print(f"📊 Analyzing commits since: {from_tag}")
    else:
        print("📊 Analyzing all commits (no previous tags found)")
    
    commits = get_commits_since_tag(from_tag)
    
    if not commits:
        print("\n✓ No new commits to add to changelog")
        sys.exit(0)
    
    print(f"📋 Found {len(commits)} commit(s)")
    
    # Categorize commits
    categories = categorize_commits(commits)
    
    # Count commits by category
    print("\n📊 Commit Summary:")
    category_names = {
        'breaking': '⚠️  Breaking Changes',
        'feat': '✨ Features',
        'fix': '🐛 Bug Fixes',
        'perf': '⚡ Performance',
        'refactor': '♻️  Refactoring',
        'docs': '📚 Documentation',
        'test': '🧪 Tests',
        'build': '🔧 Build',
        'ci': '🔧 CI',
        'chore': '🔨 Maintenance',
        'style': '💄 Styling',
        'revert': '⏪ Reverts',
        'other': '📝 Other'
    }
    
    for key, name in category_names.items():
        count = len(categories.get(key, []))
        if count > 0:
            print(f"  {name}: {count}")
    
    # Generate changelog content
    changelog_content = generate_changelog_section(version, categories)
    
    # Update file
    print(f"\n📄 Updating CHANGELOG.md for version {version}...")
    if update_changelog_file(changelog_content, version):
        print("✅ CHANGELOG.md updated successfully!")
        
        print("\n📋 Next Steps:")
        print("1. Review and edit CHANGELOG.md for clarity")
        print("2. Commit the changes:")
        print(f'   git add CHANGELOG.md')
        print(f'   git commit -m "docs(changelog): update changelog for {version}"')
        print("3. Continue with release process")
    else:
        print("⚠️  Changelog update cancelled")

if __name__ == "__main__":
    main()
