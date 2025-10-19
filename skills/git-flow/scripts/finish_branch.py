#!/usr/bin/env python3
"""
Complete and merge a Git Flow branch (feature/release/hotfix) with proper cleanup.

Usage:
    python finish_branch.py [--no-delete] [--no-tag]

Options:
    --no-delete    Keep the branch after merging
    --no-tag       Skip tag creation (for releases/hotfixes)

Example:
    python finish_branch.py
    python finish_branch.py --no-delete
"""

import subprocess
import sys
import re
import json
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

def get_current_branch():
    """Get the current Git branch."""
    output, _ = run_command("git branch --show-current")
    return output or ""

def get_branch_type(branch_name):
    """Determine the type of Git Flow branch."""
    if branch_name.startswith("feature/"):
        return "feature"
    elif branch_name.startswith("release/"):
        return "release"
    elif branch_name.startswith("hotfix/"):
        return "hotfix"
    return None

def check_uncommitted_changes():
    """Check for uncommitted changes."""
    output, _ = run_command("git status --porcelain")
    if output:
        files = output.split('\n')
        return True, files
    return False, []

def check_unpushed_commits():
    """Check for unpushed commits."""
    output, _ = run_command("git log @{u}.. --oneline", check=False)
    if output:
        commits = output.split('\n')
        return len(commits), commits
    return 0, []

def get_latest_tag():
    """Get the latest tag from main branch."""
    output, _ = run_command("git describe --tags --abbrev=0 origin/main", check=False)
    return output if output else "v0.0.0"

def increment_version(version, bump_type="patch"):
    """Increment semantic version."""
    # Remove 'v' prefix if present
    version = version.lstrip('v')
    
    try:
        major, minor, patch = map(int, version.split('.'))
    except:
        return "v1.0.0"
    
    if bump_type == "major":
        return f"v{major + 1}.0.0"
    elif bump_type == "minor":
        return f"v{major}.{minor + 1}.0"
    else:  # patch
        return f"v{major}.{minor}.{patch + 1}"

def run_tests():
    """Run tests if available."""
    # Try npm test first
    output, error = run_command("npm test", check=False)
    if not error or "no test specified" not in error:
        return output, error
    
    # Try pytest
    output, error = run_command("pytest", check=False)
    if not error:
        return output, error
    
    # Try go test
    output, error = run_command("go test ./...", check=False)
    if not error:
        return output, error
    
    return "No tests found", None

def merge_branch(source, target, message=None):
    """Merge source branch into target."""
    print(f"\n📥 Merging {source} into {target}...")
    
    # Checkout target
    output, error = run_command(f"git checkout {target}")
    if error:
        return False, f"Failed to checkout {target}: {error}"
    
    # Pull latest
    output, error = run_command(f"git pull origin {target}", check=False)
    
    # Merge with no-ff
    if message:
        cmd = f'git merge --no-ff {source} -m "{message}"'
    else:
        cmd = f"git merge --no-ff {source}"
    
    output, error = run_command(cmd)
    if error:
        return False, f"Merge failed: {error}"
    
    # Push
    output, error = run_command(f"git push origin {target}")
    if error and "Could not resolve host" not in error:
        return False, f"Push failed: {error}"
    
    return True, "Successfully merged"

