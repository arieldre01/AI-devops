# Ollama Setup

## Installation

1. Install Ollama from https://ollama.com/download
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start Ollama service (usually runs automatically):
   ```bash
   ollama serve
   ```

2. Pull a model (first time):
   ```bash
   ollama pull llama2
   ```

3. Run the setup script:
   ```bash
   python ollama_setup.py
   ```

## API Endpoint

Ollama runs on: `http://localhost:11434`

