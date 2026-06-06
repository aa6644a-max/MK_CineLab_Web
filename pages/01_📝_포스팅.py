import streamlit as st
import base64
import re
import pdfplumber
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tmdb_client import TMDBClient
from claude_client import ClaudeClient
from prompt_builder import PromptBuilder
from DailyPromptBuilder import DailyPromptBuilder
from html_formatter import HTMLFormatter
from naver_client import NaverClient
from db_manager import DBManager
from rss_client import RSSClient

load_dotenv()

st.set_page_config(page_title="MK Studio · 포스팅", page_icon="✦", layout="centered")

from mk_theme import inject_css, PREVIEW_FONT_STYLE
inject_css()

from navbar import render_navbar
render_navbar()

# API keys for movie search (raw HTTP)
KOBIS_API_KEY  = (st.secrets.get("KOBIS_API_KEY")         or os.getenv("KOBIS_API_KEY")         or "").strip().strip("'\"")
TMDB_SEARCH_KEY = (st.secrets.get("TMDB_API_KEY")         or os.getenv("TMDB_API_KEY")           or "").strip().strip("'\"")
OMDB_API_KEY   = (st.secrets.get("OMDB_API_KEY")          or os.getenv("OMDB_API_KEY")           or "").strip().strip("'\"")
NAVER_ID       = (st.secrets.get("NAVER_CLIENT_ID")       or os.getenv("NAVER_CLIENT_ID")        or "").strip().strip("'\"")
NAVER_SECRET   = (st.secrets.get("NAVER_CLIENT_SECRET")   or os.getenv("NAVER_CLIENT_SECRET")    or "").strip().strip("'\"")


# ─────────────────────────────────────────────
# HTML 렌더링 헬퍼
# ─────────────────────────────────────────────
def section_card(icon, title, desc=""):
    desc_html = f'<div class="sc-desc">{desc}</div>' if desc else ""
    st.markdown(f"""
    <div class="mk-section-card">
      <span class="sc-icon">{icon}</span>
      <div class="sc-title">{title}</div>
      {desc_html}
    </div>""", unsafe_allow_html=True)


def parse_titles_from_html(html_text):
    match = re.search(r'<!--\s*TITLES:\s*(.+?)\s*-->', html_text, re.DOTALL)
    if not match:
        return []
    return [t.strip() for t in match.group(1).split('||') if t.strip()]


