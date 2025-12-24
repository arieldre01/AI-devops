# Files Needed for Automatic Changelog Generation

## Essential Files (Required)

### Core Scripts
- **`generate_changelog.py`** - Main script that generates changelog entries from git diffs using Ollama
- **`requirements.txt`** - Python dependencies (ollama, requests)

### Git Hooks (Required for automatic generation)
- **`.git/hooks/post-merge.py`** - Python wrapper that finds repo root and calls generate_changelog.py
- **`.git/hooks/post-merge.bat`** - Windows hook entry point
- **`.git/hooks/post-merge`** - Unix/Mac hook entry point

### Documentation
- **`SETUP.md`** - Complete setup guide for new computers
- **`README.md`** - Project overview and quick start

## Optional Files (Helpful but not required)

- **`ollama_setup.py`** - Test script to verify Ollama connection
- **`simple_chat.py`** - Simple chat interface for testing Ollama
- **`.gitignore`** - Git ignore patterns

## Generated Files (Created automatically)

- **`CHANGELOG.md`** - Auto-generated changelog file (created on first merge)

## What Gets Deleted

All test files (ending in `_test.py`, `test_*.py`, etc.) are not needed and can be removed.

## File Structure

```
project-root/
├── generate_changelog.py      # Main script
├── requirements.txt            # Dependencies
├── SETUP.md                   # Setup guide
├── README.md                  # Project docs
├── ollama_setup.py            # Optional: test Ollama
├── simple_chat.py             # Optional: chat interface
├── .gitignore                 # Optional: git config
├── CHANGELOG.md               # Auto-generated
└── .git/
    └── hooks/
        ├── post-merge.py      # Hook wrapper
        ├── post-merge.bat     # Windows hook
        └── post-merge         # Unix/Mac hook
```

