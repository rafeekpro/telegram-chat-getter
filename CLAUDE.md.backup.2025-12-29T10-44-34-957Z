# CLAUDE.md

> Think carefully and implement the most concise solution that changes as little code as possible.

## 🚨 AGENT USAGE - MANDATORY

**CRITICAL: You MUST use specialized agents for ALL non-trivial tasks.**

See: `.claude/rules/agent-mandatory.md` for complete enforcement rules.

### Quick Reference - When to Use Agents:

| Task Type | Agent | Example |
|-----------|-------|---------|
| Python code | `python-backend-engineer` | Build FastAPI endpoint |
| React/UI | `react-frontend-engineer` | Create dashboard component |
| Testing | `test-runner` | Run test suite |
| Database | `postgresql-expert`, `mongodb-expert` | Design schema |
| DevOps | `kubernetes-orchestrator`, `docker-containerization-expert` | Deploy app |
| Code review | `code-analyzer` | Find bugs/security issues |
| Large files | `file-analyzer` | Parse logs >1000 lines |

**Before doing ANY complex task**: Check if there's a specialized agent. If YES → USE IT!

## Active Team Agents

<!-- AGENTS_START -->
- @include .claude/agents/core/agent-manager.md
- @include .claude/agents/core/code-analyzer.md
- @include .claude/agents/core/test-runner.md
- @include .claude/agents/core/file-analyzer.md
- @include .claude/agents/languages/python-backend-engineer.md
- @include .claude/agents/languages/python-backend-expert.md
- @include .claude/agents/languages/nodejs-backend-engineer.md
- @include .claude/agents/languages/javascript-frontend-engineer.md
- @include .claude/agents/languages/bash-scripting-expert.md
<!-- AGENTS_END -->

## 🔄 STANDARD TASK WORKFLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│  🚨 CRITICAL: ALL DEVELOPMENT FOLLOWS TDD (RED-GREEN-REFACTOR)     │
├─────────────────────────────────────────────────────────────────────┤
│  1. 🔴 RED:     Write FAILING test first                            │
│  2. ✅ GREEN:   Write MINIMUM code to pass                          │
│  3. ♻️  REFACTOR: Improve while tests stay green                    │
│                                                                     │
│  ❌ NO CODE WITHOUT TESTS                                           │
│  ❌ NO PARTIAL IMPLEMENTATIONS                                      │
│  ❌ NO "TODO: ADD TESTS LATER"                                      │
│                                                                     │
│  See: .claude/rules/tdd.enforcement.md (HIGHEST PRIORITY)          │
└─────────────────────────────────────────────────────────────────────┘
```

### 🎯 Core Workflow Principles

1. **Follow TDD Religiously** - Test FIRST, code SECOND
2. **Work in Branches** - Never commit directly to main
3. **Create Pull Requests** - All changes go through PR review
4. **Resolve Conflicts** - Address merge conflicts immediately
5. **Address Feedback** - Interpret and resolve all PR comments
6. **Merge When Ready** - Only merge after all checks pass
7. **Mark Complete** - Update task status and move to next task

### 🚀 Task Execution Steps

#### 1. Pick Task → 2. Create Branch → 3. Implement (TDD) → 4. Verify → 5. Create PR → 6. Address Feedback → 7. Merge → 8. Complete → 9. Next Task

**TDD Implementation (Step 3):**
```bash
# 🔴 RED: Write failing test FIRST
touch tests/test_feature.py
@test-runner run tests/test_feature.py  # MUST FAIL ❌
git commit -m "test: add failing test for feature"

# ✅ GREEN: Write MINIMUM code to pass
@test-runner run tests/test_feature.py  # MUST PASS ✅
git commit -m "feat: implement feature"

# ♻️ REFACTOR: Improve while tests stay green
@test-runner run all tests  # ALL MUST PASS ✅
git commit -m "refactor: improve feature structure"
```

**Integration with Context7:**
```bash
# Query documentation BEFORE implementing
mcp://context7/<framework>/testing-best-practices
mcp://context7/<framework>/authentication-patterns
mcp://context7/<language>/test-frameworks
```

**Quality Checks (Step 4):**
```bash
npm test          # or pytest, go test, etc.
npm run lint      # or ruff check, golangci-lint, etc.
npm run typecheck # or mypy, go vet, etc.
```

**PR Creation (Step 5):**
```bash
git push origin feature/TASK-ID-description
gh pr create --title "Feature: TASK-ID Description" --body "..."
```

### 📊 Definition of Done

- [ ] Code Complete (Acceptance Criteria met, no TODOs)
- [ ] Tests Pass (unit, integration, e2e, coverage threshold met)
- [ ] Quality Checks (linters pass, formatters applied, type checking)
- [ ] Documentation (code comments, API docs, README, CHANGELOG)
- [ ] Review Complete (PR approved, comments addressed, CI/CD green)
- [ ] Deployed (merged to main, deployed, verified in production)
- [ ] Task Closed (issue closed, status updated)

### ⚠️ Critical Rules

**🚨 HIGHEST PRIORITY:**
1. **FOLLOW TDD CYCLE** - ZERO TOLERANCE for code without tests
2. **ALWAYS query Context7** before implementing: `mcp://context7/<framework>/<topic>`
3. **NEVER commit code before tests** - Test first, code second, refactor third
4. **ALWAYS use specialized agents** for non-trivial tasks

