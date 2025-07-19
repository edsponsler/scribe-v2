# Project Summary

Scribe V2 is a Python-based data processing pipeline designed to parse semi-structured historical texts (like those from Project Gutenberg) into clean, machine-readable JSONL format. The pipeline processes each text into a main content file and a metadata header file. It uses Google Firestore to track the processing status of files based on their content hash, ensuring idempotency. The core workflow involves reading raw text files from a source directory, mapping them to specific processor functions, checking for prior processing, parsing the text into structured records, and outputting the processed data and metadata to a designated directory. The project is designed to be extensible, allowing users to add new text processors. It also integrates with the Gemini CLI for code generation and project development assistance, using the Google Agent Development Kit (ADK).

# Chosen Activities

## Improvement

The chosen improvement activity is to implement robust error handling with logging in the Scribe V2 processor scripts (`scripts/process_josephus.py`, `scripts/process_kjv.py`, etc.). This includes adding try-except blocks, using the Python logging module, and implementing retry mechanisms for transient errors to improve the project's robustness and stability.

## Development

The chosen development activity is to enhance test coverage by adding unit tests for the existing processor scripts (`scripts/process_josephus.py`, `scripts/process_kjv.py`) and the `firestore_tracker.py` module. This involves setting up pytest, writing test cases for edge cases and error handling scenarios, using mocks to isolate components, and ensuring sufficient code coverage.

## New Feature

The chosen new feature is to enhance the Gemini CLI integration for the Scribe V2 project. This aims to assist users in creating new processor scripts and debugging existing ones using the Google ADK. This will involve designing specific prompts for code generation, creating workflows for debugging processor scripts, using the ADK to create agents that assist in the processor creation and debugging process, and providing clear instructions for users on how to use the enhanced integration.

# Gemini CLI Prompts

## Improvement Prompt

```
Create a project outline for implementing robust error handling and logging in the Scribe V2 processor scripts (scripts/process_josephus.py, scripts/process_kjv.py). The outline should include steps for identifying potential error sources, implementing try-except blocks, using the Python logging module, and configuring logging levels. Focus on error scenarios related to file I/O, data parsing, and interaction with external services like Firestore. Also describe how to handle retry mechanisms for transient errors.
```

## Development Prompt

```
Create a project outline for enhancing test coverage for the Scribe V2 project. The outline should cover adding unit tests for the processor scripts (scripts/process_josephus.py, scripts/process_kjv.py) and the firestore_tracker.py module. The outline should include steps for setting up pytest, writing test cases for edge cases and error handling scenarios, using mocks to isolate components, and ensuring sufficient code coverage. The tests should cover scenarios where files are missing, invalid data is encountered, or Firestore is unavailable.
```

## New Feature Prompt

```
Create a project outline for enhancing the Gemini CLI integration for the Scribe V2 project. The goal is to assist users in creating new processor scripts and debugging existing ones using the Google ADK. The outline should include steps for designing specific prompts for code generation, creating workflows for debugging processor scripts, using the ADK to create agents that assist in the processor creation and debugging process, and providing clear instructions for users on how to use the enhanced integration. Consider using the 'llms-full.txt' file in the project as context for generating the prompts and workflows. The outline should also cover the use of Gemini CLI to create sample processor scripts from scratch, given a description of the text format to be processed.
```

