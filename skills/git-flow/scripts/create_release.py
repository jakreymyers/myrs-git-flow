#!/usr/bin/env python3
"""
Create a new Git Flow release branch with version management and changelog generation.

Usage:
    python create_release.py <version>

Example:
    python create_release.py v1.2.0
    python create_release.py 1.2.0  # 'v' prefix will be added automatically
"""

import subprocess
import sys
import os
import json
import re
from datetime import datetime

def run_command(cmd, check=True):
    """Execute a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            return None, result.stderr
        return result.stdout.strip(), None
    except Exception as e:
        return None, str(e)

def validate_version(version):
    """Validate semantic version format."""
    # Add 'v' prefix if missing
    if not version.startswith('v'):
        version = f'v{version}'
    
    # Check format
    pattern = r'^v\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'
    if not re.match(pattern, version):
        return None, "Invalid version format"
    
    return version, None

def get_current_branch():
    """Get the current Git branch."""
    output, _ = run_command("git branch --show-current")
    return output or ""

def check_git_status():
    """Check if working directory is clean."""
    output, _ = run_command("git status --porcelain")
    return len(output) == 0 if output is not None else False

def get_latest_tag():
    """Get the latest tag."""
    output, _ = run_command("git describe --tags --abbrev=0", check=False)
    return output if output else None

def update_package_json(version):
    """Update version in package.json if it exists."""
    if not os.path.exists("package.json"):
        return True, "No package.json found"
    
    try:
        with open("package.json", 'r') as f:
            data = json.load(f)
        
        # Remove 'v' prefix for package.json
        clean_version = version.lstrip('v')
        data['version'] = clean_version
        
        with open("package.json", 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        
        return True, f"Updated package.json to version {clean_version}"
    except Exception as e:
        return False, f"Failed to update package.json: {e}"

def get_commits_since_tag(tag=None):
    """Get commits since the last tag."""
    if tag:
        cmd = f"git log {tag}..HEAD --oneline"
    else:
        cmd = "git log --oneline"
    
    output, _ = run_command(cmd, check=False)
    if output:
        return output.split('\n')
    return []

def categorize_commits(commits):
    """Categorize commits by conventional commit type."""
    categories = {
        'feat': [],
        'fix': [],
        'docs': [],
        'style': [],
        'refactor': [],
        'perf': [],
        'test': [],
        'chore': [],
        'ci': [],
        'build': [],
        'other': []
    }
    
    breaking = []
    
    for commit in commits:
        # Skip merge commits
        if 'Merge' in commit:
            continue
        
        # Check for breaking changes
        if 'BREAKING CHANGE' in commit or 'BREAKING:' in commit:
            breaking.append(commit)
        
        # Categorize by type
        found = False
        for type_key in categories.keys():
            if type_key != 'other' and commit.lower().startswith(f"{type_key}:") or f"{type_key}(" in commit.lower():
                categories[type_key].append(commit)
                found = True
                break
        
        if not found and 'Merge' not in commit:
            categories['other'].append(commit)
    
    return categories, breaking

def generate_changelog_content(version, categories, breaking):
    """Generate changelog content for the release."""
    content = []
    date = datetime.now().strftime("%Y-%m-%d")
    
    content.append(f"## [{version}] - {date}\n")
    
    if breaking:
        content.append("### ⚠️ BREAKING CHANGES\n")
        for commit in breaking:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['feat']:
        content.append("### ✨ Features\n")
        for commit in categories['feat']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['fix']:
        content.append("### 🐛 Bug Fixes\n")
        for commit in categories['fix']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['perf']:
        content.append("### ⚡ Performance Improvements\n")
        for commit in categories['perf']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['refactor']:
        content.append("### ♻️ Code Refactoring\n")
        for commit in categories['refactor']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['docs']:
        content.append("### 📚 Documentation\n")
        for commit in categories['docs']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['test']:
        content.append("### 🧪 Tests\n")
        for commit in categories['test']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['build'] or categories['ci']:
        content.append("### 🔧 Build & CI\n")
        for commit in categories['build'] + categories['ci']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['chore']:
        content.append("### 🔨 Maintenance\n")
        for commit in categories['chore']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    if categories['other']:
        content.append("### 📝 Other Changes\n")
        for commit in categories['other']:
            content.append(f"- {commit}\n")
        content.append("\n")
    
    return ''.join(content)

def update_changelog(version, content):
    """Update or create CHANGELOG.md."""
    changelog_path = "CHANGELOG.md"
    
    if os.path.exists(changelog_path):
        # Read existing changelog
        with open(changelog_path, 'r') as f:
            existing = f.read()
        
        # Insert new content after the title
        if "# Changelog" in existing:
            parts = existing.split("# Changelog\n", 1)
            if len(parts) == 2:
                new_content = f"# Changelog\n\n{content}\n{parts[1]}"
            else:
                new_content = f"# Changelog\n\n{content}\n{existing}"
        else:
            new_content = f"# Changelog\n\n{content}\n{existing}"
    else:
        # Create new changelog
        new_content = f"# Changelog\n\n{content}"
    
    # Write updated changelog
    with open(changelog_path, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python create_release.py <version>")
        print("Example: python create_release.py v1.2.0")
        print("         python create_release.py 1.2.0")
        sys.exit(1)
    
    # Validate version
    version, error = validate_version(sys.argv[1])
    if not version:
        print(f"❌ {error}")
        print("\n💡 Valid version formats:")
        print("  - v1.0.0")
        print("  - v2.1.3")
        print("  - v1.0.0-beta.1")
        print("  - 1.2.0 (v will be added)")
        sys.exit(1)
    
    branch_name = f"release/{version}"
    
    print(f"🚀 Creating Git Flow Release Branch: {branch_name}")
    print("=" * 60)
    
    # Check current branch
    current = get_current_branch()
    if current != "develop":
        print(f"⚠️  Not on develop branch (current: {current})")
        print("Switching to develop...")
        
        output, error = run_command("git checkout develop")
        if error:
            print(f"❌ Failed to switch to develop: {error}")
            sys.exit(1)
        print("✓ Switched to develop")
    
    # Pull latest develop
    print("\n📥 Pulling latest develop...")
    output, error = run_command("git pull origin develop")
    if error and "Could not resolve host" not in error:
        print(f"⚠️  Pull warning: {error}")
    else:
        print("✓ Develop is up to date")
    
    # Check for uncommitted changes
    if not check_git_status():
        print("\n⚠️  Warning: Uncommitted changes detected")
        print("Your changes will be carried to the release branch")
        response = input("Continue anyway? [Y/n]: ").strip().lower()
        if response == 'n':
            print("Aborted.")
            sys.exit(1)
    
    # Get latest tag for changelog generation
    latest_tag = get_latest_tag()
    if latest_tag:
        print(f"\n📊 Previous version: {latest_tag}")
    
    # Create the release branch
    print(f"\n🔨 Creating branch: {branch_name}")
    output, error = run_command(f"git checkout -b {branch_name}")
    if error:
        print(f"❌ Failed to create branch: {error}")
        sys.exit(1)
    
    print(f"✓ Created and switched to {branch_name}")
    
    # Update package.json if exists
    print("\n📦 Updating version files...")
    success, message = update_package_json(version)
    if success:
        if "No package.json" not in message:
            print(f"✓ {message}")
            # Commit the change
            run_command("git add package.json")
            run_command(f'git commit -m "chore(release): bump version to {version}"')
    else:
        print(f"⚠️  {message}")
    
    # Generate changelog
    print("\n📝 Generating changelog...")
    commits = get_commits_since_tag(latest_tag)
    if commits:
        print(f"Found {len(commits)} commits since {latest_tag if latest_tag else 'beginning'}")
        
        categories, breaking = categorize_commits(commits)
        changelog_content = generate_changelog_content(version, categories, breaking)
        
        if update_changelog(version, changelog_content):
            print("✓ Updated CHANGELOG.md")
            
            # Commit changelog
            run_command("git add CHANGELOG.md")
            run_command(f'git commit -m "docs(release): update changelog for {version}"')
        else:
            print("⚠️  Failed to update changelog")
    else:
        print("No commits found for changelog")
    
    # Push to remote
    print(f"\n📤 Setting up remote tracking...")
    output, error = run_command(f"git push -u origin {branch_name}")
    if error and "Could not resolve host" not in error and "Everything up-to-date" not in error:
        print(f"⚠️  Remote push skipped: Working offline or no remote configured")
    else:
        print(f"✓ Remote tracking set up: origin/{branch_name}")
    
    # Version bump suggestions
    if latest_tag:
        feat_count = len(categories.get('feat', []))
        fix_count = len(categories.get('fix', []))
        breaking_count = len(breaking)
        
        print(f"\n📊 Release Statistics:")
        print(f"  • Features: {feat_count}")
        print(f"  • Bug Fixes: {fix_count}")
        print(f"  • Breaking Changes: {breaking_count}")
        print(f"  • Total Commits: {len(commits)}")
    
    # Success summary
    print("\n" + "=" * 60)
    print("✅ Release Branch Created Successfully!")
    print(f"\n📌 Current branch: {branch_name}")
    print(f"📝 Version: {version}")
    print(f"📋 Base: develop")
    
    # Next steps
    print("\n🎯 Next Steps:")
    print("1. Review and update CHANGELOG.md if needed")
    print("2. Run final tests:")
    print("   npm test  # or your test command")
    print("3. Update documentation if needed")
    print("4. Create pull request for review:")
    print("   gh pr create --base main")
    print("5. After approval, finish the release:")
    print("   python scripts/finish_branch.py")
    print(f"\n⚠️  Important: This will create tag {version} and merge to both main and develop")
    
    print("\n💡 Release Checklist:")
    print("  [ ] Version numbers updated")
    print("  [ ] CHANGELOG.md reviewed")
    print("  [ ] All tests passing")
    print("  [ ] Documentation updated")
    print("  [ ] Team notified")

if __name__ == "__main__":
    main()