**❌ PROHIBITED PATTERNS:**
- Writing code before tests
- Committing "WIP" or "TODO: add tests"
- Partial implementations without test coverage
- Skipping refactor phase
- Mock services in tests (use real implementations)

### 🎯 Quick Commands

```bash
# Start task
/pm:backlog
git checkout -b feature/ID-desc

# During work
@<agent> <task>
mcp://context7/<lib>/<topic>
git commit -m "type: message"

# Before PR
npm test && npm run lint
git push origin <branch>

# Create & merge PR
gh pr create
gh pr merge --squash --delete-branch
gh issue close ID
```


## CRITICAL RULE FILES

All rule files in `.claude/rules/` define mandatory behaviors and must be followed:

### 🚨 HIGHEST PRIORITY Rules

- **agent-mandatory.md** - MANDATORY agent usage for all non-trivial tasks. READ THIS FIRST!
- **tdd.enforcement.md** - Test-Driven Development cycle (RED-GREEN-REFACTOR)
- **pipeline-mandatory.md** - Required pipelines for errors, features, bugs, code search, and log analysis

### Core Development Rules

- **naming-conventions.md** - Naming standards, code quality requirements, and prohibited patterns
- **context-optimization.md** - Agent usage patterns for context preservation (<20% data return)
- **development-workflow.md** - Development patterns, search-before-create, and best practices
- **command-pipelines.md** - Command sequences, prerequisites, and PM system workflows

### Operational Rules

- **agent-coordination.md** - Multi-agent parallel work with file-level coordination
- **agent-coordination-extended.md** - Extended coordination patterns for complex workflows
- **git-strategy.md** - Unified Git branch strategy, naming conventions, and merge workflows
- **datetime.md** - Real datetime requirements using ISO 8601 UTC format (no placeholders)
- **frontmatter-operations.md** - YAML frontmatter standards for PRDs, epics, and tasks
- **strip-frontmatter.md** - Metadata removal for GitHub sync and external communication
- **github-operations.md** - GitHub CLI safety and critical template repository protection
- **no-pr-workflow.md** - Direct main branch development without PRs

### Technical Rules

- **test-execution.md** - Testing standards requiring test-runner agent, no mocks, real services only
- **standard-patterns.md** - Command consistency, fail-fast philosophy, and minimal validation
- **use-ast-grep.md** - Structural code search using AST over regex for language-aware patterns
- **database-pipeline.md** - Database migrations, query optimization, and backup procedures
- **infrastructure-pipeline.md** - IaC deployments, container builds, and cloud operations

### Code Formatting & Quality

**MANDATORY**: All code MUST pass autoformatters and linters before commit:

- **Python**: Must pass `black` formatter and `ruff` linter
- **JavaScript/TypeScript**: Must pass `prettier` and `eslint`
- **Markdown**: Must pass `markdownlint`
- **Other languages**: Use language-specific standard tools

Always run formatters and linters BEFORE marking any task as complete.

## DOCUMENTATION REFERENCES

### Agent Documentation (`.claude/agents/`)

**📋 Complete Agent Registry**: See `.claude/agents/AGENT-REGISTRY.md` for comprehensive list of all available agents with descriptions, tools, and direct links.

Agents are organized by category for better maintainability:

- **Core Agents** (`.claude/agents/core/`) - Essential agents for all projects
- **Language Agents** (`.claude/agents/languages/`) - Language-specific experts
- **Framework Agents** (`.claude/agents/frameworks/`) - Framework and UI specialists
- **Cloud Agents** (`.claude/agents/cloud/`) - Cloud platform architects
- **DevOps Agents** (`.claude/agents/devops/`) - CI/CD and operations
- **Database Agents** (`.claude/agents/databases/`) - Database specialists
- **Data Agents** (`.claude/agents/data/`) - Data engineering

### Command Documentation (`.claude/commands/`)

- Custom commands and patterns documented in `.claude/commands/`
- **Azure DevOps Commands** (`.claude/commands/azure/`) - Complete Azure DevOps integration
- **PM Commands** (`.claude/commands/pm/`) - Project management workflow

## USE SUB-AGENTS FOR CONTEXT OPTIMIZATION

