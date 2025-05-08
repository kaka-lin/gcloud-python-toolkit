import io
import os
import sys
from typing import List, Dict, Optional

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# 載入 .env 內容到環境變數
if not load_dotenv():
    print("警告：.env 檔案不存在或解析失敗，請確認它位於專案根目錄。")


def get_gdrive_service(service_account_file: str, scopes: Optional[List[str]] = None) -> any:
    """
    建立並返回 Google Drive API client

    參數:
        service_account_file: Service Account JSON 憑證檔路徑
        scopes: OAuth2 授權範圍清單，預設為 drive（完整存取）

    回傳:
        drive v3 service client
    """
    base = "https://www.googleapis.com/auth"
    if scopes is None:
        scopes = [f"{base}/drive"]

    try:
        creds = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=scopes
        )
        return build("drive", "v3", credentials=creds)
    except FileNotFoundError:
        print(f"錯誤：找不到憑證檔案：{service_account_file}")
        sys.exit(1)
    except ValueError as e:
        print(f"錯誤：無效的憑證檔案或授權範圍：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"錯誤：建立 Drive 服務失敗：{e}")
        sys.exit(1)


def list_gdrive_folder_files(
    drive_service: any,
    folder_id: str,
    page_size: int = 1000
) -> List[Dict[str, str]]:
    """
    列出資料夾中的所有檔案 (ID, Name)
    """
    files: List[Dict[str, str]] = []
    page_token: Optional[str] = None
    while True:
        try:
            resp = drive_service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
                pageSize=page_size,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
        except HttpError as e:
            print(f"無法列出資料夾檔案：{e.resp.status} {e._get_reason()}")
            return []

        for f in resp.get("files", []):
            files.append({"id": f["id"], "name": f["name"]})
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return files


def download_gdrive_files_from_list(
    drive_service: any,
    files: List[Dict[str, str]],
    destination_dir: str
) -> List[str]:
    """
    下載給定檔案列表到本地資料夾
    """
    try:
        os.makedirs(destination_dir, exist_ok=True)
    except OSError as e:
        print(f"錯誤：無法建立目錄 {destination_dir}：{e}")
        sys.exit(1)

    downloaded: List[str] = []
    for f in files:
        fid, fname = f["id"], f["name"]
        out_path = os.path.join(destination_dir, fname)
        print(f"下載：{fname} → {out_path}")

        try:
            request = drive_service.files().get_media(fileId=fid)
            with io.FileIO(out_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"  已完成 {int(status.progress() * 100)}%")
                    if done:
                        break
            downloaded.append(out_path)
        except HttpError as e:
            print(f"警告：下載 {fname} 失敗：{e.resp.status} {e._get_reason()}")
        except OSError as e:
            print(f"警告：寫入檔案 {out_path} 時發生 IO 錯誤：{e}")
        except Exception as e:
            print(f"警告：下載 {fname} 時發生未預期錯誤：{e}")

    print("所有檔案下載完成。")
    return downloaded


if __name__ == "__main__":
    SERVICE_ACCOUNT_FILE = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        ""
    )
    if not SERVICE_ACCOUNT_FILE:
        print("錯誤：環境變數 GOOGLE_APPLICATION_CREDENTIALS 未設定！")
        sys.exit(1)

    FOLDER_ID = os.getenv(
        "DRIVE_FOLDER_ID",
        ""
    )
    if not FOLDER_ID:
        print("錯誤：環境變數 DRIVE_FOLDER_ID 未設定！")
        sys.exit(1)

    DESTINATION_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

    gdrive_service = get_gdrive_service(SERVICE_ACCOUNT_FILE)

    files = list_gdrive_folder_files(gdrive_service, FOLDER_ID)
    download_gdrive_files_from_list(gdrive_service, files, DESTINATION_DIR)
