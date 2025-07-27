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

def process_philo(source_path, processed_dir):
    """
    Parses "Philo-Judæus of Alexandria" by Norman Bentwich.
    It first reads the 'Contents' section to learn the document structure,
    then processes the main text, chunking by paragraph within each chapter.
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

    chapter_roman_pattern = re.compile(r'^([IVXLCDM]+)\.?$')

    # --- STATE AND DATA COLLECTION ---
    header_metadata = {}
    content_records = []
    license_text = []
    content_headers = []
    paragraph_buffer = []

    # State variables
    current_work = "Unknown Work"
    current_chapter_roman = None
    current_chapter_title = None
    paragraph_counter = 0
    in_header = True
    in_contents = False
    capturing_license = False
    expecting_chapter_title = False

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

            # --- Check for end of book marker ---
            if "*** END OF THE PROJECT GUTENBERG EBOOK" in stripped_line:
                break

            # --- Phase 2: Learn structure from "Contents" section ---
            if stripped_line == "CONTENTS":
                in_contents = True
                continue
            
            if in_contents:
                if stripped_line.startswith("CHAPTER"):
                    content_headers.append(stripped_line)
                # Assume the contents section ends with a blank line before the main text
                elif not stripped_line:
                    in_contents = False
                continue

            # --- Phase 3: Process Document Content ---
            chapter_roman_match = chapter_roman_pattern.match(stripped_line)
            if chapter_roman_match:
                # Process any buffered paragraph from the previous chapter
                if paragraph_buffer:
                    paragraph_text = " ".join(paragraph_buffer)
                    paragraph_counter += 1
                    content_records.append({
                        "work": current_work,
                        "chapter_roman": current_chapter_roman,
                        "chapter_title": current_chapter_title,
                        "paragraph": paragraph_counter,
                        "text": paragraph_text
                    })
                    paragraph_buffer = []

                current_chapter_roman = roman_to_int(chapter_roman_match.group(1))
                # The title is expected on the *next* non-blank line.
                expecting_chapter_title = True
                # Reset paragraph counter for the new chapter
                paragraph_counter = 0
                continue

            if expecting_chapter_title and stripped_line:
                current_chapter_title = stripped_line
                expecting_chapter_title = False
                continue

            # If we are in a content section, buffer lines until a blank line
            if current_chapter_roman is not None and current_chapter_title is not None:
                if stripped_line:
                    paragraph_buffer.append(stripped_line)
                else:
                    # A blank line indicates a paragraph break.
                    if paragraph_buffer:
                        paragraph_text = " ".join(paragraph_buffer)
                        paragraph_counter += 1
                        content_records.append({
                            "work": current_work,
                            "chapter_roman": current_chapter_roman,
                            "chapter_title": current_chapter_title,
                            "paragraph": paragraph_counter,
                            "text": paragraph_text
                        })
                        paragraph_buffer = []

    # --- Finalization and File Writing ---
    # Process any remaining paragraph in the buffer before writing files
    if paragraph_buffer:
        paragraph_text = " ".join(paragraph_buffer)
        paragraph_counter += 1
        content_records.append({
            "work": current_work,
            "chapter_roman": current_chapter_roman,
            "chapter_title": current_chapter_title,
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

    update_processed_status(source_filename, file_hash)

if __name__ == '__main__':
    process_philo(
        source_path='source_material/pg14657.txt',
        processed_dir='processed_corpus'
    )