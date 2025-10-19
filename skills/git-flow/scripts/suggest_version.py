#!/usr/bin/env python3
"""
Analyze commits since last tag and suggest next version based on conventional commits.

Usage:
    python suggest_version.py [--from-tag <tag>]

Example:
    python suggest_version.py
    python suggest_version.py --from-tag v1.2.0
"""

import subprocess
import sys
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
    return output if output and "fatal" not in output else "v0.0.0"

def get_commits_since_tag(tag=None):
    """Get commits since the specified tag."""
    if not tag:
        tag = get_latest_tag()
    
    if tag == "v0.0.0":
        # No tags yet, get all commits
        cmd = "git log --oneline"
    else:
        cmd = f"git log {tag}..HEAD --oneline"
    
    output, _ = run_command(cmd, check=False)
    if output:
        return output.split('\n')
    return []

def analyze_commits(commits):
    """Analyze commits for version bump indicators."""
    has_breaking = False
    has_feature = False
    has_fix = False
    
    breaking_commits = []
    feature_commits = []
    fix_commits = []
    other_commits = []
    
    for commit in commits:
        # Skip merge commits
        if 'Merge' in commit:
            continue
        
        # Check for breaking changes
        if 'BREAKING CHANGE' in commit.upper() or 'BREAKING:' in commit.upper():
            has_breaking = True
            breaking_commits.append(commit)
        
        # Check commit type
        if commit.lower().startswith('feat:') or 'feat(' in commit.lower():
            has_feature = True
            feature_commits.append(commit)
        elif commit.lower().startswith('fix:') or 'fix(' in commit.lower():
            has_fix = True
            fix_commits.append(commit)
        else:
            # Check for other conventional commit types
            conventional_types = ['docs', 'style', 'refactor', 'perf', 'test', 'chore', 'ci', 'build']
            is_conventional = False
            for ctype in conventional_types:
                if commit.lower().startswith(f"{ctype}:") or f"{ctype}(" in commit.lower():
                    is_conventional = True
                    other_commits.append(commit)
                    break
            
            if not is_conventional and commit.strip():
                other_commits.append(commit)
    
    return {
        'has_breaking': has_breaking,
        'has_feature': has_feature,
        'has_fix': has_fix,
        'breaking_commits': breaking_commits,
        'feature_commits': feature_commits,
        'fix_commits': fix_commits,
        'other_commits': other_commits
    }

def parse_version(version_string):
    """Parse semantic version string."""
    version = version_string.lstrip('v')
    try:
        parts = version.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2].split('-')[0]) if len(parts) > 2 else 0
        
        # Check for prerelease
        prerelease = None
        if '-' in version:
            prerelease = version.split('-', 1)[1]
        
        return major, minor, patch, prerelease
    except:
        return 0, 0, 0, None

def calculate_next_version(current_version, bump_type):
    """Calculate next version based on bump type."""
    major, minor, patch, _ = parse_version(current_version)
    
    if bump_type == 'major':
        return f"v{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"v{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"v{major}.{minor}.{patch + 1}"
    else:
        return current_version

def main():
    # Parse arguments
    from_tag = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--from-tag' and len(sys.argv) > 2:
            from_tag = sys.argv[2]
        elif sys.argv[1] in ['-h', '--help']:
            print(__doc__)
            sys.exit(0)
    
    print("🔍 Analyzing Commits for Version Suggestion")
    print("=" * 60)
    
    # Get current version
    current_tag = from_tag or get_latest_tag()
    print(f"📌 Current version: {current_tag}")
    
    # Get commits since tag
    commits = get_commits_since_tag(current_tag)
    
    if not commits:
        print("\n✓ No new commits since last version")
        print(f"Current version {current_tag} is up to date")
        sys.exit(0)
    
    print(f"📊 Found {len(commits)} commit(s) since {current_tag}")
    print()
    
    # Analyze commits
    analysis = analyze_commits(commits)
    
    # Determine version bump
    if analysis['has_breaking']:
        bump_type = 'major'
        bump_reason = "Breaking changes detected"
    elif analysis['has_feature']:
        bump_type = 'minor'
        bump_reason = "New features added"
    elif analysis['has_fix']:
        bump_type = 'patch'
        bump_reason = "Bug fixes only"
    else:
        bump_type = None
        bump_reason = "No version bump needed (only maintenance changes)"
    
    # Display analysis
    print("📝 Commit Analysis:")
    print("-" * 40)
    
    if analysis['breaking_commits']:
        print(f"\n⚠️  Breaking Changes ({len(analysis['breaking_commits'])}):")
        for commit in analysis['breaking_commits'][:5]:
            print(f"  • {commit}")
        if len(analysis['breaking_commits']) > 5:
            print(f"  ... and {len(analysis['breaking_commits']) - 5} more")
    
    if analysis['feature_commits']:
        print(f"\n✨ Features ({len(analysis['feature_commits'])}):")
        for commit in analysis['feature_commits'][:5]:
            print(f"  • {commit}")
        if len(analysis['feature_commits']) > 5:
            print(f"  ... and {len(analysis['feature_commits']) - 5} more")
    
    if analysis['fix_commits']:
        print(f"\n🐛 Bug Fixes ({len(analysis['fix_commits'])}):")
        for commit in analysis['fix_commits'][:5]:
            print(f"  • {commit}")
        if len(analysis['fix_commits']) > 5:
            print(f"  ... and {len(analysis['fix_commits']) - 5} more")
    
    if analysis['other_commits']:
        print(f"\n📋 Other Changes ({len(analysis['other_commits'])}):")
        for commit in analysis['other_commits'][:5]:
            print(f"  • {commit}")
        if len(analysis['other_commits']) > 5:
            print(f"  ... and {len(analysis['other_commits']) - 5} more")
    
    # Calculate and display next version
    print("\n" + "=" * 60)
    
    if bump_type:
        next_version = calculate_next_version(current_tag, bump_type)
        print(f"🎯 Suggested Version: {next_version}")
        print(f"📈 Bump Type: {bump_type.upper()}")
        print(f"💡 Reason: {bump_reason}")
        
        print("\n📋 Version Bump Summary:")
        print(f"  Current: {current_tag}")
        print(f"  Suggested: {next_version}")
        print(f"  Type: {bump_type}")
        
        # Provide command to create release
        print("\n🚀 To create a release with this version:")
        print(f"  python scripts/create_release.py {next_version}")
    else:
        print(f"ℹ️  {bump_reason}")
        print(f"Current version {current_tag} is sufficient")
    
    # Additional recommendations
    if analysis['has_breaking']:
        print("\n⚠️  IMPORTANT: Breaking Changes Detected!")
        print("Please ensure:")
        print("  1. Migration guide is documented")
        print("  2. Major version bump is intentional")
        print("  3. Users are notified before release")
        print("  4. Deprecation warnings were added in previous version")

if __name__ == "__main__":
    main()
