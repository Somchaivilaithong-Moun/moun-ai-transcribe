# 🎙️ Moun AI Transcribe

Ứng dụng Streamlit dùng **faster-whisper** để chuyển âm thanh/video thành văn bản và xuất **TXT, Word, PDF, SRT**.

## Chức năng

- Upload: MP3, WAV, M4A, MP4, WEBM, OGG, FLAC
- Tự nhận diện ngôn ngữ hoặc chọn thủ công:
  - 🇻🇳 Tiếng Việt
  - 🇬🇧 English
  - 🇱🇦 Tiếng Lào
  - 🇹🇭 Tiếng Thái
  - 🇨🇳 Tiếng Trung
- Tùy chọn thêm timestamp vào transcript
- Cho phép sửa transcript trực tiếp trên giao diện
- Xuất TXT, DOCX, PDF và SRT
- Giao diện responsive, card, gradient, hiệu ứng hover
- Model Whisper `base`, CPU `int8`
- File upload được ghi tạm khi xử lý và code cố gắng xóa sau khi hoàn tất
- Không cần OpenAI API key

## Chạy trên Windows

Khuyến nghị **Python 3.11**.

### Cách nhanh

Nhấp đúp `run_windows.bat`.

### Hoặc Terminal

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Trình duyệt thường mở tại `http://localhost:8501`.

> Lần đầu chạy, faster-whisper sẽ tải model `base`, vì vậy cần Internet.

## Deploy Streamlit Community Cloud

Repository cần có ít nhất:

```text
app.py
requirements.txt
packages.txt
.streamlit/config.toml
```

Trong Streamlit Community Cloud:

```text
Repository: Somchaivilaithong-Moun/moun-ai-transcribe
Branch: main
Main file path: app.py
Python: 3.11
```

Sau khi GitHub có commit mới, Streamlit thường tự cập nhật app.

## Lưu ý PDF đa ngôn ngữ

- Tiếng Trung dùng CID font tích hợp của ReportLab.
- `packages.txt` yêu cầu Streamlit Cloud cài Noto fonts để PDF tiếng Lào/Thái/Việt hiển thị tốt hơn.

## Tài nguyên hosting

Whisper khá nặng. Nếu hosting miễn phí thiếu RAM/CPU, có thể đổi trong `app.py`:

```python
MODEL_NAME = "base"
```

thành:

```python
MODEL_NAME = "tiny"
```

`tiny` nhanh và nhẹ hơn nhưng độ chính xác có thể thấp hơn.
