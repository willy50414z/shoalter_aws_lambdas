from jira import JIRA, JIRAError


class JiraService:
    def __init__(self):
        jiraOptions = {'server': "https://hongkongtv.atlassian.net/"}
        self.jira = JIRA(options=jiraOptions, basic_auth=(
            "willy.cheng@shoalter.com",
            ""))

    def findIssueByKey(self, issue_key):
        try:
            return self.jira.issue(id=issue_key)
        except JIRAError as e:
            print(f"[findIssueByKey] find jira issue error, e[{e}]")
            return None

    def get_transitions(self, issue_key):
        return self.jira.transitions(issue_key)

    def update_status(self, issue_key, next_status):
        txns = self.get_transitions(issue_key)
        for txn in txns:
            if txn["to"]["name"] == next_status:
                return self.jira.transition_issue(issue_key, txn["id"])
        raise ValueError(f"can't found next_status[{next_status}]")
