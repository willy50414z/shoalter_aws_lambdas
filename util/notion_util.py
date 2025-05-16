import requests

headers = {
    'Authorization': f'',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'  # Specify the Notion API version
}
ecom_engine_database_id = '12d43989266a8035886be967a4427bc4'
subtask_database_id = '12d43989266a80a7b970e3749d33540a'  # Replace with your database ID


def create_slack_subtask(title, url):
    payload = {
        "parent": {"type": "database_id", "database_id": subtask_database_id},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": title}}]
            },
            "Assignee": {
                "type": "people",
                'people': [{'object': 'user', 'id': '9ec132c2-2c35-4d72-a587-e567036b717e'}]
            },
            "Slack": {
                'type': 'url',
                'url': url
            }
        }
    }

    response = requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)
    return response

def find_by_ticket_like(issueKey):
    url = f'https://api.notion.com/v1/databases/{ecom_engine_database_id}/query'
    payload = {"page_size": 100, "filter": {
        "property": "Ticket",
        "rich_text": {
            "contains": issueKey
        }
    }}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        raise ValueError("[findByTicketLike] fetch notion data by issue key failed, issueKey[" + issueKey + "]")

def update_task_status(pageid, status):
    url = f'https://api.notion.com/v1/pages/{pageid}'
    payload = {
        "parent": {"type": "database_id", "database_id": ecom_engine_database_id},
        "properties": {
            "Status": {
                "type": "select",
                'select': {
                    'name': status
                }
            }
        }
    }
    return requests.patch(url, json=payload, headers=headers)