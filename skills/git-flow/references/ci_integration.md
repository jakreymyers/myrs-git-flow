# Git Flow CI/CD Integration

Integrating Git Flow with continuous integration and deployment pipelines.

## Table of Contents

- [GitHub Actions Integration](#github-actions-integration)
- [GitLab CI Integration](#gitlab-ci-integration)
- [Jenkins Integration](#jenkins-integration)
- [Branch Protection Rules](#branch-protection-rules)
- [Automated Testing Strategies](#automated-testing-strategies)
- [Deployment Automation](#deployment-automation)
- [Release Automation](#release-automation)

## GitHub Actions Integration

### Basic Git Flow Workflow

`.github/workflows/git-flow.yml`:
```yaml
name: Git Flow CI

on:
  push:
    branches: [main, develop, 'feature/**', 'release/**', 'hotfix/**']
  pull_request:
    branches: [main, develop]

jobs:
  validate-branch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate branch name
        run: |
          branch=${GITHUB_REF#refs/heads/}
          if [[ "$branch" =~ ^(main|develop|feature/.+|release/v[0-9]+\.[0-9]+\.[0-9]+|hotfix/.+)$ ]]; then
            echo "✓ Valid Git Flow branch: $branch"
          else
            echo "✗ Invalid branch name: $branch"
            exit 1
          fi

  test:
    runs-on: ubuntu-latest
    needs: validate-branch
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test
        
      - name: Run linting
        run: npm run lint
```

### Feature Branch Workflow

`.github/workflows/feature.yml`:
```yaml
name: Feature Branch CI

on:
  push:
    branches: ['feature/**']

jobs:
  feature-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Check sync with develop
        run: |
          git fetch origin develop
          behind=$(git rev-list --count HEAD..origin/develop)
          if [ "$behind" -gt 0 ]; then
            echo "⚠️  Feature branch is $behind commits behind develop"
            echo "Run: git merge origin/develop"
          fi
          
      - name: Run tests
        run: |
          npm ci
          npm test
          
      - name: Check code coverage
        run: |
          npm run test:coverage
          # Fail if coverage < 80%
          coverage=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$coverage < 80" | bc -l) )); then
            echo "✗ Coverage too low: $coverage%"
            exit 1
          fi
```

### Release Branch Automation

`.github/workflows/release.yml`:
```yaml
name: Release Branch CI/CD

on:
  push:
    branches: ['release/**']

jobs:
  prepare-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        
      - name: Extract version
        id: version
        run: |
          branch=${GITHUB_REF#refs/heads/release/}
          echo "version=$branch" >> $GITHUB_OUTPUT
          
      - name: Update package.json version
        run: |
          npm version ${{ steps.version.outputs.version }} --no-git-tag-version
          
      - name: Generate changelog
        run: |
          npm run changelog
          
      - name: Commit changes
        run: |
          git config --global user.name 'GitHub Actions'
          git config --global user.email 'actions@github.com'
          git add .
          git commit -m "chore(release): prepare ${{ steps.version.outputs.version }}" || true
          git push
          
      - name: Run release tests
        run: |
          npm ci
          npm run test
          npm run test:e2e
          npm run test:integration
          
      - name: Build artifacts
        run: |
          npm run build
          
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: release-${{ steps.version.outputs.version }}
          path: dist/
```

### Hotfix Automation

`.github/workflows/hotfix.yml`:
```yaml
name: Hotfix CI/CD

on:
  push:
    branches: ['hotfix/**']

jobs:
  hotfix-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Fast security scan
        run: |
          npm audit --audit-level=critical
          
      - name: Run critical tests only
        run: |
          npm ci
          npm run test:critical
          
      - name: Build hotfix
        run: |
          npm run build:production
          
      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "🔥 Hotfix branch pushed: ${{ github.ref }}",
              attachments: [{
                color: 'danger',
                text: 'Requires immediate attention and deployment!'
              }]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## GitLab CI Integration

### Complete Git Flow Pipeline

`.gitlab-ci.yml`:
```yaml
stages:
  - validate
  - test
  - build
  - deploy

variables:
  GIT_STRATEGY: fetch
  GIT_DEPTH: 0

# Branch validation
validate:branch:
  stage: validate
  script:
    - |
      if [[ ! "$CI_COMMIT_BRANCH" =~ ^(main|develop|feature/.+|release/v[0-9]+\.[0-9]+\.[0-9]+|hotfix/.+)$ ]]; then
        echo "Invalid branch name: $CI_COMMIT_BRANCH"
        exit 1
      fi
  only:
    - branches

# Feature branch tests
test:feature:
  stage: test
  script:
    - npm ci
    - npm test
    - npm run lint
  only:
    - /^feature\/.*/

# Release branch pipeline
build:release:
  stage: build
  script:
    - npm ci
    - npm run build:production
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - /^release\/.*/

# Deploy to staging from develop
deploy:staging:
  stage: deploy
  script:
    - npm ci
    - npm run build
    - npm run deploy:staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

# Deploy to production from main
deploy:production:
  stage: deploy
  script:
    - npm ci
    - npm run build:production
    - npm run deploy:production
  environment:
    name: production
    url: https://example.com
  only:
    - main
  when: manual
```

## Jenkins Integration

### Jenkinsfile for Git Flow

```groovy
pipeline {
    agent any
    
    environment {
        BRANCH_NAME = "${env.GIT_BRANCH}"
    }
    
    stages {
        stage('Validate Branch') {
            steps {
                script {
                    if (!BRANCH_NAME.matches('^(main|develop|feature/.+|release/v[0-9]+\\.[0-9]+\\.[0-9]+|hotfix/.+)$')) {
                        error("Invalid Git Flow branch: ${BRANCH_NAME}")
                    }
                }
            }
        }
        
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit'
                    }
                }
                stage('Lint') {
                    steps {
                        sh 'npm run lint'
                    }
                }
                stage('Security Scan') {
                    steps {
                        sh 'npm audit'
                    }
                }
            }
        }
        
        stage('Build') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    branch pattern: 'release/.*', comparator: 'REGEXP'
                }
            }
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Deploy Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh 'npm run deploy:staging'
            }
        }
        
        stage('Deploy Production') {
            when {
                branch 'main'
            }
            steps {
                input 'Deploy to production?'
                sh 'npm run deploy:production'
            }
        }
    }
    
    post {
        failure {
            emailext (
                subject: "Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Branch: ${BRANCH_NAME}\n${env.BUILD_URL}",
                to: 'team@example.com'
            )
        }
    }
}
```

## Branch Protection Rules

### GitHub Branch Protection

```javascript
// github-branch-protection.js
const { Octokit } = require("@octokit/rest");

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

