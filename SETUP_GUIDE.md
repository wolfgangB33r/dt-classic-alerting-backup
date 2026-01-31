# Dynatrace Settings Objects Downloader

A Python command-line tool to download all settings objects from a Dynatrace environment, organized by settings schema.

## Features

- Downloads settings objects from a Dynatrace environment
- Organizes objects by settings schema into separate folders
- Each settings object is saved as an individual JSON file
- Configurable schemas via `schemas_config.txt`
- Real-time progress output during download
- Detailed summary statistics

## Prerequisites

- Python 3.6+
- `requests` library
- `python-dotenv` library

Install dependencies:
```bash
pip install requests python-dotenv
```

## Setup

### 1. Environment Variables

Create a `.env` file in the same directory as `download_settings.py`:

```
DYNATRACE_URL=https://your-environment.dynatrace.com
DYNATRACE_API_TOKEN=your-api-token
```

You can also copy from the provided template:
```bash
cp .env.example .env
```

Then edit `.env` with your actual values.

**Note:** The `.env` file is loaded automatically when the program runs. Keep it secure and do not commit it to version control.

### 2. Configure Settings Schemas

Edit `schemas_config.txt` to specify which settings schemas to download. One schema ID per line.

**Example:**
```
builtin:anomaly-detection.metric-events
builtin:alerting.profile
builtin:problem.notifications
```

Comments (lines starting with `#`) are ignored.

## Usage

Run the script:

```bash
python download_settings.py
```

## Output Structure

Downloaded settings objects are organized as follows:

```
downloaded_settings/
├── builtin_anomaly-detection_metric-events/
│   ├── object-id-1.json
│   ├── object-id-2.json
│   └── ...
├── builtin_alerting_profile/
│   ├── object-id-1.json
│   ├── object-id-2.json
│   └── ...
└── builtin_problem_notifications/
    ├── object-id-1.json
    ├── object-id-2.json
    └── ...
```

## Example Output

```
============================================================
Dynatrace Settings Objects Downloader
============================================================
✓ Using Dynatrace environment: https://your-environment.dynatrace.com
✓ Loaded 3 schemas from config file: schemas_config.txt
✓ Output directory: C:\path\to\downloaded_settings

📋 Processing schema: builtin:anomaly-detection.metric-events
  ℹ Found 12 objects to download
  ⬇ Downloaded 12/12 objects
  ✓ Downloaded 12/12 objects successfully

📋 Processing schema: builtin:alerting.profile
  ℹ Found 5 objects to download
  ⬇ Downloaded 5/5 objects
  ✓ Downloaded 5/5 objects successfully

📋 Processing schema: builtin:problem.notifications
  ℹ Found 8 objects to download
  ⬇ Downloaded 8/8 objects
  ✓ Downloaded 8/8 objects successfully

============================================================
Summary:
  ✓ Schemas processed: 3/3
  ✓ Total objects downloaded: 25
  ✓ Output location: C:\path\to\downloaded_settings
============================================================
```

## Troubleshooting

### "DYNATRACE_URL environment variable not set"
Ensure you've created a `.env` file with `DYNATRACE_URL` set to your environment URL.

### "DYNATRACE_API_TOKEN environment variable not set"
Ensure you've created a `.env` file with `DYNATRACE_API_TOKEN` set to your API token.

### "Config file not found"
Ensure `schemas_config.txt` is in the same directory as `download_settings.py`.

### Connection errors
- Verify your environment URL is correct and accessible
- Verify your API token is valid and has the required permissions
- Check your network connectivity

## Notes

- The API token requires API access and permissions to read settings objects
- The script will create the `downloaded_settings` folder if it doesn't exist
- Schema IDs containing special characters are sanitized when used as folder names (`:` and `/` are replaced with `_`)
- Object IDs containing special characters are sanitized when used as filenames
