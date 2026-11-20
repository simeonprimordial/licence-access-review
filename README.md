
# Licence & Access Review

A Python-based access governance and SaaS licence auditing tool that helps organisations identify inactive user accounts, unused or unassigned software licences, and potentially over-privileged accounts.

The tool performs monthly reviews of user, licence, and permission records, then generates an Excel report that teams can use to review findings and track remediation.

## Project Overview

Organisations often pay for software licences assigned to inactive users or left unassigned. They may also have accounts with unnecessary administrative privileges.

Manually identifying these issues across multiple applications can be time-consuming.

Licence & Access Review automates the initial review process by analysing structured CSV records and producing a consolidated audit report.

## Features

### 1. Licence Auditing
- Identifies unassigned software licences.
- Detects licences assigned to inactive users.
- Flags accounts that have not logged in within the configured inactivity period.
- Calculates potential monthly savings where licence costs are available.

### 2. Access Auditing
- Identifies privileged accounts.
- Flags dormant administrator accounts.
- Detects privileged access assigned to inactive users.
- Identifies unclassified permission roles.
- Highlights accounts with multiple privileged assignments.

### 3. Excel Reporting
Generates an Excel workbook containing:

- Executive Summary
- Licence Findings
- Access Findings
- Remediation Tracker

Reports include severity indicators, recommendations, and review statuses.

### 4. Historical Audit Trail
- Generates timestamped monthly reports.
- Maintains an audit history CSV.
- Records the number of users reviewed and findings identified in each run.

### 5. Scheduling and Logging
- Supports scheduled execution through Windows Task Scheduler or Linux Cron.
- Records execution activity and errors in a log file.
- Returns a failure exit code when execution fails.

### 6. Configurable Audit Rules
Audit thresholds and role classifications are maintained in:

`config/settings.json`

This allows inactivity periods and permission classifications to be adjusted without modifying the audit logic.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Pandas | Data processing and analysis |
| OpenPyXL | Excel report generation |
| CSV | Input datasets and audit history |
| JSON | Audit configuration |
| Logging | Execution and error tracking |
| Pytest | Testing |
| Git | Version control |

## Project Structure

```text
licence-access-review/
│
├── config/
│   └── settings.json
│
├── data/
│   ├── users.csv
│   ├── licences.csv
│   └── permissions.csv
│
├── logs/
│   └── .gitkeep
│
├── reports/
│   └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── licence_audit.py
│   ├── access_audit.py
│   └── report_generator.py
│
├── tests/
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── run_monthly_review.bat
└── run_monthly_review.sh
```

## Prerequisites

- Python 3.10 or later
- Git
- pip

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/licence-access-review.git
cd licence-access-review
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

Run the application from the project root:

```bash
python main.py
```

The application will:

1. Load the user, licence, and permission datasets.
2. Validate the input records.
3. Execute the licence audit.
4. Execute the access audit.
5. Generate an Excel review workbook.
6. Record the execution in the audit history.
7. Log the execution status.

## Input Data

The project currently uses CSV files as its data source.

### users.csv

Contains user account information.

| Field | Description |
|---|---|
| user_id | Unique user identifier |
| name | User's full name |
| email | User email address |
| department | User department |
| last_login | Most recent login date |
| status | Account status |

### licences.csv

Contains software licence assignments.

| Field | Description |
|---|---|
| licence_id | Unique licence identifier |
| user_id | Assigned user identifier |
| application | Software application |
| plan | Licence plan |
| cost_monthly | Monthly licence cost |
| currency | Cost currency |

An empty user_id indicates an unassigned licence.

### permissions.csv

Contains application permissions and roles.

| Field | Description |
|---|---|
| user_id | User identifier |
| application | Application name |
| role | Assigned role |
| permission_level | Permission classification |

## Configuration

Audit rules are managed through `config/settings.json`.

Example:

```json
{
  "inactive_days": 90,
  "dormant_admin_days": 30,
  "currency": "USD",
  "report_format": "xlsx",
  "standard_roles": [
    "member",
    "developer"
  ],
  "privileged_roles": [
    "admin",
    "global administrator",
    "organization owner",
    "user administrator"
  ],
  "high_privilege_roles": [
    "global administrator",
    "organization owner"
  ]
}
```

- `inactive_days`: Number of days without a login before a user is flagged for review.
- `dormant_admin_days`: Number of days without a login before a privileged account is flagged.
- `standard_roles`: Roles treated as normal access.
- `privileged_roles`: Roles requiring additional scrutiny.
- `high_privilege_roles`: Roles classified as high privilege.

## Generated Reports

Reports are saved in the `reports/` directory.

Example:

```text
reports/
├── monthly_access_review_20261120_080000.xlsx
└── audit_history.csv
```

The Excel workbook provides findings and recommendations for review by the relevant team leads.

The audit history records each execution, including its timestamp, report filename, number of users reviewed, and findings identified.

## Scheduling

### Windows Task Scheduler

The project includes:

`run_monthly_review.bat`

Create a scheduled task with:

- Trigger: Monthly
- Day: First day of the month
- Time: 08:00
- Action: Start `run_monthly_review.bat`

### Linux Cron

The project includes:

`run_monthly_review.sh`

Make it executable:

```bash
chmod +x run_monthly_review.sh
```

Open the cron editor:

```bash
crontab -e
```

Add:

```cron
0 8 1 * * /path/to/licence-access-review/run_monthly_review.sh
```

## Testing

Run the test suite with:

```bash
pytest -v
```

## Security and Operational Considerations

- Do not commit real employee records or sensitive access information to a public repository.
- Use anonymised sample data for demonstrations.
- Protect generated reports because they may contain sensitive account and permission information.
- Review recommendations with the relevant application owners before removing licences or changing permissions.
- The tool identifies potential issues; it does not automatically disable accounts, revoke licences, or modify permissions.
- Missing or unavailable login activity should not automatically be interpreted as evidence of inactivity.

## Current Scope and Limitations

This version uses locally maintained CSV datasets.

It does not currently:
- Connect directly to Microsoft Graph or other SaaS APIs.
- Retrieve live licence assignments.
- Automatically revoke licences or permissions.
- Send reports by email.
- Integrate with an identity governance platform.

These capabilities may be considered as separate future enhancements.

## Future Enhancements

Potential improvements include:

- Microsoft Graph API integration.
- Additional SaaS application connectors.
- Automated email distribution of review reports.
- Approval workflows for remediation.
- Integration with identity governance platforms.

These enhancements are not required for the current project.

## Disclaimer

This tool is designed to support internal IT operations, licence optimisation, and access governance reviews.

All findings should be validated by authorised administrators and relevant application owners before remediation.

## Author

**SimeonOnTheCloud**

GitHub: https://github.com/simeonprimordial
