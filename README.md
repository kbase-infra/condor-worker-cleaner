# Condor Worker Cleaner

## Overview
This script is designed to ensure that Docker containers running on the host machine have corresponding processes. If a container does not have an associated process, a notification will be sent via Slack.

## Environment Variables
The following environment variables are required:

- `SLACK_WEBHOOK_URL`: The URL for the Slack webhook to send notifications.
- `KILL_CONTAINER`: A boolean value that determines whether the script should kill the container if no corresponding process is found. If set to `true`, the script will kill the container. If set to `false`, the script will only send a notification.

## Container Labels
The script checks containers with the following labels:

- `ee2_endpoint`: Identifies KBase containers.
- `job_id`: Identifies the job ID of the container.
- `worker_hostname`: Identifies the worker hostname.
- `app_id`: Identifies the app ID of the container.


## Functionality
The script operates as follows:

1. **Process Verification**: 
   - It checks if each Docker container has at least one corresponding ee2 job runner process running on the host machine.

2. **Notification**:
   - If a container is found without a corresponding process, the script sends a notification to the specified Slack webhook.

3. **Container Kill**:
   - If the `KILL_CONTAINER` environment variable is set to `true`, the script will kill the container.

## Example
The script needs to be deployed as a daemonset. You can change the frequency of the script my modifying run.sh. 
The script is set to run every 60 minutes. So that means that if there is a runaway container after 3 hours (3 checks), it will be deleted.


