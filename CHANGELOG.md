## Unreleased

[Refactor] - Changes to get_ci_diff function: Simplified code by directly returning changes from the last commit using `git show HEAD` instead of first getting merge commit details and then its differences with parent commits, making it unnecessary. Also removed redundant condition handling for checking if diff is empty or not as git log now provides full change history in one command output which can be filtered later on based upon requirements like `--grep`.


[Feature]: Enhanced `generate_changelog` script for better CI processing by replacing mistral model with 'phi3:mini' that is three times faster on CPUs, implemented wait logic and retry mechanisms when pulling models. Increased timeout duration in the script from 5 min to 10 min across Windows systems.

[Refactor]: Transitioned model from mistral to phi3:mini with updated OLLAMA API URLs; added improved waiting, retries and increased `generate_changelog` script execution time limit for CPU inference tasks by 'phi3:mini' which is three times faster on Windows systems.


[Feature]: Increased timeout duration in `generate_changelog` script from 5 min to 10 min, updated OLLAMA API URLs. Added wait logic and retry mechanisms when pulling models using phi3:mini model which is three times faster than mistral on CPUs for CI-friendly environment enhancement.

[Feature]: Replaced mistral model with fast 'phi3:mini' model in `generate_changelog` entry script, updated OLLAMA API URLs and implemented wait logic along with retry mechanisms when pulling models to optimize performance on Windows systems for faster CI processing time of up to 10 min.


[Refactor]: Switched model from mistral to phi3:mini, updated OLLAMA API URLs and added wait logic with retry when pulling models. Increased timeout duration in `generate_changelog` script from 5 min to 10 min for CPU inference using the fast CI-friendly 'phi3:mini' model which is three times faster than mistral on CPUs, alongside updating OLLAMA API URLs and implementing wait logic with retry mechanisms when pulling models.


[Refactor]: Replaced mistral model with phi3:mini and increased timeout for CPU inference in `generate_changelog` entry script from 5 min to 10 min, updated Ollama API URLs. Added wait logic for Ollama service and added retry mechanisms when pulling models.


[Refactor] Change model from mistral to phi3:mini, increase timeout for CPU inference from 5 min to 10 min in generate_changelog entry script.


[Refactor]: Added wait logic for Ollama service and model pull with retry mechanisms