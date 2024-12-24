from enums.enums import SlackChannel
from service import slack_reaction_svc
import json

from util import slack_util


def reaction_event(event, context):
    request_body = event.get('body', '')
    body = json.loads(request_body)
    print(request_body)
    channel = None
    for slack_channel in SlackChannel:
        if slack_channel.id == body.get("event").get("item").get(
                "channel"):
            channel = slack_channel
            break

    if channel and body.get("event").get("type") == "reaction_added":
        if body.get("event").get("reaction") == "done":
            slack_reaction_svc.add_done(channel, body)
        elif body.get("event").get("reaction") == "test_fail":
            slack_reaction_svc.add_test_fail(channel, body)
        elif body.get("event").get("reaction") == "pass":
            slack_reaction_svc.add_pass(channel, body)
        elif body.get("event").get("reaction") == "backend2-help":
            slack_reaction_svc.add_backend2_help(channel, body)
    return {
        'statusCode': 200,
        'body': "ok"
    }
if __name__ == '__main__':
    print(1)