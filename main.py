import logging
import os
from slack import send_slack_message
from process_checker import has_running_process
from container_manager import kill_container, get_docker_client
from tracker import load_tracker, save_tracker

logging.basicConfig(level=logging.INFO)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
if SLACK_WEBHOOK_URL is None:
    exit("SLACK_WEBHOOK_URL environment variable is not set.")

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
            if job_id:
                if not has_running_process(job_id):
                    tracker[job_id] = tracker.get(job_id, 0) + 1

                    logging.warning(f"Container {container.name} with job ID {job_id} has no corresponding process "
                                    f"({tracker[job_id]}/3).")

                    if tracker[job_id] >= 3:
                        kc = kill_container(container.id)
                        send_slack_message(SLACK_WEBHOOK_URL, container.id, job_id, hostname, app_id, kc)
                        del tracker[job_id]  # Remove from tracker after 3rd failure
                else:
                    if job_id in tracker:
                        del tracker[job_id]  # Remove from tracker if process found
                    logging.debug(f"Container {container.name} with job ID {job_id} has a corresponding process.")

    save_tracker(tracker)

if __name__ == "__main__":
    check_docker_containers()
