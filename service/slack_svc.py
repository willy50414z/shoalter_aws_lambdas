import configparser
import json
import os
import time

import requests
from slack_sdk import WebClient

WEBHOOK_BASE_URL = "https://hooks.slack.com/services/"

config = configparser.ConfigParser()
config.read(os.path.join('/opt/python', 'application.ini'))
# Set your Slack API token
TOKEN = config["DEFAULT"]["slack_token"]


class SlackService:
    def __init__(self):
        self.slack_id_map = None
        self.client = WebClient(token=TOKEN)

    def send_webhook_message(self, slack_webhook, text):
        res = requests.post(f"{WEBHOOK_BASE_URL}{slack_webhook.value}", json={"text": text})
        print(res)

    def get_user_profile(self, user_id):
        res = requests.get(f"https://hktvitlo.slack.com/api/users.profile.get?user={user_id}", headers={
            "Content-Type": "application/json",
            'Authorization': f'Bearer {TOKEN}'
        })
        return res.json()

    def get_channel_message(self, channel_id, period_ms):
        isNotComplete = True
        next_cursor = None
        now_timestamp = int(time.time())
        startTime = now_timestamp - period_ms / 1000
        messageList = []
        while isNotComplete:
            # Call the conversations.history method to retrieve messages from the channel
            response = self.client.conversations_history(channel=channel_id, limit=100, cursor=next_cursor)
            # Print out the retrieved messages
            # print(response)
            next_cursor = response["response_metadata"]["next_cursor"]
            for message in response["messages"]:
                if float(message["ts"]) < startTime:
                    isNotComplete = False
                    break
                messageList.append(message)
        return messageList

    def get_message(self, channel_id, ts):
        response = self.client.conversations_replies(channel=channel_id, ts=ts)
        return response

    def get_slack_user_id(self, name):
        if not self.slack_id_map:
            with open("/opt/python/resource/slack_name_id_map.json", "r", encoding="utf-8") as file:
                self.slack_id_map = json.load(file)
        return self.slack_id_map[name] if name in self.slack_id_map else name

    def get_slack_user_name(self, id):
        if not self.slack_id_map:
            with open("/opt/python/resource/slack_name_id_map.json", "r", encoding="utf-8") as file:
                self.slack_id_map = json.load(file)
        return next((k for k, v in self.slack_id_map.items() if v == id), None)
