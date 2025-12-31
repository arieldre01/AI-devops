#!/usr/bin/env python3
"""
Automated CHANGELOG.md generator using Ollama and Git.
Zero external dependencies - uses only Python standard library.
Includes auto-install for Ollama if not present.
"""

import subprocess
import sys
import os
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import socket

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
MODEL = "phi3:mini"  # Fast model for CI - 3x faster than mistral on CPU
CHANGELOG_FILE = "CHANGELOG.md"
MAX_DIFF_CHARS = 4000  # Limit diff size for faster CI processing

# Ollama download URLs
OLLAMA_WINDOWS_URL = "https://ollama.com/download/OllamaSetup.exe"
OLLAMA_LINUX_INSTALL = "curl -fsSL https://ollama.com/install.sh | sh"
OLLAMA_MAC_URL = "https://ollama.com/download/Ollama-darwin.zip"

# System prompt for the LLM (Conventional Commits format)
SYSTEM_PROMPT = """You are a Senior Technical Writer. Summarize the following code changes into a single, concise changelog entry.

Use Conventional Commits format with one of these prefixes:
- feat: for new features
- fix: for bug fixes
- refactor: for code refactoring
- docs: for documentation changes
- chore: for maintenance tasks
- perf: for performance improvements
- test: for test changes

Example output: feat: add user authentication with OAuth2 support

Do not output any preamble, conversational text, or bullet points. Just the single line entry."""

# Valid prefixes for Conventional Commits
VALID_PREFIXES = ['feat:', 'fix:', 'refactor:', 'docs:', 'chore:', 'perf:', 'test:']

# Mapping from old format to Conventional format
FORMAT_MAPPING = {
    '[feature]': 'feat:',
    '[feat]': 'feat:',
    '[fix]': 'fix:',
    '[bugfix]': 'fix:',
    '[refactor]': 'refactor:',
    '[docs]': 'docs:',
    '[documentation]': 'docs:',
    '[chore]': 'chore:',
    '[perf]': 'perf:',
    '[performance]': 'perf:',
    '[test]': 'test:',
    '[tests]': 'test:',
}


# =============================================================================
# Ollama Auto-Install Functions
# =============================================================================

