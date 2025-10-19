# Git Flow Troubleshooting Guide

Solutions for common Git Flow issues and problems.

## Table of Contents

- [Branch Issues](#branch-issues)
- [Merge Conflicts](#merge-conflicts)
- [Remote Repository Issues](#remote-repository-issues)
- [Commit Problems](#commit-problems)
- [Release Issues](#release-issues)
- [Hotfix Problems](#hotfix-problems)
- [Recovery Procedures](#recovery-procedures)
- [Common Error Messages](#common-error-messages)

## Branch Issues

### Cannot create branch - already exists

**Problem:**
```
❌ Branch 'feature/user-auth' already exists
```

**Solutions:**
```bash
# Option 1: Delete the old branch if no longer needed
git branch -D feature/user-auth
git push origin --delete feature/user-auth

# Option 2: Use a different name
git checkout -b feature/user-auth-v2

# Option 3: Resume work on existing branch
git checkout feature/user-auth
git pull origin feature/user-auth
```

### Wrong base branch

**Problem:** Created feature from main instead of develop

**Solution:**
```bash
# Save your work
git stash

# Delete wrong branch
git checkout main
git branch -D feature/wrong-base

# Create from correct base
git checkout develop
git checkout -b feature/correct-base

# Restore work
git stash pop
```

### Branch diverged from remote

**Problem:**
```
Your branch and 'origin/feature/x' have diverged
```

**Solutions:**
```bash
# Option 1: Rebase (preferred for feature branches)
git pull --rebase origin feature/x

# Option 2: Merge
git pull origin feature/x

# Option 3: Force push (only if you're sure)
git push --force-with-lease origin feature/x
```

## Merge Conflicts

### Conflict during feature finish

**Problem:** Conflicts when merging to develop

**Solution:**
```bash
# Abort the finish operation
git merge --abort

# Manually resolve
git checkout develop
git pull origin develop
git checkout feature/my-feature
git merge develop

# Resolve conflicts in editor
vim conflicted-file.js

# Complete merge
git add .
git commit
git push

# Retry finish
python scripts/finish_branch.py
```

### Multiple conflicts in release merge

**Problem:** Many conflicts when merging release to main

**Solution:**
```bash
# Create a test merge first
git checkout -b test-merge main
git merge --no-ff release/v1.2.0

# Resolve all conflicts carefully
# Test thoroughly
npm test

# If successful, apply to main
git checkout main
git merge --no-ff release/v1.2.0
```

### Binary file conflicts

**Problem:** Conflicts in images, PDFs, or other binary files

**Solution:**
```bash
# Choose one version
git checkout --ours path/to/file.pdf  # Keep current branch version
# or
git checkout --theirs path/to/file.pdf  # Keep incoming version

# Add and continue
git add path/to/file.pdf
git commit
```

## Remote Repository Issues

### Cannot push - rejected

**Problem:**
```
! [rejected] feature/x -> feature/x (fetch first)
```

**Solution:**
```bash
# Pull and merge/rebase
git pull origin feature/x
# or
git pull --rebase origin feature/x

# Then push
git push origin feature/x
```

### No remote tracking

**Problem:** No upstream branch set

**Solution:**
```bash
# Set upstream while pushing
git push -u origin feature/my-feature

# Or set upstream separately
git branch --set-upstream-to=origin/feature/my-feature
```

### Remote branch deleted

**Problem:** Remote branch was deleted by someone else

**Solution:**
```bash
# Clean up local reference
git fetch --prune

# If you need to restore it
git push origin feature/my-feature

# Or switch to a new branch
git checkout -b feature/my-feature-restored
git push -u origin feature/my-feature-restored
```

## Commit Problems

### Wrong commit message

**Problem:** Committed with wrong conventional commit format

**Solution:**
```bash
# For last commit only
git commit --amend -m "fix: correct commit message"

# For older commits
git rebase -i HEAD~3
# Change 'pick' to 'reword' for commits to fix
```

### Committed to wrong branch

**Problem:** Committed to develop instead of feature branch

**Solution:**
```bash
# Note the commit hash
git log -1 --format="%H"

# Reset develop (if not pushed)
git reset --hard HEAD~1

# Switch to correct branch
git checkout feature/my-feature

# Cherry-pick the commit
git cherry-pick <commit-hash>
```

### Need to undo commits

**Solution depends on situation:**
```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Undo last commit, discard changes
git reset --hard HEAD~1

# Revert a pushed commit (creates new commit)
git revert <commit-hash>
```

## Release Issues

### Wrong version number

**Problem:** Created release with wrong version

**Solution:**
```bash
# Delete the wrong branch
git checkout develop
git branch -D release/v1.0.0
git push origin --delete release/v1.0.0

# Create with correct version
python scripts/create_release.py v1.2.0
```

### Failed release merge

**Problem:** Release won't merge to main due to conflicts

**Solution:**
```bash
# Create a preparation branch
git checkout -b release-prep main
git merge release/v1.2.0

# Resolve all conflicts
# Test everything
npm test

# Create PR from release-prep to main
gh pr create --base main

# After approval, finish release normally
```

### Forgot to update version files

**Problem:** Merged release without updating package.json

**Solution:**
```bash
# Create a quick hotfix
git checkout main
git checkout -b hotfix/version-update

# Update version
vim package.json
git add package.json
git commit -m "fix: update version to v1.2.0"

# Finish hotfix
python scripts/finish_branch.py
```

## Hotfix Problems

### Cannot determine version

**Problem:** No tags on main branch

**Solution:**
```bash
# Manually create initial tag
git checkout main
git tag -a v1.0.0 -m "Initial version"
git push origin v1.0.0

# Now create hotfix
python scripts/create_hotfix.py critical-fix
```

### Hotfix conflicts with develop

**Problem:** Hotfix creates conflicts when merging to develop

**Solution:**
```bash
# Merge main to develop first
git checkout develop
git merge main  # This brings the hotfix

# Resolve any conflicts
vim conflicted-files
git add .
git commit

# Continue normal flow
```

### Emergency hotfix on old version

**Problem:** Need to fix older version still in production

**Solution:**
```bash
# Create branch from old tag
git checkout -b hotfix/v1.0.1 v1.0.0

# Make fix
vim src/critical-fix.js
git commit -am "fix: critical security issue"

# Create new tag
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin hotfix/v1.0.1 --tags

# Cherry-pick to current version if needed
git checkout main
git cherry-pick <commit-hash>
```

## Recovery Procedures

### Accidentally deleted branch

**Solution:**
```bash
# Find the commit hash
git reflog

# Recreate branch
git checkout -b feature/recovered <commit-hash>
```

### Lost uncommitted work

**Solution:**
```bash
# Check if it was stashed
git stash list

# Check if files are in git's database
git fsck --lost-found

# Check if IDE has local history
# (VSCode, IntelliJ, etc. often have this)
```

### Pushed sensitive data

**URGENT Solution:**
```bash
# Remove from history (destructive!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive-file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push all branches
git push origin --force --all

# Force push tags
git push origin --force --tags

# Better: Rotate any exposed credentials immediately!
```

### Repository in broken state

**Nuclear option - reset everything:**
```bash
# Backup current state
cp -r .git .git-backup

# Reset to remote state
git fetch origin
git reset --hard origin/develop  # or main

# Clean untracked files
git clean -xfd

# If still broken, clone fresh
cd ..
mv my-repo my-repo-broken
git clone <repo-url> my-repo
```

## Common Error Messages

### "fatal: not a git repository"

**Solution:**
```bash
# Initialize git
git init

# Or you're in wrong directory
cd /path/to/your/repo
```

### "fatal: refusing to merge unrelated histories"

**Solution:**
```bash
# Allow unrelated histories
git pull origin develop --allow-unrelated-histories
```

### "error: failed to push some refs"

**Solution:**
```bash
# Pull first
git pull origin <branch>

# Or force (careful!)
git push --force-with-lease origin <branch>
```

### "error: Your local changes would be overwritten"

**Solution:**
```bash
# Stash changes
git stash

# Do the operation
git checkout other-branch

# Restore changes
git stash pop
```

### "fatal: ambiguous argument"

**Solution:**
```bash
# Be more specific
git checkout origin/feature/my-feature
# or
git checkout -b feature/my-feature origin/feature/my-feature
```

## Prevention Tips

### Always verify before operations

```bash
# Before creating branch
git branch -a | grep feature/

# Before merging
git diff develop...feature/x

# Before pushing
git log origin/develop..HEAD

# Before deleting
git log branch-to-delete -1
```

### Use aliases for safety

```bash
# Add to ~/.gitconfig
[alias]
    safe-push = push --force-with-lease
    unstage = reset HEAD --
    last = log -1 HEAD
    undo = reset --soft HEAD~1
```

### Regular maintenance

```bash
# Weekly cleanup
git fetch --prune
git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -d

# Check for issues
git fsck
git gc
```
