# Automatic Changelog Generation with Ollama

**Version 1.1** - Multi-platform CI support (GitHub, Bitbucket, GitLab)

Automatically generate changelog entries when PRs are merged using a local LLM (Ollama).

## Quick Start

### Option A: GitHub Actions (Cloud Runners)

1. Copy these files to your project:
   - `generate_changelog.py`
   - `.github/workflows/changelog.yml`

2. Push to GitHub - done! Changelogs generate automatically on PR merge.

### Option B: Bitbucket Pipelines (Self-Hosted Runner)

1. Copy these files to your project:
   - `generate_changelog.py`
   - `bitbucket-pipelines.yml`

2. Set up a self-hosted runner with Ollama pre-installed
3. Push to Bitbucket - done!

### Option C: Local Development

```bash
# 1. Copy script to your project
cp generate_changelog.py /path/to/your/project/

# 2. Install (auto-sets up hook + Ollama + model)
python generate_changelog.py --install

# 3. Done! Merge branches and changelogs appear automatically
```

## Supported CI Platforms

| Platform | Configuration File | Runner Type |
|----------|-------------------|-------------|
| GitHub Actions | `.github/workflows/changelog.yml` | Cloud (auto-install Ollama) |
| Bitbucket Pipelines | `bitbucket-pipelines.yml` | Self-hosted (requires Ollama) |
| GitLab CI | Coming soon | Self-hosted |
| Local | Git hook | Your machine |

The script auto-detects the platform via environment variables:
- `GITHUB_ACTIONS` - GitHub Actions
- `BITBUCKET_BUILD_NUMBER` - Bitbucket Pipelines
- `GITLAB_CI` - GitLab CI
- `JENKINS_URL` - Jenkins
- `CIRCLECI` - CircleCI

## Features

- Uses only Python standard library
- Multi-platform CI support with auto-detection
- Conventional Commits format with timestamps
- Author and file count metadata in entries
- Duplicate detection and cleanup
- Local git hooks for development
- Windows, Mac, Linux support
- Auto-truncates large diffs

## How It Works

### CI Platforms (PR Merge)
1. Developer merges a PR
2. CI workflow triggers
3. Ollama generates changelog entry from PR diff
4. Commits and pushes updated `CHANGELOG.md`

### Local (Git Hook)
1. Developer runs `git merge feature-branch`
2. Post-merge hook triggers
3. Ollama generates changelog entry
4. Updates `CHANGELOG.md` automatically

## Entry Format

Entries include timestamp, file count, and author:

```markdown
## Unreleased

- Dec 31, 2025 at 2:30 PM | 3 files | by John - feat: add user authentication
- Dec 30, 2025 at 10:00 AM | 1 file | by Jane - fix: resolve memory leak
```

## Commands

```bash
python generate_changelog.py --install    # Install hook + Ollama + model
python generate_changelog.py --uninstall  # Remove the hook
python generate_changelog.py --setup      # Just check/install Ollama
python generate_changelog.py --cleanup    # Remove duplicates, validate format
python generate_changelog.py --auto       # Generate without prompts
python generate_changelog.py --ci         # CI mode (auto-detect platform)
python generate_changelog.py --github     # Force GitHub mode
python generate_changelog.py --bitbucket  # Force Bitbucket mode
python generate_changelog.py --gitlab     # Force GitLab mode
python generate_changelog.py --help       # Show all options
```

## Configuration

Edit `generate_changelog.py` to customize:

```python
MODEL = "phi3:mini"         # Change model (phi3:mini is fast for CI)
MAX_DIFF_CHARS = 2000       # Adjust diff size limit
SYSTEM_PROMPT = "..."       # Customize AI instructions
```

## Files

| File | Purpose |
|------|---------|
| `generate_changelog.py` | Main script (required) |
| `.github/workflows/changelog.yml` | GitHub Actions workflow |
| `bitbucket-pipelines.yml` | Bitbucket Pipelines workflow |
| `CHANGELOG.md` | Generated changelog (auto-created) |
| `.git/hooks/post-merge` | Created by --install (local only) |

## Self-Hosted Runner Setup (Bitbucket)

1. Install Ollama on your runner:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull the model:
   ```bash
   ollama pull phi3:mini
   ```

3. Start Ollama service:
   ```bash
   ollama serve  # Or set up as system service
   ```

4. Add runner labels in Bitbucket:
   - `self.hosted`
   - `linux`
   - `ollama`

## Version History

**v1.1** (Current) - Multi-platform CI:
- Auto-detect CI platform (GitHub, Bitbucket, GitLab, etc.)
- Bitbucket Pipelines support with self-hosted runners
- `--github`, `--bitbucket`, `--gitlab` CLI flags
- Entry metadata: timestamp, file count, author
- Duplicate detection and cleanup
- Performance optimizations

**v1.0-github** - GitHub Actions integration:
- GitHub Actions workflow with Ollama caching
- `--ci` flag for CI environment detection
- Automatic PR merge changelog generation

**v1.0-local** - Single-file local solution:
- Single Python file deployment
- Auto-installs Ollama and Mistral model
- Zero external dependencies

## Troubleshooting

**Ollama not running (local)?**
```bash
ollama serve
```

**Model not available?**
```bash
ollama pull phi3:mini
```

**Hook not running on Unix/Mac?**
```bash
chmod +x .git/hooks/post-merge
```

**GitHub Actions failing?**
- Check workflow logs in Actions tab
- Ensure repository has write permissions for workflows
- First run takes longer (model download)

**Bitbucket Pipeline failing?**
- Ensure self-hosted runner has Ollama installed
- Check runner has `ollama` label
- Verify Ollama service is running

## License

MIT - Free to use. Copy to any project!
