"""
Helper script to test Ollama connection.
Requires: pip install ollama
"""
try:
    import ollama
except ImportError:
    print("[ERROR] 'ollama' package not installed.")
    print("   Install with: pip install ollama")
    print("   Or use generate_changelog.py which has no dependencies.")
    exit(1)

# Test Ollama connection
def test_ollama_connection():
    try:
        # Check if Ollama is running
        response = ollama.list()
        print("[OK] Ollama is running!")
        print(f"Available models: {[model['name'] for model in response['models']]}")
        return True
    except Exception as e:
        print(f"[ERROR] Error connecting to Ollama: {e}")
        print("Make sure Ollama is installed and running (ollama serve)")
        return False

# Pull a model (if needed)
def pull_model(model_name="mistral"):
    try:
        print(f"Pulling model: {model_name}...")
        ollama.pull(model_name)
        print(f"[OK] Model {model_name} downloaded successfully!")
    except Exception as e:
        print(f"[ERROR] Error pulling model: {e}")

# Basic chat function
def chat(prompt, model="mistral"):
    try:
        response = ollama.chat(model=model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    # Test connection
    if test_ollama_connection():
        # Example usage
        result = chat("Hello, how are you?")
        print(f"\nResponse: {result}")

