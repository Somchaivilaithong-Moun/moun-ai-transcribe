# Deploy Moun AI Transcribe lên Streamlit Community Cloud

## 1. GitHub

Repository đề xuất:

```text
Somchaivilaithong-Moun/moun-ai-transcribe
```

Push toàn bộ project lên branch `main`.

## 2. Streamlit Community Cloud

Mở Streamlit Community Cloud, đăng nhập GitHub và chọn Deploy app.

Điền:

```text
Repository: Somchaivilaithong-Moun/moun-ai-transcribe
Branch: main
Main file path: app.py
```

Trong Advanced settings chọn Python 3.11.

Không cần Secrets vì bản này không dùng API key.

## 3. Sau khi deploy

App URL hiện tại có thể dùng:

```text
https://moun-ai-transcribe.streamlit.app
```

## 4. Cập nhật sau này

Mỗi lần sửa code:

```powershell
git add .
git commit -m "Update app"
git push
```

Streamlit sẽ tự lấy commit mới và cập nhật app.
