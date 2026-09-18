from __future__ import annotations

import os
import re
import tempfile
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from faster_whisper import WhisperModel
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


# =========================================================
# CẤU HÌNH ỨNG DỤNG
# =========================================================
APP_NAME = "Moun AI Transcribe"
MODEL_NAME = "base"
MAX_FILE_MB = 200
SUPPORTED_TYPES = ["mp3", "wav", "m4a", "mp4", "webm", "ogg", "flac"]

LANGUAGES = {
    "✨ Tự động nhận diện": None,
    "🇻🇳 Tiếng Việt": "vi",
    "🇬🇧 English": "en",
    "🇱🇦 ພາສາລາວ / Tiếng Lào": "lo",
    "🇹🇭 ภาษาไทย / Tiếng Thái": "th",
    "🇨🇳 中文 / Tiếng Trung": "zh",
}

LANGUAGE_DISPLAY = {
    "vi": "🇻🇳 Tiếng Việt",
    "en": "🇬🇧 English",
    "lo": "🇱🇦 ພາສາລາວ / Tiếng Lào",
    "th": "🇹🇭 ภาษาไทย / Tiếng Thái",
    "zh": "🇨🇳 中文 / Tiếng Trung",
}

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# GIAO DIỆN
# =========================================================
def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #163247;
            --muted: #607786;
            --teal: #16b8a6;
            --blue: #3b82f6;
            --gold: #f5c451;
            --card: rgba(255,255,255,.76);
            --line: rgba(29, 109, 116, .12);
        }

        .stApp {
            background:
                radial-gradient(circle at 6% 6%, rgba(245,196,81,.22), transparent 26%),
                radial-gradient(circle at 96% 7%, rgba(22,184,166,.20), transparent 28%),
                radial-gradient(circle at 75% 86%, rgba(59,130,246,.10), transparent 30%),
                linear-gradient(135deg, #fffaf0 0%, #f5fffc 44%, #f4f7ff 100%);
            color: var(--ink);
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #eefaf6 0%, #eef6ff 100%);
            border-right: 1px solid rgba(31,92,100,.08);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            padding: 34px 36px;
            border-radius: 30px;
            color: #fff;
            background: linear-gradient(120deg, #f1bd4d 0%, #69c790 46%, #20b9b1 100%);
            box-shadow: 0 22px 60px rgba(27,117,112,.18);
            margin-bottom: 20px;
            isolation: isolate;
        }

        .hero::before,
        .hero::after {
            content: "";
            position: absolute;
            border-radius: 999px;
            background: rgba(255,255,255,.14);
            z-index: -1;
            animation: floatBlob 8s ease-in-out infinite;
        }

        .hero::before {
            width: 190px;
            height: 190px;
            right: -40px;
            top: -55px;
        }

        .hero::after {
            width: 120px;
            height: 120px;
            right: 140px;
            bottom: -55px;
            animation-delay: 1.5s;
        }

        @keyframes floatBlob {
            0%, 100% { transform: translateY(0px) scale(1); }
            50% { transform: translateY(10px) scale(1.05); }
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,.19);
            border: 1px solid rgba(255,255,255,.28);
            backdrop-filter: blur(8px);
            font-size: .88rem;
            font-weight: 700;
            margin-bottom: 14px;
        }

        .hero-title {
            font-size: clamp(2.35rem, 5vw, 4rem);
            line-height: .98;
            letter-spacing: -.035em;
            margin: 0 0 14px 0;
            font-weight: 850;
        }

        .hero-text {
            font-size: 1.08rem;
            line-height: 1.75;
            max-width: 850px;
            margin: 0;
            opacity: .98;
        }

        .language-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 18px;
        }

        .lang-chip {
            padding: 7px 11px;
            border-radius: 999px;
            background: rgba(255,255,255,.16);
            border: 1px solid rgba(255,255,255,.22);
            font-size: .84rem;
            font-weight: 650;
        }

        .feature-card {
            height: 100%;
            min-height: 175px;
            padding: 22px;
            border-radius: 23px;
            background: var(--card);
            border: 1px solid var(--line);
            box-shadow: 0 12px 32px rgba(22,73,89,.07);
            backdrop-filter: blur(12px);
            transition: transform .18s ease, box-shadow .18s ease;
        }

        .feature-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 18px 42px rgba(22,73,89,.11);
        }

        .feature-icon {
            width: 44px;
            height: 44px;
            display: grid;
            place-items: center;
            border-radius: 14px;
            font-size: 1.35rem;
            background: linear-gradient(135deg, rgba(245,196,81,.24), rgba(22,184,166,.18));
            margin-bottom: 14px;
        }

        .feature-card h3 {
            margin: 0 0 9px 0;
            color: var(--ink);
            font-size: 1.22rem;
        }

        .feature-card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.65;
            font-size: .96rem;
        }

        .section-kicker {
            color: #0e927f;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-size: .78rem;
            margin-top: .8rem;
            margin-bottom: .2rem;
        }

        .section-title {
            color: var(--ink);
            font-size: clamp(1.55rem, 3vw, 2rem);
            font-weight: 850;
            margin: 0 0 .35rem 0;
            letter-spacing: -.02em;
        }

        .section-note {
            color: var(--muted);
            line-height: 1.65;
            margin-bottom: .95rem;
        }

        .privacy-card {
            margin-top: .8rem;
            padding: 14px 15px;
            border-radius: 16px;
            background: rgba(255,255,255,.64);
            border: 1px solid rgba(22,184,166,.14);
            color: #466274;
            line-height: 1.55;
            font-size: .9rem;
        }

        .info-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0,1fr));
            gap: 12px;
            margin: 14px 0 8px 0;
        }

        .info-pill {
            padding: 13px 14px;
            border-radius: 16px;
            background: rgba(255,255,255,.68);
            border: 1px solid rgba(22,184,166,.10);
            color: #436071;
            font-size: .9rem;
        }

        div[data-testid="stFileUploader"] {
            background: rgba(255,255,255,.76);
            border-radius: 24px;
            padding: 12px 14px 6px 14px;
            border: 1.5px dashed rgba(22,184,166,.40);
            box-shadow: 0 12px 32px rgba(22,73,89,.05);
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: rgba(247,255,253,.74);
            border-radius: 18px;
        }

        div[data-testid="stButton"] button,
        div[data-testid="stDownloadButton"] button {
            border-radius: 15px !important;
            min-height: 46px;
            font-weight: 800 !important;
            transition: transform .14s ease, filter .14s ease, box-shadow .14s ease;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            border: none !important;
            color: #fff !important;
            background: linear-gradient(135deg, #17ae9c 0%, #3184ef 100%) !important;
            box-shadow: 0 10px 24px rgba(49,132,239,.18);
        }

        div[data-testid="stButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover {
            transform: translateY(-1px);
            filter: brightness(1.02);
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 18px !important;
            border: 1px solid rgba(28,112,123,.14) !important;
            background: rgba(255,255,255,.80) !important;
            color: #17364a !important;
            line-height: 1.7 !important;
            font-size: 1rem !important;
        }

        .footer-card {
            margin-top: 1.6rem;
            padding: 16px 18px;
            border-radius: 18px;
            background: rgba(255,255,255,.56);
            border: 1px solid rgba(25,96,109,.08);
            text-align: center;
            color: #6b7f8c;
            font-size: .88rem;
        }

        @media (max-width: 900px) {
            .main .block-container { padding-left: 1rem; padding-right: 1rem; }
            .hero { padding: 28px 24px; border-radius: 24px; }
            .info-strip { grid-template-columns: 1fr; }
            .feature-card { min-height: 0; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_custom_css()

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">✨ AI Speech-to-Text • Word • PDF • SRT</div>
        <div class="hero-title">🎙️ Moun AI Transcribe</div>
        <p class="hero-text">
            Chuyển âm thanh và video thành văn bản bằng AI, chỉnh sửa trực tiếp trên web,
            sau đó tải về TXT, Word, PDF hoặc phụ đề SRT. Thiết kế dành cho học tập,
            bài giảng, phỏng vấn và công việc hằng ngày.
        </p>
        <div class="language-row">
            <span class="lang-chip">🇻🇳 Việt</span>
            <span class="lang-chip">🇬🇧 English</span>
            <span class="lang-chip">🇱🇦 ລາວ</span>
            <span class="lang-chip">🇹🇭 ไทย</span>
            <span class="lang-chip">🇨🇳 中文</span>
            <span class="lang-chip">✨ Auto Detect</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Nhận diện bằng AI</h3>
            <p>faster-whisper xử lý trực tiếp trên CPU, không cần OpenAI API key và không tính phí theo từng phút.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🌏</div>
            <h3>5 ngôn ngữ + Auto</h3>
            <p>Chọn Việt, Anh, Lào, Thái, Trung hoặc để AI tự nhận diện ngôn ngữ trong file.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <h3>Xuất nhiều định dạng</h3>
            <p>Chỉnh transcript trước khi tải TXT, DOCX, PDF; đồng thời tạo SRT có timestamp từ kết quả AI.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")


# =========================================================
# HÀM XỬ LÝ
# =========================================================
@st.cache_resource(show_spinner=False)
def load_model() -> WhisperModel:
    """Tải model một lần và dùng lại trong cùng phiên server."""
    return WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")


def format_clock(seconds: float) -> str:
    total = max(0, int(seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_srt_time(seconds: float) -> str:
    milliseconds = max(0, int(round(seconds * 1000)))
    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000
    minutes = milliseconds // 60_000
    milliseconds %= 60_000
    secs = milliseconds // 1000
    ms = milliseconds % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def safe_stem(filename: str) -> str:
    stem = Path(filename).stem.strip() or "transcript"
    stem = re.sub(r"[^\w\- .]+", "_", stem, flags=re.UNICODE)
    return stem[:80].strip(" ._") or "transcript"


def display_language(code: str | None) -> str:
    if not code:
        return "Không xác định"
    return LANGUAGE_DISPLAY.get(code, code.upper())


def make_docx(text: str, source_name: str, detected_language: str) -> bytes:
    doc = Document()

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Arial"
    normal_style.font.size = Pt(11)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("MOUN AI TRANSCRIBE")
    run.bold = True
    run.font.size = Pt(19)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = subtitle.add_run("Văn bản chuyển từ âm thanh / video")
    sub_run.bold = True
    sub_run.font.size = Pt(13)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_run = meta.add_run(f"Nguồn: {source_name}  •  Ngôn ngữ: {detected_language}")
    meta_run.italic = True
    meta_run.font.size = Pt(9.5)

    doc.add_paragraph("")
    for line in text.splitlines():
        if line.strip():
            p = doc.add_paragraph(line.strip())
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
        else:
            doc.add_paragraph("")

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def find_unicode_font(language_code: str | None) -> str | None:
    language_specific = {
        "lo": [
            "/usr/share/fonts/truetype/noto/NotoSansLao-Regular.ttf",
            r"C:\Windows\Fonts\NotoSansLao-Regular.ttf",
        ],
        "th": [
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
            r"C:\Windows\Fonts\NotoSansThai-Regular.ttf",
        ],
    }

    common = [
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]

    candidates = language_specific.get(language_code or "", []) + common
    for font_path in candidates:
        if os.path.exists(font_path):
            return font_path
    return None


def register_pdf_font(language_code: str | None) -> str:
    # ReportLab có CID font tích hợp cho tiếng Trung, không cần nhúng file font.
    if language_code == "zh":
        font_name = "STSong-Light"
        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        return font_name

    font_path = find_unicode_font(language_code)
    if not font_path:
        raise RuntimeError(
            "Máy chủ không tìm thấy font Unicode phù hợp để tạo PDF. "
            "Bạn vẫn có thể tải TXT, Word và SRT."
        )

    font_name = f"AppUnicodeFont_{language_code or 'default'}"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    return font_name


def make_pdf(
    text: str,
    source_name: str,
    detected_language_code: str,
    detected_language_display: str,
) -> bytes:
    font_name = register_pdf_font(detected_language_code)

    buffer = BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Moun AI Transcript",
        author=APP_NAME,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AppTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor="#17364A",
    )
    meta_style = ParagraphStyle(
        "AppMeta",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor="#667985",
        spaceAfter=14,
    )
    body_style = ParagraphStyle(
        "AppBody",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=11,
        leading=17,
        spaceAfter=7,
        textColor="#1E3747",
    )

    story = [
        Paragraph("MOUN AI TRANSCRIBE", title_style),
        Paragraph("Văn bản chuyển từ âm thanh / video", title_style),
        Paragraph(
            xml_escape(f"Nguồn: {source_name} • Ngôn ngữ: {detected_language_display}"),
            meta_style,
        ),
        Spacer(1, 4),
    ]

    for line in text.splitlines():
        if line.strip():
            story.append(Paragraph(xml_escape(line.strip()), body_style))
        else:
            story.append(Spacer(1, 8))

    pdf.build(story)
    return buffer.getvalue()


def make_srt(segments: list[dict]) -> str:
    blocks: list[str] = []
    index = 1
    for segment in segments:
        text = segment["text"].strip()
        if not text:
            continue
        blocks.append(
            f"{index}\n"
            f"{format_srt_time(segment['start'])} --> {format_srt_time(segment['end'])}\n"
            f"{text}"
        )
        index += 1
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def transcribe_file(
    file_path: str,
    language_code: str | None,
    with_timestamps: bool,
    progress_bar,
    status_box,
):
    status_box.info("🧠 Đang tải mô hình AI...")
    model = load_model()
    status_box.info("🎧 Đang nghe và nhận diện giọng nói...")

    segments_generator, info = model.transcribe(
        file_path,
        language=language_code,
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
    )

    collected: list[dict] = []
    text_lines: list[str] = []
    duration = max(float(info.duration or 0), 1.0)

    for segment in segments_generator:
        segment_text = segment.text.strip()
        if not segment_text:
            continue

        item = {
            "start": float(segment.start),
            "end": float(segment.end),
            "text": segment_text,
        }
        collected.append(item)

        if with_timestamps:
            text_lines.append(f"[{format_clock(segment.start)}] {segment_text}")
        else:
            text_lines.append(segment_text)

        percent = min(int((float(segment.end) / duration) * 100), 99)
        progress_bar.progress(percent)

    progress_bar.progress(100)
    status_box.success("✅ Hoàn thành nhận diện.")

    detected = str(info.language or "unknown")
    probability = float(info.language_probability or 0.0)
    return "\n".join(text_lines), collected, detected, probability


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ Cài đặt")
    st.caption("Tùy chỉnh trước khi bắt đầu chuyển đổi.")

    language_label = st.selectbox(
        "🌐 Ngôn ngữ trong file",
        options=list(LANGUAGES.keys()),
        index=0,
        help="Nếu không chắc, hãy để Tự động nhận diện.",
    )

    with_timestamps = st.toggle(
        "⏱️ Thêm thời gian vào văn bản",
        value=False,
        help="Ví dụ: [00:01:12] Nội dung...",
    )

    st.divider()
    st.markdown("### 🤖 Hệ thống")
    st.caption(f"Model: Whisper `{MODEL_NAME}`")
    st.caption("Thiết bị: CPU • int8")
    st.caption(f"Giới hạn upload: {MAX_FILE_MB} MB")

    st.markdown(
        """
        <div class="privacy-card">
            <b>🔐 Quyền riêng tư</b><br><br>
            File chỉ được ghi tạm trong lúc xử lý và code sẽ cố gắng xóa file tạm sau khi hoàn tất.
            Ứng dụng hiện không có database lưu lịch sử transcript.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="privacy-card">
            <b>💡 Mẹo</b><br><br>
            Âm thanh rõ, ít tạp âm và giọng nói đủ lớn sẽ giúp kết quả chính xác hơn.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# UPLOAD + XỬ LÝ
# =========================================================
st.markdown('<div class="section-kicker">Bước 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Chọn file âm thanh hoặc video</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-note">Kéo thả file vào khu vực bên dưới hoặc bấm Browse files. Hỗ trợ MP3, WAV, M4A, MP4, WEBM, OGG và FLAC.</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Tải file lên",
    type=SUPPORTED_TYPES,
    help="Giới hạn theo cấu hình hiện tại là 200 MB mỗi file.",
    label_visibility="collapsed",
)

if uploaded_file is None:
    st.markdown(
        """
        <div class="info-strip">
            <div class="info-pill">① Upload file</div>
            <div class="info-pill">② AI chuyển thành văn bản</div>
            <div class="info-pill">③ Sửa và tải TXT / Word / PDF / SRT</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="footer-card">Moun AI Transcribe • faster-whisper • Không cần API key</div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

file_size_mb = uploaded_file.size / (1024 * 1024)
if file_size_mb > MAX_FILE_MB:
    st.error(f"File lớn hơn {MAX_FILE_MB} MB. Hãy dùng file nhỏ hơn.")
    st.stop()

signature = f"{uploaded_file.name}:{uploaded_file.size}"
if st.session_state.get("upload_signature") != signature:
    st.session_state["upload_signature"] = signature
    for key in [
        "transcript_text",
        "edited_text",
        "segments",
        "detected_language",
        "language_probability",
    ]:
        st.session_state.pop(key, None)

info_col1, info_col2, info_col3 = st.columns([2.2, 1, 1])
with info_col1:
    st.info(f"📁 **{uploaded_file.name}**")
with info_col2:
    st.info(f"💾 **{file_size_mb:.2f} MB**")
with info_col3:
    st.info(f"🌐 **{language_label}**")

suffix = Path(uploaded_file.name).suffix.lower()
if suffix in {".mp4", ".webm"}:
    st.video(uploaded_file)
else:
    st.audio(uploaded_file)

st.markdown('<div class="section-kicker">Bước 2</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Chuyển thành văn bản bằng AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-note">Lần đầu server tải model có thể lâu hơn. Sau đó model được cache để các lần tiếp theo nhanh hơn.</div>',
    unsafe_allow_html=True,
)

button_col, clear_col = st.columns([3.2, 1])
with button_col:
    start = st.button(
        "✨ Chuyển thành văn bản",
        type="primary",
        use_container_width=True,
    )
with clear_col:
    if st.button("🗑️ Xóa kết quả", use_container_width=True):
        for key in [
            "transcript_text",
            "edited_text",
            "segments",
            "detected_language",
            "language_probability",
        ]:
            st.session_state.pop(key, None)
        st.rerun()

if start:
    temp_path = None
    try:
        progress = st.progress(0)
        status = st.empty()
        status.info("📦 Đang chuẩn bị file...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix or ".media") as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_path = tmp.name

        transcript, segments, detected, probability = transcribe_file(
            temp_path,
            LANGUAGES[language_label],
            with_timestamps,
            progress,
            status,
        )

        if not transcript.strip():
            st.warning("Không nhận diện được lời nói rõ ràng trong file này.")
        else:
            st.session_state["transcript_text"] = transcript
            st.session_state["edited_text"] = transcript
            st.session_state["segments"] = segments
            st.session_state["detected_language"] = detected
            st.session_state["language_probability"] = probability
            st.success("🎉 Chuyển đổi thành công! Bạn có thể kiểm tra và chỉnh sửa nội dung bên dưới.")

    except Exception as exc:
        st.error("Không thể xử lý file. Chi tiết lỗi:")
        st.code(str(exc))
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


# =========================================================
# KẾT QUẢ + XUẤT FILE
# =========================================================
if st.session_state.get("transcript_text"):
    detected_language_code = st.session_state.get("detected_language", "unknown")
    detected_language_name = display_language(detected_language_code)
    probability = st.session_state.get("language_probability", 0.0)
    segments = st.session_state.get("segments", [])

    st.markdown('<div class="section-kicker">Bước 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Kiểm tra và chỉnh sửa</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-note">AI nhận diện: <b>{detected_language_name}</b> • Độ tin cậy khoảng <b>{probability * 100:.1f}%</b>. Bạn có thể sửa trực tiếp văn bản trước khi tải.</div>',
        unsafe_allow_html=True,
    )

    edited_text = st.text_area(
        "Nội dung",
        key="edited_text",
        height=430,
        label_visibility="collapsed",
    )

    char_count = len(edited_text)
    word_count = len(edited_text.split())
    st.caption(f"✍️ {word_count:,} từ • {char_count:,} ký tự")

    st.markdown('<div class="section-kicker">Bước 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Tải kết quả</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">TXT, Word và PDF dùng nội dung bạn đang chỉnh sửa. SRT giữ các đoạn và timestamp từ kết quả AI ban đầu.</div>',
        unsafe_allow_html=True,
    )

    base_name = safe_stem(uploaded_file.name)
    txt_bytes = edited_text.encode("utf-8")
    docx_bytes = make_docx(edited_text, uploaded_file.name, detected_language_name)
    srt_text = make_srt(segments)

    pdf_bytes = None
    pdf_error = None
    try:
        pdf_bytes = make_pdf(
            edited_text,
            uploaded_file.name,
            detected_language_code,
            detected_language_name,
        )
    except Exception as exc:
        pdf_error = str(exc)

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.download_button(
            "⬇️ TXT",
            data=txt_bytes,
            file_name=f"{base_name}.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Word",
            data=docx_bytes,
            file_name=f"{base_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with d3:
        if pdf_bytes is not None:
            st.download_button(
                "⬇️ PDF",
                data=pdf_bytes,
                file_name=f"{base_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button("PDF chưa khả dụng", disabled=True, use_container_width=True)
    with d4:
        st.download_button(
            "⬇️ SRT",
            data=srt_text.encode("utf-8"),
            file_name=f"{base_name}.srt",
            mime="application/x-subrip",
            use_container_width=True,
            disabled=not bool(srt_text.strip()),
        )

    if pdf_error:
        st.warning(f"PDF chưa tạo được: {pdf_error}")

    with st.expander("🕒 Xem các đoạn có timestamp"):
        if segments:
            for item in segments:
                st.write(
                    f"`{format_clock(item['start'])} → {format_clock(item['end'])}`  {item['text']}"
                )
        else:
            st.caption("Chưa có dữ liệu đoạn.")

st.markdown(
    """
    <div class="footer-card">
        🎙️ <b>Moun AI Transcribe</b> • faster-whisper • 5 ngôn ngữ + Auto Detect • TXT / DOCX / PDF / SRT<br>
        <span style="opacity:.82">Hosting miễn phí có thể xử lý chậm với file dài hoặc khi nhiều người dùng cùng lúc.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