def is_ollama_installed() -> bool:
    """Check if Ollama CLI is installed and accessible."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def download_file(url: str, dest_path: str, show_progress: bool = True) -> bool:
    """Download a file from URL to destination path."""
    try:
        print(f"Downloading from {url}...")
        
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(request, timeout=300) as response:
            total_size = response.headers.get('Content-Length')
            total_size = int(total_size) if total_size else None
            
            downloaded = 0
            chunk_size = 8192
            
            with open(dest_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if show_progress and total_size:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"\r   Progress: {mb_downloaded:.1f}/{mb_total:.1f} MB ({percent:.1f}%)", end='', flush=True)
            
            if show_progress:
                print()  # New line after progress
        
        return True
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        return False


def install_ollama_windows() -> bool:
    """Install Ollama on Windows."""
    print("Installing Ollama for Windows...")
    
    # Download installer to temp directory
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "OllamaSetup.exe")
    
    if not download_file(OLLAMA_WINDOWS_URL, installer_path):
        return False
    
    print("Running installer (this may take a minute)...")
    print("   Note: You may see a Windows installer dialog.")
    
    try:
        # Run the installer silently if possible
        result = subprocess.run(
            [installer_path, "/S"],  # /S for silent install (NSIS style)
            check=False,
            timeout=300
        )
        
        # Clean up
        try:
            os.remove(installer_path)
        except:
            pass
        
        if result.returncode == 0:
            print("[OK] Ollama installed successfully!")
            return True
        else:
            # Try running without silent flag
            print("   Retrying with interactive installer...")
            result = subprocess.run([installer_path], check=False, timeout=600)
            return result.returncode == 0
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Installation timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Installation failed: {e}")
        return False


def install_ollama_linux() -> bool:
    """Install Ollama on Linux."""
    print("Installing Ollama for Linux...")
    
    try:
        # Check if curl is available
        curl_check = subprocess.run(["which", "curl"], capture_output=True, check=False)
        if curl_check.returncode != 0:
            print("[ERROR] 'curl' is required but not installed")
            print("   Install it with: sudo apt install curl")
            return False
        
        print("Running install script (may require sudo password)...")
        result = subprocess.run(
            OLLAMA_LINUX_INSTALL,
            shell=True,
            check=False
        )
        
        if result.returncode == 0:
            print("[OK] Ollama installed successfully!")
            return True
        else:
            print("[ERROR] Installation failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Installation failed: {e}")
        return False


def install_ollama_mac() -> bool:
    """Install Ollama on macOS."""
    print("Installing Ollama for macOS...")
    
    # Check if Homebrew is available
    brew_check = subprocess.run(["which", "brew"], capture_output=True, check=False)
    
    if brew_check.returncode == 0:
        print("Installing via Homebrew...")
        try:
            result = subprocess.run(
                ["brew", "install", "ollama"],
                check=False
            )
            if result.returncode == 0:
                print("[OK] Ollama installed successfully!")
                return True
        except Exception as e:
            print(f"   Homebrew install failed: {e}")
    
    # Fallback: Use curl install script
    print("Installing via curl script...")
    try:
        result = subprocess.run(
            "curl -fsSL https://ollama.com/install.sh | sh",
            shell=True,
            check=False
        )
        if result.returncode == 0:
            print("[OK] Ollama installed successfully!")
            return True
    except Exception as e:
        print(f"[ERROR] Installation failed: {e}")
    
    print("[ERROR] Auto-install failed. Please install manually from: https://ollama.com/download")
    return False


def install_ollama() -> bool:
    """Install Ollama based on the current OS."""
    print("\n" + "="*50)
    print("Ollama Auto-Installer")
    print("="*50 + "\n")
    
    if sys.platform == 'win32':
        return install_ollama_windows()
    elif sys.platform == 'darwin':
        return install_ollama_mac()
    elif sys.platform.startswith('linux'):
        return install_ollama_linux()
    else:
        print(f"[ERROR] Unsupported platform: {sys.platform}")
        print("   Please install Ollama manually from: https://ollama.com/download")
        return False


def start_ollama_service() -> bool:
    """Start the Ollama service if not running."""
    print("Starting Ollama service...")
    
    try:
        if sys.platform == 'win32':
            # On Windows, Ollama runs as a background process
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            # On Unix, start in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        # Wait for service to start
        print("   Waiting for Ollama to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_ollama_running():
                print("[OK] Ollama service started!")
                return True
            print(f"   Still waiting... ({i+1}s)")
        
        print("[ERROR] Timed out waiting for Ollama to start")
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to start Ollama: {e}")
        return False


def pull_model(model: str) -> bool:
    """Pull/download a model if not available."""
    print(f"\nDownloading model '{model}'...")
    print(f"   This is a one-time download (~4GB for Mistral)")
    print(f"   Please wait, this may take several minutes...\n")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", model],
            check=False
        )
        
        if result.returncode == 0:
            print(f"\n[OK] Model '{model}' downloaded successfully!")
            return True
        else:
            print(f"\n[ERROR] Failed to download model '{model}'")
            print(f"   Try manually: ollama pull {model}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error downloading model: {e}")
        return False


def ensure_ollama_ready(auto_install: bool = True) -> bool:
    """
    Ensure Ollama is installed, running, and has the required model.
    Returns True if ready, False otherwise.
    
    Args:
        auto_install: If True, attempt to install Ollama if not present
    """
    # Step 1: Check if Ollama is installed
    if not is_ollama_installed():
        print("[WARN] Ollama is not installed")
        
        if not auto_install:
            print("   Install from: https://ollama.com/download")
            return False
        
        # Prompt user for installation (skip in auto mode or CI)
        is_auto_mode = (os.environ.get('GIT_HOOK') == 'post-merge' or 
                        '--auto' in sys.argv or 
                        '--ci' in sys.argv or 
                        os.environ.get('GITHUB_ACTIONS') == 'true')
        
        if not is_auto_mode:
            response = input("   Would you like to install Ollama now? [Y/n]: ").strip().lower()
            if response and response not in ['y', 'yes']:
                print("   Skipping installation")
                return False
        
        if not install_ollama():
            return False
        
        # Verify installation
        if not is_ollama_installed():
            print("[ERROR] Installation verification failed")
            print("   Please restart your terminal and try again")
            return False
    
    print("[OK] Ollama is installed")
    
    # Step 2: Check if Ollama service is running
    if not check_ollama_running():
        print("[WARN] Ollama service is not running")
        
        if not start_ollama_service():
            print("   Try starting manually with: ollama serve")
            return False
    
    print("[OK] Ollama service is running")
    
    # Step 3: Check if model is available
    if not check_model_available(MODEL):
        print(f"[WARN] Model '{MODEL}' is not installed")
        print(f"   The model is required for AI-powered changelog generation.")
        
        # In auto mode or CI, just download it
        is_auto_mode = (os.environ.get('GIT_HOOK') == 'post-merge' or 
                        '--auto' in sys.argv or 
                        '--ci' in sys.argv or 
                        os.environ.get('GITHUB_ACTIONS') == 'true')
        
        if not is_auto_mode:
            response = input(f"   Download '{MODEL}' model now? (~4GB) [Y/n]: ").strip().lower()
            if response and response not in ['y', 'yes']:
                print("   Skipping model download")
                print(f"   To download later, run: ollama pull {MODEL}")
                return False
        
        if not pull_model(MODEL):
            return False
    
    print(f"[OK] Model '{MODEL}' is ready")
    
    return True


def check_ollama_running() -> bool:
    """
    Check if Ollama is running by pinging the tags endpoint.
    Returns True if Ollama is accessible, False otherwise.
    """
    try:
        request = Request(OLLAMA_TAGS_URL)
        with urlopen(request, timeout=2) as response:
            return response.status == 200
    except (URLError, HTTPError, OSError):
        return False


def check_model_available(model: str) -> bool:
    """
    Check if the specified model is available in Ollama.
    Returns True if model exists, False otherwise.
    """
    try:
        request = Request(OLLAMA_TAGS_URL)
        with urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            # Check if model name matches (with or without :latest tag)
            for m in models:
                model_name = m.get('name', '')
                if model_name == model or model_name == f"{model}:latest" or model_name.startswith(f"{model}:"):
                    return True
            return False
    except (URLError, HTTPError, OSError, json.JSONDecodeError):
        return False


def truncate_diff(diff: str, max_chars: int = MAX_DIFF_CHARS) -> str:
    """
    Truncate diff to avoid overwhelming the LLM context window.
    Keeps beginning and end of diff for context.
    """
    if len(diff) <= max_chars:
        return diff
    
    # Keep first 60% and last 20% of allowed characters
    first_part_size = int(max_chars * 0.6)
    last_part_size = int(max_chars * 0.2)
    
    first_part = diff[:first_part_size]
    last_part = diff[-last_part_size:]
    
    truncated = (
        f"{first_part}\n\n"
        f"... [diff truncated: {len(diff) - max_chars} characters omitted] ...\n\n"
        f"{last_part}"
    )
    
    return truncated


def get_git_diff() -> Optional[str]:
    """
    Get the diff of uncommitted changes (staged and unstaged).
    Returns the diff string or None if no changes detected.
    """
    try:
        # Get staged changes
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False
        )
        staged_diff = result.stdout if result.stdout else ""
        
        # Get unstaged changes
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False
        )
        unstaged_diff = result.stdout if result.stdout else ""
        
        # Combine both
        combined_diff = staged_diff + unstaged_diff
        
        if not combined_diff.strip():
            return None
        
        return combined_diff
    
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error running git command: {e}")
        return None
    except FileNotFoundError:
        print("[ERROR] Git is not installed or not in PATH")
        return None


def get_ci_diff() -> Optional[str]:
    """
    Get the diff for CI environment (GitHub Actions).
    For merge commits, gets the diff between first parent and HEAD.
    Returns the diff string or None if no changes detected.
    """
    try:
        # For merge commits (like GitHub PR merges), use diff from first parent
        # HEAD^1 is the main branch before merge, HEAD is after merge
        print("[DEBUG] Getting CI diff using: git diff HEAD^1 HEAD")
        result = subprocess.run(
            ["git", "diff", "HEAD^1", "HEAD", "--no-color"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False
        )
        diff = result.stdout if result.stdout else ""
        print(f"[DEBUG] Diff length from HEAD^1: {len(diff)} chars")
        
        # If that fails (not a merge commit), try git show
        if not diff.strip():
            print("[DEBUG] No diff from HEAD^1, trying git show HEAD")
            result = subprocess.run(
                ["git", "show", "--format=", "--no-color", "HEAD"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=False
            )
            diff = result.stdout if result.stdout else ""
            print(f"[DEBUG] Diff length from git show: {len(diff)} chars")
        
        if not diff or not diff.strip():
            print("[WARN] No diff found for this commit")
            return None
        
        return diff
    
    except Exception as e:
        print(f"[ERROR] Error getting CI diff: {e}")
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
            result = subprocess.run(
                ["git", "diff", "HEAD^1", "HEAD"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=False
            )
            diff = result.stdout if result.stdout else ""
        elif orig_head_check.returncode == 0:
            # ORIG_HEAD exists, use it (fast-forward merge)
            orig_head = orig_head_check.stdout.strip()
            current_head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            ).stdout.strip()
            
            # Only proceed if they're different
            if orig_head != current_head:
                result = subprocess.run(
                    ["git", "diff", orig_head, current_head],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=False
                )
                diff = result.stdout if result.stdout else ""
            else:
                # Fallback: compare HEAD~1 to HEAD (last commit)
                result = subprocess.run(
                    ["git", "diff", "HEAD~1", "HEAD"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=False
                )
                diff = result.stdout if result.stdout else ""
        else:
            # No ORIG_HEAD, try comparing HEAD~1 to HEAD
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "HEAD"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=False
            )
            diff = result.stdout if result.stdout else ""
        
        if not diff or not diff.strip():
            return None
        
        return diff
    
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error running git command: {e}")
        return None
    except FileNotFoundError:
        print("[ERROR] Git is not installed or not in PATH")
        return None


def generate_changelog_entry(diff: str) -> Optional[str]:
    """
    Use Ollama API to generate a changelog entry from the git diff.
    Returns the generated entry or None on error.
    """
    try:
        # Truncate diff if too large
        original_size = len(diff)
        diff = truncate_diff(diff)
        if len(diff) < original_size:
            print(f"[WARN] Diff truncated from {original_size} to {len(diff)} characters")
        
        # Prepare the prompt (combine system prompt with user prompt)
        user_prompt = f"Code changes:\n\n{diff}"
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        
        # Call Ollama API using urllib
        payload = {
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        request = Request(
            OLLAMA_API_URL,
            data=payload_bytes,
            headers={'Content-Type': 'application/json'}
        )
        
        with urlopen(request, timeout=300) as response:  # 5 min timeout
            result = json.loads(response.read().decode('utf-8'))
            generated_text = result.get("response", "").strip()
            
            if not generated_text:
                print("[WARN] Ollama returned an empty response")
                return None
            
            return generated_text
    
    except URLError as e:
        if "Connection refused" in str(e) or "No connection" in str(e):
            print("[ERROR] Connection refused. Is Ollama running? Try 'ollama serve'")
        else:
            print(f"[ERROR] Network error calling Ollama API: {e}")
        return None
    except HTTPError as e:
        print(f"[ERROR] HTTP error calling Ollama API: {e.code} {e.reason}")
        return None
    except socket.timeout:
        print("[ERROR] Request timed out. Ollama might be processing a large request.")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON response from Ollama: {e}")
        return None
    except KeyError as e:
        print(f"[ERROR] Unexpected response format from Ollama: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None


# =============================================================================
# Quality Functions: Timestamp, Validation, Deduplication
# =============================================================================

def format_timestamp(dt) -> str:
    """
    Format datetime to readable string: "Dec 31, 2025 at 2:30 PM"
    Cross-platform compatible (avoids %-I which is POSIX-only).
    """
    # Use %I (with leading zero) then strip it manually for cross-platform support
    formatted = dt.strftime("%b %d, %Y at %I:%M %p")
    # Remove leading zero from hour: "at 02:30" -> "at 2:30"
    formatted = formatted.replace(" at 0", " at ")
    return formatted


def get_merge_timestamp() -> str:
    """
    Get the timestamp of the current commit in readable format.
    Returns: "Dec 31, 2025 at 2:30 PM"
    """
    from datetime import datetime
    
    try:
        result = subprocess.run(
            ["git", "show", "-s", "--format=%ci", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse ISO format: "2025-12-31 14:30:00 +0000"
            timestamp_str = result.stdout.strip()
            # Remove timezone for parsing
            timestamp_str = timestamp_str.rsplit(' ', 1)[0]
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            return format_timestamp(dt)
    except Exception as e:
        print(f"[WARN] Could not get commit timestamp: {e}")
    
    # Fallback to current time
    return format_timestamp(datetime.now())


def validate_entry(entry: str) -> str:
    """
    Ensure entry follows Conventional format, fix if needed.
    Converts [Feature] -> feat:, [Fix] -> fix:, etc.
    """
    entry = entry.strip()
    
    # Remove leading bullet points or dashes
    if entry.startswith('- '):
        entry = entry[2:]
    elif entry.startswith('+ '):
        entry = entry[2:]
    elif entry.startswith('* '):
        entry = entry[2:]
    
    # Check if already valid
    entry_lower = entry.lower()
    for prefix in VALID_PREFIXES:
        if entry_lower.startswith(prefix):
            # Ensure proper capitalization: "feat: message"
            return prefix + entry[len(prefix):]
    
    # Try to convert from old format
    for old_format, new_format in FORMAT_MAPPING.items():
        if entry_lower.startswith(old_format):
            rest = entry[len(old_format):].strip()
            # Remove any following colons or dashes
            if rest.startswith(':') or rest.startswith('-'):
                rest = rest[1:].strip()
            return f"{new_format} {rest}"
    
    # If no recognized format, default to feat:
    return f"feat: {entry}"


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using word overlap.
    Returns a value between 0 and 1.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)


def find_duplicates(entries: list, threshold: float = 0.5) -> list:
    """
    Find entries that are too similar (likely duplicates).
    Returns list of indices to remove (keeps first occurrence).
    """
    duplicates_to_remove = set()
    
    for i, entry1 in enumerate(entries):
        if i in duplicates_to_remove:
            continue
        for j, entry2 in enumerate(entries[i+1:], start=i+1):
            if j in duplicates_to_remove:
                continue
            similarity = calculate_similarity(entry1, entry2)
            if similarity >= threshold:
                duplicates_to_remove.add(j)
    
    return sorted(duplicates_to_remove)


def parse_changelog_entries(content: str) -> tuple:
    """
    Parse CHANGELOG.md content into header, entries, and footer.
    Returns (header, entries_list, footer).
    """
    lines = content.split('\n')
    header_lines = []
    entries = []
    footer_lines = []
    in_unreleased = False
    passed_unreleased = False
    
    for line in lines:
        if line.strip().lower().startswith('## unreleased'):
            in_unreleased = True
            header_lines.append(line)
        elif line.strip().startswith('## ') and in_unreleased:
            # Hit next version section
            in_unreleased = False
            passed_unreleased = True
            footer_lines.append(line)
        elif in_unreleased:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                entries.append(stripped)
            elif not stripped:
                # Empty line, keep for spacing
                pass
        elif passed_unreleased:
            footer_lines.append(line)
        else:
            header_lines.append(line)
    
    return '\n'.join(header_lines), entries, '\n'.join(footer_lines)


def cleanup_changelog_file():
    """
    Clean up CHANGELOG.md: remove duplicates and validate format.
    """
    changelog_path = Path(CHANGELOG_FILE)
    
    if not changelog_path.exists():
        print(f"[ERROR] {CHANGELOG_FILE} not found")
        return False
    
    content = changelog_path.read_text(encoding='utf-8')
    header, entries, footer = parse_changelog_entries(content)
    
    if not entries:
        print("[INFO] No entries found to clean up")
        return True
    
    print(f"[INFO] Found {len(entries)} entries")
    
    # Validate all entries to Conventional format
    validated_entries = [validate_entry(e) for e in entries]
    
    # Find and remove duplicates
    duplicates = find_duplicates(validated_entries)
    if duplicates:
        print(f"[INFO] Removing {len(duplicates)} duplicate entries")
        validated_entries = [e for i, e in enumerate(validated_entries) if i not in duplicates]
    
    # Rebuild the changelog
    new_content = header.rstrip() + '\n\n'
    for entry in validated_entries:
        new_content += f"- {entry}\n"
    
    if footer.strip():
        new_content += '\n' + footer
    
    changelog_path.write_text(new_content, encoding='utf-8')
    print(f"[OK] Cleaned up {CHANGELOG_FILE}")
    print(f"     Entries: {len(entries)} -> {len(validated_entries)}")
    
    return True


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
    Validates entry format and adds timestamp.
    """
    changelog_path = Path(CHANGELOG_FILE)
    
    # Validate the entry to Conventional format
    validated_entry = validate_entry(new_entry)
    
    # Get the merge timestamp
    timestamp = get_merge_timestamp()
    
    # Format: "- Dec 31, 2025 at 2:30 PM - feat: description"
    formatted_entry = f"- {timestamp} - {validated_entry}"
    
    # Prepare the new content
    # If file is empty or doesn't start with a header, add "## Unreleased"
    existing_content = content.strip()
    
    if not existing_content:
        new_content = f"## Unreleased\n\n{formatted_entry}\n\n"
    elif existing_content.startswith("##"):
        # Prepend after the first header
        lines = existing_content.split('\n', 1)
        if len(lines) > 1:
            new_content = f"{lines[0]}\n\n{formatted_entry}\n\n{lines[1]}"
        else:
            new_content = f"{existing_content}\n\n{formatted_entry}\n\n"
    else:
        # No header, add one
        new_content = f"## Unreleased\n\n{formatted_entry}\n\n{existing_content}\n"
    
    # Write to file
    changelog_path.write_text(new_content, encoding='utf-8')
    print(f"[OK] Updated {CHANGELOG_FILE}")


