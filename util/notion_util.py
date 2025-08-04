import configparser

import requests

from util import string_util

config = configparser.ConfigParser()
config.read('../application.ini')
integration_token = config["DEFAULT"]["notion_token"]  # Replace with your integration token

headers = {
    'Authorization': f'Bearer {integration_token}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'  # Specify the Notion API version
}
ecom_engine_database_id = '12d43989266a8035886be967a4427bc4'
subtask_database_id = '12d43989266a80a7b970e3749d33540a'  # Replace with your database ID
jira_url_prefix = "https://hongkongtv.atlassian.net/browse/"
peopleIdMap = {
    'TW - IT - BE - JOHN CHANG': '744b3b5b-ca64-4a33-a074-e948f1619b25'
    , 'TW - IT - BE - Willy Cheng': '9ec132c2-2c35-4d72-a587-e567036b717e'
    , 'TW - IT - BE - Kenny Ma': '113d872b-594c-81b9-9659-0002d54432ff'
    , 'MarkHuang': '214d872b-594c-8118-8856-0002e9dcaaad'
    , 'TW - IT - BE - Tony Ng': 'da35c1a6-fc0a-4111-8c87-9e72be476b60'
}

exclude_service = ["shoalter-ecommerce-frontend", "personalization-service", "see-management-console-backend",
                   "see-management-console-frontend", "login-service", "game-service", "batch-file-processing-service",
                   "see-management-console-frontend", "see-management-console-backend"]

team1_service = ["cart-service", "address-service", "order-service", "IIDS", "IIMS", "IIMS-LM"]
team2_service = ["promotion-service", "product-service", "config-server", "user-service", "internal-API-gateway",
                 "mobile-API-gateway", "caching-management-server", "shoalter-server-starter", "frontend-api-gateway",
                 "internal-api-gateway"]
team3_service = ["notification-service", "page-component-service", "third-party-API-service", "third-party-api-service",
                 "SAC"]

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


def find_by_system_and_status(system, status):
    url = f'https://api.notion.com/v1/databases/{ecom_engine_database_id}/query'
    payload = {
        "page_size": 100,
        "filter": {
            "and": [{
                    "property": "System",
                    "select": {
                        "equals": system
                    }
                }, {
                    "property": "Status",
                    "status": {
                        "equals": status
                    }
                }
            ]
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        raise ValueError(f"[find_by_system_and_status] fetch notion data by issue key failed,system[{system}]status[{status}]")


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
                'status': {
                    'name': status
                }
            }
        }
    }
    return requests.patch(url, json=payload, headers=headers)

def findByTicket(database_id, issueKey):
    try:
        url = f'https://api.notion.com/v1/databases/{database_id}/query'

        has_more = True
        start_cursor = None
        all_result = []

        while has_more:
            payload = {"page_size": 100, "filter": {
                "property": "Ticket",
                "rich_text": {
                    "equals": issueKey
                }
            }}
            if start_cursor:
                payload["start_cursor"] = start_cursor
            response = requests.post(url, json=payload, headers=headers)
            single_page_data = response.json()
            start_cursor = single_page_data["next_cursor"]
            has_more = single_page_data["has_more"]
            if "results" in single_page_data:
                if len(single_page_data["results"]) == 0:
                    print("notion item not found, databaseId[" + database_id + "]issueKey[" + issueKey + "]")
                all_result.extend(single_page_data["results"])
            elif "status" in single_page_data and single_page_data["status"] == 404:
                return None
            else:
                raise ValueError("[findByTicketLike] fetch notion data by issue key failed, issueKey[" + issueKey + "]")
        return all_result


    except Exception as e:
        print("can't get notion item, databaseId[" + database_id + "]issueKey[" + issueKey + "]")
        raise e
