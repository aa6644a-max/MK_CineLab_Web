import streamlit as st
import streamlit.components.v1 as components
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter
from naver_client import NaverClient
from db_manager import DBManager

st.set_page_config(page_title="MK CINELAB", page_icon="🎬", layout="centered")

@st.cache_resource
def init_engines():
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter(), NaverClient(), DBManager()

tmdb, gemini, builder, formatter, naver, db = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")
st.markdown("---")

if "rev_data" not in st.session_state: st.session_state.rev_data = None
if "pre_data" not in st.session_state: st.session_state.pre_data = None
if "news_data" not in st.session_state: st.session_state.news_data = None

tab1, tab2, tab3, tab4 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식", "🗄️ 내 보물창고"])

# 탭 1: 영화 리뷰
with tab1:
    st.subheader("영화 리뷰 생성")
    col1, col2 = st.columns([3, 1])
    with col1:
        title = st.text_input("리뷰할 영화 제목", key="rev_title")
    with col2:
        year_input = st.text_input("개봉 연도 (선택)", placeholder="예: 2024", key="rev_year")
    comment = st.text_area("나의 주관적 감상평", height=150, key="rev_comment")
    
    if st.button("리뷰 생성", type="primary"):
        if title:
            with st.spinner("영화 정보 수집 및 작성 중..."):
                year_val = int(year_input) if year_input.isdigit() else None
                movie_info = tmdb.search_movie(title, year=year_val)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(title)
                    prompt = builder.build_review_prompt(details, comment, latest_news)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 리뷰", result)
                    st.session_state.rev_data = {"title": details['title'], "html": final_html}
                else:
                    st.error("영화를 찾을 수 없습니다.")
        else:
            st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.rev_data:
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1:
            st.code(st.session_state.rev_data['html'], language='html')
        with sub_tab2:
            st.components.v1.iframe(srcdoc=st.session_state.rev_data['html'], height=800, scrolling=True)
        if st.button("💾 리뷰 DB에 저장하기", key="save_rev"):
            db.save_post(movie_title=st.session_state.rev_data['title'], post_type="review", content=st.session_state.rev_data['html'])
            st.success("저장 완료! 🎉")

# 탭 2: 개봉 프리뷰
with tab2:
    st.subheader("개봉 예정작 프리뷰")
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트", key="pre_point")
    if st.button("프리뷰 생성", type="primary"):
        if p_title:
            with st.spinner("정보 수집 중..."):
                movie_info = tmdb.search_movie(p_title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    latest_news = naver.search_movie_news(p_title)
                    prompt = builder.build_preview_prompt(details, point, latest_news)
                    result = gemini.generate_post(prompt)
                    final_html = formatter.wrap_in_table(f"{details['title']} 프리뷰", result)
                    st.session_state.pre_data = {"title": details['title'], "html": final_html}
        else:
            st.warning("영화 제목을 입력해 주세요.")

    if st.session_state.pre_data:
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1:
            st.code(st.session_state.pre_data['html'], language='html')
        with sub_tab2:
            st.components.v1.iframe(srcdoc=st.session_state.pre_data['html'], height=800, scrolling=True)
        if st.button("💾 프리뷰 DB에 저장하기", key="save_pre"):
            db.save_post(movie_title=st.session_state.pre_data['title'], post_type="preview", content=st.session_state.pre_data['html'])
            st.success("저장 완료! 🎉")

# 탭 3: 영화 뉴스
with tab3:
    st.subheader("최신 영화 뉴스")
    news_content = st.text_area("뉴스 기사 원문", height=300, key="news_input")
    if st.button("뉴스 포스팅 생성", type="primary"):
        if news_content:
            with st.spinner("분석 중..."):
                prompt = builder.build_news_prompt(news_content)
                result = gemini.generate_post(prompt)
                final_html = formatter.wrap_in_table("최신 영화 뉴스", result)
                st.session_state.news_data = {"title": "영화 뉴스 포스팅", "html": final_html}
    if st.session_state.news_data:
        sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드", "👁️ 블로그 미리보기"])
        with sub_tab1:
            st.code(st.session_state.news_data['html'], language='html')
        with sub_tab2:
            st.components.v1.iframe(srcdoc=st.session_state.news_data['html'], height=800, scrolling=True)
        if st.button("💾 뉴스 DB에 저장하기", key="save_news"):
            db.save_post(movie_title="영화 뉴스", post_type="news", content=st.session_state.news_data['html'])
            st.success("저장 완료! 🎉")

# 탭 4: 내 보물창고
with tab4:
    st.subheader("🗄️ 내 콘텐츠 보물창고")
    posts = db.get_all_posts() 
    if not posts:
        st.info("저장된 포스팅이 없습니다.")
    else:
        post_options = {p[0]: f"[{p[2].upper()}] {p[1]} ({p[3]})" for p in posts}
        selected_post_id = st.selectbox("불러올 포스팅 선택:", options=list(post_options.keys()), format_func=lambda x: post_options[x])
        if selected_post_id:
            content = db.get_post_content(selected_post_id)
            if content:
                sub_tab1, sub_tab2 = st.tabs(["📄 HTML 코드 복사", "👁️ 미리보기"])
                with sub_tab1:
                    st.code(content, language='html')
                with sub_tab2:
                    st.components.v1.iframe(srcdoc=content, height=800, scrolling=True)
                if st.button("🗑️ 이 포스팅 삭제하기"):
                    db.delete_post(selected_post_id)
                    st.rerun()