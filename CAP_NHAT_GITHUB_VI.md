# Cách cập nhật website đang deploy

Website hiện tại:

`https://moun-ai-transcribe.streamlit.app`

Repository:

`Somchaivilaithong-Moun/moun-ai-transcribe`

## Cách khuyên dùng: thay file local rồi Git push

1. Giải nén gói mới.
2. Copy toàn bộ các file trong folder mới vào folder Git hiện tại của bạn:

```text
C:\Users\MSINB\Downloads\Moun_AI_Transcribe
```

3. Khi Windows hỏi Replace/Overwrite, chọn thay file cũ bằng file mới.
4. Mở folder đó bằng VS Code.
5. Mở Terminal và chạy:

```powershell
git status
git add .
git commit -m "Add Chinese and redesign UI"
git push
```

6. Chờ Streamlit redeploy khoảng vài chục giây đến vài phút.
7. Mở lại:

`https://moun-ai-transcribe.streamlit.app`

và bấm Ctrl + F5 để tải lại giao diện mới.

## Nếu muốn test local trước

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Test:

- upload MP3/MP4
- chọn Tiếng Trung
- chuyển thành văn bản
- tải TXT/Word/PDF/SRT

Sau khi local chạy ổn mới `git push`.
