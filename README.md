# gcloud-python-toolkit

A collection of Python scripts and utilities for interacting with Google Cloud services, including Google Drive, Speech-to-Text, etc.

## Features

* **Google Drive Downloader**: 列出並下載指定資料夾中的所有檔案

## Prerequisites

* Python 3.8 以上
* `pip` 或 `poetry`
* Google Cloud 服務帳號 JSON 憑證
  * 將 Service Account 的 email 加入目標 Google Drive 資料夾的共用列表，否則無法存取資料夾內容。
* `.env` 環境變數檔案

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
   GOOGLE_APPLICATION_CREDENTIALS=<your_service_account_credentials.json>
   DRIVE_FOLDER_ID=<your_drive_folder_id>
   GOOGLE_CLOUD_PROJECT=<your_project_id>
   OPENAI_API_KEY=<your_openai_api_key>
   ```

## Usage

### Google Drive Downloader

> 請將 Service Account 的 email 加入目標 Google Drive 資料夾的共用列表，否則無法存取資料夾內容。

```bash
python google_drive/downloader.py
```
* 會根據 `DRIVE_FOLDER_ID` 列出並下載所有檔案至 `downloads/`。
