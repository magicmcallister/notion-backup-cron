import os
from datetime import date
import requests
import json
import time

BACKUP_FOLDER = os.getenv("BACKUP_FOLDER")
NOTION_API = os.getenv("NOTION_API")
EXPORT_FILENAME = f"{BACKUP_FOLDER}/backup_{date.today().strftime('%d-%m-%Y')}.zip"
NOTION_TOKEN_V2 = os.getenv("NOTION_TOKEN_V2")
NOTION_SPACE_ID = os.getenv("NOTION_SPACE_ID")

ENQUEUE_TASK_PARAM = {
    "task": {
        "eventName": "exportSpace", 
        "request": {
            "spaceId": NOTION_SPACE_ID,
            "exportOptions": {"exportType": "html", "timeZone": "Europe/Madrid", "locale": "en"}
        }
    }
}


def post_request(endpoint: str, params: object):
    response = requests.post(
        f"{NOTION_API}/{endpoint}",
        data=json.dumps(params),
        headers={
            'content-type': 'application/json',
            'cookie': f'token_v2={NOTION_TOKEN_V2}; '
        },
    )
    return response.json()


def backup_process():
    task_id = post_request("enqueueTask", ENQUEUE_TASK_PARAM)["taskId"]
    print(f"Enqueued task {task_id}")

    while True:
        time.sleep(2)
        tasks = post_request("getTasks", {"taskIds": [task_id]})["results"]
        task = next(t for t in tasks if t["id"] == task_id)
        print(f"\rPages exported: {task['status']['pagesExported']}", end="")

        if task["state"] == "success":
            break

    export_url = task["status"]["exportURL"]
    print(f"\nExport created, downloading: {export_url}")

    r = requests.get(export_url, allow_redirects=True)
    with open(EXPORT_FILENAME, 'wb') as file:
        file.write(r.content)
    print(f"\nDownload complete: {EXPORT_FILENAME}")


if __name__ == "__main__":
    backup_process()
