## Unreleased

- Dec 31, 2025 at 10:34 AM | 0 files | by arieldre01 - feat: feat(Dec. 31, 2025): Add installation of Ollama if not installed and skip retry logic for model pull to ensure backward compatibility with previous changes [ci/test] - refactor: script enhancement on Windows using phi3:mini for better performance execution in generate_changelog during merge commits handling, introducing cleanup functionality (maintain only unique entries)


- Dec 31, 2025 at 8:26 AM - feat: add installation of Ollama if not installed and skip retry logic for model pull to ensure backward compatibility with previous changes. Also, introduce a cleanup step before new changelog generation in CI mode or when the --cleanup flag is provided by removing duplicates from existing CHANGELOG.md (maintain only unique entries).


- Dec 31, 2025 at 10:23 AM - feat: refactor script to enhance CI processing on Windows using phi3:mini for better performance execution of generate_changelog during merge commits handling with cleanup functionality [ci/test]


- feat: Add conditional installation prompts based on the presence of Ollama with rollback on startup failure and retry mechanisms for model pull
- feat: Changed the `generate_changelog` script to enhance CI processing on Windows systems using phi3:mini with three times faster CPUs, including wait/retry mechanisms and increased timeout duration for better performance during changelog generation. This refactor also transitioned from mistral model API URLs to phi3:mini APIs and improved retry logic based on commit type length.
- feat: Added a simple `count_to_ten` function within the script, which counts numbers 0-10 using Python's for loop functionality.
- feat: Enhancement to handle merge commits in CI environment by comparing the HEAD^1 (main branch before merging) with HEAD. Now also includes a fallback method using "git show" for non-merge cases, logging debug information about differing outputs based on commit type length and warning output when no changes are detected after applying diff logic to merge commits.
- feat: Enhanced `generate_changelog` script for better CI processing by switching from mistral model with 'phi3:mini' three times faster CPUs, implementing wait/retry mechanisms on pulling models and increased timeout duration in the script across Windows systems.
- feat: Enhanced `generate_changelog` script for better CI processing by replacing mistral model with 'phi3:mini' that is three times faster on CPUs, implemented wait logic and retry mechanisms when pulling models. Increased timeout duration in the script from 5 min to 10 min across Windows systems.
- refactor: Transitioned model from mistral to phi3:mini with updated OLLAMA API URLs; added improved waiting, retries and increased `generate_changelog` script execution time limit for CPU inference tasks by 'phi3:mini' which is three times faster on Windows systems.
- feat: Increased timeout duration in `generate_changelog` script from 5 min to 10 min, updated OLLAMA API URLs. Added wait logic and retry mechanisms when pulling models using phi3:mini model which is three times faster than mistral on CPUs for CI-friendly environment enhancement.
- feat: Replaced mistral model with fast 'phi3:mini' model in `generate_changelog` entry script, updated OLLAMA API URLs and implemented wait logic along with retry mechanisms when pulling models to optimize performance on Windows systems for faster CI processing time of up to 10 min.
- refactor: Change model from mistral to phi3:mini, increase timeout for CPU inference from 5 min to 10 min in generate_changelog entry script.
- refactor: Added wait logic for Ollama service and model pull with retry mechanisms