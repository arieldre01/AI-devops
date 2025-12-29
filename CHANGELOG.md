## Unreleased

[Refactor]: Switched model from mistral to phi3:mini, updated OLLAMA API URLs and added wait logic with retry when pulling models. Increased timeout duration in `generate_changelog` script from 5 min to 10 min for CPU inference using the fast CI-friendly 'phi3:mini' model which is three times faster than mistral on CPUs, alongside updating OLLAMA API URLs and implementing wait logic with retry mechanisms when pulling models.


[Refactor]: Replaced mistral model with phi3:mini and increased timeout for CPU inference in `generate_changelog` entry script from 5 min to 10 min, updated Ollama API URLs. Added wait logic for Ollama service and added retry mechanisms when pulling models.


[Refactor] Change model from mistral to phi3:mini, increase timeout for CPU inference from 5 min to 10 min in generate_changelog entry script.


[Refactor]: Added wait logic for Ollama service and model pull with retry mechanisms