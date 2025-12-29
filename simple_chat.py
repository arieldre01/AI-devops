"""
Simple chat interface for Ollama.
Requires: pip install ollama
"""
try:
    import ollama
except ImportError:
    print("[ERROR] 'ollama' package not installed.")
    print("   Install with: pip install ollama")
    exit(1)

def simple_chat():
    print("Ollama Simple Chat")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    # Check if Ollama is running
    try:
        models_response = ollama.list()
        models_list = models_response.get('models', [])
        
        if not models_list:
            print("[WARN] No models found. Pull a model first:")
            print("   ollama pull mistral")
            return
        
        # Extract model names safely
        model_names = []
        for m in models_list:
            if isinstance(m, dict) and 'name' in m:
                model_names.append(m['name'])
            elif isinstance(m, str):
                model_names.append(m)
        
        print(f"[OK] Connected! Available models: {model_names}\n")
        
        # Prefer mistral or llama3:8b, fallback to first available, or default to mistral
        model = 'mistral'  # Default lightweight model
        if model_names:
            # Check if mistral is available
            if any('mistral' in name.lower() for name in model_names):
                model = next(name for name in model_names if 'mistral' in name.lower())
            # Check if llama3:8b is available
            elif any('llama3' in name.lower() or 'llama3:8b' in name.lower() for name in model_names):
                model = next((name for name in model_names if 'llama3' in name.lower() or 'llama3:8b' in name.lower()), model_names[0])
            else:
                model = model_names[0]
            
    except Exception as e:
        print(f"[ERROR] Error connecting to Ollama: {e}")
        print("Make sure Ollama is running (ollama serve)")
        return
    print(f"Using model: {model}\n")
    
    # Conversation history
    messages = []
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        # Add user message to history
        messages.append({'role': 'user', 'content': user_input})
        
        try:
            # Get response from Ollama
            print("Thinking...", end='\r')
            response = ollama.chat(model=model, messages=messages)
            assistant_message = response['message']['content']
            
            # Print response
            print(f"Assistant: {assistant_message}\n")
            
            # Add assistant response to history
            messages.append(response['message'])
            
        except Exception as e:
            print(f"\n[ERROR] {e}\n")
            # Remove the last message if there was an error
            messages.pop()

if __name__ == "__main__":
    simple_chat()


