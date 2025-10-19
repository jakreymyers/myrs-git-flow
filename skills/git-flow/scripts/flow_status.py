#!/usr/bin/env python3
"""
Display comprehensive Git Flow status with branch information and recommendations.

Usage:
    python flow_status.py

Example output shows current branch, sync status, active branches, and next steps.
"""

import subprocess
import sys
from collections import defaultdict

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

def get_branch_type(branch_name):
    """Determine the type of Git Flow branch."""
    if branch_name == "main":
        return "main", "Production branch"
    elif branch_name == "develop":
        return "develop", "Development branch"
    elif branch_name.startswith("feature/"):
        return "feature", "Feature branch"
    elif branch_name.startswith("release/"):
        return "release", "Release branch"
    elif branch_name.startswith("hotfix/"):
        return "hotfix", "Hotfix branch"
    else:
        return "other", "Non-Git Flow branch"

def get_git_status():
    """Get working directory status."""
    output, _ = run_command("git status --porcelain")
    if not output:
        return 0, 0, 0, []  # modified, added, deleted, files
    
    files = output.split('\n')
    modified = sum(1 for f in files if f.startswith(' M') or f.startswith('M '))
    added = sum(1 for f in files if f.startswith('A ') or f.startswith('??'))
    deleted = sum(1 for f in files if f.startswith(' D') or f.startswith('D '))
    
    return modified, added, deleted, files

def get_sync_status():
    """Get sync status with remote."""
    # Get ahead count
    ahead_output, _ = run_command("git rev-list @{u}.. --count", check=False)
    ahead = int(ahead_output) if ahead_output and ahead_output.isdigit() else 0
    
    # Get behind count
    behind_output, _ = run_command("git rev-list ..@{u} --count", check=False)
    behind = int(behind_output) if behind_output and behind_output.isdigit() else 0
    
    return ahead, behind

def get_remote_tracking():
    """Get remote tracking branch."""
    output, _ = run_command("git rev-parse --abbrev-ref --symbolic-full-name @{u}", check=False)
    return output if output and "fatal" not in output else None

def get_all_branches():
    """Get all local branches grouped by type."""
    output, _ = run_command("git branch")
    if not output:
        return {}
    
    branches = defaultdict(list)
    for line in output.split('\n'):
        branch = line.strip().lstrip('* ')
        if not branch:
            continue
        
        if branch == "main":
            branches["protected"].append(branch)
        elif branch == "develop":
            branches["protected"].append(branch)
        elif branch.startswith("feature/"):
            branches["feature"].append(branch)
        elif branch.startswith("release/"):
            branches["release"].append(branch)
        elif branch.startswith("hotfix/"):
            branches["hotfix"].append(branch)
        else:
            branches["other"].append(branch)
    
    return dict(branches)

def get_latest_tag():
    """Get the latest tag."""
    output, _ = run_command("git describe --tags --abbrev=0", check=False)
    return output if output else None

def get_recent_commits(n=5):
    """Get recent commits."""
    output, _ = run_command(f"git log --oneline -n {n}")
    if output:
        return output.split('\n')
    return []

def check_merge_readiness(branch_name, branch_type):
    """Check if branch is ready to merge."""
    issues = []
    
    # Check uncommitted changes
    modified, added, deleted, _ = get_git_status()
    if modified + added + deleted > 0:
        issues.append("Uncommitted changes present")
    
    # Check sync status
    ahead, behind = get_sync_status()
    if ahead > 0:
        issues.append(f"{ahead} unpushed commit(s)")
    if behind > 0:
        issues.append(f"{behind} commit(s) behind remote")
    
    # Check if on correct base branch
    if branch_type == "feature":
        current, _ = run_command("git merge-base HEAD origin/develop", check=False)
        if not current:
            issues.append("Not based on latest develop")
    
    return len(issues) == 0, issues

def format_branch_status(branch_name):
    """Format branch name with indicators."""
    current = get_current_branch()
    if branch_name == current:
        return f"● {branch_name} (current)"
    return f"  {branch_name}"

