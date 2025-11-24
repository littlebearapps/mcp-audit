# GPM + CI/CD Integration Plan

**Date**: 2025-11-24
**Purpose**: Integrate git-pr-manager (gpm) with MCP Audit CI/CD workflow

---

## Current gpm Configuration Analysis

### Existing `.gpm.yml` Configuration

```yaml
branchProtection:
  enabled: false              # ✅ CORRECT - Solo developer
  requireReviews: 0           # ✅ CORRECT - No review bottleneck
  requireStatusChecks: []     # ⚠️  SHOULD ADD: quality-gate
  enforceAdmins: false

ci:
  waitForChecks: true         # ✅ CORRECT
  failFast: true              # ✅ CORRECT
  retryFlaky: false           # ✅ CORRECT
  timeout: 30                 # ✅ CORRECT

security:
  scanSecrets: true           # ✅ CORRECT
  scanDependencies: true      # ✅ CORRECT
  allowedVulnerabilities: []

pr:
  templatePath: null          # ⚠️  SHOULD SET: .github/PULL_REQUEST_TEMPLATE.md
  autoAssign: []
  autoLabel: []

autoFix:
  enabled: true               # ✅ CORRECT
  maxAttempts: 2
  maxChangedLines: 1000
  requireTests: true
  enableDryRun: false
  autoMerge: false
  createPR: true

hooks:
  prePush:
    enabled: true             # ✅ CORRECT
    reminder: true            # ✅ Already reminds about gpm ship/auto
  postCommit:
    enabled: false
    reminder: true

verification:
  detectionEnabled: true      # ✅ CORRECT
  preferMakefile: true
```

**Status**: Well-configured for solo developer. Minor updates recommended.

---

## Recommended Updates to `.gpm.yml`

### Update 1: Add Required Status Checks

```yaml
branchProtection:
  requireStatusChecks:
    - quality-gate  # Main CI workflow (pytest + mypy + ruff)
```

**Why**: Ensures CI must pass before merge (even though reviews not required)

### Update 2: Set PR Template Path

```yaml
pr:
  templatePath: .github/PULL_REQUEST_TEMPLATE.md
```

**Why**: Ensures PRs use standardized template

---

## GPM Integration with GitHub Actions

### Pattern: Security Scanning in CI

**File**: `.github/workflows/ci.yml` (add as first job)

```yaml
jobs:
  # JOB 1: gpm security scan (fastest, runs first)
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret scanning

      - name: Setup Node.js for gpm
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install gpm
        run: npm install -g @littlebearapps/git-pr-manager

      - name: Run gpm security scan
        run: gpm security --json > security-report.json
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        continue-on-error: true  # Don't block CI if gpm fails

      - name: Upload security report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: security-report.json

  # JOB 2: Quality gate (pytest, mypy, ruff)
  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: security  # Run after security
    steps:
      # ... pytest, mypy, ruff steps ...
```

**Why this pattern**:
- ✅ Security runs first (fastest feedback)
- ✅ Doesn't block other checks (continue-on-error)
- ✅ Uploads report for review
- ✅ Matches gpm best practices

---

## Complete CI/CD Workflow with gpm

### Recommended Workflow Structure

**File**: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # ============================================================================
  # JOB 1: Security (gpm)
  # ============================================================================
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install gpm
        run: npm install -g @littlebearapps/git-pr-manager

      - name: Security scan
        run: gpm security --json
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        continue-on-error: true

  # ============================================================================
  # JOB 2: Quality Gate (Python testing)
  # ============================================================================
  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: security
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      # Run pytest with coverage
      - name: Run tests
        run: pytest --cov=. --cov-report=term-missing --cov-report=xml

      # Run mypy type checking
      - name: Type check
        run: mypy --config-file=mypy.ini .

      # Run ruff linting
      - name: Lint
        run: ruff check .

      # Run black formatting check
      - name: Format check
        run: black --check .

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: always()
        with:
          file: ./coverage.xml
```

**Key Features**:
- Security scan runs first (fastest feedback)
- Quality gate runs comprehensive checks
- Coverage uploaded to Codecov (optional)
- All checks required for merge

---

## Local Developer Workflow with gpm

### Recommended Commands

```bash
# 1. Start feature branch
gpm feature add-new-platform

# 2. Make changes, commit
git add .
git commit -m "feat: add Gemini CLI support"

# 3. Create PR (gpm handles everything)
gpm auto
# - Creates PR
# - Waits for CI
# - Shows check status
# - Ready to merge when green

