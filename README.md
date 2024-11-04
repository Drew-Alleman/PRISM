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

## TODO
* Finish Google() Class
* Other Google Authentication methods
* Build a framework for handling arguments and building the log_entries from the provided file
* Create email sender class and build script to send warnings to recipents
* Create documentation for each library
* Finish README
* Improve report generation
* Django Website (idk)

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

## Setting up the Service Account
### Creating a new Project
Log in to your Google Workspace Admin account and navigate to the Google Cloud Console. Click on the "Select a project" button in the top left corner, then choose "New Project" to create a new one. Feel free to name it anything you like.
![image](https://github.com/user-attachments/assets/7b0db779-b36e-489c-9206-2096a235d0e8)

### Enabling the Needed API's
Now We need to enable the GMAIL and Admin API to manage emails and users.
![image](https://github.com/user-attachments/assets/ac078bfc-b43c-4822-a771-6ee7d613b3b3)
![image](https://github.com/user-attachments/assets/139a51af-b6b1-4b6b-b3ad-83d5df6699a8)
![image](https://github.com/user-attachments/assets/88e2b8fa-8130-4238-8a3b-309e9abacddd)
![image](https://github.com/user-attachments/assets/49d2b98f-d192-4650-be11-f046ab950e18)

## Generating the JSON Secret File
Now we need to generate the JSON secret file to allow PRISM to authenticate to Google.
![image](https://github.com/user-attachments/assets/46e7cd4d-538f-48f6-b08d-3b13ca85599e)
![image](https://github.com/user-attachments/assets/21d144e3-3f68-41da-8f55-b874af920a72)
![image](https://github.com/user-attachments/assets/eb4d7366-e54e-4a85-b860-3b9597c4cd1e)
![image](https://github.com/user-attachments/assets/6f4bc577-9abb-40ac-9192-adbed0c3d08f)
![image](https://github.com/user-attachments/assets/e2a1ba08-9b14-4264-94c4-8094cc3d20da)
![image](https://github.com/user-attachments/assets/475dc088-c8b1-4568-aab8-913205ce4526)
## Configuring the Scopes and Delegation
![image](https://github.com/user-attachments/assets/57196a6a-ef6e-41c7-bbf1-b992c4fd8a1c)
![image](https://github.com/user-attachments/assets/b35902a2-c6fb-430a-b1a7-129ad13f20d9)
![image](https://github.com/user-attachments/assets/332bdb35-d05c-4dcc-a14a-0db89d948393)

Now we need to paste the client ID we copied from the cloud console and we need to input the following scopes
- https://www.googleapis.com/auth/admin.directory.user
- https://mail.google.com/

![image](https://github.com/user-attachments/assets/e38ba6e9-0386-4608-bae9-c26fefa228ac)