def show_isolated_html(html_str, height=1000, scrolling=True):
    clean_html = html_str.replace("```html\n", "").replace("```html", "").replace("```", "")
    if "<html" not in clean_html.lower():
        clean_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;">
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css" rel="stylesheet">
<style>
*{{box-sizing:border-box;}}
body{{margin:0;padding:16px;font-family:'Pretendard Variable','Pretendard',sans-serif;max-width:720px;margin:0 auto;}}
img{{max-width:100% !important;height:auto !important;display:block;margin:12px auto;border-radius:6px;}}
</style>
</head>
<body>
{clean_html}
</body>
</html>"""
    b64 = base64.b64encode(clean_html.encode("utf-8")).decode("utf-8")
    scroll_css = "overflow:auto;" if scrolling else "overflow:hidden;"
    iframe = f'<iframe src="data:text/html;charset=utf-8;base64,{b64}" width="100%" height="{height}" style="border:none;{scroll_css}"></iframe>'
    st.markdown(iframe, unsafe_allow_html=True)


def render_preview_with_photos(html_str, photos):
    from PIL import Image
    import io as _io
    clean = html_str.replace("```html\n", "").replace("```html", "").replace("```", "")

    # 사진 → base64 data URI (최대 900px 리사이즈)
    data_uris = []
    for photo in photos:
        photo.seek(0)
        try:
            img = Image.open(photo)
            if img.width > 900:
                ratio = 900 / img.width
                img = img.resize((900, int(img.height * ratio)), Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            buf = _io.BytesIO()
            img.save(buf, format="JPEG", quality=82)
            b64str = base64.b64encode(buf.getvalue()).decode("utf-8")
            data_uris.append(f"data:image/jpeg;base64,{b64str}")
        except Exception:
            photo.seek(0)
            b64str = base64.b64encode(photo.read()).decode("utf-8")
            data_uris.append(f"data:image/jpeg;base64,{b64str}")

    # [PHOTO_N] 플레이스홀더 교체
    for i, uri in enumerate(data_uris):
        img_tag = f'<div style="text-align:center;margin:20px 0;"><img src="{uri}" style="max-width:100%;max-height:600px;object-fit:contain;border-radius:8px;" alt="사진{i+1}"></div>'
        clean = clean.replace(f"[PHOTO_{i+1}]", img_tag)

    # 잔여 외부 http 이미지 URL도 data URI로 대체
    for uri in data_uris:
        img_tag = f'<div style="text-align:center;margin:20px 0;"><img src="{uri}" style="max-width:100%;max-height:600px;object-fit:contain;border-radius:8px;"></div>'
        pattern_div = r'<div[^>]*>\s*<img[^>]*src=["\']https?://[^"\'>\s]+["\'][^>]*>\s*</div>'
        pattern_img = r'<img[^>]*src=["\']https?://[^"\'>\s]+["\'][^>]*>'
        if re.search(pattern_div, clean):
            clean = re.sub(pattern_div, img_tag, clean, count=1)
        elif re.search(pattern_img, clean):
            clean = re.sub(pattern_img, img_tag, clean, count=1)

    show_isolated_html(clean, height=2500)




def strip_images_for_copy(html_str, photo_count):
    result = html_str
    for i in range(photo_count):
        replacement = f'<p style="text-align:center;color:#e53e3e;font-weight:bold;margin:30px 0;">[📸 블로그 에디터에서 이곳에 사진 {i+1}을 직접 업로드해주세요]</p>'
        result = result.replace(f"[PHOTO_{i+1}]", replacement)
        pattern_div = r'<div[^>]*>\s*<img[^>]*src=["\']https?://[^"\'>\s]+["\'][^>]*>\s*</div>'
        pattern_img = r'<img[^>]*src=["\']https?://[^"\'>\s]+["\'][^>]*>'
        if re.search(pattern_div, result):
            result = re.sub(pattern_div, replacement, result, count=1)
        elif re.search(pattern_img, result):
            result = re.sub(pattern_img, replacement, result, count=1)
    return result


# ─────────────────────────────────────────────
# 영화 검색 HTTP 함수 (raw API calls)
# ─────────────────────────────────────────────
def fetch_daily_boxoffice():
    if not KOBIS_API_KEY: return []
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOBIS_API_KEY}&targetDt={yesterday}"
    try:
        return requests.get(url).json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
    except:
        return []


def fetch_kobis_search(query):
    if not KOBIS_API_KEY: return []
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={KOBIS_API_KEY}&movieNm={query}"
    try:
        return requests.get(url).json().get("movieListResult", {}).get("movieList", [])
    except:
        return []


def fetch_kobis_detail_and_boxoffice(movie_cd):
    detail_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={KOBIS_API_KEY}&movieCd={movie_cd}"
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    box_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOBIS_API_KEY}&targetDt={yesterday}"
    try:
        detail = requests.get(detail_url).json().get("movieInfoResult", {}).get("movieInfo", {})
        box_list = requests.get(box_url).json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        stats = next((i for i in box_list if i["movieCd"] == movie_cd), None)
        return detail, stats
    except:
        return {}, None


def fetch_tmdb_search(movie_nm, movie_en, year):
    if not TMDB_SEARCH_KEY: return None, None, "", 0, 0
    headers = {"Authorization": f"Bearer {TMDB_SEARCH_KEY}", "accept": "application/json"}
    queries = [q for q in [movie_nm, movie_en] if q]
    for query in queries:
        for lang in ["ko-KR", "en-US"]:
            for y in [year, ""]:
                url = "https://api.themoviedb.org/3/search/movie"
                params = {"query": query, "language": lang}
                if y: params["year"] = y
                try:
                    res = requests.get(url, headers=headers, params=params).json().get('results', [])
                    if res:
                        movie_id = res[0]['id']
                        detail = requests.get(
                            f"https://api.themoviedb.org/3/movie/{movie_id}",
                            headers=headers,
                            params={"append_to_response": "external_ids", "language": "ko-KR"}
                        ).json()
                        poster = f"https://image.tmdb.org/t/p/w500{detail.get('poster_path')}" if detail.get('poster_path') else None
                        imdb_id = detail.get('external_ids', {}).get('imdb_id')
                        return poster, imdb_id, detail.get('overview', ""), detail.get('vote_average', 0), detail.get('vote_count', 0)
                except:
                    continue
    return None, None, "", 0, 0


def fetch_naver_plot_fallback(movie_nm):
    if not NAVER_ID: return ""
    url = f"https://openapi.naver.com/v1/search/encyc.json?query={movie_nm}+영화&display=1"
    headers = {"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get('items'):
            return re.sub('<[^<]+?>', '', res['items'][0].get('description', ""))
    except:
        pass
    return "등록된 줄거리 정보가 없습니다."


def fetch_omdb_ratings(imdb_id):
    if not OMDB_API_KEY or not imdb_id: return []
    try:
        res = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}").json()
        return res.get('Ratings', []) if res.get('Response') == 'True' else []
    except:
        return []


def format_money(amount_str):
    try:
        amount = int(amount_str)
        if amount >= 100000000:
            return f"{amount // 100000000:,}억 {(amount % 100000000) // 10000:,}만 원"
        return f"₩{amount:,}"
    except:
        return "정보 없음"


# ─────────────────────────────────────────────
# 엔진 초기화
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_posting_engines():
    return (
        TMDBClient(), ClaudeClient(), PromptBuilder(), DailyPromptBuilder(),
        HTMLFormatter(), NaverClient(), DBManager(), RSSClient()
    )

tmdb, claude_ai, builder, daily_builder, formatter, naver, db, rss = init_posting_engines()


# ─────────────────────────────────────────────
# 세션 스테이트
# ─────────────────────────────────────────────
_defaults = {
    "rev_data": None, "pre_data": None, "cur_data": None, "binge_data": None,
    "daily_html": None, "daily_titles": [],
    "photo_result_html": None, "photo_copy_html": None,
    "photo_uploaded_files": None, "photo_titles": [],
    "place_search_results": None, "selected_place": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
if "cur_entries" not in st.session_state:
    st.session_state.cur_entries = [{"id": i, "t": "", "c": ""} for i in range(3)]
    st.session_state._cur_next_id = 3
if "binge_entries" not in st.session_state:
    st.session_state.binge_entries = [{"id": i} for i in range(3)]
    st.session_state._binge_next_id = 3


def get_recent_references(post_type_filter, limit=2):
    try:
        all_posts = db.get_all_posts()
        filtered = [p[4] for p in all_posts if p[2] == post_type_filter and len(p) > 4 and p[4]]
        if not filtered: return ""
        return "\n\n---\n[이전 글 구분선]\n---\n\n".join(filtered[-limit:])
    except Exception as e:
        print(f"DB 참조 실패: {e}")
        return ""


# ─────────────────────────────────────────────
# 페이지
# ─────────────────────────────────────────────
st.markdown("""
<div style="padding:4px 0 24px;">
  <div style="font-size:11px;font-weight:700;letter-spacing:2px;color:#C09030;text-transform:uppercase;margin-bottom:8px;">MK STUDIO</div>
  <div style="font-size:1.7rem;font-weight:800;color:#2C2010;letter-spacing:-0.4px;line-height:1.15;">포스팅 작업실</div>
  <div style="font-size:0.875rem;color:rgba(44,32,16,0.55);margin-top:7px;line-height:1.6;">AI가 영화 리뷰, 큐레이션, 사진 포스팅까지 모든 과정을 도와드립니다</div>
