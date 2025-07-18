import os
import json

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

def reconstruct_text(jsonl_path, output_path):
    """
    Reconstructs a text file from a structured JSONL file to validate
    the parsing process.
    """
    if not os.path.exists(jsonl_path):
        print(f"Error: Input file not found at '{jsonl_path}'")
        return

    print(f"Reconstructing from '{jsonl_path}'...")

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Track the last seen book/chapter to know when to print headers
    last_book = None
    last_chapter = None

    with open(jsonl_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        for line in infile:
            record = json.loads(line)
            
            book = record.get('book')
            chapter = record.get('chapter')
            paragraph = record.get('paragraph')
            text = record.get('text')

            # --- Print Book Header ---
            if book != last_book:
                if last_book is not None:
                    outfile.write('\n\n\n') # Add space between books
                
                if book == "Preface":
                    outfile.write("PREFACE\n")
                else:
                    outfile.write(f"BOOK {book}.\n")
                
                last_book = book
                last_chapter = None # Reset chapter when book changes

            # --- Print Chapter or Footnotes Header ---
            if chapter != last_chapter:
                outfile.write('\n\n') # Add space before chapter/footnotes
                
                if chapter == "Footnotes":
                    # Reconstruct the specific footnote header format
                    if last_book == "Preface":
                         outfile.write("WAR PREFACE FOOTNOTES\n")
                    else:
                         outfile.write(f"WAR BOOK {roman_to_int(last_book)} FOOTNOTES\n")
                elif chapter != "Preface": # Preface doesn't have a separate chapter header
                    outfile.write(f"CHAPTER {chapter}.\n")
                
                last_chapter = chapter
                outfile.write('\n')

            # --- Print the Paragraph ---
            # Reconstruct the original paragraph format "1. Some text..."
            outfile.write(f"{paragraph}. {text}\n")

    print(f"Reconstruction complete. Output saved to '{output_path}'")


if __name__ == '__main__':
    # Define the input and where to save the reconstructed file
    source_jsonl = 'processed_corpus/pg2850_content.jsonl'
    reconstructed_output = 'reconstructed/pg2850_reconstructed.txt'
    
    reconstruct_text(source_jsonl, reconstructed_output)