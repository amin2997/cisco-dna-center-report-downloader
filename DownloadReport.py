import os
import http.client
import json
import csv
from base64 import b64encode
from datetime import datetime
import argparse

class CiscoDNACenter:
    def __init__(self, host, username, password, reportId):
        self.host = host
        self.reportId = reportId
        self.token = None
        self.conn = http.client.HTTPSConnection(self.host)
        self.basic_auth = self._generate_basic_auth(username, password)
    
    def _generate_basic_auth(self, username, password):
        """Generate the Basic Auth token."""
        return b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")

    def authenticate(self):
        """Authenticate with Cisco DNA Center and retrieve the API token."""
        headers = {'Authorization': f'Basic {self.basic_auth}'}
        try:
            self.conn.request("POST", "/dna/system/api/v1/auth/token", '', headers)
            res = self.conn.getresponse()
            if res.status != 200:
                raise Exception(f"Authentication failed: {res.status} {res.reason}")
            
            data = json.loads(res.read().decode("utf-8"))
            self.token = data.get("Token")
            print("Authentication successful.")
        except Exception as e:
            print(f"Error during authentication: {e}")

    def _get_authentication_header(self):
        """Return the authentication header with the token."""
        if not self.token:
            raise Exception("No authentication token. Please authenticate first.")
        return {
            'Content-Type': 'application/json',
            'X-Auth-Token': self.token
        }

    def get_latest_execution_id(self):
        """Fetch the latest successful execution ID for the given report."""
        uri = f'/dna/intent/api/v1/data/reports/{self.reportId}/executions'
        try:
            self.conn.request("GET", uri, '', self._get_authentication_header())
            res = self.conn.getresponse()
            if res.status != 200:
                raise Exception(f"Failed to fetch executions: {res.status} {res.reason}")

            data = json.loads(res.read().decode("utf-8"))
            executions = data.get("executions", [])
            # Filter successful and accepted executions
            filtered_executions = [
                execution for execution in executions
                if execution.get("processStatus") == "SUCCESS" and execution.get("requestStatus") == "ACCEPT"
            ]
            # Get the latest execution based on the endTime
            latest_execution = max(filtered_executions, key=lambda x: x["endTime"], default=None)
            if latest_execution:
                print(f"Latest Execution ID: {latest_execution['executionId']}")
                return latest_execution["executionId"]
            else:
                print("No valid executions found.")
                return None
        except Exception as e:
            print(f"Error fetching execution ID: {e}")
            return None

    def download_latest_report(self, filename):
        """Download the latest report based on the latest execution ID."""
        execution_id = self.get_latest_execution_id()
        if not execution_id:
            print("No execution ID found. Cannot download report.")
            return

        uri = f"/dna/intent/api/v1/data/reports/{self.reportId}/executions/{execution_id}"
        try:
            self.conn.request("GET", uri, '', self._get_authentication_header())
            res = self.conn.getresponse()
            if res.status != 200:
                raise Exception(f"Failed to download report: {res.status} {res.reason}")

            data = res.read().decode("utf-8")
            csv_lines = data.split('\n')
            # Remove unwanted header section (first 9 lines)
            cleaned_csv_data = '\n'.join(csv_lines[9:]).strip()        

            # Save the cleaned CSV data to the file
            with open(filename, mode="w", encoding="utf-8", newline="") as file:
                file.write(cleaned_csv_data)

            print(f"Report downloaded and saved as {filename}")
        except Exception as e:
            print(f"Error downloading report: {e}")

def main():
    """Main function to retrieve username, password, and reportId from command-line arguments."""
    """ python DownloadReport.py --host MYHOST --username ADMIN --password myPassword --reportId ReportID123 --outputDir \\shares-cifs.nyumc.org\Groups2\WifiReportDir\ """
    parser = argparse.ArgumentParser(description="Cisco DNA Center Report Downloader")
    parser.add_argument("--host", required=True, help="Cisco DNA Center hostname or IP address")
    parser.add_argument("--username", required=True, help="Username for authentication")
    parser.add_argument("--password", required=True, help="Password for authentication")
    parser.add_argument("--reportId", required=True, help="Report ID to download")
    parser.add_argument("--outputDir", required=True, help="Destination Folder Path to write the write")

    args = parser.parse_args()

    # Create an instance of CiscoDNACenter with the provided arguments
    dnac = CiscoDNACenter(args.host, args.username, args.password, args.reportId)

    # Authenticate and download the latest report
    dnac.authenticate()

    # Ensure outputDir is valid and ends with a slash
    output_dir = args.outputDir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the directory if it doesn't exist

    # Ensure directory ends with the correct slash
    if not output_dir.endswith(os.path.sep):
        output_dir += os.path.sep

     # Generate a dynamic filename with the current date and time                    
    current_datetime = datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")
    filename = os.path.join(output_dir, f"WiFi_Report_{current_datetime}.csv")
    dnac.download_latest_report(filename)


if __name__ == "__main__":
    main()


