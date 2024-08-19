# Condor Worker Cleaner

## Overview
This script is designed to ensure that Docker containers running on the host machine have corresponding processes. If a container does not have an associated process, a notification will be sent via Slack.

## Environment Variables
The following environment variables are expected to be set for the script to function properly:

- `SLACK_WEBHOOK_URL`: The URL for the Slack webhook to send notifications.

## Container Labels
The script checks containers with the following labels:

- `ee2_endpoint`: Identifies KBase containers.
- `job_id`: Identifies the job ID of the container.
- `worker_hostname`: Identifies the worker hostname.
- `app_id`: Identifies the app ID of the container.

## Functionality
The script operates as follows:

1. **Process Verification**: 
   - It checks if each Docker container has a corresponding process running on the host machine.

2. **Notification**:
   - If a container is found without a corresponding process, the script sends a notification to the specified Slack webhook.

## Example
The script can be run as part of a Kubernetes CronJob or another scheduled task to ensure ongoing monitoring of Docker containers.

