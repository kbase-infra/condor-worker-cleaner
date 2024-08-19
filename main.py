import logging
import os
from datetime import datetime, timezone
from slack import send_slack_message
from process_checker import has_running_process
from container_manager import kill_container, get_docker_client
from tracker import load_tracker, save_tracker

logging.basicConfig(level=logging.INFO)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
if SLACK_WEBHOOK_URL is None:
    exit("SLACK_WEBHOOK_URL environment variable is not set.")


def get_container_running_time(container):
    """
    Calculate how long the container has been running in days.

    Parameters:
    - container: The Docker container object

    Returns:
    - int: The number of days the container has been running
    """
    start_time_str = container.attrs['State']['StartedAt']
    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    current_time = datetime.now(timezone.utc)
    running_time = current_time - start_time
    return running_time.days


def check_docker_containers():
    """
    Iterates through all running Docker containers and checks if those with the
    'ee2_endpoint' label have a corresponding process running on the host.

    If a container has no matching process, it tracks the job ID and only sends
    a Slack notification and deletes the container after 3 consecutive runs.
    """
    tracker = load_tracker()
    client = get_docker_client()

    for container in client.containers.list(all=False):  # Check only running containers
        labels = container.labels
        if 'ee2_endpoint' in labels:
            job_id = labels.get('job_id')
            app_id = labels.get('app_id')
            hostname = labels.get('worker_hostname')
            container_id = container.id
            running_days = get_container_running_time(container)

            if job_id:
                if not has_running_process(job_id):
                    tracker[job_id] = tracker.get(job_id, 0) + 1

                    logging.warning(f"Container ID: {container_id}, App ID: {app_id}, Job ID: {job_id} "
                                    f"has no corresponding process ({tracker[job_id]}/3). "
                                    f"Container has been running for {running_days} days.")

                    if tracker[job_id] >= 3:
                        kc = kill_container(container_id)
                        send_slack_message(SLACK_WEBHOOK_URL, container_id, job_id, hostname, app_id, kc, running_days)
                        del tracker[job_id]  # Remove from tracker after 3rd failure
                else:
                    if job_id in tracker:
                        del tracker[job_id]  # Remove from tracker if process found
                    logging.debug(f"Container ID: {container_id}, App ID: {app_id}, Job ID: {job_id} "
                                  f"has a corresponding process. Container has been running for {running_days} days.")

    save_tracker(tracker)


if __name__ == "__main__":
    check_docker_containers()
