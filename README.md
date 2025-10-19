# MYRS Git Flow Plugin

Git workflow automation and best practices for seamless version control, branching strategies, commit conventions, and collaboration workflows.

> 📖 **Complete Guide**: For a comprehensive tutorial on setting up Git Flow in Claude Code, read [Complete Guide to Setting Up Git Flow in Claude Code](https://medium.com/@dan.avila7/complete-guide-to-setting-up-git-flow-in-claude-code-616477941f78) by Dan Avila.

## Overview

MYRS Git Flow (Claude Code plugin) provides comprehensive tools and patterns for managing Git workflows effectively. The plugin emphasizes systematic approaches to version control, commit quality, branch management, and team collaboration using the proven Git Flow branching model.

## What is Git Flow?

Git Flow is a branching model designed to provide a robust framework for managing larger projects with parallel development. It defines a strict branching structure that makes collaboration and release management more systematic.

![Git Flow Diagram](https://miro.medium.com/v2/resize:fit:720/format:webp/1*MA-cfyl9Cysel1SlNBYR-w.png)

### Branch Types

- **main**: Production-ready code (protected)
- **develop**: Integration branch for features (protected)
- **feature/**: New features (branches from develop, merges to develop)
- **release/**: Release preparation (branches from develop, merges to main and develop)
- **hotfix/**: Emergency production fixes (branches from main, merges to main and develop)

## Installation

Add the MYRS.ai marketplace first:

```bash
/plugin marketplace add jakreymyers/myrs-ai-marketplace
```

Then install MYRS Git Flow:

```bash
/plugin install myrs-git-flow@myrs-ai-marketplace
```

## What's Included

### Git Flow Manager Agent

The plugin includes an intelligent Git Flow manager that automates and enforces Git Flow branching strategies:

![Git Flow Manager Agent](https://miro.medium.com/v2/resize:fit:720/format:webp/1*dsxfpIX0RaF0dN9ALpv4uA.png)

**Capabilities:**
- Automated branch creation with validation
- Conventional commit message formatting
- Merge conflict detection and resolution guidance
- Release management and changelog generation
- Pull request generation with descriptive templates
- Status reporting with visual formatting

### Commands

Custom slash commands for Git Flow operations:

- `/myrs-git-flow:feature <name>` - Create a new feature branch from develop
- `/myrs-git-flow:release <version>` - Create a release branch for version preparation
- `/myrs-git-flow:hotfix <name>` - Create a hotfix branch from main
- `/myrs-git-flow:finish` - Complete and merge the current branch
- `/myrs-git-flow:flow-status` - Display comprehensive Git Flow status

### Hooks

Three validation hooks to ensure Git Flow best practices:

**1. Conventional Commits Hook**
- Enforces conventional commit message format
- Validates commit types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
- Ensures consistent commit history for changelog generation

**2. Prevent Direct Push Hook**
- Blocks direct pushes to protected branches (main, develop)
- Enforces Git Flow workflow with feature/release/hotfix branches
- Requires pull requests for protected branch changes

**3. Validate Branch Name Hook**
- Ensures branch names follow Git Flow conventions
- Validates format: feature/*, release/*, hotfix/*
- Prevents non-standard branch naming

### Workflows

Proven patterns for:

- Feature branch workflows
- Pull request creation and review
- Commit message formatting
- Merge strategies
- Release management
- Hotfix workflows

## Statusline Integration

Track your Git Flow status directly in Claude Code's statusline! For enhanced visibility of your current branch, sync status, and workflow state, check out:

🎨 **[Awesome Claude Statusline](https://github.com/jakreymyers/awesome-claude-statusline)**

This statusline configuration provides:
- Current branch with Git Flow indicators
- Sync status (commits ahead/behind)
- Working directory status
- Branch type identification (feature/release/hotfix)
- Visual feedback for your workflow state

## Usage

### Starting a New Feature

```bash
/myrs-git-flow:feature user-authentication
```

The agent will:
1. Verify you're on the correct base branch (develop)
2. Create `feature/user-authentication`
3. Set up remote tracking
4. Provide next steps

### Creating a Release

```bash
/myrs-git-flow:release v1.2.0
```

The agent will:
1. Create `release/v1.2.0` from develop
2. Update version in package.json (if applicable)
3. Generate changelog from commits
4. Guide you through release preparation

### Emergency Hotfix

```bash
/myrs-git-flow:hotfix critical-security-patch
```

The agent will:
1. Create `hotfix/critical-security-patch` from main
2. Provide guidance for urgent fixes
3. Set up for merging to both main and develop

### Completing Work

```bash
/myrs-git-flow:finish
```

The agent will:
1. Run validation checks
2. Merge to appropriate branches
3. Create tags for releases/hotfixes
4. Clean up merged branches
5. Push changes to remote

### Check Status

```bash
/myrs-git-flow:flow-status
```

Get a comprehensive view of:
- Current branch type and state
- Sync status with remote
- Working directory changes
- Active branches by type
- Merge readiness
- Recommended next steps


## Resources

- 📖 [Complete Guide to Setting Up Git Flow in Claude Code](https://medium.com/@dan.avila7/complete-guide-to-setting-up-git-flow-in-claude-code-616477941f78)
- 🎨 [Awesome Claude Statusline](https://github.com/jakreymyers/awesome-claude-statusline)
- 📦 [MYRS.ai Marketplace](https://github.com/jakreymyers/myrs-ai-marketplace)

## License

MIT License - See [LICENSE](LICENSE) for details.
