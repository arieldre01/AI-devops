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

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
MODEL = "mistral"  # Change this to use a different model
CHANGELOG_FILE = "CHANGELOG.md"
MAX_DIFF_CHARS = 8000  # Limit diff size to avoid context overflow

# Ollama download URLs
OLLAMA_WINDOWS_URL = "https://ollama.com/download/OllamaSetup.exe"
OLLAMA_LINUX_INSTALL = "curl -fsSL https://ollama.com/install.sh | sh"
OLLAMA_MAC_URL = "https://ollama.com/download/Ollama-darwin.zip"

# System prompt for the LLM
SYSTEM_PROMPT = "You are a Senior Technical Writer. Summarize the following code changes into a single, concise bullet point. Start with a category like [Feature], [Fix], or [Refactor]. Do not output any preamble or conversational text."


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
        
        # Prompt user for installation (skip in auto mode)
        is_auto_mode = os.environ.get('GIT_HOOK') == 'post-merge' or '--auto' in sys.argv
        
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
        
        # In auto mode, just download it
        is_auto_mode = os.environ.get('GIT_HOOK') == 'post-merge' or '--auto' in sys.argv
        
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
        
        with urlopen(request, timeout=300) as response:
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
    except TimeoutError:
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
    print(f"[OK] Updated {CHANGELOG_FILE}")


def main(auto_write=False):
    """Main function to orchestrate the changelog generation.
    
    Args:
        auto_write: If True, skip confirmation and write automatically.
    """
    # Pre-flight checks with auto-install
    print("Running pre-flight checks...")
    
    if not ensure_ollama_ready(auto_install=True):
        print("\n[ERROR] Ollama setup failed")
        print("   Please install manually from: https://ollama.com/download")
        sys.exit(1)
    
    print("\n[OK] All pre-flight checks passed!")
    
    # Check if we're in a post-merge context
    is_post_merge = os.environ.get('GIT_HOOK') == 'post-merge'
    
    if is_post_merge:
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
    
    # Skip confirmation if auto_write is True or in post-merge hook
    if not auto_write and not is_post_merge:
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


if __name__ == "__main__":
    # Check for --setup flag (just install/setup, don't generate changelog)
    if '--setup' in sys.argv:
        print("Running Ollama setup...")
        if ensure_ollama_ready(auto_install=True):
            print("\n[OK] Setup complete! You can now use the changelog generator.")
            sys.exit(0)
        else:
            print("\n[ERROR] Setup failed.")
            sys.exit(1)
    
    # Check for --auto flag or post-merge hook
    auto_write = '--auto' in sys.argv or os.environ.get('GIT_HOOK') == 'post-merge'
    main(auto_write=auto_write)
