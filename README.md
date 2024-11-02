# PRISM - Phishing Reporting and Incident Security Mitigation 
*This project is currently under development.*

These streamlined modules and scripts are designed to efficiently mitigate phishing threats across *multiple* Google Workspaces automatically. The system loads and processes data from Google Email Log Search exports, enabling quick detection, analysis, and resolution. Azure support will come in the future. 

## Features
- **Automated Graphs and Summaries:** Generate insightful graphs and summaries of the provided phishing attack based on exports from Google’s Email Log Search tool. <br>
- **Preset Remediation Scripts:** Quickly delete phishing emails and suspend affected user access with ready-to-use scripts.<br>
- **Incident Response Email Templates:** Use customizable templates to streamline communication with internal and external users about phishing incidents.<br>
- **Suspicious Sign-In Monitoring:** Check phishing victims for recent suspicious sign-ins to assess potential account compromise.<br>
- **Comprehensive Action Logging:** Ensure full transparency with detailed logs of all actions performed by this tool for auditing and accountability.<br>
- **Multi-Instance Google Workspace Processing:** Seamlessly manage multiple Google Workspace environments and perform bulk email deletions across all instances with a single script.<br>

## Generating a Report Based on The Export from Google’s Email Log Search tool
```
python .\gmailLogReporter.py --docx 11-2-24-report.docx --logfile .\logSearch-11-2-2024.csv
```
![image](https://github.com/user-attachments/assets/95984b69-0876-4637-a24b-6ccf4634be7b)

## Utilizing the Coding Module Example
```python

google_client = Google()
log_parser = GoogleLogParser()
log_parser.read_exports(["export1.csv", "export2.csv"])

for user in log_parser.get_entries():
    google_client.delete_email(user.message_id, user.email)

    if user.opened_email:
        google_client.suspend(user.email)
```

## Configuration
The Google Python Class is able to automatically determine what authentication to use. All we need to do is fill out `/configurations/config.yaml` with the service account information.
| Field          | Description                                                                                                 | Example Value                      |
|----------------|-------------------------------------------------------------------------------------------------------------|------------------------------------|
| `name`         | A friendly identifier for the Google Workspace instance, used for distinguishing accounts in logs and reports. | `ExampleWorkspace1`               |
| `secret_file`  | The path to the JSON credentials file for the service account, allowing PRISM to authenticate with Google.  | `/path/to/service_account1.json`   |
| `domains`      | A list of domains managed by this workspace. PRISM will use this service account for actions on any of these domains. | `example.com`, `store.example.com` |

```yaml
google_service_accounts:
  - name: ExampleWorkspace1
    secret_file: /path/to/service_account1.json
    domains:
      - example.com
      - store.example.com

  - name: ExampleWorkspace2
    secret_file: /path/to/service_account2.json
    domains:
      - github.com
      - docs.github.com
```

