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
        if i > 0 and rom_val[s[i]] > rom_val[s[i-1]]:
            int_val += rom_val[s[i]] - 2 * rom_val[s[i-1]]
        else:
            int_val += rom_val[s[i]]
    return int_val

def process_augustine(source_path, processed_dir):
    """
    Parses "The Confessions of St. Augustine".
    It processes the main text, chunking by paragraph within each book (referred to as chapter).
    """
    print(f"Starting processing of {source_path}...")

    # --- IDEMPOTENCY CHECK ---
    source_filename = os.path.basename(source_path)
    file_hash = get_file_hash(source_path)
    # Since we are reprocessing, we should ideally clear the previous status,
    # but for this flow, we'll just overwrite. A more robust system
    # might handle this differently.

    # --- SETUP ---
    base_filename = os.path.splitext(source_filename)[0]
    header_output_path = os.path.join(processed_dir, f'{base_filename}_header.json')
    content_output_path = os.path.join(processed_dir, f'{base_filename}_content.jsonl')

    chapter_pattern = re.compile(r'^BOOK ([IVXLCDM]+)$')

    # --- STATE AND DATA COLLECTION ---
    header_metadata = {}
    content_records = []
    license_text = []
    paragraph_buffer = []

    # State variables
    current_work = "Unknown Work"
    current_chapter = None
    paragraph_counter = 0
    in_header = True
    in_main_content = False
    capturing_license = False

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
                    in_main_content = True
                continue

            if not in_main_content:
                continue

            # --- Check for end of book marker ---
            if "*** END OF THE PROJECT GUTENBERG EBOOK" in stripped_line:
                break

            # --- Phase 2: Process Document Content ---
            chapter_match = chapter_pattern.match(stripped_line)
            if chapter_match:
                if paragraph_buffer and current_chapter is not None:
                    paragraph_text = " ".join(paragraph_buffer)
                    paragraph_counter += 1
                    content_records.append({
                        "work": current_work,
                        "chapter": current_chapter,
                        "paragraph": paragraph_counter,
                        "text": paragraph_text
                    })
                    paragraph_buffer = []

                current_chapter = roman_to_int(chapter_match.group(1))
                paragraph_counter = 0
                print(f"  Processing Chapter: {current_chapter}")
                continue

            if current_chapter is not None:
                if stripped_line:
                    paragraph_buffer.append(stripped_line)
                # A blank line indicates a paragraph break.
                elif paragraph_buffer:
                    paragraph_text = " ".join(paragraph_buffer)
                    paragraph_counter += 1
                    content_records.append({
                        "work": current_work,
                        "chapter": current_chapter,
                        "paragraph": paragraph_counter,
                        "text": paragraph_text
                    })
                    paragraph_buffer = []

    # --- Finalization and File Writing ---
    # Process any remaining paragraph in the buffer
    if paragraph_buffer and current_chapter is not None:
        paragraph_text = " ".join(paragraph_buffer)
        paragraph_counter += 1
        content_records.append({
            "work": current_work,
            "chapter": current_chapter,
            "paragraph": paragraph_counter,
            "text": paragraph_text
        })

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

    # We are overwriting, so we update the status again.
    update_processed_status(source_filename, file_hash)

if __name__ == '__main__':
    process_augustine(
        source_path='source_material/pg3296.txt',
        processed_dir='processed_corpus'
    )