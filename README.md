# Cisco DNA Center Report Downloader

This Python project is designed to interact with Cisco DNA Center's API to authenticate a user, fetch the latest execution of a report based on a specific `reportId`, and download the report as a CSV file. The report is saved to a specified directory, and the report's filename includes the date and time of download.

## Features

- **Authentication**: Uses basic authentication to connect to Cisco DNA Center's API.
- **Report Execution**: Fetches the latest execution of a report where the process and request statuses are `SUCCESS` and `ACCEPT`.
- **CSV Download**: Downloads the report in CSV format and saves it to a specified directory.
- **Custom Output Directory**: Allows specifying a directory to save the downloaded report.

## Requirements

- Python 3.x
- Required Python libraries:
  - `http.client`
  - `json`
  - `csv`
  - `base64`
  - `argparse`
  - `os`
  - `datetime`

You can install the required libraries using `pip`:
```bash
pip install requests
```

## Setup
1. Clone or download the repository.
2. Ensure you have Python 3.x installed on your system.
3. Install required dependencies (as mentioned above).

## Usage
You can run the script from the command line by passing the following arguments:

## Arguments:
- **--host**: Cisco DNA Center hostname or IP address (required).
- **--username**: Cisco DNA Center username for authentication (required).
- **--password**: Cisco DNA Center password for authentication (required).
- **--reportId**: The report ID to retrieve the latest execution of the report (required).
- **--outputDir**: The directory where the report will be saved (required).

## Example:
```bash
python script_name.py --host myhost --username admin --password mypassword --reportId report123 --outputDir C:\Reports
```
