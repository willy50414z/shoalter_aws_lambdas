import requests

WEBHOOK_BASE_URL = "https://hooks.slack.com/services/"



def send_webhook_message(slack_webhook, text):
    res = requests.post(f"{WEBHOOK_BASE_URL}{slack_webhook.value}", json={"text": text})
    print(res.text)


def get_user_profile(user_id):
    res = requests.get(f"https://hktvitlo.slack.com/api/users.profile.get?user={user_id}", headers={
        "Content-Type": "application/json",
        'Authorization': f'Bearer {TOKEN}'
    })
    return res.json()