def get_assignee_by_issue(issue):
    if issue.fields.assignee is not None and issue.fields.assignee.displayName in peopleIdMap:
        return peopleIdMap[issue.fields.assignee.displayName]
    else:
        pic_name = issue.fields.customfield_11563.displayName if hasattr(issue.fields,
                                                                         "customfield_11563") and issue.fields.customfield_11563 is not None and issue.fields.customfield_11563.displayName in peopleIdMap else 'TW - IT - BE - Tony Ng'

    team1_people = ['TW - IT - BE - JOHN CHANG', 'TW - IT - BE - Willy Cheng', 'TW - IT - BE - Kenny Ma', 'MarkHuang']
    if (hasattr(issue.fields.assignee, "displayName") and issue.fields.assignee.displayName not in team1_people) and (
            hasattr(hasattr(issue.fields,"customfield_11563") and issue.fields.customfield_11563,
                    "displayName") and issue.fields.customfield_11563.displayName not in team1_people) and (
            hasattr(hasattr(issue.fields,"customfield_11608") and issue.fields.customfield_11608,
                    "displayName") and issue.fields.customfield_11608.displayName not in team1_people):
        pic_name = 'TW - IT - BE - Tony Ng'

    return peopleIdMap[pic_name]

def findByTicketLike(issueKey, datatase=ecom_engine_database_id):
    url = f'https://api.notion.com/v1/databases/{datatase}/query'
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

def delete_task_in_subtask_db(subtask_issue):
    if subtask_issue.fields.issuetype.subtask:
        task = findByTicketLike(subtask_issue.fields.parent.key, subtask_database_id)
        if len(task) > 0:
            print(
                f"subtask has created, parent ticket will be deleted, parent key[{task[0]["properties"]["Ticket"]["url"]}]")
            return requests.delete("https://api.notion.com/v1/blocks/" + task[0]["id"], headers=headers)

def createSubTask(issue, task_id=None):
    print(f'start create subtask, issue.key[{issue.key}]')
    parent_task = findByTicket(ecom_engine_database_id,
                               f"{jira_url_prefix}{issue.fields.parent.key if issue.fields.issuetype.subtask else issue.key}")
    if len(parent_task) == 0:
        return

    delete_task_in_subtask_db(issue)

    payload = {
        "parent": {"type": "database_id", "database_id": subtask_database_id},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"[{issue.key}] {issue.fields.summary}"}}]
            },
            'Assignee': {
                'type': 'people',
                'people': [{'object': 'user', 'id': get_assignee_by_issue(issue)}]
            },
            "Ticket": {
                'type': 'url',
                'url': jira_url_prefix + issue.key
            },
            "JiraStatus": {
                "type": "select",
                'select': {
                    'name': issue.fields.status.name
                }
            },
            "Status": {"status": {"name": "Not started"}},
            "Task": {
                "type": "relation",
                "relation": [
                    {
                        "id":
                            task_id if task_id else parent_task[
                                0]["id"]
                    }
                ]
            }
        }
    }

    return requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)

def get_system_code_and_assignee(issue):
    willy_name = 'TW - IT - BE - Willy Cheng'
    system_name = None
    assignee = willy_name

    for service_name in team1_service:
        if "[" + service_name + "]" in issue.fields.summary:
            return service_name, willy_name

    for service_name in team2_service:
        if "[" + service_name + "]" in issue.fields.summary:
            return service_name, willy_name

    for service_name in team3_service:
        if "[" + service_name + "]" in issue.fields.summary:
            return service_name, None

    for service_name in exclude_service:
        if "[" + service_name + "]" in issue.fields.summary:
            return service_name, None

    if "[ThePlace]" in issue.fields.summary:
        system_name = "IIMS-LM"
        assignee = willy_name
    elif "[HKTV-IIMS]" in issue.fields.summary or "[IIMS-HKTV]" in issue.fields.summary or "[iims]" in issue.fields.summary or "[IIMS]" in issue.fields.summary:
        system_name = "IIMS"
        assignee = willy_name
    elif issue.key.startswith("HYBRIS-"):
        system_name = "HYBRIS"
        assignee = willy_name
    else:
        assignee = get_assignee_by_issue(issue)

    return system_name, assignee

