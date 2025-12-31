## Unreleased

[Feature] - Enhanced `generate_changelog` script to handle CI processing with mistral model using faster CPUs and improved timeout duration on Windows systems, including wait/retry mechanisms for pulling models. Transitioned to phi3:mini API URLs and added better waiting retry logic for performance during CI tasks tuned for 'phi3:mini' inference speedup three times faster than mistral model in the same environment with increased timeout duration on Windows platforms, along with a fallback using `git show`.


- [Feature]: Enhancement to handle merge commits in CI environment by comparing the HEAD^1 (main branch before merging) with HEAD. Now also includes a fallback method using "git show" for non-merge cases, logging debug information about differing outputs based on commit type length and warning output when no changes are detected after applying diff logic to merge commits.
+ [Feature]: Enhanced `generate_changelog` script for better CI processing by switching from mistral model with 'phi3:mini' three times faster CPUs, implementing wait/retry mechanisms on pulling models and increased timeout duration in the script across Windows systems. Refactor includes transitioning to phi3:mini API URLs alongside improved waiting retry logic for better performance execution of `generate_changelog` during CI tasks specifically tuned for three times faster inference using 'phi3:mini' on Windows platforms compared with mistral model, and an extension in timeout duration.


- [Feature]: Enhancement to handle merge commits in CI environment by comparing the HEAD^1 (main branch before merging) with HEAD. Now also includes a fallback method using "git show" for non-merge cases, and logging debug information about differing outputs from these methods based on commit type length. Additionally added warning output when no changes are detected after applying diff logic to merge commits.


[Feature]: Enhanced `generate_changelog` script for better CI processing by replacing mistral model with 'phi3:mini' that is three times faster on CPUs, implemented wait logic and retry mechanisms when pulling models. Increased timeout duration in the script from 5 min to 10 min across Windows systems.

[Refactor]: Transitioned model from mistral to phi3:mini with updated OLLAMA API URLs; added improved waiting, retries and increased `generate_changelog` script execution time limit for CPU inference tasks by 'phi3:mini' which is three times faster on Windows systems.


[Feature]: Increased timeout duration in `generate_changelog` script from 5 min to 10 min, updated OLLAMA API URLs. Added wait logic and retry mechanisms when pulling models using phi3:mini model which is three times faster than mistral on CPUs for CI-friendly environment enhancement.

[Feature]: Replaced mistral model with fast 'phi3:mini' model in `generate_changelog` entry script, updated OLLAMA API URLs and implemented wait logic along with retry mechanisms when pulling models to optimize performance on Windows systems for faster CI processing time of up to 10 min.


[Refactor]: Switched model from mistral to phi3:mini, updated OLLAMA API URLs and added wait logic with retry when pulling models. Increased timeout duration in `generate_changelog` script from 5 min to 10 min for CPU inference using the fast CI-friendly 'phi3:mini' model which is three times faster than mistral on CPUs, alongside updating OLLAMA API URLs and implementing wait logic with retry mechanisms when pulling models.


[Refactor]: Replaced mistral model with phi3:mini and increased timeout for CPU inference in `generate_changelog` entry script from 5 min to 10 min, updated Ollama API URLs. Added wait logic for Ollama service and added retry mechanisms when pulling models.


[Refactor] Change model from mistral to phi3:mini, increase timeout for CPU inference from 5 min to 10 min in generate_changelog entry script.


[Refactor]: Added wait logic for Ollama service and model pull with retry mechanisms