def main():
    no_delete = "--no-delete" in sys.argv
    no_tag = "--no-tag" in sys.argv
    
    current_branch = get_current_branch()
    branch_type = get_branch_type(current_branch)
    
    print(f"🏁 Finishing Git Flow Branch: {current_branch}")
    print("=" * 60)
    
    # Validate branch type
    if not branch_type:
        print(f"❌ Not on a Git Flow branch: {current_branch}")
        print("\nThis command only works on:")
        print("  - feature/* branches")
        print("  - release/* branches")
        print("  - hotfix/* branches")
        sys.exit(1)
    
    print(f"📋 Branch Type: {branch_type.capitalize()}")
    
    # Pre-merge validation
    print("\n🔍 Pre-Merge Validation")
    print("-" * 30)
    
    # Check uncommitted changes
    has_changes, changed_files = check_uncommitted_changes()
    if has_changes:
        print("❌ Uncommitted changes detected:")
        for f in changed_files[:5]:
            print(f"  {f}")
        if len(changed_files) > 5:
            print(f"  ... and {len(changed_files) - 5} more")
        print("\n💡 Please commit or stash your changes first:")
        print("   git add . && git commit -m 'your message'")
        print("   OR")
        print("   git stash")
        sys.exit(1)
    print("✓ Working directory clean")
    
    # Check unpushed commits
    unpushed_count, unpushed_commits = check_unpushed_commits()
    if unpushed_count > 0:
        print(f"⚠️  {unpushed_count} unpushed commit(s) detected:")
        for commit in unpushed_commits[:3]:
            print(f"  {commit}")
        print("\nPushing commits...")
        output, error = run_command("git push")
        if error and "Could not resolve host" not in error:
            print(f"❌ Push failed: {error}")
            sys.exit(1)
        print("✓ All commits pushed")
    else:
        print("✓ All commits pushed to remote")
    
    # Run tests
    print("\n🧪 Running tests...")
    test_output, test_error = run_tests()
    if test_error and "command not found" not in test_error and "no test specified" not in test_error:
        print(f"❌ Tests failed: {test_error}")
        response = input("\n⚠️  Continue anyway? (NOT RECOMMENDED) [y/N]: ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(1)
    elif "No tests found" in test_output:
        print("⚠️  No tests found")
    else:
        print("✓ Tests passed")
    
    # Determine merge strategy based on branch type
    print(f"\n🎯 Merge Strategy for {branch_type}")
    print("-" * 30)
    
    if branch_type == "feature":
        merge_targets = ["develop"]
        create_tag = False
        tag_name = None
        print("→ Will merge to: develop")
        
    elif branch_type == "release":
        merge_targets = ["main", "develop"]
        create_tag = not no_tag
        # Extract version from branch name
        tag_name = current_branch.replace("release/", "")
        if not tag_name.startswith("v"):
            tag_name = f"v{tag_name}"
        print(f"→ Will merge to: main, develop")
        if create_tag:
            print(f"→ Will create tag: {tag_name}")
            
    else:  # hotfix
        merge_targets = ["main", "develop"]
        create_tag = not no_tag
        # Calculate new patch version
        latest_tag = get_latest_tag()
        tag_name = increment_version(latest_tag, "patch")
        print(f"→ Will merge to: main, develop")
        if create_tag:
            print(f"→ Will create tag: {tag_name} (patch bump from {latest_tag})")
    
    # Confirmation
    print("\n📊 Summary")
    print("-" * 30)
    print(f"Branch: {current_branch}")
    print(f"Type: {branch_type.capitalize()}")
    print(f"Merge to: {', '.join(merge_targets)}")
    if create_tag:
        print(f"Tag: {tag_name}")
    if not no_delete:
        print("Delete branch: Yes (local and remote)")
    else:
        print("Delete branch: No (keeping branch)")
    
    response = input("\n🚀 Proceed with finish? [Y/n]: ").strip().lower()
    if response == 'n':
        print("Aborted.")
        sys.exit(1)
    
    # Perform merges
    print("\n🔀 Performing Merges")
    print("=" * 60)
    
    for target in merge_targets:
        # Create merge message
        if branch_type == "feature":
            merge_msg = f"Merge {current_branch} into {target}"
        elif branch_type == "release":
            merge_msg = f"Merge {current_branch} into {target} - Release {tag_name}"
        else:  # hotfix
            merge_msg = f"Merge {current_branch} into {target} - Hotfix {tag_name}"
        
        success, message = merge_branch(current_branch, target, merge_msg)
        if not success:
            print(f"❌ {message}")
            print("\n💡 You may need to:")
            print("1. Resolve merge conflicts")
            print("2. Complete the merge manually")
            print("3. Run this command again")
            sys.exit(1)
        print(f"✓ Merged to {target}")
        
        # Create tag on main if applicable
        if target == "main" and create_tag and tag_name:
            print(f"\n🏷️  Creating tag: {tag_name}")
            tag_msg = f"Release {tag_name}" if branch_type == "release" else f"Hotfix {tag_name}"
            
            output, error = run_command(f'git tag -a {tag_name} -m "{tag_msg}"')
            if error:
                print(f"⚠️  Failed to create tag: {error}")
            else:
                print(f"✓ Tag created: {tag_name}")
                
                # Push tag
                output, error = run_command(f"git push origin {tag_name}")
                if error and "Could not resolve host" not in error:
                    print(f"⚠️  Failed to push tag: {error}")
                else:
                    print(f"✓ Tag pushed to remote")
    
    # Clean up branches
    if not no_delete:
        print(f"\n🧹 Cleaning up branches")
        print("-" * 30)
        
        # Return to develop (safe branch)
        run_command("git checkout develop", check=False)
        
        # Delete local branch
        output, error = run_command(f"git branch -d {current_branch}")
        if error:
            print(f"⚠️  Failed to delete local branch: {error}")
            # Try force delete
            output, error = run_command(f"git branch -D {current_branch}")
            if not error:
                print(f"✓ Force deleted local branch: {current_branch}")
        else:
            print(f"✓ Deleted local branch: {current_branch}")
        
        # Delete remote branch
        output, error = run_command(f"git push origin --delete {current_branch}")
        if error and "Could not resolve host" not in error:
            print(f"⚠️  Failed to delete remote branch: {error}")
        else:
            print(f"✓ Deleted remote branch: origin/{current_branch}")
    
    # Success summary
    print("\n" + "=" * 60)
    print(f"✅ {branch_type.capitalize()} Branch Finished Successfully!")
    
    # Type-specific summary and next steps
    if branch_type == "feature":
        print("\n📊 Feature Summary:")
        print(f"  • Merged to: develop")
        if not no_delete:
            print(f"  • Branches deleted: {current_branch}")
        print("\n🎯 Next Steps:")
        print("  • Feature is now in develop")
        print("  • Will be included in next release")
        print("  • Start a new feature: python scripts/create_feature.py <n>")
        
    elif branch_type == "release":
        print("\n📊 Release Summary:")
        print(f"  • Merged to: main, develop")
        if create_tag:
            print(f"  • Tag created: {tag_name}")
        if not no_delete:
            print(f"  • Branches deleted: {current_branch}")
        print("\n🚀 DEPLOYMENT CHECKLIST:")
        print(f"  [ ] Deploy {tag_name} to production")
        print("  [ ] Verify deployment")
        print("  [ ] Monitor for issues")
        print("  [ ] Announce release to team")
        print("  [ ] Update documentation")
        
    else:  # hotfix
        print("\n📊 Hotfix Summary:")
        print(f"  • Merged to: main, develop")
        if create_tag:
            print(f"  • Tag created: {tag_name}")
        if not no_delete:
            print(f"  • Branches deleted: {current_branch}")
        print("\n🚨 IMMEDIATE ACTIONS REQUIRED:")
        print(f"  [ ] Deploy {tag_name} to production NOW")
        print("  [ ] Monitor production systems")
        print("  [ ] Verify fix is working")
        print("  [ ] Update incident documentation")
        print("  [ ] Notify stakeholders")

if __name__ == "__main__":
    main()
