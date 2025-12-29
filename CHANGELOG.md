## Unreleased

[Refactor]: Replaced mistral model with phi3:mini and increased timeout for CPU inference in `generate_changelog` entry script from 5 min to 10 min, updated Ollama API URLs. Added wait logic for Ollama service and added retry mechanisms when pulling models.


[Refactor] Change model from mistral to phi3:mini, increase timeout for CPU inference from 5 min to 10 min in generate_changelog entry script.


[Refactor]: Added wait logic for Ollama service and model pull with retry mechanisms