#!/usr/bin/env python3
"""
Dynatrace Settings Objects Downloader

Downloads all settings objects from a Dynatrace environment organized by schema.
Requires environment variables:
  - DYNATRACE_URL: Dynatrace environment URL (e.g., https://your-environment.dynatrace.com)
  - DYNATRACE_API_TOKEN: Dynatrace API token
"""

import os
import json
import sys
from pathlib import Path
from urllib.parse import quote
import requests
from dotenv import load_dotenv


def read_config(config_file: str) -> list:
    """Read schema IDs from config file."""
    schemas = []
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    schemas.append(line)
        print(f"✓ Loaded {len(schemas)} schemas from config file: {config_file}")
        return schemas
    except FileNotFoundError:
        print(f"✗ Config file not found: {config_file}")
        sys.exit(1)


def get_env_variables() -> tuple:
    """Get Dynatrace URL and API token from environment variables."""
    url = os.environ.get('DYNATRACE_URL')
    token = os.environ.get('DYNATRACE_API_TOKEN')

    if not url:
        print("✗ Error: DYNATRACE_URL environment variable not set")
        sys.exit(1)
    if not token:
        print("✗ Error: DYNATRACE_API_TOKEN environment variable not set")
        sys.exit(1)

    # Remove trailing slash if present
    url = url.rstrip('/')

    print(f"✓ Using Dynatrace environment: {url}")
    return url, token


def create_schema_folder(base_dir: str, schema_id: str) -> str:
    """Create folder for schema using schema ID as folder name."""
    # Sanitize schema ID for folder name (replace colons with underscores)
    folder_name = schema_id.replace(':', '_').replace('/', '_')
    schema_folder = os.path.join(base_dir, folder_name)
    Path(schema_folder).mkdir(parents=True, exist_ok=True)
    return schema_folder


def list_settings_objects(url: str, token: str, schema_id: str) -> list:
    """List all settings objects for a given schema ID."""
    # URL encode the schema ID
    encoded_schema = quote(schema_id, safe='')
    api_url = f"{url}/api/v2/settings/objects?schemaIds={encoded_schema}&fields=objectId%2Cvalue"

    headers = {
        'Authorization': f'Api-Token {token}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        objects = data.get('items', [])
        return objects
    except requests.exceptions.RequestException as e:
        print(f"✗ Error listing settings for schema {schema_id}: {e}")
        return []


def download_settings_object(url: str, token: str, object_id: str) -> dict:
    """Download a single settings object."""
    api_url = f"{url}/api/v2/settings/objects/{object_id}"
    headers = {
        'Authorization': f'Api-Token {token}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading object {object_id}: {e}")
        return None


def save_settings_object(schema_folder: str, object_id: str, object_data: dict) -> None:
    """Save settings object as JSON file."""
    # Sanitize object ID for filename
    safe_id = object_id.replace('/', '_').replace(':', '_')
    file_path = os.path.join(schema_folder, f"{safe_id}.json")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(object_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"✗ Error saving object {object_id}: {e}")


def download_schema_objects(
    url: str,
    token: str,
    schema_id: str,
    output_dir: str
) -> int:
    """Download all objects for a schema."""
    print(f"\n📋 Processing schema: {schema_id}")

    # List objects for this schema
    objects = list_settings_objects(url, token, schema_id)
    total_objects = len(objects)

    if total_objects == 0:
        print(f"  ℹ No objects found for this schema")
        return 0

    print(f"  ℹ Found {total_objects} objects to download")

    # Create schema folder
    schema_folder = create_schema_folder(output_dir, schema_id)

    # Download each object
    successful = 0
    for idx, obj in enumerate(objects, 1):
        object_id = obj.get('objectId')
        if not object_id:
            continue

        # Download the full object data
        object_data = download_settings_object(url, token, object_id)
        if object_data:
            save_settings_object(schema_folder, object_id, object_data)
            successful += 1

        # Progress indicator
        if idx % 5 == 0 or idx == total_objects:
            print(f"  ⬇ Downloaded {idx}/{total_objects} objects", end='\r')

    print(f"  ✓ Downloaded {successful}/{total_objects} objects successfully")
    return successful


def main():
    """Main execution function."""
    # Load environment variables from .env file
    load_dotenv()

    print("=" * 60)
    print("Dynatrace Settings Objects Downloader")
    print("=" * 60)

    # Get environment variables
    url, token = get_env_variables()

    # Read config file
    config_file = os.path.join(os.path.dirname(__file__), 'schemas_config.txt')
    schemas = read_config(config_file)

    # Create output directory
    output_dir = 'downloaded_settings'
    Path(output_dir).mkdir(exist_ok=True)
    print(f"✓ Output directory: {os.path.abspath(output_dir)}")

    # Download objects for each schema
    total_downloaded = 0
    successful_schemas = 0

    for schema_id in schemas:
        downloaded = download_schema_objects(url, token, schema_id, output_dir)
        total_downloaded += downloaded
        if downloaded > 0:
            successful_schemas += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  ✓ Schemas processed: {successful_schemas}/{len(schemas)}")
    print(f"  ✓ Total objects downloaded: {total_downloaded}")
    print(f"  ✓ Output location: {os.path.abspath(output_dir)}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