def main(auto_write=False, ci_mode=False):
    """Main function to orchestrate the changelog generation.
    
    Args:
        auto_write: If True, skip confirmation and write automatically.
        ci_mode: If True, running in CI environment (GitHub Actions).
    """
    # Pre-flight checks with auto-install
    print("Running pre-flight checks...")
    
    if not ensure_ollama_ready(auto_install=True):
        print("\n[ERROR] Ollama setup failed")
        print("   Please install manually from: https://ollama.com/download")
        sys.exit(1)
    
    print("\n[OK] All pre-flight checks passed!")
    
    # Check if we're in a CI environment
    is_ci = ci_mode or os.environ.get('GITHUB_ACTIONS') == 'true'
    
    # Check if we're in a post-merge context
    is_post_merge = os.environ.get('GIT_HOOK') == 'post-merge'
    
    if is_ci:
        print("Detected CI environment (GitHub Actions), checking merge changes...")
        diff = get_ci_diff()
    elif is_post_merge:
        print("Detected post-merge hook, checking merge changes...")
        diff = get_merge_diff()
    else:
        print("Checking for uncommitted changes...")
        diff = get_git_diff()
    
    if not diff:
        print("[INFO] No changes detected")
        sys.exit(0)
    
    print(f"Found changes ({len(diff)} characters)")
    print("\n" + "="*50)
    print("Generating changelog entry with Ollama...")
    print("="*50 + "\n")
    
    # Generate changelog entry
    entry = generate_changelog_entry(diff)
    
    if not entry:
        print("[ERROR] Failed to generate changelog entry")
        sys.exit(1)
    
    # Display the generated entry
    print("Generated changelog entry:")
    print("-" * 50)
    print(entry)
    print("-" * 50)
    print()
    
    # Skip confirmation if auto_write is True, in CI mode, or in post-merge hook
    if not auto_write and not is_ci and not is_post_merge:
        response = input("Write this entry to CHANGELOG.md? [Y/n]: ").strip().lower()
        if response and response not in ['y', 'yes']:
            print("Cancelled")
            sys.exit(0)
    else:
        print("Auto-writing to CHANGELOG.md...")
    
    # Read existing changelog
    existing_content = read_changelog()
    
    # Write the new entry
    write_changelog(existing_content, entry)
    
    print("Done!")


