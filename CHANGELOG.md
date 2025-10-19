# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-10-19

### Fixed

- **Critical**: Removed invalid hooks field from plugin.json that prevented plugin installation
  - The hooks field contained an unsupported structure with "enabled" and "description" properties
  - Hooks are now properly loaded from the default `hooks/hooks.json` location
  - Plugin validation now passes and installation works correctly

## [1.1.0] - 2024-10-18

### Added

- **Git Flow Validation Hooks**: Three automated hooks to enforce Git Flow best practices
  - `conventional-commits`: Enforces conventional commit message format (feat, fix, docs, etc.)
  - `prevent-direct-push`: Blocks direct pushes to protected branches (main, develop)
  - `validate-branch-name`: Ensures branch names follow Git Flow conventions (feature/*, release/*, hotfix/*)
- Comprehensive README documentation including:
  - Git Flow diagram and branch type explanations
  - Git Flow Manager agent capabilities with visual examples
  - Complete hook documentation with usage examples
  - Statusline integration guide linking to awesome-claude-statusline
  - Reference to "Complete Guide to Setting Up Git Flow in Claude Code" article
- Hook metadata in plugin.json for automatic discovery
- Plugin hooks configuration in `hooks/hooks.json`

### Fixed

- Removed invalid `model: sonnet` specification from command frontmatter files
- Removed npm test inline command from finish command that was causing permission errors

### Changed

- Updated plugin version to 1.1.0
- Converted hooks from project-level to plugin-level for automatic installation
- Updated hook paths to use `${CLAUDE_PLUGIN_ROOT}` for plugin distribution

## [1.0.0] - 2024-10-18

### Added

- Initial release of MYRS Git Flow plugin
- Git Flow Manager agent for automated workflow management
- `/myrs-git-flow:feature <name>` - Create feature branches from develop
- `/myrs-git-flow:release <version>` - Create release branches with version management
- `/myrs-git-flow:hotfix <name>` - Create hotfix branches from main
- `/myrs-git-flow:finish` - Complete and merge branches with cleanup
- `/myrs-git-flow:flow-status` - Display comprehensive Git Flow repository status
- Comprehensive documentation and best practices
- MIT License
