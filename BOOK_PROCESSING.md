# Book Processing Guide

This document outlines the step-by-step process for ingesting a new book into the Scribe v2 corpus. Following these steps ensures that the new data is correctly processed, enriched, and stored in a consistent format.

## Step 1: Add the New Book to `source_material`

Place the raw text file of the new book into the `source_material/` directory. For this guide, we will use `pg3296.txt` (The Confessions of St. Augustine) as our example.

## Step 2: Create a New Processing Script

Each book has a unique structure, so a dedicated Python script is required to parse it. This script will read the raw text and produce two files in the `processed_corpus/` directory: a `_header.json` file containing metadata, and a `_content.jsonl` file containing the structured text.

To expedite this process, you can use the Gemini CLI to generate the script for you.

### Suggested Gemini CLI Prompt:

```
Analyze the structure of `source_material/pg3296.txt`. Based on the existing scripts in the `scripts/` directory (like `process_josephus.py` and `process_kjv.py`), create a new Python script named `scripts/process_augustine.py`. This script should parse the new book and generate a `_header.json` file and a `_content.jsonl` file in the `processed_corpus` directory, following the established schema.
```

Assuming the script `scripts/process_augustine.py` is now created, proceed to the next step.

## Step 3: Update `main.py`

The `main.py` script orchestrates the entire processing workflow. It needs to be updated to recognize the new book and its corresponding processing script.

1.  **Import the new processing function:**
    ```python
    from scripts.process_augustine import process_augustine
    ```

2.  **Add an entry to the `PROCESSOR_MAP`:**
    ```python
    PROCESSOR_MAP = {
        'pg10.txt': process_kjv_bible,
        'pg2850.txt': process_josephus,
        'pg14657.txt': process_philo,
        'pg3296.txt': process_augustine, # Add this line
    }
    ```

## Step 4: Run the Main Processing Script

Execute the `main.py` script to process all the source files. This will generate the initial `_header.json` and `_content.jsonl` files for the new book.

```bash
python3 main.py
```

## Step 5: Run the Enrichment Script

The `enrich_and_restructure_data.py` script takes the output from the previous step and enriches it with additional metadata, standardizes the schema, and creates aggregated chapter-level files.

```bash
python3 enrich_and_restructure_data.py
```

## Step 6: Upload to Google Cloud Storage

Finally, upload the newly generated files from the `processed_corpus_enriched/` directory to the appropriate folders in your GCS bucket.

```bash
gcloud storage cp processed_corpus_enriched/content_paragraph/pg3296_content.jsonl gs://<your-gcs-bucket-name>/content_paragraph/
gcloud storage cp processed_corpus_enriched/content_chapter/pg3296_content.jsonl gs://<your-gcs-bucket-name>/content_chapter/
```

## The Importance of Schema Consistency

It is **critical** to maintain a consistent schema across all files within each of the three main data folders:

*   `processed_corpus_enriched/content_verse/`
*   `processed_corpus_enriched/content_paragraph/`
*   `processed_corpus_enriched/content_chapter/`

Upstream processes, such as data indexing and search, rely on a uniform data structure. Inconsistent field names (e.g., using `book` in one file and `chapter` in another) will cause these processes to fail or produce unexpected results.

Always ensure that the final output of your processing and enrichment scripts adheres to the established schema for each data type.
