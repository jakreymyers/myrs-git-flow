# Git Flow Skill for Claude

## Overview

This Git Flow skill has been created based on your MYRS Git Flow plugin for Claude Code. It provides comprehensive Git Flow workflow management capabilities that Claude can use to help with version control, branching strategies, and release management.

## What's Included

### Main Skill File (SKILL.md)
- Comprehensive Git Flow guidance and best practices
- Quick start commands for all branch types
- Commit conventions (Conventional Commits)
- Version management strategies
- Protected branch rules
- Merge strategies for each branch type

### Python Scripts (scripts/)

1. **create_feature.py** - Automated feature branch creation with validation
2. **create_release.py** - Release branch creation with version management and changelog generation
3. **create_hotfix.py** - Emergency hotfix branch creation with automatic version bumping
4. **finish_branch.py** - Complete and merge any Git Flow branch with proper cleanup
5. **flow_status.py** - Display comprehensive Git Flow status and recommendations
6. **suggest_version.py** - Analyze commits and suggest next semantic version
7. **generate_changelog.py** - Generate or update CHANGELOG.md from conventional commits
8. **validate_commit.py** - Validate commit messages against Conventional Commits spec

### Reference Documentation (references/)

1. **workflows.md** - Detailed workflow patterns for all Git Flow scenarios
2. **troubleshooting.md** - Common issues and their solutions
3. **ci_integration.md** - CI/CD pipeline integration (GitHub Actions, GitLab CI, Jenkins)

## How to Install the Skill

1. Download the packaged skill: `git-flow.zip`
2. Extract it to your skills directory
3. Claude will automatically detect and use it when you ask about Git Flow workflows

## Key Features

### Branch Management
- Automated creation of feature, release, and hotfix branches
- Branch name validation following Git Flow conventions
- Protection against direct pushes to main/develop
- Automatic cleanup after branch completion

### Version Control
- Semantic versioning support (MAJOR.MINOR.PATCH)
- Automatic version suggestion based on commit analysis
- Version file updates (package.json, etc.)
- Tag creation for releases and hotfixes

### Commit Standards
- Conventional Commits enforcement
- Commit message validation
- Automatic changelog generation from commits
- Breaking change detection

### Workflow Automation
- Pre-merge validation checks
- Test execution before branch completion
- Merge conflict detection
- Pull request template generation
- Deployment readiness checks

## Usage Examples

When using Claude with this skill, you can ask questions like:

- "How do I start a new feature branch for user authentication?"
- "Create a release branch for version 1.2.0"
- "What's the proper Git Flow workflow for emergency fixes?"
- "Generate a changelog from my recent commits"
- "Help me set up Git Flow CI/CD with GitHub Actions"
- "How do I resolve merge conflicts in a release branch?"
- "What version should my next release be based on recent commits?"

## Integration with Claude Code

While this skill is designed for general Claude use, it incorporates the same Git Flow principles and patterns from your MYRS Git Flow plugin. The main differences:

1. **Scripts vs Commands**: Instead of slash commands like `/myrs-git-flow:feature`, the skill uses Python scripts that can be executed directly
2. **No Hooks**: The skill doesn't include the Git hooks (as those need to be installed separately), but it's aware of their rules and won't suggest actions that would violate them
3. **Universal Use**: This skill can be used in any Git repository, not just within Claude Code

## Best Practices Enforced

The skill enforces these Git Flow best practices:

✅ Always branch from the correct base (develop for features, main for hotfixes)
✅ Use descriptive branch names following conventions
✅ Follow Conventional Commits format for all commits
✅ Run tests before completing branches
✅ Never push directly to protected branches
✅ Create tags for all releases and hotfixes
✅ Keep feature branches small and focused
✅ Delete branches after successful merge
✅ Maintain a clean, linear history with --no-ff merges

## Compatibility

This skill is compatible with:
- Any Git repository following Git Flow
- Projects using Node.js (package.json version management)
- CI/CD systems (GitHub Actions, GitLab CI, Jenkins)
- Teams using Conventional Commits
- Semantic versioning practices

## Source

This skill was created based on:
- The MYRS Git Flow Claude Code plugin (https://github.com/jakreymyers/myrs-git-flow)
- Industry best practices for Git Flow implementation (https://nvie.com/posts/a-successful-git-branching-model/)

## Support

The skill includes comprehensive troubleshooting documentation in `references/troubleshooting.md` for common issues. Claude can access this automatically when helping you resolve Git Flow problems.
