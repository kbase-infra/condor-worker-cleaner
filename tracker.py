import pickle
import os

PICKLE_FILE = "job_id_tracker.pkl"

def load_tracker():
    """
    Load the job ID tracker from a pickle file. If the file does not exist,
    initialize an empty dictionary.
    """
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_tracker(tracker):
    """
    Save the job ID tracker to a pickle file.
    """
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(tracker, f)
