#!/usr/bin/env python3
"""
Automated CHANGELOG.md generator using Ollama and Git.
Generates changelog entries from uncommitted changes using a local LLM.
"""

import subprocess
import sys
import os
from pathlib import Path
import requests
from typing import Optional

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"  # Change this to use a different model
CHANGELOG_FILE = "CHANGELOG.md"

# System prompt for the LLM
SYSTEM_PROMPT = "You are a Senior Technical Writer. Summarize the following code changes into a single, concise bullet point. Start with a category like [Feature], [Fix], or [Refactor]. Do not output any preamble or conversational text."


def get_git_diff() -> Optional[str]:
    """
    Get the diff of uncommitted changes (staged and unstaged).
    Returns the diff string or None if no changes detected.
    """
    try:
        # Get staged changes
        staged_diff = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=False
        ).stdout
        
        # Get unstaged changes
        unstaged_diff = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            check=False
        ).stdout
        
        # Combine both
        combined_diff = staged_diff + unstaged_diff
        
        if not combined_diff.strip():
            return None
        
        return combined_diff
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running git command: {e}")
        return None
    except FileNotFoundError:
        print("❌ Git is not installed or not in PATH")
        return None


def get_merge_diff() -> Optional[str]:
    """
    Get the diff between HEAD and ORIG_HEAD (for merge commits).
    ORIG_HEAD is set by git to the previous HEAD before merge.
    Returns the diff string or None if no changes detected.
    """
    try:
        # Check if ORIG_HEAD exists (set by git before merge)
        orig_head_check = subprocess.run(
            ["git", "rev-parse", "--verify", "ORIG_HEAD"],
            capture_output=True,
            check=False
        )
        
        # Check if this is a merge commit (has two parents)
        merge_check = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD^2"],
            capture_output=True,
            check=False
        )
        
        if merge_check.returncode == 0:
            # This is a merge commit with two parents
            # Get diff between the merged branch and current HEAD
            diff = subprocess.run(
                ["git", "diff", "HEAD^1", "HEAD"],
                capture_output=True,
                text=True,
                check=False
            ).stdout
        elif orig_head_check.returncode == 0:
            # ORIG_HEAD exists, use it (fast-forward merge)
            orig_head = orig_head_check.stdout.strip()
            current_head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            # Only proceed if they're different
            if orig_head != current_head:
                diff = subprocess.run(
                    ["git", "diff", orig_head, current_head],
                    capture_output=True,
                    text=True,
                    check=False
                ).stdout
            else:
                # Fallback: compare HEAD~1 to HEAD (last commit)
                diff = subprocess.run(
                    ["git", "diff", "HEAD~1", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=False
                ).stdout
        else:
            # No ORIG_HEAD, try comparing HEAD~1 to HEAD
            diff = subprocess.run(
                ["git", "diff", "HEAD~1", "HEAD"],
                capture_output=True,
                text=True,
                check=False
            ).stdout
        
        if not diff or not diff.strip():
            return None
        
        return diff
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running git command: {e}")
        return None
    except FileNotFoundError:
        print("❌ Git is not installed or not in PATH")
        return None


def generate_changelog_entry(diff: str) -> Optional[str]:
    """
    Use Ollama API to generate a changelog entry from the git diff.
    Returns the generated entry or None on error.
    """
    try:
        # Prepare the prompt (combine system prompt with user prompt)
        user_prompt = f"Code changes:\n\n{diff}"
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        
        # Call Ollama API
        payload = {
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "").strip()
        
        if not generated_text:
            print("⚠️  Ollama returned an empty response")
            return None
        
        return generated_text
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused. Is Ollama running? Try 'ollama serve'")
        return None
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Ollama might be processing a large request.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Ollama API: {e}")
        return None
    except KeyError as e:
        print(f"❌ Unexpected response format from Ollama: {e}")
        return None


def read_changelog() -> str:
    """
    Read the current CHANGELOG.md content.
    Creates the file if it doesn't exist.
    """
    changelog_path = Path(CHANGELOG_FILE)
    
    if changelog_path.exists():
        return changelog_path.read_text(encoding='utf-8')
    else:
        return ""


def write_changelog(content: str, new_entry: str):
    """
    Prepend the new entry to the CHANGELOG.md file.
    """
    changelog_path = Path(CHANGELOG_FILE)
    
    # Prepare the new content
    # If file is empty or doesn't start with a header, add "## Unreleased"
    existing_content = content.strip()
    
    if not existing_content:
        new_content = f"## Unreleased\n\n{new_entry}\n\n"
    elif existing_content.startswith("##"):
        # Prepend after the first header
        lines = existing_content.split('\n', 1)
        if len(lines) > 1:
            new_content = f"{lines[0]}\n\n{new_entry}\n\n{lines[1]}"
        else:
            new_content = f"{existing_content}\n\n{new_entry}\n\n"
    else:
        # No header, add one
        new_content = f"## Unreleased\n\n{new_entry}\n\n{existing_content}\n"
    
    # Write to file
    changelog_path.write_text(new_content, encoding='utf-8')
    print(f"✅ Updated {CHANGELOG_FILE}")


def main(auto_write=False):
    """Main function to orchestrate the changelog generation.
    
    Args:
        auto_write: If True, skip confirmation and write automatically.
    """
    # Check if we're in a post-merge context
    is_post_merge = os.environ.get('GIT_HOOK') == 'post-merge'
    
    if is_post_merge:
        print("🔍 Detected post-merge hook, checking merge changes...")
        diff = get_merge_diff()
    else:
        print("🔍 Checking for uncommitted changes...")
        diff = get_git_diff()
    
    if not diff:
        print("ℹ️  No changes detected")
        sys.exit(0)
    
    print(f"📝 Found changes ({len(diff)} characters)")
    print("\n" + "="*50)
    print("Generating changelog entry with Ollama...")
    print("="*50 + "\n")
    
    # Generate changelog entry
    entry = generate_changelog_entry(diff)
    
    if not entry:
        print("❌ Failed to generate changelog entry")
        sys.exit(1)
    
    # Display the generated entry
    print("📋 Generated changelog entry:")
    print("-" * 50)
    print(entry)
    print("-" * 50)
    print()
    
    # Skip confirmation if auto_write is True or in post-merge hook
    if not auto_write and not is_post_merge:
        response = input("Write this entry to CHANGELOG.md? [Y/n]: ").strip().lower()
        if response and response not in ['y', 'yes']:
            print("❌ Cancelled")
            sys.exit(0)
    else:
        print("🤖 Auto-writing to CHANGELOG.md...")
    
    # Read existing changelog
    existing_content = read_changelog()
    
    # Write the new entry
    write_changelog(existing_content, entry)
    
    print("✨ Done!")


if __name__ == "__main__":
    # Check for --auto flag or post-merge hook
    auto_write = '--auto' in sys.argv or os.environ.get('GIT_HOOK') == 'post-merge'
    main(auto_write=auto_write)

