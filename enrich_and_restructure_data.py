import json
import os
import re
from collections import defaultdict

def create_shortname(name):
    """Creates a short, filesystem-friendly name."""
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r'[\s\W]+', '-', name.lower())
    return name.strip('-')

def process_files():
    """
    Processes JSONL and JSON files to enrich content data with metadata,
    restructure it, and create chapter-level aggregations.
    """
    input_dir = 'processed_corpus'
    output_dir = 'processed_corpus_enriched'
    verse_dir = os.path.join(output_dir, 'content_verse')
    paragraph_dir = os.path.join(output_dir, 'content_paragraph')
    chapter_dir = os.path.join(output_dir, 'content_chapter')

    # Create output directories if they don't exist
    os.makedirs(verse_dir, exist_ok=True)
    os.makedirs(paragraph_dir, exist_ok=True)
    os.makedirs(chapter_dir, exist_ok=True)

    # --- 1. Load all header files into memory ---
    headers = {}
    for filename in os.listdir(input_dir):
        if filename.endswith('_header.json'):
            with open(os.path.join(input_dir, filename), 'r') as f:
                header_data = json.load(f)
                content_filename = header_data.get('content_filename')
                if content_filename:
                    headers[content_filename] = header_data

    # --- 2. Process each content file ---
    for filename, header in headers.items():
        input_path = os.path.join(input_dir, filename)
        if not os.path.exists(input_path):
            print(f"Warning: Content file {filename} not found. Skipping.")
            continue

        print(f"Processing {filename} for verse/paragraph and chapter schemas...")

        # Data structures for aggregation
        chapter_aggregator = defaultdict(lambda: {'content': [], 'metadata': {}})

        with open(input_path, 'r') as infile:
            # Determine schema from the first line
            try:
                first_line = infile.readline()
                if not first_line:
                    continue
                infile.seek(0)
                sample_data = json.loads(first_line)
                is_verse_schema = 'verse' in sample_data
            except (json.JSONDecodeError, IndexError):
                print(f"Could not determine schema for {filename}. Skipping.")
                continue

            # Define output paths
            granular_output_path = os.path.join(verse_dir if is_verse_schema else paragraph_dir, filename)
            chapter_output_path = os.path.join(chapter_dir, filename)

            with open(granular_output_path, 'w') as granular_outfile:
                for line in infile:
                    try:
                        content_data = json.loads(line)
                        enriched_data = {}
                        source_shortname = create_shortname(header.get('source_filename', 'unknown'))

                        # --- Enrich and write granular (verse/paragraph) data ---
                        enriched_data['source_title'] = header.get('title')
                        enriched_data['author'] = header.get('author')
                        enriched_data['language'] = header.get('language', 'en')
                        if enriched_data['language'].lower() == 'english':
                            enriched_data['language'] = 'en'

                        if is_verse_schema:
                            book_short = create_shortname(content_data.get('book', ''))
                            chapter = content_data.get('chapter', '')
                            verse = content_data.get('verse', '')
                            enriched_data['id'] = f"{source_shortname}-{book_short}-{chapter}-{verse}"
                            enriched_data['work'] = "The Bible"
                            enriched_data['book'] = content_data.get('book')
                            enriched_data['chapter'] = chapter
                            enriched_data['verse'] = verse
                            chapter_key = (enriched_data['work'], enriched_data['book'], enriched_data['chapter'])
                        else: # Paragraph schema
                            work_short = create_shortname(content_data.get('work', ''))
                            chapter_num = content_data.get('chapter_roman', content_data.get('chapter', ''))
                            paragraph = content_data.get('paragraph', '')
                            enriched_data['id'] = f"{source_shortname}-{work_short}-{chapter_num}-{paragraph}"
                            enriched_data['work'] = content_data.get('work')
                            if content_data.get('book'): enriched_data['book'] = content_data.get('book')
                            if content_data.get('chapter_roman'): enriched_data['chapter_roman'] = content_data.get('chapter_roman')
                            if content_data.get('chapter_title'): enriched_data['chapter_title'] = content_data.get('chapter_title')
                            if content_data.get('chapter'): enriched_data['chapter'] = content_data.get('chapter')
                            enriched_data['paragraph'] = paragraph
                            chapter_key = (enriched_data['work'], enriched_data.get('book', '-'), enriched_data.get('chapter', chapter_num))

                        enriched_data['content'] = content_data.get('text')
                        granular_outfile.write(json.dumps(enriched_data) + '\n')

                        # --- Aggregate data for chapter-level document ---
                        chapter_aggregator[chapter_key]['content'].append(content_data.get('text', ''))
                        if not chapter_aggregator[chapter_key]['metadata']: # Store metadata once
                            chapter_aggregator[chapter_key]['metadata'] = enriched_data

                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from line in {filename}: {line.strip()}")
                        continue

            # --- Write aggregated chapter data ---
            with open(chapter_output_path, 'w') as chapter_outfile:
                for key, data in chapter_aggregator.items():
                    chapter_doc = data['metadata'].copy()
                    # Remove verse/paragraph specific fields
                    chapter_doc.pop('verse', None)
                    chapter_doc.pop('paragraph', None)
                    # Create new chapter-level ID and content
                    chapter_doc['id'] = f"{create_shortname(chapter_doc['source_title'])}-{create_shortname(key[1])}-{key[2]}"
                    chapter_doc['content'] = " ".join(data['content'])
                    chapter_outfile.write(json.dumps(chapter_doc) + '\n')

        print(f"Finished processing {filename}. Granular output at {granular_output_path}, Chapter output at {chapter_output_path}")

if __name__ == '__main__':
    process_files()
    print("\nData enrichment, restructuring, and aggregation complete.")