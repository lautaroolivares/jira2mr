import configparser
import sys
import git
import gitlab
from pathlib import Path
import configparser
import sysconfig
from jira2mr.core import (
    jira_auth, get_jira_issue, manage_git_branch,
    get_gitlab_project_id, create_gitlab_mr
)

CONFIG_DIR = Path.home() / ".jira2mr"
CONFIG_PATH = CONFIG_DIR / "config.ini"
# ---------------------
# Configuration Handling
# ---------------------

def load_config():
    """
    Loads configuration from conf/config.ini file.
    Returns:
        configparser.ConfigParser object
    """
    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        data_dir = Path(sysconfig.get_paths()["data"]) / "share" / "jira2mr"
        example_file = data_dir / "config.ini.example"

        if not example_file.exists():
            raise FileNotFoundError(f"Could not find bundled example config at {example_file}")
        print(f"Config created at {CONFIG_PATH}. Fill it in before running again.")
        exit(1)

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

# ---------------------
# Entry Point
# ---------------------

def main():
    """
    Main function to coordinate the full flow: Jira → Git → GitLab MR

    Args:
        issue_key (str): Jira issue key (e.g., "PROJ-123")
    """
    if len(sys.argv) != 2:
        print("Usage: jira2mr <JIRA-ISSUE-KEY>")
        sys.exit(1)

    issue_key = sys.argv[1]
    config = load_config()

    verifySSL = config.getboolean("SETTINGS", "VerifySSL")

    # Initialize clients
    jira = jira_auth(config, verifySSL)
    gl = gitlab.Gitlab(config["GITLAB"]["URL"], private_token=config["GITLAB"]["Token"], ssl_verify = verifySSL)
    repo = git.Repo(".")
    
    issue = get_jira_issue(jira, issue_key, config["JIRA"]["ProjectURL"])
    new_branch = manage_git_branch(repo, issue["key"])
    project_id = get_gitlab_project_id(gl, repo)
    mr_url = create_gitlab_mr(gl, project_id, new_branch, issue)
    
    print(f"Merge request created: {mr_url}")

# Run script from command line

if __name__ == "__main__":
    main()