import os
import logging
import docker
import psutil
import requests
import time

# -----------------------------------------------
# This script checks if a Docker container has a
# corresponding process running on the host machine.
#
# It expects the following environment variables:
# - SLACK_WEBHOOK_URL: The URL for the Slack webhook
#
# The containers should have the following labels:
# - ee2_endpoint: Identifies Kbase containers
# - job_id: Identifies the job ID of the container
# - worker_hostname: Identifies the worker hostname
# - app_id: Identifies the KBase app ID of the container
#
# If a container does not have a corresponding process
# running on the host, the script sends a message to
# the specified Slack webhook.
# -----------------------------------------------

logging.basicConfig(level=logging.INFO)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
if SLACK_WEBHOOK_URL is None:
    exit("SLACK_WEBHOOK_URL environment variable is not set.")

KILL_CONTAINER = os.environ.get("KILL_CONTAINER", "false").lower() == "true"


# Initialize Docker client to interact with Docker API
client = docker.from_env()


def send_slack_message(container_id, job_id, hostname, app_id, kc):
    """
    Sends a message to Slack if a container with the specified job ID
    has no corresponding process running on the host.

    Parameters:
    - container_name: Name of the Docker container
    - job_id: Job ID of the Docker container
    - hostname: Hostname of the worker running the container
    - app_id: App ID of the Docker container
    - kc: Boolean indicating if the container was killed
    """
    message = {
        "text": f"Container {container_id} with job ID {job_id} has no corresponding process running on the host. {hostname}. App ID: {app_id} Container killed: {kc}"
    }
    requests.post(SLACK_WEBHOOK_URL, json=message)


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


def kill_container(container_id, retries=3, delay=5):
    if KILL_CONTAINER:
        for attempt in range(retries):
            try:
                logging.info(f"Stopping container {container_id}")
                container = client.containers.get(container_id)
                container.stop()
                container.remove()
                logging.info(f"Container {container_id} stopped and removed successfully.")
                return True
            except docker.errors.APIError as e:
                logging.error(f"Error stopping container {container_id}: {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(delay)

        logging.error(f"Failed to stop container {container_id} after {retries} attempts.")
        return False
    else:
        return False




def check_docker_containers():
    """
    Iterates through all running Docker containers and checks if those with the
    'ee2_endpoint' label have a corresponding process running on the host.

    If a container has no matching process, a Slack notification is sent.
    """
    for container in client.containers.list(all=False):  # Check only running containers
        labels = container.labels
        if 'ee2_endpoint' in labels:
            job_id = labels.get('job_id')
            app_id = labels.get('app_id')
            if job_id and not has_running_process(job_id):
                logging.warning(f"Container {container.name} with job ID {job_id} has no corresponding process.")
                kc = kill_container(container.id)
                send_slack_message(container.id, job_id, labels.get('worker_hostname'), app_id, kc)
            else:
                logging.debug(f"Container {container.name} with job ID {job_id} has a corresponding process.")


if __name__ == "__main__":
    check_docker_containers()
