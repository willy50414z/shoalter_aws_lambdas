import configparser
import os

from jira import JIRA

jiraOptions = {'server': "https://hongkongtv.atlassian.net/"}

# Print the current working directory (project path)
project_path = os.getcwd()
print("Project path:", project_path)

# Specify the filename or relative path
file_path = os.path.join(project_path, 'application.ini')

# Check if the file exists
if os.path.exists(file_path):
    print("File exists.")
else:
    print("File does not exist.")

config = configparser.ConfigParser()
config.read('../application.ini')
jira = JIRA(options=jiraOptions, basic_auth=(
    config["DEFAULT"]["email"],config["DEFAULT"]["jira_token"]))

incomplete_statuses = ['Done', 'Cancelled', 'Pending UAT', 'Launch Ready', 'Closed']
incomplete_issueTypes = ['Task', 'New Feature', 'Bug', 'Improvement', "Enhancement", "Story"]  # , 'QA Defect'


def get_team1_incompleted_task():
    # assemble filter
    assignees = ['TW - IT - BE - Willy Cheng', 'MarkHuang',
                 'TW - IT - BE - JOHN CHANG', 'TW - IT - BE - Kenny Ma']
    assignee_query = ', '.join([f'"{assignee}"' for assignee in assignees])

    devPICs = ['TW - IT - BE - Willy Cheng', 'MarkHuang',
               'TW - IT - BE - JOHN CHANG', 'TW - IT - BE - Kenny Ma']
    devPIC_query = ', '.join([f'"{devPIC}"' for devPIC in devPICs])

    status_query = ', '.join([f'"{status}"' for status in incomplete_statuses])
    issueType_query = ', '.join([f'"{issueType}"' for issueType in incomplete_issueTypes])

    jql_query = f'("Development PIC" IN ({devPIC_query}) OR assignee IN ({assignee_query})) AND ((status not in ({status_query}) AND issuetype in ({issueType_query})) OR issuetype in ("Sub-task"))'

    # jql_query = f'("Development PIC" IN ({devPIC_query}) OR assignee IN ({assignee_query})) AND ((status not in ({status_query}) AND issuetype in ({issueType_query}))'

    # fetch data
    startIdx = 0
    fetch_size = 100

    issues = jira.search_issues(jql_str=jql_query, maxResults=fetch_size)
    totalSize = issues.total
    allIssues = issues.iterable
    startIdx += fetch_size
    while startIdx < totalSize:
        issues = jira.search_issues(jql_str=jql_query, startAt=startIdx,
                                    maxResults=min(fetch_size, totalSize - startIdx))
        allIssues.extend(issues.iterable)
        startIdx += fetch_size
    return allIssues


def getEERIncompletedTask():
    status_query = ', '.join([f'"{status}"' for status in incomplete_statuses])

    issueType_query = ', '.join([f'"{issueType}"' for issueType in incomplete_issueTypes])

    jql_query = f'Project="EER" AND (status not in ({status_query}) AND type in ({issueType_query}))'

    # jql_query = f'("Development PIC" IN ({devPIC_query}) OR assignee IN ({assignee_query})) AND ((status not in ({status_query}) AND issuetype in ({issueType_query}))'

    # fetch data
    startIdx = 0
    fetch_size = 100

    issues = jira.search_issues(jql_str=jql_query, maxResults=fetch_size)
    totalSize = issues.total
    allIssues = issues.iterable
    startIdx += fetch_size
    while startIdx < totalSize:
        issues = jira.search_issues(jql_str=jql_query, startAt=startIdx,
                                    maxResults=min(fetch_size, totalSize - startIdx))
        allIssues.extend(issues.iterable)
        startIdx += fetch_size
    return allIssues

def findIssueByKey(issueKey):
    try:
        return jira.issue(id=issueKey)
    except Exception as e:
        raise ValueError(f"can't find issue, issue[{issueKey}]e[{e}]")