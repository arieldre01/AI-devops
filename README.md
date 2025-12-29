# Automatic Changelog Generation with Ollama

Automatically generate changelog entries when you merge branches using a local LLM (Ollama).

## Quick Start

```bash
# 1. Copy script to your project
cp generate_changelog.py /path/to/your/project/

# 2. Install (auto-sets up hook + Ollama + model)
python generate_changelog.py --install

# 3. Done! Merge branches and changelogs appear automatically
```

That's it! Just **1 file** and **1 command**.

## Features

- Uses only Python standard library
- Simple deployment to any project
- Windows, Mac, Linux
- Auto-truncates large diffs
- Verifies Ollama and model availability
- Run on-demand or via git hooks

## How It Works

When you merge a branch into `main`, the git hook automatically:
1. Detects the merge and gets the diff
2. Checks if Ollama is running and model is available
3. Sends the diff to Ollama/Mistral for analysis
4. Generates a concise changelog entry
5. Updates `CHANGELOG.md` under "## Unreleased"

## Manual Usage

Run manually to generate changelog from uncommitted changes:

```bash
python generate_changelog.py
```

With auto-confirm:

```bash
python generate_changelog.py --auto
```

## Deployment to Other Projects

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

**TL;DR:** Just copy 2 files - no pip install needed!

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

### Auto-Installed
- **Ollama** - Downloaded and installed automatically
- **Mistral model** - Downloaded automatically (~4GB)
- **Git hook** - Created automatically by `--install`

### Per Project
- `generate_changelog.py` - Just this one file!

No pip install needed. No manual hook setup. The script handles everything.

## Troubleshooting

**Ollama not running?**
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

## Commands

```bash
python generate_changelog.py --install    # Install hook + Ollama + model
python generate_changelog.py --uninstall  # Remove the hook
python generate_changelog.py --setup      # Just check/install Ollama
python generate_changelog.py --auto       # Generate without prompts
python generate_changelog.py --help       # Show all options
```

## Files

- `generate_changelog.py` - The only file you need!
- `CHANGELOG.md` - Generated changelog (auto-created)
- `.git/hooks/post-merge` - Created by --install (don't copy manually)

## What Changed?

**Version 2.0** - Simplified to 2 files:
- Replaced `requests` with `urllib` (stdlib only)
- Added pre-flight checks (Ollama health, model verification)
- Added smart diff truncation (prevents context overflow)
- Consolidated 4 hook files into 1 universal hook
- Zero external dependencies

**Version 1.0** - Original:
- Required `requests` package
- 4 separate hook files (Windows/Unix/wrapper)
- Complex path resolution logic

## License

Free to use. Copy these 2 files to any project!
