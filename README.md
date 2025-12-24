# Automatic Changelog Generation with Ollama

This project automatically generates changelog entries when you merge branches using a local LLM (Ollama).

## Quick Start

1. **Install Ollama**: https://ollama.com/download
2. **Pull Mistral model**: `ollama pull mistral`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Merge a branch** - changelog is generated automatically!

## How It Works

When you merge a branch into `main`, the git hook automatically:
- Detects the merge
- Analyzes the changes using Ollama/Mistral
- Generates a changelog entry
- Updates `CHANGELOG.md`

## Full Setup Guide

See [SETUP.md](SETUP.md) for complete setup instructions for new computers.

## Files

- `generate_changelog.py` - Main changelog generator
- `ollama_setup.py` - Test Ollama connection
- `simple_chat.py` - Simple chat interface
- `.git/hooks/post-merge.py` - Git hook wrapper
- `CHANGELOG.md` - Generated changelog (auto-updated)

## Manual Usage

Run manually to generate changelog from uncommitted changes:
```bash
python generate_changelog.py
```

