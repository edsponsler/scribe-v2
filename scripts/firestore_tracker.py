# scripts/firestore_tracker.py
import os
import hashlib
from datetime import datetime, timezone
from google.cloud import firestore

# Initialize the Firestore client.
# When running on Google Cloud services (like Cloud Functions or Cloud Run),
# authentication is handled automatically. For local development, it uses
# the credentials you set up with 'gcloud auth application-default login'.
db = firestore.Client()

# The name of the collection we'll use in Firestore.
COLLECTION_NAME = os.getenv('FIRESTORE_COLLECTION_NAME', 'processed_files_tracker')

def get_file_hash(file_path):
    """Calculates the SHA-256 hash of a file's content."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_if_processed(source_filename, file_hash):
    """
    Checks Firestore to see if a file with the same hash has already been processed.
    The source_filename will be the ID of our document in Firestore.
    """
    doc_ref = db.collection(COLLECTION_NAME).document(source_filename)
    doc = doc_ref.get()

    if doc.exists:
        # The file has been processed before, check if the content has changed.
        if doc.to_dict().get('content_hash') == file_hash:
            print(f"'{source_filename}' is already processed and unchanged. Skipping.")
            return True # File is processed and up-to-date.
    return False # File is new or has been modified.

def update_processed_status(source_filename, file_hash):
    """
    Adds or updates a file's record in Firestore after it has been processed.
    """
    doc_ref = db.collection(COLLECTION_NAME).document(source_filename)
    doc_ref.set({
        'source_filename': source_filename,
        'content_hash': file_hash,
        'processed_at': datetime.now(timezone.utc)
    })
    print(f"Updated tracking status for '{source_filename}' in Firestore.")