import streamlit as st

_AMBER = "#D4A853"
_AMBER_DIM = "#8B6F47"
_BG = "#1C1410"
_SURFACE = "#241A14"
_SURFACE2 = "#2E2018"
_TEXT = "#F5F0E8"
_TEXT_MUTED = "rgba(245,240,232,0.55)"
_BORDER = "rgba(212,168,83,0.15)"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700&display=swap');

/* ── Streamlit 크롬 최소화 (사이드바 토글은 유지) ── */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
.stAppDeployButton {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stStatusWidget"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
/* 헤더 투명화 — 토글 버튼은 살림 */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border-bottom: none !important;
}}
/* 사이드바 닫혔을 때 토글 버튼 강제 표시 */
[data-testid="stSidebarCollapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: {_SURFACE} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 0 8px 8px 0 !important;
}}
[data-testid="stSidebarCollapsedControl"] svg {{
    fill: {_AMBER} !important;
}}
.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}}

/* ── 전체 앱 배경 ── */
.stApp {{
    background-color: {_BG};
}}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {{
    background-color: #130E0A !important;
    border-right: 1px solid {_BORDER};
}}
[data-testid="stSidebarNav"] a {{
    color: {_TEXT_MUTED} !important;
    font-size: 14px;
    letter-spacing: 0.3px;
    transition: color 0.2s;
}}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-selected="true"] {{
    color: {_AMBER} !important;
}}

/* ── 탭 ── */
[data-baseweb="tab-list"] {{
    background-color: {_SURFACE} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid {_BORDER};
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    color: {_TEXT_MUTED} !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    padding: 6px 12px !important;
    border: none !important;
}}
[data-baseweb="tab"]:hover {{
    color: {_TEXT} !important;
    background: rgba(212,168,83,0.08) !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background: {_AMBER} !important;
    color: #1a0f00 !important;
    font-weight: 700 !important;
}}
[data-baseweb="tab-highlight"] {{
    display: none !important;
}}
[data-baseweb="tab-border"] {{
    display: none !important;
}}

/* ── 버튼 ── */
.stButton > button {{
    background: {_SURFACE2} !important;
    color: {_TEXT} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}}
.stButton > button:hover {{
    border-color: {_AMBER} !important;
    color: {_AMBER} !important;
    background: rgba(212,168,83,0.08) !important;
}}
.stButton > button[kind="primary"] {{
    background: {_AMBER} !important;
    color: #1a0f00 !important;
    border-color: {_AMBER} !important;
    font-weight: 700 !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: #c49340 !important;
    color: #1a0f00 !important;
}}

/* ── 입력 필드 ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {{
    background-color: {_SURFACE} !important;
    color: {_TEXT} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 8px !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {_AMBER} !important;
    box-shadow: 0 0 0 1px {_AMBER}40 !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: {_TEXT_MUTED} !important;
}}

/* ── 셀렉트박스 / 슬라이더 ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {{
    background-color: {_SURFACE} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 8px !important;
    color: {_TEXT} !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {{
    background: {_AMBER} !important;
}}

/* ── 컨테이너/카드 ── */
[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background-color: {_SURFACE} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 12px !important;
}}

/* ── 메트릭 ── */
[data-testid="stMetric"] {{
    background: {_SURFACE} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 10px !important;
    padding: 12px !important;
}}
[data-testid="stMetricLabel"] {{
    color: {_TEXT_MUTED} !important;
}}
[data-testid="stMetricValue"] {{
    color: {_AMBER} !important;
}}

/* ── 익스팬더 ── */
[data-testid="stExpander"] {{
    background: {_SURFACE} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 10px !important;
}}

/* ── 알림 박스 ── */
[data-testid="stAlert"] {{
    border-radius: 8px !important;
    border-left: 3px solid {_AMBER} !important;
}}

/* ── 코드 블록 ── */
[data-testid="stCodeBlock"] > div {{
    background: #0D0A07 !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 8px !important;
}}

/* ── 제목 ── */
h1, h2, h3 {{
    color: {_TEXT} !important;
    letter-spacing: -0.3px;
}}
h1 {{
    font-size: 1.8rem !important;
    border-bottom: 1px solid {_BORDER};
    padding-bottom: 12px;
    margin-bottom: 4px !important;
}}

/* ── 구분선 ── */
hr {{
    border-color: {_BORDER} !important;
    opacity: 1 !important;
}}

/* ── 데이터에디터 ── */
[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {{
    border: 1px solid {_BORDER} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] > div {{
    background: {_SURFACE} !important;
    border: 1.5px dashed {_BORDER} !important;
    border-radius: 10px !important;
    transition: border-color 0.2s;
}}
[data-testid="stFileUploader"] > div:hover {{
    border-color: {_AMBER} !important;
}}

/* ── 캡션/서브텍스트 ── */
[data-testid="stCaptionContainer"] p,
.stCaption {{
    color: {_TEXT_MUTED} !important;
}}

/* ── 스피너 ── */
[data-testid="stSpinner"] > div {{
    border-top-color: {_AMBER} !important;
}}

/* ── 토스트 ── */
[data-testid="stToast"] {{
    background: {_SURFACE2} !important;
    border: 1px solid {_BORDER} !important;
    color: {_TEXT} !important;
}}

/* ── 페이지 링크 ── */
[data-testid="stPageLink"] a {{
    color: {_AMBER} !important;
    text-decoration: none !important;
}}
[data-testid="stPageLink"] a:hover {{
    color: #c49340 !important;
}}

/* ── 스크롤바 ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {_BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {_AMBER_DIM}; }}
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


PREVIEW_FONT_STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  body {{ font-family: 'Noto Serif KR', serif !important; }}
  div, p, span, li, td {{ font-family: 'Noto Serif KR', serif !important; }}
</style>
"""
