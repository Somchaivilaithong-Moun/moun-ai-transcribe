# 🎙️ Moun AI Transcribe

Website Python dùng `faster-whisper` để chuyển âm thanh/video thành văn bản và xuất **TXT, Word, PDF, SRT**.

## Chức năng

- Upload: MP3, WAV, M4A, MP4, WEBM, OGG, FLAC
- Tự nhận diện ngôn ngữ hoặc chọn: Việt / Lào / Thái / Anh
- Tùy chọn timestamp trong transcript
- Cho phép sửa transcript ngay trên giao diện
- Xuất TXT, DOCX, PDF và phụ đề SRT
- Model Whisper `base`, CPU `int8`
- File upload được ghi tạm khi xử lý rồi xóa; app không có database lưu lịch sử

## Chạy trên Windows

Khuyến nghị **Python 3.11**.

### Cách nhanh

Nhấp đúp `run_windows.bat`.

### Hoặc chạy bằng Terminal

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Trình duyệt sẽ mở địa chỉ local, thường là `http://localhost:8501`.

> Lần đầu chạy, faster-whisper sẽ tải model `base` từ Hugging Face. Vì vậy cần Internet ở lần tải model đầu tiên.

## Deploy lên Streamlit Community Cloud

1. Tạo repository GitHub mới.
2. Upload **toàn bộ nội dung trong folder này** lên repository, bao gồm `.streamlit/config.toml`.
3. Vào Streamlit Community Cloud và đăng nhập bằng GitHub.
4. Chọn **Create app** → chọn repository vừa tạo.
5. Branch: `main`.
6. Main file / entrypoint: `app.py`.
7. Trong **Advanced settings**, chọn **Python 3.11**.
8. Bấm **Deploy**.
9. Lần deploy đầu tiên có thể mất thêm thời gian để cài thư viện và tải model.
10. Khi chạy xong, bạn sẽ có link dạng `ten-cua-ban.streamlit.app` để gửi cho người khác.

## Lưu ý khi dùng hosting miễn phí

Whisper là AI khá nặng. Bản `base` phù hợp cho demo và file vừa/nhỏ nhưng có thể chậm nếu nhiều người dùng cùng lúc hoặc video dài. Nếu vượt giới hạn RAM/CPU của hosting miễn phí, cân nhắc:

- đổi `MODEL_NAME = "base"` thành `"tiny"` trong `app.py` để nhẹ hơn;
- giới hạn file nhỏ hơn;
- hoặc chuyển sang server có nhiều CPU/RAM hơn.

## Cấu trúc project

```text
Moun_AI_Transcribe/
├── app.py
├── requirements.txt
├── README.md
├── DEPLOY_GUIDE_VI.md
├── run_windows.bat
├── .gitignore
└── .streamlit/
    └── config.toml
```
