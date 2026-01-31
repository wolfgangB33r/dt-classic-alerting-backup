# dt-classic-alerting-backup

Fetches all the classic Dynatrace alerting configs (metric events, alerting profiles and classic problem notifications)

## Prompt

Implement a Python cmd line program that reads a Dynatrace environment URL and a Dynatrace API token as environment variables 
and use the following api to list and download all settings objects into a folder structure where each downloaded settings 
schema is represented as a folder and each settings object is an individual json file.
List objects per settings schema:
'/api/v2/settings/objects?schemaIds=builtin%3Aanomaly-detection.metric-events&fields=objectId%2Cvalue'

Give some progress output on the console about the total number of objects per settings schema and about the download progress of objects.
The settings schemas to download should be configurable through a local config text file.
Start with the following three settings schemas:
- builtin:anomaly-detection.metric-events
- settings/builtin:alerting.profile
- builtin:problem.notifications
- 

