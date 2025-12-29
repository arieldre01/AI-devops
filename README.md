# Automatic Changelog Generation with Ollama

Automatically generate changelog entries when you merge branches using a local LLM (Ollama).

> **Note:** Requires Ollama installed with a model (e.g., Mistral). See Prerequisites below.


## Quick Start

1. **Copy 2 files to your project**:
   - `generate_changelog.py` → project root
   - `.git/hooks/post-merge` → `.git/hooks/` directory
2. **Make hook executable** (Unix/Mac): `chmod +x .git/hooks/post-merge`
3. **Run setup** (auto-installs Ollama + Mistral if needed):
   ```bash
   python generate_changelog.py --setup
   ```
4. **Merge a branch** - changelog is generated automatically!

> **Note:** The script auto-installs Ollama and downloads the Mistral model if not present!

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

### Auto-Installed (if missing)
- **Ollama** - Downloaded and installed automatically
- **Mistral model** - Downloaded automatically (~4GB)

### Per Project (just 2 files!)
- `generate_changelog.py` - copy to project root
- `.git/hooks/post-merge` - copy to `.git/hooks/`

No pip install needed - the script uses only Python standard library.

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

## Files

- `generate_changelog.py` - Main script (zero dependencies!)
- `.git/hooks/post-merge` - Git hook (30 lines)
- `CHANGELOG.md` - Generated changelog (auto-created)
- `DEPLOY.md` - Deployment guide
- `SETUP.md` - Original detailed setup guide
- `FILES_NEEDED.md` - File reference (legacy)

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
