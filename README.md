# gcloud-python-toolkit

A collection of Python scripts and utilities for interacting with Google Cloud services, including Google Drive, Speech-to-Text, etc.

## Features

- **Google Drive Downloader**: 列出並下載指定資料夾中的所有檔案
- **Google Speech Transcribe**: 使用 [Chrip2](https://cloud.google.com/speech-to-text/v2/docs/chirp_2-model) 模型轉錄 Audio

## Prerequisites

- Python 3.8 以上
- `pip` 或 `poetry`
- Google Cloud 服務帳號 JSON 憑證
  - 將 Service Account 的 email 加入目標 Google Drive 資料夾的共用列表，否則無法存取資料夾內容。
  - 為 Speech-to-Text，請確保 Service Account 擁有 `roles/speech.recognizerUser` 或更高權限。
- `.env` 環境變數檔案

## Installation

```bash
# Clone the repository
git clone https://github.com/kaka-lin/gcloud-python-toolkit.git
cd gcloud-python-toolkit

# 使用 pip
pip install -r requirements.txt

# 或使用 Poetry
poetry install
```

## Configuration

1. 複製範本：

   ```bash
   cp .env.example .env
   ```
2. 在 `.env` 中填入：

    ```dotenv
    # Drive 相關
    GDRIVE_CREDENTIALS=<path/to/your/drive-service-account.json>
    DRIVE_FOLDER_ID=<your_drive_folder_id>

    # Speech-to-Text 相關
    GSPEECH_CREDENTIALS=<path/to/your/speech-service-account.json>
    GOOGLE_CLOUD_PROJECT=<your_project_id>
    ```

## Usage

### Google Drive Downloader

> 請將 Service Account 的 email 加入目標 Google Drive 資料夾的共用列表，否則無法存取資料夾內容。

```bash
python google_drive/downloader.py
```
  - 會根據 `DRIVE_FOLDER_ID` 列出並下載所有檔案至 `downloads/`。

### Google Speech Transcribe (Chirp2)

```bash
# preprocess audio
python google_chirp/preprocess.py

# 開始轉錄
python google_chirp/transcribe.py
```
  - 會讀取 .env 中的 GOOGLE_CLOUD_PROJECT、GSPEECH_CREDENTIALS 以及在程式碼中設定的 audio_uri，使用 Chirp2 模型轉錄並輸出結果。