async function setupBranchProtection() {
  const owner = "your-org";
  const repo = "your-repo";
  
  // Protect main branch
  await octokit.repos.updateBranchProtection({
    owner,
    repo,
    branch: "main",
    required_status_checks: {
      strict: true,
      contexts: ["continuous-integration", "tests", "security-scan"]
    },
    enforce_admins: true,
    required_pull_request_reviews: {
      required_approving_review_count: 2,
      dismiss_stale_reviews: true,
      require_code_owner_reviews: true
    },
    restrictions: null,
    allow_force_pushes: false,
    allow_deletions: false
  });
  
  // Protect develop branch
  await octokit.repos.updateBranchProtection({
    owner,
    repo,
    branch: "develop",
    required_status_checks: {
      strict: true,
      contexts: ["continuous-integration", "tests"]
    },
    enforce_admins: false,
    required_pull_request_reviews: {
      required_approving_review_count: 1,
      dismiss_stale_reviews: true
    },
    restrictions: null,
    allow_force_pushes: false,
    allow_deletions: false
  });
}
```

## Automated Testing Strategies

### Test Execution by Branch Type

```javascript
// test-runner.js
const branch = process.env.GIT_BRANCH || '';

async function runTests() {
  // Always run unit tests
  await runCommand('npm run test:unit');
  
  if (branch.startsWith('feature/')) {
    // Feature branches: unit + integration
    await runCommand('npm run test:integration');
    
  } else if (branch.startsWith('release/')) {
    // Release branches: full test suite
    await runCommand('npm run test:unit');
    await runCommand('npm run test:integration');
    await runCommand('npm run test:e2e');
    await runCommand('npm run test:performance');
    
  } else if (branch.startsWith('hotfix/')) {
    // Hotfix branches: critical + regression
    await runCommand('npm run test:critical');
    await runCommand('npm run test:regression');
    
  } else if (branch === 'develop') {
    // Develop: comprehensive testing
    await runCommand('npm run test:unit');
    await runCommand('npm run test:integration');
    await runCommand('npm run test:smoke');
    
  } else if (branch === 'main') {
    // Main: production validation
    await runCommand('npm run test:smoke');
    await runCommand('npm run test:production');
  }
}
```

## Deployment Automation

### Automatic Deployment Configuration

```yaml
# deployment-config.yml
deployments:
  # Feature branches -> Review apps
  feature:
    trigger: push
    environment: review
    url: "https://review-{branch}.example.com"
    auto_deploy: true
    cleanup_on_merge: true
    
  # Develop -> Staging
  develop:
    trigger: push
    environment: staging
    url: "https://staging.example.com"
    auto_deploy: true
    health_check: true
    rollback_on_failure: true
    
  # Release branches -> Pre-production
  release:
    trigger: push
    environment: pre-production
    url: "https://pre-prod.example.com"
    auto_deploy: false
    requires_approval: true
    
  # Main -> Production
  main:
    trigger: tag
    environment: production
    url: "https://example.com"
    auto_deploy: false
    requires_approval: true
    backup_before_deploy: true
    blue_green_deployment: true
