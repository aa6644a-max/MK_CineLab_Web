import streamlit as st

_AMBER = "#C09030"
_AMBER_DIM = "#8B6F47"
_BG = "#FAF7F0"
_SURFACE = "#F2EAD6"
_SURFACE2 = "#E8DEC6"
_TEXT = "#2C2010"
_TEXT_MUTED = "rgba(44,32,16,0.55)"
_BORDER = "rgba(150,120,60,0.2)"

_CSS = f"""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');

/* ── 전체 폰트 Pretendard ── */
*, *::before, *::after,
html, body, .stApp, .block-container,
h1, h2, h3, h4, p, span, div, button, input, textarea, select, label {{
    font-family: 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif !important;
}}

/* ── Streamlit 크롬 제거 + 사이드바 완전 숨김 ── */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
.stAppDeployButton {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stStatusWidget"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}}

/* ── 상단 네비게이션 ── */
[data-testid="stPageLink"] a {{
    color: #6B5040 !important;
    text-decoration: none !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 6px 2px 8px !important;
    display: block !important;
    text-align: center !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.2s, border-color 0.2s !important;
    white-space: nowrap !important;
}}
[data-testid="stPageLink"] a:hover {{
    color: {_AMBER} !important;
    border-bottom-color: {_AMBER} !important;
    text-decoration: none !important;
}}
[data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stPageLink"] a.active {{
    color: {_AMBER} !important;
    border-bottom: 2px solid {_AMBER} !important;
    font-weight: 700 !important;
}}

/* ── 전체 앱 배경 ── */
.stApp {{
    background-color: {_BG};
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
    color: #6B5040 !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    padding: 6px 12px !important;
    border: none !important;
}}
[data-baseweb="tab"]:hover {{
    color: {_TEXT} !important;
    background: rgba(192,144,48,0.1) !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background: {_AMBER} !important;
    color: #fff !important;
    font-weight: 700 !important;
}}
[data-baseweb="tab-highlight"] {{ display: none !important; }}
[data-baseweb="tab-border"] {{ display: none !important; }}

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
    background: rgba(192,144,48,0.08) !important;
}}
.stButton > button[kind="primary"] {{
    background: {_AMBER} !important;
    color: #fff !important;
    border-color: {_AMBER} !important;
    font-weight: 700 !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: #a87820 !important;
    color: #fff !important;
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
[data-testid="stMetricLabel"] {{ color: {_TEXT_MUTED} !important; }}
[data-testid="stMetricValue"] {{ color: {_AMBER} !important; }}

/* ── 익스팬더 ── */
[data-testid="stExpander"] {{
    background: {_SURFACE} !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 10px !important;
}}

/* ── 알림 박스 (info/warning/error/success 통일) ── */
[data-testid="stAlert"],
[data-testid="stAlert"] > div,
div[role="alert"] {{
    background-color: {_SURFACE} !important;
    border-radius: 8px !important;
    border: 1px solid {_BORDER} !important;
    border-left: 3px solid {_AMBER} !important;
    color: {_TEXT} !important;
}}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {{
    color: {_TEXT} !important;
}}
[data-testid="stAlert"] svg {{
    fill: {_AMBER} !important;
    color: {_AMBER} !important;
}}

/* ── 코드 블록 ── */
[data-testid="stCodeBlock"] > div {{
    background: #EDE5CE !important;
    border: 1px solid {_BORDER} !important;
    border-radius: 8px !important;
}}

/* ── 제목 ── */
h1, h2, h3 {{
    color: {_TEXT} !important;
    letter-spacing: -0.3px;
}}
h1 {{
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    border-bottom: 1px solid {_BORDER};
    padding-bottom: 12px;
    margin-bottom: 4px !important;
}}
h2 {{
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: {_TEXT} !important;
}}
h3 {{
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: {_TEXT} !important;
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
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] section {{
    background: {_SURFACE} !important;
    border: 1.5px dashed rgba(150,120,60,0.35) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s;
}}
[data-testid="stFileUploader"] > div:hover,
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {_AMBER} !important;
}}
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploader"] section * {{
    color: {_TEXT} !important;
}}
[data-testid="stFileUploader"] small {{
    color: {_TEXT_MUTED} !important;
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

/* ── 스크롤바 ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {_BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {_AMBER_DIM}; }}

/* ── 애니메이션 키프레임 ── */
@keyframes fadeSlideUp {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes inputGlow {{
    0%   {{ box-shadow: 0 0 0 0 rgba(192,144,48,0.45); }}
    60%  {{ box-shadow: 0 0 0 7px rgba(192,144,48,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(192,144,48,0); }}
}}
@keyframes rippleOut {{
    0%   {{ transform: translate(-50%,-50%) scale(0); opacity: 0.5; }}
    100% {{ transform: translate(-50%,-50%) scale(5); opacity: 0; }}
}}

/* ── 페이지/탭 전환 페이드슬라이드 ── */
.block-container {{
    animation: fadeSlideUp 0.35s ease-out both;
}}
[data-baseweb="tab-panel"] > div {{
    animation: fadeSlideUp 0.3s ease-out both;
}}

/* ── 입력 hover lift ── */
.stTextInput, .stTextArea, .stNumberInput, .stSelectbox {{
    transition: transform 0.18s ease;
}}
.stTextInput:hover, .stTextArea:hover,
.stNumberInput:hover, .stSelectbox:hover {{
    transform: translateY(-2px);
}}

/* ── 입력 포커스 글로우 ── */
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {{
    animation: inputGlow 0.55s ease !important;
    border-color: {_AMBER} !important;
    box-shadow: 0 0 0 2px rgba(192,144,48,0.18), 0 4px 12px rgba(192,144,48,0.1) !important;
    transform: translateY(-1px);
    transition: transform 0.18s ease !important;
}}

/* ── 버튼 리플 + 클릭 팝 ── */
.stButton > button {{
    position: relative !important;
    overflow: hidden !important;
    transition: all 0.18s ease !important;
}}
.stButton > button:active {{
    transform: scale(0.97) !important;
}}
.stButton > button::after {{
    content: '' !important;
    position: absolute !important;
    top: 50%; left: 50% !important;
    width: 8px; height: 8px !important;
    background: rgba(255,255,255,0.35) !important;
    border-radius: 50% !important;
    transform: translate(-50%,-50%) scale(0) !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}
.stButton > button:active::after {{
    animation: rippleOut 0.45s ease-out forwards !important;
}}

/* ── 탭 모바일 가로스크롤 ── */
[data-baseweb="tab-list"] {{
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none !important;
    flex-wrap: nowrap !important;
}}
[data-baseweb="tab-list"]::-webkit-scrollbar {{ display: none !important; }}
[data-baseweb="tab"] {{
    flex-shrink: 0 !important;
}}

/* ── 섹션 카드 헤더 (.mk-section-card) ── */
.mk-section-card {{
    background: {_SURFACE};
    border-radius: 14px;
    padding: 20px 22px 16px;
    margin-bottom: 22px;
    border-left: 4px solid {_AMBER};
    border: 1px solid {_BORDER};
    border-left: 4px solid {_AMBER};
    animation: fadeSlideUp 0.3s ease-out both;
}}
.mk-section-card .sc-icon {{
    font-size: 1.6rem; margin-bottom: 6px; display: block;
}}
.mk-section-card .sc-title {{
    font-size: 1.05rem; font-weight: 700; color: {_TEXT}; margin-bottom: 4px;
}}
.mk-section-card .sc-desc {{
    font-size: 0.85rem; color: {_TEXT_MUTED}; line-height: 1.55;
}}
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


PREVIEW_FONT_STYLE = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css">
<style>
  * { font-family: 'Pretendard Variable', 'Pretendard', -apple-system, sans-serif !important; }
</style>
"""
