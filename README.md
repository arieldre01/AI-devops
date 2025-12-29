# Automatic Changelog Generation with Ollama

**Version 1.0-github** - GitHub Actions integration with cached Ollama

Automatically generate changelog entries when PRs are merged using a local LLM (Ollama).

## Quick Start

### Option A: GitHub Actions (Recommended for Teams)

1. Copy these files to your project:
   - `generate_changelog.py`
   - `.github/workflows/changelog.yml`

2. Push to GitHub - done! Changelogs generate automatically on PR merge.

### Option B: Local Development

```bash
# 1. Copy script to your project
cp generate_changelog.py /path/to/your/project/

# 2. Install (auto-sets up hook + Ollama + model)
python generate_changelog.py --install

# 3. Done! Merge branches and changelogs appear automatically
```

## Features

- Uses only Python standard library
- GitHub Actions with cached Ollama model
- Local git hooks for development
- Windows, Mac, Linux
- Auto-truncates large diffs
- Verifies Ollama and model availability

## How It Works

### GitHub Actions (PR Merge)
1. Developer merges a PR to `main`
2. GitHub Actions workflow triggers
3. Restores cached Ollama model (~4GB, first run downloads it)
4. Generates changelog entry from PR diff
5. Commits and pushes updated `CHANGELOG.md`

### Local (Git Hook)
1. Developer runs `git merge feature-branch`
2. Post-merge hook triggers
3. Ollama generates changelog entry
4. Updates `CHANGELOG.md` automatically

## GitHub Actions Setup

The workflow file `.github/workflows/changelog.yml` handles everything:

```yaml
# Triggers on PR merge to main
on:
  pull_request:
    types: [closed]
    branches: [main]
```

**Cache Details:**
- Cache key: `ollama-mistral-v1`
- Size: ~4GB (Mistral model)
- Lifetime: 7 days of inactivity
- Shared across all branches and contributors

First PR merge: ~5-10 minutes (downloads model)
Subsequent merges: ~1-2 minutes (uses cache)

## Manual Usage

Run manually to generate changelog from uncommitted changes:

```bash
python generate_changelog.py
```

With auto-confirm:

```bash
python generate_changelog.py --auto
```

In CI environment:

```bash
python generate_changelog.py --ci
```

## Configuration

Edit `generate_changelog.py` to customize:

```python
MODEL = "mistral"           # Change model
MAX_DIFF_CHARS = 8000       # Adjust diff size limit
SYSTEM_PROMPT = "..."       # Customize AI instructions
```

## Example Output

```markdown
## Unreleased

[Feature] Added user authentication with JWT tokens

[Fix] Resolved memory leak in database connection pool

[Refactor] Simplified error handling in API routes
```

## Requirements

### Prerequisites
- **Python 3.7+** - https://python.org/downloads
- **Git** - https://git-scm.com/downloads

### For GitHub Actions
- Just the workflow file and script - Ollama installs automatically

### For Local Development
- **Ollama** - Downloaded and installed automatically
- **Mistral model** - Downloaded automatically (~4GB)
- **Git hook** - Created automatically by `--install`

## Commands

```bash
python generate_changelog.py --install    # Install hook + Ollama + model
python generate_changelog.py --uninstall  # Remove the hook
python generate_changelog.py --setup      # Just check/install Ollama
python generate_changelog.py --auto       # Generate without prompts
python generate_changelog.py --ci         # CI mode (GitHub Actions)
python generate_changelog.py --help       # Show all options
```

## Files

- `generate_changelog.py` - Main script
- `.github/workflows/changelog.yml` - GitHub Actions workflow
- `CHANGELOG.md` - Generated changelog (auto-created)
- `.git/hooks/post-merge` - Created by --install (local only)

## Version History

**v1.0-github** (Current) - GitHub Actions integration:
- GitHub Actions workflow with Ollama caching
- `--ci` flag for CI environment detection
- Automatic PR merge changelog generation
- Shared cache across all contributors

**v1.0-local** - Single-file local solution:
- Single Python file deployment
- Auto-installs Ollama and Mistral model
- Zero external dependencies (Python stdlib only)
- Cross-platform (Windows, Mac, Linux)
- Git hook auto-configuration

## Troubleshooting

**Ollama not running (local)?**
```bash
ollama serve
```

**Model not available?**
```bash
ollama pull mistral
```

**Hook not running on Unix/Mac?**
```bash
chmod +x .git/hooks/post-merge
```

**GitHub Actions failing?**
- Check workflow logs in Actions tab
- Ensure repository has write permissions for workflows
- First run takes longer (model download)

## License

MIT - Free to use. Copy to any project!
