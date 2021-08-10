import os
import datetime
import filecmp
import requests
import json
import time

from config import Config

config = Config()
config.load()

BACKUP_FOLDER = config.get("BACKUP", "FOLDER")
NOTION_API = config.get("NOTION", "API")
EXPORT_FILENAME = f"{BACKUP_FOLDER}/backup_{datetime.datetime.now().strftime('%d-%m-%Y-%H:%M:%S')}.zip"
NOTION_TOKEN_V2 = config.get("NOTION", "TOKEN_V2")
NOTION_SPACE_ID = config.get("NOTION", "SPACE_ID")


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


def get_old_backup_file():
    zip_files = []
    for root, dirs, files in os.walk(BACKUP_FOLDER):
        files_path = list(os.path.join(root, f) for f in files)
        for file in files_path:
            if os.path.splitext(file)[1] == ".zip":
                zip_files.append(file)

    if len(zip_files) > 0:
        old_backup_file = zip_files[0]
        return old_backup_file
    else:
        return None


def run():
    old_backup_file = get_old_backup_file()
    backup_process()
    os.remove(old_backup_file)

if __name__ == "__main__":
    run()
