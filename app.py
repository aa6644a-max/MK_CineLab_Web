import streamlit as st
from tmdb_client import TMDBClient
from gemini_client import GeminiClient
from prompt_builder import PromptBuilder
from html_formatter import HTMLFormatter

st.set_page_config(page_title="MK CINELAB", page_icon="🎬")

@st.cache_resource
def init_engines():
    return TMDBClient(), GeminiClient(), PromptBuilder(), HTMLFormatter()

tmdb, gemini, builder, formatter = init_engines()

st.title("🎬 MK CINELAB 블로그 자동화")

# 3가지 기능 탭 유지
tab1, tab2, tab3 = st.tabs(["🎥 영화 리뷰", "📅 개봉 프리뷰", "📰 영화 소식"])

with tab1:
    st.subheader("영화 리뷰 생성")
    title = st.text_input("리뷰할 영화 제목", key="rev_title")
    comment = st.text_area("나의 주관적 감상평", height=150, key="rev_comment")
    if st.button("리뷰 생성"):
        if title:
            with st.spinner("정보 수집 중..."):
                movie_info = tmdb.search_movie(title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    prompt = builder.build_review_prompt(details, comment)
                    result = gemini.generate_post(prompt)
                    st.code(formatter.wrap_in_table(f"{details['title']} 리뷰", result), language='html')
                else:
                    st.error("영화를 찾을 수 없습니다.")

with tab2:
    st.subheader("개봉 예정작 프리뷰")
    p_title = st.text_input("프리뷰 영화 제목", key="pre_title")
    point = st.text_input("강조 포인트", key="pre_point")
    if st.button("프리뷰 생성"):
        if p_title:
            with st.spinner("프리뷰 원고 작성 중..."):
                movie_info = tmdb.search_movie(p_title)
                if movie_info:
                    details = tmdb.get_movie_details(movie_info['id'])
                    prompt = builder.build_preview_prompt(details, point)
                    result = gemini.generate_post(prompt)
                    st.code(formatter.wrap_in_table(f"{details['title']} 프리뷰", result), language='html')

with tab3:
    st.subheader("최신 영화 뉴스")
    news_content = st.text_area("뉴스 기사 원문", height=300, key="news_input")
    if st.button("뉴스 포스팅 생성"):
        if news_content:
            with st.spinner("뉴스 분석 중..."):
                prompt = builder.build_news_prompt(news_content)
                result = gemini.generate_post(prompt)
                st.code(formatter.wrap_in_table("최신 영화 뉴스", result), language='html')