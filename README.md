# chittyfoundation/.github

Organization-wide GitHub configurations, reusable workflows, and CI/CD templates.

## Reusable Workflows

Any repository can call our centralized CI pipeline:

```yaml
name: CI
on: [push, pull_request]
jobs:
  ci:
    uses: chittyfoundation/.github/.github/workflows/reusable-ci-pipeline.yml@main
    with:
      run-ai-review: true
      run-governance: true
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Workflow Templates

Available in Actions > New workflow:
- **AI Code Review** - Claude-powered PR review
- - **Governance Checks** - chittycanon compliance
 
  - ## Governance
 
  - Reference: `chittycanon://gov/governance`
