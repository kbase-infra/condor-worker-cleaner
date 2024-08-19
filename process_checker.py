import psutil
import logging

def has_running_process(job_id):
    """
    Checks if any running process on the host contains the given job ID
    in its command-line arguments.

    Parameters:
    - job_id: Job ID to search for in process arguments

    Returns:
    - bool: True if a matching process is found, False otherwise
    """
    for proc in psutil.process_iter(['pid', 'cmdline']):
        cmdline = proc.info['cmdline']
        if cmdline is not None and job_id in ' '.join(cmdline):
            logging.debug(f"Matching process found: PID {proc.info['pid']} - CMD: {' '.join(cmdline)}")
            return True
    logging.info(f"No matching process found for job ID: {job_id}")
    return False
