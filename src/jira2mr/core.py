import git
import gitlab
from atlassian import Jira
import re

# ---------------------
# JIRA Helpers
# ---------------------

def jira_auth(config, verifySSL):
    """
    Authenticates to Jira using provided config credentials.

    Args:
        config (ConfigParser): Loaded configuration
        verifySSL (bool): Whether to verify SSL certs

    Returns:
        Jira: Authenticated Jira client object
    """

    jira = Jira(
        url=config['JIRA']['ProjectURL'],
        username=config['JIRA']['Username'],
        password=config['JIRA']['Token'],
        verify_ssl=verifySSL
    )

    return jira

def convert_jira_to_markdown(text):
    """
    Cleans Jira text for use in GitLab markdown by removing Jira-specific formatting.

    Args:
        text (str): Raw Jira description or summary.

    Returns:
        str: Cleaned markdown-compatible text.
    """
    if not text:
        return ""
    
    text = re.sub(r"\{color:[^}]+\}(.*?)\{color\}", r"\1", text)  # Remove color tags
    return text


def get_jira_issue(jira, issue_key, jira_url):
    """
    Fetches issue data from Jira, including parent details if it is a subtask.

    Args:
        jira (Jira): Authenticated Jira client
        issue_key (str): Key of the Jira issue (e.g. "PROJ-123")
        jira_url (str): Base URL of the Jira instance

    Returns:
        dict: Issue details including key, summary, description, parent info, and link
    """
    issue = jira.issue(issue_key)
    parent_issue = None
    if "parent" in issue["fields"]:
        parent_key = issue["fields"]["parent"]["key"]
        parent_issue = jira.issue(parent_key)
    
    return {
        "key": issue["key"],
        "summary": issue["fields"]["summary"],
        "description": convert_jira_to_markdown(issue["fields"].get("description", "")),
        "parent_summary": convert_jira_to_markdown(parent_issue["fields"]["summary"]) if parent_issue else "",
        "parent_description": convert_jira_to_markdown(parent_issue["fields"].get("description", "")) if parent_issue else "",
        "jira_link": f"{jira_url}browse/{issue['key']}"
    }

# ---------------------
# Git Operations
# ---------------------

def manage_git_branch(repo, issue_key):
    """
    Creates a new feature branch from main based on the Jira issue key.

    Args:
        repo (git.Repo): Local Git repo object
        issue_key (str): Jira issue key used to name the branch

    Returns:
        str: Name of the new branch
    """
    main_branch = "main"
    new_branch = f"feature/{issue_key}"
    
    repo.git.checkout(main_branch)
    repo.git.pull()
    repo.git.checkout("-b", new_branch)
    repo.git.push("origin", new_branch, set_upstream=True)
    
    return new_branch

def create_gitlab_mr(gl, project_id, source_branch, issue):
    """
    Creates a GitLab merge request from the given branch with Jira issue info.

    Args:
        gl (gitlab.Gitlab): Authenticated GitLab client
        project_id (int): ID of the GitLab project
        source_branch (str): Branch name to merge from
        issue (dict): Jira issue details

    Returns:
        str: URL of the created merge request
    """
    project = gl.projects.get(project_id)
    description = f"{issue['description']}\n\n"
    if issue['parent_summary']:
        description += f"**Parent Story:**\n##{issue['parent_summary']}\n{issue['parent_description']}"
    
    description += f"\n\nJira issue link: {issue['jira_link']}"
    
    mr = project.mergerequests.create({
        "source_branch": source_branch,
        "target_branch": "main",
        "title": f"Draft: {issue['summary']}",
        "description": description,
        "draft": True,
        "remove_source_branch": True
    })
    return mr.web_url

def get_gitlab_project_id(gl, repo):
    """
    Extracts the GitLab project ID from the remote Git URL.

    Args:
        gl (gitlab.Gitlab): Authenticated GitLab client
        repo (git.Repo): Local Git repo object

    Returns:
        int: Project ID from GitLab
    """
    remote_url = repo.remotes.origin.url

    if remote_url.startswith("git@"):
        # SSH URL: git@gitlab.com:namespace/project.git
        path = remote_url.split(":")[-1]
    elif remote_url.startswith("http"):
        # HTTP(S) URL: https://gitlab.com/namespace/project.git
        path = remote_url.split("/", 3)[-1]
    else:
        raise ValueError("Unsupported Git remote URL format")

    project_path = path.rstrip(".git")  # Remove .git suffix if present

    # Fetch project details from GitLab
    project = gl.projects.get(project_path)
    return project.id