# Jira2MR: Automate Merge Requests from JIRA to GitLab

## Overview
Jira2MR is a Python script that automates the creation of GitLab Merge Requests (MRs) using a JIRA ticket ID. It streamlines the development workflow by generating branches, setting up MRs with appropriate titles and descriptions, and linking back to the JIRA ticket.

## Installation

### 1. Clone the Repository
Ensure you clone this repository inside your home folder:
```sh
cd ~
git clone <repository_url> jira2mr
```

### 2. Install Dependencies
Navigate to the `jira2mr` directory and install required Python libraries:
```sh
cd ~/jira2mr
pip install -r requirements.txt
```

### 3. Configure the Project
Create a `config.ini` file in the `jira2mr` directory based on the provided `example_config.ini`:

#### Example `config.ini`:
```ini
[JIRA]
Token = jira-token
ProjectURL = jira-project-url
Username = jira-username
ProjectKey = jira-project-key

[GITLAB]
URL = https://gitlab.com
Token = your-gitlab-token

[SETTINGS]
VerifySSL = true
```
Replace the values with you actual credentials and project settings. Put the VerifySSL to no if you have problems with SSL verification, such as in an internal network.

## Usage
Run the script from the repository where you are working. For example, if your working directory is `~/working_repo`, execute:
```sh
cd ~/working_repo
python ../jira2mr/jira2mr.py <JIRA_TICKET_ID>
```
Example:
```sh
python ../jira2mr/jira2mr.py TICKET-481
```

## Behavior
- If the JIRA ticket is a **Story**, the script:
  - Creates a new branch `feature/<JIRA_TICKET_ID>`.
  - Uses the ticket summary as the MR title.
  - Sets the ticket description as the MR description.
- If the JIRA ticket is a **Sub-task**, the script:
  - Includes the parent Story's content in the MR description.
- A link to the JIRA ticket is appended at the end of the MR description.

## Notes
- Ensure your `config.ini` is correctly set up before running the script.
- The script requires valid JIRA and GitLab API tokens with appropriate permissions.

## License
This project is licensed under [MIT License](LICENSE.txt).

## Contributions
Feel free to submit issues or pull requests to improve the project!