</div>
""", unsafe_allow_html=True)

tab_pdf, tab_rev, tab_pre, tab_cur, tab_binge, tab_photo, tab_search = st.tabs([
    "📄 PDF 요약", "🎥 영화 리뷰", "📅 개봉 프리뷰",
    "🎬 큐레이션 리스트", "📺 정주행 추천", "📸 사진 포스팅", "🔍 영화 검색"
])


# ==========================================
# [TAB 1] PDF 요약 포스팅
# ==========================================
with tab_pdf:
    section_card("📄", "PDF 자료 기반 초안 생성", "다양한 PDF 자료를 업로드하면 오직 그 내용만 분석해 MK 스타일로 요약합니다.")
    st.info("💡 여러 개의 PDF를 한꺼번에 올릴 수 있습니다. 자료가 많을수록 더 정확한 분석이 가능해요.")

    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "참고할 PDF 파일들을 선택하세요 (중복 선택 가능)",
            type="pdf", accept_multiple_files=True, key="daily_pdf_uploader"
        )
        if uploaded_files:
            st.caption(f"📂 총 {len(uploaded_files)}개의 파일이 선택되었습니다.")
        user_context = st.text_area(
            "이 기록에 담고 싶은 상황이나 생각",
            placeholder="예: 영화 살목지 개봉 전, 실제 장소에 대한 괴담 정보들만 모아서 정리하고 싶습니다. 영화 정보보다는 PDF 속 실화에 집중해 주세요.",
            height=200, key="daily_context"
        )
    with col2:
        post_category = st.text_input("포스팅 카테고리 입력", placeholder="예: ☕ 카페 탐방, 🛠️ 현장 일지 등", key="daily_category_input")
        writing_vibe = st.select_slider("글의 감성 농도", options=["담백하게", "차분하게", "다정하게", "감성 가득", "위트 있게"], value="다정하게", key="daily_vibe")
        st.write("---")
        generate_btn = st.button("✨ MK 스타일 포스팅 생성", type="primary", width='stretch')

    if generate_btn:
        if uploaded_files and user_context and post_category:
            with st.spinner(f"{len(uploaded_files)}개의 PDF 데이터를 분석 중입니다..."):
                combined_text = ""
                for file in uploaded_files:
                    try:
                        with pdfplumber.open(file) as pdf:
                            combined_text += "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                    except Exception as e:
                        st.error(f"{file.name} 읽기 오류: {e}")
                if not combined_text.strip():
                    st.error("PDF에서 텍스트를 추출할 수 없습니다. 이미지로 된 PDF인지 확인해 주세요.")
                else:
                    reference_posts = rss.get_latest_posts_text(limit=3)
                    prompt = daily_builder.build_pdf_summary_prompt(
                        combined_text, f"[{post_category} / {writing_vibe} 분위기] {user_context}", reference_posts
                    )
                    result = claude_ai.generate_post(prompt)
                    st.session_state.daily_titles = parse_titles_from_html(result)
                    st.session_state.daily_html = formatter.wrap_in_table(f"{post_category} 기록", result, post_type="일상")
                    st.success("노트북LM 스타일의 맞춤형 포스팅 생성이 완료되었습니다!")
        else:
            st.warning("PDF 파일, 카테고리, 그리고 추가 맥락을 모두 입력해 주세요.")

    if st.session_state.daily_html:
        st.markdown("---")
        if st.session_state.daily_titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", st.session_state.daily_titles, key="daily_title_select")
                st.code(selected, language=None)
        res_tab1, res_tab2 = st.tabs(["👁️ 블로그 미리보기", "📄 HTML 코드"])
        with res_tab1:
            st.info("외부 정보 없이 민규님이 주신 자료로만 구성된 미리보기입니다.")
            show_isolated_html(st.session_state.daily_html)
        with res_tab2:
            st.code(st.session_state.daily_html, language="html")


# ==========================================
# [TAB 2] 영화 리뷰
# ==========================================
with tab_rev:
    section_card("🎥", "영화 리뷰 생성", "영화 정보와 나의 감상을 바탕으로 네이버 최적화 리뷰를 자동 완성합니다.")
    col1, col2 = st.columns([3, 1])
    with col1: title = st.text_input("리뷰할 영화 제목", key="rev_title")
    with col2: year_input = st.text_input("개봉 연도 (선택)", placeholder="예: 2024", key="rev_year")

    reason_input = st.text_input("영화를 보게 된 계기/관람 이유", placeholder="예: 평소 좋아하는 감독의 신작이라 개봉하자마자 아이맥스로 관람했습니다.", key="rev_reason")
    comment = st.text_area("나의 주관적 감상평", height=150, key="rev_comment")

    if st.button("리뷰 생성", type="primary"):
        if title:
            with st.spinner("영화 정보, 최신 뉴스, 그리고 실시간 네이버 블로그(RSS) 데이터를 수집 중..."):
                year_val = int(year_input) if year_input.isdigit() else None
                movie_info = tmdb.search_movie(title, year=year_val)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(title)
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("리뷰")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts
                    prompt = builder.build_review_prompt(details, comment, reason=reason_input, latest_news=latest_news, reference_posts=reference_posts)
                    result = claude_ai.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result, post_type="리뷰")
                    st.session_state.rev_data = {"title": details['title'], "html": final_html, "titles": titles}
                else:
                    st.error(f"'{title}' 영화를 찾을 수 없습니다.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.rev_data:
        st.success(f"'{st.session_state.rev_data['title']}' 리뷰 생성 완료!")
        titles = st.session_state.rev_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="rev_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 리뷰를 내 취향 DB에 저장하기", key="save_rev_btn"):
            if db.save_post(st.session_state.rev_data['title'], "리뷰", st.session_state.rev_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.rev_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.rev_data['html'])


# ==========================================
# [TAB 3] 개봉 프리뷰
# ==========================================
with tab_pre:
    section_card("📅", "개봉 예정작 프리뷰", "기대작의 정보와 나만의 기대감을 담은 프리뷰 포스팅을 작성합니다.")
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트 (예: 배우 라인업, 감독의 전작 등)", key="pre_point")
    pre_reason_input = st.text_input("프리뷰를 쓰는 이유", placeholder="예: 예고편의 강렬한 분위기에 압도되어 개봉일만 손꼽아 기다리고 있습니다.", key="pre_reason")

    if st.button("프리뷰 생성", type="primary"):
        if p_title:
            with st.spinner("정보 및 실시간 블로그 취향 데이터 수집 중..."):
                movie_info = tmdb.search_movie(p_title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(p_title)
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("프리뷰")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts
                    prompt = builder.build_preview_prompt(details, point, reason=pre_reason_input, latest_news=latest_news, reference_posts=reference_posts)
                    result = claude_ai.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result, post_type="프리뷰")
                    st.session_state.pre_data = {"title": details['title'], "html": final_html, "titles": titles}
                else:
                    st.error("해당하는 영화 정보가 없습니다.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.pre_data:
        st.success("프리뷰 생성 완료!")
        titles = st.session_state.pre_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="pre_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 프리뷰를 내 취향 DB에 저장하기", key="save_pre_btn"):
            if db.save_post(st.session_state.pre_data['title'], "프리뷰", st.session_state.pre_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.pre_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.pre_data['html'])


# ==========================================
# [TAB 4] 큐레이션 리스트
# ==========================================
with tab_cur:
    section_card("🎬", "영화 큐레이션 리스트", "여러 편의 영화를 특정 테마에 맞춰 한 번에 소개하는 포스팅을 작성합니다.")

    cur_theme = st.text_input("포스팅 메인 테마", placeholder="예: 다가오는 2026년 3월 개봉 예정 기대작 정리", key="cur_theme")

    def _cur_add():
        nid = st.session_state._cur_next_id
        st.session_state.cur_entries.append({"id": nid, "t": "", "c": ""})
        st.session_state._cur_next_id = nid + 1

    def _cur_del(eid):
        st.session_state.cur_entries = [e for e in st.session_state.cur_entries if e["id"] != eid]

    st.markdown("""<div style="display:grid;grid-template-columns:1fr 1.4fr 32px;gap:8px;margin-bottom:4px;">
      <span style="font-size:12px;font-weight:600;color:rgba(44,32,16,0.5);">영화 제목</span>
      <span style="font-size:12px;font-weight:600;color:rgba(44,32,16,0.5);">한마디 코멘트 (선택)</span>
      <span></span></div>""", unsafe_allow_html=True)

    for entry in st.session_state.cur_entries:
        eid = entry["id"]
        c1, c2, c3 = st.columns([1, 1.4, 0.18])
        with c1:
            st.text_input("영화 제목", key=f"cur_t_{eid}",
                          placeholder="예: 인터스텔라", label_visibility="collapsed")
        with c2:
            st.text_input("한마디 코멘트", key=f"cur_c_{eid}",
                          placeholder="예: 놀란 감독 최고작", label_visibility="collapsed")
        with c3:
            st.button("✕", key=f"cur_del_{eid}", on_click=_cur_del, args=(eid,))

    st.button("＋ 영화 추가", on_click=_cur_add)

    if st.button("큐레이션 포스팅 생성", type="primary"):
        movie_entries = [
            (st.session_state.get(f"cur_t_{e['id']}", "").strip(),
             st.session_state.get(f"cur_c_{e['id']}", "").strip())
            for e in st.session_state.cur_entries
            if st.session_state.get(f"cur_t_{e['id']}", "").strip()
        ]
        if cur_theme and movie_entries:
            with st.spinner(f"{len(movie_entries)}편의 영화 정보(TMDB)와 뉴스(Naver) 수집 중..."):
                movies_data_text = ""
                for m_title, m_comment in movie_entries:
                    m_info = tmdb.search_movie(m_title)
                    if m_info:
                        details = tmdb.get_movie_details(m_info['id'])
                        latest_news = naver.search_movie_news(m_title, display=2)
                        poster_html = builder._build_image_html(details.get('poster_url'), f"{details.get('title')} 포스터")
                        if not poster_html:
                            poster_html = builder._build_placeholder_html(f"영화 '{details.get('title')}' 메인 포스터")
                        comment_line = f"- [MK의 한마디]: {m_comment}" if m_comment and m_comment != "nan" else ""
                        movies_data_text += f"""