```

### Deployment Script

```bash
#!/bin/bash
# deploy.sh

BRANCH=$(git rev-parse --abbrev-ref HEAD)
ENVIRONMENT=""

# Determine environment based on branch
case "$BRANCH" in
  main)
    ENVIRONMENT="production"
    ;;
  develop)
    ENVIRONMENT="staging"
    ;;
  release/*)
    ENVIRONMENT="pre-production"
    ;;
  feature/*)
    ENVIRONMENT="review"
    ;;
  hotfix/*)
    ENVIRONMENT="hotfix"
    ;;
  *)
    echo "No deployment configured for branch: $BRANCH"
    exit 1
    ;;
esac

echo "Deploying branch '$BRANCH' to '$ENVIRONMENT'"

# Run environment-specific deployment
case "$ENVIRONMENT" in
  production)
    npm run build:production
    npm run deploy:production
    npm run health-check:production
    ;;
  staging)
    npm run build:staging
    npm run deploy:staging
    ;;
  *)
    npm run build
    npm run deploy:$ENVIRONMENT
    ;;
esac
```

## Release Automation

### Automated Release Process

```javascript
// auto-release.js
const { exec } = require('child_process');
const fs = require('fs');

async function automateRelease(version) {
  const steps = [
    // 1. Create release branch
    `git checkout develop`,
    `git pull origin develop`,
    `git checkout -b release/${version}`,
    
    // 2. Update version
    `npm version ${version} --no-git-tag-version`,
    
    // 3. Generate changelog
    `conventional-changelog -p angular -i CHANGELOG.md -s`,
    
    // 4. Commit changes
    `git add .`,
    `git commit -m "chore(release): prepare ${version}"`,
    
    // 5. Push branch
    `git push -u origin release/${version}`,
    
    // 6. Create pull requests
    `gh pr create --base main --title "Release ${version}" --body "Release ${version}"`,
    `gh pr create --base develop --title "Merge back ${version}" --body "Merge release back to develop"`
  ];
  
  for (const step of steps) {
    await execCommand(step);
  }
}

// Semantic version detection
async function detectNextVersion() {
  const commits = await getCommitsSinceLastTag();
  
  let major = false;
  let minor = false;
  let patch = false;
  
  commits.forEach(commit => {
    if (commit.includes('BREAKING CHANGE')) major = true;
    else if (commit.startsWith('feat')) minor = true;
    else if (commit.startsWith('fix')) patch = true;
  });
  
  if (major) return 'major';
  if (minor) return 'minor';
  if (patch) return 'patch';
  return null;
}
```

### Tag and Release Creation

```yaml
# .github/workflows/create-release.yml
name: Create Release

on:
  push:
    branches: [main]
    paths-ignore:
      - '**.md'

jobs:
  create-release:
    if: "!contains(github.event.head_commit.message, '[skip-release]')"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Get version from package.json
        id: version
        run: |
          VERSION=$(node -p "require('./package.json').version")
          echo "version=v$VERSION" >> $GITHUB_OUTPUT
          
      - name: Create tag
        run: |
          git tag -a ${{ steps.version.outputs.version }} -m "Release ${{ steps.version.outputs.version }}"
          git push origin ${{ steps.version.outputs.version }}
          
      - name: Generate release notes
        id: changelog
        run: |
          CHANGELOG=$(git log --pretty=format:"- %s" $(git describe --tags --abbrev=0 @^)..@)
          echo "changelog<<EOF" >> $GITHUB_OUTPUT
          echo "$CHANGELOG" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
          
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ steps.version.outputs.version }}
          release_name: Release ${{ steps.version.outputs.version }}
          body: ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false
```
