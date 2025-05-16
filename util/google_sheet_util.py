import json

import requests

from util import datetime_util

# Service account credentials file
# SERVICE_ACCOUNT_FILE = '/opt/python/resource/sage-inquiry-388907-041263e1f9e9.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Google Sheets setup
CLIENT_ID = ""
CLIENT_SECRET = ""
REFRESH_TOKEN = ""

API_KEY = ""  # https://ithelp.ithome.com.tw/articles/10283037

def refresh_access_token():
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }

    response = requests.post(token_url, data=data)
    response_data = response.json()
    if response.status_code == 200:
        return response_data.get("access_token")
    else:
        print("Failed to refresh token:", response_data)
        return None


def find_all(sheet_id, sheet_name):
    sheet_data = requests.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{sheet_name}?key={API_KEY}")
    return sheet_data.json()


def update(sheet_id, RANGE, data):
    res = requests.put(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{RANGE}?valueInputOption=USER_ENTERED",
        headers={
            "Content-Type": "application/json",
            'Authorization': f'Bearer {refresh_access_token()}'
        },
        data=json.dumps(data)
    )
    return res

# def resolve(channel_name, ts):
#     print(f"start resolve, channel_name[{channel_name}]ts[{ts}]")
#     creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#     print(f"creds")
#     service = build('sheets', 'v4', credentials=creds)
#     print(f"service")
#     # Get all rows from the sheet
#     sheet = service.spreadsheets()
#     print(f"sheet")
#     result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
#     print(f"result")
#     rows = result.get('values', [])
#     print(f"sheet length[{len(rows)}]")
#     # Find the row with matching criteria
#     headers = rows[0]  # Assumes the first row is headers
#     channel_idx = headers.index('channel name')
#     ts_idx = headers.index('ts time')
#     body = {
#         "values": [["Y"]]
#     }
#     for i in range(1, len(rows)):  # Skip the header row
#         row = rows[i]
#         print(f"check row[{row}]")
#         if len(row) > max(channel_idx, ts_idx):  # Ensure the row has enough columns
#             print(f"check row[channel_idx][{row[channel_idx]}]row[ts_idx][{row[ts_idx]}]channel_name[{channel_name}]ts[{ts}]i[{i}]")
#             if row[channel_idx] == channel_name and row[ts_idx] == ts:
#                 service.spreadsheets().values().update(
#                     spreadsheetId=SPREADSHEET_ID,
#                     range=f"{RANGE_NAME}!H{i + 1}",
#                     valueInputOption="RAW",  # or "USER_ENTERED" for formatted input
#                     body=body
#                 ).execute()
#                 return


# if __name__ == '__main__':
#     print(update("hktvmall-hybris-revamp-checkout-qa", "12/3/2024 6:35:33"))
