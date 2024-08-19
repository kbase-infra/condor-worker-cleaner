import os
import logging
import docker
import psutil
import requests

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
#
# If a container does not have a corresponding process
# running on the host, the script sends a message to
# the specified Slack webhook.
# -----------------------------------------------

logging.basicConfig(level=logging.DEBUG)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
if SLACK_WEBHOOK_URL is None:
    exit("SLACK_WEBHOOK_URL environment variable is not set.")

# Initialize Docker client to interact with Docker API
client = docker.from_env()


def send_slack_message(container_name, job_id):
    """
    Sends a message to Slack if a container with the specified job ID
    has no corresponding process running on the host.

    Parameters:
    - container_name: Name of the Docker container
    - job_id: Job ID of the Docker container
    """
    message = {
        "text": f"Container {container_name} with job ID {job_id} has no corresponding process running on the host."
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
    return any(job_id in proc.info['cmdline'] for proc in psutil.process_iter(['cmdline']))


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
            if job_id and not has_running_process(job_id):
                logging.warning(f"Container {container.name} with job ID {job_id} has no corresponding process.")
                send_slack_message(container.name, job_id)
            else:
                logging.info(f"Container {container.name} with job ID {job_id} has a corresponding process.")


if __name__ == "__main__":
    check_docker_containers()
