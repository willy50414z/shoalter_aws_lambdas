import requests

from service import google_sheet_svc, slack_svc
from service.slack_svc import SlackService
from util import datetime_util, google_sheet_util, notion_util, slack_util


def get_user_profile(user_id):
    user_name = user_id
    user_email = user_id
    try:
        user_profile = slack_svc.get_user_profile(user_id)
        user_email = user_profile["profile"]["email"]
        user_name = user_email.split("@")[0]
    except Exception:
        print(f"can't get user profile[{user_id}]")
    return user_email, user_name


def add_done(channel, body):
    msg_ts = int(float(body.get("event").get("item").get("ts"))) + 60 * 60 * 8
    event_time = datetime_util.ts_to_datetime_str(float(body.get("event").get("event_ts")) + 60 * 60 * 8)
    print(f"start update google sheet,channel_name[{channel.channel_name}]msg_time[{msg_ts}][{event_time}]")
    row_idx, total_rows = google_sheet_svc.get_updated_row_idx(channel, msg_ts)
    # update google sheet
    if row_idx:
        RANGE = f"{channel.channel_name}!G{row_idx + 1}:J{row_idx + 1}"
        user_email, user_name = get_user_profile(body.get("event").get("user"))
        res = google_sheet_util.update(channel.sheet_id, RANGE,
                                       {"values": [["QA", "", event_time,
                                                    f"pushed to QA by [{SlackService().get_slack_user_name(user_name)}]"]]})
        print(res.json())
    else:
        print(f"can't find row")


def add_test_fail(slack_channel, body):
    print(f"[add_test_fail]start,channel_name[{slack_channel.channel_name}]")
    msg_ts = int(float(body.get("event").get("item").get("ts"))) + 60 * 60 * 8
    row_idx, total_rows = google_sheet_svc.get_updated_row_idx(slack_channel, msg_ts)
    if row_idx:
        RANGE = f"{slack_channel.channel_name}!G{row_idx + 1}:J{row_idx + 1}"
        user_email, user_name = get_user_profile(body.get("event").get("user"))
        res = google_sheet_util.update(slack_channel.sheet_id, RANGE,
                                       {"values": [["", "", "",
                                                    f"Reopened by [{SlackService().get_slack_user_name(user_name)}]"]]})
        print(res.json())
    else:
        print(f"can't find row")


def add_pass(slack_channel, body):
    print(f"[add_pass]start,channel_name[{slack_channel.channel_name}]")
    msg_ts = int(float(body.get("event").get("item").get("ts"))) + 60 * 60 * 8
    row_idx, total_rows = google_sheet_svc.get_updated_row_idx(slack_channel, msg_ts)
    if row_idx:
        event_time = datetime_util.ts_to_datetime_str(float(body.get("event").get("event_ts")) + 60 * 60 * 8)
        RANGE = f"{slack_channel.channel_name}!G{row_idx + 1}:J{row_idx + 1}"
        user_email, user_name = get_user_profile(body.get("event").get("user"))
        res = google_sheet_util.update(slack_channel.sheet_id, RANGE,
                                       {"values": [["", "Y", event_time,
                                                    f"Passed by [{SlackService().get_slack_user_name(user_name)}]"]]})
        print(res.json())
    else:
        print(f"can't find row")


def add_backend2_help(slack_channel, body):
    print(f"[add_backend2_help]start,channel_name[{slack_channel.channel_name}]")
    msg_ts = int(float(body.get("event").get("item").get("ts"))) + 60 * 60 * 8
    row_idx, total_rows = google_sheet_svc.get_updated_row_idx(slack_channel, msg_ts)
    if row_idx:
        print("this issue is exist")
    else:
        slack_svc = SlackService()
        slack_msg = slack_svc.get_message(slack_channel.id, body.get("event").get("item").get("ts"))
        msg_text = slack_msg.data["messages"][0]["text"]
        msg_user_id = slack_msg.data["messages"][0]["user"]
        user_email, user_name = get_user_profile(msg_user_id)
        slack_url = slack_util.get_message_link(body)
        RANGE = f"{slack_channel.channel_name}!A{total_rows + 1}:f{total_rows + 1}"
        values = [
            [slack_channel.channel_name, datetime_util.ts_to_datetime_str(msg_ts), user_email, user_name, msg_text,
             slack_url]]
        res = google_sheet_util.update(slack_channel.sheet_id, RANGE,
                                       {"values": values})
        print(res.json())


def add_rabbit_key(slack_channel, body):
    title = "UNKNOW CHANNEL"
    if slack_channel:
        slack_svc = SlackService()
        slack_msg = slack_svc.get_message(slack_channel.id, body.get("event").get("item").get("ts"))
        title = slack_msg.data["messages"][0]["text"]
    slack_url = slack_util.get_message_link(body)
    res = notion_util.create_slack_subtask(title, slack_url)
    print(res.json())
    return res
