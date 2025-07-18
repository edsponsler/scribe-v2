import os
import re
import json
from datetime import datetime, timezone

# Import our Firestore tracker functions
from scripts.firestore_tracker import get_file_hash, check_if_processed, update_processed_status

# [cite_start]A complete set of book titles from the KJV table of contents. [cite: 18, 19, 20, 21, 22]
KJV_BOOKS = {
    "The First Book of Moses: Called Genesis", "The Second Book of Moses: Called Exodus",
    "The Third Book of Moses: Called Leviticus", "The Fourth Book of Moses: Called Numbers",
    "The Fifth Book of Moses: Called Deuteronomy", "The Book of Joshua", "The Book of Judges",
    "The Book of Ruth", "The First Book of Samuel", "The Second Book of Samuel",
    "The First Book of the Kings", "The Second Book of the Kings",
    "The First Book of the Chronicles", "The Second Book of the Chronicles", "Ezra",
    "The Book of Nehemiah", "The Book of Esther", "The Book of Job", "The Book of Psalms",
    "The Proverbs", "Ecclesiastes", "The Song of Solomon", "The Book of the Prophet Isaiah",
    "The Book of the Prophet Jeremiah", "The Lamentations of Jeremiah",
    "The Book of the Prophet Ezekiel", "The Book of Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
    "Malachi", "The Gospel According to Saint Matthew", "The Gospel According to Saint Mark",
    "The Gospel According to Saint Luke", "The Gospel According to Saint John",
    "The Acts of the Apostles", "The Epistle of Paul the Apostle to the Romans",
    "The First Epistle of Paul the Apostle to the Corinthians",
    "The Second Epistle of Paul the Apostle to the Corinthians",
    "The Epistle of Paul the Apostle to the Galatians",
    "The Epistle of Paul the Apostle to the Ephesians",
    "The Epistle of Paul the Apostle to the Philippians",
    "The Epistle of Paul the Apostle to the Colossians",
    "The First Epistle of Paul the Apostle to the Thessalonians",
    "The Second Epistle of Paul the Apostle to the Thessalonians",
    "The First Epistle of Paul the Apostle to Timothy",
    "The Second Epistle of Paul the Apostle to Timothy",
    "The Epistle of Paul the Apostle to Titus", "The Epistle of Paul the Apostle to Philemon",
    "The Epistle of Paul the Apostle to the Hebrews", "The General Epistle of James",
    "The First Epistle General of Peter", "The Second General Epistle of Peter",
    "The First Epistle General of John", "The Second Epistle General of John",
    "The Third Epistle General of John", "The General Epistle of Jude",
    "The Revelation of Saint John the Divine"
}

def process_kjv_bible(source_path, processed_dir):
    """
    Parses the Project Gutenberg KJV Bible text file into a structured
    [cite_start]JSONL file, one verse per line, and a separate header metadata file. [cite: 23]
    """
    print(f"Starting processing of {source_path}...")

    # --- IDEMPOTENCY CHECK ---
    source_filename = os.path.basename(source_path)
    file_hash = get_file_hash(source_path)

    if check_if_processed(source_filename, file_hash):
        return

    # --- PREPARE FILENAMES AND METADATA ---
    base_filename = os.path.splitext(source_filename)[0]
    header_output_path = os.path.join(processed_dir, f'{base_filename}_header.json')
    verses_output_path = os.path.join(processed_dir, f'{base_filename}_content.jsonl')

    # --- PROCESSING LOGIC ---
    verse_pattern = re.compile(r'^(\d+):(\d+)\s(.*)')
    
    header_metadata = {}
    verse_records = []
    license_text = []
    current_book = None
    in_header = True
    in_bible_text = False
    capturing_license = False

    with open(source_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()

            if in_header:
                if "This ebook is for the use of anyone anywhere" in stripped_line:
                    capturing_license = True
                
                if capturing_license:
                    license_text.append(stripped_line)
                
                if stripped_line.startswith("Title:"):
                    header_metadata['title'] = stripped_line.split(":", 1)[1].strip()
                elif stripped_line.startswith("Release date:"):
                    header_metadata['release_date'] = stripped_line.split(":", 1)[1].strip().split("[")[0].strip()
                elif stripped_line.startswith("Language:"):
                    header_metadata['language'] = stripped_line.split(":", 1)[1].strip() 
                elif "*** START OF THE PROJECT GUTENBERG EBOOK" in stripped_line:
                    in_header = False
                    capturing_license = False
                continue

            if not stripped_line:
                continue

            if not in_bible_text and stripped_line in KJV_BOOKS: 
                in_bible_text = True
            
            if not in_bible_text:
                continue

            if "*** END OF THE PROJECT GUTENBERG EBOOK" in stripped_line: 
                break

            if stripped_line in KJV_BOOKS:
                current_book = stripped_line
                print(f"  Processing book: {current_book}") 
                continue
            
            match = verse_pattern.match(stripped_line)
            if match:
                chapter, verse, text = match.groups() 
                record = {
                    "book": current_book,
                    "chapter": int(chapter),
                    "verse": int(verse),
                    "text": text 
                }
                verse_records.append(record)
                continue

            if verse_records:
                 verse_records[-1]['text'] += ' ' + stripped_line 

    # --- ADD NEW METADATA FIELDS ---
    header_metadata['source_filename'] = source_filename
    header_metadata['content_filename'] = os.path.basename(verses_output_path)
    header_metadata['processing_date_utc'] = datetime.now(timezone.utc).isoformat()
    header_metadata['license'] = "\n".join(license_text).strip()
    header_metadata['record_count'] = len(verse_records)

    # --- WRITE THE OUTPUT FILES ---
    with open(header_output_path, 'w', encoding='utf-8') as f:
        json.dump(header_metadata, f, indent=2)
    print(f"Header metadata saved to {header_output_path}")

    with open(verses_output_path, 'w', encoding='utf-8') as f:
        for record in verse_records:
            f.write(json.dumps(record) + '\n')
    print(f"{len(verse_records)} verse records saved to {verses_output_path}")

    # --- AFTER all file writing is successful, UPDATE THE TRACKER ---
    update_processed_status(source_filename, file_hash) 

if __name__ == '__main__':
    process_kjv_bible(
        source_path='source_material/pg10.txt',
        processed_dir='processed_corpus'
    )