# =============================================================================
# Git Hook Installation
# =============================================================================

# The hook script that will be installed to .git/hooks/post-merge
HOOK_SCRIPT = '''#!/bin/sh
# Post-merge hook - automatically generates changelog entries
# Installed by: python generate_changelog.py --install

export GIT_HOOK="post-merge"
REPO_ROOT=$(git rev-parse --show-toplevel)

if [ ! -f "$REPO_ROOT/generate_changelog.py" ]; then
    echo "[ERROR] generate_changelog.py not found at $REPO_ROOT"
    exit 1
fi

cd "$REPO_ROOT"

# Try py (Windows), then python3, then python
if command -v py >/dev/null 2>&1; then
    py "$REPO_ROOT/generate_changelog.py" --auto
elif command -v python3 >/dev/null 2>&1; then
    python3 "$REPO_ROOT/generate_changelog.py" --auto
elif command -v python >/dev/null 2>&1; then
    python "$REPO_ROOT/generate_changelog.py" --auto
else
    echo "[ERROR] Python not found"
    exit 1
fi
'''


def get_git_root() -> Optional[Path]:
    """Get the root directory of the current git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def install_hook() -> bool:
    """
    Install the post-merge git hook.
    Creates .git/hooks/post-merge that calls generate_changelog.py
    """
    print("\n" + "="*50)
    print("Installing Changelog Hook")
    print("="*50 + "\n")
    
    # Check if in git repo
    git_root = get_git_root()
    if not git_root:
        print("[ERROR] Not in a git repository")
        print("   Run 'git init' first or navigate to a git repository")
        return False
    
    print(f"[OK] Git repository found: {git_root}")
    
    # Check if generate_changelog.py is in the repo root
    script_path = git_root / "generate_changelog.py"
    if not script_path.exists():
        current_script = Path(__file__).resolve()
        if current_script != script_path:
            print(f"[WARN] generate_changelog.py not in repo root")
            print(f"   Current location: {current_script}")
            print(f"   Expected location: {script_path}")
            print(f"   Copy the script to your project root first")
            return False
    
    # Create hooks directory if it doesn't exist
    hooks_dir = git_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the hook script
    hook_path = hooks_dir / "post-merge"
    
    # Check if hook already exists
    if hook_path.exists():
        print(f"[WARN] Hook already exists at {hook_path}")
        # Check if it's our hook
        content = hook_path.read_text(encoding='utf-8', errors='replace')
        if "generate_changelog.py" in content:
            print("   This appears to be the changelog hook (already installed)")
            print("   Use --uninstall first if you want to reinstall")
            return True
        else:
            print("   This is a different hook - not overwriting")
            print("   Backup or remove it first if you want to install")
            return False
    
    # Write hook
    hook_path.write_text(HOOK_SCRIPT, encoding='utf-8')
    print(f"[OK] Hook installed: {hook_path}")
    
    # Make executable on Unix
    if sys.platform != 'win32':
        import stat
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print("[OK] Made hook executable")
    
    # Run Ollama setup
    print("\nSetting up Ollama...")
    if not ensure_ollama_ready(auto_install=True):
        print("[WARN] Ollama setup incomplete - you can run --setup later")
    
    print("\n" + "="*50)
    print("Installation Complete!")
    print("="*50)
    print("\nThe changelog will now be generated automatically when you merge branches.")
    print("\nTo test it:")
    print("   1. Create a branch:  git checkout -b test-branch")
    print("   2. Make changes and commit")
    print("   3. Merge to main:    git checkout main && git merge test-branch")
    print("   4. Check CHANGELOG.md - a new entry should appear!")
    print("\nTo uninstall: python generate_changelog.py --uninstall")
    
    return True


def uninstall_hook() -> bool:
    """Remove the post-merge git hook."""
    print("\n" + "="*50)
    print("Uninstalling Changelog Hook")
    print("="*50 + "\n")
    
    git_root = get_git_root()
    if not git_root:
        print("[ERROR] Not in a git repository")
        return False
    
    hook_path = git_root / ".git" / "hooks" / "post-merge"
    
    if not hook_path.exists():
        print("[INFO] No hook installed - nothing to remove")
        return True
    
    # Verify it's our hook before removing
    content = hook_path.read_text(encoding='utf-8', errors='replace')
    if "generate_changelog.py" not in content:
        print("[ERROR] The existing hook is not the changelog hook")
        print("   Not removing to avoid breaking your setup")
        return False
    
    # Remove the hook
    hook_path.unlink()
    print(f"[OK] Hook removed: {hook_path}")
    print("\nAutomatic changelog generation is now disabled.")
    print("You can still run manually: python generate_changelog.py")
    
    return True


def print_help():
    """Print usage help."""
    print("""
