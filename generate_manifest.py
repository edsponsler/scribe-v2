import os
import json

PROCESSED_DIR = 'processed_corpus'

def generate_manifest():
    """
    Scans the processed corpus directory for header files and prints a manifest.
    """
    print("--- SCRIBE v2 Corpus Manifest ---")
    print(f"Reading from: ./{PROCESSED_DIR}/\n")

    try:
        all_files = os.listdir(PROCESSED_DIR)
    except FileNotFoundError:
        print(f"Error: Processed directory not found at '{PROCESSED_DIR}'.")
        print("Please run the main processing script first.")
        return

    header_files = sorted([f for f in all_files if f.endswith('_header.json')])

    if not header_files:
        print("No header files found. The corpus appears to be empty.")
        return

    for i, filename in enumerate(header_files):
        path = os.path.join(PROCESSED_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"Entry {i+1}: {data.get('title', 'N/A')}")
        print(f"  Author: {data.get('author', 'N/A')}")
        print(f"  Source File: {data.get('source_filename', 'N/A')}")
        print(f"  Content File: {data.get('content_filename', 'N/A')}")
        print(f"  Records: {data.get('record_count', 0)}")
        print(f"  Processed on: {data.get('processing_date_utc', 'N/A')}")
        print("-" * 40)


if __name__ == '__main__':
    generate_manifest()