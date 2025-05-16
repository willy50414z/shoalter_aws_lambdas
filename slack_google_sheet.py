from enums.enums import SlackChannel, SlackWebhooks
from service import slack_reaction_svc
import json

from service.slack_svc import SlackService


# def reaction_event(request_body):
# request_body = event.get('body', '')
def reaction_event(event, context):
    request_body = event.get('body', '')
    body = json.loads(request_body)
    print(request_body)
    channel = None

    event_type = body.get("event").get("type")
    reaction = body.get("event").get("reaction")
    for slack_channel in SlackChannel:
        if slack_channel.id == body.get("event").get("item").get(
                "channel"):
            channel = slack_channel
            break
    if event_type == "reaction_added" and reaction == "rabbit-key":
        slack_reaction_svc.add_rabbit_key(channel, body)
    else:
        if channel and event_type == "reaction_added":
            if reaction == "done":
                slack_reaction_svc.add_done(channel, body)
            elif reaction == "test_fail":
                slack_reaction_svc.add_test_fail(channel, body)
            elif reaction == "pass":
                slack_reaction_svc.add_pass(channel, body)
            elif reaction == "backend2-help":
                slack_reaction_svc.add_backend2_help(channel, body)
    return {
        'statusCode': 200,
        'body': "ok"
    }

# if __name__ == '__main__':
#     slack_svc = SlackService()
#     msg = "<@U03D1KMA3RV> This Merge Request has merged. Please continue the other actions.\r\n<https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/business_module/shoalter-ecommerce-business-cart-service/-/merge_requests/1270>"
#     slack_svc.send_webhook_message(slack_webhook=SlackWebhooks.gitlab_build_team1, text=msg)
# with open("E:\\Code\\shoalter_aws_lambdas\\resource\\slack_users_list.json", "r", encoding="utf-8") as file:
#     data = json.load(file)
#
# simple_data = []
# res = {}
# for member in data["members"]:
#     res[member["name"]] = member["id"]
#     # member_simple_data = {"id": member["id"], "team_id": member["team_id"], "name": member["name"]}
#     # if "real_name" in member:
#     #     member_simple_data["real_name"] = member["real_name"]
#     # elif "real_name" in member["profile"]:
#     #     member_simple_data["real_name"] = member["profile"]["real_name"]
#     # simple_data.append(member_simple_data)
# print(res)
# if __name__ == '__main__':
#     request_body = """{
#     "token": "ZDV2mO7Sf6jf9OrOkNfS3mTj",
#     "team_id": "T1PH69YNN",
#     "context_team_id": "T1PH69YNN",
#     "context_enterprise_id": null,
#     "api_app_id": "A085S4TQTHU",
#     "event": {
#         "type": "reaction_added",
#         "user": "U03D1KMA3RV",
#         "reaction": "rabbit-key",
#         "item": {
#             "type": "message",
#             "channel": "C031P32SL91",
#             "ts": "1736481402.423579"
#         },
#         "item_user": "U03D1KMA3RV",
#         "event_ts": "1736482514.002200"
#     },
#     "type": "event_callback",
#     "event_id": "Ev0882EUADL2",
#     "event_time": 1736482514,
#     "authorizations": [
#         {
#             "enterprise_id": null,
#             "team_id": "T1PH69YNN",
#             "user_id": "U03D1KMA3RV",
#             "is_bot": false,
#             "is_enterprise_install": false
#         }
#     ],
#     "is_ext_shared_channel": false,
#     "event_context": "4-eyJldCI6InJlYWN0aW9uX2FkZGVkIiwidGlkIjoiVDFQSDY5WU5OIiwiYWlkIjoiQTA4NVM0VFFUSFUiLCJjaWQiOiJDMDMxUDMyU0w5MSJ9"
# }"""
#     reaction_event(request_body)