[영화: {details.get('title')}]
- 원제: {details.get('original_title', '정보 없음')}
- 국가: {details.get('country', '정보 없음')}
- 감독: {details.get('director', '')}
- 출연: {details.get('actors', '')}
- 개봉일: {details.get('release_date', '')}
- 줄거리: {details.get('overview', '')}
{comment_line}
- <메인 포스터 HTML 코드>: {poster_html}
- [최신 네이버 뉴스 동향]:
{latest_news}
============================================
"""
                    else:
                        st.warning(f"'{m_title}' 정보를 찾을 수 없어 리스트에서 제외했습니다.")

                if movies_data_text.strip():
                    st.info("Claude가 수집된 데이터를 바탕으로 MK 스타일 원고를 작성하고 있습니다...")
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("리스트")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts
                    prompt = builder.build_curation_prompt(cur_theme, movies_data_text, reference_posts)
                    result = claude_ai.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(cur_theme, result, post_type="리스트")
                    st.session_state.cur_data = {"title": cur_theme, "html": final_html, "titles": titles}
                else:
                    st.error("유효한 영화 정보를 하나도 수집하지 못했습니다. 제목을 정확히 확인해 주세요.")
        elif not cur_theme:
            st.warning("포스팅 메인 테마를 입력해 주세요.")
        else:
            st.warning("영화 제목을 한 편 이상 입력해 주세요.")

    if st.session_state.cur_data:
        st.success("큐레이션 리스트 포스팅 생성 완료!")
        titles = st.session_state.cur_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="cur_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 리스트를 내 취향 DB에 저장하기", key="save_cur_btn"):
            if db.save_post(st.session_state.cur_data['title'], "리스트", st.session_state.cur_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.cur_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.cur_data['html'])


# ==========================================
# [TAB 5] 정주행 추천
# ==========================================
with tab_binge:
    section_card("📺", "정주행 추천 포스팅", "애니메이션·드라마 등 시리즈물을 정주행 관점으로 소개하는 포스팅을 작성합니다.")

    binge_theme = st.text_input("포스팅 메인 테마", placeholder="예: 2025년 상반기 정주행 완료 애니 총결산", key="binge_theme")

    def _binge_add():
        nid = st.session_state._binge_next_id
        st.session_state.binge_entries.append({"id": nid})
        st.session_state._binge_next_id = nid + 1

    def _binge_del(eid):
        st.session_state.binge_entries = [e for e in st.session_state.binge_entries if e["id"] != eid]

    st.markdown('<div style="font-size:12px;font-weight:600;color:rgba(44,32,16,0.5);margin-bottom:4px;">소개할 작품 제목</div>', unsafe_allow_html=True)
    for entry in st.session_state.binge_entries:
        eid = entry["id"]
        c1, c2 = st.columns([1, 0.1])
        with c1:
            st.text_input("작품 제목", key=f"binge_t_{eid}",
                          placeholder="예: 귀멸의 칼날", label_visibility="collapsed")
        with c2:
            st.button("✕", key=f"binge_del_{eid}", on_click=_binge_del, args=(eid,))

    st.button("＋ 작품 추가", on_click=_binge_add)

    if st.button("정주행 추천 포스팅 생성", type="primary"):
        title_list = [
            st.session_state.get(f"binge_t_{e['id']}", "").strip()
            for e in st.session_state.binge_entries
            if st.session_state.get(f"binge_t_{e['id']}", "").strip()
        ]
        if binge_theme and title_list:
            with st.spinner(f"{len(title_list)}편의 시리즈 정보(TMDB) 수집 중..."):
                series_data_text = ""
                for s_title in title_list:
                    tv_info = tmdb.search_tv(s_title)
                    if tv_info:
                        details = tmdb.get_tv_details(tv_info['id'])
                        poster_html = builder._build_image_html(details.get('poster_url'), f"{details.get('title')} 포스터")
                        if not poster_html:
                            poster_html = builder._build_placeholder_html(f"'{details.get('title')}' 포스터")
                        series_data_text += f"""