def main():
    print("🌿 Git Flow Status")
    print("=" * 60)
    
    # Current branch info
    current_branch = get_current_branch()
    branch_type, description = get_branch_type(current_branch)
    
    print(f"📍 Current Branch: {current_branch}")
    print(f"📋 Type: {description}")
    
    # Remote tracking
    remote = get_remote_tracking()
    if remote:
        print(f"🔗 Remote: {remote}")
    else:
        print(f"🔗 Remote: No remote tracking")
    
    # Working directory status
    modified, added, deleted, files = get_git_status()
    total_changes = modified + added + deleted
    
    print(f"\n📂 Working Directory:")
    if total_changes == 0:
        print("  ✓ Clean (no uncommitted changes)")
    else:
        print(f"  ● {modified} modified")
        print(f"  ✚ {added} added")
        print(f"  ✖ {deleted} deleted")
        print(f"  Total: {total_changes} file(s) with changes")
    
    # Sync status
    ahead, behind = get_sync_status()
    print(f"\n🔄 Sync Status:")
    if ahead == 0 and behind == 0:
        print("  ✓ In sync with remote")
    else:
        if ahead > 0:
            print(f"  ↑ {ahead} commit(s) ahead of remote")
        if behind > 0:
            print(f"  ↓ {behind} commit(s) behind remote")
    
    # All branches
    branches = get_all_branches()
    if branches:
        print(f"\n🌳 Active Branches:")
        
        if "protected" in branches:
            print("  Protected:")
            for b in branches["protected"]:
                print(f"    {format_branch_status(b)}")
        
        if "feature" in branches:
            print(f"  Features ({len(branches['feature'])}):")
            for b in branches["feature"][:5]:
                print(f"    {format_branch_status(b)}")
            if len(branches["feature"]) > 5:
                print(f"    ... and {len(branches['feature']) - 5} more")
        
        if "release" in branches:
            print(f"  Releases ({len(branches['release'])}):")
            for b in branches["release"]:
                print(f"    {format_branch_status(b)}")
        
        if "hotfix" in branches:
            print(f"  Hotfixes ({len(branches['hotfix'])}):")
            for b in branches["hotfix"]:
                print(f"    {format_branch_status(b)}")
        
        if "other" in branches:
            print(f"  Other ({len(branches['other'])}):")
            for b in branches["other"][:3]:
                print(f"    {format_branch_status(b)}")
            if len(branches["other"]) > 3:
                print(f"    ... and {len(branches['other']) - 3} more")
    
    # Latest tag
    latest_tag = get_latest_tag()
    if latest_tag:
        print(f"\n🏷️  Latest Tag: {latest_tag}")
    
    # Recent commits
    recent = get_recent_commits(5)
    if recent:
        print(f"\n📝 Recent Commits:")
        for commit in recent:
            print(f"  {commit}")
    
    # Merge readiness (for feature/release/hotfix branches)
    if branch_type in ["feature", "release", "hotfix"]:
        ready, issues = check_merge_readiness(current_branch, branch_type)
        
        print(f"\n🎯 Merge Readiness:")
        if ready:
            print("  ✅ Ready to merge!")
            print(f"  → Run: python scripts/finish_branch.py")
        else:
            print("  ⚠️  Not ready to merge:")
            for issue in issues:
                print(f"    - {issue}")
    
    # Recommendations based on current state
    print(f"\n💡 Recommendations:")
    
    if branch_type == "main":
        print("  • You're on the production branch")
        print("  • Create a hotfix for emergency fixes:")
        print("    python scripts/create_hotfix.py <n>")
        print("  • Or switch to develop for regular work:")
        print("    git checkout develop")
        
    elif branch_type == "develop":
        print("  • You're on the development branch")
        print("  • Start a new feature:")
        print("    python scripts/create_feature.py <n>")
        print("  • Or create a release:")
        print("    python scripts/create_release.py v<version>")
        
    elif branch_type == "feature":
        if total_changes > 0:
            print("  • Commit your changes:")
            print(f'    git add . && git commit -m "feat: your message"')
        elif ahead > 0:
            print("  • Push your commits:")
            print("    git push")
        elif behind > 0:
            print("  • Pull remote changes:")
            print("    git pull")
        else:
            print("  • Continue working on your feature")
            print("  • Or finish if complete:")
            print("    python scripts/finish_branch.py")
            
    elif branch_type == "release":
        if total_changes > 0:
            print("  • Commit your release preparation:")
            print(f'    git add . && git commit -m "chore(release): prepare v<version>"')
        else:
            print("  • Finish the release:")
            print("    python scripts/finish_branch.py")
            print("  • This will merge to main and develop")
            
    elif branch_type == "hotfix":
        if total_changes > 0:
            print("  • Commit your hotfix:")
            print(f'    git add . && git commit -m "fix: your urgent fix"')
        else:
            print("  • Finish the hotfix ASAP:")
            print("    python scripts/finish_branch.py")
            print("  • ⚠️  Remember to deploy immediately after!")
            
    else:
        print("  • ⚠️  You're not on a Git Flow branch")
        print("  • Consider switching to a proper Git Flow branch:")
        print("    git checkout develop")
        print("  • Then create a feature branch:")
        print("    python scripts/create_feature.py <n>")
    
    # Stale branch cleanup suggestion
    if branches and "feature" in branches and len(branches["feature"]) > 5:
        print("\n  🧹 Consider cleaning up old feature branches:")
        print("    git branch -d <branch-name>")

if __name__ == "__main__":
    main()
