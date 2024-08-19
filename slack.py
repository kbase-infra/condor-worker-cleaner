import requests

def send_slack_message(webhook_url, container_id, job_id, hostname, app_id, kc, running_days):
    """
    Sends a message to Slack if a container with the specified job ID
    has no corresponding process running on the host.

    Parameters:
    - webhook_url: Slack webhook URL to send the message to
    - container_id: ID of the Docker container
    - job_id: Job ID of the Docker container
    - hostname: Hostname of the worker running the container
    - app_id: App ID of the Docker container
    - kc: Boolean indicating if the container was killed
    """
    message = {
        "text": f"Container {container_id} with job ID {job_id} has no corresponding process running on the host. "
                f"Hostname: {hostname}. App ID: {app_id}. Container killed: {kc}. Running for {running_days} days."
    }
    requests.post(webhook_url, json=message)