### Core Agents (Always Available)

#### file-analyzer - File and log analysis
Always use for reading and summarizing files, especially logs and verbose outputs.

#### code-analyzer - Bug hunting and logic tracing
Use for code analysis, bug detection, and tracing execution paths.

#### test-runner - Test execution and analysis
Use for running tests and analyzing results with structured reports.

#### parallel-worker - Multi-stream parallel execution
Use for coordinating multiple work streams in parallel.

## AGENT SELECTION GUIDANCE

Use appropriate agents for traditional development:

### Language Agents

#### javascript-frontend-engineer, nodejs-backend-engineer
- Modern JS/TS, ES6+, browser APIs
- Node.js backends, Express, NestJS
- Build tools, testing frameworks

#### python-backend-engineer
- FastAPI, Flask, Django development
- API design and implementation
- Traditional Python tooling (pip, virtualenv)

#### bash-scripting-expert
- Shell automation, system administration
- Build scripts, deployment automation
- POSIX compliance, cross-platform

### Framework Agents

#### react-frontend-engineer
- React, TypeScript, Next.js applications
- Component architecture and state management
- Traditional build tools (webpack, vite)

#### frontend-testing-engineer
- E2E testing with native runners
- Cross-browser testing
- Test automation frameworks

### Database Agents

#### postgresql-expert, mongodb-expert
- Local database setup and management
- Schema design and migrations
- Query optimization

### Cloud Agents (for deployment)

#### aws-cloud-architect, gcp-cloud-architect, azure-cloud-architect
- Traditional VM deployments
- Managed services configuration
- Infrastructure setup (not containerized)

---

**📋 Full Agent Details**: For complete agent descriptions, parameters, tools, and file locations, see `.claude/agents/AGENT-REGISTRY.md`

## Project Management

This project uses local development workflow without CI/CD automation.

### Development Workflow

1. **Local Development**
   - Make changes locally
   - Run tests manually
   - Commit when ready

2. **Manual Testing**
   - Test changes locally before committing
   - Use project-specific test commands
   - Verify functionality manually

3. **Deployment**
   - Deploy manually as needed
   - Follow project-specific deployment procedures
   - Coordinate with team for releases

### Version Control
```bash
# Standard git workflow
git add .
git commit -m "Your message"
git push origin main
```

Focus on code quality and manual verification before commits.

## 🚨 TDD PIPELINE FOR ALL IMPLEMENTATIONS (HIGHEST PRIORITY)

