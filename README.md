# PRISM - Phishing Reporting and Incident Security Mitigation 
*This project is currently under development.*

These streamlined modules are designed to efficiently mitigate phishing threats across *multiple* Google Workspaces by automaticlly. The system loads and processes data from Google Email Log Search exports, enabling quick detection, analysis, and resolution.

## Example
```python

google_client = Google()
reporter = Reporter()

log_data = load_email_log_search_export('gmail_log.csv')
reporter.generate_report("report.pdf", log_data)

for user in log_data:
    # Attempt to delete the email
    if not google_client.delete_email(user.message_id, user.email):
        print(f"[-] Failed to delete email with ID {user.message_id} in {user.email}'s inbox.")
    
    # Check if the user opened the email and suspend if necessary
    if user.opened_email:
        if not google_client.suspend(user.email):
            print(f"[-] Failed to suspend user: {user.email}")
```

## Features
- **Automated Graphs and Summaries:** Generate insightful graphs and summaries of the provided phishing attack based on exports from Google’s Email Log Search tool. <br>
- **Preset Remediation Scripts:** Quickly delete phishing emails and suspend affected user access with ready-to-use scripts.<br>
- **Incident Response Email Templates:** Use customizable templates to streamline communication with internal and external users about phishing incidents.<br>
- **Suspicious Sign-In Monitoring:** Check phishing victims for recent suspicious sign-ins to assess potential account compromise.<br>
- **Comprehensive Action Logging:** Ensure full transparency with detailed logs of all actions performed by this tool for auditing and accountability.<br>
- **Multi-Instance Google Workspace Processing:** Seamlessly manage multiple Google Workspace environments and perform bulk email deletions across all instances with a single script.<br>
