import io
import os, sys
from typing import List, Dict, Optional, Any

# 將專案根目錄加入模組搜尋路徑
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from dotenv import load_dotenv
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

from common.google_service import get_google_service

# 載入 .env 內容到環境變數，並強制更新
if not load_dotenv(override=True):
    print("警告：.env 檔案不存在或解析失敗，請確認它位於專案根目錄。")


def list_drive_folder_files(
    drive_service: Resource,
    folder_id: str,
    page_size: int = 1000
) -> List[Dict[str, str]]:
    """
    列出指定 Google Drive 資料夾中的所有檔案
    Args:
        drive_service (Resource): Google Drive API 服務物件
        folder_id (str): Google Drive 資料夾 ID
        page_size (int): 每頁檔案數量，預設為 1000
    Returns:
        List[Dict[str, str]]: 包含檔案 ID 和名稱的字典列表
    """
    if not isinstance(drive_service, Resource):
        raise TypeError(f"drive_service 必須是 Resource，實際收到 {type(drive_service)}")

    files: List[Dict[str, str]] = []
    page_token: Optional[str] = None

    while True:
        try:
            resp = drive_service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                spaces="drive",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                pageToken=page_token,
                pageSize=page_size,
                fields="nextPageToken, files(id, name)",
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


def download_drive_files_from_list(
    drive_service: Any,
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
    # 讀取環境變數
    GDRIVE_CREDENTIALS = os.getenv("GDRIVE_CREDENTIALS")
    if not GDRIVE_CREDENTIALS:
        print("錯誤：環境變數 GDRIVE_CREDENTIALS 未設定！")
        sys.exit(1)

    DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
    if not DRIVE_FOLDER_ID:
        print("錯誤：環境變數 DRIVE_FOLDER_ID 未設定！")
        sys.exit(1)

    DESTINATION_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

    # 取得 Google Drive API 服務
    gdrive_service, creds = get_google_service(
        service_name="drive",
        version="v3",
        credentials=GDRIVE_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    files = list_drive_folder_files(gdrive_service, DRIVE_FOLDER_ID)
    download_drive_files_from_list(gdrive_service, files, DESTINATION_DIR)
