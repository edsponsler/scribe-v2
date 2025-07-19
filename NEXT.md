## Project Summary

Scribe V2 is a data processing pipeline designed to parse semi-structured historical texts (like those from Project Gutenberg) into a clean, machine-readable JSONL format. The pipeline processes each text into a main content file and a metadata header file. It uses Google Firestore to track the processing status of each source file, making it idempotent.

**Capabilities:**

*   Parses raw `.txt` files from the `source_material/` directory.
*   Maps source filenames to dedicated Python processor functions located in the `scripts/` directory.
*   Checks if a file has already been processed using Firestore.
*   Parses the text into structured records (e.g., paragraph by paragraph).
*   Generates a `_header.json` file (metadata) and a `_content.jsonl` file (content) in the `processed_corpus/` directory.
*   Provides utility scripts (`reconstruct_from_jsonl.py`) to validate the parsing logic by converting the JSONL back into text.
*   Includes example processors for "The Wars of the Jews" and the King James Bible.
*   Supports extension by adding new text processors.
*   Provides instructions for setting up Google Cloud and local environments.
*   Explains how to use the Gemini CLI as a coding partner.

**Development Status:**

The project appears to be functional, with a well-defined structure and clear instructions for setup and usage. The `README.md` provides details on adding new text processors, indicating that the project is designed to be extensible. The project also details how to use the Gemini CLI to develop agents that can analyze the current project and suggest next steps.

## Chosen Activities

### Improvement

**Summary:** Implement a linter and formatter to enforce consistent code style. This includes choosing a linter (like `flake8` or `pylint`) and a formatter (like `black`), configuring them, and adding a pre-commit hook to automatically run them before each commit.

### Development

**Summary:** Add unit tests for the core functions within the processor scripts. This involves creating tests for the parsing logic and the generation of the `_header.json` and `_content.jsonl` files, using `pytest` as the testing framework.

### New Feature

**Summary:** Develop a web-based interface for corpus management. This interface will allow users to upload source texts, monitor processing status, view processed texts, and manage processor mappings, making the pipeline more accessible to non-developers.

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

Web Interface for Corpus Management: A web-based interface for uploading source texts, monitoring processing, viewing results, and managing processor mappings. This would significantly improve accessibility for non-developers.

The project outline should include:

*   A list of specific tasks to be completed, including front-end, back-end, and database considerations.
*   The order in which the tasks should be completed.
*   The estimated time required for each task.
*   Any dependencies between the tasks.
*   Specific technologies to be used (e.g., Flask, Django, React, Vue.js).
*   How the new feature will integrate with the existing project.
*   Considerations for user interface/user experience (UI/UX).
*   API design and implementation for back-end support.
*   Database schema design for storing relevant data.

