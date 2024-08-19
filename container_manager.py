import os

import docker
import logging
import time

KILL_CONTAINER = os.environ.get("KILL_CONTAINER", "false").lower() == "true"

def get_docker_client():
    """
    Initialize Docker client to interact with Docker API
    """
    return docker.from_env()

def kill_container(container_id, retries=3, delay=5):
    """
    Attempts to stop and remove a Docker container. Retries up to a specified
    number of times with a delay between attempts.

    Parameters:
    - container_id: ID of the Docker container to stop
    - retries: Number of retry attempts
    - delay: Delay between retry attempts in seconds

    Returns:
    - bool: True if the container was successfully stopped and removed, False otherwise
    """
    if KILL_CONTAINER:
        client = get_docker_client()
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
