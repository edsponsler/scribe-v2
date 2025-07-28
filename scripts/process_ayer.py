import os
import re
import json
from datetime import datetime, timezone

from scripts.firestore_tracker import get_file_hash, check_if_processed, update_processed_status

def process_ayer(source_path, processed_dir):
    """
    Parses "A Source Book for Ancient Church History" by Joseph Cullen Ayer.
    It processes the main text, treating each numbered section (§) as a chapter
    and chunking the content within into paragraphs.
    """
    print(f"Starting processing of {source_path}...")

    # --- IDEMPOTENCY CHECK ---
    source_filename = os.path.basename(source_path)
    file_hash = get_file_hash(source_path)
    if check_if_processed(source_filename, file_hash):
        return

    # --- SETUP ---
    base_filename = os.path.splitext(source_filename)[0]
    header_output_path = os.path.join(processed_dir, f'{base_filename}_header.json')
    content_output_path = os.path.join(processed_dir, f'{base_filename}_content.jsonl')

    section_pattern = re.compile(r'^§ (\d+)\. (.*)$')

    # --- STATE AND DATA COLLECTION ---
    header_metadata = {}
    content_records = []
    license_text = []
    paragraph_buffer = []

    # State variables
    current_work = "A Source Book for Ancient Church History"
    current_chapter_number = None
    current_chapter_title = None
    paragraph_counter = 0
    in_main_content = False

    with open(source_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()

            if not in_main_content:
                if stripped_line.startswith("THE FIRST DIVISION OF ANCIENT CHRISTIANITY:"):
                    in_main_content = True
                continue

            if stripped_line.startswith("*** END OF THE PROJECT GUTENBERG EBOOK"):
                break

            # --- Phase 2: Process Document Content ---
            section_match = section_pattern.match(stripped_line)
            if section_match:
                # Process any buffered paragraph from the previous section
                if paragraph_buffer and current_chapter_number is not None:
                    paragraph_text = " ".join(paragraph_buffer).strip()
                    if paragraph_text:
                        paragraph_counter += 1
                        content_records.append({
                            "work": current_work,
                            "chapter": current_chapter_number,
                            "chapter_title": current_chapter_title,
                            "paragraph": paragraph_counter,
                            "text": paragraph_text
                        })
                    paragraph_buffer = []

                current_chapter_number = int(section_match.group(1))
                current_chapter_title = section_match.group(2).strip()
                paragraph_counter = 0
                print(f"  Processing Chapter (Section {current_chapter_number}): {current_chapter_title}")
                continue

            # If we are in a content section, buffer lines until a blank line
            if current_chapter_number is not None:
                if stripped_line:
                    paragraph_buffer.append(stripped_line)
                else:
                    # A blank line indicates a paragraph break.
                    if paragraph_buffer:
                        paragraph_text = " ".join(paragraph_buffer).strip()
                        if paragraph_text:
                            paragraph_counter += 1
                            content_records.append({
                                "work": current_work,
                                "chapter": current_chapter_number,
                                "chapter_title": current_chapter_title,
                                "paragraph": paragraph_counter,
                                "text": paragraph_text
                            })
                        paragraph_buffer = []

    # --- Finalization and File Writing ---
    if paragraph_buffer and current_chapter_number is not None:
        paragraph_text = " ".join(paragraph_buffer).strip()
        if paragraph_text:
            paragraph_counter += 1
            content_records.append({
                "work": current_work,
                "chapter": current_chapter_number,
                "chapter_title": current_chapter_title,
                "paragraph": paragraph_counter,
                "text": paragraph_text
            })

    # --- Create Header ---
    with open(source_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith("Title:"):
                header_metadata['title'] = stripped_line.split(":", 1)[1].strip()
            elif stripped_line.startswith("Author:"):
                header_metadata['author'] = stripped_line.split(":", 1)[1].strip()
            elif stripped_line.startswith("*** START OF THE PROJECT GUTENBERG EBOOK"):
                break

    header_metadata['source_filename'] = source_filename
    header_metadata['content_filename'] = os.path.basename(content_output_path)
    header_metadata['processing_date_utc'] = datetime.now(timezone.utc).isoformat()
    header_metadata['license'] = "The Project Gutenberg License"
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
    process_ayer(
        source_path='source_material/pg24979.txt',
        processed_dir='processed_corpus'
    )