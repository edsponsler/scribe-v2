# Scribe V2: Historical Corpus Processor

Scribe V2 is a data processing pipeline designed to parse semi-structured historical texts, such as those from Project Gutenberg, into a clean, machine-readable JSONL format. Each text is processed into a main content file and a corresponding metadata header file.

The pipeline is designed to be idempotent, using Google Firestore to track the processing status of each source file based on its content hash. This prevents redundant processing of unchanged files.

## Overview

The core workflow is as follows:

1.  **Source Texts**: Raw `.txt` files are placed in the `source_material/` directory.
2.  **Orchestration**: The `main.py` script acts as a controller, iterating through source files.
3.  **Processor Mapping**: A dictionary in `main.py` maps specific source filenames to their dedicated Python processor functions located in the `scripts/` directory.
4.  **Idempotency Check**: Before processing, `scripts/firestore_tracker.py` checks if the file's hash has already been successfully processed. If so, the script skips it.
5.  **Parsing**: The appropriate processor (e.g., `process_josephus.py`) reads the source text and parses it into structured records (e.g., paragraph by paragraph).
6.  **Output**: The processor generates two files in the `processed_corpus/` directory:
    *   A `_header.json` file containing metadata about the work (title, author, processing date, etc.).
    *   A `_content.jsonl` file where each line is a JSON object representing a single record (e.g., a verse or a paragraph).
7.  **Validation**: Utility scripts like `reconstruct_from_jsonl.py` can be used to convert the structured JSONL back into a text format to validate the parsing logic.

## Project Structure

```
scribe-v2/
├── .gitignore
├── gcenv.sh.example      # Template for environment variables
├── generate_manifest.py  # Utility to display a summary of the processed corpus
├── main.py               # Main controller script for the pipeline
├── processed_corpus/     # Output directory for structured data
├── reconstruct_from_jsonl.py # Validation utility
├── reconstructed/        # Output for reconstructed texts
├── requirements.txt      # Python dependencies
├── scripts/
│   ├── firestore_tracker.py # Idempotency checks using Google Firestore
│   ├── process_josephus.py  # Parser for "The Wars of the Jews"
│   └── process_kjv.py       # Parser for the King James Bible
└── source_material/      # Input directory for raw text files
```

## Setup Instructions

### Prerequisites

*   Python 3.8+
*   Google Cloud SDK (`gcloud` CLI) installed and configured.

### 1. Google Cloud Setup

This project uses Google Firestore for tracking processed files.

1.  **Select or Create a GCP Project**:
    ```bash
    gcloud projects create YOUR_PROJECT_ID
    gcloud config set project YOUR_PROJECT_ID
    ```

2.  **Enable Firestore API**:
    ```bash
    gcloud services enable firestore.googleapis.com
    ```

3.  **Create a Firestore Database**:
    *   Go to the Firestore console for your project.
    *   Choose **Native Mode**.
    *   Select a location for your database.

4.  **Authenticate Locally**:
    Log in with Application Default Credentials. The Python client library will use these credentials automatically.
    ```bash
    gcloud auth application-default login
    ```

### 2. Local Environment Setup

1.  **Clone the Repository**:
    ```bash
    git clone <your-repo-url>
    cd scribe-v2
    ```

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Copy the example configuration file and edit it with your GCP details.
    ```bash
    cp gcenv.sh.example gcenv.sh
    ```
    Edit `gcenv.sh` and set `GOOGLE_CLOUD_PROJECT` and `FIRESTORE_COLLECTION_NAME`.

5.  **Load Environment Variables**:
    Source the configuration file in your terminal session before running any scripts.
    ```bash
    source gcenv.sh
    ```

## Usage

*   **Run the Full Pipeline**:
    To process all texts configured in `main.py`:
    ```bash
    python -m main
    ```

*   **Generate a Manifest**:
    To view a summary of all works processed in the `processed_corpus` directory:
    ```bash
    python -m generate_manifest.py
    ```

*   **Validate a Parsed Text**:
    To reconstruct a text from its JSONL file for validation (example for Josephus):
    ```bash
    python -m reconstruct_from_jsonl.py
    ```

## Adding a New Text Processor

The pipeline is designed to be extensible. To add a processor for a new text:

1.  **Add the Source File**: Place the new text file (e.g., `new_text.txt`) into the `source_material/` directory.

2.  **Create a Processor Script**:
    *   Create a new Python script in the `scripts/` directory (e.g., `scripts/process_new_text.py`).
    *   This script should contain a main function (e.g., `process_new_text(source_path, processed_dir)`) that handles the parsing logic.
    *   Implement the idempotency check using the functions from `scripts/firestore_tracker.py`.
    *   The script should output a `_header.json` and `_content.jsonl` file to the `processed_dir`.

3.  **Update the Main Controller**:
    *   Open `main.py`.
    *   Import your new processor function: `from scripts.process_new_text import process_new_text`.
    *   Add an entry to the `PROCESSOR_MAP` dictionary:
        ```python
        PROCESSOR_MAP = {
            'pg10.txt': process_kjv_bible,
            'pg2850.txt': process_josephus,
            'new_text.txt': process_new_text, # Add your new entry here
        }
        ```

You can now run `python -m main` to process the new text alongside the existing ones.

