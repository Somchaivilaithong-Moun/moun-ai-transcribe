# Hướng dẫn deploy Moun AI Transcribe

## Phần A — Test trên máy trước

1. Giải nén project.
2. Mở folder bằng VS Code.
3. Mở Terminal.
4. Chạy:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

5. Upload thử một file MP3 ngắn và kiểm tra TXT / Word / PDF / SRT.

## Phần B — Đưa code lên GitHub bằng giao diện web

1. Đăng nhập GitHub.
2. Chọn **New repository**.
3. Đặt tên ví dụ: `moun-ai-transcribe`.
4. Có thể chọn Public để deploy đơn giản.
5. Tạo repository.
6. Chọn **Add file → Upload files**.
7. Kéo toàn bộ file/folder trong project vào GitHub.
8. Commit changes.

Quan trọng: phải có `app.py` và `requirements.txt` ở repository. Folder `.streamlit` cũng nên được upload.

## Phần C — Deploy Streamlit

1. Mở Streamlit Community Cloud.
2. Đăng nhập / kết nối GitHub.
3. Chọn **Create app**.
4. Repository: chọn `moun-ai-transcribe`.
5. Branch: `main`.
6. File path: `app.py`.
7. Mở **Advanced settings** và chọn Python **3.11**.
8. Không cần nhập API key vì app chạy faster-whisper trực tiếp.
9. Bấm **Deploy**.

## Phần D — Sau khi deploy

Khi trạng thái thành công, Streamlit cấp cho bạn một URL `*.streamlit.app`. Gửi URL đó cho người khác là họ có thể upload file và dùng app.

Nếu app báo thiếu tài nguyên hoặc chạy quá chậm, đổi dòng:

```python
MODEL_NAME = "base"
```

thành:

```python
MODEL_NAME = "tiny"
```

commit lên GitHub. Streamlit sẽ tự cập nhật app.

## Lỗi thường gặp

### `ModuleNotFoundError`
Kiểm tra package đã có trong `requirements.txt` chưa.

### App lâu ở bước khởi động đầu tiên
Lần đầu server phải tải model Whisper. Chờ thêm và mở Cloud logs để xem tiến trình.

### App vượt RAM
Dùng model `tiny`, giảm kích thước file, hoặc dùng hosting mạnh hơn.

### PDF không tạo được
TXT và Word vẫn hoạt động. PDF cần một font Unicode có sẵn trên máy chủ. Code đã tự tìm Arial / DejaVu Sans / Liberation Sans trên Windows, Linux và macOS.
