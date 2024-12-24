import json
import requests

from enums.enums import SlackWebhooks
from service import slack_svc


def pushed_commit(event, context):
    request_body = event.get('body', '')
    body = json.loads(request_body)
    print(request_body)
    commit_message = f"Following commit has been pushed to {request_body["ref"].replace("refs/heads/", "")}\r\n```"
    for commit in body["commits"]:
        commit_message = f"{commit_message}{commit["title"]}\r\n"
    commit_message = f"{commit_message}```"
    print(commit_message)
    slack_svc.send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1, text=commit_message)
    return {
        'statusCode': 200,
        'body': "ok"
    }