def create_task(db_id, issue):
    print(f'start create task, issue.key[{issue.key}]')

    system_name, assignee = get_system_code_and_assignee(issue)

    fix_versions = ""
    release_date = None
    for fix_version in issue.fields.fixVersions:
        fix_versions += fix_version.name + ","
        if "@" in fix_version.name:
            release_date = fix_version.name.split("@")[1]

    if len(fix_versions) > 0:
        fix_versions = fix_versions[0:len(fix_versions) - 1]

    payload = {
        "parent": {"type": "database_id", "database_id": db_id},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"[{issue.key}] {issue.fields.summary}"}}]
            },
            "Ticket": {
                'type': 'url',
                'url': jira_url_prefix + issue.key
            },
            "JiraStatus": {
                "type": "select",
                'select': {
                    'name': issue.fields.status.name
                }
            },
            "ReleaseDate": {
                "type": "select",
                'select': {
                    'name': release_date if string_util.is_valid_date(release_date) else "uncheck"
                }
            },
            "fixVersion": {
                'rich_text': [{
                    'text': {
                        'content': fix_versions
                    }
                }]
            }
        }
    }
    if issue.fields.issuetype.name in ["故事", "Story"]:
        payload["properties"]["Status"] = {"status": {"name": "Done"}}

    if system_name:
        payload["properties"]["System"] = {
            "type": "select",
            'select': {
                'name': system_name
            }
        }

    if assignee and assignee in peopleIdMap:
        payload["properties"]["Assignee"] = {
            "type": "people",
            'people': [{'object': 'user', 'id': peopleIdMap[assignee]}]
        }

    if issue.fields.summary in exclude_service:
        payload["properties"]["Status"] = {
            "type": "select",
            'select': {
                'name': "exclude"
            }
        }

    if hasattr(issue.fields, "parent") and issue.fields.parent and len(issue.fields.parent.key) > 0:
        payload["properties"]["Epic"] = {
            'type': 'url',
            'url': jira_url_prefix + issue.fields.parent.key
        }

    return requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)

def update_subtask_relate_to_task(page_id, task_id):
    url = f'https://api.notion.com/v1/pages/{page_id}'
    payload = {
        "properties": {
            "Task": {
                "type": "relation",
                "relation": [
                    {
                        "id": task_id
                    }
                ]
            }
        }
    }
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()

def get_check_task_error_msg(issue):
    msg = ""
    if hasattr(issue.fields, "customfield_11563") and not issue.fields.customfield_11568:
        msg += "[Notes for Testing] missing\r\n"
    if not issue.fields.duedate:
        msg += "[DueDate] missing\r\n"
    return msg[0:max(len(msg) - 2, 0)]

