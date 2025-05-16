def get_message_link(body):
    return f"https://hktvitlo.slack.com/archives/{body.get("event").get("item").get("channel")}/p{body.get("event").get("item").get("ts").replace(".", "")}"