import json
import re

from enums.enums import SlackWebhooks
from service.jira_svc import JiraService
from service.slack_svc import SlackService
from util import slack_util, notion_util

pushed_message_branch = ["dev", "staging"]

task_finish_jira_status = ["Pending Review", "Waiting for Test", "In Testing", "Pending for UAT"]

slack_service = SlackService()


def check_jira_status_after_merge_mr(body):
    # send merge request merged and check Jira status
    source_branch = body["object_attributes"]["source_branch"]
    jira_issue_key = source_branch[source_branch.rfind("/") + 1:]
    jira_svc = JiraService()
    issue = jira_svc.findIssueByKey(jira_issue_key)
    if issue:
        if issue.fields.issuetype.subtask:
            if issue.fields.status.name != "完成":
                user_id = slack_service.get_slack_user_id(
                    body["object_attributes"]["last_commit"]["author"]["email"].split("@")[0])
                message = f"<@{user_id}> Please help to update JIRA status\r\n<https://hongkongtv.atlassian.net/browse/{jira_issue_key}>"
                slack_service.send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1, text=message)
        else:
            if issue.fields.status.name not in task_finish_jira_status:
                user_id = slack_service.get_slack_user_id(
                    body["object_attributes"]["last_commit"]["author"]["email"].split("@")[0])
                message = f"<@{user_id}> Please help to update JIRA status\r\n<https://hongkongtv.atlassian.net/browse/{jira_issue_key}>"
                slack_service.send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1, text=message)
            elif issue.fields.status.name == "Pending Review" and body["object_attributes"]["target_branch"] == "dev":
                aa = 0
                # update Jira status to Waiting for Test
                # need to check is merged by me
                # jira_svc.update_status(issue.key, "Waiting for Test")
                # slack_service.send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1,
                #                                    text=f"<@U03D1KMA3RV> JIRA status has updated to [Waiting for Test]\r\n<https://hongkongtv.atlassian.net/browse/{jira_issue_key}>")


def update_notion_status_after_pipeline_finish(issue_key, target_branch):
    # send merge request merged and check Jira status
    print(f"[update_notion_status_after_pipeline_finish] start,issue_key[{issue_key}]target_branch[{target_branch}]")
    if target_branch == "dev" or target_branch == "staging":
        task = notion_util.find_by_ticket_like(issue_key)
        print(f"update notion statuc, sys_code[{task[0]['properties']['System']['select']['name']}]status[{f"{target_branch}-wait_pipeline"}]")
        tasks = notion_util.find_by_system_and_status(task[0]['properties']['System']['select']['name'],
                                                      f"{target_branch}-wait_pipeline")
        print(f"updated tasks[{tasks}]")
        if len(tasks) > 0:
            for task in tasks:
                notion_util.update_task_status(task["id"], target_branch)


def update_notion_status_while_pipeline_running(issue_key, target_branch):
    # send merge request merged and check Jira status
    if target_branch == "dev" or target_branch == "staging":
        task = notion_util.find_by_ticket_like(issue_key)
        if len(task) > 0:
            notion_util.update_task_status(task[0]["id"], "staging-wait_pipeline")


def pushed_commit(event, context):
    request_body = event.get('body', '')
    body = json.loads(request_body)
    print(body)
    slack_svc = SlackService()
    if body["object_kind"] == "merge_request":
        if body["object_attributes"]["action"] == "merge":
            if body["object_attributes"]["target_branch"] not in pushed_message_branch:
                # send merge to dev/staging commits
                message = f"<@{slack_svc.get_slack_user_id(body["object_attributes"]["last_commit"]["author"]["email"].split("@")[0])}> This Merge Request has merged to {body["object_attributes"]["target_branch"]}. Please continue the other actions.\r\n<{body["object_attributes"]["url"]}>"
                print(f"message[{message}]")
                slack_svc.send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1, text=message)
            check_jira_status_after_merge_mr(body)


    elif body["object_kind"] == "push":
        pushed_branch_name = body["ref"].replace("refs/heads/", "")
        if pushed_branch_name in pushed_message_branch:
            project_name = body["project"]["name"]
            commit_message = f"{project_name} has been pushed commits to {pushed_branch_name}\r\n```"
            for commit in body["commits"]:
                commit_message = f"{commit_message}{commit["title"]}\r\n"
            commit_message = f"{commit_message}```"
            SlackService().send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1, text=commit_message)
    elif body["object_kind"] == "pipeline":
        pushed_branch_name = body["object_attributes"]["ref"]
        if pushed_branch_name in pushed_message_branch:
            status = body["object_attributes"]["status"]
            detailed_status = body["object_attributes"]["detailed_status"]
            # pipeline跑成功後
            if status == "success" and detailed_status == "passed":
                # 發slack通知到gitlab_build_team1 channel
                commit_user = body["commit"]["author"]["email"].split("@")[0]
                slack_svc = SlackService()
                user_id = slack_svc.get_slack_user_id(commit_user)
                commit_message = f"<@{user_id}> {body["project"]["name"]} deploy to {pushed_branch_name} success"
                slack_svc.send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1, text=commit_message)
                # 如果是merge到dev或staging，更新notion Task的status成dev/staging
                match = re.search(r"branch '([^']+)'", body["commit"]["message"])
                if match:
                    branch_name = match.group(1)
                    issue_key = branch_name[branch_name.rfind("/") + 1:]
                    print(f"issue_key[{issue_key}]ref[{body["object_attributes"]["ref"]}]")
                    update_notion_status_after_pipeline_finish(issue_key, body["object_attributes"]["ref"])
            elif status == "running":
                # 如果是merge到dev或staging，更新notion Task的status成dev/staging
                match = re.search(r"branch '([^']+)'", body["commit"]["message"])
                if match:
                    branch_name = match.group(1)
                    issue_key = branch_name[branch_name.rfind("/"):]
                    update_notion_status_while_pipeline_running(issue_key, body["object_attributes"]["ref"])
    return {
        'statusCode': 200,
        'body': "ok"
    }
