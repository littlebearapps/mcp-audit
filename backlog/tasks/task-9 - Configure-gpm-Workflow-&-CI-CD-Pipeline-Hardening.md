---
id: task-9
title: Configure gpm Workflow & CI/CD Pipeline Hardening
status: In Progress
assignee: []
created_date: '2025-11-25 05:53'
updated_date: '2025-11-25 05:55'
labels:
  - ci-cd
  - gpm
  - github-actions
  - workflow
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure gpm (git-pr-manager) for proper PR workflow and harden CI/CD pipeline to ensure:
- All changes go through PR with CI checks
- PyPI publishes ONLY after successful PR merge
- Auto-delete feature branches on merge
- CLAUDE.md documents gpm workflow

**Current Issues:**
1. Branch protection disabled in .gpm.yml
2. GitHub repo deleteBranchOnMerge is false
3. PyPI publish triggers on release (bypasses CI check requirement)
4. CLAUDE.md missing gpm workflow documentation

**References:**
- gpm docs: `gpm docs --guide=GITHUB-ACTIONS-INTEGRATION`
- gpm config: `gpm docs --guide=CONFIGURATION`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 gpm init --interactive completed or .gpm.yml manually updated
- [ ] #2 Branch protection enabled requiring quality-gate check
- [ ] #3 GitHub repo setting: deleteBranchOnMerge = true
- [ ] #4 Publish workflow requires CI to pass (not just release trigger)
- [ ] #5 CLAUDE.md updated with gpm workflow section (succinct)
- [ ] #6 Feature branch workflow tested: gpm feature → gpm ship
- [ ] #7 All lint/format errors fixed before merge
- [ ] #8 PyPI publish only occurs after PR merged to main with passing CI
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Phase 1: Fix Current Lint Errors
1. Commit pending ruff fixes (display module)
2. Run full CI locally to verify: `gpm verify`

### Phase 2: Configure GitHub Repo Settings
1. Enable auto-delete branches on merge:
   ```bash
   gh repo edit littlebearapps/mcp-audit --delete-branch-on-merge
   ```

### Phase 3: Update .gpm.yml
1. Enable branch protection:
   ```yaml
   branchProtection:
     enabled: true
     requireReviews: 0  # Solo dev, no reviews needed
     requireStatusChecks:
       - quality-gate
     enforceAdmins: false
   ```

### Phase 4: Modify Publish Workflow
1. Change trigger from `release` to `push to main` with version tag detection
2. Add CI check requirement before publish
3. Alternative: Keep release trigger but require release only from main after CI passes

**Option A - Push-based (recommended):**
```yaml
on:
  push:
    branches: [main]
    tags: ['v*']  # Only publish on version tags
```

**Option B - Release-based (current, needs guard):**
- Add workflow_run dependency on CI
- Or add CI job check in publish workflow

### Phase 5: Update CLAUDE.md
Add gpm workflow section:
```markdown
## Git Workflow (gpm)

Use gpm for all changes:
\`\`\`bash
gpm feature my-feature   # Create feature branch
# ... make changes ...
gpm ship                 # Create PR, wait CI, merge
\`\`\`

**Never push directly to main.** All changes require PR with passing CI.
```

### Phase 6: Test Workflow
1. Create test feature branch: `gpm feature test-workflow`
2. Make trivial change
3. Run `gpm ship` to verify full workflow
4. Verify branch auto-deleted after merge
<!-- SECTION:PLAN:END -->
