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