import ollama

def simple_chat():
    print("🤖 Ollama Simple Chat")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    # Check if Ollama is running
    try:
        models_response = ollama.list()
        models_list = models_response.get('models', [])
        
        if not models_list:
            print("⚠️  No models found. Pull a model first:")
            print("   ollama pull llama2")
            return
        
        # Extract model names safely
        model_names = []
        for m in models_list:
            if isinstance(m, dict) and 'name' in m:
                model_names.append(m['name'])
            elif isinstance(m, str):
                model_names.append(m)
        
        print(f"✅ Connected! Available models: {model_names}\n")
        
        # Use the first available model or default to llama2
        if model_names:
            model = model_names[0]
        else:
            model = 'llama2'
            
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
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
            print("\n👋 Goodbye!")
            break
        
        # Add user message to history
        messages.append({'role': 'user', 'content': user_input})
        
        try:
            # Get response from Ollama
            print("🤖 Thinking...", end='\r')
            response = ollama.chat(model=model, messages=messages)
            assistant_message = response['message']['content']
            
            # Print response
            print(f"🤖 {assistant_message}\n")
            
            # Add assistant response to history
            messages.append(response['message'])
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            # Remove the last message if there was an error
            messages.pop()

if __name__ == "__main__":
    simple_chat()


