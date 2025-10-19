#!/usr/bin/env python3
"""
Create a new Git Flow feature branch with validation and setup.

Usage:
    python create_feature.py <feature-name>

Example:
    python create_feature.py user-authentication
    python create_feature.py payment-integration
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Execute a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
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
    """Validate the feature branch name."""
    if not name:
        return False, "Feature name is required"
    
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

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python create_feature.py <feature-name>")
        print("Example: python create_feature.py user-authentication")
        sys.exit(1)
    
    feature_name = sys.argv[1]
    branch_name = f"feature/{feature_name}"
    
    print(f"🌿 Creating Git Flow Feature Branch: {branch_name}")
    print("=" * 50)
    
    # Validate branch name
    valid, error = validate_branch_name(feature_name)
    if not valid:
        print(f"❌ Invalid branch name: {error}")
        print("\n💡 Valid examples:")
        print("  - user-authentication")
        print("  - payment-gateway")
        print("  - api-refactor")
        sys.exit(1)
    
    # Check if branch already exists
    exists, where = branch_exists(branch_name)
    if exists:
        print(f"❌ Branch '{branch_name}' already exists ({where})")
        print("\n💡 Use a different name or delete the existing branch first")
        sys.exit(1)
    
    # Check current branch
    current = get_current_branch()
    if current != "develop":
        print(f"⚠️  Not on develop branch (current: {current})")
        print("Switching to develop...")
        
        # Try to switch to develop
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
        print("Your changes will be carried to the new branch")
        response = input("Continue anyway? [Y/n]: ").strip().lower()
        if response == 'n':
            print("Aborted.")
            sys.exit(1)
    
    # Create the feature branch
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
    print("\n" + "=" * 50)
    print("✅ Feature Branch Created Successfully!")
    print(f"\n📌 Current branch: {branch_name}")
    print(f"📝 Base branch: develop")
    
    # Next steps
    print("\n🎯 Next Steps:")
    print("1. Implement your feature")
    print("2. Commit changes with conventional commits:")
    print('   git commit -m "feat: add user authentication"')
    print("3. Push changes regularly:")
    print("   git push")
    print("4. When ready, finish the feature:")
    print("   python scripts/finish_branch.py")
    print("\n💡 Remember to:")
    print("- Write tests for your feature")
    print("- Update documentation")
    print("- Keep commits focused and descriptive")

if __name__ == "__main__":
    main()