# Alternative: Ship workflow (waits for CI + merges)
gpm ship
# - Creates PR
# - Waits for CI
# - Auto-merges when green
```

**Benefits**:
- ✅ Single command PR creation
- ✅ Automatic CI monitoring
- ✅ Security scanning before push
- ✅ Consistent workflow

---

## gpm Commands for AI Agents (Claude Code)

### Recommended gpm Usage Patterns

#### Pattern 1: Create PR with Auto-Wait

```bash
# AI Agent: "I'll create a PR and wait for CI"
gpm auto
```

**What it does**:
- Creates PR
- Waits for CI checks
- Shows status updates
- Does NOT auto-merge (safe for solo dev)

#### Pattern 2: Full Automated Workflow

```bash
# AI Agent: "I'll create PR and merge when ready"
gpm ship
```

**What it does**:
- Creates PR
- Waits for CI checks
- Auto-merges when green
- Only use when changes are verified

#### Pattern 3: Check PR Status

```bash
# AI Agent: "Let me check CI status"
gpm checks 47  # Check PR #47
```

**What it does**:
- Shows all check statuses
- Lists failed/pending checks
- Machine-readable with --json

#### Pattern 4: Security Scan Before Push

```bash
# AI Agent: "Running security scan..."
gpm security
```

**What it does**:
- Scans for secrets (API keys, tokens)
- Checks dependencies for vulnerabilities
- Fails if issues found

---

## Anti-Patterns to Avoid

### ❌ DON'T: Create Workflow to Monitor Workflows

```yaml
# ❌ BAD: Don't do this
name: Check PR Status
on: pull_request
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: gpm checks ${{ github.event.pull_request.number }}
```

**Why bad**: Creates circular dependency, duplicates GitHub's built-in status

### ✅ DO: Use gpm for Security + Local Workflow

```yaml
# ✅ GOOD: Security as validation step
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - run: gpm security  # Adds value
```

---

## Recommended .gpm.yml Updates

### Minimal Changes (Solo Developer)

```yaml
branchProtection:
  enabled: false
  requireReviews: 0
  requireStatusChecks:
    - quality-gate  # ← ADD THIS
  enforceAdmins: false

# ... rest stays same ...

pr:
  templatePath: .github/PULL_REQUEST_TEMPLATE.md  # ← ADD THIS
  autoAssign: []
  autoLabel: []
```

**Changes**:
1. Add `quality-gate` to required checks
2. Set PR template path

---

## Testing the Integration

### Step-by-Step Verification

```bash
# 1. Update .gpm.yml (add quality-gate)
# 2. Commit and push
git add .gpm.yml
git commit -m "chore: configure gpm for CI integration"
git push

# 3. Create test PR with gpm
gpm feature test-gpm-integration
echo "test" > test.txt
git add test.txt
git commit -m "test: verify gpm integration"
gpm auto

# 4. Verify:
# - PR created ✓
# - CI runs (security + quality-gate) ✓
# - gpm waits for checks ✓
# - Status shown correctly ✓

# 5. Clean up test PR
gh pr close --delete-branch
```

---

## Benefits Summary

### For CI/CD

- ✅ **Security scanning** before code review
- ✅ **Standardized workflows** across contributors
- ✅ **Automated PR creation** reduces manual steps
- ✅ **CI status monitoring** built-in

### For AI Agents (Claude Code)

- ✅ **Single command workflows** (`gpm auto`, `gpm ship`)
- ✅ **Machine-readable output** (`--json` flag)
- ✅ **Error handling** with fix suggestions
- ✅ **Context awareness** (knows when CI passes)

### For Solo Developer

- ✅ **No review bottleneck** (requireReviews: 0)
- ✅ **Fast merge workflow** (auto when CI passes)
- ✅ **Security before push** (gpm security hook)
- ✅ **Consistent PR format** (template enforcement)

---

## Implementation Checklist

### Phase 1: Update gpm Configuration

- [ ] Update `.gpm.yml` - Add `quality-gate` to requireStatusChecks
- [ ] Update `.gpm.yml` - Set PR template path
- [ ] Test: `gpm init --show` to verify config

### Phase 2: Create GitHub Actions Workflow

- [ ] Create `.github/workflows/ci.yml`
- [ ] Add security job (gpm security)
- [ ] Add quality-gate job (pytest + mypy + ruff)
- [ ] Test: Push to branch, verify workflow runs

### Phase 3: Create Templates

- [ ] Create `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] Test: Create PR, verify template appears

### Phase 4: Verification

- [ ] Test `gpm auto` creates PR correctly
- [ ] Test CI runs both jobs (security + quality-gate)
- [ ] Test gpm waits for CI completion
- [ ] Test security scan catches secrets (if any)

---

## Estimated Time

- **Phase 1**: 5 minutes (update .gpm.yml)
- **Phase 2**: 30 minutes (create workflow)
- **Phase 3**: 10 minutes (create template)
- **Phase 4**: 15 minutes (testing)

**Total**: ~1 hour

---

## Conclusion

**Recommended approach**:
1. Keep current gpm setup (solo developer optimized)
2. Add minimal updates (quality-gate check, PR template)
3. Add security scan as first CI job
4. Use gpm for local workflow (`gpm auto`)
5. Let GitHub Actions handle CI execution

**Result**: Clean integration without duplication or circular dependencies.
