import os
import re
import json
from datetime import datetime, timezone

from scripts.firestore_tracker import get_file_hash, check_if_processed, update_processed_status

def roman_to_int(s: str) -> int:
    """Converts a Roman numeral string to an integer."""
    s = s.upper()
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        # Check for subtractive notation (e.g., IV, IX, XL, etc.)
        if i > 0 and rom_val[s[i]] > rom_val[s[i-1]]:
            # The value is the current numeral minus twice the previous one
            # (since the previous one was already added).
            int_val += rom_val[s[i]] - 2 * rom_val[s[i-1]]
        else:
            int_val += rom_val[s[i]]
    return int_val

def process_josephus(source_path, processed_dir):
    """
    Parses a prose work by Josephus using a data-driven approach.
    It first reads the 'Contents' section to learn the document structure,
    then processes the main text, footnotes, and preface accordingly.
    """
    print(f"Starting data-driven processing of {source_path}...")

    # --- IDEMPOTENCY CHECK ---
    source_filename = os.path.basename(source_path)
    file_hash = get_file_hash(source_path)
    if check_if_processed(source_filename, file_hash):
        return

    # --- SETUP ---
    base_filename = os.path.splitext(source_filename)[0]
    header_output_path = os.path.join(processed_dir, f'{base_filename}_header.json')
    content_output_path = os.path.join(processed_dir, f'{base_filename}_content.jsonl')

    paragraph_pattern = re.compile(r'^(\d+)\.?\s(.*)')
    # This pattern now specifically looks for top-level headers like PREFACE or BOOK...
    header_pattern = re.compile(r'^(PREFACE|BOOK [IVXLCDM]+)\.?$')

    # --- STATE AND DATA COLLECTION ---
    header_metadata = {}
    content_records = []
    license_text = []
    content_headers = [] # <-- NEW: This will hold the structure learned from "Contents"

    # State variables
    current_work = "Unknown Work"
    current_book = None
    current_chapter = None
    in_header = True
    in_contents = False # <-- NEW: State to track if we are in the "Contents" section
    capturing_license = False
    in_footnotes = False

    with open(source_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()

            # --- Phase 1: Gutenberg Header Parsing ---
            if in_header:
                if "This ebook is for the use of anyone anywhere" in stripped_line:
                    capturing_license = True
                if capturing_license:
                    license_text.append(stripped_line)
                if stripped_line.startswith("Title:"):
                    header_metadata['title'] = stripped_line.split(":", 1)[1].strip()
                    current_work = header_metadata['title']
                elif stripped_line.startswith("Author:"):
                    header_metadata['author'] = stripped_line.split(":", 1)[1].strip()
                elif "*** START OF THE PROJECT GUTENBERG EBOOK" in stripped_line:
                    in_header = False
                    capturing_license = False
                continue

            # --- Phase 2: Learn structure from "Contents" section ---
            # The 'in_contents' flag is turned off when we encounter the first
            # real header that we learned from the contents list.
            if in_contents and content_headers and stripped_line == content_headers[0]:
                in_contents = False
                print(f"Learned document structure: {content_headers}")
                # Do not continue; let this line be processed by Phase 3.

            if stripped_line == "Contents":
                in_contents = True
                continue

            if in_contents:
                header_match = header_pattern.match(stripped_line)
                if header_match:
                    if stripped_line not in content_headers:
                        content_headers.append(stripped_line)
                continue # Ignore blank lines and other text within the Contents section

            # --- Phase 3: Process Document Content ---
            if not stripped_line:
                continue

            # Check if the line is one of the headers we learned from the Contents
            if stripped_line in content_headers:
                in_footnotes = False
                # Determine book identifier ("Preface" or "I", "II", etc.)
                if stripped_line == "PREFACE":
                    current_book = "Preface"
                    current_chapter = "Preface"
                else:
                    # Extracts the Roman numeral from "BOOK I."
                    current_book = stripped_line.split(' ')[1].replace('.', '')
                    current_chapter = None
                print(f"  Processing Section: {current_book}")
                continue # Move to the next line

            # The rest of the logic remains largely the same
            if stripped_line.endswith("FOOTNOTES"):
                in_footnotes = True
                current_chapter = "Footnotes"
                print(f"  Processing Footnotes for Section: {current_book}")
                continue

            if stripped_line.startswith("CHAPTER ") and not in_footnotes:
                chapter_str = stripped_line.split(' ')[1].replace('.', '')
                try:
                    # Try parsing as a standard integer first (e.g., "CHAPTER 1.")
                    current_chapter = int(chapter_str)
                except ValueError:
                    # If that fails, parse it as a Roman numeral (e.g., "CHAPTER I.")
                    current_chapter = roman_to_int(chapter_str)
                continue

            paragraph_match = paragraph_pattern.match(stripped_line)
            if paragraph_match:
                paragraph_num, text = paragraph_match.groups()
                content_records.append({
                    "work": current_work, "book": current_book, "chapter": current_chapter,
                    "paragraph": int(paragraph_num), "text": text
                })
            elif content_records and stripped_line:
                content_records[-1]['text'] += ' ' + stripped_line

    # --- Finalization and File Writing ---
    header_metadata['source_filename'] = source_filename
    header_metadata['content_filename'] = os.path.basename(content_output_path)
    header_metadata['processing_date_utc'] = datetime.now(timezone.utc).isoformat()
    header_metadata['license'] = "\n".join(license_text).strip()
    header_metadata['record_count'] = len(content_records)

    with open(header_output_path, 'w', encoding='utf-8') as f:
        json.dump(header_metadata, f, indent=2)
    print(f"Header metadata saved to {header_output_path}")

    with open(content_output_path, 'w', encoding='utf-8') as f:
        for record in content_records:
            f.write(json.dumps(record) + '\n')
    print(f"{len(content_records)} paragraph records saved to {content_output_path}")

    update_processed_status(source_filename, file_hash)

if __name__ == '__main__':
    process_josephus(
        source_path='source_material/pg2850.txt',
        processed_dir='processed_corpus'
    )