## Using Gemini CLI as a Coding Partner

For developers looking for an interactive coding assistant directly in their terminal, the Gemini CLI can be a powerful partner. It can help with generating code, explaining snippets, and brainstorming solutions for your processors.

### Installation (Ubuntu)

The standard method for installing the Gemini CLI on an Ubuntu system is to use `npm` (Node Package Manager):

```bash
npm install -g @google/gemini-cli
```

### Authentication

The Gemini CLI can automatically use the same authentication you've already set up for this project. If you have run `gcloud auth application-default login`, the CLI will use those credentials to access the Gemini API.

### More Information

For more detailed installation instructions and advanced usage, visit the official repository:

https://github.com/google-gemini/gemini-cli

## Using Gemini CLI with ADK Context for Project Development

This project includes a file named `llms-full.txt`, which contains comprehensive documentation for the Google Agent Development Kit (ADK). You can use this file to provide rich context to the Gemini CLI, enabling it to assist you in developing new agents that extend this project's capabilities.

By passing this file as context, you can ask Gemini to generate code, create project plans, and even act as a mentor, all with a deep understanding of the ADK framework.

### Example 1: Generating a Project Outline

Use the following prompt to ask Gemini to create a project outline for enhancing Gemini CLI integration for the Scribe V2 project. 

```bash
gemini -f llms-full.txt "Create a project outline for enhancing the Gemini CLI integration for the Scribe V2 project. The goal is to assist users in creating new processor scripts and debugging existing ones using the Google ADK. The outline should include steps for designing specific prompts for code generation, creating workflows for debugging processor scripts, using the ADK to create agents that assist in the processor creation and debugging process, and providing clear instructions for users on how to use the enhanced integration. Consider using the 'llms-full.txt' file in the project as context for generating the prompts and workflows. The outline should also cover the use of Gemini CLI to create sample processor scripts from scratch, given a description of the text format to be processed."
```

### Example 2: Step-by-Step Mentorship

After generating an outline, you can ask Gemini to guide you through the implementation.

```bash
gemini -f llms-full.txt "Act as my mentor. Using the project outline we just created, walk me through a step by step tutorial to implement the project using the Google ADK. Explain each part of the ADK code as we build it. Pause after each step and ask if I am ready to continue."
```

https://github.com/google-gemini/gemini-cli

## Understanding Authentication and Billing in this Project

I will use the following fake accounts for the following discussion:

*   My Google Account: **ed@example.com** (This account is used to setup the Google Cloud account and setup billing for your projects.)
*   My Adminiatrative Project: **admin-1234567** (Expense administrative gcloud commands to this project)
*   My Active Project: **fun-project-1234567** (The current project we're working on; expense all python API and Gemini CLI calls to this project)

A key aspect of working with Google Cloud is understanding how different tools authenticate and how costs are attributed. Our setup for this project highlights an important distinction between the `gcloud` command-line tool and the Python application code (including the Gemini CLI).

### Two Distinct Contexts: `gcloud` vs. Application Code

When you work on this project, you operate in two separate authentication and billing contexts:

1.  **The `gcloud` CLI Context**:
    *   **Authentication**: This is the account you log into with `gcloud auth login`. It's the identity used when you run `gcloud` commands directly in your terminal.
    *   **Billing**: When a `gcloud` command makes an API call (e.g., `gcloud projects describe`), the associated costs and API quotas are billed to the project set in its *own* configuration. In our discussion, this was the `admin-1234567` project, as seen in the `[billing] quota_project` setting from `gcloud config list`.

2.  **The Application Default Credentials (ADC) Context**:
    *   **Authentication**: This is the account you authorize with `gcloud auth application-default login`. This is the identity used by Google Cloud client libraries, which includes our **Python scripts** and the **Gemini CLI**. The credentials for this context are stored in a separate JSON file.
    *   **Billing**: The `gcenv.sh` script correctly sets the quota project for this context to **`fun-project-1234567`**. This means all API calls made by the Python application (to Firestore, Cloud Storage, etc.) and the Gemini CLI are billed to the `fun-project-1234567` project, not the `gcloud` CLI's default billing project `admin-1234567`.

This separation is powerful: it allows your command-line administrative tasks to be billed differently from your application's operational costs, preventing accidental cross-billing.

### Required IAM Roles

For the project to function correctly, the user account authenticated for **Application Default Credentials** (e.g., `ed@example.com`) needs the following roles granted on the `fun-project-1234567` project:

*   `roles/firestore.user`: Allows the Python scripts to read from and write to the Firestore database to track file processing status.
*   `roles/aiplatform.user`: Required for the Gemini CLI to access the Gemini API for generative AI tasks.
*   `roles/serviceusage.serviceUsageConsumer`: Allows the project to be billed for the API usage generated by the application and Gemini CLI.

For a user to perform administrative tasks with the `gcloud` CLI, such as creating new resources like a Cloud Storage bucket, they would need different roles, like `roles/storage.admin`.

### Credential Lifetime

The Application Default Credentials you create are long-lived. They use a short-lived (1 hour) access token that is automatically and seamlessly refreshed by the client libraries using a secure, long-lived refresh token. This means you do not need to re-authenticate every hour. The credentials remain valid until they are explicitly revoked.