```
╔═══════════════════════════════════════════════════════════════════╗
║  🔴 RED → ✅ GREEN → ♻️ REFACTOR                                   ║
║                                                                   ║
║  ZERO TOLERANCE: No code without tests. No exceptions.           ║
║  See: .claude/rules/tdd.enforcement.md                           ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Mandatory Test-Driven Development Cycle

**CRITICAL**: Every implementation MUST follow TDD cycle. This rule has **HIGHEST PRIORITY**.

#### 1. 🔴 RED Phase: Write FAILING Test First

- Write test that describes desired behavior
- Test **MUST FAIL** initially (run `@test-runner` to confirm)
- Test must be meaningful (no trivial assertions)
- **NEVER proceed to code without failing test**

```bash
# Example workflow:
touch tests/test_feature.py
# Write test
@test-runner run tests/test_feature.py  # MUST SEE RED ❌
git commit -m "test: add failing test for feature"
```

#### 2. ✅ GREEN Phase: Write MINIMUM Code to Pass

- Write **MINIMUM** code to pass test
- Don't add features not required by test
- Focus on making test green, not perfection
- Run `@test-runner` to confirm tests pass

```bash
# Implement feature
@test-runner run tests/test_feature.py  # MUST SEE GREEN ✅
git commit -m "feat: implement feature"
```

#### 3. ♻️ REFACTOR Phase: Improve While Tests Stay Green

- Improve code structure
- Remove duplication
- Enhance readability
- **All tests MUST remain green**
- Run `@test-runner` after each change

```bash
# Refactor code
@test-runner run all tests  # ALL MUST BE GREEN ✅
git commit -m "refactor: improve feature structure"
```

### TDD Commit Pattern (MANDATORY)

For EVERY feature, you MUST see this commit sequence:
```bash
git log --oneline
# c3d4e5f refactor: improve feature structure  ♻️
# b2c3d4e feat: implement feature              ✅
# a1b2c3d test: add failing test for feature  🔴
```

**❌ VIOLATIONS (Auto-Reject):**
- Commits with code but no tests
- Commits with "WIP" or "TODO: add tests later"
- Skipping any phase of TDD cycle
- Tests written after implementation

## CONTEXT OPTIMIZATION RULES

See **`.claude/rules/context-optimization.md`** for detailed context preservation patterns and agent usage requirements.

## ERROR HANDLING PIPELINE

See **`.claude/rules/development-workflow.md`** for complete error handling and development pipelines.

## WHY THESE RULES EXIST

### Development Quality

- **No partial implementations** → Technical debt compounds exponentially
- **No mock services in tests** → Real bugs hide behind mocks
- **TDD mandatory** → Prevents regression and ensures coverage

### Context Preservation

- **Agent-first search** → Preserves main thread for decisions
- **No verbose outputs** → Maintains conversation clarity
- **10-20% return rule** → Focuses on actionable insights

### Code Integrity

- **No "_fixed" suffixes** → Indicates poor planning
- **No orphan docs** → Documentation should be intentional
- **No mixed concerns** → Maintainability over convenience

## Philosophy

### Error Handling

- **Fail fast** for critical configuration (missing text model)
- **Log and continue** for optional features (extraction model)
- **Graceful degradation** when external services unavailable
- **User-friendly messages** through resilience layer

### Testing

See **`.claude/rules/test-execution.md`** for testing standards and requirements.

## Tone and Behavior

- Criticism is welcome. Please tell me when I am wrong or mistaken, or even when you think I might be wrong or mistaken.
- Please tell me if there is a better approach than the one I am taking.
- Please tell me if there is a relevant standard or convention that I appear to be unaware of.
- Be skeptical.
- Be concise.
- Short summaries are OK, but don't give an extended breakdown unless we are working through the details of a plan.
- Do not flatter, and do not give compliments unless I am specifically asking for your judgement.
- Occasional pleasantries are fine.
- Feel free to ask many questions. If you are in doubt of my intent, don't guess. Ask.

## ABSOLUTE RULES

See **`.claude/rules/naming-conventions.md`** for code quality standards and prohibited patterns.

Key principles:

- NO PARTIAL IMPLEMENTATION
- NO CODE DUPLICATION (always search first)
- IMPLEMENT TEST FOR EVERY FUNCTION (see `.claude/rules/tdd.enforcement.md`)
- NO CHEATER TESTS (tests must be meaningful)
- Follow all rules defined in `.claude/rules/` without exception

## 📋 Quick Reference Checklists

### Before Committing

```bash
# Minimum Definition of Done
✓ Tests written and passing (TDD - see .claude/rules/tdd.enforcement.md)
✓ Code formatted (black, prettier, eslint)
✓ No partial implementations
✓ No code duplication
✓ Error handling implemented
✓ Security considered

# Run project-appropriate checks (automated with git hooks)
# Test: npm test | pytest | go test | cargo test | mvn test
# Lint: npm run lint | ruff check | golint | cargo clippy | rubocop
# Build: npm run build | python setup.py build | go build | cargo build
# Type check: npm run typecheck | mypy | go vet

# Or use safe-commit script for all checks
./scripts/safe-commit.sh "feat: your message"

# Simulate CI locally before push (if available)
# Check package.json, Makefile, or project docs for CI simulation commands
```

### Before Creating PR

```bash
✓ Branch up to date with main
✓ All tests passing
✓ CI/CD pipeline green
✓ Documentation updated
✓ Breaking changes noted
```

### Code Quality Checklist

```bash
✓ Functions are single-purpose
✓ Variable names are descriptive
✓ No hardcoded values
✓ No debugging code left
✓ Comments explain "why" not "what"
```

For detailed checklists, see `.claude/checklists/`

# Traditional Development Workflow

## ⚙️ TRADITIONAL DEVELOPMENT WORKFLOW

This project uses a traditional development approach focused on native tooling and direct local execution.

### 🏠 Development Environment

- **Local execution** - Run code directly on your machine
- **Native tooling** - Use language-specific tools (npm, pip, etc.)
- **System dependencies** - Install requirements locally
- **Traditional testing** - Standard test runners and frameworks

### 🔧 Getting Started

1. **Check project type and install dependencies**

   ```bash
   # Detect project type from files present
   # package.json → Node.js/React/Vue/Next.js
   # requirements.txt/Pipfile → Python/Django/Flask
   # go.mod → Go
   # Cargo.toml → Rust
   # pom.xml → Java/Maven
   # build.gradle → Java/Gradle
   # composer.json → PHP
   # Gemfile → Ruby
   ```

2. **Install dependencies based on project type**

   ```bash
   # Project-specific installation commands will be used
   # The framework will detect and use the appropriate commands
   ```

3. **Run development and tests**

   ```bash
   # Commands will be determined from:
   # - package.json scripts (Node.js)
   # - Makefile targets (if present)
   # - Standard conventions for the detected language
   # - README.md instructions
   ```

### 📋 Development Rules

- Use native language tools and package managers
- Install dependencies on local system
- Run tests using standard frameworks
- Deploy using traditional methods (not containerized)
