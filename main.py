import os

# Import the specific processing functions from our scripts module
from scripts.process_kjv import process_kjv_bible
from scripts.process_josephus import process_josephus

# Define the directories we'll be working with
SOURCE_DIR = 'source_material'
PROCESSED_DIR = 'processed_corpus'

# This dictionary is the core of our controller. It maps a
# specific filename to the function that knows how to process it.
PROCESSOR_MAP = {
    'pg10.txt': process_kjv_bible,
    'pg2850.txt': process_josephus,
    # When you create a processor for Philo, you'll add it here:
    # 'philo_on_creation.txt': process_philo,
}

def main():
    """
    Main function to orchestrate the processing of all source files.
    """
    print("--- Starting SCRIBE v2 Corpus Processing ---")

    # Create the output directory if it doesn't exist
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
        print(f"Created directory: {PROCESSED_DIR}")

    try:
        source_files = os.listdir(SOURCE_DIR)
    except FileNotFoundError:
        print(f"Error: Source directory not found at '{SOURCE_DIR}'. Please create it.")
        return

    # Loop through every file in the source directory
    for filename in source_files:
        if filename in PROCESSOR_MAP:
            # Find the correct processing function from our map
            processor_function = PROCESSOR_MAP[filename]
            source_path = os.path.join(SOURCE_DIR, filename)
            
            # Call the mapped function
            processor_function(source_path, PROCESSED_DIR)
        else:
            print(f"--> WARNING: No processor defined for '{filename}'. Skipping.")
    
    print("\n--- Corpus Processing Complete ---")

if __name__ == '__main__':
    main()