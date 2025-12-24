# Automatic Changelog Generation Setup Guide

This guide explains how to set up automatic changelog generation using Ollama on a new computer.

## Overview

This system automatically generates changelog entries when you merge branches into `main`. It uses:
- **Git hooks** to detect merges
- **Ollama** (local LLM) to generate changelog entries
- **Mistral model** for efficient text generation

## Prerequisites

1. **Python 3.7+** installed
2. **Git** installed
3. **Ollama** installed and running
4. **Mistral model** pulled in Ollama

## Step-by-Step Setup

### Step 1: Install Ollama

1. Download Ollama from: https://ollama.com/download
2. Install it on your system
3. Verify installation:
   ```bash
   ollama --version
   ```

### Step 2: Pull the Mistral Model

Run this command to download the Mistral model:
```bash
ollama pull mistral
```

This may take a few minutes depending on your internet connection.

### Step 3: Verify Ollama is Running

Ollama usually starts automatically. To verify:
```bash
ollama list
```

If it's not running, start it:
```bash
ollama serve
```

### Step 4: Install Python Dependencies

Navigate to the project directory and install required packages:
```bash
pip install -r requirements.txt
```

This installs:
- `ollama` - Python client for Ollama
- `requests` - For API calls

### Step 5: Set Up Git Hooks

The git hooks are already in place in `.git/hooks/`. They will automatically work when you:
1. Clone this repository, OR
2. Copy the `.git/hooks/` directory to your repository

**Important**: The hooks must be in `.git/hooks/` directory of your repository.

#### For Windows:
- `.git/hooks/post-merge.bat` will be used

#### For Unix/Mac:
- `.git/hooks/post-merge` will be used

Both hooks call the Python wrapper (`.git/hooks/post-merge.py`) which handles path resolution.

### Step 6: Test the Setup

1. Create a test branch:
   ```bash
   git checkout -b test-changelog
   ```

2. Make a small change (add a file or modify existing code):
   ```bash
   echo "# Test" > test_file.py
   git add test_file.py
   git commit -m "Test changelog generation"
   ```

3. Merge back to main:
   ```bash
   git checkout main
   git merge test-changelog
   ```

4. Check `CHANGELOG.md` - it should have a new entry automatically generated!

## How It Works

1. **When you merge a branch** into `main`, Git triggers the `post-merge` hook
2. **The hook** calls `post-merge.py` which finds the repository root
3. **The script** gets the diff between `ORIG_HEAD` and `HEAD` (what was merged)
4. **Ollama/Mistral** analyzes the diff and generates a concise changelog entry
5. **The entry** is automatically prepended to `CHANGELOG.md` under "## Unreleased"

## File Structure

### Essential Files:
- `generate_changelog.py` - Main script that generates changelog entries
- `requirements.txt` - Python dependencies
- `.git/hooks/post-merge.py` - Python wrapper for path resolution
- `.git/hooks/post-merge.bat` - Windows hook entry point
- `.git/hooks/post-merge` - Unix/Mac hook entry point

### Optional Files:
- `ollama_setup.py` - Helper script to test Ollama connection
- `simple_chat.py` - Simple chat interface for testing Ollama
- `README.md` - Project documentation
- `CHANGELOG.md` - Generated changelog (created automatically)

## Troubleshooting

### Hook Not Running?
- Verify hooks are executable (Unix/Mac): `chmod +x .git/hooks/post-merge`
- Check that hooks are in `.git/hooks/` directory
- Try running the hook manually: `python .git/hooks/post-merge.py`

### Ollama Connection Error?
- Make sure Ollama is running: `ollama serve`
- Verify Mistral is installed: `ollama list`
- Test connection: `python ollama_setup.py`

### No Changes Detected?
- The hook only runs on merges, not regular commits
- Make sure you're merging into `main` branch
- Check that there are actual changes in the merge

### Path Errors?
- The Python wrapper handles path resolution automatically
- If you get path errors, make sure you're in a git repository
- Verify `.git/hooks/post-merge.py` exists

## Customization

### Change the Model

Edit `generate_changelog.py` and change the `MODEL` variable:
```python
MODEL = "mistral"  # Change to "llama3:8b" or any other model
```

Then pull the new model:
```bash
ollama pull llama3:8b
```

### Change the System Prompt

Edit the `SYSTEM_PROMPT` in `generate_changelog.py` to customize how changelog entries are formatted.

### Manual Changelog Generation

You can also run the script manually:
```bash
python generate_changelog.py
```

This will:
- Check for uncommitted changes
- Generate a changelog entry
- Ask for confirmation before writing

## Notes

- The hook only runs on **merges**, not on regular commits
- Changelog entries are added to the **top** of `CHANGELOG.md` under "## Unreleased"
- The system requires **Ollama to be running** when you merge
- All processing happens **locally** - no data is sent to external services

## Support

If you encounter issues:
1. Check that Ollama is running and Mistral is installed
2. Verify Python dependencies are installed
3. Test the hook manually: `python .git/hooks/post-merge.py`
4. Check the error messages for specific issues