Automatic Changelog Generator

Usage:
    python generate_changelog.py [options]

Options:
    --install     Install the git hook for automatic changelog generation
    --uninstall   Remove the git hook
    --setup       Check/install Ollama and download the model
    --cleanup     Clean up CHANGELOG.md (remove duplicates, validate format)
    --auto        Generate changelog without confirmation prompt
    --ci          CI mode (non-interactive, for GitHub Actions)
    --help        Show this help message

Format:
    Entries use Conventional Commits format with timestamps:
    - Dec 31, 2025 at 2:30 PM - feat: add new feature
    - Dec 30, 2025 at 10:00 AM - fix: resolve bug in auth

Examples:
    # First-time setup (recommended)
    python generate_changelog.py --install
    
    # Manual changelog generation
    python generate_changelog.py
    
    # Check Ollama setup
    python generate_changelog.py --setup
    
    # Clean up existing changelog (remove duplicates)
    python generate_changelog.py --cleanup
    
    # Remove the hook
    python generate_changelog.py --uninstall
""")


def count_to_ten():
    """Simple function that counts from 0 to 10."""
    for i in range(11):
        print(i)
    return 10


if __name__ == "__main__":
    # Check for --help
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        sys.exit(0)
    
    # Check for --install flag
    if '--install' in sys.argv:
        success = install_hook()
        sys.exit(0 if success else 1)
    
    # Check for --uninstall flag
    if '--uninstall' in sys.argv:
        success = uninstall_hook()
        sys.exit(0 if success else 1)
    
    # Check for --setup flag (just install/setup, don't generate changelog)
    if '--setup' in sys.argv:
        print("Running Ollama setup...")
        if ensure_ollama_ready(auto_install=True):
            print("\n[OK] Setup complete! You can now use the changelog generator.")
            sys.exit(0)
        else:
            print("\n[ERROR] Setup failed.")
            sys.exit(1)
    
    # Check for --cleanup flag (remove duplicates and validate format)
    if '--cleanup' in sys.argv:
        print("Cleaning up CHANGELOG.md...")
        success = cleanup_changelog_file()
        sys.exit(0 if success else 1)
    
    # Check for --ci flag (GitHub Actions mode)
    ci_mode = '--ci' in sys.argv or os.environ.get('GITHUB_ACTIONS') == 'true'
    
    # Check for --auto flag or post-merge hook
    auto_write = '--auto' in sys.argv or os.environ.get('GIT_HOOK') == 'post-merge' or ci_mode
    main(auto_write=auto_write, ci_mode=ci_mode)
