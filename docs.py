from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import time
import re
import datetime
import requests
import ftplib


CLIENT_SECRET_FILE = "credentials.json"
TOKEN_FILE = "token.json"
LIST_FILE = "g_files.txt"
DOWNLOAD_DIR = f"Google_Drive_Backup {datetime.datetime.now().date()}"
SERVICE_ACCOUNT_FILE = "service-account.json"


def authorize() -> Credentials:
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    creds = get_creds(scopes, TOKEN_FILE)
    return creds


def write_file_list(creds: Credentials) -> None:
    service = build("drive", "v3", credentials=creds)
    results = (
        service.files()
        .list(pageSize=100, fields="nextPageToken, files(id, name, mimeType)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
        print("Нет файлов для скачивания")
        return
    print("Файлы:")

    with open("g_files.txt", "w", encoding="UTF-8") as f:
        for item in items:
            if item["mimeType"] == "application/vnd.google-apps.spreadsheet":
                f.write(f"{item['name']} _|_ {item['id']}" + "\n")
                print(f"{item['name']} ({item['id']})")


def load_file_list() -> list:
    files = []
    with open(LIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            name, file_id = line.strip().split(" _|_ ")
            files.append({"name": name, "id": file_id})
    print(f"Найдено файлов для скачивания: {len(files)}")
    return files

def get_creds(scopes: list, file: str) -> Credentials:
    creds = None
    
    if os.path.exists(file):
        creds = Credentials.from_authorized_user_file(file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes)
            creds = flow.run_local_server(port=0)
        with open(file, "w") as token:
            token.write(creds.to_json())
    return creds

def download_excel_sheets_api(files: list) -> None:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = get_creds(scopes, SERVICE_ACCOUNT_FILE)

    service = build("sheets", "v4", credentials=creds)

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    for file in files:
        request = service.spreadsheets().get(
            spreadsheetId=file["id"], includeGridData=False
        )
        response = request.execute()

        export_url = f"https://docs.google.com/spreadsheets/export?id={file['id']}&exportFormat=xlsx"

        response = requests.get(
            export_url, headers={"Authorization": f"Bearer {creds.token}"}
        )

        file["name"] = re.sub(r'[\\/*?:"<>|]', "", file["name"])
        file_path = os.path.join(DOWNLOAD_DIR, file["name"])
        with open(f"{file_path}.xlsx", "wb") as f:
            f.write(response.content)

        print(f"Файл сохранен: {file['name']}.xlsx")
    print("\n" + "Загрузка завершена!")


def main():
    creds = authorize()

    write_file_list(creds)

    files = load_file_list()

    download_excel_sheets_api(files)


if __name__ == "__main__":
    main()
