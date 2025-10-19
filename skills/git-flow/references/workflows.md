# Git Flow Detailed Workflows

Comprehensive workflow patterns for Git Flow implementation.

## Table of Contents

- [Complete Feature Development Workflow](#complete-feature-development-workflow)
- [Release Preparation Workflow](#release-preparation-workflow)
- [Emergency Hotfix Workflow](#emergency-hotfix-workflow)
- [Parallel Development Patterns](#parallel-development-patterns)
- [Conflict Resolution Strategies](#conflict-resolution-strategies)
- [Pull Request Workflows](#pull-request-workflows)
- [Team Collaboration Patterns](#team-collaboration-patterns)

## Complete Feature Development Workflow

### 1. Feature Planning Phase

Before starting development:
```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Review existing features
git branch -a | grep feature/

# Check for related work
git log --grep="authentication" --oneline
```

### 2. Feature Creation

```bash
# Create feature branch
git checkout -b feature/user-authentication

# Or use the script
python scripts/create_feature.py user-authentication
```

### 3. Development Cycle

#### Daily Workflow
```bash
# Start of day: sync with develop
git fetch origin develop
git merge origin/develop  # or rebase if preferred

# Work and commit
git add src/auth/*
git commit -m "feat(auth): implement JWT token generation"

# End of day: push progress
git push origin feature/user-authentication
```

#### Commit Best Practices
```bash
# Atomic commits
git add src/auth/jwt.js
git commit -m "feat(auth): add JWT token generation"

git add tests/auth/jwt.test.js
git commit -m "test(auth): add JWT generation tests"

git add docs/auth.md
git commit -m "docs(auth): document JWT implementation"
```

### 4. Feature Completion

```bash
# Final sync with develop
git fetch origin develop
git merge origin/develop

# Run all tests
npm test

# Create pull request
gh pr create --base develop --title "feat: user authentication system"

# After approval, finish
python scripts/finish_branch.py
```

## Release Preparation Workflow

### 1. Pre-Release Checklist

```bash
# Review all features in develop
git log develop ^main --oneline

# Check for incomplete features
git branch -r | grep feature/

# Run full test suite
npm test
npm run e2e
npm run integration
```

### 2. Release Branch Creation

```bash
# Determine version based on changes
# Major: breaking changes
# Minor: new features
# Patch: bug fixes only

# Create release branch
python scripts/create_release.py v1.2.0
```

### 3. Release Preparation Tasks

```bash
# On release/v1.2.0 branch

# 1. Update version files
vim package.json  # Update version
vim VERSION       # If you have a VERSION file

# 2. Update changelog
vim CHANGELOG.md  # Review and enhance generated changelog

# 3. Update documentation
vim README.md     # Update version references
vim docs/api.md   # Update API docs

# 4. Final testing
npm test
npm run build
npm run smoke-test

# 5. Commit preparations
git add .
git commit -m "chore(release): prepare v1.2.0 release"
git push
```

### 4. Release Finalization

```bash
# Create PR to main
gh pr create --base main --title "release: v1.2.0"

# After approval, finish release
python scripts/finish_branch.py

# This will:
# - Merge to main
# - Create tag v1.2.0
# - Merge back to develop
# - Delete release branch
```

## Emergency Hotfix Workflow

### 1. Issue Identification

```bash
# Check production status
git checkout main
git pull origin main
git log --oneline -10

# Verify the issue
# Review error logs, monitoring, etc.
```

### 2. Hotfix Creation

```bash
# Create hotfix immediately
python scripts/create_hotfix.py critical-security-fix

# You're now on hotfix/critical-security-fix
```

### 3. Fix Implementation

```bash
# Minimal fix only - no extra changes!
vim src/security/validator.js

# Test the specific fix
npm test src/security/validator.test.js

# Commit with clear message
git add src/security/validator.js
git commit -m "fix: prevent SQL injection in user input validation

CRITICAL: This fixes a security vulnerability that allows SQL injection
through unescaped user input in the search functionality.

Affected versions: v1.2.0 - v1.2.3
Solution: Properly escape all user input before database queries"
```

### 4. Hotfix Deployment

```bash
# Push and create PR
git push
gh pr create --base main --title "hotfix: critical security fix" --label "critical,security"

# After emergency approval
python scripts/finish_branch.py

# Deploy immediately!
./deploy-production.sh v1.2.4
```

### 5. Post-Hotfix Actions

```bash
# Verify fix in production
curl https://api.production.com/health

# Monitor for issues
tail -f /var/log/application.log

# Document incident
vim docs/incidents/2024-01-15-sql-injection.md
```

## Parallel Development Patterns

### Multiple Features

When working on multiple features simultaneously:

```bash
# Feature 1: Authentication
git checkout develop
git checkout -b feature/authentication

# Work on feature 1
git add . && git commit -m "feat(auth): add login"
git checkout develop

# Feature 2: Payment
git checkout -b feature/payment

# Work on feature 2
git add . && git commit -m "feat(payment): add stripe integration"

# Switch between features
git checkout feature/authentication
# continue work...
```

### Feature Dependencies

When feature B depends on feature A:

```bash
# Complete feature A first
git checkout feature/user-profile
git push
# Create PR and get it reviewed

# Start feature B from feature A
git checkout -b feature/user-settings

# After feature A is merged to develop
git checkout feature/user-settings
git rebase develop
```

## Conflict Resolution Strategies

### Merge Conflicts During Feature Development

```bash
# Conflict when merging develop into feature
git checkout feature/my-feature
git merge develop
# CONFLICT in src/app.js

# Resolve conflicts
vim src/app.js
# Look for <<<<<<< HEAD, =======, >>>>>>> develop
# Keep the appropriate code

# Complete merge
git add src/app.js
git commit  # Will use default merge message
```

### Rebase Strategy (Alternative)

```bash
# Rebase feature on latest develop
git checkout feature/my-feature
git rebase develop

# If conflicts occur
vim conflicted-file.js
git add conflicted-file.js
git rebase --continue

# Force push if already published
git push --force-with-lease origin feature/my-feature
```

## Pull Request Workflows

### Creating Effective PRs

```bash
# Push latest changes
git push origin feature/user-authentication

# Create PR with template
gh pr create \
  --base develop \
  --title "feat: add user authentication system" \
  --body "## Summary
Implements complete user authentication with JWT tokens.

## Changes
- Add login/logout endpoints
- Implement JWT token generation
- Add password hashing with bcrypt
- Create auth middleware

## Testing
- Unit tests: 45 passing
- Integration tests: 12 passing
- Manual testing completed

## Checklist
- [x] Tests passing
- [x] Documentation updated
- [x] No console.logs
- [x] Security review completed"
```

### PR Review Process

```bash
# As reviewer, check out PR locally
gh pr checkout 123

# Run tests
npm test

# Review changes
git diff develop...HEAD

# Approve or request changes
gh pr review 123 --approve
# or
gh pr review 123 --request-changes -b "Please add tests for error cases"
```

## Team Collaboration Patterns

### Daily Sync Pattern

```bash
# Morning routine
git fetch --all
git checkout develop
git pull origin develop

# Check team activity
git log --oneline --graph --all --since="1 day ago"

# Update your feature branch
git checkout feature/my-feature
git merge develop  # or rebase
```

### Code Review Workflow

```bash
# Before requesting review
git diff develop...HEAD --stat  # Review your changes
npm test  # Ensure tests pass
npm run lint  # Check code style

# Request review
gh pr create --assignee @teammate1,@teammate2

# After feedback
git add .
git commit -m "fix: address PR feedback"
git push
```

### Release Coordination

```bash
# Release manager workflow
# 1. Announce release freeze
echo "Release v1.2.0 freeze - no new features to develop"

# 2. Create release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 3. Coordinate testing
echo "QA Team: Please test release/v1.2.0"

# 4. Manage release PRs
gh pr create --base main --assignee @tech-lead

# 5. Tag and deploy
python scripts/finish_branch.py
./scripts/deploy.sh v1.2.0
```

## Advanced Patterns

### Cherry-Picking Hotfixes

When a hotfix needs to be applied to multiple versions:

```bash
# Create hotfix from main
git checkout -b hotfix/security-fix main

# Make fix
git commit -m "fix: security vulnerability"

# Apply to other branches
git checkout release/v1.1.x
git cherry-pick <commit-hash>

git checkout release/v1.0.x
git cherry-pick <commit-hash>
```

### Feature Flags Pattern

For long-running features:

```bash
# Develop behind feature flag
git checkout -b feature/new-dashboard

# Commit with flag
git commit -m "feat(dashboard): add new dashboard (behind flag)

Feature flag: NEW_DASHBOARD_ENABLED
Default: false"

# Can merge to develop/main even if incomplete
python scripts/finish_branch.py

# Enable in production when ready
# No code deployment needed
```

### Squash Merging Pattern

For cleaner history:

```bash
# Before finishing feature
git checkout feature/messy-history

# Interactive rebase to clean up
git rebase -i develop

# Squash related commits
# Mark commits with 's' to squash

# Or merge with squash
git checkout develop
git merge --squash feature/messy-history
git commit -m "feat: complete feature implementation"
```
