# MYRS Git Flow Plugin

Git workflow automation and best practices for seamless version control, branching strategies, commit conventions, and collaboration workflows.

> 🎉 **NEW**: Now featuring [**Claude Skills**](https://www.anthropic.com/news/skills) - the revolutionary new capability from Anthropic that enables progressive disclosure of specialized knowledge and automation!

## Overview

MYRS Git Flow is the **most flexible and powerful Git Flow implementation for AI-assisted development**. Built on Anthropic's recently announced [Claude Skills](https://www.anthropic.com/news/skills) capability, it provides three distinct usage modes that no other Git workflow tool can match - giving you unprecedented control over how AI assists your development workflow.

### Three Ways to Use MYRS Git Flow

**🤖 1. Git Flow Manager Subagent**
A specialized AI assistant with its own context window, invoked proactively by Claude or explicitly by you:
- **Separate context**: Operates independently without cluttering your main conversation
- **Specialized tools**: Has restricted access to only Git-relevant tools (Bash, Read, Grep, Glob, Edit, Write)
- **Git Flow expertise**: Custom system prompt with complete branching model knowledge
- **Proactive invocation**: Claude automatically delegates Git Flow tasks to this subagent
- **Explicit invocation**: You can request it directly: "Use the git-flow-manager to create a release"

The subagent handles complete workflows (branch creation, merging, validation, release management, PR generation) and returns results to your main conversation.

**⚡ 2. Slash Commands**
User-invoked commands that execute structured workflows - you type the command, agent handles the details:
- `/myrs-git-flow:feature <name>` - Create feature branch from develop
- `/myrs-git-flow:release <version>` - Create release branch with versioning
- `/myrs-git-flow:hotfix <name>` - Create emergency hotfix branch
- `/myrs-git-flow:finish` - Complete and merge current branch
- `/myrs-git-flow:flow-status` - Display comprehensive Git Flow status

Each command provides pre-validation checks, executes Git operations, and reports status. Commands can invoke the subagent or execute in main context depending on complexity.

**🧠 3. Claude Skill (Model-Invoked)**
Git Flow knowledge base that Claude autonomously accesses when relevant - available to main agent AND all subagents:
- **Progressive disclosure**: Claude only reads SKILL.md and reference files when Git Flow context is needed
- **Rationalization resistance**: 11-entry table countering shortcuts like "over a branch name" or "just this once"
- **Automation scripts**: 8 Python tools (validate_commit.py, suggest_version.py, flow_status.py, etc.)
- **Situational awareness**: Claude recognizes Git Flow situations and applies appropriate guidance
- **Universal access**: Both main agent and git-flow-manager subagent can consult the skill

The skill provides deep expertise without cluttering context - it's there when needed, invisible when not.

### Why This Matters

**Traditional Git tools** require you to:
- ❌ Remember all Git Flow commands and sequences
- ❌ Manually validate branch names, commit formats, and merge targets
- ❌ Context-switch between documentation and terminal

**AI assistants without Skills** give you:
- ❌ Generic advice that may miss Git Flow specifics
- ❌ Verbose explanations that clutter your main conversation
- ❌ No consistent enforcement of best practices

**MYRS Git Flow uniquely provides**:
- ✅ **Context preservation**: Subagent handles Git complexity in separate context
- ✅ **User control**: Slash commands for when you want direct workflow invocation
- ✅ **Autonomous intelligence**: Claude Skills provide Git Flow expertise to all agents automatically
- ✅ **Validated automation**: 8 tested Python scripts + RED-GREEN-REFACTOR methodology
- ✅ **Flexible invocation**: Proactive (Claude decides), explicit (you request), or command-driven (you type)

This combination of **subagents** (Anthropic's agent orchestration), **commands** (user-invoked workflows), and **Skills** (Anthropic's [just-released capability](https://www.anthropic.com/news/skills) for model-invoked knowledge) creates a Git Flow experience no other tool can match.

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

### 🤖 Git Flow Manager Subagent (NEW Architecture!)

Specialized AI assistant with its own context window and restricted tools:

![Git Flow Manager Agent](https://miro.medium.com/v2/resize:fit:720/format:webp/1*dsxfpIX0RaF0dN9ALpv4uA.png)

**Technical Details:**
- **Separate context**: Operates independently from main conversation
- **Custom system prompt**: Deep Git Flow expertise built into its instructions
- **Restricted tools**: Only has access to Git-relevant tools (Bash, Read, Grep, Glob, Edit, Write)
- **Proactive mode**: Marked "Use PROACTIVELY" so Claude invokes it automatically for Git Flow tasks
- **Explicit mode**: You can request it: "Use the git-flow-manager to..."

**Capabilities:**
- Branch creation with automatic validation and remote tracking
- Branch completion with merging, tagging, and cleanup
- Conventional commit message formatting
- Merge conflict detection and resolution guidance
- Release management with changelog generation
- Pull request generation with descriptive templates
- Status reporting with visual formatting
- **Accesses Claude Skill** for rationalization resistance and automation scripts

**File**: `agents/git-flow-manager.md`

### ⚡ Slash Commands (User-Invoked)

Five commands you type to trigger structured Git Flow workflows:

- `/myrs-git-flow:feature <name>` - Create feature branch from develop
- `/myrs-git-flow:release <version>` - Create release branch for version preparation
- `/myrs-git-flow:hotfix <name>` - Create hotfix branch from main for emergencies
- `/myrs-git-flow:finish` - Complete and merge current branch with validation
- `/myrs-git-flow:flow-status` - Display comprehensive Git Flow repository status

**How Commands Work:**
- **User-invoked**: You type the command (unlike Skills which are model-invoked)
- **Argument support**: Use `$ARGUMENTS` placeholder for dynamic values
- **Pre-validation**: Check working directory, branch status, remote sync before executing
- **Inline execution**: Commands can run bash directly with `!` backticks
- **Can invoke subagent**: Complex commands may delegate to git-flow-manager for heavy lifting

**File location**: `commands/*.md` (5 command files)

### 🧠 Claude Skill

**Git Flow implementation using Anthropic's [Claude Skills](https://www.anthropic.com/news/skills)**

**What Makes This Revolutionary:**
- **Model-invoked**: Claude decides when to read it (not user-invoked like commands)
- **Progressive disclosure**: Only accessed when Git Flow context is relevant
- **Universal access**: Available to main agent AND git-flow-manager subagent
- **Context-efficient**: Doesn't clutter conversation - read on-demand only

**Skill Components:**

**1. SKILL.md** - Core Git Flow knowledge:
  - Complete branching model (main, develop, feature/, release/, hotfix/)
  - Protected branch rules with NEVER/MUST authority language
  - 11-entry rationalization table countering common shortcuts:
    - "Over a branch name" → "Branch structure enforces code review, not cosmetic"
    - "Not risking X hours work" → "git stash = 3 minutes, stash is safe"
    - "Senior/CTO does this" → "Senior habit ≠ team policy"
  - Sunk cost recovery procedure with exact time breakdown (3-5 minutes)
  - Merge strategies, commit conventions, version management

**2. 8 Automation Scripts** (Python with comprehensive validation):
  - `validate_commit.py` - Conventional commit format validation
  - `suggest_version.py` - SemVer analysis from commit history
  - `flow_status.py` - Comprehensive Git Flow status reporting
  - `generate_changelog.py` - Automated CHANGELOG.md generation
  - `create_feature.py` - Feature branch creation with validation
  - `create_release.py` - Release branch management and versioning
  - `create_hotfix.py` - Emergency hotfix workflows
  - `finish_branch.py` - Branch completion automation

**3. Reference Files** (progressive disclosure):
  - `workflows.md` - Detailed workflow patterns
  - `troubleshooting.md` - Common issues and recovery procedures
  - `ci_integration.md` - CI/CD pipeline integration

**4. TESTING.md** - Complete validation report:
  - RED-GREEN-REFACTOR methodology (TDD for process documentation)
  - 8 pressure scenarios tested with 10+ agent trials
  - Captured rationalizations and counters
  - 100% compliance in GREEN phase after skill enhancement

**File location**: `skills/git-flow/` (SKILL.md + scripts/ + references/)

### 🔒 Validation Hooks

Three hooks ensure Git Flow best practices (installed automatically):

**1. Conventional Commits Hook**
- Enforces conventional commit message format
- Validates commit types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
- Enables automated versioning and changelog generation

**2. Prevent Direct Push Hook**
- Blocks direct pushes to protected branches (main, develop)
- Enforces Git Flow workflow with feature/release/hotfix branches
- Requires pull requests for protected branch changes

**3. Validate Branch Name Hook**
- Ensures branch names follow Git Flow conventions
- Validates format: feature/*, release/*, hotfix/*
- Prevents non-standard branch naming

### 📚 Documentation & Testing

- **TESTING.md**: Complete validation report (RED-GREEN-REFACTOR methodology)
- **agents/git-flow-manager.md**: Subagent system prompt and configuration
- **commands/*.md**: 5 slash command definitions with workflows
- **skills/git-flow/SKILL.md**: Model-invoked knowledge base
- **skills/git-flow/scripts/**: 8 Python automation tools
- **skills/git-flow/references/**: Progressive disclosure documentation

## Statusline Integration

Track your Git Flow status directly in Claude Code's statusline! For enhanced visibility of your current branch, sync status, and workflow state, check out:

🎨 **[Awesome Claude Statusline](https://github.com/jakreymyers/awesome-claude-statusline)**

This statusline configuration provides:
- Current branch with Git Flow indicators
- Sync status (commits ahead/behind)
- Working directory status
- Branch type identification (feature/release/hotfix)
- Visual feedback for your workflow state

## Usage Examples

### How the Three Modes Work Together

**🤖 Subagent (git-flow-manager)**
- **Proactive**: Claude automatically delegates Git Flow tasks to this subagent
- **Explicit**: You request it: "Use the git-flow-manager to create a release for v1.2.0"
- **Use when**: Complex workflows, want separate context, multiple operations
- **Example**: "I need to create a release with changelog and version bumping"

**⚡ Slash Commands**
- **User-invoked**: You type the command directly
- **Structured workflow**: Pre-defined steps with validation
- **Use when**: You know exactly what Git Flow operation you need
- **Examples**:
  - `/myrs-git-flow:feature payment-integration` - Create feature branch
  - `/myrs-git-flow:flow-status` - Quick status check
  - `/myrs-git-flow:finish` - Complete current branch

**🧠 Claude Skill (Automatic)**
- **Model-invoked**: Claude reads it when Git Flow context is detected
- **Progressive disclosure**: Only accessed when relevant
- **Universal**: Both main agent and subagent can access
- **Use when**: You don't think about it - it just works!
- **Examples of automatic activation**:
  - You ask about branching → Skill consulted
  - Subagent validates commit → Uses validation scripts
  - Agent resists shortcut → Cites rationalization table

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

## Technical Innovation

### Why MYRS Git Flow is Different

**Claude Skills Integration** (First in Git tooling):
- Anthropic just announced [Skills](https://www.anthropic.com/news/skills) as a revolutionary new capability
- MYRS Git Flow is among the first tools to leverage this technology
- Enables true progressive disclosure - agents access detailed knowledge only when needed
- Reduces context usage while providing deep expertise

**Triple-Mode Flexibility**:
1. **Subagent preserves context** - Specialized AI with separate context handles Git complexity
2. **Commands orchestrate workflows** - User-invoked automation with pre-validation
3. **Skills provide intelligence** - Model-invoked knowledge with progressive disclosure

**Validated Quality**:
- Comprehensive testing using RED-GREEN-REFACTOR methodology (TDD for process documentation)
- 8 pressure scenarios tested with 10+ agent trials
- Captured and countered real rationalization patterns
- 4 automation scripts validated with edge case testing
- See `TESTING.md` for complete validation report

**Production-Ready Automation**:
- 8 Python scripts with comprehensive validation
- Error handling with helpful guidance
- Visual output formatting
- Time-quantified procedures (no vague "this will take a while")
- Tested against actual Git repositories

**No Competitor Offers**:
- ❌ Other Git tools: Manual commands only
- ❌ AI assistants: General knowledge without domain expertise
- ❌ Git Flow extensions: No AI integration
- ✅ **MYRS Git Flow**: Subagent architecture + slash commands + Claude Skills

This combination of **subagents** (separate AI contexts), **slash commands** (user-invoked workflows), and **Claude Skills** (model-invoked progressive disclosure) creates a Git Flow experience that's impossible to replicate without Claude Code's architecture and Anthropic's [newly-released Skills technology](https://www.anthropic.com/news/skills).

## Resources

- 🎉 [Anthropic: Introducing Claude Skills](https://www.anthropic.com/news/skills) - The technology powering MYRS Git Flow
- 📖 [Complete Guide to Setting Up Git Flow in Claude Code](https://medium.com/@dan.avila7/complete-guide-to-setting-up-git-flow-in-claude-code-616477941f78)
- 🎨 [Awesome Claude Statusline](https://github.com/jakreymyers/awesome-claude-statusline)
- 📦 [MYRS.ai Marketplace](https://github.com/jakreymyers/myrs-ai-marketplace)
- 📋 [TESTING.md](skills/git-flow/TESTING.md) - Complete validation report

## License

MIT License - See [LICENSE](LICENSE) for details.
