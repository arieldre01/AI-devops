# Quick Deployment Guide

Deploy automatic changelog generation to **any project** with just **1 file** and **1 command**!

## Prerequisites

You only need:

1. **Python 3.7+** - https://python.org/downloads
2. **Git** - https://git-scm.com/downloads

Everything else is auto-installed:
- Ollama (Windows/Mac/Linux)
- Mistral model (~4GB)
- Git hook

## Deployment (2 Steps)

### Step 1: Copy Script

Copy `generate_changelog.py` to your project root:

```bash
cp generate_changelog.py /path/to/your/project/
```

### Step 2: Install

```bash
cd /path/to/your/project
python generate_changelog.py --install
```

This will:
- Create the git hook automatically
- Install Ollama if missing
- Download the Mistral model if needed
- Start the Ollama service

**That's it!**


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

### Essential (1 file!)
- `generate_changelog.py` - The only file you need

### Auto-Created
- `.git/hooks/post-merge` - Created by `--install`
- `CHANGELOG.md` - Created on first merge

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

```bash
# Remove the hook
python generate_changelog.py --uninstall

# Optionally remove the script
rm generate_changelog.py
```