def updateTaskStatus(page, issue):
    # issue.fields.fixVersions[0].name
    # page["properties"]["fixVersion"]["rich_text"][0]["plain_text"]
    if page["properties"]["JiraStatus"]["select"]["name"] == issue.fields.status.name and len(
            page["properties"]["fixVersion"]["rich_text"]) > 1 and page["properties"]["fixVersion"]["rich_text"][0][
        "plain_text"] == issue.fields.fixVersions[0].name:
        return ""
    else:
        url = f'https://api.notion.com/v1/pages/{page["id"]}'
        fix_versions = ""
        release_date = None
        for fix_version in issue.fields.fixVersions:
            fix_versions += fix_version.name + ","
            if "@" in fix_version.name:
                release_date = fix_version.name.split("@")[1]
        if len(fix_versions) > 0:
            fix_versions = fix_versions[0:len(fix_versions) - 1]
        system_name, assignee = get_system_code_and_assignee(issue)
        payload = {
            "properties": {
                # 'Assignee': {
                #     'type': 'people',
                #     'people': [{'object': 'user', 'id': getAssigneeByIssue(issue)}]
                # },
                "JiraStatus": {
                    "type": "select",
                    'select': {
                        'name': issue.fields.status.name
                    }
                },
                "fixVersion": {
                    'rich_text': [{
                        'text': {
                            'content': fix_versions
                        }
                    }]
                },
                "ReleaseDate": {
                    "type": "select",
                    'select': {
                        'name': release_date if string_util.is_valid_date(release_date) else "uncheck"
                    }
                },
                "CheckTicketMsg": {
                    'rich_text': [{
                        'text': {
                            'content': get_check_task_error_msg(issue)
                        }
                    }]
                }
                ,
                "Name": {
                    "type": "title",
                    "title": [{"type": "text", "text": {"content": f"[{issue.key}] {issue.fields.summary}"}}]
                }
            }
        }

        if system_name:
            payload["properties"]["System"] = {
                "type": "select",
                'select': {
                    'name': system_name
                }
            }

        if hasattr(issue.fields, "parent") and issue.fields.parent and len(issue.fields.parent.key) > 0:
            payload["properties"]["Epic"] = {
                'type': 'url',
                'url': jira_url_prefix + issue.fields.parent.key
            }

        return requests.patch(url, json=payload, headers=headers)

def findOpenedItem(database_id):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'

    has_more = True
    start_cursor = None
    all_result = []

    while has_more:
        payload = {"page_size": 100, "filter": {
            "and": [
                {
                    "property": "JiraStatus",
                    "select": {
                        "does_not_equal": "CLOSED"
                    }
                },
                {
                    "property": "JiraStatus",
                    "select": {
                        "does_not_equal": "CANCELED"
                    }
                },
                {
                    "property": "JiraStatus",
                    "select": {
                        "does_not_equal": "Report"
                    }
                }
            ]

        }}

        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(url, json=payload, headers=headers)
        single_page_data = response.json()
        start_cursor = single_page_data["next_cursor"]
        has_more = single_page_data["has_more"]
        if "results" in single_page_data:
            if len(single_page_data["results"]) == 0:
                print("notion item not found, databaseId[" + database_id + "]")
            all_result.extend(single_page_data["results"])
        elif "status" in single_page_data and single_page_data["status"] == 404:
            return None
        else:
            raise ValueError("[findByTicketLike] fetch notion data by issue key failed")

    return all_result

def updateSubTaskStatus(page, issue):
    # issue.fields.fixVersions[0].name
    # page["properties"]["fixVersion"]["rich_text"][0]["plain_text"]
    try:
        if page["properties"]["JiraStatus"]["select"] is not None and page["properties"]["JiraStatus"]["select"][
            "name"] == issue.fields.status.name and not issue.fields.duedate and page["properties"]["DevDate"][
            'date'] and page["properties"]["DevDate"]['date']['start'] == issue.fields.duedate:
            return ""
        else:
            url = f'https://api.notion.com/v1/pages/{page["id"]}'
            payload = {
                "properties": {
                    # 'Assignee': {
                    #     'type': 'people',
                    #     'people': [{'object': 'user', 'id': getAssigneeByIssue(issue)}]
                    # },
                    "JiraStatus": {
                        "type": "select",
                        'select': {
                            'name': issue.fields.status.name
                        }
                    }
                    , "Name": {
                        "type": "title",
                        "title": [{"type": "text", "text": {"content": f"[{issue.key}] {issue.fields.summary}"}}]
                    }
                }
            }
            if issue.fields.duedate:
                payload["properties"]["DevDate"] = {"date": {"start": f"{issue.fields.duedate}"}}
            if issue.fields.status.name == "已取消":
                payload["properties"]["Status"] = {"status": {"name": "Done"}}
            response = requests.patch(url, json=payload, headers=headers)
            return response.json()
    except Exception:
        print("[updateSubTaskStatus] update SubTask Status throw error")
        print(page)
        print(issue)
        raise