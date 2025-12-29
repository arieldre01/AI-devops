# Quick Deployment Guide

Deploy automatic changelog generation to **any project** with just 2 files!

## Prerequisites

You only need these installed manually:

1. **Python 3.7+** - https://python.org/downloads
2. **Git** - https://git-scm.com/downloads

**Ollama and Mistral are auto-installed!** The script handles:
- Downloading and installing Ollama (Windows/Mac/Linux)
- Downloading the Mistral model (~4GB)
- Starting the Ollama service

## Deployment Steps

## Deployment Steps

### Step 1: Copy Main Script

Copy `generate_changelog.py` to your project root:

```bash
cp generate_changelog.py /path/to/your/project/
```

### Step 2: Copy Git Hook

Copy the hook to your project's `.git/hooks/` directory:

```bash
cp .git/hooks/post-merge /path/to/your/project/.git/hooks/
```

### Step 3: Make Hook Executable (Unix/Mac only)

```bash
chmod +x /path/to/your/project/.git/hooks/post-merge
```

On Windows, this step is automatic.

### Step 4: Run Setup (Auto-Installs Everything)

```bash
python generate_changelog.py --setup
```

This will:
- Check if Ollama is installed (installs if missing)
- Start Ollama service (if not running)
- Download Mistral model (if not present, ~4GB)


## How to Use

### Automatic (after merges)

Just merge a branch - the changelog updates automatically:

```bash
git checkout main
git merge feature-branch
# Changelog entry generated automatically!
```

### Manual (for uncommitted changes)

Run the script manually:

```bash
python generate_changelog.py
```

It will:
1. Check if Ollama is running
2. Verify the model is available
3. Get your git diff
4. Generate a changelog entry
5. Ask for confirmation (unless using `--auto`)

## Files Needed

### Essential (2 files)
- `generate_changelog.py` - Main script (zero dependencies!)
- `.git/hooks/post-merge` - Git hook

### Optional
- `CHANGELOG.md` - Auto-created on first run

## Configuration

Edit `generate_changelog.py` to customize:

```python
MODEL = "mistral"  # Change to "llama3:8b" or any model
MAX_DIFF_CHARS = 8000  # Adjust diff size limit
SYSTEM_PROMPT = "..."  # Customize AI instructions
```

## Troubleshooting

### "Ollama is not running"
Start Ollama:
```bash
ollama serve
```

### "Model 'mistral' is not available"
Download the model:
```bash
ollama pull mistral
```

### Hook not running on Windows
Git on Windows uses Python automatically for `.py` files in hooks directory. Make sure Python is in your PATH.

### Hook not running on Unix/Mac
Make the hook executable:
```bash
chmod +x .git/hooks/post-merge
```

## Features

- **Zero external dependencies** - Uses only Python stdlib  
- **Cross-platform** - Works on Windows, Mac, Linux  
- **Smart truncation** - Handles large diffs automatically  
- **Pre-flight checks** - Verifies Ollama and model before running  
- **Manual or automatic** - Run on-demand or via git hooks  
- **Clear error messages** - Easy to debug  

## What Gets Generated

Changelog entries look like this:

```
[Feature] Added user authentication with JWT tokens
[Fix] Resolved memory leak in database connection pool
[Refactor] Simplified error handling in API routes
```

Entries are added under "## Unreleased" in `CHANGELOG.md`.

## Advanced: Use Different Model

1. Pull a different model:
```bash
ollama pull llama3:8b
```

2. Edit `generate_changelog.py`:
```python
MODEL = "llama3:8b"
```

3. Done!

## Uninstall

Remove the 2 files:
```bash
rm generate_changelog.py
rm .git/hooks/post-merge
```

