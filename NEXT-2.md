## Project Summary

Scribe V2 is a Python-based data processing pipeline designed to parse semi-structured historical texts (e.g., from Project Gutenberg) into a clean, machine-readable JSONL format. The core idea is to take raw `.txt` files from the `source_material/` directory, process them using dedicated Python processor functions (located in the `scripts/` directory), and output structured data (metadata header and content) to the `processed_corpus/` directory.

Key features and capabilities:

*   **Data Parsing:** Parses historical texts into structured JSONL format.
*   **Idempotency:** Uses Google Firestore to track processed files, preventing redundant processing.
*   **Extensibility:** Designed to be extensible with new text processors.
*   **Google Cloud Integration:** Leverages Google Cloud Firestore and Storage.
*   **Validation:** Includes a utility script (`reconstruct_from_jsonl.py`) to validate parsing logic.
*   **Gemini CLI Integration:** Provides instructions on how to use Gemini CLI as a coding partner, especially for developing new agents using the Google Agent Development Kit (ADK).

Current development status:

The project appears to be in a functional state, with a clear workflow for processing text files and a structure that allows for adding new processors. The `README.md` provides comprehensive setup and usage instructions. The presence of files like `NEXT.md` suggests active development and future plans. The project relies on Google Cloud services, so it requires a Google Cloud project with Firestore enabled.

## Chosen Activities

### Improvement

**Summary:** Implement a linter and formatter to enforce consistent code style. This includes choosing a linter (like `flake8` or `pylint`) and a formatter (like `black`), configuring them, and adding a pre-commit hook to automatically run them before each commit.

### Development

**Summary:** Add unit tests for the core functions within the processor scripts. This involves creating tests for the parsing logic and the generation of the `_header.json` and `_content.jsonl` files, using `pytest` as the testing framework.

### New Feature

**Summary:** Integrate Named Entity Recognition (NER) capabilities to automatically identify and classify entities within the texts. This will greatly enhance the searchability and analytical potential of the processed data.

## Gemini CLI Prompts

### Improvement Prompt

```
Create a detailed project outline to implement the following improvement for a Python project:

Use a Linter and Formatter: Enforce consistent code style by using a linter (like flake8 or pylint) and a formatter (like black). Add a pre-commit hook to automatically run the linter and formatter before each commit.

The project outline should include:

*   A list of specific tasks to be completed.
*   The order in which the tasks should be completed.
*   The estimated time required for each task.
*   Any dependencies between the tasks.
*   Specific tools and technologies to be used.
*   How to integrate this into the existing project using pre-commit hooks.
```

### Development Prompt

```
Create a detailed project outline to implement the following development task for a Python project:

Add Unit Tests: Create unit tests for the core functions within the processor scripts. Focus on testing the parsing logic and the generation of the `_header.json` and `_content.jsonl` files. Use a testing framework like `pytest`.

The project outline should include:

*   A list of specific tasks to be completed.
*   The order in which the tasks should be completed.
*   The estimated time required for each task.
*   Any dependencies between the tasks.
*   Specific files that need to be created or changed.
*   How to write tests for the existing code.
*   How to generate the header and content jsonl files.
*   Specific tools and technologies to be used (e.g., pytest, mocking libraries).
```

### New Feature Prompt

```
Create a detailed project outline to implement the following new feature for a Python project:

Integrate Named Entity Recognition (NER) capabilities to automatically identify and classify people, locations, organizations, and dates within the texts. This will greatly enhance the searchability and analytical potential of the processed data.

The project outline should include:

*   A list of specific tasks to be completed, including data preparation, model selection, integration, and evaluation.
*   The order in which the tasks should be completed.
*   The estimated time required for each task.
*   Any dependencies between the tasks.
*   Specific technologies to be used (e.g., spaCy, transformers, stanza, NLTK).
*   How the new feature will integrate with the existing project.
*   Considerations for data storage, indexing, and search.
*   API design and implementation for back-end support.
*   How to handle historical text and potential variations in entity names.

