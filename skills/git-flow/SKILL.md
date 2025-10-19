---
name: git-flow
description: Comprehensive Git Flow workflow management for feature branches, releases, hotfixes, and version control. When Claude needs to manage Git branches following Git Flow methodology, create releases, handle hotfixes, enforce commit conventions, or set up systematic version control workflows.
---

# Git Flow Workflow Management

Systematic Git Flow implementation for professional version control and release management.

## Quick Start

```bash
# Start a feature
git checkout develop
git checkout -b feature/user-authentication

# Finish a feature
git checkout develop
git merge --no-ff feature/user-authentication
git branch -d feature/user-authentication

# Create a release
git checkout -b release/v1.2.0
# Update version, prepare release
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
```

## Core Concepts

### Branch Types

- **main** - Production-ready code (protected)
- **develop** - Integration branch for features (protected)  
- **feature/** - New features (from develop → develop)
- **release/** - Release preparation (from develop → main + develop)
- **hotfix/** - Emergency fixes (from main → main + develop)

### When to Use Each Branch

**feature/** - New functionality, enhancements, non-urgent bug fixes
**release/** - Preparing a new version for production deployment
**hotfix/** - Critical production issues requiring immediate fix

## Branch Operations

### Creating Feature Branches

```bash
# Always start from develop
git checkout develop
git pull origin develop
git checkout -b feature/<descriptive-name>
git push -u origin feature/<descriptive-name>
```

Use `scripts/create_feature.py` for automated feature creation with validation.

### Creating Release Branches

```bash
# Start from develop
git checkout develop
git pull origin develop
git checkout -b release/v<MAJOR>.<MINOR>.<PATCH>
```

Use `scripts/create_release.py` for automated release creation with:
- Version validation
- Changelog generation
- Package.json updates

### Creating Hotfix Branches

```bash
# Start from main (production)
git checkout main
git pull origin main
git checkout -b hotfix/<descriptive-name>
```

Use `scripts/create_hotfix.py` for emergency fixes with automatic version bumping.

### Finishing Branches

Use `scripts/finish_branch.py` to complete any Git Flow branch:
- Validates all changes are committed
- Ensures tests pass
- Merges to appropriate branches
- Creates tags for releases/hotfixes
- Cleans up branches

## Commit Conventions

All commits MUST follow Conventional Commits format:

```
<type>(<scope>): <description>

[optional body]
```

### Types
- **feat** - New feature
- **fix** - Bug fix  
- **docs** - Documentation only
- **style** - Code style (formatting)
- **refactor** - Code restructuring
- **perf** - Performance improvements
- **test** - Adding/updating tests
- **chore** - Maintenance tasks
- **ci** - CI/CD changes
- **build** - Build system changes

### Examples
```bash
git commit -m "feat(auth): add JWT authentication"
git commit -m "fix: resolve memory leak in parser"
git commit -m "docs: update API documentation"
```

## Protected Branch Rules

**NEVER** push directly to main or develop. These branches require:
- Pull requests for all changes
- Code review approval
- Passing tests
- No merge conflicts

## Version Management

### Semantic Versioning

Use semantic versioning (vMAJOR.MINOR.PATCH):
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### Automatic Version Detection

Analyze commits to determine version bump:
- Breaking changes → Major version
- feat: commits → Minor version
- fix: commits → Patch version

Use `scripts/suggest_version.py` to analyze commits and suggest next version.

## Merge Strategies

### Feature → Develop
```bash
git checkout develop
git merge --no-ff feature/<n>  # Always use --no-ff
```

### Release → Main + Develop
```bash
# To main
git checkout main
git merge --no-ff release/v<version>
git tag -a v<version> -m "Release v<version>"

# Back to develop
git checkout develop
git merge --no-ff release/v<version>
```

### Hotfix → Main + Develop
```bash
# To main
git checkout main
git merge --no-ff hotfix/<n>
git tag -a v<new-patch> -m "Hotfix v<new-patch>"

# Back to develop
git checkout develop
git merge --no-ff hotfix/<n>
```

## Conflict Resolution

When conflicts occur:

1. **Identify conflicts**
   ```bash
   git status  # Shows conflicted files
   ```

2. **Resolve conflicts**
   - Open conflicted files
   - Look for conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
   - Choose appropriate code
   - Remove conflict markers

3. **Complete merge**
   ```bash
   git add <resolved-files>
   git commit
   ```

## Status Checking

Use `scripts/flow_status.py` to get comprehensive Git Flow status:
- Current branch type and validity
- Sync status with remote
- Working directory changes
- Active branches by type
- Merge readiness
- Recommended next actions

## Pull Request Best Practices

### PR Title Format
- Features: `feat: <description>`
- Fixes: `fix: <description>`
- Releases: `release: v<version>`
- Hotfixes: `hotfix: <description>`

### PR Description Template
```markdown
## Summary
[Brief description of changes]

## Type of Change
- [ ] Feature
- [ ] Bug Fix
- [ ] Hotfix
- [ ] Release

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

## Automation Scripts

### Available Scripts

- `scripts/create_feature.py` - Create and validate feature branches
- `scripts/create_release.py` - Create releases with version management
- `scripts/create_hotfix.py` - Create emergency hotfix branches
- `scripts/finish_branch.py` - Complete and merge any Git Flow branch
- `scripts/flow_status.py` - Display comprehensive Git Flow status
- `scripts/suggest_version.py` - Analyze commits and suggest version
- `scripts/generate_changelog.py` - Generate changelog from commits
- `scripts/validate_commit.py` - Validate commit message format

### Script Usage

All scripts can be run directly:
```bash
python scripts/create_feature.py user-authentication
python scripts/create_release.py v1.2.0
python scripts/finish_branch.py --no-delete
```

## Advanced Workflows

For complex scenarios, see reference documentation:
- `references/workflows.md` - Detailed workflow patterns
- `references/troubleshooting.md` - Common issues and solutions
- `references/ci_integration.md` - CI/CD pipeline integration

## Quick Reference

### Commands by Scenario

**Starting new work:**
```bash
python scripts/create_feature.py <n>
```

**Preparing a release:**
```bash
python scripts/create_release.py v<version>
python scripts/generate_changelog.py
```

**Emergency fix:**
```bash
python scripts/create_hotfix.py <n>
python scripts/finish_branch.py
```

**Check status:**
```bash
python scripts/flow_status.py
```

**Complete work:**
```bash
python scripts/finish_branch.py
```

## Error Prevention

The skill includes validation to prevent common mistakes:
- Branch name validation (must follow Git Flow conventions)
- Protected branch push prevention
- Commit message format enforcement
- Merge conflict detection before operations
- Test execution before branch completion

## Best Practices

**DO:**
- ✅ Always pull before creating branches
- ✅ Use descriptive branch names
- ✅ Follow commit conventions
- ✅ Run tests before merging
- ✅ Delete branches after merging
- ✅ Keep features small and focused

**DON'T:**
- ❌ Push directly to main/develop
- ❌ Force push to shared branches
- ❌ Merge with failing tests
- ❌ Skip pull requests
- ❌ Leave stale branches
- ❌ Mix features in one branch

## Rationalization Counters

When tempted to skip Git Flow rules, recognize these common excuses and their reality:

| Excuse | Reality | Counter |
|--------|---------|---------|
| "Over a branch name" | Minimizes protected branch rules | Branch structure enforces code review + prevents unreviewed production code. Not cosmetic. |
| "Not risking X hours work" | Sunk cost fallacy | `git stash && git checkout -b feature/name && git stash pop` = 3 minutes. Stash is safe. |
| "Code already tested/working" | Quality ≠ process compliance | Process ensures team coordination, not just code quality. Manual testing ≠ PR review. |
| "Personal deadline (dinner/EOD)" | Personal urgency over discipline | 3-5 min proper workflow won't end relationship. Skipping pattern ends career trajectory. |
| "Senior/CTO does this" | Authority validates shortcuts | Senior's habit ≠ team policy. Tooling (hooks, CI/CD) depends on conventions regardless of seniority. |
| "Being pragmatic not dogmatic" | False dichotomy | Pragmatic = sustainable practices. Shortcuts create 10x cleanup cost tomorrow. Dogmatic would be "never adapt." |
| "Eventually sync up" | Wishful thinking | Divergent branches accumulate conflicts. "Later" becomes "never" or painful merge. Monday chaos guaranteed. |
| "Format doesn't matter" | Ignores automation | `suggest_version.py`, `generate_changelog.py`, CI/CD pipelines parse commit format. Breaking format breaks toolchain. |
| "Just this once" | Slippery slope | "Once" becomes precedent. Team sees shortcut → normalizes violation → chaos compounds. |
| "Keep as reference" | Disguised testing-after | Looking at old code = adapting it = testing after writing. Delete means delete. |
| "Time pressure (prod down)" | Emergency justifies shortcuts | Even emergencies use hotfix workflow. 5 min proper branching prevents 2-hour rollback later. |

### Sunk Cost Recovery

**Scenario:** Hours of work on wrong branch (main/develop instead of feature branch)

**Time cost:** 3-5 minutes
**Procedure:**
```bash
git stash push -m "Work in progress"           # 10 sec - safe
git checkout develop && git pull               # 15 sec
git checkout -b feature/descriptive-name       # 5 sec
git stash pop                                  # 10 sec - restores work
git add . && git commit -m "type: description" # 30 sec
git push -u origin feature/descriptive-name    # 20 sec
```

**Reality check:** Claiming "no time" for 3-5 minutes while spending hours coding = prioritization failure, not time constraint.
