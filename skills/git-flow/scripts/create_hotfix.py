#!/usr/bin/env python3
"""
Create a new Git Flow hotfix branch for emergency production fixes.

Usage:
    python create_hotfix.py <hotfix-name>

Example:
    python create_hotfix.py security-patch
    python create_hotfix.py critical-bug-fix
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """Execute a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            return None, result.stderr
        return result.stdout.strip(), None
    except Exception as e:
        return None, str(e)

def get_current_branch():
    """Get the current Git branch."""
    output, _ = run_command("git branch --show-current")
    return output or ""

def check_git_status():
    """Check if working directory is clean."""
    output, _ = run_command("git status --porcelain")
    return len(output) == 0 if output is not None else False

def validate_branch_name(name):
    """Validate the hotfix branch name."""
    if not name:
        return False, "Hotfix name is required"
    
    # Check for invalid characters
    invalid_chars = [' ', '..', '~', '^', ':', '?', '*', '[', '@{', '\\']
    for char in invalid_chars:
        if char in name:
            return False, f"Invalid character '{char}' in branch name"
    
    # Check name length
    if len(name) > 100:
        return False, "Branch name too long (max 100 characters)"
    
    return True, None

def branch_exists(branch_name):
    """Check if branch already exists locally or remotely."""
    # Check local branches
    local, _ = run_command(f"git branch -l {branch_name}")
    if local:
        return True, "local"
    
    # Check remote branches
    remote, _ = run_command(f"git ls-remote --heads origin {branch_name}")
    if remote:
        return True, "remote"
    
    return False, None

def get_latest_tag():
    """Get the latest tag from main branch."""
    output, _ = run_command("git describe --tags --abbrev=0 origin/main", check=False)
    return output if output else "v0.0.0"

def get_production_status():
    """Get information about production (main) branch."""
    # Get latest tag
    latest_tag = get_latest_tag()
    
    # Get commits since last tag
    commits_cmd = f"git log {latest_tag}..origin/main --oneline"
    commits_output, _ = run_command(commits_cmd, check=False)
    
    if commits_output:
        commits = commits_output.split('\n')
        commit_count = len(commits)
    else:
        commits = []
        commit_count = 0
    
    return latest_tag, commit_count, commits

def calculate_next_version(current_version):
    """Calculate the next patch version."""
    # Remove 'v' prefix if present
    version = current_version.lstrip('v')
    
    try:
        major, minor, patch = map(int, version.split('.'))
        return f"v{major}.{minor}.{patch + 1}"
    except:
        return "v0.0.1"

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python create_hotfix.py <hotfix-name>")
        print("Example: python create_hotfix.py security-patch")
        print("         python create_hotfix.py critical-bug-fix")
        sys.exit(1)
    
    hotfix_name = sys.argv[1]
    branch_name = f"hotfix/{hotfix_name}"
    
    print(f"🔥 Creating Git Flow Hotfix Branch: {branch_name}")
    print("=" * 60)
    print("⚠️  HOTFIX: Emergency production fix")
    print("=" * 60)
    
    # Validate branch name
    valid, error = validate_branch_name(hotfix_name)
    if not valid:
        print(f"❌ Invalid branch name: {error}")
        print("\n💡 Valid examples:")
        print("  - security-patch")
        print("  - memory-leak-fix")
        print("  - critical-api-error")
        sys.exit(1)
    
    # Check if branch already exists
    exists, where = branch_exists(branch_name)
    if exists:
        print(f"❌ Branch '{branch_name}' already exists ({where})")
        print("\n💡 Use a different name or delete the existing branch first")
        sys.exit(1)
    
    # Get production status
    print("\n📊 Production Status:")
    latest_tag, commits_since_tag, recent_commits = get_production_status()
    next_version = calculate_next_version(latest_tag)
    
    print(f"  • Current version: {latest_tag}")
    print(f"  • Next version will be: {next_version}")
    if commits_since_tag > 0:
        print(f"  • {commits_since_tag} unreleased commit(s) on main")
        print("  • Recent commits:")
        for commit in recent_commits[:3]:
            print(f"    - {commit}")
    
    # Check current branch
    current = get_current_branch()
    if current != "main":
        print(f"\n⚠️  Not on main branch (current: {current})")
        print("Switching to main...")
        
        # Try to switch to main
        output, error = run_command("git checkout main")
        if error:
            print(f"❌ Failed to switch to main: {error}")
            sys.exit(1)
        print("✓ Switched to main")
    
    # Pull latest main
    print("\n📥 Pulling latest main (production)...")
    output, error = run_command("git pull origin main")
    if error and "Could not resolve host" not in error:
        print(f"⚠️  Pull warning: {error}")
    else:
        print("✓ Main is up to date")
    
    # Check for uncommitted changes
    if not check_git_status():
        print("\n⚠️  Warning: Uncommitted changes detected")
        print("⚠️  CRITICAL: Hotfixes should start from a clean production state!")
        response = input("Continue anyway? [y/N]: ").strip().lower()
        if response != 'y':
            print("Aborted. Please commit or stash your changes first.")
            sys.exit(1)
    
    # Create the hotfix branch
    print(f"\n🔨 Creating branch: {branch_name}")
    output, error = run_command(f"git checkout -b {branch_name}")
    if error:
        print(f"❌ Failed to create branch: {error}")
        sys.exit(1)
    
    print(f"✓ Created and switched to {branch_name}")
    
    # Push to remote and set upstream
    print(f"\n📤 Setting up remote tracking...")
    output, error = run_command(f"git push -u origin {branch_name}")
    if error and "Could not resolve host" not in error and "Everything up-to-date" not in error:
        print(f"⚠️  Remote push skipped: Working offline or no remote configured")
    else:
        print(f"✓ Remote tracking set up: origin/{branch_name}")
    
    # Success summary
    print("\n" + "=" * 60)
    print("✅ Hotfix Branch Created Successfully!")
    print(f"\n📌 Current branch: {branch_name}")
    print(f"📝 Base: main (production)")
    print(f"🏷️  Will create version: {next_version} when finished")
    
    # Critical reminders
    print("\n🚨 CRITICAL REMINDERS:")
    print("• This is an EMERGENCY fix for production")
    print("• Keep changes minimal and focused")
    print("• Test thoroughly before finishing")
    print("• Deploy immediately after merging")
    
    # Next steps
    print("\n🎯 Next Steps:")
    print("1. Implement the critical fix")
    print("2. Test the fix thoroughly:")
    print("   - Run unit tests")
    print("   - Test in staging if possible")
    print("   - Verify fix resolves the issue")
    print("3. Commit with descriptive message:")
    print(f'   git commit -m "fix: {hotfix_name}"')
    print("4. Push changes:")
    print("   git push")
    print("5. Finish the hotfix:")
    print("   python scripts/finish_branch.py")
    print(f"6. Deploy {next_version} to production IMMEDIATELY")
    
    print("\n⚠️  Time-Critical Actions:")
    print("  [ ] Fix implemented")
    print("  [ ] Tests passing")
    print("  [ ] Fix verified")
    print("  [ ] Ready for immediate deployment")
    
    print("\n💡 Best Practices for Hotfixes:")
    print("  • Keep scope minimal - only fix the critical issue")
    print("  • Don't include unrelated changes")
    print("  • Document the issue and fix")
    print("  • Notify team immediately")
    print("  • Monitor after deployment")

if __name__ == "__main__":
    main()