[작품: {details.get('title')}]
- 원제: {details.get('original_title', '정보 없음')}
- 국가: {details.get('country', '정보 없음')}
- 방영 시작: {details.get('first_air_date', '정보 없음')}
- 총 화수: {details.get('number_of_episodes', '?')}화
- 시즌 수: {details.get('number_of_seasons', 1)}시즌
- 편당 러닝타임: 약 {details.get('episode_runtime', 24)}분
- 정주행 총 소요 시간: {details.get('total_watch_time', '정보 없음')}
- 장르: {details.get('genres', '')}
- 줄거리: {details.get('overview', '')}
- <포스터 HTML 코드>: {poster_html}
============================================
"""
                    else:
                        st.warning(f"'{s_title}' 정보를 찾을 수 없어 제외했습니다.")

                if series_data_text.strip():
                    reference_posts = rss.get_latest_posts_text(limit=5)
                    db_refs = get_recent_references("정주행")
                    if db_refs:
                        reference_posts = db_refs + "\n\n---\n[RSS 최신글]\n---\n\n" + reference_posts
                    prompt = builder.build_binge_prompt(binge_theme, series_data_text, reference_posts)
                    result = claude_ai.generate_post(prompt)
                    titles = parse_titles_from_html(result)
                    final_html = formatter.wrap_in_table(binge_theme, result, post_type="정주행")
                    st.session_state.binge_data = {"title": binge_theme, "html": final_html, "titles": titles}
                else:
                    st.error("유효한 작품 정보를 하나도 수집하지 못했습니다. 제목을 확인해 주세요.")
        else:
            st.warning("테마와 작품 제목을 하나 이상 입력해 주세요.")

    if st.session_state.binge_data:
        st.success("정주행 추천 포스팅 생성 완료!")
        titles = st.session_state.binge_data.get("titles", [])
        if titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", titles, key="binge_title_select")
                st.code(selected, language=None)
        if st.button("💾 이 포스팅을 내 취향 DB에 저장하기", key="save_binge_btn"):
            if db.save_post(st.session_state.binge_data['title'], "정주행", st.session_state.binge_data['html']):
                st.toast("✅ DB에 저장되었습니다!", icon="🎉")
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1: st.code(st.session_state.binge_data['html'], language='html')
        with sub_tab2: show_isolated_html(st.session_state.binge_data['html'])


# ==========================================
# [TAB 6] 사진 포스팅
# ==========================================
with tab_photo:
    section_card("📸", "사진 기반 포스팅", "직접 찍은 사진과 함께 MK 비평가 스타일의 감성 포스팅을 작성합니다.")
    st.write("장소 배경 조사(PDF) → 방문 경위 → 메뉴/감상 순서로 작성됩니다. 맛집 인플루언서 글이 아닌, MK만의 시선으로 기록합니다.")

    st.markdown("#### 📍 1. 장소 정보 입력 (선택)")
    col_region, col_search, col_btn = st.columns([1.5, 3, 1])
    region_list = ["직접 입력", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
    with col_region:
        region_option = st.selectbox("지역 선택", options=region_list, index=0, label_visibility="collapsed")
    with col_search:
        if region_option == "직접 입력":
            search_query = st.text_input("검색어", placeholder="지역명 + 상호명 (예: 제주 애월읍 카페)", label_visibility="collapsed")
            target_region = ""
        else:
            search_query = st.text_input("상호명 검색", placeholder=f"예: 남산동 스타벅스, 무촌리 철물점 등", label_visibility="collapsed")
            target_region = region_option
    with col_btn:
        search_place_btn = st.button("네이버 검색", key="search_place_btn", width='stretch')

    if search_place_btn and search_query:
        final_query = f"{target_region} {search_query}".strip()
        with st.spinner(f"'{final_query}'(으)로 네이버 지도를 뒤지는 중..."):
            results = naver.search_local_place(final_query)
            if "error" in results:
                st.error(results["error"])
            elif results.get("items"):
                st.session_state.place_search_results = results["items"]
                st.session_state.selected_place = None
            else:
                st.warning("검색 결과가 없습니다. 검색어를 바꿔보세요!")

    if st.session_state.place_search_results and not st.session_state.selected_place:
        st.markdown("##### 📌 어느 곳인가요? (검색 결과)")
        with st.container(height=300):
            for i, item in enumerate(st.session_state.place_search_results):
                title_p = item['title'].replace('<b>', '').replace('</b>', '')
                category = item['category']
                address = item['roadAddress'] or item['address']
                col_info, col_sel = st.columns([5, 1])
                with col_info:
                    st.write(f"**{title_p}** \n<small>{category} | 📍 {address}</small>", unsafe_allow_html=True)
                with col_sel:
                    if st.button("선택", key=f"sel_place_{i}", width='stretch'):
                        st.session_state.selected_place = {"title": title_p, "category": category, "address": address, "link": item.get('link', '')}
                        st.session_state.place_search_results = None
                        st.rerun()
        st.markdown("---")

    if st.session_state.selected_place:
        p = st.session_state.selected_place
        st.success(f"✅ **{p['title']}** 장소가 선택되었습니다! (📍 {p['address']})")
        if st.button("장소 다시 검색하기", key="reset_place_btn"):
            st.session_state.selected_place = None
            st.rerun()
    st.markdown("---")

    st.markdown("#### 📄 2. 배경 조사 자료 (선택)")
    st.caption("방문 전 가게/장소에 대해 조사한 자료를 PDF로 업로드하세요. 글의 도입부 배경 설명에 활용됩니다.")
    photo_pdf_files = st.file_uploader(
        "배경 조사 PDF (선택)", type="pdf", accept_multiple_files=True, key="photo_pdf_uploader"
    )
    if photo_pdf_files:
        st.caption(f"📂 {len(photo_pdf_files)}개 파일 선택됨")
    st.markdown("---")

    st.markdown("#### 🖼️ 3. 사진 업로드 및 메모")
    uploaded_photos = st.file_uploader("포스팅에 들어갈 사진들을 순서대로 올려주세요.", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="photo_uploader")
    photo_contexts = []

    if uploaded_photos:
        st.caption(f"총 {len(uploaded_photos)}장의 사진이 업로드되었습니다.")
        for i, photo in enumerate(uploaded_photos):
            col_img, col_text = st.columns([1, 3])
            with col_img:
                st.image(photo, width='stretch')
            with col_text:
                caption = st.text_area(f"사진 {i+1} 설명", placeholder="예: 타설 전 철근 배근 완료 상태 / 우드톤 가구 조립 중", height=100, key=f"photo_cap_{i}")
                photo_contexts.append({"photo": photo, "caption": caption})
    st.markdown("---")

    st.markdown("#### 📝 4. 포스팅 설정")
    col_cat, col_vibe = st.columns(2)
    with col_cat:
        photo_category = st.selectbox("포스팅 카테고리", options=["🍽️ 맛집/카페 탐방", "🛠️ 현장/건축 일지", "🎬 일상 및 모임"], key="photo_category")
    with col_vibe:
        photo_vibe = st.select_slider("글의 감성 농도", options=["담백하게", "전문적으로", "차분하게", "다정하게", "위트 있게"], value="차분하게", key="photo_vibe")

    st.write("")
    generate_photo_btn = st.button("📸 사진 포스팅 생성", type="primary", width='stretch')

    if generate_photo_btn:
        if not uploaded_photos:
            st.warning("먼저 사진을 업로드해 주세요!")
        else:
            with st.spinner("사진과 메모를 분석하여 포스팅을 작성 중입니다..."):
                place_info_text = ""
                if st.session_state.selected_place:
                    p = st.session_state.selected_place
                    place_info_text = f"[장소 정보]\n- 상호명: {p['title']}\n- 주소: {p['address']}\n- 카테고리: {p['category']}"
                photo_contexts_text = ""
                for i, ctx in enumerate(photo_contexts):
                    photo_contexts_text += f"- 사진 {i+1} 메모: {ctx['caption']}\n"
                photo_pdf_text = ""
                if photo_pdf_files:
                    for pf in photo_pdf_files:
                        try:
                            with pdfplumber.open(pf) as pdf:
                                photo_pdf_text += "\n".join([pg.extract_text() for pg in pdf.pages if pg.extract_text()])
                        except Exception as e:
                            st.warning(f"{pf.name} 읽기 오류: {e}")
                # 이미지 전송 시 토큰 절약: PDF 8000자 / 레퍼런스 1개로 제한
                if len(photo_pdf_text) > 8000:
                    photo_pdf_text = photo_pdf_text[:8000] + "\n...(이하 생략)"
                reference_posts = rss.get_latest_posts_text(limit=1)
                prompt = daily_builder.build_photo_post_prompt(
                    category=photo_category, vibe=photo_vibe,
                    place_info_text=place_info_text,
                    photo_contexts_text=photo_contexts_text,
                    reference_posts=reference_posts,
                    pdf_text=photo_pdf_text
                )
                result = claude_ai.generate_post(prompt, images=uploaded_photos)
                st.session_state.photo_titles = parse_titles_from_html(result)
                st.session_state.photo_result_html = formatter.wrap_in_table(f"{photo_category} 기록", result, post_type="사진")
                st.session_state.photo_uploaded_files = uploaded_photos
                copy_html_raw = strip_images_for_copy(result, len(uploaded_photos))
                st.session_state.photo_copy_html = formatter.wrap_in_table(f"{photo_category} 기록", copy_html_raw, post_type="사진")
                st.success("사진 기반 맞춤형 포스팅 생성이 완료되었습니다!")

    if st.session_state.get("photo_result_html"):
        st.markdown("---")
        if st.session_state.photo_titles:
            with st.container(border=True):
                st.markdown("##### 📌 네이버 SEO 최적화 제목 추천")
                selected = st.selectbox("원하는 제목을 선택하세요", st.session_state.photo_titles, key="photo_title_select")
                st.code(selected, language=None)
        res_tab1, res_tab2, res_tab3 = st.tabs(["👁️ 완벽 미리보기", "📋 블로그 복사용 화면", "📄 HTML 원본 코드"])
        with res_tab1:
            st.info("✨ 실제 사진들이 적용된 완벽한 미리보기입니다.")
            render_preview_with_photos(st.session_state.photo_result_html, st.session_state.photo_uploaded_files or [])
        with res_tab2:
            st.success("💡 아래 회색 네모 박스 안의 내용을 마우스로 쭉 드래그해서 복사(Ctrl+C)한 뒤 붙여넣기(Ctrl+V) 하세요!")
            clean_copy_html = st.session_state.photo_copy_html.replace("```html\n", "").replace("```html", "").replace("```", "")
            show_isolated_html(clean_copy_html, height=1000, scrolling=True)
        with res_tab3:
            st.warning("티스토리 등 HTML 소스코드 직접 입력이 가능한 곳을 위한 예비용 코드입니다.")
            st.code(st.session_state.photo_copy_html, language="html")


# ==========================================
# [TAB 7] 영화 검색
# ==========================================
with tab_search:
    section_card("🔍", "영화 검색 & 박스오피스", "TMDB·KOBIS 기반으로 영화 정보와 박스오피스 데이터를 실시간으로 검색합니다.")
    st.markdown("현재 극장가 트렌드를 확인하고, 원하는 영화의 상세 정보를 검색해 보세요.")

    search_sub1, search_sub2 = st.tabs(["🏆 일별 박스오피스", "🔍 영화 상세 검색"])

    with search_sub1:
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y년 %m월 %d일')
        st.header("🍿 일별 박스오피스 TOP 10")
        st.caption(f"기준일: {yesterday_str} (데이터 제공: 영화진흥위원회)")

        with st.spinner("박스오피스 순위를 불러오는 중입니다..."):
            box_office_data = fetch_daily_boxoffice()

        if box_office_data:
            st.info("💡 순위를 확인한 후, **[영화 상세 검색]** 탭에서 영화 제목을 검색해 보세요!")
            for movie in box_office_data:
                with st.container(border=True):
                    inten = int(movie['rankInten'])
                    if movie['rankOldAndNew'] == 'NEW':
                        rank_mark = "🆕 NEW"
                    elif inten > 0:
                        rank_mark = f"🔺 {inten}"
                    elif inten < 0:
                        rank_mark = f"🔻 {abs(inten)}"
                    else:
                        rank_mark = "➖"
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        rank = int(movie['rank'])
                        icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
                        st.markdown(f"### {icon} {rank}위")
                        st.caption(rank_mark)
                    with col2:
                        st.markdown(f"#### {movie['movieNm']}")
                        st.markdown(f"👥 **당일 관객:** {int(movie['audiCnt']):,}명 (누적: {int(movie['audiAcc']):,}명)")
                        st.markdown(f"💰 **누적 매출:** {format_money(movie['salesAcc'])}")
        else:
            st.warning("박스오피스 데이터를 불러올 수 없습니다. API 키를 확인해 주세요.")

    with search_sub2:
        st.markdown("정확한 영화 식별을 위해 **검색 후 드롭다운**에서 조회할 영화를 선택해 주세요.")
        search_q = st.text_input("🔍 영화 제목 입력", placeholder="예: 파묘, 에이리언, 프로젝트 헤일메리", key="movie_search_q")

        if search_q:
            movies = fetch_kobis_search(search_q)
            if not movies:
                st.warning(f"영진위 DB에 '{search_q}'에 대한 검색 결과가 없습니다.")
            else:
                movie_options = {f"{m['movieNm']} ({m['prdtYear']} | {m['genreAlt']})": m for m in movies}
                selected_m = st.selectbox("🎯 정확한 영화를 선택하세요", options=["선택 안 함"] + list(movie_options.keys()))

                if selected_m != "선택 안 함":
                    m_info = movie_options[selected_m]
                    m_nm, m_en, m_cd, m_yr = m_info['movieNm'], m_info.get('movieNmEn', ''), m_info['movieCd'], m_info['prdtYear']

                    with st.spinner("모든 데이터베이스를 조회 중입니다..."):
                        k_detail, k_stats = fetch_kobis_detail_and_boxoffice(m_cd)
                        poster_url, imdb_id, tmdb_overview, tmdb_vote, tmdb_cnt = fetch_tmdb_search(m_nm, m_en, m_yr)
                        ratings = fetch_omdb_ratings(imdb_id)
                        final_plot = tmdb_overview if tmdb_overview else fetch_naver_plot_fallback(m_nm)

                    st.divider()
                    col1, col2 = st.columns([1, 2.2])
                    with col1:
                        if poster_url:
                            st.image(poster_url, width='stretch', caption="TMDB Database")
                        else:
                            st.warning("🖼️ 포스터 이미지를 찾을 수 없습니다.")
                        st.markdown("### ⭐ 글로벌 평점")
                        if ratings:
                            for r in ratings:
                                icon = "🍅" if r['Source'] == "Rotten Tomatoes" else ("🎬" if r['Source'] == "Internet Movie Database" else "Ⓜ️")
                                st.metric(f"{icon} {r['Source']}", r['Value'])
                        elif tmdb_vote and tmdb_cnt > 0:
                            st.info("OMDB 공식 평점 대신 TMDB 유저 평점을 제공합니다.")
                            st.metric("💠 TMDB User Rating", f"{tmdb_vote:.1f} / 10", f"{tmdb_cnt:,} votes")
                        else:
                            st.info("등록된 평점 정보가 없습니다. (개봉 전 이거나 데이터 부족)")
                    with col2:
                        st.header(f"{m_nm} ({m_yr})")
                        if m_en: st.caption(f"Original Title: {m_en}")
                        c1, c2, c3 = st.columns(3)
                        c1.write(f"⏱ **러닝타임:** {k_detail.get('showTm', '정보없음')}분")
                        c2.write(f"🎞 **장르:** {', '.join([g['genreNm'] for g in k_detail.get('genres', [])])}")
                        open_dt = k_detail.get('openDt', '')
                        f_open_dt = f"{open_dt[:4]}-{open_dt[4:6]}-{open_dt[6:]}" if len(open_dt) == 8 else "미정"
                        c3.write(f"📅 **개봉일:** {f_open_dt}")
                        st.markdown("---")
                        st.markdown("#### 📖 시놉시스 (Synopsis)")
                        if final_plot:
                            st.write(final_plot)
                        else:
                            st.info("등록된 공식 줄거리가 없습니다.")
                        st.markdown("---")
                        st.markdown("#### 📊 영진위 실시간 통계")
                        if k_stats:
                            st.success(f"🔥 현재 박스오피스 **{k_stats['rank']}위** 기록 중!")
                            r1c1, r1c2 = st.columns(2)
                            with r1c1: st.metric("누적 관객수", f"{int(k_stats['audiAcc']):,}명", f"+{int(k_stats['audiInten']):,}명 (전일 대비)")
                            with r1c2: st.metric("당일 관객수", f"{int(k_stats['audiCnt']):,}명")
                            r2c1, r2c2 = st.columns(2)
                            with r2c1: st.metric("누적 매출액", format_money(k_stats['salesAcc']))
                            with r2c2: st.metric("스크린 수", f"{k_stats['scrnCnt']}개")
                        else:
                            st.info("현재 박스오피스 TOP 10 진입작이 아닙니다. (과거 개봉작 또는 상영 전)")
                        st.markdown("---")
                        st.markdown("#### 👥 상세 제작 정보 (KOBIS Database)")
                        with st.expander("🎬 감독 및 주요 출연진"):
                            st.write(f"**감독:** {', '.join([d['peopleNm'] for d in k_detail.get('directors', [])])}")
                            actors = [a['peopleNm'] for a in k_detail.get('actors', [])]
                            st.write(f"**출연진:** {', '.join(actors) if actors else '등록된 배우 정보가 없습니다.'}")
                        with st.expander("🛠️ 주요 스태프 및 제작진"):
                            staffs = [f"{s['peopleNm']} ({s['staffRoleNm']})" for s in k_detail.get('staffs', [])]
                            st.write(", ".join(staffs) if staffs else "스태프 정보가 없습니다.")
                        with st.expander("🏢 관련 회사 및 배급사"):
                            companies = [f"{c['companyNm']} ({c['companyPartNm']})" for c in k_detail.get('companys', [])]
                            for comp in companies: st.write(f"- {comp}")
                        with st.expander("📋 심의 및 관람 등급"):
                            audits = [a['watchGradeNm'] for a in k_detail.get('audits', [])]
                            st.write(f"**심의 등급:** {', '.join(audits) if audits else '심의 정보 없음'}")
                            nations = [n['nationNm'] for n in k_detail.get('nations', [])]
                            st.write(f"**제작 국가:** {', '.join(nations) if nations else '정보 없음'}")
